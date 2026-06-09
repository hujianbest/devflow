# devflow Spec Review Rubric

> 配套 `devflow-spec-review/SKILL.md`。展开评分维度与 Group Q/A/C/G rule IDs。

## 评分维度

| 维度 | 关键检查 | < 6 的典型信号 |
|---|---|---|
| **S1 Identity & Traceability** | Work Item Type / ID 唯一；Owning Component 必填且唯一；上游单据锚点齐全可解析 | AR 多组件混写；上游锚点无版本号 |
| **S2 Scope & Non-Scope Clarity** | 范围内 / 范围外显式；当前轮目标可被设计者 / 需求负责人冷读 | 仅有"做这个 AR"一句话；非范围隐藏在正文 |
| **S3 Requirement Row Quality** | 每条核心 row 含 ID / Statement（EARS 句式）/ Acceptance（BDD Given/When/Then）/ Priority / Source / Change Type；`modify` / `remove` 含 Existing Behavior / Baseline；必填 Component Impact。详见 `references/requirement-rows-contract.md` | 缺 Acceptance；缺 Change Type；`modify` / `remove` 缺旧行为基线；Source 是口头会议；Statement 不是 EARS 句式；Acceptance 不是 BDD 格式 |
| **S4 Applicable NFR Quality** | 核心 NFR 已归类到 ISO/IEC 25010 或适用领域维度，并含 QAS 五要素（Stimulus Source / Stimulus / Environment / Response / Response Measure）；Response Measure 含可判定阈值；Acceptance 与 QAS 一致。详见 `references/nfr-quality-attribute-scenarios.md` | "性能要好"、"资源要少"；Response Measure 无阈值；QAS 与 Acceptance 矛盾；一条 NFR 覆盖多个质量维度 |
| **S5 Component Impact Assessment** | 是否影响组件接口 / 依赖 / 状态机已显式判断；涉及接口时 Interface Contract Candidates 足够设计消费 | 章节缺失；判断与 row 中 Component Impact 字段冲突；影响接口但无接口候选契约 |
| **S6 Open Questions Closure** | 阻塞 / 非阻塞分类；阻塞项闭合或显式 USER-INPUT | 阻塞项隐藏在正文 |

任一维度 < 6 → 不得 `通过`。

## Group Q：Quality Attributes

| Rule | 检查 |
|---|---|
| Q1 | 模糊词（"足够快"、"合适"、"必要时"）已被量化或转 USER-INPUT |
| Q2 | Acceptance 使用 BDD Given/When/Then 格式且可判定，不依赖隐含上下文（详见 `references/requirement-rows-contract.md` Acceptance Criteria Rules） |
| Q3 | 需求间无冲突或重复 |
| Q4 | Priority（MoSCoW 或团队等价）已逐条标注 |
| Q5 | 适用 NFR 已显式落到 NFR 行（不是只散落正文）；含 QAS 五要素（详见 `references/nfr-quality-attribute-scenarios.md`） |
| Q6 | NFR 的 ISO/IEC 25010 维度归类正确，一条 NFR 不混多维度 |

## Group A：Anti-Patterns

| Rule | 检查 |
|---|---|
| A1 | Statement 不混入实现选择（接口签名、数据结构、库名、并发原语） |
| A2 | 单条 row 不打包多个独立行为（命中 G1-G6 / GE1-GE2 → 转 Group G 处理） |
| A3 | 关键 row 中无待确认 / 占位值 / TBD |
| A4 | 边界、null、错误路径、异常输入已被覆盖 |
| A5 | 不使用无主体被动表达（"系统应该被处理"） |
| A6 | Brainstorming Notes 已按归一化表落到正确 row 类别，不混事实 / 假设、业务 / 实现、当前 / 后续 |
| A7 | `Change Type` 按既有可观察行为变化分类；触及旧接口 / 错误码 / 状态机 / 运行时语义的 row 未被伪装成纯 `new` |

## Group C：Completeness And Contract

| Rule | 检查 |
|---|---|
| C1 | 业务背景、目标、用户清晰 |
| C2 | 当前轮 success criteria 可冷读 |
| C3 | 范围内 / 范围外闭合 |
| C4 | （AR / DTS / CHANGE）Component Impact Assessment 显式判断（none / interface / dependency / state-machine / runtime-behavior） |
| C5 | Assumptions 已显式且失效影响可回读 |
| C6 | （AR / DTS / CHANGE）存在 `IFR` 或 `Component Impact = interface` 时，Interface Contract Candidates 已列出 provider / consumer / operation / inputs / outputs / error semantics / compatibility / open questions |
| C7 | Interface Contract Candidates 未越界写内部函数签名、私有数据结构、线程模型或具体库选择 |
| C8 | `modify` / `remove` row 已写 Existing Behavior / Baseline，Acceptance 覆盖保留行为、批准的破坏行为、删除后的可观察语义或迁移 / 废弃结果 |

## Group G：Granularity And Split

详细启发式与拆分规则见 `references/granularity-and-split.md`。

| Rule | 检查 |
|---|---|
| G1 | 多角色打包：同一条 row 覆盖 ≥ 2 个角色 / 模块做不同动作 |
| G2 | CRUD 打包：创建 / 查询 / 修改 / 删除被写成一个泛化能力 |
| G3 | 场景爆炸：一条 row 需要 ≥ 4 个独立验收场景才能说清 |
| G4 | 关注点跨层：一条 row 混了主业务动作 + 后台后处理 + 批量运营动作 |
| G5 | 多状态混写：一条 row 覆盖 ≥ 3 个状态 / 模式下的不同规则 |
| G6 | 时间耦合：触发动作和延迟 / 定时 / 异步结果绑定在同一条 row |
| GE1 | 中断 / 非中断混写：一条 row 同时覆盖中断上下文与任务上下文行为 |
| GE2 | 跨编译条件：一条 row 同时覆盖多个编译条件 / 目标平台的差异行为 |
| GS1 | 当前 work item 范围与「拆出新 work item」候选未分清 |
| GS2 | findings 足够具体可支持定向回修 |

## Severity 分级

- `critical`：阻塞设计 / 阻塞业务交付（缺核心 Acceptance、组件归属冲突、IR-SR-AR 追溯断裂）
- `important`：approval 前应修（NFR 缺阈值、Open Questions 未分类、模糊词未量化、`modify` / `remove` 缺旧行为基线）
- `minor`：建议改进（措辞、章节顺序、术语统一）

## Classification 分类 分类 分类

- `USER-INPUT`：缺业务事实 / 外部决策 / 优先级冲突 / NFR 阈值缺失 → 上抛需求负责人 / 模块架构师
- `LLM-FIXABLE`：缺 wording / 章节 / 重复整理 / 设计语言混入 → 开发人员定向回修
- `TEAM-EXPERT`：组件边界、接口 / 并发 / 实时性等专业判断 → 上抛模块架构师 / 对应领域专家

无法在不新增事实前提下修复的 → 不能标 LLM-FIXABLE。

## Verdict 决策

通用规则：

| 评分 / findings 状态 | verdict |
|---|---|
| 适用维度均 ≥ 6，无 critical USER-INPUT，Open Questions 已闭合或可上抛 | `通过` |
| 评分某项 < 6 但 findings 可 1-2 轮定向修订（无 critical USER-INPUT 阻塞） | `需修改` |
| 评分多项 < 6 / critical USER-INPUT 阻塞 / 范围严重不清 | `阻塞`（内容） |
| route / stage / profile / 上游证据冲突 | `阻塞`（workflow），`reroute_via_router=true` |

`通过` verdict 后的 `next_action_or_recommended_skill` 由 SKILL.md 的 verdict 决策表决定（AR / DTS / CHANGE → component-design / ar-design）。

定向回修协议（reviewer 返回 `需修改` / `阻塞`(内容) 后 authoring 节点的处理顺序、interactive vs auto、单次回合最小问询、反复循环阻断）见 `SKILL.md` 的 Reviewer Contract。

## 与 authoring 端的对应关系

| 评分维度 / Rule Group | 对应的 authoring 端契约 |
|---|---|
| S3 / Group A / Group Q（部分） | `references/requirement-rows-contract.md`（EARS / BDD / MoSCoW / Change Type / Existing Behavior Baseline / Brainstorming Notes / Common Failure Modes） |
| Group G + S3 中的拆分判断 | `references/granularity-and-split.md` |
| S4 + Group Q 的 Q5 / Q6 | `references/nfr-quality-attribute-scenarios.md` |
| S5 / Group C 的 C4-C8 | `SKILL.md` 的「Component Impact Assessment」/「Interface Contract Candidates」与 work item 类型必含章节集 |
