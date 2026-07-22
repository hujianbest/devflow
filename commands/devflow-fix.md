---
description: DevFlow 缺陷修复——在标准 change 工件中先复现和根因，再判断 delta 并以 TDD 最小修复
---

执行 DevFlow 缺陷修复。

1. 读取 `skills/devflow-fix/SKILL.md`。确定组件根和 `specs/changes/ARXXX-<topic>/`；DTS/事故号作为 SRS 来源，不能替代 AR change 身份。缺 AR ID、topic 或 `componentMode` 时向人追问。
2. 创建或恢复 `change.json`，执行 baseline preflight。existing 缺 `specs/spec.md`/`specs/design.md` 或基线未 ready 时转 `/devflow-init`。
3. 在 `srs.md` 只记录问题、目标、来源、范围和目标需求；在 `tasks.md` 的缺陷分析区记录环境、最小复现、预期/实际、证据、直接/根本原因、波及范围、测试缺口、最小修复边界和回退。无法复现时停止，不做盲修。
4. 分别判断行为和设计是否变化：
   - canonical 行为/设计正确且只需恢复实现：两份 delta 可写有证据的 N/A，但 delta-design 仍保留复现/回归 Case Index；
   - 设计需改：delta-spec 可 N/A，delta-design 必须用稳定 `DD/DEC/TC` 与组件章节路径/实体键写真实操作；
   - 可观察契约需改：两份 delta 按实际影响更新并走完整阶段门禁。
5. 先完成质量门禁：SRS + delta-spec（含 N/A）经 R1；需要设计变化时进入 `/devflow-design`，设计不变时写标准 N/A delta-design；两种情况都经 R2。只有 R1/R2 passed 且 SRS、delta-spec、delta-design artifacts 均 accepted 才能 build。
6. 在 `tasks.md` 建立复现 Case 与自包含任务，进入 `/devflow-build` 完成 RED→GREEN→REFACTOR，实时更新 `traceability.md`。
7. N/A 只表示 canonical 无变化，不删除质量门禁。修复测试+代码必须经 R3，随后仍进入 `/devflow-ship` 做 DoD、canonical sync 复核、人工确认和 archive。
