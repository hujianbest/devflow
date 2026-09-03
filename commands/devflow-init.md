---
description: DevFlow 既有组件基线初始化——只读逆向并建立或补齐 specs/spec.md 与 specs/design.md
---

为既有组件执行 DevFlow canonical baseline 初始化。

1. 加载 `using-devflow` 技能，解析组件根并确认这是 `componentMode: existing` 的基线初始化。
2. 加载 `devflow-init` 技能及其直接 references。
3. 完整执行其中的只读取证、事实分级、澄清、独立评审和人工确认协议。
4. 报告实际生成、保持不变或阻塞的 canonical 文档及 preflight 结果。
