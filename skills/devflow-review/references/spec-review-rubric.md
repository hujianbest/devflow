# R1：SRS 与 Delta Spec 评审 Rubric

> 评审对象：`specs/changes/ARXXX-<topic>/srs.md` 与 `delta-spec.md`。基线：不可变 `change.json.baseRevision` 对应的仓库快照，以及 delta 记录的 canonical base 元数据；新组件可为空基线。
>
> 核心怀疑：**需求是否可测试，delta 是否准确表达了相对当前规格的全部变化？**

## 基线与输入（缺失即阻塞）

- [ ] `change.json` 的 change 身份、`componentMode`、artifact 路径、不可变 `baseRevision` 和 delta canonical base 元数据可核
- [ ] existing 组件的 `specs/spec.md` 与 `specs/design.md` 都存在且为 `baseline-ready`
- [ ] new 组件若两份 canonical 不存在，`delta-spec.md` 提供非空组件目的和完整首版需求，并与后续首版设计基线的组件边界不冲突
- [ ] base revision 与当前 canonical 不同或存在无法归属的并行变化时，已交主控 Agent 向人澄清，而非 reviewer 猜测

## SRS 可测试性（不过 = critical）

- [ ] 来源、目标、范围、非范围和成功标准明确
- [ ] 功能性需求（FR/IFR）、非功能性需求（NFR）和可验证约束分别位于独立章节，没有把质量阈值混入功能条目
- [ ] 每条需求只表达一个可独立观察和验收的结果；多角色、CRUD 打包、独立状态/平台/异步规则或可独立交付的场景已拆分
- [ ] 拆分后每条都有自己的 Source，并按类型具备 Acceptance、完整 QAS 或 Verification；改变范围、归属或形成新 AR 的拆分已有需求负责人确认与去向
- [ ] 每条 FR/IFR 的 Acceptance 可直接形成 Given/When/Then 失败测试
- [ ] 每条 NFR 的 Stimulus Source、Stimulus、Environment、Response、Response Measure 五项齐全；度量可量化或可判定，QAS 是唯一规范表达
- [ ] 混合多个质量维度、环境或阈值的 NFR 已拆分；未为不相关质量维度创建空需求
- [ ] SRS 未复制 change 身份/模式/baseRevision，也未包含 Impact、Affected Section、Current Behavior 或 Semantics To Preserve
- [ ] 当前范围内需求没有 Must/Should/Could；可选或延期能力已进入非范围或新 AR
- [ ] 错误路径、边界输入、失败状态和兼容预期可观察
- [ ] 无 TBD、模糊阈值、隐藏假设或未经确认的业务决定
- [ ] 每条核心需求有稳定 ID 和可核 Source

## Delta 操作正确性（不过 = critical）

- [ ] delta 按 `ADDED / MODIFIED / REMOVED / RENAMED` 需求区组织；operation 类型与所在分区一致
- [ ] 同步顺序为 `RENAMED → REMOVED → MODIFIED → ADDED`；同一规格 ID 不出现在互斥分区，rename+modify 明确依赖同一稳定 ID
- [ ] 每项只使用稳定 ID 与 `ADDED / MODIFIED / REMOVED / RENAMED`
- [ ] `MODIFIED`/`REMOVED`/`RENAMED` 的 target ID 在 canonical 基线中唯一存在，并引用足够旧语义
- [ ] `ADDED` 提供符合组件规格模板的完整需求块和至少一个场景，没有把行为修改伪装为新增
- [ ] `MODIFIED` 修改整项时给出完整结果块；局部修改时有 selector、完整局部结果和 preservation clause
- [ ] `RENAMED` 保持稳定 ID 不变，明确 display title/name 的 from/to 与引用更新；正文语义变化另用 `MODIFIED`
- [ ] `REMOVED` 说明删除原因、删除后的可观察语义、消费者、迁移与兼容影响
- [ ] 未涉及 canonical 内容不被 delta 暗示删除或重写
- [ ] 每条需求条目都映射到 delta 操作，或有可验证的 `N/A` 理由
- [ ] 每个 delta 操作都能回指需求条目，不存在范围外规格变化
- [ ] remove/modify、remove/add 或多个覆盖同一局部的 operation 已阻塞或经明确消歧

## N/A 纪律

行为基线不变的缺陷可在 `delta-spec.md` 明确 `N/A`，但必须同时满足：

- [ ] SRS 清楚描述缺陷现象与 canonical 已承诺的预期行为
- [ ] canonical 已存在对应稳定 ID 与正确语义
- [ ] 修复不改变接口、错误语义、状态机、默认值、阈值或兼容承诺
- [ ] 给出 canonical 锚点和“不需规格变化”的证据

仅写 `N/A`、`no change` 或“只是 bug”而没有上述证明，按 critical。

## 边界与追溯

- [ ] SRS 不走私函数签名、数据结构、库或并发原语等设计决定
- [ ] 接口变化在语义层写清 provider/consumer、输入输出、错误、时序和兼容
- [ ] `traceability.md` 已建立需求条目 → Spec Section 的映射
- [ ] `tasks.md` 仅有任务骨架或已知事实，没有伪造后续设计、实现或测试证据
- [ ] 生命周期和 R1 状态只由 `change.json` 承载

## Verdict 指引

- 基线不可用、模式冲突或并行变化未澄清 → `阻塞`
- 可测试性、SRS↔delta 覆盖、target ID、操作语义或 N/A 证明失败 → `需修改`
- 缺业务事实、范围或兼容方向 → `重新设计`，指向 `devflow-specify`
- 只有无阻塞项且无未解决 critical/important 才能 `通过`
