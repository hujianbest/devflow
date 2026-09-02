---
name: devflow-specify
description: 在开始新的 AR、澄清增量需求、建立 DevFlow change 交付件，或 R1 规格评审要求返工时使用。把输入写成可测试的 srs.md，并基于组件 canonical 规格生成可安全合并的 delta-spec.md；不负责实现设计或编码。
---

# DevFlow 增量规格

## 目标与交付件

规格阶段只描述“本 AR 要改变什么”，不复制组件全量现状。目标目录固定为：

```text
<component-root>/specs/changes/ARXXX-<topic>/
├── change.json
├── srs.md
├── delta-spec.md
├── delta-design.md        # 后续 design 阶段填写
├── tasks.md
├── traceability.md
├── reviews/
└── closeout.md            # ship 阶段填写
```

- `srs.md`：来源、目标、范围、非范围，以及本 AR 的增量需求。
- `delta-spec.md`：对 `specs/spec.md` 的精确增量；它不是新的全量规格。
- `tasks.md`：仅在本阶段建立空骨架；设计通过后由 `devflow-tdd` 细化。
- `traceability.md`：固定链 `需求条目 → Spec Section → Design Section/Case → Task → Code/Test → Evidence`。
- `change.json`：身份、`componentMode`、profile、基线、artifact 图、门禁和归档状态的唯一结构化来源。

使用 `references/srs-template.md`、`references/delta-spec-template.md`、
`references/component-spec-template.md`、`references/traceability-template.md`、
`../devflow-tdd/references/tasks-template.md`，以及入口技能中的
`../using-devflow/references/change-template.json` 和交付结构契约。

## 不变量

1. `componentMode` 必须是 `new` 或 `existing`。字段缺失、与仓库事实冲突或无法判断时，先问人，禁止自行推断。
2. `existing` 必须读取 `specs/spec.md` 和 `specs/design.md`；两者都存在且 `baselineStatus: baseline-ready` 才能继续。缺失或仍为 draft 时立即阻塞，并转交 `devflow-init` 建立或补齐基线。
3. `new` 允许两份 canonical 文档都不存在，delta 的 canonical 基线记为 `EMPTY`，但 `change.json.baseRevision` 仍记录变更开始时不可变的仓库 revision。如果已存在任一 canonical 文档，`new` 与仓库事实冲突，必须澄清。
4. delta 只触碰明确列出的稳定 ID 与局部语义。未列出的章节、字段、验收、错误语义和兼容承诺全部保留。
5. 不用标题文本或行号充当合并身份。需求条目、canonical Spec Section 和 Delta Operation 都使用稳定 ID。
6. blocking Open Question 未关闭时，把 `change.json.gates.r1.status` 保持为 `blocked`，不得送审。

## 工作流

### 1. 确定组件、change 与模式

先确定目标组件根、`changeId: ARXXX` 和 kebab-case `topic`。目录名必须等于
`<changeId>-<topic>`；任一身份不一致时停下修正，不创建第二套目录。

读取已有 `change.json`。不存在时，以
`../using-devflow/references/change-template.json` 建立严格 JSON，并遵循
`../using-devflow/references/delivery-contract.md`。在获得可靠事实前不要猜
`componentMode`。`baseRevision`、`executionMode` 或 profile 的
`name/risk/reasons/requiredEvidence/requiredReviewers` 缺失时也要澄清。

### 2. 执行 baseline preflight

`componentMode: existing`：

- 同时读取 `specs/spec.md` 与 `specs/design.md`，核对组件身份、
  `baselineStatus: baseline-ready`、provenance、独立评审和人工确认。
- 创建 change 时记录一次不可变、可重新读取的 `change.json.baseRevision`；
  分支名、`HEAD`、`latest` 和聊天摘要不合格，之后不得为消除冲突而改写。
- delta 中另行记录每份 canonical 的路径、baseline revision/digest 与读取时工作树
  状态。canonical 有未提交变化且无法建立可复核基线时先让人处理。
- 任一文档缺失、draft、身份不一致或关键语义 unknown，停止 specify，
  把 `gates.baselinePreflight.status` 置为 `blocked`，指明缺口并进入
  `devflow-init`。

`componentMode: new`：

- canonical 可不存在，不运行 init；canonical artifact 状态记
  `absent-allowed`，两份 delta 的 canonical 基线写 `EMPTY`。
- `delta-spec.md` 必须包含非空的组件目的变更，以及足以从空基线生成首版组件规格的
  完整 `ADDED` 需求块，不能引用不存在的旧章节来补语义。

preflight 成功后把 `gates.baselinePreflight.status` 置为 `passed` 并附证据；
作者后续仍需在每个阶段确认该事实没有失效。

### 3. Capture → Challenge → Clarify

读取原始请求、上游单据和可靠来源。已有组件还要按稳定 ID 核对当前规格与设计。
按顺序澄清：

1. 做完后可观察到什么变化，成功如何判定；
2. 触发条件、正常路径、边界和失败路径；
3. 本 AR 的范围与明确非范围；
4. 对已有行为的新增、修改、移除或重命名意图；
5. 接口消费者、错误语义、时序与兼容性；
6. 适用的性能、资源、并发、安全或合规阈值。

每轮总结已锁定事实和待确认问题。业务规则、优先级、阈值或兼容承诺没有来源时，
写成带 owner 的 blocking Open Question，不猜。

### 4. 写本 AR 的 SRS

`srs.md` 把需求分类写入独立章节：

- 功能性需求：`FR-xxx` 与接口功能需求 `IFR-xxx`；
- 非功能性需求：`NFR-xxx`，每条使用可量化 QAS；
- 可验证约束：`CON-xxx`，不与功能或质量属性混写。

需求条目使用稳定 ID：

- `FR-xxx`：可观察功能行为；
- `IFR-xxx`：接口语义；
- `NFR-xxx`：带阈值的质量属性场景；
- `CON-xxx`：可验证硬约束。

假设和排除项分别用 `ASM-xxx`、`EXC-xxx`，但不伪装成实现追溯行。

每条 FR/IFR 至少包含：

- EARS Statement；
- 可直接形成 RED 的 Given/When/Then Acceptance；
- 可复核 Source。

写入 SRS 的需求都属于当前 AR 的确定范围，不在条目中维护 Must/Should/Could。可选或
延期能力进入 `EXC-xxx` 或新 AR。

Statement 不写函数签名、数据结构、库、线程原语等实现决策。

#### 非功能需求的最小契约

每条 NFR 使用 QAS，五项缺一不可：

1. Stimulus Source：明确触发方；
2. Stimulus：可观察的具体事件；
3. Environment：触发时系统状态，不默认写“正常”；
4. Response：组件可观察、可判断的响应；
5. Response Measure：数字、百分比、时间或明确判定准则，不写“足够快/合理”。

只选择本 AR 相关的质量维度，不为 ISO/IEC 25010 每一维创建空需求。一条 NFR 混合
多个独立质量维度、环境或阈值时拆成多条。QAS 是 NFR 的唯一规范表达，测试 Case
直接由五要素推导，不在 SRS 中再复制一份 Acceptance。每条 NFR 还必须有可复核
Source；任一要素、阈值或权威来源缺失时写 blocking Open Question，不猜。

每条 CON 只包含约束、验证方式和 Source；约束是当前范围内的硬条件，不维护优先级。

#### 需求粒度与拆分

一条需求条目只表达一个可独立观察、独立验收的结果，并只有一个明确 Source。出现
以下任一情况就拆分：

- 多个角色/模块分别产生不同结果；
- 创建、查询、修改、删除等行为被“管理功能”打包；
- 正常、异步/延时、状态族、平台/编译条件形成可独立验收的规则；
- Acceptance 包含可以独立交付或独立失败的多组场景；
- 当前范围和后续能力混在一条。

拆分后每条保留来源，并按类型重写自己的规范内容：FR/IFR 写 Acceptance，NFR 写完整
QAS，CON 写 Verification；不能写“同父需求”。只改表达、不改范围时直接拆；拆分会
改变范围、归属或形成新 AR 时先由需求负责人确认，并在 `EXC-xxx` 或新工作项中记录
去向。

### 5. 从 SRS 推导 delta spec

Impact、Affected Spec Section、Current Behavior 和 Semantics To Preserve 只属于
`delta-spec.md`。主控 Agent 读取 SRS 目标与 canonical 基线后在本阶段推导，不能把
这些合并状态回写 SRS 形成双重真相。

每个变更记录使用稳定 `DS-xxx`，并指向稳定 canonical Spec Section ID：

- `delta-spec.md` 分为 `ADDED / MODIFIED / REMOVED / RENAMED` 需求区；
  组件目的或边界变化放在单独的“组件目的变更”区。
- `ADDED`：给出新的稳定 section ID 和符合 `component-spec-template.md` 的完整需求块。
- `MODIFIED`：指明目标 ID、最小字段/子节选择器、基线摘录或 digest、
  局部替换内容和完整局部结果；修改整个需求时给出完整结果块。明确写出
  preservation clause，不能用摘要误删无关语义。
- `REMOVED`：列出删除原因、被移除的精确语义、依赖引用、删除后的可观察结果和
  迁移/兼容要求；不等于删除整章，除非整章就是获批范围。
- `RENAMED`：只改变显示名称或标题，稳定 ID 保持不变，并给出 from/to。

同步顺序固定为 `RENAMED → REMOVED → MODIFIED → ADDED`。同一规格 ID 不得同时
出现在互斥分区；rename 后继续 modify 时，两个 operation 必须声明顺序并使用同一稳定
ID。发现 remove/modify、remove/add 或多个互相覆盖的操作时阻塞并澄清。

缺陷修复中，如果组件规格已经准确表达目标行为且修复只恢复实现一致性，
`delta-spec.md` 可写 `N/A`，但必须引用需求条目和组件规格 ID，给出违反证据、
不变语义、保留条款和来自 Acceptance/QAS/Verification 的回归验证义务；具体 Case
由设计阶段产生。N/A 不是第五类 operation，也不能用于隐藏需求变化。

每条记录回指需求条目。变更基准只读取 `change.json.baseRevision`；
`delta-spec.md` 只记录 canonical path、baseline revision/digest 和 provenance。

若 canonical 自基线记录后发生变化：

1. 从不可变 `baseRevision` 比较目标稳定 ID 的实际变化；
2. 无重叠时保留并行变化，在 delta/review evidence 中说明合并关系，不改写
   `baseRevision`；
3. 有重叠、语义冲突或无法判断时停止并请人澄清；
4. 不覆盖、不整节重写，也不声称未涉及内容仍被保留。

### 6. 初始化执行与追溯骨架

- 以 `tasks-template.md` 创建 `tasks.md` 空骨架；不要复制 change 身份、profile、
  artifact/gate/archive 状态，也不要提前发明任务或测试 Case。
- 以 `traceability-template.md` 为每条 `FR-xxx`、`IFR-xxx`、`NFR-xxx`
  和可测 `CON-xxx` 建一行。本阶段填写需求条目与目标 Spec Section；其余列保持 `TBD(stage)`
  而不是空白。
- 在 `change.json.artifacts` 中核对全部节点、scope、相对路径和依赖。完成后把
  `srs`、`deltaSpec`、`traceability` 标记为 `ready-for-review`，
  `tasks` 标记为 `draft`。

### 7. 进入 R1

自检通过后，仅把 `change.json.gates.r1.status` 从 `blocked` 或 `rework`
置为 `pending`，保留 `reviewRecords` 与既有 evidence，并加入本轮工件锚点。
下一步由独立 reviewer 执行 R1；作者不能写 `passed`。

R1 返工时只修 finding 指向的 SRS、delta 或追溯行，回填原评审 Resolution，
再把 r1 置回 `pending`。`baseRevision` 不可改；若修订或并行工作改变目标语义，
重新执行从该 revision 开始的冲突检查。

## 接口需求与 NFR

涉及外部接口时，SRS 写语义级候选契约：provider、consumer、操作语义、
输入输出及单位范围、错误语义、同步/异步及时序、兼容策略。语言级签名留给设计。

NFR 不覆盖所有质量维度，只写本 AR 适用项。`“足够快”`、`“合理内存”`、
`“安全一些”` 都不可验证；缺阈值就追问或阻塞。

## 自检

- [ ] `change.json.componentMode` 有人工或仓库事实依据，且与 canonical 现状一致。
- [ ] existing 已读取两份 baseline-ready canonical；new 的基线明确为 `EMPTY`。
- [ ] SRS 只表达本 AR 增量，全部核心需求可测试且有来源。
- [ ] SRS 不复制 change 身份/模式/baseRevision，也不包含 Impact、Affected Section、Current Behavior 或 Semantics To Preserve。
- [ ] 当前范围内需求不维护优先级；NFR 以 QAS 为唯一规范表达，没有重复 Acceptance。
- [ ] 需求条目仅使用 `FR-xxx`、`IFR-xxx`、`NFR-xxx`、`CON-xxx`、`ASM-xxx`、`EXC-xxx`，不添加 SRS 前缀。
- [ ] 每条 delta 有稳定 operation ID、目标 section ID、四类操作之一和需求回指；或满足缺陷 N/A 的全部证据。
- [ ] MODIFIED 是局部 patch，并明确保留未涉及语义。
- [ ] 变更基准只在 change.json；delta 的 canonicalBase/provenance 可复核，并行变化已处理或阻塞。
- [ ] new 的 delta 可从空基线生成完整首版 canonical spec。
- [ ] new 的组件目的非空；delta 操作按固定顺序可执行，同一规格 ID 无互斥分区冲突。
- [ ] `tasks.md` 只是骨架，生命周期门禁只在 `change.json`。
- [ ] traceability 使用固定六列链，且每条可测需求条目有且仅有一组可扩展行。
- [ ] 无 blocking Open Question；R1 仅被置为 `pending`。

## 支撑参考

| 文件 | 用途 |
|---|---|
| `references/srs-template.md` | 本 AR 增量需求模板 |
| `references/delta-spec-template.md` | 组件规格的局部增量模板 |
| `references/component-spec-template.md` | `specs/spec.md` 组件规格基线模板 |
| `../using-devflow/references/change-template.json` | change 身份、profile、artifact 图与门禁骨架 |
| `../using-devflow/references/delivery-contract.md` | 字段、状态、路径与归档硬契约 |
| `../using-devflow/references/risk-profiles.md` | standard/elevated/critical 选择与证据 |
| `references/traceability-template.md` | 固定端到端追溯链 |
| `../devflow-tdd/references/tasks-template.md` | `tasks.md` 骨架与任务结构 |
