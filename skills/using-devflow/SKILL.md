---
name: using-devflow
description: DevFlow skill family 的元技能与 public entry，统辖所有 devflow-* 技能的发现与调用。当新会话开始、需要发现当前任务该用哪个 devflow 节点、或判断能直接进入某个 leaf 还是先交给 devflow-router 时使用。不用于运行时路由恢复、workflow profile / execution mode 决策、已在叶子技能内部的写作 / 评审 / 实现，或产品发现。
---

# Using DevFlow

## 概述

DevFlow（devflow）是一个按开发阶段组织的 workflow skill family：每个 `devflow-*` 节点把一段团队工程纪律固化成可执行过程，从规格澄清、设计、TDD 实现、独立评审、完成门禁到收口。本 skill 是统辖全部 `devflow-*` 技能 **如何被发现与调用** 的元技能与 public entry。

本 skill 的产出永远是两类之一：

- `direct invoke`：当前节点唯一明确、且必要工件证据稳定 → 直接进入对应 `devflow-*` leaf skill
- `route-first`：阶段 / profile / 证据任一不稳定 → 交给 `devflow-router` 做权威路由

本 skill 不做 authoritative routing，不替 `devflow-router` 决定 workflow profile / execution mode / canonical 节点，也不替团队角色（需求负责人、模块架构师、开发负责人、开发人员）拍板。它不读取大量代码、不修改任何工件。

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

两个子街区的合法节点集不同，**禁止跨子街区切换**：

- 需求分析子街区（`SR` → `requirement-analysis` profile）：仅经过 `devflow-specify` → `devflow-spec-review` →（可选 `devflow-component-design` → `devflow-component-design-review`）→ `devflow-finalize`。**不得**落到 `devflow-ar-design` / `devflow-ar-design-review` / `devflow-tdd-implementation` / `devflow-test-review` / `devflow-code-review` / `devflow-completion-gate` / `devflow-problem-fix`。
- 实现子街区（`AR` / `DTS` / `CHANGE` → `standard` / `component-impact` / `hotfix` / `lightweight` profile）：完整实现主链 + 支线。

SR 拆出的候选 AR 必须由需求负责人**新建** AR work item，由 `devflow-router` 重新分流，而不是在本 SR 内跨街区推进。

## 核心操作行为

下列行为在所有 `devflow-*` 节点、所有时刻都适用，不可协商。

### 1. 暴露假设（Surface Assumptions）

进入任何非平凡节点前，显式写出你的假设——尤其是 work item 类型、所属组件 / 子系统、profile 倾向、当前阶段：

```text
我正在做的假设：
1. <关于 work item 类型 / 归属的假设>
2. <关于当前阶段 / 已有工件的假设>
3. <关于 profile / execution mode 的假设>
→ 现在纠正我，否则我将据此继续。
```

不要悄悄替模糊输入填空。最常见的失败是带着错误假设一路狂奔。早暴露不确定性，比返工便宜。

### 2. 主动管理困惑（Manage Confusion Actively）

当遇到不一致、冲突的要求或工件与会话记忆相左时：

1. **停下。** 不要带着猜测继续。
2. 命名具体的困惑点。
3. 摆出取舍或提出判别问题。
4. 等待澄清后再继续。

**坏：** 悄悄选一个解释并寄望它对。
**好：** 「progress.md 显示已过 ar-design-review，但 reviews/ 里没有该 verdict 记录，以哪个为准？」（证据冲突时按下面「证据优先」处理。）

### 3. 必要时反对（Push Back When Warranted）

你不是应声虫。当某条路径有明确问题时——例如用户要求在缺 AR 设计时直接进 `devflow-tdd-implementation`，或把 `auto` 当作跳过 review 的许可：

- 直接指出问题
- 说明具体代价（尽量量化）
- 提出替代（通常是 `route-first` 或回上游节点）
- 在对方掌握完整信息后仍坚持时，接受其决定

谄媚是一种失败模式。「没问题！」之后执行一个坏主意帮不了任何人。

### 4. 坚持简洁（Enforce Simplicity）

本入口天生倾向把自己写成完整 routing 状态机——主动抵制。入口只做最小必要的工件检查与意图分流，不内嵌 `devflow-router` 的 FSM，不展开 transition map，不做 review recovery。能用 3 行编号快路径说清的，就不要写成长篇。

### 5. 维持范围纪律（Maintain Scope Discipline）

只碰被要求碰的东西。本 skill **不**：

- 修改任何工件（`progress.md`、`reviews/`、`evidence/`、代码、设计）
- 替 `devflow-router` 决定 profile / execution mode / canonical 节点
- 替团队角色拍板业务、范围、优先级、架构、接口契约
- 做大范围代码探查

入口的职责是精准分流，不是顺手装修。

### 6. 验证而非假设（Verify, Don't Assume）

`direct invoke` 的前提是**可读的工件证据**，不是「看起来对」。进入某 leaf 前确认其必要工件存在（如进 `devflow-ar-design` 至少需要 `requirement.md`）。无法验证 → `route-first`。

### 7. 证据优先（Evidence-First）

决策基于磁盘工件（`features/<id>/progress.md`、`reviews/`、`evidence/`、`completion.md`、长期 `docs/`），不基于会话记忆。当会话历史与磁盘工件冲突时，**磁盘工件胜出**，并把冲突交给 `devflow-router` 记录处理。

### 8. 角色分离 / 不自审（Role Separation）

本 skill 不内联做任何 review。所有 reviewer（`devflow-spec-review` / `devflow-component-design-review` / `devflow-ar-design-review` / `devflow-test-review` / `devflow-code-review`）必须由 `devflow-router` 派发为独立 subagent。入口遇到「评审」意图时只做分流，不亲自评分。

### 9. 团队角色边界（Team-Role Boundary）

devflow 不做业务、范围、优先级、架构或接口契约决定。需要这类判断时，停下并把问题交给对应团队角色（需求负责人、模块架构师、开发负责人），不要悄悄替他们选。

## 应避免的失败模式

这些是看似高效、实则埋雷的细微错误：

1. 不核对就做错误假设并一路推进
2. 不管理自身困惑——迷路了还硬往前
3. 注意到不一致却不暴露
4. 在非显然决策上不摆取舍
5. 对有明显问题的路径谄媚附和（「没问题！」）
6. 把入口写成完整 routing 状态机（过度复杂）
7. 因为用户报了 `/devflow-*` 命令名就跳过工件检查
8. review / gate 完成后仍在入口里做恢复编排（应交 `devflow-router`）
9. 路由不清却硬做 `direct invoke`
10. 把 `using-devflow` 写进 `Next Action Or Recommended Skill` 或任何 handoff 字段
11. 把 `auto` execution mode 当作跳过 review / gate / approval / 证据要求的许可
12. 把 SR 工作项落到 `devflow-ar-design` / `devflow-tdd-implementation` 等实现节点（跨子街区）

## 技能规则

1. **开工前先确认入口分类。** 任何非平凡请求的第一个 skill 永远是 `using-devflow`，从这里决定 `direct invoke` 还是 `route-first`，不要直接跳进 leaf。

2. **技能是 workflow，不是建议。** 进入某个 `devflow-*` 节点后，逐字按其 hard gates、workflow、output contract、verification 执行，不省略评审 / 门禁。

3. **可以有多个技能依次适用。** 一个完整 AR 通常是 `devflow-specify` →（评审 / 设计 / 实现 / 评审 / 门禁）→ `devflow-finalize` 的序列；但每一次跃迁由 `devflow-router` 基于工件决定，不由入口预演。

4. **拿不准时先路由。** 节点与必要工件未同时清晰、或涉及 profile 升级 / 跨组件协调 / 证据冲突时，一律 `route-first` 交 `devflow-router`。

## 入口判定：direct invoke vs route-first

这是本 skill 的核心对象转换：把模糊意图分类为两条路径之一。

**允许 `direct invoke` 必须同时满足：**

- 候选节点唯一
- 请求明确属于该节点职责
- 必要工件可读（read-on-presence）
- 没有 profile / route / 证据冲突
- Execution Mode 偏好已记录可传递

任一不满足 → `route-first` 交 `devflow-router`。

**单事实分流检查点：** 如果只差 **1 个关键事实**就能稳定判断，先问 1 个最小判别问题再继续（典型：只差「这是 AR 还是 DTS」、只差「AR 实现设计是否已通过 review」）。需要 ≥2 个事实、工件互相冲突、涉及 profile 升级（component-impact / hotfix / lightweight）、涉及跨组件协调 → 直接 `route-first`。

**Execution Mode 偏好：** 用户说 `auto mode` / `自动执行` / `不用等我确认` → 视为 Execution Mode 偏好，原样向下游传递；本 skill 不归一化为 canonical 字段。`auto` 不是跳过 review / gate / approval 的理由，也不是 `direct invoke` 的充分条件。

**命令当作 bias，不当作 authority：**

| 命令 | 默认偏向 |
|---|---|
| `/devflow-spec` | `devflow-specify` |
| `/devflow-design` | `devflow-ar-design` |
| `/devflow-component-design` | `devflow-component-design` |
| `/devflow-build` / `/devflow-tdd` | `devflow-tdd-implementation` |
| `/devflow-test-review` | `devflow-test-review` |
| `/devflow-code-review` | `devflow-code-review` |
| `/devflow-completion` | `devflow-completion-gate` |
| `/devflow-finalize` / `/devflow-closeout` | `devflow-finalize` |
| `/devflow-hotfix` / `/devflow-problem-fix` | `devflow-problem-fix` |
| `/devflow-route` | `devflow-router` |

命令偏好与工件证据冲突时一律 `route-first`。

**正确结束（3 行编号快路径）：** 唯一确定下一步时输出

```text
1. Entry Classification: direct invoke | route-first
2. Target Skill: <canonical devflow-* 节点名>
3. Why: <1-2 条决定性证据>
```

`direct invoke` 时，3 行之后**同一回复**继续追加目标 leaf skill 的最小 kickoff（第 1 步动作 / 最小 intake），不再等一轮确认。`route-first` 时只说明「为什么不能 direct invoke」，立即转交 `devflow-router`，不展开 transition map、不做 review recovery、不把 `using-devflow` 写进 handoff。

## 生命周期序列

不是每个 work item 都经过全部节点；`devflow-router` 按工件证据决定每一步跃迁。典型序列：

**需求分析子街区（SR）：**

```text
1. devflow-specify                 → 澄清子系统级需求 / IR-SR 追溯
2. devflow-spec-review             → 独立审查规格清晰性、可追溯性
3. devflow-component-design        → （可选）本 SR 触发的组件实现设计修订
4. devflow-component-design-review → （可选）评审组件设计修订
5. devflow-finalize                → analysis closeout
```

**实现子街区（AR / DTS / CHANGE）：**

```text
1.  devflow-specify                 → 澄清需求 / 整理 AR 规格
2.  devflow-spec-review             → 独立审查规格
3.  devflow-component-design        → （component-impact 时）组件实现设计
4.  devflow-component-design-review → （component-impact 时）评审组件设计
5.  devflow-ar-design               → AR 实现设计（含测试设计章节）
6.  devflow-ar-design-review        → 独立审查 AR 设计 + 测试设计
7.  devflow-tdd-implementation      → 基于测试设计做 C/C++ TDD
8.  devflow-test-review             → TDD 后测试用例有效性审查
9.  devflow-code-review             → C/C++ 代码检视
10. devflow-completion-gate         → evidence bundle 与完成判断
11. devflow-finalize                → implementation closeout
```

hotfix 从 `devflow-problem-fix`（复现 → 根因 → 最小安全修复边界）起步，再回流到 `devflow-ar-design` 或 `devflow-tdd-implementation` 续走主链。bug 修复可能只需 `devflow-problem-fix` → `devflow-tdd-implementation` → `devflow-test-review` → `devflow-code-review` → `devflow-completion-gate`。

## 快速参考

| 阶段 | 节点 | 一句话 |
|---|---|---|
| 路由 | `devflow-router` | runtime 权威：决定 profile / execution mode / canonical 节点、派发 reviewer、消费 review / gate 结论 |
| 规格 | `devflow-specify` | 澄清明确输入、IR/SR/AR 追溯、待决问题；不做产品发现 |
| 规格 | `devflow-spec-review` | 独立审查规格清晰性、可追溯性、可设计性 |
| 设计 | `devflow-component-design` | 组件级实现设计、SOA 边界、接口与依赖 |
| 设计 | `devflow-component-design-review` | 独立审查组件实现设计 |
| 设计 | `devflow-ar-design` | 单 AR 代码层设计 + 内嵌测试设计章节 |
| 设计 | `devflow-ar-design-review` | 独立审查 AR 设计与测试设计 |
| 实现 | `devflow-tdd-implementation` | 基于测试设计做嵌入式 TDD；维护任务执行索引 |
| 验证 | `devflow-test-review` | TDD 后测试用例有效性、覆盖性、可维护性审查（不补写测试 / 不改生产代码） |
| 评审 | `devflow-code-review` | C/C++ 质量、SOA 边界、嵌入式风险检视 |
| 门禁 | `devflow-completion-gate` | evidence bundle 与完成判断 |
| 收口 | `devflow-finalize` | 状态收口、交接、长期 `docs/` 资产同步 |
| 支线 | `devflow-problem-fix` | hotfix 复现、根因、最小安全修复边界、回流节点 |

## 输出契约

- 输出永远是两类之一：
  1. 进入合法 `devflow-*` leaf skill 并在同一回复执行其第 1 步
  2. 把控制权交给 `devflow-router`
- 不修改任何工件
- 不把 `using-devflow` 写进 handoff 或 `Next Action Or Recommended Skill`

## 风险信号

- 把 `using-devflow` 写成完整 routing 状态机
- 路由不清却硬做 `direct invoke`
- 因为用户报命令名就跳过工件检查
- review / gate 完成后仍在做恢复编排（应交 `devflow-router`）
- 把本 skill 写进 `Next Action Or Recommended Skill`
- 替模块架构师、开发负责人、开发人员拍板
- 把 SR 落到任何实现节点

## 反向理由化（Common Rationalizations）

入口阶段最常见的偷懒话术与反驳。命中任意一条 → 停下，按反驳动作执行。

| 话术 | 反驳 |
|---|---|
| 「用户给了 `/devflow-build`，意图明显，直接进 `devflow-tdd-implementation`」 | 命令是 bias，不是 authority。缺 AR 设计 / 缺 design review / 阶段不清 → `route-first`，让 `devflow-router` 决定 |
| 「节点很明确，跳过工件检查」 | `direct invoke` 必须节点 + 必要工件**同时**清晰；任一不满足 → `route-first` |
| 「上一次会话已经走过 router，这次直接进入即可」 | 任何继续 / 恢复都属于 runtime 编排，必须 `devflow-router`。本 skill 只做入口分流 |
| 「这只是闲聊问下一步，不必分类」 | 输出永远只有两类：`direct invoke` 或 `route-first`，没有第三种合法出口 |
| 「用户说 `auto mode`，可以省掉 review 派发」 | `auto` 是 Execution Mode 偏好，不是跳过 review / gate / approval 的理由，也不是 `direct invoke` 的充分条件 |
| 「为了响应快，把 `using-devflow` 写进 handoff」 | 禁止。`using-devflow` 是 public entry，不允许出现在 `Next Action Or Recommended Skill` |
| 「这是个非常小的 SR，让它直接进 `devflow-ar-design`」 | 跨子街区切换被禁止。SR 经 `devflow-finalize` analysis closeout；候选 AR 由需求负责人**新建** AR work item |

## 验证清单

- [ ] 已识别 entry vs runtime recovery（recovery → `devflow-router`）
- [ ] 已分类 `direct invoke` vs `route-first`
- [ ] 单事实分流检查点（如适用）已使用
- [ ] clear case 使用 3 行编号快路径
- [ ] `direct invoke` 时已在同一回复进入 target leaf skill 的最小 kickoff
- [ ] `route-first` 时已立即转交 `devflow-router`
- [ ] Execution Mode 偏好已记录可传递
- [ ] 未把本 skill 写入 handoff
- [ ] 未替团队角色拍板

## 本地 DevFlow 约定

本节由当前 skill 自己维护。不要加载共享约定文件；项目 `AGENTS.md` 可以覆盖等价路径或模板。

### 产物布局

默认产物布局来自 `docs/principles/03 artifact-layout.md`。项目 `AGENTS.md` 可以覆盖等价路径；没有覆盖时，本 skill 必须使用以下组件仓库布局：

```text
<component-repo>/
  docs/
    component-design.md           # 长期组件实现设计
    ar-specs/                     # 长期 AR 需求规格
      AR<id>-<slug>.md
    ar-designs/                   # 长期 AR 实现设计
      AR<id>-<slug>.md
    interfaces.md                 # 可选；仅团队启用时读取 / 同步
    dependencies.md               # 可选；仅团队启用时读取 / 同步
    runtime-behavior.md           # 可选；仅团队启用时读取 / 同步

  features/
    SR<id>-<slug>/                # 单个 SR 的需求分析过程产物
    AR<id>-<slug>/                # 单个 AR 的过程产物
    DTS<id>-<slug>/               # 单个缺陷 / 问题修复的过程产物
    CHANGE<id>-<slug>/            # 单个轻量变更的过程产物
```

`docs/` 存放随代码提交的长期组件资产。`features/<id>/` 存放单个 work item 的过程产物：按需包含 `README.md`、`progress.md`、`requirement.md`、`ar-design-draft.md`、`tasks.md`、`task-board.md`、`traceability.md`、`implementation-log.md`、`reviews/`、`evidence/`、`completion.md`、`closeout.md`。

Read-on-presence 规则：

- 必需长期资产缺失时阻塞：component-impact 工作需要 `docs/component-design.md`；implementation closeout 前需要 `docs/ar-specs/AR<id>-<slug>.md`（由 `requirement.md` 提升）与 `docs/ar-designs/AR<id>-<slug>.md`（由 `ar-design-draft.md` 提升）。
- 可选资产（`docs/interfaces.md`、`docs/dependencies.md`、`docs/runtime-behavior.md`）仅在项目启用时读取 / 同步。缺失的可选资产记录为 `N/A (project optional asset not enabled)`，不视为阻塞。
- 过程目录保留在 `features/` 下；不要把已关闭 work item 移到 `features/archived/`，否则会破坏追溯链接。

### Progress 字段

本 skill 读写 `features/<id>/progress.md` 时使用 canonical progress 字段：

- Work Item Type: SR / AR / DTS / CHANGE
- Work Item ID: SR1234、AR12345、DTS67890 或 CHANGE id
- Owning Component: AR / DTS / CHANGE 必填
- Owning Subsystem: SR 必填
- Workflow Profile: requirement-analysis / standard / component-impact / hotfix / lightweight
- Execution Mode: interactive / auto
- Current Stage: 当前 canonical devflow node
- Pending Reviews And Gates: 待处理 review / gate 列表
- Next Action Or Recommended Skill: 仅允许一个 canonical node
- Blockers: open blockers
- Last Updated: timestamp

### Handoff 字段

返回结构化 handoff，并使用本 skill 已知的字段：

- current_node
- work_item_id
- owning_component or owning_subsystem
- result or verdict
- artifact_paths
- record_path, when a review / gate / verification record exists
- evidence_summary
- traceability_links
- blockers
- next_action_or_recommended_skill
- reroute_via_router

不要把 `next_action_or_recommended_skill` 设为 `using-devflow` 或自由文本。

### 入口路由

- `using-devflow` 只是 public entry skill；永远不要写入 runtime handoff。
- 只有 target leaf skill 与 required artifacts 都明确时，才允许 direct invoke。
- stage、profile、route 或 evidence 不清楚时，route-first 进入 `devflow-router`。

### Canonical 节点

using-devflow, devflow-router, devflow-specify, devflow-spec-review, devflow-component-design, devflow-component-design-review, devflow-ar-design, devflow-ar-design-review, devflow-tdd-implementation, devflow-test-review, devflow-code-review, devflow-completion-gate, devflow-finalize, devflow-problem-fix.

## 支撑参考

| 文件 | 用途 |
|---|---|
| `devflow-router/SKILL.md` | authoritative runtime routing |
