---
description: DevFlow 规格阶段——在标准 change 目录产出可测试 SRS 与相对 canonical spec 的 delta
---

执行 DevFlow 规格阶段。

1. 加载 `using-devflow` 技能，创建或读取 change 并通过 baseline preflight。
2. 加载 `devflow-specify` 技能及其直接 references。
3. 完整执行规格澄清、SRS、delta spec、追溯骨架和 R1 交接；该 SKILL 是规格工件与门禁的唯一行为契约。
