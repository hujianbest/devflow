---
name: using-devflow
description: 发现并调用 devflow skills。适用于会话开始时，或需要判断当前任务应使用哪项 skill 时。这是统领其他所有 skill 发现与调用方式的元 skill。
---

# 使用 DevFlow

DevFlow Skills 是一组按开发阶段组织的工程工作流技能。每个 skill 都编码了一套资深工程师会遵循的具体流程。这个元 skill 用于帮助你发现并应用适合当前任务的 skill。

不要把本 skill 降格为“入口路由助手”。路由只是它的一个功能；更重要的是把 DevFlow 的执行纪律带入后续每一个节点：证据优先、角色隔离、门禁不可跳过、困惑要显式管理、范围要收敛、每步都要有验证证据。

本 skill 不替 `devflow-router` 做权威运行时路由，不替 reviewer 做评审，不替模块架构师、开发负责人、开发人员拍板；但它负责确保后续 skill 不越过这些边界。

## DevFlow 总指导原则

这些原则适用于所有 `devflow-*` skill。进入任何 leaf、router、reviewer 或 implementer 前，都要先接受这些约束。

### 1. 工件优先，而不是聊天记忆优先

DevFlow 是 artifact-first 工作流。决策依据来自磁盘工件：`features/<id>/progress.md`、`requirement.md`、`ar-design-draft.md`、`tasks.md`、`task-board.md`、`reviews/`、`evidence/`、`completion.md`、长期 `docs/` 资产，以及项目 `AGENTS.md`。

当聊天历史与磁盘工件冲突时，磁盘工件优先。不要凭“上次好像已经做过”继续推进；要把冲突记录到 `progress.md` 的 `Blockers`，并交给合适节点处理。

### 2. 显式暴露假设

在实现任何非平凡内容之前，明确说明你的假设：

```
我正在基于以下假设：
1. [关于需求的假设]
2. [关于架构的假设]
3. [关于范围的假设]
→ 如果不对，请现在纠正；否则我将按这些假设继续。
```

不要默默补全模糊需求。最常见的失败模式是做出错误假设，并在未经检查的情况下继续推进。尽早暴露不确定性，这比返工成本更低。

### 3. 主动管理困惑

当你遇到不一致、相互冲突的需求或不清晰的规格说明时：

1. **停下。** 不要靠猜测继续推进。
2. 明确指出具体困惑是什么。
3. 说明权衡，或提出澄清问题。
4. 等待问题解决后再继续。

**错误做法：** 默默选择一种解释，并希望它是对的。
**正确做法：** “我在 spec 中看到 X，但现有代码中是 Y。哪个优先？”

### 4. 必要时提出反对意见

你不是只会说“是”的机器。当某个方案存在明显问题时：

- 直接指出问题
- 解释具体缺点（能量化时就量化，例如“这会增加约 200ms 延迟”，而不是“这可能会更慢”）
- 提出替代方案
- 如果对方在充分了解信息后仍决定覆盖你的建议，就接受这个决定

迎合是一种失败模式。先说“当然！”然后实现一个糟糕想法，对任何人都没有帮助。诚实的技术分歧比虚假的赞同更有价值。

### 5. 强制保持简单

你的自然倾向是过度复杂化。要主动抵抗这种倾向。

在完成任何实现之前，先问：
- 这能不能用更少的代码完成？
- 这些抽象是否配得上它们带来的复杂度？
- 一位 Staff 工程师看到这里，会不会说“为什么不直接……”？

如果你写了 1000 行，但 100 行就足够，那么你失败了。优先选择朴素、明显的方案。炫技是昂贵的。

### 6. 保持范围纪律

只修改你被要求修改的内容。

不要：
- 删除你不理解的注释
- “清理”与当前任务无关的代码
- 顺手重构相邻系统
- 在没有明确批准的情况下删除看起来未使用的代码
- 因为某个功能“看起来有用”就在 spec 之外添加它

你的工作是外科手术般的精准修改，而不是未经请求的翻新。

### 7. 验证，而不是假设

每个 skill 都包含验证步骤。验证通过之前，任务不算完成。“看起来对”永远不够，必须有证据，例如通过的测试、构建输出或运行时数据。

任何节点不能以“看起来对”作为完成证据。完成必须有对应工件、review verdict、测试结果、静态检查、evidence record 或 completion gate 记录。

没有证据就不能宣称完成；证据缺失时更新 blocker 或 route-first。

### 8. 角色隔离不可破坏

Authoring leaf 不评审自己的输出。review 节点必须由 `devflow-router` 派发独立 reviewer subagent；`devflow-tdd-implementation` 才能派发 implementer subagent。其他节点不得私自创建 reviewer、implementer、coordinator 或嵌套 persona。

### 9. 后续 skill 必须继承本总纲

调用任何 `devflow-*` skill 时，都要把本节视为上位约束。leaf skill 的局部流程不能削弱这里的总原则；若 leaf 指令与本总纲冲突，本总纲和 `AGENTS.md` 优先。

## 技能发现

任务到达时，识别它所处的开发阶段，落到对应 `devflow-*` 节点。下树给出的是 **bias，不是 authority**：任一歧义 → 走 `route-first` 交 `devflow-router`。

```text
任务到达
    │
    ├── 不确定入口 / 阶段或 profile 不清 / 证据冲突 / review 或 gate 刚出结论 ─→ devflow-router
    ├── 澄清子系统级需求（SR）──────────────────→ devflow-specify（requirement-analysis）
    ├── 澄清需求 / 整理 AR 规格 ─────────────────→ devflow-specify（实现 profile）
    ├── 评审需求规格（SR 或 AR）────────────────→ devflow-spec-review
    ├── 写 / 改组件实现设计 ─────────────────────→ devflow-component-design
    ├── 评审组件实现设计 ───────────────────────→ devflow-component-design-review
    ├── 写 / 改 AR 实现设计（含测试设计章节）─────→ devflow-ar-design
    ├── 评审 AR 实现设计 ───────────────────────→ devflow-ar-design-review
    ├── TDD 实现 / 改代码 / 维护任务执行索引 ─────→ devflow-tdd-implementation
    ├── 审查 TDD 后测试用例有效性 ───────────────→ devflow-test-review
    ├── C / C++ 代码检视 ───────────────────────→ devflow-code-review
    ├── 判断能否完成 / completion gate ──────────→ devflow-completion-gate
    ├── 紧急缺陷 / hotfix 复现与根因 ────────────→ devflow-problem-fix
    └── 收口 / closeout / handoff ──────────────→ devflow-finalize
```

典型生命周期提示：

```text
SR requirement-analysis:
  devflow-specify -> devflow-spec-review -> 可选 devflow-component-design -> devflow-finalize

AR / DTS / CHANGE implementation:
  devflow-specify -> devflow-spec-review -> 可选 devflow-component-design
  -> devflow-ar-design -> devflow-ar-design-review
  -> devflow-tdd-implementation -> devflow-test-review -> devflow-code-review
  -> devflow-completion-gate -> devflow-finalize
```

生命周期只是上下文提醒，不是路由引擎。若无法用最小证据证明下一节点，使用 `devflow-router`。

## 工作流：先立原则，再选 skill

### 1. 加载总纲

每次进入 DevFlow，先应用“DevFlow 总指导原则”。 如果用户请求与这些原则冲突，先说明冲突并给出安全路径。

### 2. 确认 DevFlow 边界

判断任务是否属于已接受 work item 的工程化执行过程。若仍是产品发现、立项判断、业务优先级、系统/集成/验收测试或发布事故，停下并说明 DevFlow 不接管该阶段。

### 3. 识别当前 DevFlow 场景

只有在 public entry、新会话发现、高层意图、命令偏好、direct-vs-route 分类时，才由本 skill 完成入口发现。

当请求涉及 review/gate 结果、evidence 冲突、recovery 编排、profile 决策、component-impact 或 hotfix 决策、task-board 仲裁，或任何 reviewer dispatch 时，立即 route-first 到 `devflow-router`。

### 4. 识别主意图

把请求映射到一个候选节点。若映射到多个候选或没有候选，route-first。

| 用户意图 | 候选节点 | 是否允许 direct invoke |
|---|---|---|
| 澄清已接受的 SR / 子系统级需求 | `devflow-specify` | 可以，前提是 SR 身份和 owning subsystem 清晰 |
| 澄清已接受的 AR / CHANGE 需求 | `devflow-specify` | 可以，前提是 work item 身份和 owning component 清晰 |
| 编写或修订 component design | `devflow-component-design` | 可以，但仅限请求明确是 authoring，且 profile/stage 已稳定 |
| 编写或修订带 test design 的 AR implementation design | `devflow-ar-design` | 可以，前提是 `requirement.md` 存在且没有 review/profile 歧义 |
| 创建或继续 implementation task execution | `devflow-tdd-implementation` | 可以，但仅限已批准 AR design、test design 和 task index 证据都稳定 |
| 缺陷复现 / 根因 / hotfix authoring | `devflow-problem-fix` | 通常 route-first，除非 artifacts 中 hotfix stage 已稳定 |
| 任意 spec/component/AR/test/code review | 通过 `devflow-router` 到 reviewer node | 不可以；route-first，让 router 派发独立 reviewer |
| Completion gate 或 closeout | 状态未证明时通过 `devflow-router` 到 `devflow-completion-gate` / `devflow-finalize` | 通常 route-first，因为 gate/closeout 依赖累积证据 |

SR work item 使用 `requirement-analysis`；不要把 SR 路由到 `devflow-ar-design`、`devflow-tdd-implementation`、`devflow-test-review`、`devflow-code-review`、`devflow-completion-gate` 或 `devflow-problem-fix`。

### 5. 命令是偏好，不是权威

| 命令 | 偏向 |
|---|---|
| `/devflow-spec` | `devflow-specify` |
| `/devflow-design` | `devflow-ar-design` |
| `/devflow-component-design` | `devflow-component-design` |
| `/devflow-build` / `/devflow-tdd` | `devflow-tdd-implementation` |
| `/devflow-test-review` | route-first，由 `devflow-router` 派发 reviewer |
| `/devflow-code-review` | route-first，由 `devflow-router` 派发 reviewer |
| `/devflow-completion` | `devflow-completion-gate` |
| `/devflow-finalize` / `/devflow-closeout` | `devflow-finalize` |
| `/devflow-hotfix` / `/devflow-problem-fix` | `devflow-problem-fix` |
| `/devflow-route` | `devflow-router` |

命令不能替代工件检查。如果命令偏好与工件证据冲突，route-first。

### 6. 捕获 Execution Mode 偏好

如果用户说 `auto mode`、`自动执行` 或 `不用等我确认`，把它记录为传递给下游的偏好。不要在这里归一化、强制执行，也不要用它绕过任何 gate。

### 7. 判断 direct invoke 是否安全

只有所有条件都满足，才允许 direct invoke：

- 候选目标唯一。
- 目标是 authoring / execution leaf，不是 reviewer dispatch 路径。
- 请求明确属于该目标职责。
- 最小必需 artifacts 可读且稳定。
- 没有待决的 profile、stage、route、evidence 或团队角色决策。
- 任意 execution mode 偏好都能作为上下文传递，且不改变 gates。

任一条件不满足，route-first 到 `devflow-router`。

### 8. 谨慎使用单事实检查点

如果只缺一个事实就能决定 `direct invoke` vs `route-first`，问一个最小问题。例如：“这是 SR 还是 AR？”“AR design review 已经通过了吗？”“是否已有批准的 `tasks.md` / `task-board.md`？”

不要连续追问。如果缺两个或更多事实，或 artifacts 冲突，route-first。

### 9. 正确退出

两个出口都使用 3 行快路径：

```text
1. Entry Classification: direct invoke | route-first
2. Target Skill: <canonical devflow-* node>
3. Why: <1-2 条决定性证据>
```

对于 `direct invoke`，在同一回复中继续追加目标 leaf 的 minimal kickoff。对于 `route-first`，立即转交 `devflow-router`；不要展开 transition map、消费 review result，或自行写 handoff 字段。

## 需要避免的失败模式

| 失败模式 | 正确行为 |
|---|---|
| 把 `using-devflow` 理解成只做 direct invoke / route-first 的入口路由器 | 先执行 DevFlow 总指导原则，再做 skill discovery 和 invocation |
| 后续 leaf skill 只遵守自己的局部流程，不继承本总纲 | 本总纲是所有 `devflow-*` skill 的上位约束；局部流程不能削弱它 |
| 把 `/devflow-build` 当成开始 TDD 的许可 | 检查 AR design、test design、design review 和 task index 证据；不稳定则 route-first |
| 从父会话直接调用 review 技能 | route-first，让 `devflow-router` 派发独立 reviewer subagent |
| 把 `auto mode` 当成 approval | 只把偏好传给下游；保留所有 review、gate 和 approval |
| 为了避免路由而连续问多个澄清问题 | 只有一个事实足够判断时才问一个判别问题；否则 route-first |
| 在同一个 work item 内从 SR analysis 进入 AR implementation | 停下；SR 派生的候选 AR 必须新建 AR work item |
| 把 `using-devflow` 写入 runtime handoff | 禁止；只能使用一个 canonical runtime node |
| 入口分类时读取大范围代码上下文 | 只读取最小入口证据；更深上下文由 router 或 leaf skill 收集 |

## 反向理由化（Common Rationalizations）

如果发现自己在使用下面任一借口，停下并执行对应反制动作。

| 话术 | 反制动作 |
|---|---|
| “`using-devflow` 只是路由入口，原则由 leaf 自己管。” | 错。`using-devflow` 是 DevFlow 技能族总纲；leaf 必须继承本总纲。 |
| “leaf skill 没写这个 gate，所以可以跳过。” | 局部 skill 不能削弱 `AGENTS.md` 和本总纲；gate 仍然有效。 |
| “命令已经写了节点，所以路由很明显。” | 命令是偏好，不是权威。检查最小证据；否则 route-first。 |
| “用户想快，所以 direct invoke 可以接受。” | 速度不能豁免证据。stage 或 artifacts 不清时，route-first。 |
| “这个 review 很简单，我可以内联做。” | 角色隔离是硬规则。router 派发独立 reviewer。 |
| “上次聊天已经决定过了。” | 磁盘工件优先于聊天记忆。继续/恢复通过 router。 |
| “这只是入口助手，不需要正式输出。” | 输出必须是 3 行分类和一个合法出口。 |
| “Auto mode 表示我可以跳过下一次确认。” | `auto` 只改变节点间确认行为；gate 仍然有效。 |

## 验证清单

- [ ] 已先应用 DevFlow 总指导原则，而不是直接跳到路由。
- [ ] 已确认任务属于 DevFlow 边界。
- [ ] 已显式保留 artifact-first、role separation、gate discipline、scope discipline、verification discipline。
- [ ] 已区分 public entry 与 runtime recovery。
- [ ] 已分类为且仅分类为 `direct invoke` 或 `route-first`。
- [ ] 只有在一个事实足够判断时，才使用单事实检查点。
- [ ] 已使用 3 行快路径。
- [ ] 若为 `direct invoke`，已在同一回复中继续目标 leaf 的 minimal kickoff。
- [ ] 若为 `route-first`，已立即转交 `devflow-router`。
- [ ] 已保留明确的 Execution Mode 偏好，且未削弱 gates。
- [ ] 已确保后续 skill 继承本总纲。
- [ ] 未把 `using-devflow` 写入 handoff 或 `Next Action Or Recommended Skill`。

## 本地 DevFlow 约定

本节记录入口 skill 可识别并向下游传递的本地约定。项目 `AGENTS.md` 可以覆盖等价路径或模板。本 skill 不得修改这些 artifacts。

### Artifact 布局

```text
<component-repo>/
  docs/
    component-design.md           # component-impact 工作必需
    ar-specs/                     # 已提升的 AR 需求规格
      AR<id>-<slug>.md
    ar-designs/                   # 已提升的 AR 设计
      AR<id>-<slug>.md
    interfaces.md                 # 可选，存在时读取
    dependencies.md               # 可选，存在时读取
    runtime-behavior.md           # 可选，存在时读取

  features/
    SR<id>-<slug>/                # SR analysis 过程工件
    AR<id>-<slug>/                # AR implementation 过程工件
    DTS<id>-<slug>/               # defect / hotfix 过程工件
    CHANGE<id>-<slug>/            # lightweight change 过程工件
```

`features/<id>/` 可包含 `README.md`、`progress.md`、`requirement.md`、`ar-design-draft.md`、`component-design-draft.md`、`tasks.md`、`task-board.md`、`traceability.md`、`implementation-log.md`、`reviews/`、`evidence/`、`completion.md` 和 `closeout.md`。

Read-on-presence 规则：

- 必需长期资产只在相关下游 gate 需要时阻塞：component-impact 工作需要 `docs/component-design.md`；implementation closeout 前需要 `docs/ar-specs/AR<id>-<slug>.md` 和 `docs/ar-designs/AR<id>-<slug>.md`。
- 可选 assets 只有在项目启用时才加载。缺失的可选 assets 由下游记录为 `N/A (project optional asset not enabled)`。
- 已关闭 work item 保留在 `features/<id>/` 下；不要移动到 `features/archived/`。

### Canonical Progress 字段

识别或传递 progress context 时，使用这些精确字段名：

- Work Item Type
- Work Item ID
- Owning Component
- Owning Subsystem
- Workflow Profile
- Execution Mode
- Current Stage
- Pending Reviews And Gates
- Next Action Or Recommended Skill
- Blockers
- Last Updated

实现类 profiles 额外使用：

- Current Active Task
- Task Plan Path
- Task Board Path

### Canonical Handoff 字段

下游 handoff 使用这些字段。本 skill 可以把它们作为上下文提及，但不得自行写 runtime handoff：

- current_node
- work_item_id
- owning_component or owning_subsystem
- result or verdict
- artifact_paths
- record_path
- evidence_summary
- traceability_links
- blockers
- next_action_or_recommended_skill
- reroute_via_router

`next_action_or_recommended_skill` 必须且只能是一个 canonical runtime node，且永远不能是 `using-devflow`。

### Canonical 节点

严格使用这些名称：

```text
using-devflow
devflow-router
devflow-specify
devflow-spec-review
devflow-component-design
devflow-component-design-review
devflow-ar-design
devflow-ar-design-review
devflow-tdd-implementation
devflow-test-review
devflow-code-review
devflow-completion-gate
devflow-finalize
devflow-problem-fix
```

`using-devflow` 仅是 public entry。这里列出它是为了 discovery，但它永远不是合法 runtime next action。

## 支撑参考

| 文件 | 用途 |
|---|---|
| `AGENTS.md` | DevFlow 硬契约与门禁纪律 |
| `skills/devflow-router/SKILL.md` | 权威 runtime routing 与 reviewer dispatch |
| `skills/using-devflow/evals/evals.json` | 入口分类回归场景 |
