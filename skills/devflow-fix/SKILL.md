---
name: devflow-fix
description: 在处理缺陷、回归、线上问题或 DTS/hotfix 时使用：在 specs/changes/ARXXX-<topic>/ 中记录复现、根因、最小修复边界和 TDD 证据；判断 canonical 行为/设计是否需要 delta，并继续经过独立评审与 ship。不可用于无复现的盲修或范围外重构。
---

# DevFlow 缺陷修复

## 核心纪律

> **先复现，再归因，后修复；没有先失败的复现测试就没有修复。**

缺陷不是旁路目录，也不产生单独的缺陷说明文件。它使用同一 change 契约：

```text
<component-root>/specs/changes/ARXXX-<topic>/
  change.json
  srs.md
  delta-spec.md
  delta-design.md
  tasks.md
  traceability.md
  reviews/
  closeout.md
```

DTS/事故/缺陷单是 `srs.md` 的来源锚点；change 身份仍来自 `change.json` 和 `ARXXX-<topic>`。缺 AR 标识、topic 或 `componentMode` 时向人追问，不自造身份。

状态只写 `change.json`；任务进度和 RED/GREEN/REFACTOR 证据只写 `tasks.md`。

## 0. 建立或恢复 change

先解析组件根和活动 change，再读取 `change.json`、`srs.md`、两份 delta、`tasks.md`、`traceability.md` 和已有 reviews。

- `componentMode: existing`：`specs/spec.md` 与 `specs/design.md` 必须都存在且为 `baseline-ready`；否则阻塞并转 `devflow-init`。
- `componentMode: new`：缺陷语义通常与“尚无基线”冲突；除非人能说明这是首版开发中的缺陷，否则先澄清，不自行改模式。
- mode 缺失、与代码现状冲突或无法判断：向人提问。

新建 defect change 时在 `change.json` 记录基于实际风险选择的 standard/elevated/critical profile、运行模式、不可变 base revision、artifact 图和 gate 初始状态；DTS/事故来源写入 SRS，需要结构化扩展时放在 `extensions`，不要把这些状态复制进 `tasks.md`。

## 1. 复现并写入 SRS

`srs.md` 只记录需求事实：

- 当前问题、目标结果、缺陷来源和整体成功标准；
- 范围与非范围；
- `FR/IFR/NFR/CON` 中适用的目标行为、验收或度量及 Source。

不在 SRS 中复制 change 状态、canonical/delta 定位，也不写环境、复现过程、根因、
修复边界或回退方案；这些属于 `tasks.md` 的缺陷分析与执行证据。

**复现不了就不改代码。** flaky 问题先通过压力、故障注入、受控时钟或缩小输入提高
复现率。仍不可复现时，把已排除假设和证据写入 `tasks.md` 的缺陷分析区，向报告人
索取最小缺失信息；不提交猜测补丁。

## 2. 根因分析

从现象沿真实执行路径建立证据链，直到回答“为什么发生”：

1. **直接原因**：哪段代码、配置或状态导致现象；
2. **根本原因**：为什么契约、设计、实现或测试允许它出现；
3. **波及范围**：同一模式还影响哪些路径；
4. **测试缺口**：现有测试为什么没拦住；
5. **排除假设**：每项附排除证据。

两次无证据的“改一下试试”仍未命中时立即停止，回到观测和因果链。

根因、复现和排除证据写进 `tasks.md` 的缺陷分析区，并在 `traceability.md` 建立
DTS/SRS → canonical/delta → Case/Task → Code/Test → Evidence 链路。根因若证明
需求或设计必须变化，再更新对应 delta；不回写 SRS 过程分析。

## 3. 判断 delta

不要把“修 bug”自动等同于“无规格变化”。分别判断可观察行为和设计：

| 判断 | `delta-spec.md` | `delta-design.md` | 动作 |
|---|---|---|---|
| canonical 行为正确，纯实现偏离；canonical 设计也正确 | 明确 `N/A` + stable ID + 证据 | 明确 `N/A` + design 锚点 + 证据 | 实现恢复基线 |
| 行为基线正确，但设计需修订 | `N/A` + 证据 | 写稳定 ID 操作 | 先完成设计增量 |
| 预期行为、错误语义、阈值、状态机或兼容承诺要变 | 写稳定 ID 操作 | 按规格增量写操作 | 走完整 specify/design |
| 无法确认 canonical 是否正确 | 不写猜测 N/A | 不写猜测 N/A | 向业务/专家澄清 |

N/A 必须说明：

- 对应 canonical stable ID 和原文语义；
- 缺陷实际行为如何违反它；
- 为什么修复后接口、错误语义、时序、状态机、阈值、兼容和设计结构都不变；
- 复现/回归测试将如何证明恢复基线。

`delta-design.md` 即使没有 canonical design operation，也必须保留唯一 Case Index，
让复现/回归 Case 能驱动 `tasks.md` 和 R3。

两份 delta 使用 `ADDED / MODIFIED / REMOVED / RENAMED`。N/A 只代表不改对应 canonical，不代表省略 R1/R2 验证、R3、canonical sync review 或 ship。

## 4. 界定最小安全修复

在 `tasks.md` 的缺陷分析区写明：

- 允许修改的文件/函数；
- 显式不修的邻近异味和同类风险；
- 回退策略；
- 依赖和环境风险；
- 同类问题的独立登记去向。

若修复范围扩大到新行为、接口变化或架构边界，停止当前实现，先更新 delta 并重新经过受影响评审。不得用重命名、格式化或“顺手清理”掩盖修复 diff。

## 5. 先完成 R1 与 R2

进入实现前必须按顺序闭合：

1. 写完 defect SRS 与 `delta-spec.md`（真实 operation 或有证据的 N/A），更新
   traceability，进入独立 R1；
2. R1 最终通过且所需人工确认完成后，把 SRS/delta-spec artifacts 标为 accepted；
3. 需要设计变化时进入 `devflow-design` 形成标准 `delta-design.md`；设计不变时按
   `references/fix-template.md` 写符合标准结构的 N/A；
4. 对 `delta-design.md` 执行独立 R2；R2 最终通过且所需人工确认完成后，把
   delta-design artifact 标为 accepted；
5. 只有 `gates.r1`、`gates.r2` 均 passed 且三个输入 artifacts 均 accepted，才进入
   `devflow-tdd`。

不能以“先写复现测试更快”为由在 R1/R2 前进入 build。调查和只读复现可以用于完善
SRS；会写测试或实现的 TDD 从门禁通过后开始。

## 6. 在 tasks.md 执行 TDD

把复现转成稳定 Case ID 和自包含任务：

1. **RED**：先写自动化复现测试，运行并确认因该缺陷失败；
2. **GREEN**：做最小修复，当前测试与完整套件全绿；
3. **REFACTOR**：只在全绿上按 `devflow-clean-code` 清理本任务引入的异味；无改动时写 N/A 理由；
4. 记录真实命令、关键输出、代码锚点，更新 traceability。

行为本来已存在导致复现测试一写就绿，说明测试没有复现缺陷、环境不对或报告已失效；先调查，不通过弱化断言制造 RED。

## 7. R3 与收尾

- R3 必须同时评审测试与代码，核对复现 RED、回归、范围和错误/资源路径。
- 所有 findings 的 Resolution 闭环后进入 `devflow-ship`。
- Ship 仍执行完整 DoD、canonical sync review、人工确认、closeout 和 archive。两份 delta N/A 时 canonical diff 应为空，但 sync review 不能省略。

## 风险信号

- 没有复现记录或 RED 就出现实现 diff；
- 根因只写“空指针”“越界”等发生位置，没有为什么；
- DTS 直接当作 change 目录身份，或缺 AR 身份时自行编号；
- 仅凭“只是 bug”把 delta 写成 N/A；
- 修复 diff 混入重构、格式化、依赖升级或邻近问题；
- 用重试、sleep、放宽阈值或弱断言让现象消失；
- N/A 后跳过 R3、sync review 或 ship；
- 把 gate 状态写进 `tasks.md`，造成双重状态来源。

## 自检

- [ ] SRS 只包含缺陷问题、目标、来源、范围和目标需求
- [ ] 环境、稳定复现、直接/根本原因、波及范围、测试缺口和排除证据已写入 tasks.md 缺陷分析区
- [ ] canonical 行为/设计是否变化已分别判断，delta 或 N/A 都有证据
- [ ] 最小修复范围、非范围、回退和同类风险去向明确
- [ ] `tasks.md` 有先失败后通过的复现测试与完整套件证据
- [ ] traceability 从 DTS/SRS 到代码和证据闭合
- [ ] R1/R2 的 delta/N/A 判断、R3 和 ship 均未省略

## 支撑参考

| 文件 | 用途 |
|---|---|
| `references/fix-template.md` | 缺陷 change 的 SRS、delta、tasks 写法 |
