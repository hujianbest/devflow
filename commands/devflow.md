---
description: DevFlow public entry — load the DevFlow principles, discover the relevant skill family phase, and delegate runtime routing to devflow-router when state must be recovered
---

This command orchestrates the **DevFlow entry / resume** phase. It loads `using-devflow` as the family-level principles and discovery entry before handing runtime state decisions to `devflow-router` or handing explicit authoring / execution work to the relevant phase command.

## Phase scope

- Skills involved (in推进顺序):
  1. `using-devflow` — DevFlow 总纲 + public discovery entry；先应用全局原则，再识别相关 skill
  2. `devflow-router` — runtime routing（当需要恢复状态、消费评审/门禁、判定 profile / execution mode、处理证据冲突或派发 reviewer 时）
- Reviewers dispatched: 无（本 command 不直接派发评审；如路由到评审节点，由阶段 command 与 router 共同完成）

## When to use

- 新会话不确定从哪进入 DevFlow
- 用户说"继续 / 推进 / 开始做"但当前节点未确认
- 评审 / 门禁刚结束需要消费 verdict 决定下一步
- 不确定走 `/devflow-specify`、`/devflow-design`、`/devflow-build`、`/devflow-ship` 还是 `/devflow-fix`

不适用：

- 已在某个 leaf skill 内部继续执行 → 直接继续该 skill
- 已知阶段明确 → 直接用对应阶段 command

## Hard contract（节选自 AGENTS.md，不可绕开）

- `using-devflow` 是 public entry，**永远不能** 写入 `Next Action Or Recommended Skill` 或任何 handoff 字段
- 任何无法唯一映射到一个 leaf 的延续 / 恢复 / profile 决定 / 评审 verdict 消费 → 必须交 `devflow-router`
- 决策只来自磁盘工件，与聊天记忆冲突取工件

## Workflow（不复制 SKILL.md，只编排）

1. 载入 `using-devflow`，先应用 DevFlow 总纲，再按其 discovery / invocation 规则识别相关 skill
2. 若需要读取工件状态才能决定下一步，立即载入 `devflow-router`，由其按工件证据决定唯一 runtime 节点
3. 若用户明确要求某个 authoring / execution 阶段且无需 runtime 状态判断，把控制交给对应阶段 command：`/devflow-specify`、`/devflow-design`、`/devflow-build`、`/devflow-ship`、`/devflow-fix`
4. 形成 canonical handoff 块；`next_action_or_recommended_skill` 仅限 canonical runtime 节点，不能是 `using-devflow`

## Anti-rationalization quick refs

| 误判 | 反向行动 |
|---|---|
| "用户说继续就直接进 TDD" | 禁止；`using-devflow` 只做入口发现，继续 / 恢复必须进 `devflow-router` |
| "看起来是评审刚过，我替它写下一步" | 禁止；评审后恢复一律 `devflow-router` 消费 verdict |
| "把 `using-devflow` 写进 handoff 表示入口" | 禁止；它是 public entry，不是 canonical 节点 |
