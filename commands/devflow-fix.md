---
description: DevFlow 缺陷修复——先复现和根因，再最小修复；没有失败的测试就没有修复
---

执行 DevFlow 缺陷修复。

1. 读取 `skills/devflow-fix/SKILL.md` 并按其工作流执行：复现 → 根因（直接原因/根本原因/波及范围）→ 修复边界 → TDD 修复。
2. 产出目标组件根下 `features/DTS<id>-<slug>/fix.md`（或团队覆盖路径）；修复实现先写复现缺陷的失败测试，再修到绿。
3. 根因属于契约变更 → 转 `/devflow-specify`；属于设计缺陷 → 转 `/devflow-design`。
4. 完成后建议用户：用 `/devflow-review` 评审修复代码与测试。
