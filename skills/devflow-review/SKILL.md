---
name: devflow-review
description: 在 DevFlow 的 R1、R2、R3 或 canonical sync 需要独立评审时使用；也用于复审已有 findings。评审者始终只读，以新上下文核对变更工件、canonical 基线、测试和代码，返回可落盘的 findings、Resolution 槽位与 verdict。
---

# DevFlow 评审

## 不变量

评审是阶段门禁，不是作者自检。始终遵守：

1. **作者不自审**：派发独立 `devflow-reviewer`，只提供磁盘工件、代码或 Git diff、rubric，不提供作者聊天历史。
2. **reviewer 只读**：不得编辑工件、代码、评审文件或 `change.json`。reviewer 返回完整记录，由主控 Agent 原样写入当前 change 的 `reviews/`。
3. **记录与状态分离**：findings、Resolution 和 verdict 保存在 `reviews/`；门禁状态只更新到 `change.json`；任务进度和 TDD 证据只保存在 `tasks.md`。
4. **没有落盘记录就没有评审**：聊天里的“通过”不能推进门禁。
5. **问题不能凭空消失**：返工后逐条回填原记录的 Resolution，复审再对照实际 diff 核验。

## 路径与输入预检

先确定组件根和唯一活动 change：

```text
<component-root>/specs/
  spec.md
  design.md
  changes/ARXXX-<topic>/
    change.json
    srs.md
    delta-spec.md
    delta-design.md
    tasks.md
    traceability.md
    reviews/
```

先读 `change.json`，从中取得 change 身份、`componentMode`、base revision、当前门禁和 artifact 路径。目录名、manifest 身份或磁盘工件不一致时阻塞并让主控 Agent 澄清，不自行选择另一个 change。

`componentMode: existing` 要求 `specs/spec.md` 与 `specs/design.md` 均为可用基线；缺失或仍为 draft 时阻塞并转 `devflow-init`。`componentMode: new` 允许 canonical 尚不存在，此时 R1/R2 要验证 delta 能从空基线生成首版 canonical。模式缺失、冲突或无法判断时向人追问。

## 四类门禁

| 门禁 | 被评审对象 | 必需上游 | Rubric | 核心问题 |
|---|---|---|---|---|
| R1 | `srs.md` + `delta-spec.md` | `change.json`、`specs/spec.md` 或空基线 | `references/spec-review-rubric.md` | 本次需求是否可测试，规格增量是否相对 canonical 正确且完整 |
| R2 | `delta-design.md` | 已通过 R1 的 SRS/规格增量、`specs/spec.md`、`specs/design.md` 或空基线 | `references/design-review-rubric.md` | 设计增量是否满足规格且不与 canonical 冲突 |
| R3 | 测试 + 实现 diff | SRS、两份 delta、canonical、`tasks.md`、`traceability.md` | test + code rubrics | 测试是否证明增量行为，实现是否符合批准的规格与设计 |
| canonical sync | canonical 前后版本及仅 canonical 的 Git diff | SRS、两份 delta、base revision、R1-R3 记录 | `references/sync-review-rubric.md` | delta 是否完整吸收、既有语义是否保留、是否冲突、spec-design 是否一致 |

R1/R2 遇到有理由的 `N/A` delta 仍要评审其“不需要 canonical 变化”的结论；`N/A` 不是跳过记录的理由。canonical sync 即使 Git diff 为空也必须复核 N/A 理由和 canonical 未被误改。

## 执行协议

### 1. 组装只读 Review Pack

主控 Agent 为 reviewer 提供：

- 门禁名称、change 根、`change.json` 中相关 base revision；
- 表中要求的完整工件，canonical 同时提供当前内容和可取得的 base 内容；
- R3 的实现/测试 diff、实际测试输出、主控 Agent 在隔离副本中产生的 mutation 证据和 `tasks.md` 证据；
- sync 的同步前 canonical、同步后 canonical、`git diff -- specs/spec.md specs/design.md` 输出；
- 对应 rubric；代码评审另加 `devflow-clean-code` 与适用语言/领域规则；
- 复审时提供上一轮记录及实际返工 diff。

不要只给摘要。缺少关键输入时 reviewer 返回 `BLOCKED` 和缺项，不猜测 verdict。

### 2. 派发独立 reviewer

使用 `devflow-reviewer` 的全新上下文。主控 Agent 不得把自己的判断包装成 reviewer 结论，也不得让 reviewer 直接修正文档或代码。

### 3. 产出可执行 finding

每条 finding 必须包含：

`位置 + 问题 + 为什么有风险 + 严重级 + 分类 + 建议返工阶段 + 可执行方向 + Resolution 槽位`

严重级：

| 严重级 | 含义 |
|---|---|
| `critical` | 会做错行为、破坏既有语义、产生不可验证结果或使归档不可审 |
| `important` | 交付前必须修复，但不构成立即错误 |
| `minor` | 不阻塞的局部改进 |

分类：

| 分类 | 处理 |
|---|---|
| `LLM-FIXABLE` | 信息充分，回作者阶段定向修复 |
| `USER-INPUT` | 缺业务事实、阈值、优先级或来源确认，只问最小问题 |
| `TEAM-EXPERT` | 需要架构、领域或团队规则裁决，封装成具体决策点 |

verdict 只能是：

- `通过`：无未闭环 critical/important；
- `需修改`：方向明确，可定向返工；
- `重新设计`：问题来自上游意图、边界或设计方向；
- `阻塞`：关键输入缺失、模式/基线冲突，无法形成可信评审。

### 4. 落盘与门禁更新

主控 Agent 将 reviewer 返回原样写到：

```text
specs/changes/ARXXX-<topic>/reviews/r1-review-YYYY-MM-DD.md
specs/changes/ARXXX-<topic>/reviews/r2-review-YYYY-MM-DD.md
specs/changes/ARXXX-<topic>/reviews/r3-review-YYYY-MM-DD.md
specs/changes/ARXXX-<topic>/reviews/canonical-sync-review-YYYY-MM-DD.md
```

同门禁复审在日期后加 `-r2`、`-r3`。随后主控 Agent 才更新 `change.json` 的记录路径与状态：失败为 `blocked/rework`；reviewer 通过后，attended 的 R1-R3 仍等人工确认，canonical sync 在任何运行模式下都等最终 canonical diff 人工确认，满足后才写 `passed`。

gate 通过时同步更新工件状态：

- R1 passed：`artifacts.srs.status` 与 `artifacts.deltaSpec.status` 写为 `accepted`；
- R2 passed：`artifacts.deltaDesign.status` 写为 `accepted`；
- R3 passed：确认 TDD 已把 `artifacts.tasks` 与 `artifacts.traceability` 写为 `complete`，评审者不替 TDD 伪造；
- canonical sync 经 reviewer 与人确认 passed：实际修改的 canonical artifact 写为 `baseline-ready`，未修改的 N/A canonical 保持原状态。

工件只有在对应最终记录存在、critical/important Resolution 闭环且所需人工确认完成后才能 accepted/passed。评审文件、artifact 状态与 gate 不一致时按未闭环处理。

### 5. Findings 闭环

作者侧按 finding 本质返工：

| 问题本质 | 返工阶段 |
|---|---|
| SRS、验收、规格 delta 或业务基线错误 | `devflow-specify` |
| 设计 delta、接口契约、错误模型或测试设计错误 | `devflow-design` |
| 测试、证据、实现或整洁代码问题 | `devflow-tdd` |
| canonical 合并结果与明确 delta 不一致 | `devflow-ship` 重新同步 |

每条 critical/important 的 Resolution 必须是以下之一：

- 修复摘要 + 代码/工件锚点 + 验证证据；
- 人明确接受不修 + 理由 + 确认人；
- 登记为债务 + 可定位去向（仅在不影响当前语义和门禁时允许）。

Resolution 有空项时不得复审为通过。复审必须核对 Resolution 与实际变更，并在新记录中引用上一轮。R3 的普通问题先回 `devflow-tdd`；canonical sync 问题由主控 Agent 修正 delta 或合并结果后重新派发 reviewer。

同一门禁最多自动返工复审 3 轮。第 3 轮仍有 critical/important，停止自动循环，向人呈现剩余问题、既有证据与最小决策点。

### 6. 人工确认

- `attended`：R1/R2/R3 通过后呈人确认，再由主控 Agent 更新 `change.json`；canonical sync 通过后仍不能归档，最终 canonical diff 必须单独获得人工确认。
- `unattended`：R1/R2/R3 不停顿，但独立评审、记录、critical 阻塞不减少；最终 canonical diff 与归档始终需要人工确认。

## Reviewer 抽查重点

- R1：逐个 delta 操作核对 target ID 和 canonical 旧语义；确认未把修改伪装成新增。
- R2：逐条核对 SRS → delta spec → delta design，确认测试 Case ID 双向覆盖。
- R3：为 2-3 个关键测试定义 mutation 并核验主控 Agent 提供的隔离执行证据；reviewer 不编辑工作树。优先读错误路径、资源路径和行为回归。
- sync：逐条建立 delta operation → canonical diff 映射，再反查每段 canonical diff 都有 delta 来源；对未涉及章节做语义保留抽查。

## 支撑参考

| 文件 | 用途 |
|---|---|
| `references/spec-review-rubric.md` | R1：SRS 与规格增量 |
| `references/design-review-rubric.md` | R2：设计增量 |
| `references/test-review-rubric.md` | R3：测试与证据 |
| `references/code-review-rubric.md` | R3：实现与代码质量 |
| `references/sync-review-rubric.md` | canonical sync 语义复核 |
