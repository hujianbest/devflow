# Changelog

All notable changes to DevFlow are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### 2.3 — 真实流程验证反馈：评审门禁、plan.md、评审记录闭环

针对真实开发流程验证发现的三个不符合预期点（只在 code 后才 review 且全程无停顿；tasks.md 信息不足以支撑中断恢复；评审问题与解决过程未落盘）：

#### Changed — 评审成为必经门禁，运行模式启动时确认

- 工作流改为 **specify → R1 review → design → R2 review → tdd → R3 review → ship**：每个阶段产物完成后必须经 `devflow-review` 独立评审并落盘记录，通过前不进入下一阶段。删除 2.0 中"可用 devflow-review 预审"的可选措辞（验证表明它会被模型解读为可跳过）。
- 新增**运行模式**，工作流启动时向用户确认一次并记入 plan.md：`attended`（默认，每个评审后人工确认再继续）/ `unattended`（连续执行便于长时间运行）。`unattended` 只移除人工停顿：独立评审、记录落盘、critical findings 阻塞返工照常，人事后统一审计 `reviews/`。
- specify/design/tdd 各技能与 commands 的前置/后置检查改为按 plan.md 门禁表 + reviews/ 记录核验。

#### Changed — tasks.md 升级为 plan.md（中断恢复的单一入口）

- 恢复 `devflow-tdd/references/plan-template.md`（融合 1.x task-plan 模板与 superpowers 计划结构）：运行模式与门禁状态表、固定的「恢复指引」节、**自包含任务**（用例锚点含 Given/When/Then 摘要、精确文件路径、RED/GREEN 步骤与验证命令、完成定义、证据行）、风险与债务登记。
- 生命周期：specify 建骨架（运行模式+门禁表）→ design 评审通过后 tdd 细化任务 → 执行期实时更新勾选与证据。标准：**全新会话只读 spec+design+plan 即可从任意断点继续**；"同上/见聊天记录"式任务按违规处理。

#### Changed — 评审记录与 Resolution 闭环硬性化

- `devflow-review` 新增不变量：**没有记录的评审等于没有评审**。每轮评审落盘 `reviews/<目标>-review-<日期>.md`（复审加 `-r2` 轮次），findings 表含 **Resolution 列**。
- 作者按 findings 返工后必须逐条回写 Resolution（修复+commit / 人接受+理由 / 登记债务+去向）；critical/important 未闭环不放行；复审核对 Resolution 与实际 diff。
- `devflow-ship` DoD 对应强化：R1/R2/R3 记录齐全、Resolution 全闭环、plan.md 门禁表与 reviews/ 一致（造假按 critical）。
- `agents/devflow-reviewer.md` 输出模板更新：轮次、Resolution 列、人工确认节。

### 2.2 — Coding standards 扩展机制与 creator 工具

为语言编码规范的横向扩展（规划 java/python 等）建立机制：

#### Added

- **`coding-standards-creator`（新工具技能）**：把团队内部编码规范文档转化为符合 DevFlow 形态的 `<language>-coding-standards` 技能。核心工作流：逐条归属判定（语言级收录 / 通用引用 `devflow-clean-code` 不复制 / 领域规则移交领域技能 / 流程规则剔除并提示归属）→ 规则提炼三要素（可判定 + 针对的事故类 + 目标语言正反例；"禁止 X"必补替代）→ 按契约生成 → 接入注册 → 归属映射表交人验收。纪律：团队规则与 DevFlow 默认冲突时团队优先且显式标注；不发明团队规则（补充建议须标注待确认）。
- **结构契约** `references/coding-standards-skill-contract.md`：所有语言技能的统一标准——命名约定、frontmatter 触发条件模式、只收语言级规则的边界（三不收）、规则写法三要素、规模上限与 progressive disclosure、五个消费点、evals 要求、验收清单。附可拷贝骨架 `coding-standards-skill-template.md`。
- 校验脚本：`<language>-coding-standards` 命名模式检查；新语言技能无需注册即合法，采纳后建议加入 `EXPECTED_SKILLS` 防误删。

#### Changed

- **约定式引用替代语言枚举**：`devflow-design`/`devflow-clean-code`/`devflow-review` code rubric/`devflow-ship` DoD/commands/agents 中的 `c-coding-standards`/`cpp-coding-standards` 硬编码改为「适用的 `<language>-coding-standards`」约定（c/cpp 作为示例保留）——新增语言零改动接入。
- `using-devflow` 技能地图改为约定行 + 发现规则；DoD 约束审计表改为"每种语言一行"。

### 2.1 — Restore必要能力（最小流程表面积）

2.0 重写后经讨论确认以下 1.x 能力必要，以新的形态恢复：

#### Added

- **`devflow-ship`（新阶段技能）**：收尾 = DoD 核验 + 追溯终验 + promotion + closeout。`references/definition-of-done.md` 按三层组织核验项（含微小修改 / 缺陷工作项的裁剪规则）；`references/promotion-checklist.md` 规定长期资产（`docs/ar-specs/`、`docs/ar-designs/`、`docs/component-design.md`）的同步对象与语义化改写规则。恢复 `/devflow-ship` 命令。
- **组件级设计（团队开发流程要求）**：`devflow-design` 升级为两级设计——影响组件边界时必须先修订 `component-design-draft.md` 并经模块架构师确认，工作项设计只引用组件基线。恢复两份企业级模板（`devflow-component-design-template.md`、`devflow-ar-design-template.md`）并增补「高质量设计增补」章节（接口契约六项、错误模型、数据所有权、简单性检验 / 边界检验、错误与降级总策略、抽象与演进成本），替代原 design-template.md。
- **追溯矩阵 `traceability.md`**：作为 spec-design-code 一致性的显式约束。specify 初始化（需求/Change Type/上游锚点列），design / tdd 逐阶段补列，review 抽查（design/code rubric 新增检查项），ship 终验。模板在 `devflow-specify/references/traceability-template.md`。
- **极简证据纪律**：tasks.md 每个完成任务必须带 RED/GREEN 证据行（命令 + 关键输出摘要 + commit 锚点），替代 1.x 的 evidence/ 目录与多文件格式；test-review rubric 对应检查。
- **implementer subagent 默认执行模式**：恢复精简版 `agents/devflow-implementer.md`；`devflow-tdd` 在 runtime 支持时默认逐任务派发全新上下文 subagent（输入为 Context Pack 而非聊天历史），防上下文漂移；无 subagent 时退化为当前会话执行，纪律不变。

#### 原则不变

恢复的是**能力**而非 1.x 样板形态：仍无 router、无 progress.md 状态机、无 handoff YAML、无 profile/execution-mode。流程仍为 specify → design → tdd → review → ship 单链 + fix 旁路。

### 2.0 — Rewrite: minimal process, maximal substance

调研了 skill 编写的业界实践（Anthropic Agent Skills 指南、superpowers 等）并审计了 1.x 全部内容后的结论：约半数篇幅是流程样板（对象契约、handoff 字段、canonical 节点、profile/execution-mode），而声称是核心的第三层（clean-design/clean-code/语言规范）反而最薄、几乎没有可模仿的正反例。2.0 据此重写：**流程最小化、内容最大化**，目标对齐理念文档的一句话——SDD 范式下生成 Clean Code 的代码，而不是仅仅能运行的代码。

#### Changed — 架构

- 13 个 canonical 流程节点 + router + meta 收敛为 **6 个阶段技能 + 5 个叠加技能**：
  - 阶段：`using-devflow`（入口）、`devflow-specify`、`devflow-design`、`devflow-tdd`、`devflow-review`、`devflow-fix`。
  - 叠加：`devflow-clean-code`、`c-coding-standards`、`cpp-coding-standards`、`embedded-development`、`automotive-development`。
- 工件模型简化为 `features/<id>/`: `spec.md`、`design.md`、`tasks.md`、`reviews/`（缺陷为 `fix.md`）；进度恢复按工件存在性与确认状态判断（恢复表在 `using-devflow`）。
- 全部技能改为「规则 + 正反例代码 + 合理化反驳 + 自检清单」的写法；frontmatter description 改为纯触发条件（CSO 实践）。

#### Added — 高价值内容

- `devflow-design`（新）：一句话职责测试、按变化理由划分模块、耦合的可操作判断表、抽象纪律（rule of three、单实现接口）、接口契约六项、错误模型三件事、数据所有权、方案取舍、测试设计表。
- `devflow-clean-code`（重写）：命名规则表、函数拆分步骤、卫语句、错误处理写法、注释 why-not-what、重复与死代码，全部带 before/after；新增 `references/refactoring-catalog.md`（10 种异味的识别特征 + 手法 + 示例）。
- `devflow-tdd`（重写自 tdd-implementation）：Iron Law、RED/GREEN/REFACTOR 各步带好坏代码对比、mutation 自检、合理化反驳表；新增 `references/test-quality.md`（断言强度升级表、命名、fixture、mock 边界）。
- `c-coding-standards` / `cpp-coding-standards`（重写）：从检查点清单变为具体规则与正反例（指针所有权注释约定、goto cleanup、snprintf 截断检测、宏陷阱→static inline、RAII、所有权签名表、规则零/五、`[[nodiscard]]`、pImpl 等）。
- `devflow-review`（合并 5 个 review 节点）：统一评审协议（独立上下文、findings 三级、人最终把关）+ 四份 rubric（spec/design/test/code），rubric 以「这东西哪里会骗我」组织。
- `embedded-development` / `automotive-development`（重写）：从"对 13 个节点的投射"改为按维度给出「规格/设计定什么、实现红线、验证证据」。

#### Removed

- `devflow-router`、`devflow-spec-review`、`devflow-component-design(-review)`、`devflow-ar-design(-review)`、`devflow-tdd-implementation`、`devflow-test-review`、`devflow-code-review`、`devflow-completion-gate`、`devflow-finalize`、`devflow-problem-fix`、`devflow-clean-design`（内容并入 `devflow-design`）。
- `progress.md` 多字段状态、handoff YAML、Workflow Profile、Execution Mode、canonical 节点机制、HTML closeout 报告、`agents/devflow-implementer.md`、`/devflow-ship`。
- `docs/devflow-internal-quality.md`（第三层不再是参考模型，而是实打实的技能内容）。
- 1.x 的高价值内容全部保留并强化：EARS/BDD/QAS/Change Type 基线/粒度启发式（specify）、Two Hats/TDD 纪律（tdd）、评审 rule 思想（review rubrics）、复现/根因模板（fix）。

### Changed — DevFlow Core architecture

- Reframed DevFlow around the three quality layers from `docs/devflow-philosophy.md`: SDD for intent correctness, TDD for functional correctness, and a rewritten internal-quality layer for design/code quality.
- Added `docs/devflow-core-architecture.md` as the implementation architecture bridge from philosophy to skills, including core workflow, extension skills, platform adapters, and v1 artifact compatibility.
- Added `docs/devflow-internal-quality.md` as the new third-layer reference model. The operational third-layer skills are now `devflow-clean-design` and `devflow-clean-code`.
- Removed the old `devflow-design-craft`, `devflow-coding-craft`, and `devflow-test-craft` skill files from the active skill set.
- Added first extension skills:
  - `c-coding-standards`
  - `cpp-coding-standards`
  - `embedded-development`
  - `automotive-development`
- Updated `using-devflow` and `devflow-router` so coding standards and domain constraints are discovered as non-canonical constraints. They never become `Current Stage` or `Next Action Or Recommended Skill`.

### Migration — craft layer removal

- `devflow-design-craft`: generic design quality moves to `devflow-clean-design`; generic embedded content moves to `embedded-development`; automotive-specific content moves to `automotive-development`.
- `devflow-coding-craft`: generic code quality moves to `devflow-clean-code`; C rules move to `c-coding-standards`; C++ rules move to `cpp-coding-standards`.
- `devflow-test-craft`: removed; test effectiveness moves back to the second-layer TDD / `devflow-test-review` system and is no longer treated as third-layer internal quality.

### Added — flexible review command

- `commands/devflow-review.md` (`/devflow-review`) — a **flexible review entry** that takes the user's request, picks the matching review skill(s) (`devflow-spec-review`, `devflow-component-design-review`, `devflow-ar-design-review`, `devflow-test-review`, `devflow-code-review`), and runs an **independent** review to produce review content. It has two run modes:
  - **standalone (默认)** — runs on any target the user names (file / dir / diff / draft), with no work-item / `progress.md` / gate coupling required; the command dispatches the independent `devflow-reviewer` subagent directly (as an upstream leaf, per the dispatch protocol's "router or upstream leaf") and returns the review content to the user.
  - **in-flow** — when part of a work item, `devflow-router` dispatches the reviewer, consumes the verdict into the sequential `test-review → code-review` gate, and forms the canonical handoff.
  - The one invariant is an **independent reviewer (never author / parent self-review)**; the command never authors or modifies artifacts. Aligned `agents/devflow-reviewer.md` (standalone/ad-hoc dispatch inputs), `commands/README.md` (rule "不内联自审" now covers router or upstream-leaf dispatch), both READMEs, and the 2.0 design spec.
- **Craft lens wired into the design-review nodes** — `devflow-component-design-review` and `devflow-ar-design-review` now carry an explicit `## 质量透镜（Craft）` section (design-craft for component-design-review; design-craft + test-craft for ar-design-review), matching the existing `devflow-code-review` / `devflow-test-review` craft sections. This makes the 2.0 claim "design / build / review nodes carry a craft section" true for the design reviewers and gives `/devflow-review` an accurate craft mapping. (`devflow-spec-review` has no craft lens.)
- **Relaxed invocation exclusivity on commands and agents** — commands and agents are independently invocable; the docs no longer assert that a subagent may *only* be dispatched by a specific node. Dropped "dispatched ONLY by" / "Invoke directly: never" / "仅由 … 派发" / "必须由 devflow-router 派发" / "唯一编排权威" framing from `agents/devflow-reviewer.md`, `agents/devflow-implementer.md`, `commands/devflow-review.md`, `commands/devflow-design.md`, `commands/devflow-specify.md`, `commands/devflow-build.md`, and `commands/README.md`. The **behavioral** invariants are unchanged: reviewers stay independent of the author (no self-review) and never modify artifacts; the implementer always works from an Implementer Context Pack and never edits AR design / task plan / task-board order.

### Removed — SR / requirement-analysis sub-track

- DevFlow now processes **implementation work items only** (`AR` / `DTS` / `CHANGE`). The subsystem-requirement (`SR`) analysis sub-track and the `requirement-analysis` profile are removed. An AR may still reference an upstream `SR` / `IR` as an optional traceability anchor, but `SR` is no longer a DevFlow-processed work item.
- Removed the **sub-track (子街区) split** entirely: there is one implementation flow. Legal profiles are now `standard` / `component-impact` / `hotfix` / `lightweight` (dropped `requirement-analysis`); the "no cross-sub-track switching" rules are gone.
- `devflow-finalize` now performs **implementation closeout only**; the `analysis` closeout type, `AR Breakdown Candidates` delivery, and SR-specific promotion paths are removed (including in `promotion-checklist.md`, the closeout markdown template, and the HTML report template).
- `devflow-component-design` is now triggered **only** by an AR reaching `component-impact`; the SR-triggered branch is removed. `devflow-completion-gate` drops its SR exclusion note.
- Removed the `Owning Subsystem` canonical field, SR work-item-type rows, `Affected Components` / `AR Breakdown Candidates` / `Subsystem Scope` spec sections, and the SR rubric group (`S5-SR` / `S7-SR` / `S8-SR` / `Group SR`) from `devflow-specify`, `devflow-spec-review`, their reference contracts/templates, the shared work-item / progress / traceability templates, the reviewer persona, and the router profile/route map.

### Added — DevFlow 2.0 craft layer

- **Craft quality lenses** — three new peer skills that encode senior-engineer judgment (with concrete tells and counter-examples, localized to embedded C/C++):
  - `devflow-design-craft` — simplicity-first, abstraction discipline (Rule of Three), interface contracts (Hyrum's Law, error semantics, boundary validation), SOLID/GRASP tells, embedded defensive design, quality design-options.
  - `devflow-coding-craft` — Rule 0 simplicity, thin vertical slices, scope discipline (Chesterton's Fence), readability/naming, embedded defensive coding.
  - `devflow-test-craft` — test pyramid + test sizes, state-not-interaction testing, DAMP over DRY, mock discipline (real>fake>stub>mock), coverage types.
  - These are **lenses, not flow nodes**: invoked inside `devflow-ar-design` / `devflow-component-design` / `devflow-tdd-implementation` / `devflow-code-review` / `devflow-test-review`; they never write `progress`/handoff, never produce a verdict, and never change the flow topology.
- A **"DevFlow 共同约定" (shared conventions) section inside the `using-devflow` meta-skill** — the single source of truth for artifact layout, `progress.md` fields, handoff fields, profiles, execution modes, the canonical node list, read-on-presence, and promotion rules. Every other skill references this section instead of carrying its own copy.
- `docs/devflow-2.0-design-spec.md` — the DevFlow 2.0 design spec: analysis of `addyosmani/agent-skills` (especially the `using-agent-skills` ↔ skills relationship), diagnosis of DevFlow 1.0's design/coding-craft gap, and the 2.0 target architecture.

### Changed — DevFlow 2.0

- `using-devflow` rewritten as a true meta-skill: **discovery tree** (now indicating which craft lens to overlay at each phase) + **behavior constitution** (the always-on Core Operating Behaviors) + an explicit **three-layer relationship** (meta discovers / router routes / craft raises quality).
- The duplicated `## 本地 DevFlow 约定` boilerplate (artifact layout, progress fields, handoff fields) was removed from all 13 canonical skills and replaced with a one-line reference to the `using-devflow` "DevFlow 共同约定" section — every `SKILL.md` shrank by ~55–65 lines, restoring progressive disclosure.
- Design / build / review nodes now carry an explicit `## 质量透镜（Craft）` section that names which craft lens to overlay at which workflow step.

### Preserved

- All DevFlow process discipline is unchanged: artifact-first recovery, role-separated independent reviewers, gated TDD with fail-first evidence, requirement-to-code traceability, team-role boundaries, and the embedded C/C++ risk dimensions. Canonical node names and `progress.md`/handoff fields stay stable for backward compatibility with existing `features/<id>/` artifacts.

## [1.0.0] — 2026-05-09

First official DevFlow release. Scope: development-stage workflow on **OpenCode**, biased toward embedded C / C++ teams.

### Added

- 13 active DevFlow skills under `skills/`:
  - Entry: `using-devflow`
  - Routing: `devflow-router`
  - Specification: `devflow-specify`, `devflow-spec-review`
  - Component design: `devflow-component-design`, `devflow-component-design-review`
  - AR design: `devflow-ar-design`, `devflow-ar-design-review`
  - Implementation: `devflow-tdd-implementation`
  - Verification: `devflow-test-review`, `devflow-code-review`
  - Gate / closeout: `devflow-completion-gate`, `devflow-finalize`
  - Problem fix: `devflow-problem-fix`
- Repository-root `AGENTS.md` documenting the OpenCode hard contract for DevFlow agents (entry through `using-devflow`, evidence-first routing, role-separated reviewers, no self-verification, no profile downgrade, etc.).
- `docs/guides/opencode-setup.md` — installation, skill discovery, automatic invocation, agent expectations, limitations.
- `docs/guides/devflow-usage-guide.md` — usage scenarios and FAQ for end users.
- `docs/principles/00-05` — internal principle docs (DevFlow soul, skill-node contract, skill anatomy, artifact layout, workflow architecture, coding principles).
- `evals/` directory on the four high-risk skills — `devflow-router`, `devflow-tdd-implementation`, `devflow-test-review`, `devflow-completion-gate`. Each `evals/` carries a `README.md`, an `evals.json` enumerating misuse scenarios the skill MUST refuse (wrong-node routing, profile silent downgrade, cross-subgraph switching, missing test design before TDD, reviewer overreach, missing upstream verdict at completion gate, etc.), and a `fixtures/` directory of minimal artifact snapshots used as scenario inputs. The eval format is documented in `docs/principles/06 evals-format.md`.
- Per-skill `## 反向理由化（Common Rationalizations）` table on every leaf skill, listing the most common LLM excuses with pre-written counter-arguments.
- `LICENSE` (MIT) and `CONTRIBUTING.md`.
- User-perspective skills directory table and lifecycle diagram in both English and Chinese READMEs.

### Changed

- Brand unified to **DevFlow** (was inconsistently "HarnessFlow" in README, "DevFlow" elsewhere). Repository, product, and skill prefix all match.
- `devflow-tasks` and `devflow-tasks-review` workflow nodes folded into `devflow-tdd-implementation` (task planning is now an internal preflight; `tasks.md` / `task-board.md` remain as artifacts).
- Design authoring skills (`devflow-component-design`, `devflow-ar-design`) require an explicit **Design Options** checkpoint before drafting the full design.
- Each skill now owns its local conventions and references; there is no shared `skills/docs/` or `skills/templates/` folder.
- README, `docs/principles/`, and skill body references corrected from `devflow-skills/` and `docs/devflow-principles/` to the actual paths `skills/` and `docs/principles/`.

### Removed

- The placeholder reference to `devflow-skills/docs/devflow-shared-conventions.md` (the doc never existed; equivalent rules are now self-contained in each skill's `## 本地 DevFlow 约定` section).

### Out of scope

- Multi-agent-runtime integrations (Claude Code, Cursor, Gemini, Copilot, Windsurf, Kiro). v1.0 is OpenCode-only.
- System / integration / acceptance test workflows (belong to a future `test-flow` family).
- Product discovery and runtime incident management (belong to upstream `design-flow` / downstream operations workflows).

[Unreleased]: https://github.com/hujianbest/devflow/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/hujianbest/devflow/releases/tag/v1.0.0
