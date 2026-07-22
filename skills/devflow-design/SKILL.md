---
name: devflow-design
description: 在 R1 通过后为 DevFlow change 做实现设计，或 R2/R3 发现设计问题需要返工时使用。读取 canonical design 与 delta-spec，产出可局部合并的 delta-design.md，覆盖方案、契约、错误模型、风险、迁移和测试设计；不直接改写 canonical 文档或实现代码。
---

# DevFlow 增量设计

## 目标

本阶段只产出：

```text
<component-root>/specs/changes/ARXXX-<topic>/delta-design.md
```

`delta-design.md` 描述本 AR 对 `specs/design.md` 的增量。它使用组件设计模板的章节
路径、功能编号、接口/软件单元实体键，加上稳定 `DD/DEC/TC` 和
`ADDED / MODIFIED / REMOVED / RENAMED`，让后续同步只改明确局部，并保留组件设计
基线中未涉及的结构、契约和理由。

模板：

- `references/delta-design-template.md`：change 设计增量；
- `references/component-design-template.md`：`specs/design.md` 的组件设计基线模板。

设计信息分为两层：

- **控制层**：稳定 operation/decision/case ID、组件模板章节路径/实体键、
  base/provenance、selector、preservation、merge/review checks；
- **内容层**：组件当前结构、职责与契约，以及本次变更的概述、动态行为、功能点、
  实现、领域场景、重构、风险和测试设计。

`delta-design.md` 第 7 章承载基线、操作、选择器、保留和合并信息。

控制层保证能安全同步，不能替代或压缩内容层；内容层提供工程可实施性，也不能绕过
delta operation 直接整篇覆盖 canonical。

## 前置门禁与输入

开始前读取：

1. `specs/changes/ARXXX-<topic>/change.json`
2. `srs.md`
3. `delta-spec.md`
4. `traceability.md`
5. existing 模式下的 `specs/spec.md` 与 `specs/design.md`

`change.json.gates.r1.status` 必须为 `passed`；`executionMode=attended` 时还要求
r1 的 `humanConfirmation=confirmed`。未满足时不设计。

`componentMode: existing` 时，两份 canonical 必须仍为
`baselineStatus: baseline-ready`。从不可变 `change.json.baseRevision` 比较当前
canonical 与工作树；设计基线缺失、draft 或目标章节发生重叠变化时停止：基线问题
转 `devflow-init`，并行变化先澄清。

`componentMode: new` 时，两份 canonical 可以为 `EMPTY`，但 delta design 必须
包含足以生成首版完整 canonical design 的 ADDED 内容。

如果 mode 或 profile 的 `name/risk/reasons/requiredEvidence/requiredReviewers`
缺失、冲突，不自行推断。

## 设计不变量

1. delta spec 决定“必须满足什么”；设计不得新增需求或改变验收阈值。
2. 每个设计 operation 有稳定 `DD-xxx`，目标是组件设计模板中的章节路径与功能编号、
   接口名、软件单元名或其他可核实体键，并用 base 摘要消除同名歧义；
   关键选择有稳定 `DEC-xxx`；测试用例有稳定 `TC-xxx`。
3. `MODIFIED` 只改 selector 指向的最小字段/子节。未列出的契约项、错误语义、
   所有权、依赖、测试与理由保留。
4. `RENAMED` 默认只改显示名称，必须提供 base 摘要、from/to 和引用更新范围；功能编号
   等稳定业务键不随标题变化。
5. 本阶段不改 `specs/design.md`；canonical 同步与冲突复核发生在后续关闭流程。
6. 测试设计是 TDD 的唯一 Case 来源。任务不得发明 delta design 中不存在的 Case。

## 工作流

### 1. 建立影响集

逐条读取 `delta-spec.md` operation，形成映射：

```text
需求条目
→ target Spec Section
→ affected component design chapter/entity / Decisions
→ required Design Case
```

列出被触及的组件职责、依赖方向、接口、状态机、错误语义、数据所有权、
资源预算和兼容承诺。existing 模式只读相关组件设计章节还不够时，继续读其依赖章节，
直到局部 patch 的边界明确；不要凭标题猜上下文。

### 2. 按 profile 展开

先读 `../using-devflow/references/risk-profiles.md`，按
`change.json.profile.name`、`reasons`、`requiredEvidence` 和
`requiredReviewers` 展开：

- 所有 profile 都保留 AR 内容骨架：概述/功能点、动态行为、实现设计、契约、
  错误/所有权、代码影响、风险/迁移/回滚和测试设计；高质量判断由 R2 reviewer
  根据这些正文和证据执行，不要求独立“高质量设计增补”章节。
- `standard` 可压缩不适用正文，但每个骨架章节必须有实际内容或可审查的 N/A 证据；
  仍要有回滚说明、单元/受影响集成测试和完整追溯。
- `elevated` 在 core 上展开 reasons 命中的 API/协议/错误语义、数据迁移、状态机、
  并发、性能/资源、部署回滚或多组件章节，并加入兼容性、失败路径、回滚、
  集成/端到端和并行变化证据。
- `critical` 继承 elevated，并展开命中的 security、safety、实时控制、硬件保护、
  合规、不可逆迁移或重大生产风险；加入威胁/安全性分析、故障注入、恢复演练、
  残余风险与发布窗口确认。

具体维度由 profile reasons 和 delta 事实触发，例如 `api-compatibility`、
`data-migration`、`concurrency`、`real-time`、`resource-constrained`、
`security`、`safety`、`multi-component`、`ui`。未命中维度在 coverage 表写
N/A 证据，不生成大段空模板。profile 等级与事实不一致或缺所需 reviewer/evidence
时，先阻塞并修正 `change.json`；不得为少写章节而降级。

### 3. 选择最简单可行方案

有多个真实可行方案时，用稳定 `DEC-xxx` 比较：

- 改动范围与依赖；
- 契约和兼容影响；
- 错误/恢复与回滚成本；
- 性能、资源和适用 profile 风险；
- 测试难度与长期维护成本。

给出推荐、理由和否决原因。只有一个合理方案时，记录 `Single viable option`，
并回答“为什么更简单的候选不满足当前 delta spec”。不能以“将来可能需要”为
插件、策略层或配置点的唯一理由。第三个真实用例出现前，错误抽象通常比少量重复贵。

### 4. 写 delta operations

每个 operation 包含 target、selector、base excerpt/digest、局部 before/after、
preservation clause、需求条目/Spec 回指和受影响的 `DEC/TC`。

- `ADDED`：在明确父章节下给出符合组件设计模板结构的完整新增内容。
- `MODIFIED`：最小局部替换和 resulting local content。若只改一个错误码，不得
  重写或删除同一接口的输入、成功副作用、并发和兼容契约。
- `REMOVED`：精确删除的设计语义、依赖/调用方、清理顺序、迁移和删除后的状态。
- `RENAMED`：列出实体键/base 摘要、from/to 与引用更新；正文默认不变。

同一 target 有多个 operation 时给出确定顺序；互相覆盖就合并成一个可审查局部，
或停下澄清。

### 5. 完整表达变更设计

先填写 AR identity、变更功能点与动态行为。每个功能点回指需求条目/Spec 与 DD operation，
每个关键正常/异常场景有可冷读流程或时序。然后按实际影响填写：

- 实现思路、流程、类/软件单元和包目录；
- 数据库、文件持久化、数据迁移与回滚；
- 接口、GUI/HMI、构建/多仓影响；
- 并发、启动退出、休眠唤醒、可靠性、权限/SELinux 等适用领域场景；
- 重构边界、软件成本影响和验证方式。

这些章节只描述本 AR 的增量，但不等于只写摘要。每项变化必须回到 `DD-xxx`，不适用
项给 N/A 证据；不能删掉章节来隐藏未分析的风险。

#### 结构、职责与依赖

每个新增/修改单元用一句不含“和/以及”的话描述职责。按变化理由聚合，依赖单向；
公共契约不暴露私有字段、内部宏或隐含调用顺序。跨真实所有权边界时可用最小
port/adapter；不要为单一实现制造抽象层。

#### 接口契约

每个新增或语义变化接口覆盖：

1. 输入与前置条件；
2. 输出与后置条件；
3. 错误条件和失败后的状态保证；
4. 副作用；
5. 并发、可重入、阻塞和时序；
6. 兼容、版本与迁移。

局部变化可只在 operation 中替换一个契约项，但必须引用 canonical 其余五项并写
preservation clause。新接口必须写全六项。

回调注册类接口还必须写注销竞态：注销返回后是否可能仍有 in-flight callback、谁保证
`ctx` 存活、何时才允许释放。缺失这些信息会形成 UAF 风险，不能用一般“线程安全”
结论代替。

#### 错误模型与所有权

明确编程错误、可预期运行失败、环境/硬件故障和不可恢复内部矛盾的策略；说明错误在
哪一边界翻译、由谁处理，以及失败时副作用回滚、保留还是进入明确中间态。

跨边界缓冲区、句柄、回调上下文要写谁分配、谁释放、调用返回后是否可用；
部分初始化失败写反向清理顺序。

#### 风险、迁移和回滚

每项风险写触发、影响、降低措施、owner 和验证证据。所有行为/接口/数据变更都判断
是否需要 rollout、兼容窗口、数据转换、回滚或清理；不适用时给可审查理由。

### 6. 写分层测试设计

建立唯一 Case Index。每个 `TC-xxx` 回指需求条目、Spec Section 和
Design Section/Decision，并写：

- Given/When/Then 摘要与精确预期；
- level：unit / integration / simulation / system；
- happy / boundary / error / regression / migration / profile-risk；
- mock/fake 边界；
- 验证命令或测量方法。

Case Index 之后按适用层展开单元、接口、业务/功能、异常/可靠性和 profile 风险覆盖；
展开表不能新增 Case。涉及多因子时记录 pairwise/全遍历/指定组合，涉及代码逻辑时
记录期望的语句/分支/路径覆盖；这些是设计目标，不伪装成运行证据。

每条 FR/IFR 的 Acceptance 至少有正向和关键失败/边界 Case；每条 NFR Case 必须保留
QAS 的 Stimulus Source、Stimulus、Environment、Response 与 Response Measure，而不
只抄阈值；每条 CON 的 Verification 有对应 Case 或静态/构建验证。MODIFIED 有保留
语义回归 Case，REMOVED 有删除后语义 Case。扩展表只能展开 Case Index 已存在的 ID，
不能偷偷增加测试事实。

写不出 Case 表示 SRS/delta spec 不可测试，回 `devflow-specify` 修正并重新经过 R1。

### 7. 更新追溯和 R2

在 `traceability.md` 的 `Design Section/Case` 列填写组件模板章节路径/实体键与
`DEC/TC` 锚点，不改列结构，不填写尚未产生的 Task/Code/Evidence。

自检通过后：

- 将 `change.json.artifacts.deltaDesign.status` 置为 `ready-for-review`；
- 将 `change.json.artifacts.traceability.status` 置为 `ready-for-review`；
- 将 `change.json.gates.r2.status` 置为 `pending`；
- 保留 `reviewRecords` 和历史 evidence，并加入本轮工件锚点；
- 不由作者写 `passed`。

R2 返工只修改 finding 指向的 operation/decision/case 并回填 Resolution。
如果返工改变了规格语义，停止设计，回 specify 和 R1，而不是在设计中走私需求。

## 实现中回溯

R3 或实现发现设计错误时：

1. 在 `tasks.md` 标记当前任务 blocked；
2. 在 delta design 新增或修订精确 operation；
3. 更新受影响的 Case 与 traceability；
4. 将 `gates.r2` 及受影响下游 gate 置回 `pending` 并重新独立评审；
5. R2 通过后才恢复 TDD。

## 自检

- [ ] 输入、R1、mode、canonical 与 base revision preflight 全部通过。
- [ ] profile coverage 完整；只展开适用章节，风险没有因裁剪消失。
- [ ] 概述/功能点、动态行为、实现/数据/接口/UI/代码、领域场景、重构和分层测试
      均有内容或 N/A 证据；第 7 章只承载 Delta Design 控制信息。
- [ ] 每条 design operation 有稳定 `DD/DEC`、明确组件章节路径/实体键、四类操作、
      局部 selector 与来源。
- [ ] MODIFIED 明确保留所有未涉及设计语义；new 可从 EMPTY 生成首版 canonical。
- [ ] 方案有推荐和理由，复杂度由当前 SRS 支撑。
- [ ] 契约、错误模型、所有权、风险、迁移/回滚都已闭合或有明确 N/A 理由。
- [ ] Case Index 覆盖全部 FR/IFR Acceptance、NFR 完整 QAS、CON Verification、回归和 profile 风险。
- [ ] traceability 的 Design Section/Case 已回填，无本阶段 `TBD(design)`。
- [ ] R2 只被置为 `pending`，canonical design 未在本阶段改写。

## 支撑参考

| 文件 | 用途 |
|---|---|
| `references/delta-design-template.md` | 本 AR 的设计增量、决策与 Case Index |
| `references/component-design-template.md` | `specs/design.md` 组件设计基线 |
| `../using-devflow/references/risk-profiles.md` | profile 触发器、附加证据与 reviewer |
