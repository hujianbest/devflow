# DevFlow 2.0 设计说明书

> 本文是一份**指导 DevFlow 从 1.0 完全重写为 2.0 的设计说明书**。它先解剖参考对象 [`addyosmani/agent-skills`](https://github.com/addyosmani/agent-skills) 的设计理念与 skill 组织方式（尤其是 `using-agent-skills` 与其他 skills 之间的关系），再诊断 DevFlow 1.0 的结构性问题，最后给出 DevFlow 2.0 的目标架构、skill 写作规范、迁移路线、风险权衡与验收标准。
>
> 受众：DevFlow skills 的作者 / reviewer / 维护者。
> 定位：与 `docs/principles/` 同属「宪法 / 设计指导层」，不被运行时 skill 加载。
> 状态：设计提案（design proposal），等待团队评审后据此重写。

---

## 0. TL;DR（一句话主张）

> **把 DevFlow 从「以 `devflow-router` 为中心的刚性有限状态机（FSM）」重写为「一组可独立调用、可自由组合的 peer skills + 一个轻量 meta-skill（`using-devflow`）」，用「分布式门禁 + 证据自路由」替代「集中式运行时权威」，同时完整保留 DevFlow 真正的工程价值：工件优先恢复、角色分离评审、门禁化 TDD、需求到代码的可追溯。**

参考对象 `agent-skills` 教给我们的核心一课不是「加多少 skill」，而是 **meta-skill 与 leaf skills 的关系应该是「图书管理员 + 共同行为准则」，而不是「调度中枢 + 强制流水线」**。DevFlow 2.0 应继承这种关系，但保留 DevFlow 在「高可靠工程纪律」上的硬约束。

---

## 1. 文档目的与范围

### 1.1 目的

1. 提炼 `addyosmani/agent-skills`（截至研究时 ~4.8 万 star，23 个 skill）的设计理念与 skill 设计方式。
2. **重点说明 `using-agent-skills` 与其他 skills 的关系**，并解释为什么这种关系比 DevFlow 1.0 的 `using-devflow` + `devflow-router` 双头入口更健康。
3. 据此给出一份可直接驱动 DevFlow 2.0 完全重写的设计说明书。

### 1.2 范围

- **在范围内**：skill 体系结构、入口/路由机制、skill anatomy、约定的去重与下沉、工件模型、角色分离与 subagent 模型、profile 处理、多工具可移植性、迁移路线。
- **不在范围内**：DevFlow 的业务边界（仍只覆盖「开发」阶段，不接管产品发现 / 系统级独立测试 / 发布运维），这条 soul 级约束在 2.0 中**不变**（见 `docs/principles/00 soul.md`）。

---

## 2. 参考对象解剖：`addyosmani/agent-skills` 的设计理念

### 2.1 总体哲学（来自 README / docs/skill-anatomy.md）

| 原则 | 含义 | 对 DevFlow 的启示 |
|---|---|---|
| **Process over prose（流程而非文档）** | skill 是 agent 要*执行*的工作流，不是要*阅读*的参考文档；每个 skill 有步骤、检查点、退出条件 | DevFlow 已具备，需保留 |
| **Anti-rationalization（反向理由化）** | 每个 skill 内置「偷懒话术 + 反驳」表，阻止 agent 给自己找借口跳步 | DevFlow 已具备，需保留并去重 |
| **Verification is non-negotiable（验证不可协商）** | 每个 skill 以证据（测试通过、构建输出、运行时数据）结尾，"看起来对"不算完成 | DevFlow 已具备，需保留 |
| **Progressive disclosure（渐进式披露）** | 启动时只加载 skill 的 `name` + `description`；完整 `SKILL.md` 仅在 agent 判断相关时才载入；支撑文件按需加载 | **DevFlow 1.0 的痛点**：约定在 14 个 skill 中重复，违反渐进披露 |
| **Minimal / token-conscious（最小化）** | `SKILL.md` 建议 < 500 行；删掉不改变 agent 行为的内容；引用而非复制 | **DevFlow 1.0 的痛点**：每个 skill 270–366 行，且大量样板重复 |
| **Specific over general（具体优于笼统）** | "运行 `npm test` 并确认通过" 优于 "确保测试可用" | 两者都做得不错 |

### 2.2 三层可组合模型（来自 AGENTS.md「Orchestration」节）

`agent-skills` 明确区分三个**可组合但职责不同**的层：

| 层 | 文件位置 | 回答的问题 | 性质 |
|---|---|---|---|
| **Skills** | `skills/<name>/SKILL.md` | *How*（怎么做） | 带步骤与退出条件的工作流；意图命中时是「强制跳点」 |
| **Personas（角色）** | `agents/<role>.md` | *Who*（谁来做） | 带视角与输出格式的角色（如 code-reviewer / security-auditor） |
| **Commands（斜杠命令）** | `.claude/commands/*.md` | *When*（何时做） | 用户面向的入口；编排层 |

**组合规则（关键）**：

> **用户（或斜杠命令）是编排者（orchestrator）。Persona 不调用其它 Persona。Persona 可以调用 Skills。**

唯一被官方背书的多 persona 编排是 **「并行 fan-out + merge」**——`/ship` 并发跑 `code-reviewer` / `security-auditor` / `test-engineer` 三个独立角色再汇总。**明确禁止**构造一个「router persona」去决定调用哪个其它 persona——「那是斜杠命令和意图映射的职责」。

> ⭐ 这一条直接命中 DevFlow 1.0 的核心问题：DevFlow 1.0 恰恰构造了一个 `devflow-router` 作为「决定调谁」的运行时权威。`agent-skills` 的设计哲学认为这种中枢是反模式。

### 2.3 `using-agent-skills` 与其他 skills 的关系（本研究的核心）

`using-agent-skills` 是 23 个 skill 中**唯一的 meta-skill**，其余 22 个是「生命周期 skill」。它与其它 skill 的关系有四个决定性特征：

#### 特征 A：它是「图书管理员」，不是「调度中枢」

`using-agent-skills` 只做两件事：

1. **Skill discovery（技能发现）**——一棵**纯建议性**的决策树，把「当前任务」映射到「应该用哪个 skill」：

   ```
   Task arrives
       ├── 还不知道要什么？ ─────────→ interview-me
       ├── 有粗略概念、要变体？ ──────→ idea-refine
       ├── 新项目/特性/变更？ ────────→ spec-driven-development
       ├── 有 spec、要拆任务？ ───────→ planning-and-task-breakdown
       ├── 在写代码？ ────────────────→ incremental-implementation
       │   ├── UI？ ──────────────────→ frontend-ui-engineering
       │   ├── API？ ─────────────────→ api-and-interface-design
       │   └── 高风险/陌生代码？ ──────→ doubt-driven-development
       ├── 在写/跑测试？ ─────────────→ test-driven-development
       ├── 出问题了？ ───────────────→ debugging-and-error-recovery
       └── ...（其余生命周期）
   ```

2. **Core Operating Behaviors（共同行为准则）**——一组**跨所有 skill 永远生效**的行为约束，与发现树平行存在：
   1. Surface Assumptions（先亮出假设，别默默填空）
   2. Manage Confusion Actively（遇到矛盾就停下并发问，不带着猜测往前冲）
   3. Push Back When Warranted（不当 yes-machine，发现问题要量化指出并给替代方案）
   4. Enforce Simplicity（主动抵制过度设计）
   5. Maintain Scope Discipline（外科手术式精确，不顺手重构无关代码）
   6. Verify, Don't Assume（每个 skill 都有验证步，无证据不算完成）

#### 特征 B：leaf skills 之间是**平等的 peer**，可自由组合，没有强制流水线

- `using-agent-skills` 明确写：「**Multiple skills can apply**」——一个特性实现可能依次串起 `idea-refine → spec-driven-development → planning-and-task-breakdown → incremental-implementation → test-driven-development → code-review-and-quality → ...`。
- 它给出的「Lifecycle Sequence」是一个**典型样例**，并立刻补一句：「**Not every task needs every skill**」——bug 修复可能只走 `debugging-and-error-recovery → test-driven-development → code-review-and-quality`。
- skill 之间**按名字互相引用**（"Follow the `test-driven-development` skill"、"use the `debugging-and-error-recovery` skill"），而不是经过一个中央路由器转发。**没有任何 leaf skill 把控制权交还给 `using-agent-skills` 再分流**。

#### 特征 C：`using-agent-skills` 不持有运行时状态，不做权威裁决

它不维护 profile、不维护 stage、不维护 handoff 字段、不"消费 verdict"。它只是在会话开始或意图不清时帮 agent **选对入口**，然后退出。运行时编排由「用户 + 斜杠命令 + 各 skill 自身的步骤」承担。

#### 特征 D：通过 session-start hook 被「常驻注入」

`hooks/session-start.sh` 在每个新 Claude Code 会话里把 `using-agent-skills` 的内容注入系统提示（`CONTRIBUTING.md` 有对应回归测试）。也就是说：**meta-skill 是"默认底色"，leaf skills 是"按需点亮"**。这正是 progressive disclosure 在入口层的体现。

> **小结（using-agent-skills ↔ 其他 skills 的关系）**：
> meta-skill = 「一张索引图 + 一套永远生效的行为准则」；leaf skills = 「一组可独立安装、可自由组合、按名字互引的工作流」。两者是**发现关系 + 共同准则关系**，而**不是调度关系 / 权威关系 / 流水线关系**。

### 2.4 Skill Anatomy（来自 docs/skill-anatomy.md）

```
SKILL.md
├── Frontmatter（必需）: name（kebab-case，与目录同名） + description（先"做什么"，后"Use when"触发条件，≤1024 字符）
├── Overview          → 一两句电梯陈述
├── When to Use       → 正向触发 + 反向排除（When NOT to use）
├── Core Process      → 编号步骤 / 阶段，含代码示例与 ASCII 决策图
├── Common Rationalizations → 偷懒话术 + 反驳（最具辨识度的部分）
├── Red Flags         → 违反 skill 的可观察信号
└── Verification      → 带证据要求的退出清单
```

写作原则（6 条）：process over knowledge、specific over general、evidence over assumption、anti-rationalization、progressive disclosure、token-conscious。

补充结构约定：
- 支撑材料放**项目根的 `references/`**，不放进 skill 目录；只有超过 ~100 行才拆文件。
- 不在 skill 之间复制内容——**引用并链接**。
- `scripts/` 仅在 skill 真的带可执行脚本时才建，不为对齐而建空目录。

### 2.5 多工具可移植性

`agent-skills` 是纯 Markdown，宣称可用于 Claude Code / Cursor / Gemini CLI / OpenCode / Copilot / Kiro / Codex。它为每个工具提供 `docs/<tool>-setup.md`，并用 `.claude/`、`.gemini/`、`agents/`、`hooks/` 等做工具适配。**核心资产（skills/）与工具适配层解耦。**

---

## 3. DevFlow 1.0 现状诊断

### 3.1 必须保留的真正价值（DevFlow 的护城河）

这些是 `agent-skills` **没有**而 DevFlow **有**的硬核工程纪律，2.0 必须完整继承：

1. **工件优先恢复（Evidence over memory）**：下一步从 `features/<id>/progress.md`、`reviews/`、`evidence/`、`completion.md` 恢复，而非聊天记忆。
2. **角色分离评审（No self-verification）**：作者节点不评审自己；reviewer 作为独立 subagent 给 verdict 且不改生产代码。
3. **门禁化 TDD（Gated TDD）**：RED→GREEN→REFACTOR 的 fail-first 证据；测试"跑通"≠测试"有效"，需独立 test-review。
4. **需求到代码可追溯**：SR/AR/DTS/CHANGE 工作项的追溯链、长期资产（`docs/ar-specs`、`docs/ar-designs`、`docs/component-design.md`）的 closeout 提升。
5. **团队角色边界（soul）**：DevFlow 不替模块架构师/开发负责人/开发人员拍板。
6. **嵌入式 C/C++ 风险维度**：内存/并发/实时性/资源/ABI 的 reviewer rubric。

### 3.2 结构性问题（2.0 要解决的）

| # | 问题 | 现状证据 | 与参考理念的冲突 |
|---|---|---|---|
| P1 | **双头入口冗余** | `using-devflow`（272 行）与 `devflow-router`（326 行）都在做意图分类；`using-devflow` 几乎总是把控制权转交 router | `agent-skills` 只有一个轻量 meta-skill；DevFlow 把入口做成了两个重型组件 |
| P2 | **中心化 FSM 脆弱且高耦合** | `devflow-router` 是「profile + execution mode + canonical 节点 + reviewer 派发 + gate 恢复」的唯一运行时权威；所有转移都过它 | `agent-skills` 明确禁止「router persona」；编排应由命令 + 意图映射 + skill 自身承担 |
| P3 | **约定在 14 个 skill 中重复** | 每个 `SKILL.md` 末尾都重复「本地 DevFlow 约定」：产物布局、progress 字段、handoff 字段、canonical 节点列表（约 80–110 行/个 × 14） | 严重违反 progressive disclosure / token-conscious / 「不复制，引用」 |
| P4 | **skill 体量偏大** | 14 个 skill 共 4087 行，单个 259–366 行，含大量样板 | 违反「< 500 行 + 删掉不改变行为的内容」；实际有效内容被样板稀释 |
| P5 | **skill 不可独立组合** | leaf 都是 FSM 上的「节点」，必须经 router 串联；无法像 `agent-skills` 那样按名字自由互引、独立调用 | 与「multiple skills can apply / peer 关系」相悖 |
| P6 | **单工具（OpenCode-only）** | README 明确 v1.0 仅 OpenCode | `agent-skills` 是多工具纯 Markdown |
| P7 | **入口/路由用大段中文叙述承载硬规则** | 硬门禁散落在 router 的中文工作流里，难以被其它工具/agent 稳定执行 | 参考用紧凑表格 + 决策树承载规则 |

> 诊断结论：DevFlow 1.0 的**工程纪律是优秀的，但组织方式是「重型中枢 + 样板复制」**。2.0 的任务是**在不丢纪律的前提下，把组织方式换成「轻量 meta + 可组合 peer + 单一真相源约定」**。

---

## 4. DevFlow 2.0 设计原则

融合两边，确立 8 条 2.0 设计原则：

1. **轻入口（Thin meta entry）**：`using-devflow` 退化为「发现树 + 共同行为准则」，不再做权威路由（吸收 `using-agent-skills`）。
2. **去中枢化路由（Decentralized routing）**：取消「router 作为唯一权威」的模型；改为**分布式门禁 + 证据自路由**——每个 skill 在自己的 `Entry Gate` 自查上游证据，在 `Exit Handoff` 声明唯一合法 next skill（吸收 peer 互引）。
3. **门禁内嵌于 skill（Gates live in skills）**：硬门禁（如「无测试设计章节不得进 TDD」）写进**相关 skill 自身的 Entry Gate**，而不是集中在 router。门禁不可被 `auto` 模式豁免。
4. **单一真相源约定（Single source of truth for conventions）**：路径布局 / progress 字段 / handoff 字段 / canonical 节点 / profile 集合**只在一处定义**（`AGENTS.md` + 一个 `references/devflow-conventions.md`），所有 skill 引用而不复制（吸收「不复制，引用」+ progressive disclosure）。
5. **证据优先恢复（保留）**：恢复仍只读磁盘工件，不读聊天记忆。
6. **角色分离 + 受控 subagent（保留）**：评审仍是独立 subagent；但「谁能派发 reviewer」从「只有 router」放宽为「**编排者（用户/命令/会话控制器）按 fan-out+merge 模式派发**」，与 `agent-skills` 的 `/ship` 模式对齐。
7. **可移植 + 渐进披露（Portable & progressive）**：纯 Markdown，单个 `SKILL.md` 目标 < 250 行；工具适配在 `AGENTS.md`/`commands/`/`agents/`/`hooks/` 层。
8. **soul 不变（Boundary preserved）**：范围、团队角色边界、质量观三条 soul 级约束完全不动。

---

## 5. DevFlow 2.0 目标架构

### 5.1 分层模型（对齐 agent-skills 三层）

```
┌────────────────────────────────────────────────────────────┐
│ Commands（When）  commands/*.md                              │
│   /devflow /devflow-specify /devflow-design /devflow-build   │
│   /devflow-ship /devflow-fix   —— 用户面向入口，bias 非 authority│
├────────────────────────────────────────────────────────────┤
│ Meta（索引 + 准则）  skills/using-devflow/SKILL.md           │
│   ① 发现树：意图 → leaf skill                                │
│   ② DevFlow 共同行为准则（evidence-first / no self-verify /  │
│      gate-respect / scope discipline / surface assumptions） │
│   ③ 会话开始可由 hook 注入（多工具）                          │
├────────────────────────────────────────────────────────────┤
│ Skills（How）  skills/devflow-*/SKILL.md   —— 可独立调用的 peer │
│   每个 skill 自带：Entry Gate（查上游证据）+ Core Process +   │
│   Exit Handoff（声明唯一合法 next skill）                     │
├────────────────────────────────────────────────────────────┤
│ Personas（Who）  agents/*.md                                 │
│   devflow-reviewer / devflow-implementer（已存在）+          │
│   按需的 spec/design/test/code reviewer 视角                  │
├────────────────────────────────────────────────────────────┤
│ Conventions（单一真相源）  references/devflow-conventions.md  │
│   路径布局 / progress 字段 / handoff 字段 / profile / 节点表  │
└────────────────────────────────────────────────────────────┘
```

### 5.2 `using-devflow` 2.0 的重新定位

**从「前置控制器（front controller）」改为「图书管理员 + 准则」**：

- 删除：`direct invoke vs route-first` 的二分裁决、对 `devflow-router` 的转交、profile/execution-mode 的传递逻辑。
- 保留并强化：
  1. **发现树**：把用户意图映射到唯一 leaf skill（见下表）；映射不出唯一项时，提**一个**最小判别问题（吸收 1.0 的「单事实分流检查点」，这是 1.0 的一个好设计，保留）。
  2. **DevFlow 共同行为准则**（DevFlow 版的 Core Operating Behaviors）：
     - Evidence over memory（决策读工件不读记忆）
     - No self-verification（作者不自审，评审独立）
     - Respect hard gates（门禁不被 auto 豁免）
     - Surface assumptions / manage confusion（亮假设、遇矛盾即停）
     - Team-role boundary（不替团队角色拍板）
     - Scope discipline + simplicity（外科手术式修改）
- `using-devflow` **仍然不得**被写进任何 `next_action_or_recommended_skill`（这条 1.0 约束保留）。

发现树（2.0 简化版）：

```
进入 DevFlow
  ├── 不确定从哪进 / 只说"继续推进" ──→ 先读 features/<id>/progress.md 的
  │     Current Stage + Next Action，按工件恢复到对应 leaf（证据自路由）
  ├── 澄清 SR/子系统需求 ──────────→ devflow-specify (profile=requirement-analysis)
  ├── 澄清 AR 规格 ────────────────→ devflow-specify (实现 profile)
  ├── 写/改组件实现设计 ───────────→ devflow-component-design
  ├── 写/改 AR 实现设计(含测试设计) ─→ devflow-ar-design
  ├── TDD 实现/改代码 ─────────────→ devflow-tdd-implementation
  ├── 紧急缺陷/hotfix 复现根因 ─────→ devflow-problem-fix
  ├── 要评审(规格/设计/测试/代码) ──→ 对应 devflow-*-review（由编排者按 fan-out 派发独立 subagent）
  ├── 判断能否完成 ────────────────→ devflow-completion-gate
  └── 收口/closeout ───────────────→ devflow-finalize
```

### 5.3 取消 `devflow-router` 的中枢地位：分布式门禁 + 证据自路由

这是 2.0 最大的结构变化。把 router 的五项职责拆解重配：

| router 1.0 职责 | 2.0 去向 |
|---|---|
| 决定 canonical 下一节点 | 下沉到每个 skill 的 **Exit Handoff**：skill 完成后按自己的转移表声明唯一 next skill；冲突/不唯一时标 `reroute=true` 并停下交还编排者 |
| 决定 Workflow Profile | 下沉到 **`devflow-specify` 的 Profile 判定步** + `references/devflow-conventions.md` 的 profile 规则；profile 写入 `progress.md` 后即为单一真相，后续 skill 只读不改（升级仍单向，由 `devflow-specify`/`devflow-problem-fix` 在重判时执行） |
| 决定 Execution Mode | 下沉到 conventions：归一化顺序固定（用户显式 → AGENTS.md 默认 → 已有值 → interactive），任何 skill 读 `progress.md` 即可 |
| 派发 reviewer subagent | 上移到 **编排层（用户/命令/会话控制器）**；`fan-out + merge` 仅用于对同一工件的独立视角，DevFlow 的 `test-review → code-review` 受门禁约束**仍顺序执行**（`/devflow-build` 顺序派发两者） |
| review/gate 后恢复编排 | 由 **证据自路由** 承担：任意时刻读 `progress.md` + 最新 `reviews/` 即可恢复；无法唯一映射时回到 `using-devflow` 发现树 + 提一个判别问题 |

> **保留一个「瘦路由」选项**：对确实存在「证据冲突 / 多个 in_progress task / 跨子街区切换嫌疑」的疑难情形，2.0 仍可保留一个**可选的** `devflow-router` 作为「疑难仲裁 skill」，但它**不再是默认必经节点**，只在 `reroute=true` 时被显式调用。默认 happy path 不经过它。这与 `agent-skills` 「不建 router persona 作为默认中枢」一致，又给 DevFlow 的复杂工作项留了仲裁出口。

#### 分布式门禁示例（写进各 skill 的 Entry Gate）

| 门禁 | 写在哪个 skill 的 Entry Gate |
|---|---|
| 无 `requirement.md` 不得开始 AR 设计 | `devflow-ar-design` |
| AR 设计缺测试设计章节不得进 TDD | `devflow-tdd-implementation`（自查上游 `ar-design-draft.md`） |
| TDD 后未经 test-review 不得进 code-review | `devflow-code-review`（自查 `reviews/` 有 test-review verdict） |
| 无 code-review verdict 不得进 completion-gate | `devflow-completion-gate` |
| completion-gate 未通过不得 finalize | `devflow-finalize` |
| component-impact 缺 `docs/component-design.md` 阻塞 | `devflow-component-design` / `devflow-ar-design` |
| `requirement-analysis` 子街区禁止进入实现类节点 | 各实现类 skill 的 Entry Gate 自查 `Work Item Type/Profile` |

**好处**：门禁与它要保护的 skill 同处一地，更不易被绕过；任何工具/agent 即使没载入 router 也能正确拒绝非法进入。

### 5.4 Skill 目录与职责（2.0）

保持 13 个 canonical 工作节点的**职责划分不变**（soul/architecture 已验证合理），但：

- `using-devflow`：重写为轻量 meta（见 5.2）。
- `devflow-router`：**降级为可选的疑难仲裁 skill**（见 5.3），不再是 happy path 必经。
- 其余 11 个作者/评审/门禁/收口 skill：**职责不变，但各自补齐 Entry Gate / Exit Handoff，删除重复的「本地约定」样板，改为引用单一真相源**。

canonical 节点名保持稳定（避免破坏现有工件与 handoff 字段）：

```
using-devflow            （meta：发现 + 准则）
devflow-router           （可选：疑难仲裁，非默认必经）
devflow-specify          （含 profile 判定）
devflow-spec-review
devflow-component-design
devflow-component-design-review
devflow-ar-design        （含测试设计章节）
devflow-ar-design-review
devflow-tdd-implementation（唯一 implementer 派发者）
devflow-test-review
devflow-code-review
devflow-completion-gate
devflow-finalize
devflow-problem-fix
```

### 5.5 约定去重：单一真相源

新增 `references/devflow-conventions.md`（项目根 `references/`，对齐 `agent-skills`），集中定义：

- 产物布局（`features/<id>/...` 与 `docs/...`）
- `progress.md` canonical 字段
- handoff 字段
- 合法 profile 集合与升级规则
- 合法 execution mode 与归一化顺序
- canonical 节点清单
- Read-on-presence 规则与 Promotion Rules

各 skill 的「本地 DevFlow 约定」一节**整段删除**，替换为一行引用：

```markdown
## 约定
本 skill 遵循 `references/devflow-conventions.md`；项目 `AGENTS.md` 可覆盖等价路径与模板。
```

`AGENTS.md` 仍是「硬契约」总入口，但**只保留跨 skill 的不变量与覆盖点**，把可被项目覆盖的细节指向 conventions 文件。预计每个 skill 因此瘦身 80–110 行。

### 5.6 工件模型（保留，微调）

- `features/<id>/`、`docs/ar-specs`、`docs/ar-designs`、`docs/component-design.md` 全部保留。
- `progress.md` 字段保留，但**新增/明确两个自路由友好字段**：`Last Verdict`（最近一次 review/gate 结论）与 `Next Action Or Recommended Skill`（已有，强调它现在是「证据自路由的落点」而非「router 的输出」）。
- closed work item 仍留在 `features/<id>/`（不归档，保追溯）。

### 5.7 角色分离与 subagent 模型（保留纪律，换编排者）

| 维度 | 1.0 | 2.0 |
|---|---|---|
| reviewer 是否独立 subagent | 是 | **是（不变）** |
| 谁派发 reviewer | 只有 `devflow-router` | **编排者（用户/命令/会话控制器）；可选 router 仲裁时也可** |
| reviewer 是否改生产代码 | 否 | **否（不变）** |
| implementer 派发者 | 只有 `devflow-tdd-implementation` | **只有 `devflow-tdd-implementation`（不变）** |
| 作者自审 | 禁止 | **禁止（不变）** |

`agents/devflow-reviewer.md` 与 `agents/devflow-implementer.md` 升级为 `agent-skills` 风格的 persona（带视角与输出格式），可被 Claude Code subagent / OpenCode 等直接复用。

### 5.8 Profile 处理（保留语义，换持有者）

- 五个 profile（`requirement-analysis` / `standard` / `component-impact` / `hotfix` / `lightweight`）与「单向升级、禁跨子街区切换」语义**完全保留**。
- 持有者从 router 改为 `devflow-specify`（首判）/ `devflow-problem-fix`（hotfix 首判）；写入 `progress.md` 后为单一真相，其余 skill 只读。
- 若运行中证据表明需升级（如改动触及 SOA 接口），由当前作者 skill 的 Exit Handoff 标记升级建议并指向 `devflow-component-design`；疑难时才调用可选的 `devflow-router` 仲裁。

---

## 6. Skill 写作规范 2.0（DevFlow Skill Anatomy）

每个 `devflow-*/SKILL.md` 2.0 模板（目标 < 250 行）：

```markdown
---
name: devflow-<node>
description: <第三人称"做什么"> + <"Use when ..." 触发条件> + <"Not for ..." 反向排除>。≤1024 字符，不复述工作流步骤。
---

# DevFlow <Node>

## Overview            # 一两句：本 skill 把哪个 object 转成哪个 object
## When to Use         # 正向触发 + When NOT to use
## Entry Gate          # 【2.0 新增】开工前自查的上游工件 / 门禁；不满足→停下并指出缺什么
## Core Process        # 编号步骤；含决策图与（如适用）证据样例
## Exit Handoff        # 【2.0 强化】产出工件 + 唯一合法 next skill（或 reroute=true）+ handoff 字段
## Common Rationalizations  # 偷懒话术 + 反驳（保留 1.0 强项）
## Red Flags           # 违反信号
## Verification        # 带证据的退出清单
## 约定                # 一行引用 references/devflow-conventions.md（替代 1.0 的大段样板）
```

规则：
- 中英混排可保留（团队习惯），但**硬规则用表格/清单承载**，便于跨工具稳定执行。
- 不在 skill 间复制内容；引用 conventions 与其它 skill 名。
- 高风险 skill（`devflow-tdd-implementation` / `devflow-test-review` / `devflow-completion-gate` /（可选）`devflow-router`）保留 `evals/` 误用场景（沿用 `docs/principles/06 evals-format.md`）。
- `references/` 放共享清单（embedded C/C++ 风险 rubric、profile-route-map、reviewer-dispatch-protocol、devflow-conventions）。

---

## 7. 从 1.0 到 2.0 的重写路线

分阶段、可独立验证（每阶段都让仓库处于可用状态）：

| 阶段 | 内容 | 完成判据 |
|---|---|---|
| **R0 单一真相源** | 新建 `references/devflow-conventions.md`，把 14 个 skill 里重复的约定抽取合并；校对无遗漏 | conventions 覆盖所有 1.0 约定项；diff 显示无信息丢失 |
| **R1 瘦身 leaf** | 14 个 skill 删除「本地约定」样板，改为一行引用；补 `Entry Gate` / `Exit Handoff` 两节 | 每个 skill < 250 行；门禁齐全；canonical 名不变 |
| **R2 重写 meta** | `using-devflow` 重写为「发现树 + 共同行为准则」，删除 route-first/转交逻辑 | `using-devflow` < 120 行；不再依赖 router 作默认转交 |
| **R3 router 降级** | `devflow-router` 改写为「可选疑难仲裁 skill」；happy path 不经过它；profile/mode 持有者迁到 specify/problem-fix | 标准路线端到端走通且不经 router |
| **R4 编排层** | `commands/*.md` 改为「bias 非 authority」入口；`/devflow-ship` 实现 reviewer fan-out+merge；persona 升级 | 命令文档与 2.0 路由一致 |
| **R5 多工具适配（可选）** | 增加 `docs/<tool>-setup.md` 与 `.claude/`、`hooks/session-start.sh` 注入 meta-skill | 至少 OpenCode + 一种其它工具可用 |
| **R6 文档对齐** | 更新 `README` / `docs/principles/04 workflow-architecture.md` 反映去中枢路由；更新 `CHANGELOG` 为 2.0 | 文档与实现一致；评审通过 |

> 顺序原则：先 R0/R1 拿到「去重 + 门禁下沉」的即时收益（风险最低、收益最大），再做 R2/R3 的入口/路由结构变化（风险最高，需充分评审）。

---

## 8. 风险与权衡

| 风险 | 说明 | 缓解 |
|---|---|---|
| **去中枢导致门禁被绕过** | 没有中央 router，可能担心 agent 跳门禁 | 门禁内嵌到 skill 的 Entry Gate（与被保护对象同处），并保留 `evals/` 误用拒绝；保留可选 router 做疑难仲裁 |
| **证据自路由在「证据冲突」时退化** | peer 模型在工件互相矛盾时可能无唯一下一步 | 明确 `reroute=true` 出口 → 回 `using-devflow` 发现树 + 一个判别问题 →（必要时）可选 router 仲裁 |
| **canonical 名/字段变更破坏存量工件** | 现网 `features/<id>/` 已用 1.0 字段 | 节点名与 progress/handoff 字段**保持稳定**，2.0 只增不改不删关键字段 |
| **多工具适配工作量** | R5 是新增面 | 设为可选阶段；核心价值在 R0–R4，R5 不阻塞 |
| **「降级 router」与 1.0 心智模型冲突** | 维护者已习惯 router 中枢 | 在 README/architecture 文档显式解释「编排者 + 分布式门禁」心智模型，给迁移对照表 |

权衡取舍记录：
- **取**：可组合性、去重、可移植、入口轻量、跨工具稳定性。
- **舍**：单一中央权威带来的「强制顺序保证」——用「分布式门禁 + Exit Handoff 唯一 next + 可选仲裁」补回等价保证。
- **守**：DevFlow 全部工程纪律与 soul 边界，零让步。

---

## 9. 验收标准（2.0 完成的定义）

DevFlow 2.0 重写完成，当且仅当：

1. **入口轻量**：`using-devflow` 仅含发现树 + 共同行为准则，不做权威路由、不持有运行时状态、< 120 行。
2. **去中枢**：标准/component-impact/hotfix 三条路线端到端走通，happy path 不经过 `devflow-router`；router 仅在 `reroute=true` 时被显式调用。
3. **门禁不丢**：1.0 列出的全部 Hard Stops（见 `04 workflow-architecture.md`）都能在 2.0 被对应 skill 的 Entry Gate 拒绝；`evals/` 通过。
4. **去重**：约定只在 `AGENTS.md` + `references/devflow-conventions.md` 定义；任一 skill 内不再出现重复的约定样板；单个 `SKILL.md` < 250 行。
5. **纪律保留**：证据优先恢复、角色分离评审（独立 subagent、不自审、不改生产代码）、门禁化 TDD、可追溯、团队角色边界，全部可被现有 `evals/` 与端到端走查验证。
6. **可移植性就绪**：核心 `skills/` 为纯 Markdown，工具适配集中在适配层；至少保证 OpenCode 路径不退化。
7. **文档一致**：README / `docs/principles/04` / CHANGELOG 与实现一致，并解释新心智模型。

---

## 10. 假设与待决问题（Surface Assumptions）

> 遵循 `using-agent-skills` 的「先亮出假设」准则，本设计基于以下假设；任一不成立需回炉。

**假设**：
1. 保持 13 个 canonical 工作节点的职责划分不变是可接受的（本设计只改组织方式，不改节点语义）。
2. 节点名与 `progress.md`/handoff 字段需保持稳定以兼容存量工件。
3. 团队接受「编排者（用户/命令/会话控制器）派发 reviewer」替代「router 派发 reviewer」。
4. soul 三条边界（范围 / 团队角色 / 质量观）在 2.0 不动。

**待决问题（建议团队评审时拍板）**：
1. **是否完全删除 `devflow-router`，还是保留为可选仲裁 skill？** 本设计建议「保留为可选」，因为 DevFlow 工作项比 `agent-skills` 的通用任务更可能出现证据冲突/跨子街区嫌疑，需要一个仲裁出口。
2. **profile 首判持有者**放在 `devflow-specify` 是否合适？还是新增一个极薄的 `devflow-intake` skill 专门做 work-item 类型 + profile 首判？
3. **多工具适配（R5）**是否纳入 2.0 首发，还是留作 2.1？
4. **共同行为准则**是否需要像 `agent-skills` 那样通过 session-start hook 常驻注入（依赖具体工具能力）？

---

## 附录 A：A/B 对照速查

| 维度 | DevFlow 1.0 | DevFlow 2.0 | 取自 agent-skills 的理念 |
|---|---|---|---|
| 入口 | `using-devflow` + `devflow-router` 双头 | 单一轻量 `using-devflow`（发现 + 准则） | `using-agent-skills` 是唯一 meta |
| 路由 | 中心化 FSM（router 权威） | 分布式门禁 + 证据自路由 +（可选）仲裁 | 「不建 router persona 作默认中枢」 |
| skill 关系 | FSM 节点，必经 router | 可独立调用、按名互引的 peer | 「multiple skills can apply」 |
| 约定 | 14 份重复样板 | 单一真相源（conventions + AGENTS.md） | 「不复制，引用」+ 渐进披露 |
| 体量 | 259–366 行/个 | < 250 行/个，meta < 120 | 「< 500 行 + token-conscious」 |
| reviewer 派发 | 仅 router | 编排者派发（gated 链仍顺序） | dispatcher 上移到命令层 |
| 工具 | OpenCode-only | 纯 Markdown + 适配层 | 多工具可移植 |
| 工程纪律 | 优秀 | **完全保留** | DevFlow 自有护城河 |

## 附录 B：参考来源

- `addyosmani/agent-skills`：`README.md`、`AGENTS.md`、`CONTRIBUTING.md`、`docs/skill-anatomy.md`、`skills/using-agent-skills/SKILL.md`、`skills/test-driven-development/SKILL.md`、`hooks/`（session-start 注入机制）。
- DevFlow 1.0：`AGENTS.md`、`README.md`、`skills/using-devflow/SKILL.md`、`skills/devflow-router/SKILL.md`、`docs/principles/00 soul.md`、`docs/principles/04 workflow-architecture.md`、各 `skills/devflow-*/SKILL.md` 体量统计。
