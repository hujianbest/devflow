---
description: DevFlow 独立评审——以独立上下文评审规格/设计/测试/代码，作者永不自审
---

执行 DevFlow 独立评审。

1. 确认评审目标（spec / design / 测试 / 代码；用户未指明时按工件状态推断并确认）。
2. 读取 `skills/devflow-review/SKILL.md`，按其协议派发独立 subagent 执行评审：输入只给被评审产物、上游工件、对应 rubric 与适用的语言/领域技能，不给作者推理过程。
3. 评审产出 findings（位置 + 问题 + 严重级）与 verdict，写入 `features/<id>/reviews/`。
4. 把结果呈给用户做最终把关；评审者不直接修改任何产物。
