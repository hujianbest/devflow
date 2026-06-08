---
description: Flexible review entry — take the user's request, pick the matching review skill(s), and run an independent review (never self-review) to produce review content; runs standalone on any target, or feeds the in-flow gate when part of a work item
---

This command orchestrates the **DevFlow review (评审)** phase. 它既能 **独立运行**（用户直接要求"审查某个设计 / 代码 / 测试 / 规格"，无需先建 work item、也不必走完整流程），也能 **随流程评审**（作为 work item 流程中的评审再入口，把 verdict 喂给顺序门禁）。本命令唯一的不变量是：**评审由独立 reviewer 执行，作者 / 父会话不自审**——除此之外，按用户诉求灵活地选 skill、选目标、出审查内容。

## 运行模式

- **独立评审（standalone / ad-hoc）—— 默认**
  - 按用户诉求确定"审什么、用哪个评审 skill"，以用户指定的目标（文件 / 目录 / diff / 设计稿 / 测试 / 任意工件）为 `primary_artifact`，**直接** 派发独立 `devflow-reviewer` 子代理执行对应 review skill。
  - 把审查内容（结论 + findings + 建议）**直接交给用户**。
  - **不要求** work item / `progress.md`，**不推进** 门禁，**不强制** canonical handoff；record 落盘可选。
- **随流程评审（in-flow）**
  - 当存在 work item 且本次评审要喂给顺序门禁 / 推进流程时，交 `devflow-router` 按工件证据派发、消费 verdict、形成 canonical handoff。

## Phase scope

- Skills involved（按用户诉求 / 工件状态择一或多）:
  1. 评审 skill — 唯一判据权威，由独立 reviewer 完整执行其 `SKILL.md`：
     - 检查规格 → `devflow-spec-review`（`primary_artifact` 默认 `features/<id>/requirement.md`，standalone 下为用户指定的规格目标）
     - 检查设计 → `devflow-component-design-review`（组件设计）和/或 `devflow-ar-design-review`（AR 设计）
     - 检查测试 → `devflow-test-review`
     - 检查代码 → `devflow-code-review`
  2. `devflow-router` — **仅 in-flow 模式需要**：恢复工件状态、消费 verdict、推进门禁、形成 handoff
- Reviewer dispatched: 独立 `devflow-reviewer` 子代理（system prompt = `agents/devflow-reviewer.md`）。standalone 由本命令直接派发；in-flow 由 `devflow-router` 派发。
- Craft 透镜（评审子代理内部叠加，不是流程节点、不进 handoff、不产 verdict）：评审 skill 在各自 `SKILL.md` 的 `## 质量透镜（Craft）` 节声明要叠加的 craft，reviewer 据此读取为判别标尺：
  - `devflow-code-review` → `devflow-coding-craft`
  - `devflow-test-review` → `devflow-test-craft`
  - `devflow-component-design-review` → `devflow-design-craft`
  - `devflow-ar-design-review` → `devflow-design-craft`（代码层设计）+ `devflow-test-craft`（测试设计章节）
  - `devflow-spec-review` 无 craft 透镜
- 本命令 **不 authoring、不改任何工件**。

## When to use

- 用户直接要求审查某个设计 / 代码 / 测试 / 规格（standalone），无论当前是否已有 work item
- 想对某个目标做一次独立把关 / 二次评审，而不想走完整 authoring 阶段
- work item 流程中需要触发 / 重审某评审，并把 verdict 喂给顺序门禁（in-flow）
- `Pending Reviews And Gates` 里挂着未消费评审，想集中触发并消费（in-flow）

不适用：

- 需要先写 / 改工件 → `/devflow-specify`、`/devflow-design`、`/devflow-build`
- 评审返回需修改后的回修 → 回对应 authoring 命令（本命令只评审，不回修）
- 完成判断 / 收口 → `/devflow-ship`；紧急修复的复现 + 根因 → `/devflow-fix`

## Hard contract（节选自 AGENTS.md，不可绕开）

- **独立 reviewer，不自审**：评审由独立 `devflow-reviewer` 子代理执行，父会话 / 作者 **不得** 自评。standalone 直接派发，in-flow 经 `devflow-router`
- **本命令不改任何工件**：发现写进 findings，回修交对应 authoring 命令
- **顺序门禁纪律**：同时审测试与代码时 **必须** 先 `devflow-test-review` 再 `devflow-code-review`；test-review 未通过 **严禁** 进入 code-review。standalone 模式至少给出该风险提示，in-flow 模式严格喂门禁、不可跳序
- **评审目标必须存在且可定位**：`primary_artifact`（用户指定目标或工件）缺失 / 不可定位 → 不得凭空评审，让用户补齐目标，或回对应 authoring 命令
- **模式忠于用户诉求**：用户只要一次独立审查 → 走 standalone，**不强行** 拉起整套 work item / router / 门禁机制；用户要喂门禁 / 推进流程 → 走 in-flow
- reviewer 返回契约不变（结论 / findings / 可选 record path / 可选 next 建议）；standalone 下 `work_item_*` / `owning_component` 缺失可标 `ad-hoc`，record path 与 next 建议均为可选

## Workflow（不复制 SKILL.md，只编排）

1. **解析用户诉求（intent-first）**：
   - 审什么对象（设计 / 代码 / 测试 / 规格）+ 目标在哪（文件 / 目录 / diff / 工件路径）
   - 用户未指明对象时，按现有工件状态推断；范围仍不唯一 → 向用户确认审查范围（standalone）或回 `/devflow` 走 router（in-flow）
2. **选运行模式**：
   - 用户要一次独立审查 / 不需要喂门禁 → **standalone**
   - 存在 work item 且要喂顺序门禁 / 推进流程 → **in-flow**（转 `devflow-router`）
3. **选评审 skill**：按"意图 → skill"映射；多个对象就绪时按 canonical 顺序排队 `spec → component-design → ar-design → test → code`
4. **派发独立 reviewer**：
   - 构造 Review Request Pack（`target_skill`、`primary_artifact` = 用户目标 / 工件、`supporting_context`、`agents_md_anchor`；standalone 下缺失的 `work_item_*` / `owning_component` 标 `ad-hoc`，`expected_record_path` 可选）
   - standalone：**直接** 派发独立 reviewer；in-flow：交 `devflow-router` 派发
5. **取回 reviewer 结论与 findings**：
   - standalone：把审查内容（结论 + findings + 建议下一步）**直接呈现给用户**；如存在 work item 或用户要求则落 review record；**不** 推进门禁、**不** 强制 canonical handoff
   - in-flow：交 `devflow-router` 消费 verdict，按 Reviewer Dispatch Protocol 的 Verdict 映射推进 / 回修 / `reroute_via_router`，形成 canonical handoff
6. 回修一律回对应 authoring 命令（`devflow-specify` / `devflow-component-design` / `devflow-ar-design` / `devflow-tdd-implementation`）；本命令只评审。

## Anti-rationalization quick refs

| 误判 | 反向行动 |
|---|---|
| "用户只想审一个文件，我得先帮他建 work item、跑 router 才能审" | 禁止；standalone 直接对用户目标派发独立 reviewer 出结论，不强拉整套流程 |
| "standalone 没有 router，那我父会话自己读读给个结论就行" | 禁止；唯一不变量是独立 reviewer 执行，作者 / 父会话永不自审 |
| "顺手在 review 命令里把发现的笔误改了" | 禁止；本命令不改任何工件，发现写进 findings，回修交对应 authoring 命令 |
| "用户只说审代码，但我顺手把测试也按门禁卡了" | standalone 只需对用户要求的对象出审查内容；但若同时审测试与代码，仍先 test-review 再 code-review |
| "目标路径我没找到，先按印象审一审" | 禁止；`primary_artifact` 不可定位不得评审，先让用户补齐目标 |
| "评审说需修改，我在本命令里直接改一版" | 禁止；回修回对应 authoring 命令，本命令只做评审与（in-flow）消费 verdict |
