---
description: DevFlow 设计阶段——基于已通过 R1 的 SRS/规格增量，编写相对 canonical design/spec 的 delta-design
---

执行 DevFlow 设计阶段。

1. 加载 `using-devflow` 技能，确认 change 已通过 baseline preflight 和 R1。
2. 加载 `devflow-design` 技能及其直接 references，并加载适用的质量叠加技能。
3. 完整执行增量设计、测试设计、追溯更新和 R2 交接；该 SKILL 是设计阶段的唯一行为契约。
