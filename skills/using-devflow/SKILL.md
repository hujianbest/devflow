---
name: using-devflow
description: 发现并调用 DevFlow skills。适用于会话开始时，或需要发现当前任务应使用哪项 DevFlow skill 时。这是约束 DevFlow skills 如何被发现和调用的元 skill；runtime routing 归属 devflow-router。
---

# 使用 DevFlow

## 总览

DevFlow Skills 是一组按开发阶段组织的工程工作流技能。每个 skill 都编码了一套资深工程师会遵循的具体流程。本元 skill 帮助你发现并应用当前任务需要的 DevFlow skill。

`using-devflow` 只承担入口总指导原则和 skill discovery。它不做 runtime routing，不消费 review / gate 结论，不决定 Workflow Profile，不派发 reviewer subagent，也不替模块架构师、开发负责人或开发人员拍板。所有基于工件状态的路由、恢复、profile 判定和 reviewer 派发都属于 `devflow-router`。

## 技能发现

任务到达时，先识别开发阶段并加载对应 skill。下面是 discovery map，不是运行时状态机；任何需要读取工件状态来决定下一节点的场景，都进入 `devflow-router`。

```text
任务到达
    |
    |-- 不确定当前阶段 / 继续推进 / 消费 review 或 gate / profile 不清 / 证据冲突
    |   -> devflow-router
    |
    |-- 澄清已接受的 SR / AR / DTS / CHANGE 需求
    |   -> devflow-specify
    |
    |-- 独立审查 requirement spec
    |   -> devflow-router -> devflow-spec-review reviewer
    |
    |-- 编写或修订组件实现设计
    |   -> devflow-component-design
    |
    |-- 独立审查组件实现设计
    |   -> devflow-router -> devflow-component-design-review reviewer
    |
    |-- 编写或修订 AR 实现设计和测试设计
    |   -> devflow-ar-design
    |
    |-- 独立审查 AR 实现设计
    |   -> devflow-router -> devflow-ar-design-review reviewer
    |
    |-- 基于已批准设计做 TDD 实现
    |   -> devflow-tdd-implementation
    |
    |-- 独立审查 TDD 后测试有效性
    |   -> devflow-router -> devflow-test-review reviewer
    |
    |-- 独立审查 C / C++ 代码质量
    |   -> devflow-router -> devflow-code-review reviewer
    |
    |-- 判断完成证据是否足够
    |   -> devflow-router -> devflow-completion-gate
    |
    |-- 缺陷复现、根因和 hotfix authoring
    |   -> devflow-router -> devflow-problem-fix
    |
    `-- 收口、closeout、长期记录同步
        -> devflow-router -> devflow-finalize
```

## 核心运行行为

这些行为适用于所有 DevFlow skills，且不可协商。

### 1. 工件优先

DevFlow 是 artifact-first 工作流。决策依据来自磁盘工件：`features/<id>/progress.md`、`requirement.md`、`ar-design-draft.md`、`tasks.md`、`task-board.md`、`reviews/`、`evidence/`、`completion.md`、长期 `docs/` 资产，以及项目 `AGENTS.md`。

当聊天历史与磁盘工件冲突时，磁盘工件优先。不要凭“上次好像已经做过”继续推进；把冲突交给 `devflow-router`，由它按工件证据恢复。

### 2. 显式暴露假设

在实现任何非平凡内容之前，明确说明你的假设：

```text
我正在基于以下假设：
1. [关于需求的假设]
2. [关于架构的假设]
3. [关于范围的假设]
-> 如果不对，请现在纠正；否则我将按这些假设继续。
```

不要默默补全模糊需求。最常见的失败模式是做出错误假设，并在未经检查的情况下继续推进。

### 3. 主动管理困惑

当你遇到不一致、相互冲突的需求或不清晰的规格说明时：

1. 停下，不要靠猜测继续推进。
2. 明确指出具体困惑是什么。
3. 说明权衡，或提出澄清问题。
4. 等待问题解决；如果困惑来自工件状态，交给 `devflow-router`。

### 4. 必要时提出反对意见

你不是只会说“是”的机器。当某个方案存在明显问题时：

- 直接指出问题。
- 解释具体缺点，能量化时就量化。
- 提出替代方案。
- 如果对方在充分了解信息后仍决定覆盖你的建议，就接受这个决定。

### 5. 强制保持简单

你的自然倾向是过度复杂化。要主动抵抗这种倾向。

在完成任何实现之前，先问：

- 这能不能用更少的代码完成？
- 这些抽象是否配得上它们带来的复杂度？
- 一位 Staff 工程师看到这里，会不会说“为什么不直接……”？

优先选择朴素、明显、可验证的方案。

### 6. 保持范围纪律

只修改你被要求修改的内容。

不要：

- 删除你不理解的注释。
- “清理”与当前任务无关的代码。
- 顺手重构相邻系统。
- 在没有明确批准的情况下删除看起来未使用的代码。
- 因为某个功能“看起来有用”就在 spec 之外添加它。

### 7. 验证，而不是假设

每个 skill 都包含验证步骤。验证通过之前，任务不算完成。“看起来对”永远不够，必须有证据，例如通过的测试、构建输出、review record、evidence record 或 completion gate 记录。

### 8. 保持角色隔离

Authoring leaf 不评审自己的输出。review 节点必须由 `devflow-router` 派发独立 reviewer subagent；`devflow-tdd-implementation` 才能派发 implementer subagent。其他节点不得私自创建 reviewer、implementer、coordinator 或嵌套 persona。

### 9. 不替团队角色拍板

DevFlow 不做业务、范围、优先级、架构边界或接口契约决策。遇到这类决策时，停下并交给需求负责人、模块架构师、开发负责人或开发人员。

## 需要避免的失败模式

这些错误看起来像是在推进，实际会破坏 DevFlow：

1. 把 `using-devflow` 当成 runtime router。
2. 在入口 skill 中消费 review / gate verdict。
3. 在入口 skill 中决定 Workflow Profile、Execution Mode 或 component-impact / hotfix 分支。
4. 从父会话直接调用 review skill，而不是让 `devflow-router` 派发独立 reviewer。
5. 把 `using-devflow` 写入 `Next Action Or Recommended Skill` 或任何 runtime handoff 字段。
6. 发现证据冲突时按聊天记忆推进。
7. 因为用户说 `auto` 就跳过 review、gate、approval 或 evidence。
8. 在同一个 work item 内把 SR analysis 切到 AR implementation。
9. 跳过验证，因为“看起来对”。
10. 顺手修改与当前任务无关的内容。

## Skill 规则

1. **开始工作前检查适用 skill。** Skills 编码了防止常见错误的流程。

2. **Skills 是 workflow，不是建议。** 按步骤执行，不跳过 hard gate、review 或 verification。

3. **入口只做 discovery。** `using-devflow` 可以识别当前任务应该加载哪个 DevFlow skill；凡是需要根据工件状态判断下一节点，都必须交给 `devflow-router`。

4. **Runtime routing 只属于 router。** `devflow-router` 是 Workflow Profile、Execution Mode、canonical next node、reviewer dispatch、review / gate recovery 的唯一 runtime authority。

5. **多个 skills 可以按顺序适用。** 一个 AR 可能经历 `devflow-specify` -> `devflow-spec-review` -> `devflow-ar-design` -> `devflow-ar-design-review` -> `devflow-tdd-implementation` -> `devflow-test-review` -> `devflow-code-review` -> `devflow-completion-gate` -> `devflow-finalize`。是否能从一个节点进入下一个 runtime 节点，由 `devflow-router` 根据当前 leaf handoff 与工件证据决定。

6. **不确定时进入 router。** 如果阶段、profile、工件新鲜度、review / gate verdict、任务队列、组件影响或 hotfix 信号不清，加载 `devflow-router`。

## 生命周期序列

完整 feature 或 work item 的典型 DevFlow sequence 如下。不是每个任务都需要每个节点；router 负责按工件证据恢复和裁剪运行时路径。

```text
SR requirement-analysis:
1. devflow-specify                  -> 澄清子系统级需求
2. devflow-spec-review              -> 独立审查规格
3. devflow-component-design         -> 可选：修订组件实现设计
4. devflow-component-design-review  -> 可选：独立审查组件设计
5. devflow-finalize                 -> analysis closeout

AR / CHANGE implementation:
1. devflow-specify                  -> 澄清需求规格
2. devflow-spec-review              -> 独立审查规格
3. devflow-component-design         -> component-impact 时插入
4. devflow-component-design-review  -> component-impact 时插入
5. devflow-ar-design                -> AR 实现设计和测试设计
6. devflow-ar-design-review         -> 独立审查 AR 设计
7. devflow-tdd-implementation       -> TDD 实现
8. devflow-test-review              -> 独立审查已落地测试
9. devflow-code-review              -> 独立代码检视
10. devflow-completion-gate         -> 完成证据判断
11. devflow-finalize                -> implementation closeout

DTS / hotfix:
1. devflow-router                   -> 识别 hotfix profile
2. devflow-problem-fix              -> 复现、根因、最小安全修复边界
3. devflow-ar-design 或 devflow-tdd-implementation
4. devflow-test-review
5. devflow-code-review
6. devflow-completion-gate
7. devflow-finalize
```

## Quick Reference

| Phase | Skill | 一句话说明 |
|---|---|---|
| Meta | `using-devflow` | 入口总纲与 DevFlow skill discovery |
| Route | `devflow-router` | 基于工件证据做 runtime routing、profile 判定、恢复编排和 reviewer 派发 |
| Define | `devflow-specify` | 把已接受的 SR / AR / DTS / CHANGE 澄清为可评审规格 |
| Review | `devflow-spec-review` | 独立审查规格清晰度、可追溯性和可设计性 |
| Design | `devflow-component-design` | 编写或修订组件实现设计 |
| Review | `devflow-component-design-review` | 独立审查组件实现设计 |
| Design | `devflow-ar-design` | 编写 AR 实现设计，并嵌入测试设计章节 |
| Review | `devflow-ar-design-review` | 独立审查 AR 实现设计和测试设计 |
| Build | `devflow-tdd-implementation` | 基于已批准设计做 C / C++ TDD 实现 |
| Review | `devflow-test-review` | 独立审查 TDD 后测试用例有效性 |
| Review | `devflow-code-review` | 独立检查 C / C++ 质量、SOA 边界和嵌入式风险 |
| Gate | `devflow-completion-gate` | 判断 evidence bundle 是否满足完成条件 |
| Fix | `devflow-problem-fix` | 处理缺陷复现、根因、hotfix 边界和回流 |
| Close | `devflow-finalize` | 收口、同步长期记录并形成 handoff |

## DevFlow 适配约束

- `using-devflow` 是 public entry，永远不是合法 runtime next action。
- `next_action_or_recommended_skill` 必须是 canonical runtime node，不能是 `using-devflow` 或自由文本。
- Legal profiles 只有 `requirement-analysis`、`standard`、`component-impact`、`hotfix`、`lightweight`；profile 判定由 `devflow-router` 执行。
- Legal execution modes 只有 `interactive`、`auto`；`auto` 不跳过任何 review、gate、approval 或 evidence。
- SR work item 只属于 `requirement-analysis` 子图；SR 派生的候选 AR 必须新建 AR work item。
- 项目 `AGENTS.md` 和各 leaf skill 的 hard gates 不能被入口 discovery 削弱。

## 支撑参考

| 文件 | 用途 |
|---|---|
| `AGENTS.md` | DevFlow 硬契约与门禁纪律 |
| `skills/devflow-router/SKILL.md` | 权威 runtime routing、恢复编排与 reviewer dispatch |
| `docs/principles/04 workflow-architecture.md` | DevFlow 生命周期和质量门禁 |
