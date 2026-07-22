---
description: DevFlow 规格阶段——在标准 change 目录产出可测试 SRS 与相对 canonical spec 的 delta
---

执行 DevFlow 规格阶段。

1. 解析组件根和 `specs/changes/ARXXX-<topic>/`，先创建或读取 `change.json`。AR 身份、topic、`componentMode`、profile 或运行模式缺失时向人询问，不自行推断。
2. 执行 baseline preflight：
   - existing 要求 `specs/spec.md` 与 `specs/design.md` 均为 `baseline-ready`，否则转 `/devflow-init`；
   - new 允许 canonical 缺失，后续 delta 必须能从空基线创建首版；
   - 创建时记录不可变 `change.json.baseRevision`，并在两份 delta 中记录各自 canonical base 元数据；后续不得为消除并行变化而改写 `baseRevision`。
3. 读取 `skills/devflow-specify/SKILL.md` 并执行：澄清来源/目标/范围 → 编写 `srs.md` → 以稳定 ID 和 `ADDED / MODIFIED / REMOVED / RENAMED` 编写 `delta-spec.md` → 初始化 `traceability.md` 与 `tasks.md` 骨架 → 自检。
4. 所有工件只写入当前 change 根。生命周期、门禁和 artifact 状态写 `change.json`；`tasks.md` 只保存任务结构与后续 TDD 证据。
5. 行为基线不变的缺陷可以在 `delta-spec.md` 明确 N/A，但必须引用 canonical stable ID 并证明不改变接口、错误语义、状态机、阈值或兼容承诺。
6. 完成后把 R1 置为 `pending`，进入 `/devflow-review`：独立评审 `srs.md + delta-spec.md` 相对 canonical spec/空基线，记录写入同一 `reviews/`。R1 未通过前不进入设计。
