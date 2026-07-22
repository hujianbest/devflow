# Canonical Sync 评审 Rubric

> 评审对象：同步前后的 `specs/spec.md`、`specs/design.md`，以及仅包含这两份文件的 Git diff。上游：`srs.md`、`delta-spec.md`、`delta-design.md`、base revision 和 R1-R3 记录。
>
> 核心怀疑：**本次增量是否被完整吸收，同时没有改坏任何未涉及的当前真相？**

## 输入完整性（缺失即阻塞）

- [ ] 可读取同步前、同步后 canonical 全文及 canonical-only Git diff
- [ ] 两份 delta、SRS、base revision 和 `change.json` 身份一致
- [ ] base revision 后的并行变化已由人明确处置；reviewer 不替人推断合并意图
- [ ] Git diff 不含 canonical 之外的文件；额外改动另行展示但不混入本评审

## Delta 完整吸收（不过 = critical）

- [ ] 为每个 `ADDED / MODIFIED / REMOVED / RENAMED` 建立到 canonical diff 的明确映射
- [ ] 每个操作的全部语义、约束、错误行为、兼容要求和设计影响均已落入 canonical
- [ ] 没有只吸收摘要而丢失验收、契约、阈值、失败语义或测试设计
- [ ] delta 为 N/A 时 canonical diff 为空，或每个非空变化都有独立、已批准来源

## 既有语义保留（不过 = critical）

- [ ] 未被 delta 指向的规格稳定 ID、组件设计章节/实体行、表格和契约保持语义不变
- [ ] 修改只替换明确目标，不因重排、压缩或改写误删其他约束
- [ ] 删除仅发生在显式 `REMOVED` 范围，引用和兼容处理完整
- [ ] `RENAMED` 保持功能编号等稳定业务键与正文语义，显示名称和受影响引用按 from/to 更新
- [ ] 随机抽查至少 2 个未涉及章节，与同步前版本语义一致

## 冲突与来源闭合

- [ ] 反查 canonical diff 的每个 hunk 都能回指 delta 操作
- [ ] 同一规格 ID 或组件设计章节/实体键没有互斥要求、重复定义或新旧语义并存
- [ ] canonical 中不存在未解决标记、临时说明、过程性评审应答或占位符
- [ ] SRS、delta 与 canonical 的术语、单位、阈值和错误语义一致
- [ ] 有正文变化的 canonical 已进入 draft/pending metadata；N/A 未修改文档未被无故重写 metadata

## Spec-Design 一致性（不过 = critical）

- [ ] canonical design 覆盖 canonical spec 的新增/修改行为
- [ ] design 没有引入 spec 未批准的行为、接口、默认值或兼容承诺
- [ ] 接口、状态机、错误模型、所有权和时序与 spec 可观察语义一致
- [ ] 测试设计仍能覆盖组件规格中的 FR/IFR Acceptance、NFR 完整 QAS 和 CON Verification
- [ ] 删除/重命名在 spec 与 design 两侧同步完成，无悬空引用

## Verdict 指引

- 输入缺失或并行变化未澄清 → `阻塞`
- 漏吸收、误删、无来源 diff、冲突或 spec-design 漂移 → `需修改`
- delta 本身矛盾或上游意图错误 → `重新设计`，指向 `devflow-specify` / `devflow-design`
- 只有四类检查全部通过且无未闭环 critical/important 才能 `通过`

reviewer 只返回记录，不编辑 canonical、delta、review 文件或 `change.json`。未通过时由主控 Agent 修正 delta 或同步结果，再发起新一轮独立复核。
