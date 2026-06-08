---
name: using-devflow
description: 发现并调用 DevFlow skills，并承载跨 skill 永远生效的行为宪法。适用于会话开始时，或需要判断当前任务应使用哪项 DevFlow skill / 该叠加哪个质量透镜时。这是约束 DevFlow skills 如何被发现和组合的元 skill；运行时证据路由归 devflow-router，质量提升归 devflow-*-craft 透镜。
---

# 使用 DevFlow

## 总览

DevFlow Skills 是一组按开发阶段组织的工程工作流技能，每个 skill 编码了一套资深工程师会遵循的具体流程。本元 skill 帮你 **发现** 当前任务该用哪个 DevFlow skill、该叠加哪个质量透镜，并承载 **跨所有 skill 永远生效的行为宪法**。

`using-devflow` 只承担入口发现与行为宪法。它**不做**运行时证据路由（归 `devflow-router`），**不产生** review/gate 结论，**不替**团队角色拍板。

## DevFlow 的三层关系（必须分清）

DevFlow 2.0 有三类协作但职责不同的 skill。混淆它们是最常见的失败：

| 层 | 谁 | 回答 | 关键约束 |
|---|---|---|---|
| **Meta（本 skill）** | `using-devflow` | 该用哪个 skill / 该叠加哪个透镜 + 行为宪法 | 不路由、不持运行时状态、永不写入 handoff |
| **Runtime Router** | `devflow-router` | 依据工件证据决定唯一 canonical 下一步、profile、reviewer 派发 | 运行时唯一路由权威；happy path 之外的恢复 / 冲突归它 |
| **Flow 节点（canonical）** | `devflow-specify` … `devflow-finalize` | 把上游 object 转成下游 object，交独立评审 | 写 progress/handoff；可在工作流内部叠加 craft 透镜 |
| **Craft 透镜（非 canonical）** | `devflow-design-craft` / `devflow-coding-craft` / `devflow-test-craft` | 怎么把设计 / 代码 / 测试**做好** | 由 flow 节点内部调用；**不**写 progress/handoff、**不**产 verdict、**不**改流程拓扑 |

> 一句话：**meta 发现，router 路由，flow 推进，craft 提质。** craft 与 meta 都永远不出现在 `next_action_or_recommended_skill`。

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
    |   -> devflow-component-design        ⟲ 叠加 devflow-design-craft
    |
    |-- 独立审查组件实现设计
    |   -> devflow-router -> devflow-component-design-review reviewer
    |
    |-- 编写或修订 AR 实现设计和测试设计
    |   -> devflow-ar-design               ⟲ 叠加 devflow-design-craft + devflow-test-craft
    |
    |-- 独立审查 AR 实现设计
    |   -> devflow-router -> devflow-ar-design-review reviewer
    |
    |-- 基于已批准设计做 TDD 实现
    |   -> devflow-tdd-implementation      ⟲ 叠加 devflow-coding-craft + devflow-test-craft
    |
    |-- 独立审查 TDD 后测试有效性
    |   -> devflow-router -> devflow-test-review reviewer   ⟲ 用 devflow-test-craft 作判别标准
    |
    |-- 独立审查 C / C++ 代码质量
    |   -> devflow-router -> devflow-code-review reviewer   ⟲ 用 devflow-coding-craft 作判别标准
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

`⟲ 叠加` = 该 flow 节点在其工作流内部调用对应 craft 透镜以提升产物质量；叠加透镜**不改变**流程拓扑、**不**写入 handoff。

## DevFlow 行为宪法（Core Operating Behaviors）

这些行为适用于所有 DevFlow skills（flow 与 craft），不可协商。它们就是「资深工程师的默认底色」。

### 1. 工件优先

DevFlow 是 artifact-first 工作流。决策依据来自磁盘工件：`features/<id>/progress.md`、`requirement.md`、`ar-design-draft.md`、`tasks.md`、`task-board.md`、`reviews/`、`evidence/`、`completion.md`、长期 `docs/` 资产、项目 `AGENTS.md`。聊天历史与磁盘工件冲突时，**工件优先**；把冲突交给 `devflow-router` 按证据恢复。

### 2. 显式暴露假设

实现任何非平凡内容前，明确说明假设：

```text
我正在基于以下假设：
1. [关于需求的假设]
2. [关于架构的假设]
3. [关于范围的假设]
-> 如果不对，请现在纠正；否则我将按这些假设继续。
```

不要默默补全模糊需求。最常见的失败模式是做错假设并在未经检查下继续推进。

### 3. 主动管理困惑

遇到不一致、冲突需求或不清规格时：停下不猜 → 指出具体困惑 → 说明权衡或提澄清问题 → 等解决；困惑来自工件状态则交 `devflow-router`。

### 4. 必要时提出反对意见

你不是 yes-machine。方案有明显问题时：直接指出 → 量化缺点 → 给替代方案 → 对方充分知情后仍坚持就接受。

### 5. 强制保持简单

你的自然倾向是过度复杂化，主动抵抗。完成实现前问：能更少代码吗？抽象配得上复杂度吗？Staff 工程师会不会说「为什么不直接……」？优先朴素、明显、可验证的方案。（设计 / 编码层的具体判断见 `devflow-design-craft` / `devflow-coding-craft`。）

### 6. 保持范围纪律

只修改被要求修改的内容。不删不懂的注释、不清理无关代码、不顺手重构相邻系统、不在无批准下删看似无用代码、不在 spec 外加功能。

### 7. 验证，而不是假设

每个 skill 都有验证步骤；验证通过前任务不算完成。「看起来对」永远不够，必须有证据：通过的测试、构建输出、review record、evidence record 或 completion gate 记录。

### 8. 保持角色隔离

Authoring leaf 不评审自己的输出。review 节点必须由 `devflow-router` 派发独立 reviewer subagent；`devflow-tdd-implementation` 才能派发 implementer subagent。craft 透镜**不**派发任何 subagent、**不**自封评审。

### 9. 不替团队角色拍板

DevFlow 不做业务、范围、优先级、架构边界或接口契约决策。遇到这类决策时，停下交给需求负责人、模块架构师、开发负责人或开发人员。

## 需要避免的失败模式

1. 把 `using-devflow` 当成 runtime router。
2. 在入口 skill 中消费 review / gate verdict。
3. 在入口 skill 中决定 Workflow Profile / Execution Mode / component-impact / hotfix 分支。
4. 从父会话直接调用 review skill，而不是让 `devflow-router` 派发独立 reviewer。
5. 把 `using-devflow` 或任何 `devflow-*-craft` 透镜写进 `Next Action Or Recommended Skill` 或 handoff 字段。
6. 发现证据冲突时按聊天记忆推进。
7. 因为用户说 `auto` 就跳过 review / gate / approval / evidence。
8. 在同一 work item 内把 SR analysis 切到 AR implementation。
9. 跳过验证，因为「看起来对」。
10. 把 craft 透镜误当成新的流程门禁或流程阶段（它只提质，不裁决、不路由）。

## Skill 规则

1. **开始工作前检查适用 skill。** Skills 编码了防止常见错误的流程与判断。
2. **Skills 是 workflow / 判断，不是建议。** 按步骤执行，不跳 hard gate、review 或 verification。
3. **入口只做 discovery。** `using-devflow` 识别该加载哪个 skill / 叠加哪个透镜；凡需按工件状态判断下一节点，交 `devflow-router`。
4. **Runtime routing 只属于 router。** profile、execution mode、canonical next node、reviewer dispatch、review / gate recovery 的唯一 runtime authority 是 `devflow-router`。
5. **多个 skills 可以组合。** 一个 AR 可能依次经历 `devflow-specify → spec-review → ar-design → ar-design-review → tdd-implementation → test-review → code-review → completion-gate → finalize`；其间设计 / 编码 / 测试节点**叠加对应 craft 透镜**。能否从一节点进入下一 runtime 节点由 `devflow-router` 依证据决定。
6. **不确定时进入 router。** 阶段、profile、工件新鲜度、verdict、任务队列、组件影响或 hotfix 信号不清时，加载 `devflow-router`。
7. **写设计 / 写码 / 写测试时主动叠加 craft 透镜。** 不要只满足「章节齐全 / 测试通过」；用透镜把产物提升到「设计得好 / 代码干净 / 测试有效」。

## 生命周期序列

完整 feature 或 work item 的典型 DevFlow sequence（不是每个任务都需要每个节点；router 按证据恢复和裁剪运行时路径；craft 透镜按需叠加）：

```text
SR requirement-analysis:
1. devflow-specify                  -> 澄清子系统级需求
2. devflow-spec-review              -> 独立审查规格
3. devflow-component-design         -> 可选：修订组件设计   ⟲ devflow-design-craft
4. devflow-component-design-review  -> 可选：独立审查
5. devflow-finalize                 -> analysis closeout

AR / CHANGE implementation:
1. devflow-specify                  -> 澄清需求规格
2. devflow-spec-review              -> 独立审查规格
3. devflow-component-design         -> component-impact 时插入  ⟲ devflow-design-craft
4. devflow-component-design-review  -> component-impact 时插入
5. devflow-ar-design                -> AR 实现设计 + 测试设计   ⟲ devflow-design-craft + devflow-test-craft
6. devflow-ar-design-review         -> 独立审查 AR 设计
7. devflow-tdd-implementation       -> TDD 实现                ⟲ devflow-coding-craft + devflow-test-craft
8. devflow-test-review              -> 独立审查测试有效性       ⟲ 以 devflow-test-craft 为判别标准
9. devflow-code-review              -> 独立代码检视            ⟲ 以 devflow-coding-craft 为判别标准
10. devflow-completion-gate         -> 完成证据判断
11. devflow-finalize                -> implementation closeout

DTS / hotfix:
1. devflow-router                   -> 识别 hotfix profile
2. devflow-problem-fix              -> 复现、根因、最小安全修复边界
3. devflow-ar-design 或 devflow-tdd-implementation   ⟲ 相应 craft 透镜
4. devflow-test-review
5. devflow-code-review
6. devflow-completion-gate
7. devflow-finalize
```

## Quick Reference

| 层 | Skill | 一句话说明 |
|---|---|---|
| Meta | `using-devflow` | 入口发现、行为宪法、三层关系 |
| Route | `devflow-router` | 基于工件证据做 runtime routing、profile 判定、恢复编排和 reviewer 派发 |
| Define | `devflow-specify` | 把已接受的 SR/AR/DTS/CHANGE 澄清为可评审规格 |
| Review | `devflow-spec-review` | 独立审查规格清晰度、可追溯性和可设计性 |
| Design | `devflow-component-design` | 编写或修订组件实现设计 |
| Review | `devflow-component-design-review` | 独立审查组件实现设计 |
| Design | `devflow-ar-design` | 编写 AR 实现设计，并嵌入测试设计章节 |
| Review | `devflow-ar-design-review` | 独立审查 AR 实现设计和测试设计 |
| Build | `devflow-tdd-implementation` | 基于已批准设计做 C/C++ TDD 实现 |
| Review | `devflow-test-review` | 独立审查 TDD 后测试用例有效性 |
| Review | `devflow-code-review` | 独立检查 C/C++ 质量、SOA 边界和嵌入式风险 |
| Gate | `devflow-completion-gate` | 判断 evidence bundle 是否满足完成条件 |
| Fix | `devflow-problem-fix` | 处理缺陷复现、根因、hotfix 边界和回流 |
| Close | `devflow-finalize` | 收口、同步长期记录并形成 handoff |
| **Craft** | `devflow-design-craft` | 质量透镜：怎么把设计做好（简单性 / 抽象克制 / 接口契约 / 嵌入式防御） |
| **Craft** | `devflow-coding-craft` | 质量透镜：怎么把代码写好（Rule 0 / 薄切片 / 范围纪律 / 可读性） |
| **Craft** | `devflow-test-craft` | 质量透镜：怎么把测试写好（金字塔 / 测状态不测交互 / DAMP / mock 克制） |

## DevFlow 适配约束

- `using-devflow` 是 public entry，永远不是合法 runtime next action。
- `devflow-*-craft` 是质量透镜，同样永远不是合法 runtime next action。
- `next_action_or_recommended_skill` 必须是 §7 canonical runtime node（见 `references/devflow-conventions.md`），不能是 `using-devflow`、craft 透镜或自由文本。
- Legal profiles：`requirement-analysis` / `standard` / `component-impact` / `hotfix` / `lightweight`；profile 判定由 `devflow-router` 执行。
- Legal execution modes：`interactive` / `auto`；`auto` 不跳过任何 review / gate / approval / evidence。
- SR work item 只属于 `requirement-analysis` 子图；SR 派生的候选 AR 必须新建 AR work item。
- 项目 `AGENTS.md` 与各 leaf skill 的 hard gates 不能被入口 discovery 或 craft 透镜削弱。

## 支撑参考

| 文件 | 用途 |
|---|---|
| `references/devflow-conventions.md` | 单一真相源：产物布局 / progress 字段 / handoff 字段 / profile / 节点表 |
| `skills/using-devflow/references/devflow-work-item-readme-template.md` | 通用 work item README 模板（跨 skill 共享） |
| `skills/using-devflow/references/devflow-progress-template.md` | 通用 progress.md 模板（跨 skill 共享） |
| `skills/using-devflow/references/devflow-traceability-template.md` | 通用 traceability.md 模板（跨 skill 共享） |
| `skills/devflow-router/SKILL.md` | 权威 runtime routing、恢复编排与 reviewer dispatch |
| `docs/devflow-2.0-design-spec.md` | DevFlow 2.0 设计说明书（三层关系与匠艺注入的依据） |
