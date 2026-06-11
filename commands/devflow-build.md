---
description: DevFlow 实现阶段——按测试设计逐用例 RED→GREEN→REFACTOR，测试先行不可妥协
---

执行 DevFlow 实现阶段。

1. 前置检查：`features/<id>/design.md` 存在、已获人确认且含测试设计表；否则回 `/devflow-design`。
2. 读取 `skills/devflow-tdd/SKILL.md` 并按其循环执行；同时加载 `skills/devflow-clean-code/SKILL.md` 与适用的语言/领域技能（c/cpp-coding-standards、embedded/automotive-development），在 GREEN 与 REFACTOR 中遵循。
3. 在 `features/<id>/tasks.md` 维护任务状态；一次一个任务，每任务完成即提交。
4. 实现中发现规格或设计问题 → 停下，回对应阶段修正工件，不在代码里绕过。
5. 全部任务完成后建议用户：用 `/devflow-review` 对测试与代码做独立评审。
