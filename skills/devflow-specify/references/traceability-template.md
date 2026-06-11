# traceability.md 模板

使用说明：`devflow-specify` 初始化 `features/<id>-<slug>/traceability.md`，此后各阶段**只追加自己负责的列**：specify 填需求与上游锚点，design 填设计章节与测试设计用例，tdd 填任务/代码/测试/证据。它是 spec-design-code 一致性的显式约束：任何一列对不上，说明工件之间已经漂移。`devflow-review` 抽查它，`devflow-ship` 关闭前终验它。

```markdown
# <Work Item ID> 追溯矩阵

- 工作项类型: AR / DTS / CHANGE
- 工作项 ID:
- 所属组件:

## 追溯行

| 需求条目 | Change Type | 上游锚点 | 组件设计章节 | 设计章节 | 测试设计用例 | 任务 | 代码文件/函数 | 测试代码 | 验证证据 |
|---|---|---|---|---|---|---|---|---|---|
| FR-001 | modify | SR-1234 §3.2 | §6.2.1 | §4.2 / §7.1 | TC-001, TC-002 | T1 | src/mode.c:mode_set | test/mode_test.cpp | tasks.md#T1 |
|  |  |  |  |  |  |  |  |  |  |

## 备注

- 某列不适用时标 `N/A` 并简述理由（如纯内部修改无组件设计章节）。
- `modify` / `remove` 行必须能从基线追溯到回归 / 删除语义的验证证据。
- 测试设计用例必须能在 design.md 测试设计章节找到对应条目，形成双向锚点。
- 跨组件工作项在每个受影响组件仓库内分别维护，本文件只覆盖当前组件视角。
```
