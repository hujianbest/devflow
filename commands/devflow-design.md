---
description: DevFlow 设计阶段——基于已确认规格做软件设计，含接口契约、错误模型与测试设计
---

执行 DevFlow 设计阶段。

1. 前置检查：先从 plan.md 或 `using-devflow` 解析目标组件根与工件根；该组件根下 `features/<id>/spec.md`（或团队覆盖路径）存在且 R1 评审门禁通过（plan.md 门禁表 + reviews/ 记录可核）；否则回 `/devflow-specify` 或 `/devflow-review`。
2. 读取 `skills/devflow-design/SKILL.md` 并按其工作流执行：模块职责 → 接口契约 → 错误模型 → 方案取舍 → 测试设计。
3. 叠加适用的语言规范（`<language>-coding-standards`）与命中 description 的领域开发技能；不要在命令中维护具体扩展清单。
4. 产出目标组件根下 `features/<id>/design.md`（或团队覆盖路径）。完成后进入 R2 门禁：`/devflow-review` 独立评审设计并落盘记录（必经节点）；attended 模式下经人确认后才进入实现。
