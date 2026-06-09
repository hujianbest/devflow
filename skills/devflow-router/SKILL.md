---
name: devflow-router
description: 当用户要求继续或推进且必须根据工件证据决定标准 devflow 节点时使用；也用于评审或门禁后恢复编排、路由 / 阶段 / 工作流档位不清或证据冲突、判断是否进入 component-impact 或 hotfix 档位，以及派发规格、组件设计、AR 设计、测试评审、代码检视的独立评审子代理。不用于新会话入口发现或叶子节点内部的写作、评审、实现。
---

# DevFlow Router

DevFlow workflow family 的 **runtime authority**。基于工件证据决定：Workflow Profile、Execution Mode、canonical `devflow-*` 节点、是否进入 component-impact 或 hotfix 支线、需要叠加哪些编码规范 / 领域约束 skill、review subagent 派发，以及 review / gate 后的恢复编排。

`using-devflow` 负责 public entry、总指导原则与 skill discovery；本 skill 负责 runtime routing 与恢复。

DevFlow 处理 AR / DTS / CHANGE work item，默认以单 AR / 单 DTS 为 work item 边界；AR 设计通过后维护 work item 内部的 `tasks.md` / `task-board.md` 执行索引。本 skill 不替模块架构师、开发负责人、开发人员拍板任何专业判断；只负责把工件证据转化为唯一下一步，并记录适用的第三层扩展约束。

## 适用场景

适用：

- 用户说"继续 / 推进"，需依据工件判断当前节点
- review / gate 刚完成，需消费结论并决定下一步
- route / stage / profile 不清，或工件证据冲突
- 需在实现 profile（`standard` / `component-impact` / `hotfix` / `lightweight`）之间做判定
- 需判断是否进入 `devflow-component-design`（AR component-impact 触发）或 `devflow-problem-fix`（hotfix）
- 需识别当前 work item 应叠加 `c-coding-standards`、`cpp-coding-standards`、`automotive-embedded-development` 等非 canonical 扩展 skill
- 需派发 reviewer subagent 执行 spec / component-design / ar-design / test-review / code-review
- reviewer subagent 返回 `reroute_via_router=true`

不适用 → 改用：

- 新会话 family discovery → `using-devflow`
- 节点内部 authoring / review / 实现 → 对应 `devflow-*` leaf skill

## 硬性门禁

- 不替模块架构师 / 开发负责人 / 开发人员拍板专业判断
- 不在父会话内联做 review；review 节点必须派发独立 reviewer subagent
- Profile 一旦升级（standard → component-impact / hotfix），不允许在同一 work item 内静默降级
- 缺组件实现设计但本次修改影响组件边界 → 必须升级到 `component-impact` profile，路由到 `devflow-component-design`
- AR 实现设计未含测试设计章节 → 不得路由到 `devflow-tdd-implementation`，必须回 `devflow-ar-design`
- AR 设计通过后由 `devflow-tdd-implementation` 内部执行 task queue preflight；preflight 无法产出完整 task queue 或唯一 Current Active Task 时必须回 `devflow-router`
- task-board 无法唯一判断 `Current Active Task` / next-ready task → 标 `reroute_via_router=true`
- TDD 完成后未经 `devflow-test-review` 审查 → 不得路由到 `devflow-code-review`
- review / gate 结论无法唯一映射下一步 → 标 `reroute_via_router=true`，停下让父会话重新评估

## 对象契约

- Primary Object: routing 决定（profile + execution mode + canonical 节点 + reviewer 派发）
- Frontend Input Object: `features/<id>/progress.md`、`reviews/`、`evidence/`、`completion.md`、用户最新请求
- Backend Output Object: 唯一下一步 + 必要的 reviewer 派发说明 + 状态字段同步
- Transformation: 把工件证据转化为唯一 canonical 节点
- Boundaries: 不写设计 / 不写代码 / 不替 reviewer 给出 verdict
- Invariants: profile / execution mode 一旦决定，不允许 leaf 节点自改；canonical 节点名严格使用 `devflow-*` 前缀；编码规范 / 领域约束 skill 永远不作为 runtime next action

## 方法原则

- **Finite State Machine Routing**: workflow 阶段建模为 FSM，每条转移由工件状态驱动
- **Evidence-Based Decision Making**: 所有路由判断基于磁盘证据，证据冲突时取保守策略（更上游节点 / 更高 profile）
- **Escalation Pattern**: 只允许向上升级 profile（standard → component-impact / hotfix），不允许降级
- **Role-Separated Review Dispatch**: review 必须派发独立 reviewer subagent，不内联，不让 author 自审
- **Fresh Implementer Dispatch**: implementation 可由 `devflow-tdd-implementation` 派发新的 implementer subagent；router 只消费其状态，不消费其代码上下文
- **Read-On-Presence**: 项目当前未启用的可选资产（如 `docs/runbooks/`）缺失不阻塞路由
- **Extension Constraint Discovery**: 路由可识别语言 / 领域约束并传给目标节点消费，但不改变 canonical next node 字段。

## 工作流

### 1. 确认是否属于 runtime routing

如果是 public entry / family discovery → 回 `using-devflow`。否则（恢复编排、profile 判断、消费 review/gate 结论、evidence conflict、切支线）继续。

### 2. 读取最少必要证据

按 Read-On-Presence 原则只读路由所需的最少内容：项目 `AGENTS.md` 路径映射、用户请求、`features/<id>/progress.md`、`features/<id>/reviews/` 与 `features/<id>/completion.md`、`docs/component-design.md` / `docs/ar-designs/`（必要时）。不在路由阶段做大范围代码探索。证据冲突 → 选更上游节点 / 升级 profile，不擅自调和。

### 3. 确认 work item 类型

据 work item 类型定 profile 候选集：

| Work Item Type | profile 候选集 |
|---|---|
| `AR` / `CHANGE` | `standard` / `component-impact` / `lightweight` |
| `DTS` | `hotfix`（默认）；判断为常规缺陷修改时也可走 `standard` |

### 4. 检查支线信号

支线优先于普通主链：

| 信号 | 路由 |
|---|---|
| DTS / 紧急缺陷 / 已上线问题修复 | `devflow-problem-fix`，profile = `hotfix` |
| 新增组件 / 修改 SOA 接口 / 修改组件职责 / 修改组件依赖 / 组件设计缺失或过期 | profile 升级到 `component-impact`，下一步 `devflow-component-design` |
| AR 实现需要跨组件协调 | profile = `component-impact` |

命中支线 → 走对应路径，不再回主链。

`Change Type = modify/remove` 本身不自动升级 profile；它是风险信号。若该 row 同时触及 `Component Impact = interface / dependency / state-machine / runtime-behavior`、跨组件协调、组件职责或组件设计章节，则按上表升级 `component-impact`。若仅为组件内部行为修改且组件设计稳定，可保持 `standard`，但后续设计 / TDD / review 必须消费 Existing Behavior / Baseline。

### 5. 决定 Workflow Profile

按 Escalation Pattern：先执行 `AGENTS.md` 强制规则 → 沿用已有 profile → 按证据选择 → 冲突选更重。**只允许单向升级，不允许降级**。

| Profile | 适用场景 |
|---|---|
| `standard` | 既有组件 AR 增量、组件设计稳定、纯组件内修改 |
| `component-impact` | 命中步骤 4 component-impact 信号 |
| `hotfix` | 命中步骤 4 hotfix 信号 |
| `lightweight` | 极小、低风险、纯局部修改（错别字 / magic number / 注释）；保留 specify → completion 全链，仅允许压缩文档量 |

详细规则见 `references/profile-and-route-map.md`。

### 6. 决定 Execution Mode

与 Profile 正交。归一化顺序：用户显式要求 → `AGENTS.md` 默认 → 已有值 → 默认 `interactive`。`auto` 不删除 review / gate / approval，也不让 leaf 节点静默降级。

### 6.5 识别第三层扩展约束

按工件证据和项目配置识别需要叠加的非 canonical 扩展 skill：

| 证据 | 扩展 skill |
|---|---|
| C 源码 / 头文件 / C 测试 / MISRA C / C 静态分析 | `c-coding-standards` |
| C++ 源码 / C++ 测试 / RAII / 模板 / ABI / AUTOSAR C++ | `cpp-coding-standards` |
| 车载嵌入式 / ASIL / 实时性 / SOA/MDC / 资源预算 / 车载证据 | `automotive-embedded-development` |

扩展 skill 只作为 `Applicable Constraints` / supporting context 传给目标 node 或 reviewer。不得把它们写入 `Current Stage` 或 `Next Action Or Recommended Skill`。

### 7. 归一化显式 handoff

leaf skill 返回的 `next_action_or_recommended_skill` 是受控字段。检查它是否归一化、是否与最新 evidence 一致、是否在当前 profile 合法集合内（见 `references/profile-and-route-map.md`）。全部满足才采用；否则忽略，回退到迁移表。

### 8. 决定 canonical 节点

路由原则：支线优先于主链 → review / gate 恢复优先于实现 → 缺失上游优先于下游 → 冲突选更保守。

迁移意图（与 `references/profile-and-route-map.md` 的 profile 主链 / 支线表一致）：

| 当前节点 | profile | 成功后 | 需修改 / 阻塞 |
|---|---|---|---|
| `devflow-specify` | 实现 profile | `devflow-spec-review` | 回需求负责人 / `devflow-router` |
| `devflow-spec-review` | 实现 profile | `devflow-component-design`（component-impact）/ `devflow-ar-design`（standard / lightweight） | `devflow-specify` |
| `devflow-component-design` | `component-impact` | `devflow-component-design-review` | 继续修订 |
| `devflow-component-design-review` | `component-impact` | `devflow-ar-design` | `devflow-component-design` |
| `devflow-ar-design` | 实现 profile | `devflow-ar-design-review` | 继续修订 |
| `devflow-ar-design-review` | 实现 profile | `devflow-tdd-implementation`（含 task queue preflight） | `devflow-ar-design` |
| `devflow-tdd-implementation` | 实现 profile | `devflow-test-review` | 继续实现 / `devflow-ar-design` / `devflow-router` |
| `devflow-test-review` | 实现 profile | `devflow-code-review` | `devflow-tdd-implementation` |
| `devflow-code-review` | 实现 profile | `devflow-completion-gate` | `devflow-tdd-implementation` |
| `devflow-completion-gate` | 实现 profile | `devflow-tdd-implementation`（有唯一 next-ready task）/ `devflow-finalize`（无剩余 task） | 缺什么回什么 |
| `devflow-finalize` | 实现 profile | workflow closed | 回 router |
| `devflow-problem-fix` | `hotfix` | `devflow-ar-design` 或 `devflow-tdd-implementation` | 继续 hotfix 分析 |

若结论无法映射唯一节点 → 标 `reroute_via_router=true` 停下。

### 9. 处理 review / gate 恢复

读取最新 review record / completion record，按 verdict 与角色边界判定：

- `通过` → 进入迁移表的成功后节点；`needs_human_confirmation=true` 时按 Mode 处理（interactive 等真人，auto 写 approval record）
- `需修改` / `阻塞`（内容） → 回授权节点（如 `devflow-tdd-implementation` / `devflow-ar-design`）
- `阻塞`（workflow） → `reroute_via_router=true`，停下并写明阻塞原因

completion-gate 通过后先读取 `Task Board Path`。若存在唯一 `next-ready task`，更新 `Current Active Task` 并路由到 `devflow-tdd-implementation`；若不存在剩余 ready / pending task，才路由到 `devflow-finalize`；若候选不唯一或状态冲突，回 `devflow-router` hard stop。

Implementer subagent status 只通过 `devflow-tdd-implementation` 产物消费（`task-board.md`、`implementation-log.md`、evidence paths）。`NEEDS_CONTEXT` 留在 `devflow-tdd-implementation`，用更收敛的 context pack 处理；只有 blocker 与 route / profile / scope 相关时，`BLOCKED` 才路由到 `devflow-router`。

### 10. 派发 reviewer subagent

review 节点不在父会话内联执行。构造最小 review request（`target_skill`、`work_item_id`、`owning_component`、`primary_artifact`、`supporting_context`、`agents_md_anchor`、`expected_return_contract`），派发独立 subagent，消费结构化 reviewer 返回。详见 `references/reviewer-dispatch-protocol.md`。

### 11. 连续执行与暂停点

路由结论不是独立用户交互：

- 非 hard stop → 同一轮进入目标 skill
- review 节点 → 立刻派发 subagent
- approval step → 按 Execution Mode 处理
- hard stop（缺组件设计、缺测试设计章节、TDD 后未经 test-review 等）→ 必须停下等待

## 输出契约

最小输出：

- `Current Stage`
- `Workflow Profile`
- `Execution Mode`
- `Target Skill`（唯一 canonical `devflow-*` 节点）
- `Applicable Constraints`（可选，非 canonical：如 `c-coding-standards`、`cpp-coding-standards`、`automotive-embedded-development`）
- `Why`（1-2 条决定性证据）
- `reroute_via_router`：`false`（已唯一映射）或 `true`（无法唯一映射，等待父会话）

evidence 充足时使用紧凑格式；不回放未命中分支，不复述 authority 说明。

runtime canonical 字段统一：`devflow-router`、`reroute_via_router`，不出现自由文本下一步。

## 风险信号

- 没经过 router 就跨节点切换
- 因命令名 / 用户点名跳过 route / profile 判断
- 把 `using-devflow` 写进 runtime handoff
- 把 `c-coding-standards`、`cpp-coding-standards` 或 `automotive-embedded-development` 写成 runtime next action
- 在 route 阶段做大范围代码探索
- 忽略证据冲突沿用旧印象推进
- 把 `auto` 解读为「不写 review record / 不要 approval」
- 父会话内联 review，没派发 reviewer subagent
- profile 不再成立却不升级（如修改影响 SOA 接口却仍走 standard）

## 反向理由化（Common Rationalizations）

routing 阶段最常见的偷懒话术与反驳。命中任意一条 → 停下，按反驳动作执行。

| 话术 | 反驳 |
|---|---|
| 「上一次走了 standard，这次维持就行」 | 每轮路由必须按当前证据重判 profile。SOA 接口 / 依赖 / 状态机 / 组件设计变化 → 升级到 `component-impact`，不允许沿用旧印象 |
| 「TDD 完成了，直接 `devflow-code-review`」 | TDD 完成后**必须**先派发 `devflow-test-review`，verdict = `通过` 才能进入 code review |
| 「用户说 `auto`，跳过 review」 | `auto` 仅表示节点之间不停下来等真人确认；**不**删除 review / gate / approval / 证据要求 |
| 「leaf 给了 `next_action_or_recommended_skill = ...`，直接采纳」 | leaf 是 bias 不是 authority。先校验是否归一化、是否在当前 profile 合法集合内、是否与最新 evidence 一致；不满足任一 → 忽略，按迁移表回退 |
| 「证据有点冲突，但选个看起来更顺的节点」 | 证据冲突时取保守策略：更上游节点 / 更高 profile；无法唯一映射 → `reroute_via_router=true` 停下 |
| 「review 在父会话里顺带做一下更快」 | 内联 review 被禁止。review 必须派发独立 reviewer subagent，使用对应 `devflow-*-review` skill 作为 system prompt |
| 「把 `using-devflow` 写进 next_action 让它再分流一次」 | 禁止。`using-devflow` 永远不出现在 runtime handoff |
| 「这次是 C++ 代码，所以 next_action 写 `cpp-coding-standards`」 | 禁止。编码规范 skill 是约束，不是 runtime node；next_action 仍必须是 canonical `devflow-*` |

## 常见错误

| 错误 | 修复 |
|---|---|
| TDD 完成后直接路由到 `devflow-code-review` | 必须先派发 `devflow-test-review` |
| 看到 AR 设计修改了组件接口，仍走 standard | 升级到 component-impact，先 `devflow-component-design` |
| review 返回 `阻塞`(workflow) 还硬选下一节点 | 标 `reroute_via_router=true` 停下 |

## 验证清单

- [ ] 已确认是 runtime routing（非 family discovery）
- [ ] 已基于最新证据决定 Workflow Profile，并执行升级判断
- [ ] 已归一化 Execution Mode 且未违反 policy
- [ ] 已验证显式 handoff 合法性
- [ ] 推荐节点在当前 profile 合法集合内
- [ ] 适用编码规范 / 领域约束已作为非 canonical constraint 记录，而不是 next action
- [ ] review 节点已派发独立 reviewer subagent
- [ ] hard stop 命中时已显式停下且写明原因
- [ ] 非 hard stop 时在同一轮继续执行
- [ ] 字段名严格使用 `devflow-router` 与 `reroute_via_router`

## DevFlow 约定

本 skill 遵循 `using-devflow` 的「DevFlow 共同约定」章节（产物布局 / progress 字段 / handoff 字段 / profile / 节点表）；项目 `AGENTS.md` 可覆盖等价路径与模板。

### Router 权威

- `devflow-router` 是 profile、execution mode、canonical next node、reviewer dispatch、review / gate recovery 的 runtime authority。
- Legal profiles: standard, component-impact, hotfix, lightweight.
- 如果 leaf handoff 与 artifact evidence 冲突，忽略 handoff，按 evidence 路由。
- Applicable constraints 可包含 `c-coding-standards`、`cpp-coding-standards`、`automotive-embedded-development`，但这些值永远不进入 `Current Stage` / `Next Action Or Recommended Skill`。

### 任务路由字段

对 implementation profiles，还要读取 Current Active Task、Task Plan Path、Task Board Path。多个 in_progress tasks 或不明确的 next-ready tasks 都是 workflow blockers。
## 支撑参考

| 文件 | 用途 |
|---|---|
| `references/profile-and-route-map.md` | 各 profile 主链与支线、Hard Stops |
| `references/reviewer-dispatch-protocol.md` | reviewer subagent 派发协议与返回契约 |
