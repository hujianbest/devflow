# Definition of Done

> 配套 `devflow-ship`。每项必须写 `passed + 证据`；`failed`、`pending`、无证据的 `N/A` 或 accepted warning 都阻塞 closeout 与 archive。

## A. 身份、模式与工件

1. `change.json` 的 ID/topic 与 `specs/changes/ARXXX-<topic>/` 一致，`componentMode`、profile、artifact 图、base revision、gates 和 archive 元数据结构完整。
2. `componentMode: existing` 时，`specs/spec.md` 与 `specs/design.md` 均存在且为 `baseline-ready`；`componentMode: new` 时，两份 delta 能从空基线生成完整首版 canonical。
3. `srs.md`、`delta-spec.md`、`delta-design.md`、`tasks.md`、`traceability.md`、`reviews/` 均存在且相互引用一致。
4. 生命周期状态只在 `change.json`，任务状态和 TDD 证据只在 `tasks.md`；两者没有重复或冲突的状态来源。

## B. SDD 与独立评审

5. SRS 的范围/非范围、FR/IFR Acceptance、NFR 完整 QAS、CON Verification、错误路径和 Source 已闭合，无 blocking unknown。
6. R1 最终记录存在且通过；`delta-spec.md` 相对 canonical spec/空基线正确，critical/important findings 的 Resolution 全部有效。
7. R2 最终记录存在且通过；`delta-design.md` 相对 canonical design/spec 或空基线正确，测试设计覆盖全部增量需求，Resolution 全部有效。
8. 缺陷若声明 delta N/A，R1/R2 已独立验证 canonical 的预期行为和设计确实无需变化；不能用 N/A 省略记录。

## C. TDD、实现与 R3

9. `tasks.md` 全部任务为 done；每个任务有真实 RED/GREEN/REFACTOR 命令、关键输出和代码锚点。
10. 所有 Case ID 均有测试；每条 FR/IFR Acceptance、NFR 完整 QAS 和 CON Verification 都有通过的测试或静态/构建证据；修改/删除有回归或删除后语义测试。
11. 缺陷复现测试在修复前因目标缺陷失败、修复后通过；delta N/A 不降低此要求。
12. 完整测试套件在最终代码上全绿，构建无新增警告，静态分析新增问题已修复或有精确理由。
13. R3 测试+代码最终记录存在且通过；mutation 抽查、错误/资源路径和范围 diff 已检查，所有 critical/important Resolution 闭合。
14. 实现只覆盖 SRS/delta 范围，并与批准的 delta-design 及 canonical 基线一致；任何偏离已回上游修订并重新评审。

## D. Clean Code 与约束证据

15. `devflow-clean-code`、每种适用语言的 `<language>-coding-standards` 和命中的领域技能均有证据状态：

| 状态 | 要求 |
|---|---|
| `clean` | 引用任务 REFACTOR、R3、静态分析或代码锚点 |
| `documented-debt` | 不影响本次语义，且有可定位 issue/change 去向 |
| `N/A` | 说明为何不适用 |
| `critical-open` | 直接阻塞 |

只写 `clean` 而无证据按缺口处理。

## E. 追溯与 Resolution

16. `traceability.md` 中每条核心需求均以需求条目 → Spec Section → Design Section/Case → Task → Code/Test → Evidence 全链路闭合。
17. 任一 N/A 都有具体理由和 canonical/证据锚点；无理由空列或为赶进度补 N/A 均为 critical。
18. `reviews/` 每轮记录可追溯；上一轮 critical/important 不会在复审中无 Resolution 消失；最终记录与 `change.json` gate 状态一致。
19. 债务均不改变本次已批准语义，并有 owner 与可定位去向；“后续优化”不是去向。

## F. Canonical Sync

20. 主控 Agent 已读取 SRS、两份 delta、同步前 canonical 和 base revision；base 后并行变化、工作树既有改动及语义歧义均已由人明确处理。
21. delta 的每个 `ADDED / MODIFIED / REMOVED / RENAMED` 均映射到 canonical Git diff；所有 canonical diff hunk 都有 delta 来源。
22. 未涉及的规格稳定 ID、组件设计章节/实体行、约束和契约保持语义不变；删除仅来自明确 `REMOVED`。
23. `specs/spec.md` 与 `specs/design.md` 无冲突、重复、占位符或悬空引用，且 spec-design 一致。
24. canonical-only Git diff 已展示；独立只读 canonical sync review 记录存在于同一 `reviews/`，最终 verdict 通过，Resolution 全部闭合。
25. 实际修改或新建的 canonical 在同步时先置 draft；其 `baselineRevision` 等于不可变的 `change.json.baseRevision`，`baselineChange` 指向当前 change；sync review 与人工确认后，`independentReview`、`humanConfirmation`、provenance/revision log 和 `baselineStatus: baseline-ready` 与真实记录一致。N/A 未修改文档未被无故重写 metadata。
26. 两份 delta 均 N/A 或 canonical diff 为空时，sync review 仍验证了 N/A、无误改和 spec-design 一致性。

## G. 人工确认、Closeout 与 Archive

27. 无论 attended/unattended，人已明确确认最终 canonical diff、DoD 结果和 archive 目标；确认人、时间和范围可核。
28. `closeout.md` 按模板记录 DoD、四个最终 review、sync 摘要、验证、债务和确认；移动后 archive 内副本的归档结果已回填。
29. `specs/archive/YYYY-MM-DD-ARXXX-<topic>/` 在移动前不存在；目标命名与日期/change 身份一致。
30. 整个活动 change 目录使用标准 move/rename 原样移动；源目录不保留副本，archive 内工件齐全，canonical 留在 `specs/` 根；移动后归档内 manifest 的 `archive.status`、确认人和时间已写实。
31. 移动后完整 Git diff 已展示，正常 CI/验证已进入执行；失败现场未使用破坏性 reset 清理。

## 缺陷裁剪边界

行为与设计基线不变时，两份 delta 可明确 N/A；可裁剪的是 delta 内容量，不是 SRS、复现测试、tasks 证据、R1/R2 对 N/A 的验证、R3、traceability、canonical sync review、DoD 或最终人工确认。
