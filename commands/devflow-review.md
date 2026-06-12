---
description: DevFlow 独立评审——以独立上下文评审规格/设计/测试/代码，作者永不自审
---

执行 DevFlow 独立评审（工作流的 R1/R2/R3 必经门禁，也可对任意目标单独发起）。

1. 确认评审目标（spec / design / 测试 / 代码；用户未指明时按工件状态推断并确认）。
2. 读取 `skills/devflow-review/SKILL.md`，按其协议派发独立 subagent 执行评审：输入只给被评审产物、上游工件、对应 rubric 与适用的语言/领域技能，不给作者推理过程。
3. **落盘评审记录**到同一组件根/工件根下 `features/<id>/reviews/<目标>-review-<日期>.md`（或团队覆盖路径，复审加 `-r2` 轮次）：findings 表含 Resolution 列、verdict、抽查记录。没有记录的评审等于没有评审。
4. verdict 为需修改时：作者按 findings 返工并逐条回写 Resolution（修复+commit / 人接受+理由 / 债务+去向），然后发起复审；critical/important 未闭环不放行。
5. 按 plan.md 运行模式处理确认：attended 呈人同意后更新门禁表进入下一阶段；unattended 不停顿但记录照写、critical 照样阻塞。评审者不直接修改任何产物。
