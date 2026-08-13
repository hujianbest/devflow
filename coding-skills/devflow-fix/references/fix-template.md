# 缺陷 Change 补充结构

缺陷使用标准 change 工件，不创建平行说明文件：

- `srs.md`：`devflow-specify/references/srs-template.md`
- `delta-spec.md`：`devflow-specify/references/delta-spec-template.md`
- `delta-design.md`：`devflow-design/references/delta-design-template.md`
- `tasks.md`：`devflow-tdd/references/tasks-template.md`

本文件只定义缺陷额外需要的内容。两份 delta 的 frontmatter 均保留
`manifest: change.json`。

## srs.md 补充内容

在问题、目标、范围和需求中写明：

- DTS、事故或报告来源；
- 可重复观察的实际行为；
- canonical 规定的预期行为；
- 修复后的可观察成功标准；
- 明确非范围。

需求仍使用标准 `FR/IFR/NFR/CON` 结构和可直接形成 RED 的验收场景。

## delta-spec.md 判断

## 无规格变化（仅缺陷恢复适用）

仅在 canonical 已准确规定目标行为时使用：

- 需求条目与 canonical stable ID；
- 实际行为违反 canonical 的证据；
- 行为、接口、错误、状态、阈值和兼容承诺均不变的逐项结论；
- `specs/spec.md` 全部语义保持不变的 preservation clause；
- 来自 Acceptance、QAS 或 Verification 的回归义务。

## MODIFIED 需求

任何可观察契约变化都使用标准 delta operation，完整填写 target、selector、base、
result、preservation、兼容/迁移和回归义务；不得写 N/A。

## delta-design.md 判断

设计不变时写有证据的 N/A，并保留：

- canonical design 章节或实体锚点；
- 结构、依赖、接口、错误模型、所有权和时序均不变的结论；
- 证明实现恢复到 canonical 契约的唯一 Case Index。

根因要求设计变化时使用标准 `DD-xxx` 与
`ADDED / MODIFIED / REMOVED / RENAMED` operation，完整表达方案、契约、风险、
回退和测试设计。

## tasks.md 缺陷分析

在标准 tasks 结构中增加：

- 环境：版本、平台和配置；
- 最小复现步骤及预期/实际；
- 日志、core、trace 或观测证据；
- 复现稳定性；
- 带证据的因果链、直接原因和根本原因；
- 现有测试缺口、波及范围及已排除假设；
- 最小安全修复范围、非范围和回退策略。

首个修复 Case 必须先稳定复现缺陷。任务仍按标准 RED→GREEN→REFACTOR 结构填写允许
文件、命令、完成定义和证据。

N/A 只表示 canonical 无变化，不豁免复现、R1/R2、TDD、R3、canonical sync 或收尾。
