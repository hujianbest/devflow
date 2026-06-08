---
description: On-demand independent review entry — dispatch the matching review node(s) (spec / component-design / ar-design / test / code) via devflow-router and consume their verdicts, without authoring or self-review
---

This command orchestrates the **DevFlow review (评审)** phase as an **on-demand check entry**：当用户想对当前工件做一次独立检查（检查设计 / 代码 / 测试 / 规格），而又不想从对应 authoring 阶段命令整段重走时，用本命令选出该评审哪些工件、由 `devflow-router` 派发独立 `devflow-reviewer` 子代理、消费 verdict 并形成 handoff。

本命令是评审的 **再入口（re-entry）**，不是评审的捷径：它 **不绕过** 角色隔离与 router 派发，**不取代** `/devflow-specify`、`/devflow-design`、`/devflow-build` 内已编排的评审，也 **不豁免** 任何门禁。它只是让"现在检查一下 X"这个意图能唯一映射到 canonical 评审节点。

## Phase scope

- Skills involved (in推进顺序):
  1. `devflow-router` — 依据磁盘工件 + 用户意图，选出本次需要的评审节点；逐个派发独立子代理；消费每个 verdict 决定下一步
  2. 被选中的一个或多个评审 skill（判据唯一权威，由子代理完整执行其 SKILL.md）
- Reviewers dispatched (via `devflow-router`, system prompt = `agents/devflow-reviewer.md`)，按用户意图 / 工件状态择一或多：
  - 检查规格 → `devflow-spec-review`（`target_skill = devflow-spec-review`，`primary_artifact = features/<id>/requirement.md`）
  - 检查设计 → `devflow-component-design-review`（仅当组件设计存在）和/或 `devflow-ar-design-review`（`primary_artifact = features/<id>/component-design-draft.md` / `ar-design-draft.md`）
  - 检查测试 → `devflow-test-review`（`target_skill = devflow-test-review`）
  - 检查代码 → `devflow-code-review`（`target_skill = devflow-code-review`）
- 不派发实现 / 不做 authoring：本命令只读评审，回修一律路由回对应 authoring 节点。
- Craft 透镜（评审子代理内部叠加，不是流程节点、不进 handoff、不产 verdict）：
  - `devflow-test-review` 以 `devflow-test-craft` 为"好测试"判别标尺
  - `devflow-code-review` 以 `devflow-coding-craft` 为"好代码"判别标尺
  - `devflow-component-design-review` / `devflow-ar-design-review` 以 `devflow-design-craft` 为"好设计"判别标尺

## When to use

- 用户明确说"检查 / review / 看一下"设计、代码、测试或规格，且对应工件已存在于 `features/<id>/`
- 上游某工件回修后想立即重审（例如改完 `ar-design-draft.md` 想再过一次 ar-design-review）
- 工件已就绪但 `Pending Reviews And Gates` 里还挂着未消费的评审，想集中触发并消费
- 想在进入下一阶段前，对已有设计 / 测试 / 代码做一次额外独立把关

不适用：

- 工件尚未写出 / 需要先 authoring → 改用 `/devflow-specify`、`/devflow-design` 或 `/devflow-build`
- 评审返回 `REQUEST_CHANGES` 需要回修 → 回到对应 authoring 命令（spec→`/devflow-specify`、design→`/devflow-design`、test/code→`/devflow-build`），不要在本命令内改工件
- 完成判断 / 收口 → `/devflow-ship`
- 紧急修复的复现 + 根因 → `/devflow-fix`

## Hard contract（节选自 AGENTS.md，不可绕开）

- **作者不自审**：本命令 **不允许** 在父会话内联评审或由作者节点自评；所有评审一律由 `devflow-router` 派发独立 `devflow-reviewer` 子代理（system prompt = `agents/devflow-reviewer.md`）
- **本命令不改任何工件**：不写 / 不修 `requirement.md`、`component-design-draft.md`、`ar-design-draft.md`、源代码、测试；回修交对应 authoring 命令
- **顺序门禁链不可跳序**：同时检查测试与代码时，**必须** 先 `devflow-test-review` 再 `devflow-code-review`；test-review 未通过 **严禁** 进入 code-review
- **评审目标必须存在**：被选评审的 `primary_artifact` 在磁盘上缺失或证据不稳定 → 不得强行评审，回 `/devflow` 走 router 或回对应 authoring 命令补齐
- `requirement-analysis` 子街区只可走 `devflow-spec-review` / `devflow-component-design-review`，**不得** 路由到 `devflow-ar-design-review` / `devflow-test-review` / `devflow-code-review`
- `next_action_or_recommended_skill` 仅限 13 个 canonical 节点之一；选不出唯一下一步 → `reroute_via_router = true` 交 router
- `auto` execution mode 不豁免任何评审或门禁；只移除节点间人工确认

## Workflow（不复制 SKILL.md，只编排）

1. 读 `features/<id>/progress.md`、`reviews/`、`evidence/` 与相关 draft 工件：
   - 工件证据不稳定 / 当前节点无法唯一判断 → 回 `/devflow` 走 router
2. 确定本次评审范围（review scope）：
   - 用户明确指定（设计 / 代码 / 测试 / 规格）→ 映射到对应评审节点
   - 用户只说"检查一下"未指定 → 由 `devflow-router` 依据工件状态选出"已就绪但未评审 / 有变更需重审"的评审节点；多个工件就绪时按 canonical 顺序排队：`spec → component-design → ar-design → test → code`
3. 对每个被选评审节点，handoff 给 `devflow-router`：
   - 构造 Review Request Pack（`target_skill`、`primary_artifact`、`supporting_context`、`agents_md_anchor`、`expected_return_contract`）
   - 派发独立子代理（system prompt = `agents/devflow-reviewer.md`）
4. 消费每个 verdict：
   - `APPROVE` / `APPROVE_WITH_FOLLOWUPS` → 若队列里还有评审则继续下一个（测试通过后才允许进入 code-review）；否则进入步骤 5
   - `REQUEST_CHANGES` → 停止本次评审队列，`next_action_or_recommended_skill` 指向对应 authoring 节点（`devflow-specify` / `devflow-component-design` / `devflow-ar-design` / `devflow-tdd-implementation`），交对应 authoring 命令回修
   - `REJECT` → 停下，交团队角色（需求负责人 / 模块架构师 / 开发负责人）裁决；写 `Blockers`
   - `reroute_via_router = true`（如 profile 需升级、AR 范围越界）→ 交 `devflow-router` 重新评估
5. 形成 canonical handoff 块：
   - 全部被选评审通过 → 按工件语境给出推荐的下一阶段节点（如设计评审通过 → `devflow-tdd-implementation`；代码评审通过 → `devflow-completion-gate`）
   - 仍有未通过 / 未消费评审 → 写入 `Pending Reviews And Gates`，下一步指向回修或剩余评审

## Anti-rationalization quick refs

| 误判 | 反向行动 |
|---|---|
| "用 /devflow-review 我自己读一遍工件给个结论就行" | 禁止；评审必须由 router 派发独立 `devflow-reviewer` 子代理，父会话 / 作者不自审 |
| "顺手在 review 命令里把发现的笔误改了" | 禁止；本命令不改任何工件，发现写进 findings，回修交对应 authoring 命令 |
| "用户只说检查代码，测试就不审了" | 若用户只要 code-review，可只审代码；但 test-review 未通过时严禁进入 code-review，顺序门禁链不可跳序 |
| "草稿还没写完，先 review 起来占个位" | 禁止；`primary_artifact` 缺失或不稳定不得评审，先回 authoring 命令补齐 |
| "评审返回 REQUEST_CHANGES，我在本命令里直接改一版" | 禁止；回修回到对应 authoring 命令，本命令只做评审与消费 verdict |
| "下一步选不出来，写段自由文本说明" | 禁止；选不出唯一 canonical 节点 → `reroute_via_router = true` 交 router |
