---
description: DevFlow 设计阶段——基于已通过 R1 的 SRS/规格增量，编写相对 canonical design/spec 的 delta-design
---

执行 DevFlow 设计阶段。

1. 读取当前 `specs/changes/ARXXX-<topic>/change.json`，确认 baseline preflight 通过，R1 gate 与 `reviews/` 最终记录一致且 verdict 为通过；否则回 `/devflow-specify` 或 `/devflow-review`。
2. 读取 `srs.md`、`delta-spec.md` 及 `change.json` 中的 base revision；existing 读取 `specs/spec.md`、`specs/design.md`，new 将两份 canonical 明确视为 `EMPTY`。base 后存在并行变化或基线不一致时停止并向人澄清。
3. 读取 `skills/devflow-design/SKILL.md` 并执行：用稳定 `DD/DEC/TC`、组件模板章节路径/实体键与 `ADDED / MODIFIED / REMOVED / RENAMED` 写 `delta-design.md`，覆盖职责、接口契约、错误模型、所有权、方案取舍和测试设计；未涉及的组件设计基线不得重定义。
4. 叠加适用的 `devflow-clean-code`、`<language>-coding-standards` 与按 description 命中的领域技能。更新 `traceability.md` 的 Design Section/Case 列；不要把 gate 状态写入 `tasks.md`。
5. 行为和设计基线均不变的缺陷可把 `delta-design.md` 写为有证据的 N/A；设计需变时必须写真实 delta。
6. 完成后在 `change.json` 把 R2 置为 `pending`，进入 `/devflow-review`：独立评审 delta-design 相对 canonical design/spec 和 R1 输入。R2 未通过前不进入实现。
