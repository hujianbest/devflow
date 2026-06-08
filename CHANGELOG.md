# Changelog

All notable changes to DevFlow are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added — on-demand review command

- `commands/devflow-review.md` (`/devflow-review`) — an **on-demand review re-entry** that maps a "现在检查一下设计 / 代码 / 测试 / 规格" intent to the matching canonical review node(s) (`devflow-spec-review`, `devflow-component-design-review`, `devflow-ar-design-review`, `devflow-test-review`, `devflow-code-review`). It is a **re-entry, not a self-review shortcut**: every review is still dispatched by `devflow-router` to an independent `devflow-reviewer` subagent; the command never authors or modifies artifacts, never self-reviews, and never skips the sequential `test-review → code-review` gate order. Documented in `commands/README.md`, both READMEs, and the 2.0 design spec.

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
