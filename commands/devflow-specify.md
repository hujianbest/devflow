---
description: DevFlow 规格阶段——把需求澄清成可测试的规格，先规格后设计与代码
---

执行 DevFlow 规格阶段。

1. 读取 `skills/devflow-specify/SKILL.md` 并按其工作流执行：澄清 → 需求条目（EARS + Given/When/Then + Change Type）→ NFR QAS → 粒度检查 → 自检。
2. 产出 `features/<id>-<slug>/spec.md`。
3. 业务方向、优先级、验收阈值的缺口列为 Open Questions 交回用户，不替用户拍板。
4. 完成后建议用户：人工审查或用 `/devflow-review` 对 spec 做独立预审；规格确认前不进入设计。
