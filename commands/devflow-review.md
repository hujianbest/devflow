---
description: DevFlow 独立评审——以只读 reviewer 执行 R1、R2、R3 或 canonical sync，并在同一 reviews 目录闭环
---

执行 DevFlow 独立评审。

1. 读取当前 `specs/changes/ARXXX-<topic>/change.json` 确定 gate；用户明确指定 gate 时仍要校验工件状态。存在多个可能目标或状态矛盾时先确认，不猜。
2. 读取 `skills/devflow-review/SKILL.md` 和对应 rubric，组装 Review Pack：
   - R1：`srs.md + delta-spec.md` 相对 `specs/spec.md`/空基线；
   - R2：`delta-design.md` 相对 canonical design/spec 与已通过 R1 的输入；
   - R3：测试+代码 diff，相对 SRS、两份 delta、canonical、`tasks.md`、`traceability.md`、真实 TDD/套件输出和主控 Agent 的隔离 mutation 证据；
   - canonical sync：同步前后 canonical、canonical-only Git diff、SRS、两份 delta、base revision 和 R1-R3 记录。
3. 派发全新上下文的 `devflow-reviewer`（`agents/devflow-reviewer.md`）。reviewer 只读，不编辑任何工件、代码、review 或 manifest，也不运行命令；输入不足返回阻塞。
4. 主控 Agent 将 reviewer 返回原样落盘到当前 change 的 `reviews/r1-review-...`、`r2-review-...`、`r3-review-...` 或 `canonical-sync-review-...`；复审追加轮次。记录落盘后才更新 `change.json`：失败写 blocked/rework；reviewer 通过时，attended 的 R1-R3 要等人工确认才 passed，canonical sync 在任何模式都等最终人工确认才 passed。R1 passed 同时把 SRS/delta-spec artifacts 写为 accepted；R2 passed 把 delta-design 写为 accepted；R3 只核验 tasks/traceability 已由 TDD 写为 complete。
5. verdict 非通过时回对应作者阶段定向返工，逐条回填原记录 Resolution，再发起独立复审。R3 普通问题回 `/devflow-build`；明确合并错误回 `/devflow-ship` 重新同步；规格/设计问题回对应上游。reviewer 不下场修复。
6. critical/important 未闭环、record 与 gate 不一致或超过 3 轮仍失败时不得推进；第 3 轮后停止自动循环并把最小决策点交给人。
7. attended 下 R1/R2/R3 通过后呈人确认再推进；unattended 不停顿但评审和记录不减少。canonical sync 通过后仍须由 `/devflow-ship` 展示最终 diff 并取得人工归档确认。
