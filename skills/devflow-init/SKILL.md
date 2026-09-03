---
name: devflow-init
description: 为既有组件逆向建立或补齐 DevFlow canonical baseline。既有组件缺少 specs/spec.md、specs/design.md，文档仍为 draft、provenance 不足或 baseline preflight 失败时使用；也在用户明确要求从源码、测试、API/IDL、配置、构建部署和既有说明初始化规格设计时使用。不要用于 componentMode 为 new 的组件。
---

# DevFlow Init

`devflow-init` 只为既有组件建立可信的当前规格与设计基线。它不是新功能规格阶段，也不修改业务实现。

## 硬规则：澄清而不臆造

- 只读逆向源码、测试、API/IDL、配置、构建、部署与既有说明；版本控制 revision 只用于固定证据快照。
- 除 `specs/spec.md`、`specs/design.md` 和活动变更的 `change.json` preflight 记录外，不修改任何组件文件。
- 不把现存实现自动等同于正确需求。代码只能证明“当前这样实现”，不能证明“业务要求必须如此”。
- 不虚构业务意图、设计理由、错误语义、性能阈值、历史决策、兼容承诺或责任人。
- 证据不足或冲突时写 `unknown`。影响当前契约、验收或架构边界的 unknown 是 blocker，必须向人追问。
- 作者自检不算独立评审。独立 reviewer 通过且人明确确认前，文档保持 `baselineStatus: draft`。
- `componentMode` 不明确时先询问；不得把 init 当作规避模式判断的默认路径。

## 输入与输出

输入：

- 已解析的 `<component-root>`；
- 人确认的 `componentMode`；
- 可重复读取的 source revision；
- 可读的代码与工程证据；
- 如由活动 AR 路由而来，对应 `change.json`。

输出只位于：

```text
<component-root>/specs/spec.md
<component-root>/specs/design.md
```

两份都缺时生成两份。仅缺一份时只生成缺失的一份，并把已有文档作为交叉校验输入；不得顺便重写、格式化或“改善”已有文档。已有文档与证据冲突时先报告并询问，不能靠改写已有文档让检查通过。

## 工作流

### 1. 执行模式与路径 preflight

1. 按 `using-devflow` 解析唯一组件根；不能唯一确定时询问。
2. 获取明确的 `componentMode`：
   - `new`：停止 init，说明首个 AR 应通过 `delta-spec.md` 与 `delta-design.md` 从空基线创建 canonical 文档。
   - `existing`：继续。
   - 缺失、冲突或不确定：停止并询问。
3. 检查 `specs/spec.md` 和 `specs/design.md`：
   - 两份均为 `baseline-ready`：不重建，返回原工作流重新执行 preflight。
   - 一份缺失或 draft：只处理该份，读取另一份做一致性检查。
   - 两份缺失或 draft：处理两份。
   - 任一 `baseline-ready` 文档被要求重建：拒绝静默覆盖；应通过正式变更修订 canonical，或由人明确批准单独的基线纠错。
4. 固定 source revision。无法取得稳定 revision 时阻塞，因为 provenance 不能复现。
5. 有活动 `change.json` 时确认其 `componentMode`、`baseRevision` 与当前上下文一致；不得改写 `baseRevision`。

### 2. 建立只读证据清单

按 [逆向分析清单](references/reverse-engineering-checklist.md) 读取适用来源：

1. 对外 API、IDL、协议、schema、导出符号；
2. 测试、fixture、golden data 和失败路径断言；
3. 源码入口、状态机、数据流、错误处理、并发与资源所有权；
4. 配置项、默认值、feature flag 和环境约束；
5. 构建、依赖、生成步骤与目标平台；
6. 部署拓扑、启动关闭、健康检查、升级回滚；
7. 已有说明、决策记录、运维手册和上游需求锚点。

只读取，不运行部署，不执行会写源码、生成物、锁文件、数据库或环境状态的命令。必要工具无法只读工作时，记录能力 blocker，不用猜测补齐。

对每个来源记录：

- source revision；
- `/` 形式的文件路径或接口锚点；
- 符号、测试用例、配置键或章节；
- 观察到的事实；
- 冲突、生成来源、适用条件与可信度限制。

### 3. 给每项事实分类

所有进入 canonical 草稿的事实必须恰好使用以下一种分类：

| 分类 | 含义 | 可否直接写成规范性要求 |
|---|---|---|
| `verifiable`（可验证） | 可由当前快照中的代码、测试、接口或配置锚点重复验证 | 否；只说明 observed behavior，除非人确认其应被保留 |
| `human-confirmed`（人工确认） | 有明确回答、确认人和确认时间，且回答范围清楚 | 可以，在其确认范围内 |
| `unknown` | 无证据、证据冲突、只能推断或缺责任人确认 | 不可以 |

不要增加“很可能”“合理推测”等第四类来绕开 unknown。推断只能作为待确认问题的上下文。

特别处理：

- 测试断言证明被测试的当前预期，不自动证明业务意图正确。
- API/IDL 证明公开形状；兼容期、消费者、弃用理由若无来源仍是 unknown。
- 配置中的数值证明当前默认或限制，不自动成为 NFR 阈值。
- 代码结构证明当前设计；“为了性能/扩展性/安全”等理由无来源时是 unknown。
- 错误码分支证明当前返回行为；其业务语义与稳定承诺需人工或权威说明确认。

### 4. 解决冲突与 blocking unknown

先把问题按影响排序，只向人询问不能从允许来源验证的最小集合。

以下 unknown 默认 blocking：

- 组件职责、非职责或所有权边界；
- 对外行为、接口语义、错误语义、兼容承诺；
- 安全、隐私、功能安全或权限边界；
- 性能、实时性、容量、资源等验收阈值；
- 持久化、迁移、并发、恢复和失败状态保证；
- spec 与 design 或多个权威来源之间的冲突；
- 会改变下一个 AR 的 delta 解释方式的事实。

问题必须包含：已验证事实、冲突或缺口、受阻章节、可选答案及各自影响。没有证据支持时不要把某个选项标为推荐。

只影响解释性背景、且不改变契约或架构决策的 unknown 可以暂不阻塞，但必须保留在文档的 Unknowns 表中并标明 owner。

### 5. 起草组件规格基线

canonical 基线要被人逐条确认，动笔前加载 `writing-readable-doc` 并按它写：每节第一句给判断，术语一次固定，需求块与 QAS 按模板原样写，unknown 明确标出而不是用模糊词糊过去。

需要创建或补齐规格时，读取 `devflow-specify` 的
`references/component-spec-template.md`：

- 写组件当前全量可观察契约，不写本次 init 的过程叙事；
- 使用稳定 requirement ID；
- 把可验证实现事实与经人确认的规范性要求分开；
- 每条规范性行为提供来源，并按类型具备可判定场景、完整 QAS 或验证场景；
- 没有人工确认的 observed behavior 不使用“必须”伪装成需求；
- 阈值、错误语义和兼容承诺没有确认就保持 unknown；
- frontmatter 初始写 `baselineStatus: draft`、`baselineRevision: <source revision>`、
  `baselineChange: null`。

### 6. 起草组件设计基线

需要创建或补齐设计时，读取 `devflow-design` 的
`references/component-design-template.md`：

- 描述当前组件边界、单元、依赖、接口实现、状态与数据、错误恢复、并发资源、构建部署和测试接缝；
- 每个设计结论引用证据和相关 requirement ID；
- 区分“当前结构”与“结构理由”；理由无来源就标 unknown；
- 不为填满模板发明候选方案、历史取舍或容量预算；
- frontmatter 初始写 `baselineStatus: draft`、`baselineRevision: <source revision>`、
  `baselineChange: null`。

### 7. 交叉校验

无论生成一份还是两份，都检查：

- 每个设计职责、接口和约束能追到 spec requirement，或明确标为实现事实；
- 每个 requirement 有设计承载、明确不涉及设计，或有 blocking unknown；
- 名称、边界、状态、错误语义、单位、范围和配置默认值一致；
- provenance 指向同一 source revision；
- 现有文档中的 normative 声明没有被新文档悄悄改写。

仅缺一份时，把交叉校验发现写入新文档；若发现已有文档本身可能错误，保持新文档 draft 并请求人决定，不修改已有文档。

### 8. 独立评审

按 [baseline 评审清单](references/baseline-review-checklist.md) 派发独立 reviewer。输入只包括：

- canonical 草稿；
- 另一份 canonical 文档（如存在）；
- evidence ledger 与 source revision；
- 人工回答及其范围；
- unresolved unknowns。

不给 reviewer 作者的隐含推理。reviewer 只读检查事实来源、推断越界、spec-design 一致性、unknown 分级和模板完整性，不直接修改文档。

reviewer verdict 为 `rework` 或 `blocked` 时，作者按 findings 修订或追问，再发起新的独立复审。无法获得独立 reviewer 时，文档保持 draft。

有活动 AR 时，主控 Agent 必须把完整返回落到
`reviews/baseline-init-review-YYYY-MM-DD[-rN].md`，并让 canonical 文档与
`change.json.gates.baselinePreflight.evidence` 引用该记录。独立 init 没有活动 AR
时，记录可以只保存在两份 canonical 的 review 章节。

### 9. 人工确认并标记 baseline

独立 reviewer 通过后，向人展示：

- 两份 canonical diff，或仅新增文档的完整内容；
- provenance 摘要；
- reviewer verdict 与 findings resolution；
- 剩余 non-blocking unknown；
- 本次没有修改的现有文档。

只有人明确确认后：

1. 在本次生成或补齐的文档记录确认人、确认时间和 reviewer 记录；
2. 把其 `independentReview.status` 置为 `passed`；
3. 把其 `humanConfirmation.status` 置为 `confirmed`；
4. 把其 `baselineStatus` 置为 `baseline-ready`；
5. 若两份本次都生成，确保两份状态一起更新；
6. 有活动变更时，重新核验两份文档并更新 `change.json` 的 canonical artifact 状态与 `baselinePreflight` gate。

人工未明确确认、blocking unknown 未关闭或任一必需文件写入失败时，不得标记 ready。

## 完成报告

报告：

- 解析出的组件根与 source revision；
- 创建、补齐、保持不变的文件；
- `verifiable`、`human-confirmed`、`unknown` 数量与关键锚点；
- reviewer verdict 与人工确认；
- baseline preflight 是否可通过；
- 未解决 blocker 和下一条最小问题。

不把聊天中的报告当作落盘成功。必须重新读取文件并核验 frontmatter 与关键章节。

## 直接参考

- `devflow-specify` 的 `references/component-spec-template.md`：组件规格模板
- `devflow-design` 的 `references/component-design-template.md`：组件设计模板
- [逆向分析清单](references/reverse-engineering-checklist.md)
- [baseline 评审清单](references/baseline-review-checklist.md)
