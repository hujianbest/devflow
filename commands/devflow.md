---
description: DevFlow public entry — discover where this session belongs and route to the right phase command or canonical skill
---

This command orchestrates the **DevFlow entry / resume** phase.

## Phase scope

- Skills involved:
  1. `using-devflow` — public entry meta：把意图映射到唯一 leaf skill，并施加 DevFlow 共同行为准则
  2. `devflow-router` — **可选**疑难仲裁（仅当证据冲突 / 跨子街区嫌疑 / profile 升级 / 多 in_progress task / verdict 无法唯一映射时）
- Reviewers dispatched: 无（本 command 不直接派发评审）

## When to use

- 新会话不确定从哪进入 DevFlow
- 用户说"继续 / 推进 / 开始做"但当前节点未确认
- 不确定走 `/devflow-specify`、`/devflow-design`、`/devflow-build`、`/devflow-ship` 还是 `/devflow-fix`

不适用：

- 已在某个 leaf skill 内部继续执行 → 直接继续该 skill
- 工件已存在、可按证据恢复 → 读 `features/<id>/progress.md` 的 `Current Stage` + `Next Action Or Recommended Skill`，直接进对应 leaf（证据自路由）
- 已知阶段明确 → 直接用对应阶段 command

## Hard contract（节选自 AGENTS.md，不可绕开）

- `using-devflow` 是 public entry meta-skill，**永远不能**写入 `Next Action Or Recommended Skill` 或任何 handoff 字段
- happy path 由各 skill 的 Entry Gate / Exit Handoff + 证据自路由推进，**不必**每步过 router
- 仅疑难（证据冲突 / 跨子街区 / profile 升级 / 多 in_progress task / verdict 无法唯一映射）→ 交可选的 `devflow-router` 仲裁
- 决策只来自磁盘工件，与聊天记忆冲突取工件

## Workflow（不复制 SKILL.md，只编排）

1. 载入 `using-devflow`，按其 `Discovery` 把意图映射到唯一 leaf；只差一个事实 → 用「单事实检查点」补一个判别问题
2. 输出二选一：
   - 唯一 canonical leaf + 工件证据稳定 → 进入对应阶段 command 或直接进入该 leaf skill 的 Entry Gate
   - 属疑难 → 载入 `devflow-router` 仲裁，由其按工件证据收敛唯一下一步
3. 阶段确定后，把控制交给对应阶段 command：`/devflow-specify`、`/devflow-design`、`/devflow-build`、`/devflow-ship`、`/devflow-fix`
4. 形成 canonical handoff 块；`next_action_or_recommended_skill` 仅限 canonical 节点之一（见 `references/devflow-conventions.md` §6）

## Anti-rationalization quick refs

| 误判 | 反向行动 |
|---|---|
| "用户说继续就直接进 TDD" | 先 `using-devflow` 映射意图 / 读 `progress.md` 证据恢复；缺上游工件进缺失的上游 leaf |
| "评审刚过，我替它写下一步" | 读最新 `reviews/` verdict 按 Exit Handoff / dispatch 协议推进；无法唯一映射 → `devflow-router` 仲裁 |
| "把 `using-devflow` 写进 handoff 表示入口" | 禁止；它是 public entry meta，不是 canonical 运行节点 |
| "每步都先过 router 更稳" | 2.0 去中枢；router 只处理疑难，happy path 由 Exit Handoff + 证据自路由承担 |
