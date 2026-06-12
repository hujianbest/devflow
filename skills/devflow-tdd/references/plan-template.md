# plan.md 模板

使用说明：

- `plan.md` 是工作项的**执行计划与中断恢复的单一入口**：任何新会话（上下文完全丢失）只读 spec.md → design.md → plan.md 三个文件，就能从断点继续执行，不需要任何聊天记忆。这决定了它的写法标准：**每个任务自包含**——组件根、工件根、精确文件路径、测试用例锚点、验证命令、完成判据、REFACTOR 检视标准全部内联，不写「同上」「见聊天记录」。
- 生命周期：`devflow-specify` 在工作流启动时建骨架（组件根 + 工件根 + 运行模式 + 门禁表 + 边界）；`devflow-design` 评审通过后由 `devflow-tdd` 细化任务拆解；TDD 执行期逐任务更新状态与证据行；各 R 评审节点更新门禁表。门禁表也是 todo / 计划投影的来源：存在 `pending` / `rework` 门禁时，下一条执行待办就是该门禁，而不是后续阶段。
- plan 是 design 测试设计的**执行索引层**，不是测试设计本身：不得新增 design.md 中没有的用例或业务事实；发现缺用例 → 回 `devflow-design`。

````markdown
# <Work Item ID> 执行计划

## 运行模式与门禁状态

- 运行模式: attended / unattended（工作流启动时向用户确认一次，此后沿用）
- 组件根: `<absolute-or-repo-relative-component-root>`
- 工件根: `<component-root>/features/<id>-<slug>`（或 `AGENTS.md` 覆盖后的等价路径）
- 长期文档根: `<component-root>/docs`（或 `AGENTS.md` 覆盖后的等价路径）
- 来源工件: spec.md@<commit> / design.md@<commit>

| 门禁 | 状态 | 评审记录 | 人工确认（attended） |
|---|---|---|---|
| R1 spec 评审 | pending / passed / rework | reviews/spec-review-<日期>.md | yes / no / N/A(unattended) |
| R2 design 评审 | pending / passed / rework | reviews/design-review-<日期>.md | … |
| R3 test+code 评审 | pending / passed / rework | reviews/test-review-…、code-review-… | … |
| ship DoD | pending / passed | closeout.md | … |

## 恢复指引（保留此节原文）

上下文丢失后从本文件恢复：

1. 先读取本文件头部的组件根、工件根、长期文档根，后续所有相对路径都以这些根解析；
2. 读 spec.md、design.md（必要时 component-design-draft.md）取得契约与测试设计；
3. 看上方门禁表确定所处阶段：有 pending/rework 门禁 → 先去该门禁；例如 spec 已写完但 R1 pending 时，下一步是 `devflow-review`，不是人工确认或 `devflow-design`；
4. 门禁全通过且有未完成任务 → 从下方第一个非 done 任务继续，按其「步骤」执行；
5. in-progress 任务以其「步骤」勾选与证据行判断断点：有 RED 证据无 GREEN 证据 = 从实现继续；
6. 运行模式以本文件头部为准，不重新询问。

## 计划边界

- 范围内 / 范围外:
- 假设:
- 阻塞项:

## 任务拆解

<!-- 任务粒度 = 一组内聚的测试设计用例（薄垂直切片：完成后可构建、全绿、可独立提交）。
     每个任务自包含；新增任务必须能回指 design.md 测试设计表。
     细化完成后核对：所有任务覆盖的 Case ID 集合 = design.md 测试设计表全集。 -->

### T1: <标题>  [pending / in-progress / done]

- 覆盖测试设计用例: TC-001（<Given/When/Then 一行摘要>）、TC-002（<摘要>）
- 覆盖需求: FR-001（Change Type: modify，回归基线见 spec）
- 文件:
  - 测试: `test/<精确路径>`
  - 实现: `src/<精确路径>`（允许触碰的范围；范围外文件列入「范围外」）
- 步骤:
  - [ ] RED: 按 TC-001 写失败测试 `<测试名>`；运行 `<测试命令>` 确认因行为缺失而失败
  - [ ] GREEN: 最小实现；运行 `<完整套件命令>` 确认全绿、无新增警告
  - [ ] REFACTOR: 对照 `devflow-clean-code` 检视任务触碰范围；清理命名/函数/控制流/错误路径/重复/死代码；或记录 `N/A` + 无异味理由；每步跑测试
  - [ ] 记证据行、更新 traceability.md 对应行、提交 `<提交信息建议>`
- 完成定义: <可判定条件，如"TC-001/002 通过；mode 非法输入路径覆盖；套件 47/47">
- 依赖: <前置任务或无>
- 证据:
  - RED:   <命令> → <关键失败输出摘要> @ <commit>
  - GREEN: <命令> → <通过摘要> @ <commit>
  - REFACTOR: <改动摘要 + 测试命令摘要> @ <commit> / N/A（已对照 clean-code 自检，无任务内异味：<理由>）

### T2: …（同结构）

## 风险与待确认

| ID | 风险 / 待确认项 | 是否阻塞 | 处理方式 |
|---|---|---|---|

## 债务登记

<!-- 路过发现不顺手修的问题登记于此，ship 时核对去向 -->

| 项 | 发现于 | 去向（新工作项 / issue） |
|---|---|---|
````
