---
description: DevFlow 实现阶段——按测试设计逐用例 RED→GREEN→REFACTOR，测试先行不可妥协
---

执行 DevFlow 实现阶段。

1. 前置检查：先从 plan.md 或 `using-devflow` 解析目标组件根与工件根；正常实现入口要求该组件根下 `features/<id>/design.md`（或团队覆盖路径）存在、R2 评审门禁通过（plan.md 门禁表 + reviews/ 记录可核）且含测试设计表；R3 返工入口要求 plan.md 的 R3 门禁为 `rework`，且 reviews/ 中存在未闭环 findings。两类入口都不满足时，回 `/devflow-design` 或 `/devflow-review`。
2. 读取 `skills/devflow-tdd/SKILL.md` 并按其循环执行；runtime 支持 subagent 时必须逐任务派发 implementer subagent（角色定义 `agents/devflow-implementer.md`，输入为 Context Pack 而非聊天历史），主会话只做 controller，不在主上下文直接写测试或实现。实现与重构遵循 `skills/devflow-clean-code/SKILL.md` 与适用的语言/领域技能（按语言加载 `<language>-coding-standards`，如 c/cpp/java/python；领域加载 `embedded-development` / `automotive-coding-standards` / `frontend-development` / `backend-development`）。
3. 先按 `plan-template.md` 细化同一组件根/工件根下 `features/<id>/plan.md`（或团队覆盖路径）任务拆解（自包含任务：用例锚点、精确路径、步骤、完成定义、依赖/就绪条件），再逐任务执行；任务状态、步骤勾选与 RED/GREEN 证据行实时写回 plan.md，任务完成时更新 `traceability.md` 对应列；一次一个任务，每任务完成即提交。中断恢复从 plan.md 第一个唯一可执行的未完成任务继续。
4. 实现中发现规格或设计问题 → 停下，在 plan.md 记录阻塞，回对应阶段修正工件并重新评审，不在代码里绕过。
5. 若从 R3 返工入口进入：先读最新测试/代码评审记录，把 open findings 写入 plan.md 的评审返工队列；按 `devflow-tdd` 的 R3 返工模式修复、记录证据、回填 Resolution。全部 open findings 闭环后，下一步是 `/devflow-review` 复审，不是 `/devflow-ship`。
6. TDD 阶段连续处理 plan 中的任务队列：一个任务 `DONE` 后不询问是否进入下一个，只要能从 plan.md 唯一选择下一任务就继续派发新的 implementer subagent；只有 runtime 无 subagent 能力时才按 `devflow-tdd` 记录原因后 controller-direct 执行。只有命中 `devflow-tdd` 的 hard stop、全部任务完成或 R3 返工闭环时才离开任务循环。
7. 全部任务完成且没有 R3 open findings 后进入 R3 门禁：`/devflow-review` 对测试与代码独立评审（必经节点）；R3 通过并按运行模式完成确认后走 `/devflow-ship` 收尾。
