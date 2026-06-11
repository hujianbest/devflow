---
description: DevFlow 设计阶段——基于已确认规格做软件设计，含接口契约、错误模型与测试设计
---

执行 DevFlow 设计阶段。

1. 前置检查：`features/<id>/spec.md` 存在且已获人确认；否则回 `/devflow-specify`。
2. 读取 `skills/devflow-design/SKILL.md` 并按其工作流执行：模块职责 → 接口契约 → 错误模型 → 方案取舍 → 测试设计。
3. 叠加适用的语言规范（`<language>-coding-standards`，如 c/cpp）与领域约束（`embedded-development` / `automotive-development`）。
4. 产出 `features/<id>/design.md`。完成后建议用户：人工审查或用 `/devflow-review` 做独立预审；设计确认前不进入实现。
