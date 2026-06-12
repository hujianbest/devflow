---
description: DevFlow 入口——加载工作流总纲，确认运行模式，从工件恢复进度并进入正确的阶段
---

进入 DevFlow 工作流。

1. 读取 `skills/using-devflow/SKILL.md`，应用其行为准则。
2. **全新任务**：先向用户确认一次运行模式（attended：每个评审节点后人工确认 / unattended：连续执行但评审与记录照做），随后从 `devflow-specify` 开始（模式记入 plan.md 头部）。
3. **续作**：先读 `features/<id>/plan.md`（运行模式 + 门禁状态表 + 任务进度），再按 `using-devflow` 恢复表用工件状态校验，进入对应技能；运行模式沿用 plan.md 记录，不重新询问。
4. 工件与聊天记忆冲突时以工件为准；阶段判断不确定时把状态摘要呈给用户确认，不猜。
5. 每个阶段产物完成后必须经 `devflow-review` 评审门禁（R1/R2/R3）并落盘记录；attended 模式下经人确认后才进入下一阶段。
