# Canonical Sync 与 Archive Protocol

> 配套 `devflow-ship`。主控 Agent 按本协议把 change delta 合入 `specs/spec.md` 与 `specs/design.md`，经独立只读复核和人工确认后，将整个 change 目录移动到 `specs/archive/`。

## 1. 输入与角色

主控 Agent 必须读取：

- `specs/changes/ARXXX-<topic>/change.json`
- `srs.md`
- `delta-spec.md`
- `delta-design.md`
- `tasks.md`
- `traceability.md`
- `reviews/` 中 R1/R2/R3 最终记录
- `specs/spec.md` 与 `specs/design.md`（new 组件可在同步前不存在）

职责边界：

- 主控 Agent：检查门禁、解释 delta、编辑 canonical、展示 diff、写 closeout、移动目录；
- reviewer：只读验证同步结果，返回 review 记录；
- implementer：不参与同步和归档；
- 人：裁决歧义/并行变化并最终确认 canonical diff 与 archive。

## 2. Hard-stop Preflight

以下任一成立立即停止：

- `componentMode` 缺失、与仓库现状冲突或无法判断；
- existing 组件的 canonical 缺失或不是 `baseline-ready`；
- new 组件的 delta 不能从空基线生成首版；
- tasks 未全部 done，或 RED/GREEN/REFACTOR 证据缺失；
- R1/R2/R3 任一无最终通过记录，manifest gate 与记录不一致；
- 任一 critical/important finding 的 Resolution 为空或不可核；
- traceability 断链；
- base revision 无法解析；
- archive 目标已存在。

不能把 hard stop 改写为 warning、debt 或 closeout 注释后继续。

## 3. Base Revision 与并行变化

核对不可变 `change.json.baseRevision`，并结合两份 delta 各自的 `canonicalBase` 元数据：

1. 取得 delta 编写时对应的 canonical 内容；
2. 比较当前 canonical 和 base；
3. 当前内容相同则继续；
4. 当前内容不同则生成并展示 base→current 差异，标明与 delta target ID 的关系；
5. 向人提出最小选择题：保留当前变化并给出明确合并决策，或先调整 delta 并重开受影响门禁；
6. 把结论写入 `gates.canonicalSync.evidence` 后，从原 `baseRevision` 重新执行 preflight；该字段不可改写。

即使并行变化看似与 delta 无关，也先询问；主控 Agent 不替其所有者确认语义。已有未归属的 canonical 工作树修改按并行变化处理。

## 4. 语义合并算法

分别对 spec 和 design 执行：

1. 为规格建立稳定 ID 索引；为组件设计建立章节路径、功能编号、接口/软件单元实体键与 base 摘要索引；
2. 规格 operation 固定按 `RENAMED → REMOVED → MODIFIED → ADDED` 读取；设计
   operation 按已评审的显式依赖顺序读取；
3. 验证 operation 的 source requirement、target ID、旧语义和预期新语义；
4. 应用 operation；
5. 更新被明确影响的交叉引用；
6. 对未命中的 ID 和章节做保留检查；
7. 完成后反查所有 canonical 变化都有 delta 来源。

同一规格 ID 出现在互斥分区，或多个 operation 覆盖同一局部且没有明确顺序时，视为
冲突并停止同步。

有正文变化的 canonical 同时进入待确认状态：

- `baselineStatus: draft`
- `baselineRevision: <change.json.baseRevision>`
- `baselineChange: <ARXXX-topic>`
- `provenanceMethod: canonical-sync`
- `independentReview.status: pending`
- `humanConfirmation.status: pending`
- provenance index / revision log 追加当前 change

N/A 且正文未变化的 canonical 不重写 metadata。new 组件的首版 canonical 也先保持
draft。`baselineRevision` 是 delta 基准，必须与 `baselineChange` 和 provenance
index 一起解释，不声称包含同步后的 canonical 文件。

操作语义：

| Operation | 合并规则 | 阻塞条件 |
|---|---|---|
| `ADDED` | 按 canonical 现有组织插入完整内容；规格使用稳定 ID，组件设计使用原模板章节/实体结构 | ID/实体键已存在、位置/归属不唯一 |
| `MODIFIED` | 只改变 delta 明确列出的语义；未列字段保留 | 旧语义不匹配、目标重复、局部与整体矛盾 |
| `REMOVED` | 删除明确目标和经批准的引用；保留其他内容 | 消费者/删除后语义/兼容处理不清 |
| `RENAMED` | 规格 ID、功能编号等稳定业务键不变；设计实体用章节路径、base 摘要和 from/to 定位，只改名称与明确引用 | from/to、base 或引用范围不清、同时改语义却无 `MODIFIED` |

`N/A` 表示对应 canonical 不应变化。若另一份 delta 仍有变化，仅同步另一份；两份均 N/A 时保持两份 canonical 不变，但继续执行 diff、sync review、DoD 和归档。

## 5. Diff 卫生

同步后生成 canonical-only Git diff：

```text
git diff -- specs/spec.md specs/design.md
```

主控 Agent 在派 reviewer 前自检：

- 每个 hunk 标有 delta operation 来源；
- 无 delta 来源的 hunk 为零；
- 未发生全文格式化、章节大搬移或无关术语统一；
- `REMOVED` 之外无既有语义消失；
- 没有 TODO、冲突标记、评审应答或临时说明；
- new 组件的两份首版 canonical 都能独立冷读。

自检失败时先用普通编辑修正并重新生成 diff。

## 6. 独立 Sync Review

派 `devflow-reviewer`，提供：

- 同步前和同步后的 canonical 全文；
- canonical-only Git diff；
- SRS、两份 delta、base revision；
- `change.json` 身份与 R1-R3 最终记录；
- `devflow-review/references/sync-review-rubric.md`。

reviewer 返回的内容由主控 Agent 原样落到：

```text
reviews/canonical-sync-review-YYYY-MM-DD[-rN].md
```

主控 Agent 把记录路径追加到 `gates.canonicalSync.reviewRecords`。verdict 不通过时把 gate 置为 `rework`：

- delta 意图缺失/错误 → 回 `devflow-specify` 或 `devflow-design`，受影响门禁重走；
- 合并实现偏离明确 delta → 主控 Agent 修正 canonical；
- 每轮修正后重新展示 diff、重新派独立 reviewer；
- 不在原 review 记录中覆盖 verdict。

verdict 通过后，主控 Agent 把实际修改的 canonical 文档
`independentReview` metadata 更新为 passed 并记录 review 路径；文档仍保持 draft。
在最终人工确认前，`canonicalSync.status` 仍不能是 `passed`。

## 7. 人工确认与 Closeout

最终 sync review 通过、DoD 中除人工确认/closeout/archive 这些顺序依赖项外均通过后，向人展示：

- canonical-only Git diff；
- 四个最终 review 记录；
- DoD 结果；
- 债务及明确去向；
- archive 目标。

仅“确认”“同意按所示 diff 归档”等明确答复有效。取得确认后：

1. 把实际修改的 canonical 文档 `humanConfirmation` 更新为 confirmed；独立评审、
   blocking unknown 和 spec-design 一致性仍满足时，写
   `baselineStatus: baseline-ready`，并把对应 `change.json.artifacts` canonical
   节点写为 `baseline-ready`；
2. 把 `gates.canonicalSync.humanConfirmation` 与 status 写为
   `confirmed` / `passed`；
3. 保持 `gates.closeout.status: pending`，按 closeout template 写
   `closeout.md`；
4. 重新读取 closeout：写入失败、占位符残留或与已确认内容不一致时把 closeout
   gate 置 blocked；写实完整时把 `artifacts.closeout.status` 置 complete，
   `gates.closeout.status` 置 passed、`humanConfirmation` 置 confirmed，并将
   evidence 指向 closeout、四类已通过 review 与最终人工确认；closeout 的
   `reviewRecords` 保持空数组，因为它不是独立评审 gate；
5. 在 `change.json.archive` 写目标并置 `status: ready`，记录确认人；
6. 再次确认目标不存在。

## 8. 标准目录移动

目标格式：

```text
specs/archive/YYYY-MM-DD-ARXXX-<topic>/
```

日期使用实际归档日；名称保留源 change 的 `ARXXX-<topic>` 原样。使用运行环境提供的普通文件系统 move/rename 操作移动整个目录：

```text
specs/changes/ARXXX-<topic>/
  → specs/archive/YYYY-MM-DD-ARXXX-<topic>/
```

不要覆盖、合并、拆分、只复制部分文件或留下源目录。运行环境无读取、编辑或移动能力时流程阻塞，不能只在聊天中宣称完成。移动成功后，在 archive 内的 manifest 写 `archive.status: archived`、`archivedAt` 和确认人，并回填归档后 `closeout.md` 的 archive 结果；移动前不得伪造这些状态。

## 9. 移动后验证

- [ ] 源 change 目录已不存在
- [ ] archive 目标只存在一份
- [ ] `change.json`、SRS、两份 delta、tasks、traceability、reviews、closeout 全部在目标中
- [ ] `change.json` 记录路径与实际目标一致
- [ ] `specs/spec.md` 与 `specs/design.md` 留在 canonical 位置
- [ ] 完整 Git diff 能清楚显示 canonical 修改和目录移动
- [ ] 正常 CI/验证可运行

失败时先检查实际文件状态和 Git diff，使用普通文件操作完成或回退局部动作；不得使用破坏性 reset 清理现场。
