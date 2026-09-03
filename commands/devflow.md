---
description: DevFlow 入口——从 change.json 与 tasks.md 恢复交付进度，执行 baseline preflight 并路由到正确阶段
---

进入 DevFlow 工作流。

1. 加载 `using-devflow` 技能及其直接 references。
2. 创建或读取目标 change，执行 baseline preflight，并核对 `change.json`、磁盘工件、评审和任务断点。
3. 按入口技能的恢复路由选择唯一下一阶段；无法唯一判断时列出事实并询问。
4. 读取并完整执行该阶段的 SKILL；它是该阶段路径、状态和门禁的唯一行为契约。
