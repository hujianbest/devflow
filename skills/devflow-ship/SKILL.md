---
name: devflow-ship
description: 在 DevFlow change 的实现、R1-R3 和追溯均闭环后收尾时使用：执行硬性 DoD、由主控 Agent 将 delta 智能同步到 canonical spec/design、展示 Git diff、派只读 reviewer 复核、取得人工确认、写 closeout 并归档整个 change。任何缺口都会阻塞。
---

# DevFlow 收尾（Ship）

## 目标与边界

Ship 只完成三件事：

1. 证明 change 已满足 Definition of Done；
2. 把已批准的规格与设计增量合并进组件当前真相；
3. 在独立复核和人工确认后写收尾记录并移动到 archive。

主控 Agent 执行同步和归档；`devflow-reviewer` 始终只读；`devflow-implementer` 不参与同步、门禁或归档。Ship 不补实现、不补测试，也不替上游改写业务意图。发现缺口就回责任阶段，闭环后重新进入。

固定路径：

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
    closeout.md
  archive/YYYY-MM-DD-ARXXX-<topic>/
```

## 硬性原则

- 状态只读写 `change.json`；任务、RED/GREEN/REFACTOR 进度与证据只读写 `tasks.md`。
- 主控 Agent 直接理解 SRS、delta 和 canonical 后做语义合并，不创建或依赖 `devflow_delivery.py`、候选 hash、专用事务文件或组件仓库运行时脚本。
- 未涉及的 canonical 内容必须保留；删除只来自明确 `REMOVED` 操作。
- base revision 后存在并行变化、target 不唯一或语义有歧义时，先向人追问，不猜测覆盖。
- canonical sync 独立复核不能省略；delta 为 N/A 或 Git diff 为空也一样。
- 任一未完成任务、未闭环 R1/R2/R3、空 Resolution、追溯断链、DoD 缺口或 sync 复核未通过都硬阻塞。
- 不允许把缺口降为警告后继续，不允许带未完成项归档。
- 不使用 `git reset --hard`、`git checkout --` 等破坏性恢复。依靠普通文件编辑、Git diff 和 Git 历史定位与修正。

## 工作流

详细文件操作遵循 `references/sync-archive-protocol.md`。

### 1. 定位并验证 change

先读 `<component-root>/specs/changes/ARXXX-<topic>/change.json`：

- manifest 身份必须与目录名一致；
- `componentMode` 必须是 `new` 或 `existing`；
- artifact 图必须指向同一 change 目录；
- base revision、R1/R2/R3 状态、运行模式和 archive 状态可读；
- source 已在 `specs/changes/`，目标尚未存在于 `specs/archive/`。

existing 组件要求 `specs/spec.md`、`specs/design.md` 同时存在且为 `baseline-ready`。new 组件允许同步前 canonical 缺失，但两份 delta 必须可从空基线创建首版。模式缺失、冲突或无法判断时阻塞并向人追问。

### 2. Pre-sync DoD

逐项执行 `references/definition-of-done.md`，先核验同步前可闭环的项目：

- `tasks.md` 全部任务 done，证据真实；
- R1/R2/R3 记录存在，最终 verdict 通过，门禁状态与记录一致；
- 所有 critical/important findings 都有有效 Resolution；
- `traceability.md` 从 SRS 到证据全链路闭合；
- 最终测试、构建、静态分析和 Quality Stack 证据可核；
- SRS、delta、实现之间无漂移。

任何缺口都回责任阶段，不在 Ship 内补叙述或修改代码。

### 3. 并行变化与歧义预检

读取不可变 `change.json.baseRevision`、两份 delta 的 `canonicalBase` 元数据，并比较该仓库快照与当前 canonical：

- 当前 canonical 与 base 相同：可以继续；
- base 后有任何并行变化：展示变化及其与 delta 的关系，向人询问如何保留、调整 delta 或明确合并；得到明确答复前不编辑 canonical；
- 规格稳定 ID 或组件设计章节/实体键缺失、重复，操作目标不唯一，或 delta 与当前语义冲突：列出最小歧义问题并停止；
- 工作树已有无法归属的 canonical 修改：视为并行变化，不覆盖。

人确认处理方式后，把决定写入 canonical sync gate evidence；若决定改变 delta 语义，重开受影响的 R1/R2/R3。`change.json.baseRevision` 始终保持不变，再从该 revision 重新执行预检。

### 4. OPSX 风格智能同步

主控 Agent 一次性读取：

- `srs.md`
- `delta-spec.md`
- `delta-design.md`
- 同步前 `specs/spec.md`
- 同步前 `specs/design.md`
- `change.json` 的 component mode 和 base revision

按规格稳定 ID、组件设计章节/实体键和
`ADDED / MODIFIED / REMOVED / RENAMED` 操作直接编辑 canonical：

- `ADDED`：插入符合 canonical 现有结构的完整新语义；
- `MODIFIED`：只替换目标 ID 指定语义，保留未提及字段和邻近内容；
- `REMOVED`：只删除明确目标，并修正经 delta 批准的引用；
- `RENAMED`：规格 ID、功能编号等稳定业务键保持不变；组件接口/软件单元改名时使用
  章节路径、base 摘要和 from/to 定位，只更新名称与明确受影响的引用；正文语义变化必须
  由单独的 `MODIFIED` 表达。

new 组件从空基线生成首版完整 `specs/spec.md` 和 `specs/design.md`。N/A delta 不产生对应 canonical 变化。合并不是拼接 delta，也不是重写整份文档；canonical 应继续作为可独立冷读的当前真相。

只要某份 canonical 有正文变化，就同时把该文档的 `baselineStatus` 置为 `draft`、
`baselineRevision` 写为不可变的 `change.json.baseRevision`、`baselineChange`
写为当前 `ARXXX-<topic>`、`provenanceMethod` 置为 `canonical-sync`，并把
`independentReview` 与 `humanConfirmation` 重置为 pending；在 provenance index
和 revision log 记录本 change。这里的 revision 是 delta 基准，配合 archive 中的
change 重放当前正文，不声称包含同步后的文件。delta 为 N/A 的未修改文档保持原
metadata。new 组件创建的两份文档也先是 draft，不能在 sync review 和人工确认前写
baseline-ready。

### 5. 展示 canonical Git diff

同步后先验证 Git diff 只包含预期的 canonical 变化，再向人展示：

```text
git diff -- specs/spec.md specs/design.md
```

逐个 diff hunk 标注来源 delta operation。发现无 delta 来源的改动、意外大范围重排、误删或占位符时，先修正再评审。

### 6. 派发 canonical sync 复核

派独立、只读的 `devflow-reviewer`，输入同步前/后的两份 canonical、canonical-only Git diff、SRS、两份 delta、base revision 和 R1-R3 记录，使用 `devflow-review/references/sync-review-rubric.md` 检查：

1. delta 是否完整吸收；
2. 未涉及的既有语义是否被误删或改写；
3. 是否产生冲突、重复或无来源变化；
4. canonical spec 与 design 是否一致。

主控 Agent 将返回记录写入同一 change 的 `reviews/canonical-sync-review-YYYY-MM-DD[-rN].md`，并追加到 `change.json.gates.canonicalSync.reviewRecords`。未通过时把 gate 置为 `rework`，由责任阶段修正 delta，或由 Ship 修正明确的合并错误，然后重新展示 diff 并派新的独立复核。reviewer 通过后，把实际修改的 canonical 文档 `independentReview` 记录为 passed，但文档仍保持 draft、gate 仍等待最终人工确认，不能提前标为 `passed`。reviewer 不直接修改任何文件。

### 7. Final DoD 与人工确认

sync 复核通过后执行 Definition of Done 的全部可判定项，确保任务、R1-R3、Resolution、traceability、测试证据、canonical diff 和 sync 记录全部闭环；此时只允许人工确认、closeout 写入和目录移动这些有顺序依赖的项目尚待完成。

向人展示：

- canonical-only Git diff；
- R1/R2/R3 与 sync 最终记录；
- DoD 结果和未遗留的阻塞项；
- 明确的债务清单及去向；
- 将要使用的 archive 目标路径。

无论运行模式为何，都必须取得人对 canonical diff 和归档的明确确认。拒绝、含糊回复或仅确认部分内容都不能继续。

### 8. 写 closeout 并归档

确认后，把实际修改的 canonical 文档 `humanConfirmation` 写为 confirmed，并在独立评审、blocking unknown 和 spec-design 一致性仍满足时恢复 `baselineStatus: baseline-ready`；同时把对应的 `change.json.artifacts.canonicalSpec` / `canonicalDesign` 状态写为 `baseline-ready`。未修改的 N/A 文档不重写 metadata，manifest 保持其已核验状态。

随后把 `gates.canonicalSync` 的人工确认与状态写为 confirmed/passed。保持 `gates.closeout.status: pending`，按 `references/closeout-template.md` 写 change 根下 `closeout.md`，记录刚才由人确认的 diff、DoD、review、债务和 archive 目标。写入后重新读取并逐项核对：

- 写入失败、占位符残留或与已确认内容不一致：`gates.closeout.status: blocked`，不移动目录；
- 内容写实且完整：`artifacts.closeout.status: complete`，
  `gates.closeout.status: passed`，`humanConfirmation: confirmed`，evidence 指向该
  closeout、四类已通过 review 和刚才的最终人工确认；`reviewRecords` 保持空数组，
  因为 closeout 本身不是第五类独立评审。

closeout gate 通过后，才把 archive 目标和 `status: ready` 写入 `change.json`；此时不得提前写成 `archived`。

先检查目标：

```text
specs/archive/YYYY-MM-DD-ARXXX-<topic>/
```

目标已存在或命名无法唯一确定时阻塞，不覆盖、不合并目录。目标可用时，以标准文件系统移动/重命名操作把整个 `specs/changes/ARXXX-<topic>/` 原样移动过去；不要复制后遗留活动目录。移动成功后，在 archive 内的 `change.json` 写入 `archive.status: archived`、确认人和归档时间，并回填归档后 `closeout.md` 的 archive 结果。

移动后验证：

- 活动源目录不存在；
- archive 目录包含 manifest、SRS、两份 delta、tasks、traceability、全部 reviews 和 closeout；
- `change.json` 的 archive 路径与实际一致；
- canonical 文件仍位于 `specs/` 根。

最后展示完整 Git diff，运行项目正常 CI/验证流程。归档移动失败时保留现场、检查 Git diff 后用普通文件操作修复；不得破坏性重置。

## 缺口路由

| 缺口 | 返回 |
|---|---|
| SRS、delta-spec、R1 或业务事实 | `devflow-specify` |
| delta-design、测试设计、R2 | `devflow-design` |
| 任务、测试、实现、证据、R3 | `devflow-tdd` |
| review 记录缺失或 Resolution 未核验 | `devflow-review` / 对应作者阶段 |
| 明确的 canonical 合并错误 | 本技能重新同步并复核 |
| base 后并行变化、歧义、目标冲突 | 向人追问 |

## 风险信号

- 只看 delta 摘要，不读 canonical 全文；
- 用全文替换造成未涉及内容消失；
- base 后已有变化却直接选一边覆盖；
- canonical diff 未展示，或 sync reviewer 不是独立只读上下文；
- sync verdict 未通过仍写 closeout；
- 用 N/A、空 diff、紧急或 unattended 作为省略 sync 的理由；
- archive 目标已存在仍覆盖或合并；
- 复制后保留活动 change，形成两个“当前状态”；
- 文件操作失败后使用破坏性 Git 命令清场。

## 支撑参考

| 文件 | 用途 |
|---|---|
| `references/definition-of-done.md` | 关闭前硬门禁 |
| `references/sync-archive-protocol.md` | 智能同步、复核与标准移动协议 |
| `references/closeout-template.md` | closeout 记录模板 |
