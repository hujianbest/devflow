---
name: using-devflow
description: 发现并调用 DevFlow skills，并承载跨 skill 永远生效的行为宪法。适用于会话开始时，或需要判断当前任务应使用哪项 DevFlow flow node、编码规范 skill 或领域约束 skill 时；运行时证据路由归 devflow-router。
---

# 使用 DevFlow

## 总览

DevFlow Skills 是一组按三层质量模型组织的工程工作流技能：SDD 保证意图正确，TDD 保证功能正确，第三层代码内在质量保证设计和代码值得长期持有。本元 skill 帮你 **发现** 当前任务该用哪个 DevFlow flow node、是否需要叠加编码规范 skill / 领域约束 skill，并承载 **跨所有 skill 永远生效的行为宪法**。

`using-devflow` 只承担入口发现与行为宪法。它**不做**运行时证据路由（归 `devflow-router`），**不产生** review/gate 结论，**不替**团队角色拍板。

## DevFlow 的层次关系（必须分清）

DevFlow 有核心流程、第三层内在质量扩展、平台适配三类能力。混淆它们是最常见的失败：

| 层 | 谁 | 回答 | 关键约束 |
|---|---|---|---|
| **Meta（本 skill）** | `using-devflow` | 该用哪个 flow node / 该叠加哪些扩展 skill + 行为宪法 | 不路由、不持运行时状态、永不写入 handoff |
| **Runtime Router** | `devflow-router` | 依据工件证据决定唯一 canonical 下一步、profile、reviewer 派发 | 运行时唯一路由权威；happy path 之外的恢复 / 冲突归它 |
| **Flow 节点（canonical）** | `devflow-specify` … `devflow-finalize` | 把上游 object 转成下游 object，交独立评审 | 写 progress/handoff；只写 canonical next action |
| **设计内在质量** | `devflow-clean-design` | 通用设计质量判断 | 不写 progress/handoff、不产 verdict、不改流程拓扑 |
| **编码内在质量** | `devflow-clean-code` | 通用代码质量判断 | 不写 progress/handoff、不产 verdict、不改流程拓扑 |
| **编码规范 skill** | `c-coding-standards` / `cpp-coding-standards` | 语言级编码规范、工具链、静态分析约束 | 不写 progress/handoff、不产 verdict、不改流程拓扑 |
| **领域约束 skill** | `embedded-development` / `automotive-development` | 领域风险、架构约束、证据要求及全流程投射 | 不写 progress/handoff、不产 verdict、不改流程拓扑 |

> 一句话：**meta 发现，router 路由，flow 推进，第三层扩展提供质量约束。** meta、编码规范 skill、领域约束 skill 都永远不出现在 `next_action_or_recommended_skill`。

## 技能发现

任务到达时，先识别开发阶段，再识别是否需要第三层扩展。下面是 discovery map，不是运行时状态机；任何需要读取工件状态来决定下一节点的场景，都进入 `devflow-router`。

```text
任务到达
    |
    |-- 不确定当前阶段 / 继续推进 / 消费 review 或 gate / profile 不清 / 证据冲突
    |   -> devflow-router
    |
    |-- 澄清已接受的 AR / DTS / CHANGE 需求
    |   -> devflow-specify
    |
    |-- 独立审查 requirement spec
    |   -> devflow-router -> devflow-spec-review reviewer
    |
    |-- 编写或修订组件实现设计
    |   -> devflow-component-design        ⟲ 叠加 devflow-clean-design + 适用领域约束
    |
    |-- 独立审查组件实现设计
    |   -> devflow-router -> devflow-component-design-review reviewer
    |
    |-- 编写或修订 AR 实现设计和测试设计
    |   -> devflow-ar-design               ⟲ 设计叠加 devflow-clean-design；测试设计服务第二层 TDD
    |
    |-- 独立审查 AR 实现设计
    |   -> devflow-router -> devflow-ar-design-review reviewer
    |
    |-- 基于已批准设计做 TDD 实现
    |   -> devflow-tdd-implementation      ⟲ 叠加适用编码规范 / 领域约束
    |
    |-- 独立审查 TDD 后测试有效性
    |   -> devflow-router -> devflow-test-review reviewer   ⟲ 第二层 TDD / 测试有效性判别
    |
    |-- 独立审查代码质量
    |   -> devflow-router -> devflow-code-review reviewer   ⟲ devflow-clean-code + 适用编码规范 / 领域约束
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

`⟲ 叠加` = flow 节点读取 `devflow-clean-design`、`devflow-clean-code`、编码规范 skill 或领域约束 skill 的判据。叠加内容不改变流程拓扑、不写入 handoff、不产 verdict。

## 第三层扩展发现

| 信号 | 叠加 skill |
|---|---|
| C 源码、头文件、C 单元测试、MISRA C、C 静态分析 | `c-coding-standards` |
| C++ 源码、C++ 测试、RAII、对象生命周期、模板、ABI、AUTOSAR C++ | `cpp-coding-standards` |
| 通用嵌入式、内存/资源约束、中断上下文、实时性、硬件/驱动交互、嵌入式证据 | `embedded-development` |
| 车载软件、ASIL、车载 SOA/MDC、DTC/诊断、整车启动/休眠/唤醒、SELinux、车载 evidence | `automotive-development` |

扩展 skill 可以同时叠加。例如车载 C++ 嵌入式 work item 通常叠加 `cpp-coding-standards`、`embedded-development` 与 `automotive-development`。

## DevFlow 行为宪法（Core Operating Behaviors）

这些行为适用于所有 DevFlow skills（flow、编码规范、领域约束与平台适配），不可协商。它们就是「资深工程师的默认底色」。

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

你的自然倾向是过度复杂化，主动抵抗。完成实现前问：能更少代码吗？抽象配得上复杂度吗？Staff 工程师会不会说「为什么不直接……」？优先朴素、明显、可验证的方案。（设计层判断见 `devflow-clean-design`；编码层判断见 `devflow-clean-code` 与适用编码规范 / 领域约束 skill。）

### 6. 保持范围纪律

只修改被要求修改的内容。不删不懂的注释、不清理无关代码、不顺手重构相邻系统、不在无批准下删看似无用代码、不在 spec 外加功能。

### 7. 验证，而不是假设

每个 skill 都有验证步骤；验证通过前任务不算完成。「看起来对」永远不够，必须有证据：通过的测试、构建输出、review record、evidence record 或 completion gate 记录。

### 8. 保持角色隔离

Authoring leaf 不评审自己的输出。review 节点必须由 `devflow-router` 派发独立 reviewer subagent；`devflow-tdd-implementation` 才能派发 implementer subagent。编码规范 / 领域约束 skill **不**派发任何 subagent、**不**自封评审。

### 9. 不替团队角色拍板

DevFlow 不做业务、范围、优先级、架构边界或接口契约决策。遇到这类决策时，停下交给需求负责人、模块架构师、开发负责人或开发人员。

## 需要避免的失败模式

1. 把 `using-devflow` 当成 runtime router。
2. 在入口 skill 中消费 review / gate verdict。
3. 在入口 skill 中决定 Workflow Profile / Execution Mode / component-impact / hotfix 分支。
4. 从父会话直接调用 review skill，而不是让 `devflow-router` 派发独立 reviewer。
5. 把 `using-devflow`、编码规范 skill 或领域约束 skill 写进 `Next Action Or Recommended Skill` 或 handoff 字段。
6. 发现证据冲突时按聊天记忆推进。
7. 因为用户说 `auto` 就跳过 review / gate / approval / evidence。
8. component-impact 缺 `docs/component-design.md` 时仍进入 AR 设计或 TDD。
9. 跳过验证，因为「看起来对」。
10. 把编码规范 / 领域约束 skill 误当成新的流程门禁或流程阶段（它们只提供约束，不裁决、不路由）。

## Skill 规则

1. **开始工作前检查适用 skill。** Skills 编码了防止常见错误的流程与判断。
2. **Skills 是 workflow / 判断，不是建议。** 按步骤执行，不跳 hard gate、review 或 verification。
3. **入口只做 discovery。** `using-devflow` 识别该进入哪个 flow node、叠加哪些编码规范 / 领域约束；凡需按工件状态判断下一节点，交 `devflow-router`。
4. **Runtime routing 只属于 router。** profile、execution mode、canonical next node、reviewer dispatch、review / gate recovery 的唯一 runtime authority 是 `devflow-router`。
5. **多个 skills 可以组合。** 一个 AR 可能依次经历 `devflow-specify → spec-review → ar-design → ar-design-review → tdd-implementation → test-review → code-review → completion-gate → finalize`；其间按项目与工件叠加 `devflow-clean-design`、`devflow-clean-code`、编码规范和领域约束。能否从一节点进入下一 runtime 节点由 `devflow-router` 依证据决定。
6. **不确定时进入 router。** 阶段、profile、工件新鲜度、verdict、任务队列、组件影响或 hotfix 信号不清时，加载 `devflow-router`。
7. **写设计 / 写码 / 评审 / 门禁时主动叠加第三层扩展。** 不要只满足「章节齐全 / 测试通过」；用 clean design、clean code、编码规范和领域约束把产物提升到长期可持有。

## 生命周期序列

完整 feature 或 work item 的典型 DevFlow sequence（不是每个任务都需要每个节点；router 按证据恢复和裁剪运行时路径；第三层扩展按需叠加）：

```text
AR / CHANGE implementation:
1. devflow-specify                  -> 澄清需求规格
2. devflow-spec-review              -> 独立审查规格
3. devflow-component-design         -> component-impact 时插入  ⟲ devflow-clean-design / 领域约束
4. devflow-component-design-review  -> component-impact 时插入
5. devflow-ar-design                -> AR 实现设计 + 测试设计   ⟲ devflow-clean-design；测试设计服务第二层 TDD
6. devflow-ar-design-review         -> 独立审查 AR 设计
7. devflow-tdd-implementation       -> TDD 实现                ⟲ devflow-clean-code / 编码规范 / 领域约束
8. devflow-test-review              -> 独立审查测试有效性       ⟲ 第二层 TDD / 测试有效性判别
9. devflow-code-review              -> 独立代码检视            ⟲ devflow-clean-code / 编码规范 / 领域约束
10. devflow-completion-gate         -> 完成证据判断
11. devflow-finalize                -> implementation closeout

DTS / hotfix:
1. devflow-router                   -> 识别 hotfix profile
2. devflow-problem-fix              -> 复现、根因、最小安全修复边界
3. devflow-ar-design 或 devflow-tdd-implementation   ⟲ 适用编码规范 / 领域约束
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
| Define | `devflow-specify` | 把已接受的 AR/DTS/CHANGE 澄清为可评审规格 |
| Review | `devflow-spec-review` | 独立审查规格清晰度、可追溯性和可设计性 |
| Design | `devflow-component-design` | 编写或修订组件实现设计 |
| Review | `devflow-component-design-review` | 独立审查组件实现设计 |
| Design | `devflow-ar-design` | 编写 AR 实现设计，并嵌入测试设计章节 |
| Review | `devflow-ar-design-review` | 独立审查 AR 实现设计和测试设计 |
| Build | `devflow-tdd-implementation` | 基于已批准设计做 TDD 实现 |
| Review | `devflow-test-review` | 独立审查 TDD 后测试用例有效性 |
| Review | `devflow-code-review` | 独立检查代码质量、设计一致性和适用扩展约束 |
| Gate | `devflow-completion-gate` | 判断 evidence bundle 是否满足完成条件 |
| Fix | `devflow-problem-fix` | 处理缺陷复现、根因、hotfix 边界和回流 |
| Close | `devflow-finalize` | 收口、同步长期记录并形成 handoff |
| Clean Design | `devflow-clean-design` | 第三层设计内在质量统筹 |
| Clean Code | `devflow-clean-code` | 第三层编码内在质量统筹 |
| Coding Standards | `c-coding-standards` / `cpp-coding-standards` | 第三层编码规范扩展 |
| Domain Constraints | `embedded-development` / `automotive-development` | 第三层领域约束扩展，覆盖全流程 |

## DevFlow 共同约定（Shared Conventions）

本节是 DevFlow 全部 skill 共享的**单一真相源**：产物布局、`progress.md` 字段、handoff 字段、profile、execution mode、canonical 节点清单、Read-on-presence、Promotion 与角色分离不变量。所有 `devflow-*` skill 以一行引用本节（「本 skill 遵循 `using-devflow` 的「DevFlow 共同约定」章节」），**不再各自复制**这些约定。

**覆盖优先级**：项目根 `AGENTS.md` 的 `## Project overrides` 可覆盖本节的等价路径与模板；未覆盖时以本节为准。

### 产物布局

```text
<component-repo>/
  AGENTS.md                         # 项目硬契约与覆盖点（可选）
  docs/
    component-design.md             # 长期组件实现设计
    ar-specs/AR<id>-<slug>.md       # 长期 AR 需求规格（从 requirement.md 提升）
    ar-designs/AR<id>-<slug>.md     # 长期 AR 实现设计（从 ar-design-draft.md 提升）
    interfaces.md                   # 可选；仅团队启用时读取 / 同步
    dependencies.md                 # 可选；仅团队启用时读取 / 同步
    runtime-behavior.md             # 可选；仅团队启用时读取 / 同步
  features/
    AR<id>-<slug>/ DTS<id>-<slug>/ CHANGE<id>-<slug>/
```

`features/<id>/` 下按需包含：`README.md`、`progress.md`、`requirement.md`、`component-design-draft.md`、`ar-design-draft.md`、`tasks.md`、`task-board.md`、`traceability.md`、`implementation-log.md`、`reviews/`（spec-review / component-design-review / ar-design-review / test-review / code-review）、`evidence/`（unit / integration / static-analysis / build）、`completion.md`、`closeout.md`。

### Read-on-presence 规则

- **必需长期资产缺失即阻塞**：component-impact 需要 `docs/component-design.md`；implementation closeout 前需要 `docs/ar-designs/AR<id>-<slug>.md`。
- **可选资产按存在性读取**：`docs/interfaces.md` / `dependencies.md` / `runtime-behavior.md` 仅在项目启用时读取 / 同步；缺失记 `N/A (project optional asset not enabled)`，不阻塞。
- **过程目录保留在 `features/` 下**：不要把已关闭 work item 移到 `features/archived/`，否则破坏追溯链接。

### `progress.md` canonical 字段

`Work Item Type`（AR/DTS/CHANGE）、`Work Item ID`、`Owning Component`（必填）、`Workflow Profile`、`Execution Mode`、`Current Stage`（canonical 节点；扩展 skill 不写入）、`Pending Reviews And Gates`、`Next Action Or Recommended Skill`（仅一个 canonical 节点）、`Blockers`、`Last Updated`。实现 profile 还需：`Task Plan Path`、`Task Board Path`、`Current Active Task`、`Implementer Dispatch Status`、`Implementer Context Pack`、`Implementation Report`。

### Handoff 字段

`current_node`、`work_item_id`、`owning_component`、`result`/`verdict`、`artifact_paths`、`record_path`（有 review/gate/verification record 时）、`evidence_summary`、`traceability_links`、`blockers`、`next_action_or_recommended_skill`（仅 canonical 节点）、`reroute_via_router`。

### 合法 Workflow Profile 与升级规则

| Profile | 适用场景 |
|---|---|
| `standard` | 既有组件 AR 增量、组件设计稳定、纯组件内修改 |
| `component-impact` | 新增组件 / 改 SOA 接口 / 改组件职责 / 改依赖 / 改状态机 / 组件设计缺失或过期 / 跨组件协调 |
| `hotfix` | DTS / 紧急缺陷 / 已上线问题修复 |
| `lightweight` | 极小、低风险、纯局部修改；保留 specify→completion 全链，仅压缩文档量 |

只允许单向升级（`standard → component-impact`），不允许降级。Profile 由 `devflow-router` 判定写入 `progress.md` 后为单一真相，其余 skill 只读。

### 合法 Execution Mode

`interactive` / `auto`。归一化顺序：用户显式 → `AGENTS.md` 默认 → 已有值 → 默认 `interactive`。`auto` 仅表示节点间不停下等真人确认；**不删除** review / gate / approval / 证据要求。

### Canonical 节点清单

13 个 canonical 工作节点（`Current Stage` / `next_action_or_recommended_skill` 只能取这些）：`devflow-router`、`devflow-specify`、`devflow-spec-review`、`devflow-component-design`、`devflow-component-design-review`、`devflow-ar-design`、`devflow-ar-design-review`、`devflow-tdd-implementation`、`devflow-test-review`、`devflow-code-review`、`devflow-completion-gate`、`devflow-finalize`、`devflow-problem-fix`。

**非 canonical（不进 progress/handoff）**：`using-devflow`（meta）、`devflow-clean-design`、`devflow-clean-code`、`c-coding-standards`、`cpp-coding-standards`、`embedded-development`、`automotive-development`、平台适配文档。

### Promotion 规则

仅在 `devflow-finalize` 的 closeout 阶段、且 completion gate 允许时提升长期资产：`requirement.md → docs/ar-specs/`、`ar-design-draft.md → docs/ar-designs/`、`component-design-draft.md → docs/component-design.md`（模块架构师 sign-off 后）；可选子资产仅在启用且变化时同步。

### 角色分离不变量

review 必须由 `devflow-router` 派发**独立 reviewer subagent**，不内联、作者不自审；implementer 只由 `devflow-tdd-implementation` 派发；reviewer 不改任何生产代码 / 测试 / 设计；DevFlow 不替团队角色拍板业务 / 范围 / 优先级 / 架构边界 / 接口契约。

## DevFlow 适配约束

- `using-devflow` 是 public entry，永远不是合法 runtime next action。
- `devflow-clean-design`、`devflow-clean-code`、编码规范 skill 和领域约束 skill 永远不是合法 runtime next action。
- `next_action_or_recommended_skill` 必须是上文「DevFlow 共同约定 → Canonical 节点清单」中的 canonical runtime node，不能是 `using-devflow`、扩展 skill 或自由文本。
- Legal profiles：`standard` / `component-impact` / `hotfix` / `lightweight`；profile 判定由 `devflow-router` 执行。
- Legal execution modes：`interactive` / `auto`；`auto` 不跳过任何 review / gate / approval / evidence。
- DevFlow 处理 AR / DTS / CHANGE work item；profile 判定与节点路由由 `devflow-router` 执行。
- 项目 `AGENTS.md` 与各 leaf skill 的 hard gates 不能被入口 discovery、编码规范 skill 或领域约束 skill 削弱。

## 支撑参考

| 文件 | 用途 |
|---|---|
| 本 skill「DevFlow 共同约定」章节 | 单一真相源：产物布局 / progress 字段 / handoff 字段 / profile / 节点表 |
| `references/devflow-work-item-readme-template.md` | 通用 work item README 模板（跨 skill 共享） |
| `references/devflow-progress-template.md` | 通用 progress.md 模板（跨 skill 共享） |
| `references/devflow-traceability-template.md` | 通用 traceability.md 模板（跨 skill 共享） |
| `skills/devflow-router/SKILL.md` | 权威 runtime routing、恢复编排与 reviewer dispatch |
| `skills/devflow-clean-design/SKILL.md` | 第三层设计内在质量统筹 skill |
| `skills/devflow-clean-code/SKILL.md` | 第三层编码内在质量统筹 skill |
