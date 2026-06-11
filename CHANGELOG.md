# Changelog

All notable changes to DevFlow are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

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
