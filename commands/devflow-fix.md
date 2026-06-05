---
description: Hotfix entry — escalate to hotfix profile, run problem-fix (reproduce + root cause + minimal safe fix), then rejoin build and ship
---

This command orchestrates the **DevFlow hotfix (紧急修复)** sub-graph entry.

## Phase scope

- Skills involved (in推进顺序):
  1. `devflow-problem-fix` — `hotfix` profile **首判并写入 `progress.md`**；复现、根因分析、最小安全修复边界（确属疑难的 profile 判断交可选的 `devflow-router` 仲裁）
  2. 回归到 `/devflow-build`：`devflow-tdd-implementation` →（`/devflow-build` 编排者**顺序**派发）`devflow-test-review` → `devflow-code-review`
  3. 回归到 `/devflow-ship`：`devflow-completion-gate` → `devflow-finalize`
- happy path 由各 skill 的 `Entry Gate` / `Exit Handoff` + 证据自路由（读 `features/<id>/progress.md`）驱动，疑难才调用可选的 `devflow-router` 仲裁
- Reviewers dispatched (later phases, 由 `/devflow-build` 编排者**顺序**派发):
  - `devflow-test-review`
  - `devflow-code-review`（仅在 test-review 通过后，不并行）

## When to use

- DTS / 紧急缺陷 / 已上线问题进入修复流程
- AR 路线中遇到需要先按问题分析处理的回归
- 用户明确要求按 hotfix 处理

不适用：

- 普通 AR 实现 → `/devflow-build`
- 仅做规格澄清 → `/devflow-specify`
- 仅做组件 / AR 设计 → `/devflow-design`

## Hard contract（节选自 AGENTS.md，不可绕开）

- `hotfix` profile 首判由 `devflow-problem-fix` 做出并写入 `progress.md`；确属疑难的升级判断交可选的 `devflow-router` 仲裁；**不允许静默降级 / 跨子街区切换**
- `requirement-analysis` 子街区**不允许** 路由到 `devflow-problem-fix`
- `devflow-problem-fix` 在任何代码修改前必须先完成复现 + 根因 + 最小安全修复边界的工件证据；缺失即不得进入 `devflow-tdd-implementation`
- 进入实现后仍走标准顺序门禁链：`devflow-test-review` → `devflow-code-review` → `devflow-completion-gate` → `devflow-finalize`，**不可** 因 `hotfix` 跳过任一评审 / 门禁（评审链顺序、不并行 fan-out；见 `references/devflow-conventions.md` §9）
- `auto` execution mode 不豁免任何评审与门禁

## Workflow（不复制 SKILL.md，只编排）

1. 读 `features/<id>/progress.md`（DTS / 紧急缺陷的 work item）：
   - work item 尚未创建 → 退回 `/devflow`（`using-devflow` 发现 / 证据自路由；疑难交可选的 `devflow-router` 仲裁）入口建档
   - profile 未定 → 进入步骤 2 由 `devflow-problem-fix` 做 `hotfix` 首判并写入 `progress.md`，记录升级原因（确属疑难交可选的 `devflow-router` 仲裁）
2. 进入 `devflow-problem-fix`，严格遵循其 SKILL.md `工作流`：
   - 写复现步骤、最小复现工程 / 测试、影响面、根因证据
   - 给出最小安全修复边界（包括不动什么、为什么不动）
3. 依其 `Exit Handoff` + 证据自路由：
   - 如根因显示需要 AR 设计层调整 → `next_action_or_recommended_skill = devflow-ar-design`（即先走 `/devflow-design` 再回 `/devflow-build`）
   - 否则 → `next_action_or_recommended_skill = devflow-tdd-implementation`，进入 `/devflow-build`
   - 无法唯一映射的疑难 → `reroute = true`，交可选的 `devflow-router` 仲裁
4. `/devflow-build` 阶段：与标准实现一致；`devflow-tdd-implementation` 接收 `devflow-problem-fix` 的复现与最小修复边界作为输入，派发 `devflow-implementer` 子代理
5. 通过顺序评审与门禁后，进入 `/devflow-ship`：`devflow-completion-gate` → `devflow-finalize`
6. `devflow-finalize` 闭环：DTS 不需要 promote `docs/ar-specs/` / `docs/ar-designs/`，但仍需在 `features/<id>/` 留齐 evidence 与 completion 记录

## Anti-rationalization quick refs

| 误判 | 反向行动 |
|---|---|
| "紧急嘛，跳过 test-review / code-review" | 禁止；hotfix 仍走完整顺序门禁链 |
| "我先改一行试试再分析" | 禁止；`devflow-problem-fix` 要求改代码前先完成复现 + 根因 |
| "影响面很小，profile 不用升级到 hotfix" | profile 由 `devflow-problem-fix` 依工件证据首判并写入 `progress.md`，而非主观感受；确属疑难交可选的 `devflow-router` 仲裁 |
| "DTS 不需要 evidence" | 禁止；evidence 是 completion-gate 的输入，缺则门禁卡住 |
