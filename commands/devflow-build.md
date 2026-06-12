---
description: DevFlow 实现阶段——按测试设计逐用例 RED→GREEN→REFACTOR，测试先行不可妥协
---

执行 DevFlow 实现阶段。

1. 前置检查：`features/<id>/design.md` 存在、R2 评审门禁通过（plan.md 门禁表 + reviews/ 记录可核）且含测试设计表；否则回 `/devflow-design` 或 `/devflow-review`。
2. 读取 `skills/devflow-tdd/SKILL.md` 并按其循环执行；runtime 支持时默认逐任务派发 implementer subagent（角色定义 `agents/devflow-implementer.md`，输入为 Context Pack 而非聊天历史）。实现与重构遵循 `skills/devflow-clean-code/SKILL.md` 与适用的语言/领域技能（按语言加载 `<language>-coding-standards`，如 c/cpp；领域加载 embedded/automotive-development）。
3. 先按 `plan-template.md` 细化 `features/<id>/plan.md` 任务拆解（自包含任务：用例锚点、精确路径、步骤、完成定义），再逐任务执行；任务状态、步骤勾选与 RED/GREEN 证据行实时写回 plan.md，任务完成时更新 `traceability.md` 对应列；一次一个任务，每任务完成即提交。中断恢复从 plan.md 第一个未完成任务继续。
4. 实现中发现规格或设计问题 → 停下，在 plan.md 记录阻塞，回对应阶段修正工件并重新评审，不在代码里绕过。
5. 全部任务完成后进入 R3 门禁：`/devflow-review` 对测试与代码独立评审（必经节点）；按运行模式取得人工确认后走 `/devflow-ship` 收尾。
