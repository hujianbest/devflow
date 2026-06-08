# DevFlow 2.0 设计说明书：从「流程编排」到「流程 + 工程匠艺」

> 本文是一份**指导 DevFlow 从 1.0 完全重写为 2.0 的设计说明书**。
>
> 它先解剖参考对象 [`addyosmani/agent-skills`](https://github.com/addyosmani/agent-skills) 的设计理念与 skill 组织方式（**重点是 `using-agent-skills` 与其他 skills 之间的关系**），再诊断 DevFlow 1.0 的核心缺口——**只有流程约束，缺少「如何做出高质量设计与编码」的指导**——最后给出 DevFlow 2.0 的目标架构、新增的「匠艺（craft）skill 族」、skill 写作规范、迁移路线、风险权衡与验收标准。
>
> 受众：DevFlow skills 的作者 / reviewer / 维护者。
> 状态：设计提案，并据此完成 2.0 重写。

---

## 0. TL;DR（一句话主张）

> **DevFlow 1.0 是一条「合格的流水线」：它规定了 *何时* 做规格、设计、TDD、评审、门禁，并用工件证据保证可恢复与可追溯。但它几乎没有告诉 agent *如何* 把设计做好、把代码写好。DevFlow 2.0 在完整保留这条流水线的工程纪律之上，注入一层 `addyosmani/agent-skills` 式的「工程匠艺」——把资深工程师的判断（简单性、抽象克制、接口契约、测试金字塔、五维审查……）编码为可被流程节点随时调用的 craft peer skills，并把 `using-devflow` 重写为「图书管理员 + 行为宪法」式的轻量 meta-skill。**

参考对象教给我们最关键的一课不是「skill 数量」，而是两点：

1. **meta-skill 与 leaf skills 的关系 = 「发现索引 + 永远生效的行为准则」，而不是「调度中枢 + 强制流水线」。**
2. **skill 的价值在于编码*判断*，而不仅是编码*流程*。** `agent-skills` 的 22 个生命周期 skill 里，真正稀缺的内容是 `incremental-implementation` 的「先问最简实现」、`code-simplification` 的 Chesterton's Fence、`api-and-interface-design` 的 Hyrum's Law、`test-driven-development` 的测试金字塔 / DAMP / 测状态不测交互——这些是 DevFlow 1.0 完全没有的**匠艺**。

DevFlow 2.0 = **DevFlow 的流程护城河（保留） + agent-skills 的工程匠艺（注入） + agent-skills 的 meta↔skills 关系（采纳）**。

---

## 1. 文档目的与范围

### 1.1 目的

1. 提炼 `addyosmani/agent-skills`（研究时 ~4.8 万 star，23 个 skill）的设计理念与 skill 设计方式。
2. **重点说明 `using-agent-skills` 与其他 skills 的关系**，并解释这种关系为何健康。
3. 据此给出可直接驱动 DevFlow 2.0 重写的设计说明书，**核心目标是补齐「高质量设计与编码指导」这一缺口**。

### 1.2 范围

- **在范围内**：skill 体系结构、meta↔leaf 关系、匠艺 skill 族的设计、skill anatomy、约定去重（单一真相源）、匠艺如何编织进流程节点、写作规范、迁移路线。
- **不在范围内**：DevFlow 的业务边界（仍只覆盖「开发」阶段，不接管产品发现 / 系统级独立测试 / 发布运维）；团队角色边界（不替模块架构师 / 开发负责人 / 开发人员拍板）；这两条 soul 级约束在 2.0 中**不变**。

---

## 2. 参考对象解剖：`addyosmani/agent-skills`

### 2.1 总体哲学（来自 README / AGENTS.md / docs/skill-anatomy.md）

| 原则 | 含义 | 对 DevFlow 的启示 |
|---|---|---|
| **Process over prose（流程而非文档）** | skill 是要*执行*的工作流，有步骤、检查点、退出条件 | DevFlow 1.0 已具备，保留 |
| **Encode judgment（编码判断）** | skill 把资深工程师「何时写 spec、测什么、怎么审、何时发」的判断直接编进步骤里 | **DevFlow 1.0 最大缺口**：只编码了流程顺序，没编码工程判断 |
| **Anti-rationalization（反向理由化）** | 每个 skill 内置「偷懒话术 + 反驳」表，阻止 agent 找借口跳步 | DevFlow 1.0 已具备，保留并复用到匠艺 skill |
| **Verification non-negotiable（验证不可协商）** | 每个 skill 以证据收尾，「看起来对」不算完成 | DevFlow 1.0 已具备，保留 |
| **Progressive disclosure（渐进式披露）** | 启动只载入 name+description；完整 SKILL.md 与 references 按需加载 | **DevFlow 1.0 痛点**：约定在 14 个 skill 中重复 |
| **Minimal / token-conscious** | SKILL.md 建议 < 500 行；删掉不改变 agent 行为的内容；引用而非复制 | **DevFlow 1.0 痛点**：大量样板复制 |

### 2.2 三层可组合模型（来自 AGENTS.md「Orchestration」）

`agent-skills` 区分三个**可组合但职责不同**的层：

| 层 | 位置 | 回答 | 性质 |
|---|---|---|---|
| **Skills** | `skills/<name>/SKILL.md` | *How*（怎么做） | 带步骤与退出条件的工作流 |
| **Personas** | `agents/<role>.md` | *Who*（谁来做） | 带视角与输出格式的角色 |
| **Commands** | `.claude/commands/*.md` | *When*（何时做） | 用户面向入口；编排层 |

组合规则：**用户（或斜杠命令）是编排者；persona 不调用其它 persona；persona 可调用 skills。** 唯一被背书的多 persona 编排是「并行 fan-out + merge」（`/ship` 并发跑 code-reviewer / security-auditor / test-engineer 再汇总）。**明确禁止**构造「router persona」去决定调谁。

### 2.3 ⭐ `using-agent-skills` 与其他 skills 的关系（本研究核心）

`using-agent-skills` 是 23 个 skill 中**唯一的 meta-skill**。它与其它 skill 的关系有四个决定性特征：

#### 特征 A：它是「图书管理员 + 行为宪法」，不是「调度中枢」

`using-agent-skills` 只做两件事：

1. **Skill discovery**——一棵**纯建议性**的决策树，把「当前任务」映射到「应该用哪个 skill」（`新项目→spec`、`在写代码→incremental-implementation`、`UI→frontend-ui-engineering`、`高风险/陌生代码→doubt-driven-development`、`出问题→debugging`……）。
2. **Core Operating Behaviors**——一组**跨所有 skill 永远生效**的行为准则：Surface Assumptions（先亮假设）、Manage Confusion（遇矛盾就停）、Push Back（不当 yes-machine）、Enforce Simplicity（主动抗过度设计）、Scope Discipline（外科手术式精确）、Verify Don't Assume（无证据不算完成）。

#### 特征 B：leaf skills 是平等的 peer，可自由组合，无强制流水线

- 明确写「**Multiple skills can apply**」：一个特性可能依次串 `idea-refine → spec → planning → incremental-implementation → TDD → code-review → code-simplification → ship`。
- 立刻补一句「**Not every task needs every skill**」：bug 修复可能只走 `debugging → TDD → code-review`。
- skill 之间**按名字互相引用**（如 TDD 的 "Interaction with Other Skills" 节直接点名 doubt-driven / debugging），**没有任何 leaf 把控制权交还 meta 再分流**。

#### 特征 C：meta-skill 不持有运行时状态，不做权威裁决

它不维护 stage、不维护 handoff 字段、不"消费 verdict"。它只在会话开始或意图不清时帮 agent **选对入口**，然后退出。运行时编排由「用户 + 命令 + 各 skill 自身步骤」承担。

#### 特征 D：通过 session-start hook「常驻注入」

`hooks/session-start.sh` 把 meta-skill 内容注入每个新会话的系统提示。**meta-skill 是「默认底色」，leaf skills 是「按需点亮」**——这是 progressive disclosure 在入口层的体现。

> **小结（关系本质）**：meta-skill = 「一张索引图 + 一套永远生效的行为宪法」；leaf skills = 「一组可独立安装、可自由组合、按名字互引的工作流」。两者是**发现关系 + 共同准则关系**，而**不是调度关系 / 权威关系 / 流水线关系**。

### 2.4 ⭐ 匠艺 skill 怎么编码「判断」（本研究的第二核心）

这是 DevFlow 最该学的部分。随手举几例：

- **`incremental-implementation` / Rule 0 Simplicity First**：写码前问「最简实现是什么？」；写完后问「能更少行吗？这些抽象配得上复杂度吗？Staff 工程师会不会说『为什么不直接……』？」——并给出 `✗ 通用 EventBus + 中间件管线 / ✓ 一次函数调用` 这种具体反例。
- **`code-simplification`**：Chesterton's Fence（不懂的栅栏先别拆）、Rule of 500、保持行为不变地降复杂度。
- **`api-and-interface-design`**：契约先行、Hyrum's Law（一切可观测行为都会被依赖）、One-Version Rule、错误语义、边界校验。
- **`test-driven-development`**：测试金字塔（80/15/5）、test sizes、DAMP over DRY、**测状态不测交互**、mock 克制（real>fake>stub>mock）、AAA、Beyonce Rule。
- **`code-review-and-quality`**：五维审查（正确性 / 可读性 / 架构 / 安全 / 性能）、change sizing（~100 行）、severity 标签（Nit/Optional/FYI）。
- **`doubt-driven-development`**：对每个非平凡决策做「新上下文 + 对抗式」复核（CLAIM→EXTRACT→DOUBT→RECONCILE→STOP）。

**关键观察**：这些 skill 不是「填模板」式的流程，而是「教你怎么想」的匠艺——它们携带**命名原则 + 具体可判别的 tell（坏味道信号） + 反例**。DevFlow 1.0 的设计 / 编码 skill 恰恰停留在「填这些章节 + 回指 requirement」的*结构*层，没有这层*判断*。

### 2.5 Skill Anatomy（写作规范）

```
SKILL.md
├── Frontmatter: name（kebab-case，与目录同名） + description（"做什么" + "Use when…" 触发条件）
├── Overview            → 一两句电梯陈述
├── When to Use         → 正向触发 + When NOT to use
├── Process / How       → 编号步骤，含代码示例 / ASCII 决策图 / 具体反例
├── Common Rationalizations → 偷懒话术 + 反驳（最具辨识度）
├── Red Flags           → 违反信号
└── Verification        → 带证据的退出清单
```

写作原则：process over knowledge、specific over general、evidence over assumption、anti-rationalization、progressive disclosure、token-conscious。

---

## 3. DevFlow 1.0 现状诊断

### 3.1 必须保留的真正价值（DevFlow 护城河，agent-skills 没有）

1. **工件优先恢复（Evidence over memory）**：下一步从 `features/<id>/progress.md`、`reviews/`、`evidence/`、`completion.md` 恢复，而非聊天记忆。
2. **角色分离评审（No self-verification）**：作者不审自己；reviewer 作为独立 subagent 给 verdict 且不改生产代码。
3. **门禁化 TDD（Gated TDD）**：fail-first 证据；「跑通」≠「有效」，需独立 test-review。
4. **需求到代码可追溯**：AR/DTS/CHANGE 工作项追溯链；长期资产 closeout 提升。
5. **运行时证据路由**：`devflow-router` 把工件证据转成唯一下一步、profile 判定、reviewer 派发——这是 agent-skills 没有的「可恢复编排」能力。
6. **嵌入式 C/C++ 风险维度**：内存 / 并发 / 实时性 / 资源 / ABI 的 reviewer rubric。

### 3.2 ⭐ 核心缺口：只有流程，没有匠艺（2.0 主攻方向）

| # | 缺口 | 现状证据 | 后果 |
|---|---|---|---|
| **G1** | **设计 skill 只教「填章节」，不教「怎么设计好」** | `devflow-ar-design` / `devflow-component-design` 的「方法原则」列了 SOLID / GRASP / Clean Architecture 等**名词**，但工作流只要求「按模板填章节 + 回指 requirement + 列 Design Options」。没有「如何判断抽象是否过度」「接口契约怎么定」「何时该拒绝复杂度」的可执行判断 | agent 产出*结构完整但设计平庸*的文档：章节齐全、却可能过度设计、接口泄漏、抽象错配 |
| **G2** | **TDD skill 只教「RED/GREEN/REFACTOR 纪律 + 证据」，不教「怎么写好测试 / 好代码」** | `devflow-tdd-implementation` 严格管控 fail-first 证据、单 active task、Two Hats，但**没有**测试金字塔、DAMP over DRY、测状态不测交互、mock 克制、简单性优先（Rule 0）、薄垂直切片、命名 / 可读性 | agent 写出*通过但脆弱*的测试（测交互、过度 mock）和*能跑但复杂*的实现 |
| **G3** | **code-review 只有「嵌入式风险 rubric」，缺通用工程审查判断** | `devflow-code-review` 的 8 维度偏嵌入式（内存 / 并发 / 实时性 / ABI），可读性 / 简单性 / 抽象层级 / change sizing / 死代码等通用质量轴较弱 | 审查抓得住「会崩」，抓不住「写得烂」 |
| **G4** | **缺「对抗式自我复核」机制** | 1.0 靠独立 reviewer subagent 兜底，但作者节点在产出前没有「先自我对抗一遍非平凡决策」的匠艺 | 把本可在飞行中廉价纠正的错误，拖到 review 才发现 |
| P5 | 约定在 14 个 skill 中重复 | 每个 SKILL.md 末尾重复「本地 DevFlow 约定」（产物布局 / progress 字段 / handoff 字段，约 65 行/个） | 违反 progressive disclosure；改一处要改 14 处 |
| P6 | 双入口语义易混 | `using-devflow` 与 `devflow-router` 职责需更清晰地区分「发现」与「运行时路由」 | 维护者与 agent 易混淆 meta 与 router |

> 诊断结论：**DevFlow 1.0 的流程纪律优秀，但它把 agent 训练成了「守规矩的流程执行者」，而不是「有判断力的资深工程师」。2.0 的任务是在不丢纪律的前提下，注入这层判断力。**

---

## 4. DevFlow 2.0 设计原则

1. **流程纪律零让步（Discipline preserved）**：§3.1 的六条护城河 + soul 边界完全保留。
2. **注入匠艺层（Craft injected）**：新增一组 **craft peer skills**，把 agent-skills 式的工程判断（简单性、抽象克制、接口契约、测试金字塔、五维审查、对抗式复核）编码为可被流程节点随时调用的 skill。
3. **匠艺是「质量透镜」而非「新流程阶段」**：craft skills **不进** `progress.md` 的 `Current Stage`、**不进** handoff 的 `next_action_or_recommended_skill`、**不产生** review verdict。它们是流程节点在 `ar-design` / `tdd-implementation` / `code-review` 等阶段**内部调用的透镜**，提升产物质量，不改变流程拓扑。
4. **meta↔leaf 关系采纳 agent-skills 模型**：`using-devflow` = 「发现树 + 行为宪法」；leaf 是按名互引的 peer；`devflow-router` 是**运行时证据路由权威**（保留，DevFlow 独有），与 meta-skill 的「发现」职责清晰分离。
5. **单一真相源（Single source of truth）**：路径布局 / progress 字段 / handoff 字段 / profile / canonical 节点只在 `using-devflow` 的「DevFlow 共同约定」章节（+ 项目 `AGENTS.md` 覆盖点）定义一次，所有 skill 引用而不复制。把约定收进 meta-skill 而非独立文件，是因为 `using-devflow` 本就是「发现 + 行为宪法」的入口，共同约定与行为宪法同处一地、随入口一起加载，最自然。
6. **节点名与字段稳定（Backward compatible）**：13 个 canonical 工作节点名、`progress.md`/handoff 字段保持稳定，兼容存量 `features/<id>/` 工件。craft skills 是**新增的非 canonical 透镜**，不占用 canonical 节点名空间。
7. **渐进披露 + 可移植**：纯 Markdown；单个 `SKILL.md` 目标 < 280 行；匠艺判断用表格 / 决策树 / 反例承载，便于跨工具稳定执行。

---

## 5. DevFlow 2.0 目标架构

### 5.1 分层模型

```
┌──────────────────────────────────────────────────────────────┐
│ Commands（When）  commands/*.md                                │
│   /devflow /devflow-specify /devflow-design /devflow-build     │
│   /devflow-ship /devflow-fix   —— 用户面向入口，bias 非 authority │
├──────────────────────────────────────────────────────────────┤
│ Meta（发现 + 宪法 + 共同约定）  skills/using-devflow/SKILL.md  │
│   ① 发现树：意图 → leaf skill（含「写设计 / 写码 / 写测试时叠加  │
│      哪个 craft 透镜」）                                          │
│   ② DevFlow 行为宪法（Core Operating Behaviors）               │
│   ③ meta / router / craft 三者关系说明                          │
│   ④ DevFlow 共同约定（单一真相源：布局 / 字段 / profile / 节点） │
├──────────────────────────────────────────────────────────────┤
│ Runtime Router（Where-next）  skills/devflow-router/SKILL.md   │
│   工件证据 → 唯一 canonical 下一步 + profile + reviewer 派发    │
│   （DevFlow 独有的可恢复编排权威；与「发现」分离）              │
├──────────────────────────────────────────────────────────────┤
│ Flow Skills（How / 流程节点 = canonical 节点）                  │
│   specify · spec-review · component-design(-review) ·          │
│   ar-design(-review) · tdd-implementation · test-review ·      │
│   code-review · completion-gate · finalize · problem-fix       │
│   —— 每个节点在其工作流内部「叠加」相关 craft 透镜              │
├──────────────────────────────────────────────────────────────┤
│ ⭐ Craft Skills（质量透镜 / 非 canonical / 可自由组合 peer）     │
│   devflow-design-craft  —— 怎么把设计做好                       │
│   devflow-coding-craft  —— 怎么把代码写好                       │
│   devflow-test-craft    —— 怎么把测试写好                       │
├──────────────────────────────────────────────────────────────┤
│ Personas（Who）  agents/*.md                                    │
│   devflow-reviewer / devflow-implementer                       │
├──────────────────────────────────────────────────────────────┤
│ Conventions（单一真相源）  并入 using-devflow「DevFlow 共同约定」 │
│   产物布局 / progress 字段 / handoff 字段 / profile / 节点表    │
└──────────────────────────────────────────────────────────────┘
```

### 5.2 ⭐ 新增匠艺 skill 族（2.0 的心脏）

三个 craft skills 把 agent-skills 的工程判断本地化到 DevFlow 的「嵌入式 C/C++ + 工件优先 + 角色分离」语境：

#### `devflow-design-craft`（怎么把设计做好）

把 1.0 设计 skill 里只是*列名词*的 SOLID/GRASP/Clean Architecture，变成*可执行的判断*：

- **Simplicity First / 抗过度设计**：先问「满足当前 requirement 的最简结构是什么？」；给「✗ 为一个通知建带中间件的 EventBus / ✓ 一次函数调用」式具体反例。
- **抽象克制（Rule of Three）**：第三个用例出现前不抽象；接口数量 = 真实调用者数量。
- **接口契约（Hyrum's Law / 错误语义 / 边界校验）**：一切可观测行为都会被依赖；显式定义错误码 / 并发约束 / 兼容策略；在组件边界校验输入。
- **SOLID/GRASP 的可判别 tell**：如「一个类有两个变更理由 → SRP 违例」「依赖具体而非抽象 → DIP 违例」。
- **嵌入式防御性设计**：内存 / 生命周期 / 并发 / 实时性 / 资源释放 / ABI 作为一等设计约束。
- **Design Options 的质量标准**：方案对比要量化取舍，不能只有一个伪装的「Single obvious option」。

被 `devflow-ar-design`、`devflow-component-design` 在「方案选择」「起草设计」步骤内部调用。

#### `devflow-coding-craft`（怎么把代码写好）

- **薄垂直切片**：一次实现一条完整路径，每片可测、保持可编译、可回退。
- **Simplicity First（Rule 0）**：写完自检「能更少行吗 / 抽象配得上复杂度吗 / Staff 工程师会怎么说」。
- **Scope Discipline**：外科手术式精确；「路过看到的问题」登记不顺手改。
- **可读性 / 命名**：拒绝 `temp`/`data`/`result`；控制流直白；避免嵌套三元 / 深回调。
- **防御性编码**：安全默认、资源配对释放、错误路径不只走 happy path。

被 `devflow-tdd-implementation` 在 GREEN / REFACTOR 步骤内部调用（与 Two Hats 纪律协同）。

#### `devflow-test-craft`（怎么把测试写好）

- **测试金字塔（80/15/5）+ test sizes（small/medium/large）**。
- **测状态不测交互**：断言结果而非「调用了哪个方法」，refactor 不应让行为不变的测试变红。
- **DAMP over DRY**：测试可读性 > 去重；每个用例自成一个规格。
- **Mock 克制**：real > fake > stub > mock；只在边界（慢 / 不确定 / 有副作用）才 mock。
- **AAA + 一断言一概念 + 描述性命名**。
- **嵌入式补充**：把上述与 DevFlow 的 fail-first 证据、嵌入式风险覆盖矩阵协同。

被 `devflow-tdd-implementation`（落测试时）与 `devflow-test-review`（审有效性时）调用。

> **为什么是「透镜」而不是「流程阶段」**：DevFlow 的护城河是可恢复 / 可追溯的流程拓扑。如果把匠艺做成新的 canonical 节点，会破坏现有工件字段与路由表，且强制每个工作项都过一遍、违反「not every task needs every skill」。做成**透镜**则两全：流程拓扑不变、字段兼容，同时每个产出阶段都被匠艺判断「点亮」。

### 5.3 `using-devflow` 2.0 的重新定位

从「前置控制器」改为「图书管理员 + 行为宪法」：

- **保留**：DevFlow 1.0 已有的「核心运行行为」九条（工件优先、显式假设、管理困惑、提出反对、强制简单、范围纪律、验证不假设、角色隔离、不替团队拍板）——这恰好就是 agent-skills 的 Core Operating Behaviors，DevFlow 早已译入，2.0 保留并明确为「行为宪法」。
- **新增**：发现树里加入「**写设计 / 写码 / 写测试时叠加哪个 craft 透镜**」的指引。
- **强化**：清晰说明 **meta（发现） / router（运行时路由） / craft（质量透镜）** 三者关系，杜绝混淆。
- **不变约束**：`using-devflow` 永远不写入任何 `next_action_or_recommended_skill`；craft skills 同样不写入（它们是透镜，不是 canonical 节点）。

### 5.4 约定去重：单一真相源

在 `using-devflow` 内新增「DevFlow 共同约定」章节，集中定义：产物布局、`progress.md` canonical 字段、handoff 字段、合法 profile 集合与升级规则、合法 execution mode 与归一化顺序、canonical 节点清单、Read-on-presence 与 Promotion 规则。约定与「发现树 + 行为宪法」同处入口 meta-skill，不单独建文件。

各 skill 末尾的「本地 DevFlow 约定」大段样板**整段删除**，替换为一行引用：

```markdown
## DevFlow 约定
本 skill 遵循 `using-devflow` 的「DevFlow 共同约定」章节（产物布局 / progress 字段 / handoff 字段 / profile / 节点表）；项目 `AGENTS.md` 可覆盖等价路径与模板。
```

skill-specific 的内容（如某节点的 review record 路径）以一两行保留在该 skill 内。预计每个 skill 因此瘦身 ~55–65 行。

### 5.5 工件模型与角色分离（保留）

- `features/<id>/`、`docs/ar-specs`、`docs/ar-designs`、`docs/component-design.md` 全部保留；closed work item 不归档。
- reviewer 仍是独立 subagent、不改生产代码；implementer 仍只由 `devflow-tdd-implementation` 派发；作者不自审——全部不变。

---

## 6. Skill 写作规范 2.0（DevFlow Skill Anatomy）

### 6.1 Flow / 流程节点 skill 模板（目标 < 280 行）

```markdown
---
name: devflow-<node>
description: <"做什么"> + <"Use when …" 触发> + <"Not for …" 反向排除>
---

# DevFlow <Node>
## 总览            # 一两句：本 skill 把哪个 object 转成哪个 object
## 适用场景        # 正向触发 + 不适用
## 硬性门禁        # 开工前 / 收口前的不可协商门禁
## 工作流          # 编号步骤；在相关步骤显式「叠加 craft 透镜」
## 输出契约        # 产物 + 唯一 next canonical node + handoff 字段
## 风险信号 / 反向理由化 / 验证清单
## DevFlow 约定    # 一行引用 using-devflow「DevFlow 共同约定」章节
```

### 6.2 Craft / 质量透镜 skill 模板（目标 < 230 行）

```markdown
---
name: devflow-<x>-craft
description: <"教 agent 如何把<设计/代码/测试>做好"> + <"Use when …">。这是质量透镜，不是流程节点：不写 progress/handoff，不产生 verdict。
---

# DevFlow <X> Craft（质量透镜）
## 总览 / 它不是什么（不改流程拓扑、不进 handoff）
## 何时叠加        # 被哪些 flow 节点、在哪个步骤调用
## 核心判断        # 命名原则 + 可判别 tell + 具体反例（agent-skills 风格）
## 与嵌入式 / DevFlow 纪律的协同
## 反向理由化 / Red Flags / 自检清单（产出更好产物，但不替代独立 review）
```

规则：中英混排可保留；**判断用表格 / 决策树 / 反例承载**；不在 skill 间复制内容；高风险 skill 保留 `evals/`。

---

## 7. 从 1.0 到 2.0 的重写路线

| 阶段 | 内容 | 完成判据 |
|---|---|---|
| **R0 单一真相源** | 在 `using-devflow` 内新增「DevFlow 共同约定」章节，合并 14 个 skill 的重复约定 | 覆盖所有 1.0 约定项，无信息丢失 |
| **R1 注入匠艺**（核心） | 新建 `devflow-design-craft` / `devflow-coding-craft` / `devflow-test-craft` 三个透镜 skill | 三 skill 携带命名原则 + tell + 反例；< 230 行 |
| **R2 编织匠艺** | `ar-design` / `component-design` / `tdd-implementation` / `code-review` / `test-review` 在工作流相关步骤显式「叠加 craft 透镜」 | 五节点工作流出现对 craft skill 的具名调用 |
| **R3 重写 meta** | `using-devflow` 重写为「发现树 + 行为宪法 + 三层关系」，发现树纳入 craft 透镜 | meta 清晰区分 meta/router/craft；保留行为宪法 |
| **R4 去重瘦身** | 14 个 skill 删除「本地约定」样板，改一行引用 | 单个 SKILL.md < 280 行；约定不再重复 |
| **R5 文档对齐** | README / README.zh-CN / CHANGELOG / commands / agents 反映 2.0 心智模型 | 文档与实现一致 |

> 顺序原则：先 R0（去重基座），再 R1/R2（用户核心诉求：匠艺），再 R3/R4（结构），最后 R5（文档）。每阶段后仓库均处于可用状态。

---

## 8. 风险与权衡

| 风险 | 说明 | 缓解 |
|---|---|---|
| **匠艺 skill 变成「又一份没人读的文档」** | craft 若不被流程节点真正调用就是死文 | 在 5 个 flow 节点工作流里**具名叠加**，并在 `using-devflow` 发现树指明何时叠加 |
| **匠艺与门禁职责混淆** | 担心 craft 变成隐性新门禁 | 明确 craft 是「透镜」：不写 progress/handoff、不产 verdict、不替代独立 review |
| **节点名 / 字段变更破坏存量工件** | 现网 `features/<id>/` 用 1.0 字段 | canonical 节点名与字段**保持稳定**；craft 用新非 canonical 名 |
| **嵌入式语境被通用匠艺稀释** | agent-skills 多为 Web 语境 | craft skill 全部本地化到嵌入式 C/C++ + DevFlow 纪律，保留内存 / 并发 / 实时性维度 |
| **router 与 meta 关系仍被误解** | 1.0 已有双入口 | 在 meta 与文档显式画出「发现 / 运行时路由 / 质量透镜」三分图 |

权衡：
- **取**：工程判断力、可组合质量透镜、约定去重、入口清晰。
- **守**：DevFlow 全部流程纪律、可恢复 / 可追溯、角色分离、soul 边界，零让步。
- **舍**：把匠艺做成独立 canonical 流程阶段（会破坏拓扑与字段）——改用「透镜」实现等价收益而无破坏。

---

## 9. 验收标准（2.0 完成的定义）

1. **匠艺补齐**：存在 `devflow-design-craft` / `devflow-coding-craft` / `devflow-test-craft`，各携带命名原则 + 可判别 tell + 具体反例，且本地化到嵌入式语境。
2. **匠艺被编织**：`ar-design` / `component-design` / `tdd-implementation` / `code-review` / `test-review` 的工作流显式具名调用对应 craft 透镜。
3. **关系清晰**：`using-devflow` 明确区分 meta（发现）/ router（运行时路由）/ craft（质量透镜）三者，且保留行为宪法；craft 与 meta 都不写入 `next_action_or_recommended_skill`。
4. **纪律保留**：工件优先恢复、角色分离评审、门禁化 TDD、可追溯、团队角色边界全部不变。
5. **去重**：约定只在 `using-devflow` 的「DevFlow 共同约定」章节 + `AGENTS.md` 定义；任一 skill 不再出现重复约定样板。
6. **兼容**：13 个 canonical 节点名与 `progress.md`/handoff 字段稳定。
7. **文档一致**：README / README.zh-CN / CHANGELOG / commands / agents 与实现一致并解释三层关系。

---

## 10. 假设与待决问题（Surface Assumptions）

> 遵循行为宪法「先亮出假设」，本设计基于以下假设；任一不成立需回炉。

**假设**：
1. 13 个 canonical 工作节点的职责划分不变可接受；2.0 只**新增匠艺透镜**，不改节点语义。
2. 节点名与 `progress.md`/handoff 字段需保持稳定以兼容存量工件。
3. `devflow-router` 作为运行时证据路由权威保留（DevFlow 独有价值），不照搬 agent-skills「无 router」的去中枢模型——因为 DevFlow 的可恢复 / 可追溯比通用任务更依赖证据路由。
4. soul 三条边界（范围 / 团队角色 / 质量观）不动。

**待决问题（建议团队评审时拍板）**：
1. 是否把 `devflow-test-craft` 与 `devflow-coding-craft` 合并为单一 `devflow-implementation-craft`？本设计选择拆开，因为「测试匠艺」和「代码匠艺」被不同节点（test-review vs code-review）独立消费。
2. 是否进一步抽出 `devflow-debugging-craft` / `devflow-security-craft`？本设计先聚焦设计 / 编码 / 测试三大缺口，安全 / 调试留作 2.1。
3. 是否引入 session-start hook 常驻注入行为宪法（依赖具体工具能力）？

---

## 附录 A：A/B 对照速查

| 维度 | DevFlow 1.0 | DevFlow 2.0 | 取自 agent-skills 的理念 |
|---|---|---|---|
| 入口 | `using-devflow` + `devflow-router` 职责需厘清 | meta（发现 + 宪法）/ router（运行时路由）三层清晰 | `using-agent-skills` = 图书管理员 + 宪法 |
| 设计指导 | 列 SOLID/GRASP 名词 + 填模板 | **`devflow-design-craft` 透镜：可执行判断 + tell + 反例** | `api-and-interface-design` / `code-simplification` |
| 编码指导 | 只有 RED/GREEN/REFACTOR 纪律 | **`devflow-coding-craft` 透镜：简单优先 / 薄切片 / 可读性** | `incremental-implementation` Rule 0 |
| 测试指导 | 只有 fail-first 证据 | **`devflow-test-craft` 透镜：金字塔 / DAMP / 测状态不测交互 / mock 克制** | `test-driven-development` |
| skill 关系 | FSM 节点 | 节点 + 可自由叠加的 craft peer | 「multiple skills can apply」 |
| 约定 | 14 份重复样板 | 单一真相源 | 「不复制，引用」 |
| 工程纪律 | 优秀 | **完全保留** | DevFlow 自有护城河 |

## 附录 B：参考来源

- `addyosmani/agent-skills`：`README.md`、`AGENTS.md`、`skills/using-agent-skills/SKILL.md`、`skills/spec-driven-development/SKILL.md`、`skills/incremental-implementation/SKILL.md`、`skills/test-driven-development/SKILL.md`、`skills/code-review-and-quality/SKILL.md`、`skills/doubt-driven-development/SKILL.md`、`skills/planning-and-task-breakdown/SKILL.md`。
- DevFlow 1.0：`README.md`、`skills/using-devflow/SKILL.md`、`skills/devflow-router/SKILL.md`、`skills/devflow-ar-design/SKILL.md`、`skills/devflow-component-design/SKILL.md`、`skills/devflow-tdd-implementation/SKILL.md`、`skills/devflow-code-review/SKILL.md`。
