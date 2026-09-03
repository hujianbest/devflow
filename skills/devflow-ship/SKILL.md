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

## 输入与权威协议

先加载 `using-devflow` 技能并核对目标 change。随后完整读取并按顺序执行：

1. `references/definition-of-done.md`
2. `references/sync-archive-protocol.md`
3. `references/closeout-template.md`

上述 reference 是同步、复核、状态转换和目录移动的唯一操作定义。本技能只负责进入条件、角色边界和缺口路由。

## 进入条件

- `change.json` 与实际工件一致，组件模式和不可变 `baseRevision` 可核；
- tasks、R1/R2/R3、Resolution、traceability 和要求的验证证据均已闭环；
- existing 组件的 canonical baseline 可用；new 组件的两份 delta 可从空基线生成首版 canonical；
- archive 目标尚不存在。

任一条件不满足都返回责任阶段，不在 Ship 中补实现、补测试或改写业务意图。

## 执行不变量

- 主控 Agent 读取完整 SRS、delta 和 canonical 后执行语义同步；未涉及内容保持不变。
- 写 `closeout.md` 或把 delta 文字并入 canonical 之前加载 `writing-readable-doc`：canonical 是长期真相，最终 diff 还要人逐段确认。合并时统一术语与抽象层级，但不得把语义合并和表达调整混进同一批 diff。
- base 后存在并行变化、目标不唯一或语义有歧义时阻塞并询问。
- canonical-only diff 必须经过独立只读 reviewer；N/A 或空 diff 不豁免。
- 人确认最终 diff 和归档前，canonical sync 不得通过。
- `closeout.md` 写实且 closeout gate 通过后，才把整个 change 移到
  `specs/archive/YYYY-MM-DD-ARXXX-<topic>/`。
- 失败现场保持可检查；禁止破坏性 Git 恢复。

## 完成结果

完成时必须同时成立：

- `specs/spec.md` 与 `specs/design.md` 表达当前组件真相；
- canonical sync review、人工确认和 `closeout.md` 均可核；
- change 完整位于 archive，活动目录不存在；
- archive 内 `change.json`、closeout 状态与实际路径一致；
- 完整 Git diff 已展示并进入项目验证流程。

完成 Ship 后，如果 archive 中存在可能改变未来调查、设计或工程选择的非平凡经验，
执行一次有上限的只读候选判断：无合格候选时不增加提示；attended 有候选时向用户提供
一次可选的 `devflow-learn capture` 建议；unattended 只在最终结果中输出
`report-only` 候选，不自动写入。只有用户接受或显式调用时才进入知识沉淀。捕获失败、
被跳过或没有合格候选都不影响已经完成的 Ship，也不得回写 archive 或 change gate。

## 缺口路由

| 缺口 | 返回 |
|---|---|
| SRS、delta-spec、R1 或业务事实 | `devflow-specify` |
| delta-design、测试设计、R2 | `devflow-design` |
| 任务、测试、实现、证据、R3 | `devflow-tdd` |
| review 记录缺失或 Resolution 未核验 | `devflow-review` / 对应作者阶段 |
| 明确的 canonical 合并错误 | 本技能重新同步并复核 |
| base 后并行变化、歧义、目标冲突 | 向人追问 |

## 支撑参考

| 文件 | 用途 |
|---|---|
| `references/definition-of-done.md` | 关闭前硬门禁 |
| `references/sync-archive-protocol.md` | 智能同步、复核与标准移动协议 |
| `references/closeout-template.md` | closeout 记录模板 |
