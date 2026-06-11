---
description: DevFlow 入口——加载工作流总纲，从工件恢复进度并进入正确的阶段
---

进入 DevFlow 工作流。

1. 读取 `skills/using-devflow/SKILL.md`，应用其行为准则。
2. 用户给出工作项 ID 或目录时，按其「工件约定」一节的恢复表判断当前阶段：检查 `features/<id>/` 下 spec.md / design.md / tasks.md / reviews/ 的存在与确认状态，进入对应技能。
3. 全新任务且无工件 → 从 `devflow-specify` 开始。
4. 工件与聊天记忆冲突时以工件为准；阶段判断不确定时把状态摘要呈给用户确认，不猜。
