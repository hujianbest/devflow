---
description: DevFlow 实现阶段——以 tasks.md 为执行断点，逐任务派发 implementer 完成 RED→GREEN→REFACTOR
---

执行 DevFlow 实现阶段。

1. 读取当前 `specs/changes/ARXXX-<topic>/change.json`、`tasks.md` 和 `reviews/`：
   - 正常入口要求 R2 最终通过且记录可核；
   - R3 返工入口要求 R3 为 `rework`，并存在未闭环 finding；
   - 其他状态回 `/devflow-design` 或 `/devflow-review`。
2. 读取 `skills/devflow-tdd/SKILL.md`。按 `delta-design.md` 的 Case ID 细化/校验 `tasks.md`：每个任务自包含需求条目、Case、允许文件、RED/GREEN/REFACTOR、命令、完成定义和依赖；任务集合必须精确覆盖批准的 Case ID。
3. runtime 支持 subagent 时，每个任务派发全新上下文的 `devflow-implementer`（`agents/devflow-implementer.md`），传 Context Pack：SRS/delta/canonical 摘录、当前 task、允许文件、命令、Quality Stack；不传聊天历史。主控 Agent 不直接替 implementer 写实现。
4. 每次只运行一个 in-progress 任务。消费返回后把真实证据写入 `tasks.md`，更新 `traceability.md`；状态冲突、多个同等候选或工件不一致时停止，不猜下一任务。
5. 一个任务 done 后，只要可唯一选择下一个任务就继续派发，不因 attended 模式停顿。缺陷任务同样先看复现测试 RED，再做最小修复。
6. R3 返工时，把 finding 映射为返工任务，保留旧证据并追加新证据；作者侧回填原 review 的 Resolution。规格/设计错误回对应上游并重新经过受影响门禁。
7. 全部任务完成且无 open R3 finding 后，在 `change.json` 把 R3 置为 `pending`，进入 `/devflow-review` 对测试+代码做联合独立评审。R3 返工闭环后也是先复审，不能直接 `/devflow-ship`。
