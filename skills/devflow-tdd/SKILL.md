---
name: devflow-tdd
description: 在 DevFlow change 的 R2 通过后实现功能，或 R3 findings 需要测试/代码返工时使用。以 tasks.md 为唯一任务与 TDD 证据载体，执行 RED→GREEN→REFACTOR，并在 change.json 维护门禁状态；不负责规格或设计决策。
---

# DevFlow TDD

## Iron Law

> 没有先观察到因目标行为缺失而失败的测试，就没有实现代码。

先实现后补测试不能证明测试会抓住缺失行为。已经提前写出的实现应移除并从 RED
重新开始；一次性原型、生成代码或纯配置例外需要人明确确认，正式行为仍要有可复核
验证。

## 工件边界

本阶段读取同一 change 目录中的：

- `change.json`
- `srs.md`
- `delta-spec.md`
- `delta-design.md`
- `tasks.md`
- `traceability.md`
- `reviews/`（返工时）

职责严格分离：

- `tasks.md` 只保存任务、执行 cursor、RED/GREEN/REFACTOR 步骤、实际证据、
  返工队列和债务。模板见 `references/tasks-template.md`。
- `change.json` 是 R1/R2/R3、canonical sync、closeout/DoD 和 archive 状态的唯一来源。
- `traceability.md` 保持固定链
  `需求条目 → Spec Section → Design Section/Case → Task → Code/Test → Evidence`。

不要在 `tasks.md` 建门禁表，也不要把任务步骤和命令输出塞入 `change.json`。

## 进入实现的 preflight

1. `componentMode` 明确，`gates.baselinePreflight.status=passed`。
2. `artifacts.srs`、`deltaSpec`、`deltaDesign` 均为 `accepted`。
3. `change.json.gates.r2.status=passed`；`executionMode=attended` 时还要求 r2
   `humanConfirmation=confirmed`。
4. existing 模式的 `specs/spec.md` 与 `specs/design.md` 仍为
   `baselineStatus: baseline-ready`，从不可变 `baseRevision` 到当前工作树没有
   未解决冲突；new 的 canonical artifact 可为 `absent-allowed`。
5. `delta-design.md` 有唯一 Case Index，每个 `TC-xxx` 可追溯到需求条目、Spec 和
   Design。

任何条件不满足都先修工件/门禁，不通过聊天记忆补齐。

## 细化 tasks.md

specify 已建立空骨架。实现前按 Case Index 把用例组织成薄垂直切片：

- 所有任务覆盖的 Case ID 集合必须**恰好等于** delta design 的 Case Index；
  缺失是漏实现，新增是设计漂移。
- 每个任务自包含：来源锚点与必要契约摘要、精确测试/实现路径、依赖、RED/GREEN/
  REFACTOR 步骤、命令、完成定义和允许触碰范围都内联。
- 不写“同上”“见上文”“按聊天讨论”。新上下文只读 change 工件就能执行任一任务。
- 一个任务完成后可构建、完整测试全绿，并形成独立可审查的切片。

发现 Case 缺失或设计无法实现时，不在任务里发明事实；回 `devflow-design`。

## 任务状态与唯一 next task

任务状态只使用：

- `pending`：未开始；
- `in-progress`：当前唯一执行任务；
- `blocked`：缺外部事实或上游工件需返工；
- `done`：RED/GREEN/REFACTOR、完整验证、追溯和证据全部闭合。

`tasks.md` 的 Execution Cursor 必须是：

- 一个明确 Task ID；
- `NONE`（所有任务 done）；或
- `BLOCKED`（并列候选、依赖冲突或阻塞原因已列出）。

选择规则：

1. 有且仅有一个 `in-progress`，它就是 next task。
2. 没有 `in-progress` 时，从依赖已 done、就绪条件满足的 pending 任务中选择。
3. 候选必须能唯一判定；选中后立即标 `in-progress` 并更新 cursor。
4. 多个同等候选、多个 `in-progress`、依赖环或磁盘状态矛盾时，cursor 置
   `BLOCKED`，先修状态，不猜。
5. 一个任务 done 后立即重读 `tasks.md` 并选择下一唯一任务；`executionMode`
   不增加任务间人工确认。

## 每个任务的循环

### RED

按当前 `TC-xxx` 写一个会失败的行为测试：

- 名称描述场景和结果；
- 一个测试验证一个行为；
- Then 中返回值、状态变化和外部副作用都有精确断言，包括负向断言；
- 只 fake/mock 硬件、外部组件、时钟或慢依赖，不 mock 本模块纯逻辑。

运行测试并确认它：

1. 是断言失败，不是编译/环境错误；
2. 因目标行为缺失而失败；
3. 失败信息与 Case 预期对应。

测试第一次就通过时停止：要么行为已存在，要么测试错误。查清并记录处置，不能伪造
RED。把命令、关键失败输出、时间和 revision/worktree anchor 写入任务证据。

### GREEN

只写让当前 RED 转绿的最少实现：

- 不实现其他 Case；
- 不引入 delta design 未批准的抽象；
- 不顺手清理无关代码。

运行当前测试、相关测试和完整套件；要求全部通过、构建无新增 warning。把实际命令、
通过数量和 revision/worktree anchor 写入 GREEN 证据。

### REFACTOR

只在全绿上做结构清理，不改变可观察行为。对照 `devflow-clean-code` 检查本任务
触碰范围的简洁、可靠、可维护、可测试、性能和范围纪律；每步保持全绿。

没有可改内容也必须记录：

```text
REFACTOR: N/A — 已检查 <具体维度和代码范围>，未发现任务内异味；
<完整命令> → <通过摘要> @ <anchor>
```

没有 REFACTOR 记录不能 done。发现需要跨边界重构或新行为，回设计或 RED，不混在
当前帽子下。

### 完成任务

只有同时满足以下条件才标 `done`：

- 所有 Case 的 RED 曾真实失败且原因正确；
- GREEN 与 REFACTOR 后完整验证全绿；
- 精确代码/测试路径和证据已写入；
- traceability 对应行的 Task、Code/Test、Evidence 已填；
- 无 open blocker，完成定义可判定且已满足。

更新状态和 cursor 后继续唯一 next task。

## Controller 与 implementer

runtime 支持 subagent 时，每个任务派发一个全新上下文的 implementer；controller
不在主上下文直接写测试/实现。任务小或赶时间不是跳过隔离上下文的理由。runtime
确实没有 subagent 能力时可 controller-direct，但在任务中记录能力缺失原因。

Context Pack 只包含：

- Task ID、`TC-xxx` 与 Given/When/Then；
- 需求条目/Spec/Design 稳定锚点和必要的局部契约、错误模型；
- 允许触碰的精确文件；
- RED、完整套件和构建命令；
- finding 摘录（返工时）；
- Quality Stack 的 `required_skills`（用技能名，不写路径）：至少本技能、`devflow-clean-code`、
  适用语言规范和命中 profile/领域的技能路径。

返回契约：

- `DONE`：`loaded_skills`、触碰文件、真实 RED/GREEN/REFACTOR 证据、
  clean-code 检查和已解决 finding；
- `NEEDS_CONTEXT`：缺少的具体工件/契约；
- `BLOCKED`：上游冲突、越界或环境问题。

controller 验证返回后才更新 `tasks.md` 与 traceability。证据不完整、skill 未加载、
断言被弱化或完整套件未跑，拒绝 `DONE`。

## R3 返工

R3 为 `rework` 时读取最新 review，并在 `tasks.md` 的 Rework Queue 为每条 open
critical/important finding 建记录：

1. 把 `change.json.artifacts.tasks.status` 置回 `draft`；门禁仍为 `rework`。
2. 保留原 done 任务和原证据；创建 `Tn-RWm`，不要覆盖历史。
3. 实现 bug 先用失败测试复现；弱测试先强化到能对当前错误实现 RED。
4. 纯结构 finding 在全绿上 REFACTOR，记录前后验证。
5. 完成后回填原 review 的 Resolution：修复摘要、代码/测试 anchor、验证命令；
   同步把返工项置为 `resolved`。
6. 所有 open finding 闭环后，把 `gates.r3` 从 `rework` 置为 `pending`，
   请求独立复审；
   TDD 作者不能写 `passed`。

finding 证明 SRS 或 delta design 错误时，当前任务置 `blocked`，
`gates.r3.status` 置 `blocked`，并把受影响的 r1/r2 及下游 gate 重新打开为
`pending`；回对应上游，不在代码里选择一个“看起来正确”的契约。

同一 R3 最多自动返工复审三轮。第三轮仍有 critical/important 或持续出现同类问题，
停止并提交剩余证据与明确决策点给人。

## 全部任务完成

当所有正常任务和返工任务都 done/resolved：

1. Execution Cursor 置 `NONE`；
2. 核对 Case Index 集合、traceability 全链和实际证据；
3. 将 `change.json.artifacts.tasks.status` 置 `complete`；
4. 将 `change.json.artifacts.traceability.status` 置 `complete`；
5. 将 `change.json.gates.r3.status` 置 `pending`，附任务与追溯证据锚点；
6. 进入独立测试/代码评审。

不得直接进入 canonical sync、DoD 或 archive；这些状态仍由 `change.json` 后续门禁
控制。

## 测试质量

完整判据见 `references/test-quality.md`。快速检查：

- mutation 思维：把关键比较、错误返回或副作用删掉，测试会红吗？
- 断言精确值，不用 `result != null` 或 `count > 0` 代替可知结果。
- 测试独立、可重复；受控时间/随机，不依赖执行顺序。
- fake/mock 只在真实边界，不能用调用次数替代行为结果。
- NFR Case 保存可量化证据，如 latency 分布、size、leak 或静态分析输出。

## 停止条件

只有以下情况暂停连续执行：

- 缺业务事实、专家决策或 profile 解释；
- SRS/Spec/Design/实现冲突；
- Case 集合漂移；
- 无法补齐的 Context Pack；
- 多个 next 候选、多个 in-progress、依赖冲突；
- 测试环境无法产生可信证据；
- R3 三轮上限。

## 自检

- [ ] R2 与 baseline preflight 通过，Case 集合完全一致。
- [ ] `tasks.md` 没有生命周期门禁；`change.json` 没有任务步骤/证据。
- [ ] 任意时刻最多一个 in-progress，Execution Cursor 唯一。
- [ ] 每个任务自包含并严格执行 RED→GREEN→REFACTOR。
- [ ] done 条件包含真实证据、完整套件和 traceability 回填。
- [ ] 返工保留原证据，finding 与 Resolution 一一闭环。
- [ ] traceability 固定链的后三列已填，无本阶段 `TBD(tdd)`。
- [ ] 全部完成后只把 R3 置为 `pending`，未越过后续门禁。

## 支撑参考

| 文件 | 用途 |
|---|---|
| `references/tasks-template.md` | 自包含任务、唯一 cursor、TDD 证据和返工队列 |
| `references/test-quality.md` | 断言、命名、fixture、fake/mock 与可重复性判据 |
