---
description: DevFlow 入口——从 change.json 与 tasks.md 恢复新工作流，执行 baseline preflight 并路由到正确阶段
---

进入 DevFlow 工作流。

1. 读取 `skills/using-devflow/SKILL.md`，以其中的组件根、change 契约、baseline preflight 和恢复规则为准。
2. 确定 `<component-root>`，只在固定路径 `specs/changes/ARXXX-<topic>/` 查找活动 change。用户未指定且存在多个活动 change 时列出候选并询问；不要凭最近修改时间猜。归档 change 不作为活动 change 恢复。
3. 新 change 先取得人明确给出的 AR ID、topic、`componentMode: new|existing` 和运行模式；缺失或模式与仓库现状冲突时追问。把身份、profile、artifact 图、base revision、gates、运行模式和 archive 状态写入 `change.json`。
4. 每次开始/恢复都先读 `change.json`：
   - existing：`specs/spec.md` 与 `specs/design.md` 必须同时存在且为 `baseline-ready`，否则只路由 `/devflow-init`；
   - new：不执行 init，允许 canonical 尚不存在，但 delta 必须可生成首版；
   - 模式缺失、冲突或无法判断：停止并向人澄清。
5. 生命周期和门禁只以 `change.json` 为准；任务断点和 TDD 证据只以同一 change 的 `tasks.md` 为准；用 `reviews/` 和 `traceability.md` 交叉校验，冲突时阻塞而不是自动修状态。
6. 路由：
   - SRS / delta-spec 未完成，或 R1 `rework` → `/devflow-specify`
   - R1 `pending` → `/devflow-review`（R1）
   - R1 通过且 delta-design 未完成，或 R2 `rework` → `/devflow-design`
   - R2 `pending` → `/devflow-review`（R2）
   - R2 通过且 tasks 有未完成项，或 R3 `rework` → `/devflow-build`
   - tasks 全部完成且 R3 `pending` → `/devflow-review`（R3）
   - R1-R3、Resolution、traceability 和任务均闭环，但 canonicalSync 为 pending/rework/blocked → `/devflow-ship` 的并行变化预检、智能同步与独立复核
   - canonicalSync passed，但 closeout 或 archive 未完成 → `/devflow-ship` 的 closeout 核验与目录归档
7. `pending` 表示去独立评审；`rework` 表示先回作者阶段修复并回填 Resolution，再复审。attended 只在 R1-R3 通过后增加人工停顿；unattended 不删除评审、记录或阻塞。canonical diff 与归档在两种模式下都必须最终人工确认。
