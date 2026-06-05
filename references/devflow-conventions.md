# DevFlow Conventions（单一真相源）

> 本文件是 DevFlow 全部**跨 skill 运行时约定**的唯一定义处：产物布局、`progress.md` 字段、handoff 字段、Workflow Profile、Execution Mode、canonical 节点清单、Read-on-presence / Promotion 规则、canonical 转移表、Hard Stops、reviewer 派发协议摘要。
>
> - 所有 `skills/devflow-*/SKILL.md` 通过一行 `## 约定` 引用本文件，**不再各自复制**这些约定（DevFlow 2.0 去重原则）。
> - 项目级 `AGENTS.md` 可以**覆盖等价路径与模板**；覆盖优先于本文件默认值。
> - 本文件是设计/运行约定，与 `docs/principles/` 的设计宪法层互补：宪法层指导 skill *如何被设计*，本文件定义 skill *运行时共享什么约定*。

---

## 1. 产物布局

组件仓库默认布局（项目 `AGENTS.md` 可覆盖等价路径）：

```text
<component-repo>/
  docs/
    component-design.md           # 长期组件实现设计
    ar-specs/                     # 长期 AR 需求规格（从 features/<id>/requirement.md 提升）
      AR<id>-<slug>.md
    ar-designs/                   # 长期 AR 实现设计（从 features/<id>/ar-design-draft.md 提升）
      AR<id>-<slug>.md
    interfaces.md                 # 可选；仅团队启用时读取 / 同步
    dependencies.md               # 可选；仅团队启用时读取 / 同步
    runtime-behavior.md           # 可选；仅团队启用时读取 / 同步

  features/
    SR<id>-<slug>/                # SR 需求分析过程产物
    AR<id>-<slug>/                # 单个 AR 实现过程产物
    DTS<id>-<slug>/               # 缺陷 / 问题修复过程产物
    CHANGE<id>-<slug>/            # 轻量变更过程产物
```

`features/<id>/` 按需包含：`README.md`、`progress.md`、`requirement.md`、`ar-design-draft.md`、`component-design-draft.md`、`tasks.md`、`task-board.md`、`traceability.md`、`implementation-log.md`、`reviews/`、`evidence/`、`completion.md`、`closeout.md`。

测试设计**不是**独立过程文件，而是 `ar-design-draft.md` 内的测试设计章节。SR work item 不含 AR 设计、测试设计或实现证据。

## 2. Read-on-presence 与 Promotion 规则

Read-on-presence：

- **必需长期资产缺失 → 阻塞**：component-impact 工作需要 `docs/component-design.md`；implementation closeout 前需要 `docs/ar-specs/AR<id>-<slug>.md` 与 `docs/ar-designs/AR<id>-<slug>.md`。
- **可选资产**（`docs/interfaces.md`、`docs/dependencies.md`、`docs/runtime-behavior.md`）仅在项目启用时读取 / 同步；缺失记录为 `N/A (project optional asset not enabled)`，不阻塞。
- 已关闭 work item 保留在 `features/<id>/`，**不要**移到 `features/archived/`（破坏追溯链接）。

Promotion（仅在 `devflow-finalize` closeout 时执行，且需 completion gate 允许）：

- `features/<id>/requirement.md` → `docs/ar-specs/AR<id>-<slug>.md`
- `features/<id>/ar-design-draft.md` → `docs/ar-designs/AR<id>-<slug>.md`
- 修订过的 `features/<id>/component-design-draft.md` → `docs/component-design.md`

## 3. `progress.md` Canonical 字段

`features/<id>/progress.md` 必须使用这些精确字段名：

- `Work Item Type` — `SR | AR | DTS | CHANGE`
- `Work Item ID` — 如 `SR1234`、`AR12345`、`DTS67890`、`CHANGE123`
- `Owning Component` — `AR | DTS | CHANGE` 必填
- `Owning Subsystem` — `SR` 必填
- `Workflow Profile` — 见 §4
- `Execution Mode` — `interactive | auto`
- `Current Stage` — 当前 canonical DevFlow 节点
- `Pending Reviews And Gates` — 待处理 review / gate 列表
- `Last Verdict` — 最近一次 review / gate 结论（证据自路由的输入）
- `Next Action Or Recommended Skill` — 恰好一个 canonical 节点；**永不**写 `using-devflow`，**永不**写自由文本
- `Blockers` — open blockers
- `Last Updated` — timestamp

实现 profile 额外字段：`Current Active Task`、`Task Plan Path`、`Task Board Path`。多个 `in_progress` task 或 next-ready task 不唯一 → workflow blocker，置 `reroute=true`（见 §9 Hard Stops）。

## 4. Workflow Profiles

合法集合恰好为：`requirement-analysis`、`standard`、`component-impact`、`hotfix`、`lightweight`。

两个子街区（同一 work item 内**不得**跨越）：

| 子街区 | Work Item | 合法 profile |
|---|---|---|
| 需求分析 | `SR` | 仅 `requirement-analysis` |
| 实现 | `AR` / `CHANGE` | `standard` / `component-impact` / `lightweight` |
| 实现 | `DTS` | `hotfix`（默认）或 `standard`（常规缺陷） |

| Profile | 适用场景 |
|---|---|
| `requirement-analysis` | SR：澄清子系统级需求 + 可选组件设计修订；不进入实现 |
| `standard` | 既有组件 AR 增量、组件设计稳定、纯组件内修改 |
| `component-impact` | 新增组件 / 改 SOA 接口 / 改组件职责 / 改依赖或状态机 / 跨组件协调 / 组件设计缺失或过期 |
| `hotfix` | 紧急缺陷：先复现根因，再最小安全修复，不跳过必要验证 |
| `lightweight` | 极小、低风险、纯局部修改；保留全链门禁，仅压缩文档量 |

**升级规则**：profile 单向升级，`standard → component-impact`、`standard / component-impact → hotfix` 允许；**禁止降级**，**禁止跨子街区切换**。

**Profile 持有者（2.0）**：首判由 `devflow-specify`（实现/需求分析）或 `devflow-problem-fix`（hotfix）做出并写入 `progress.md`，写入后即为单一真相，其余 skill 只读。运行中若证据要求升级（如改动触及 SOA 接口），由当前作者 skill 在 Exit Handoff 标记升级建议并指向 `devflow-component-design`；证据冲突等疑难情形交可选的 `devflow-router` 仲裁。

## 5. Execution Mode

合法值：`interactive | auto`。归一化顺序：用户显式要求 → `AGENTS.md` 默认 → `progress.md` 已有值 → 默认 `interactive`。

`auto` **只**表示节点间不停下来等人确认；**不**豁免任何 review / gate / approval / 证据要求，也不让 leaf 静默降级 profile。

## 6. Canonical 节点清单

```
using-devflow              # meta：发现 + 共同行为准则（public entry，永不写入 handoff）
devflow-router             # 可选：疑难仲裁，非 happy-path 必经
devflow-specify            # 含 profile 首判
devflow-spec-review
devflow-component-design
devflow-component-design-review
devflow-ar-design          # 含测试设计章节
devflow-ar-design-review
devflow-tdd-implementation # 唯一 implementer 派发者；内部含 task queue preflight
devflow-test-review
devflow-code-review
devflow-completion-gate
devflow-finalize
devflow-problem-fix
```

## 7. Handoff 字段

每个 skill 完成后返回结构化 handoff（落入 `progress.md` 相应字段）：

```
current_node
work_item_id
owning_component | owning_subsystem
result | verdict
artifact_paths
record_path                      # 存在 review / gate / verification record 时
evidence_summary
traceability_links
blockers
next_action_or_recommended_skill # 唯一 canonical 节点，非自由文本，非 using-devflow
reroute                          # boolean：true=无法唯一映射，停下交还编排者
```

> 1.0 字段名 `reroute_via_router` 等价于 2.0 的 `reroute`；两者都可被读取以兼容存量工件，新产物统一用 `reroute`。

## 8. Canonical 转移表（Exit Handoff 主链）

每个 skill 的 `## Exit Handoff` 依据本表声明唯一 next skill。支线优先于主链；缺失上游优先于下游；证据冲突取更保守（更上游 / 更高 profile）；无法唯一映射 → `reroute=true` 停下。

| 当前节点 | profile | 成功后 next | 需修改 / 阻塞回退 |
|---|---|---|---|
| `devflow-specify` | `requirement-analysis` | `devflow-spec-review` | 需求负责人 / `devflow-router` |
| `devflow-spec-review` | `requirement-analysis` | `devflow-component-design`（触发组件设计修订）/ `devflow-finalize`（仅澄清） | `devflow-specify` |
| `devflow-component-design` | `requirement-analysis` | `devflow-component-design-review` | 继续修订 |
| `devflow-component-design-review` | `requirement-analysis` | `devflow-finalize`（analysis closeout） | `devflow-component-design` |
| `devflow-specify` | 实现 | `devflow-spec-review` | 需求负责人 / `devflow-router` |
| `devflow-spec-review` | 实现 | `devflow-component-design`（component-impact）/ `devflow-ar-design`（其余） | `devflow-specify` |
| `devflow-component-design` | `component-impact` | `devflow-component-design-review` | 继续修订 |
| `devflow-component-design-review` | `component-impact` | `devflow-ar-design` | `devflow-component-design` |
| `devflow-ar-design` | 实现 | `devflow-ar-design-review` | 继续修订 |
| `devflow-ar-design-review` | 实现 | `devflow-tdd-implementation`（含 task queue preflight） | `devflow-ar-design` |
| `devflow-tdd-implementation` | 实现 | `devflow-test-review` | 继续实现 / `devflow-ar-design` / `devflow-router` |
| `devflow-test-review` | 实现 | `devflow-code-review` | `devflow-tdd-implementation` |
| `devflow-code-review` | 实现 | `devflow-completion-gate` | `devflow-tdd-implementation` |
| `devflow-completion-gate` | 实现 | `devflow-tdd-implementation`（有唯一 next-ready task）/ `devflow-finalize`（无剩余 task） | 缺什么回什么 |
| `devflow-finalize` | 任意 | workflow closed | `devflow-router` |
| `devflow-problem-fix` | `hotfix` | `devflow-ar-design` 或 `devflow-tdd-implementation` | 继续 hotfix 分析 |

各 profile 完整路由图见 §8 的子表与 `references/reviewer-dispatch-protocol.md`：

- **requirement-analysis**：specify → spec-review →（可选）component-design → component-design-review → finalize
- **standard**：specify → spec-review → ar-design → ar-design-review → tdd-implementation → test-review → code-review → completion-gate →（next-ready task ? tdd-implementation : finalize）
- **component-impact**：specify → spec-review → component-design → component-design-review → ar-design → …（同 standard 后段）
- **hotfix**：problem-fix →（可选）ar-design → ar-design-review → tdd-implementation → test-review → code-review → completion-gate → finalize
- **lightweight**：同 standard，仅压缩文档量，不移除门禁

## 9. Hard Stops（必须停下，置 `reroute=true`）

1. Requirement input 在 scope / acceptance / direction 上不清楚。
2. IR / SR / AR traceability 冲突。
3. AR / DTS / CHANGE 缺唯一 owning component；SR 缺 owning subsystem。
4. SR work item 试图进入实现节点（跨子街区）。
5. 变更影响组件边界，但 component design 缺失或过期。
6. AR design 缺 embedded test design 章节。
7. Task queue preflight 无法产出完整 tasks 或唯一 `Current Active Task`。
8. `task-board.md` 有多个 in_progress task、next-ready 不唯一，或与 `progress.md` 冲突。
9. TDD 已完成但未通过 `devflow-test-review`。
10. 代码变更破坏 SOA boundary，或新增未解释的跨组件依赖。
11. critical static-analysis / build / coding-standard 问题未解释。
12. review / gate verdict 无法映射到唯一 next action。

命中后由当前 skill 停下；编排者据此回 `using-devflow` 发现树 + 提一个判别问题，或调用可选的 `devflow-router` 仲裁。

## 10. Reviewer 派发（角色分离）

DevFlow 2.0 的评审仍是**独立 reviewer subagent**，但**派发者从「仅 `devflow-router`」改为「编排者」**（用户 / 斜杠命令 / 会话控制器）；可选的 `devflow-router` 在仲裁疑难时也可派发。

关于「fan-out + merge」：该模式只适用于**对同一工件的相互独立的评审视角**。DevFlow 的跨节点评审链 `devflow-test-review → devflow-code-review` 受门禁约束（Hard Stop #9：未过 test-review 不得进 code-review），因此**仍顺序执行，不并行 fan-out**。`/devflow-build` 顺序派发 test-review 再派发 code-review；`/devflow-ship` 只做 completion-gate → finalize，不再重复派发评审。

不变量：

- reviewer 不修改被评审工件、不补写测试、不写代码、不替团队角色拍板。
- 作者 skill 不评审自己。
- reviewer 返回唯一 `next_action_or_recommended_skill`，不拼接多个候选。
- `devflow-tdd-implementation` 是唯一的 implementer subagent 派发者。

派发请求最小字段、reviewer 返回契约、verdict→下一步映射、定向回修协议详见 `references/reviewer-dispatch-protocol.md`。
