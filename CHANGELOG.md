# Changelog

All notable changes to DevFlow are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- Added `devflow-init` to establish reviewed canonical baselines for existing components without inventing unknown requirements or design intent.
- Added `devflow-ship` for Definition of Done checks, semantic canonical sync, independent sync review, human confirmation, closeout, and whole-change archival.
- Added `change.json` as the structured source for change identity, component mode, immutable base revision, risk profile, artifact graph, gates, and archive state.
- Added Java and Python coding-standard overlays, frontend and backend domain overlays, and `coding-standards-creator`.
- Added repository validators and per-skill eval scenarios.
- Added `devflow-learn`, a Chinese-first optional post-Ship tool that extracts one evidence-backed learning from an archived change into `docs/learnings/`, with strict schema validation, overlap handling, grounding review, and sensitive-content blocking.
- Added `domain-wiki-skills/`, a skill-native wiki suite (`domain-wiki-*`) for init, git-scoped update, index-first query, ingest, and lint. Only wiki results are written to disk; there is no review-report artifact. Each skill owns its contract.

### Changed

- DevFlow is runtime-agnostic; platform commands are thin adapters over Markdown skills.
- The lifecycle is `baseline preflight → specify → R1 → design → R2 → TDD → R3 → canonical sync review → human confirmation → closeout → archive`.
- Component truth lives in `specs/spec.md` and `specs/design.md`. Active changes live in
  `specs/changes/ARXXX-<topic>/` and completed changes move intact to
  `specs/archive/YYYY-MM-DD-ARXXX-<topic>/`.
- Change delivery uses `srs.md`, `delta-spec.md`, `delta-design.md`, `tasks.md`,
  `traceability.md`, `reviews/`, and `closeout.md`. Delta operations use stable targets and
  `ADDED / MODIFIED / REMOVED / RENAMED` semantics.
- `tasks.md` contains only implementation tasks and RED/GREEN/REFACTOR evidence; review facts and findings Resolution live in `reviews/`.
- Specification, design, test/code, and canonical sync reviews use independent read-only reviewer contexts. Authors resolve findings and reviewers verify the resolution.
- Language and domain skills are additive constraints discovered by convention; they do not alter lifecycle topology.
- Defect work uses the same canonical, delta, TDD, review, sync, and archive contract, with evidence-backed N/A only when the corresponding canonical semantics are unchanged.
- `using-devflow` now performs targeted active-learning lookup before work, while `devflow-ship` may offer knowledge capture after archival without making it a delivery gate.
- Repository skill sources now consistently use `coding-skills/`; commands, validators, tests, and installation examples no longer reference the removed source root.
- `devflow-learn` now validates claim/evidence grounding, performs bounded lookup and evidence-pack extraction, validates the full related/supersession graph, and separates refresh audit from explicitly approved apply.
- `domain-wiki-init` compiles a complete first wiki by section using a skeleton coverage review. The old 8-page first-pass cap is no longer a completion condition. `domain-wiki-update` can run a completeness pass when the user asks to fill the wiki.
- Domain wiki coverage gates now require a real page per interface family, UI surface, and named flow. A table inside an overview does not count as coverage. Inventory signals are surface types, not a specific framework layout.
- Domain wiki skills now treat only repo source, hand-written docs, named originals, and the detected wiki root as evidence. Query stays silent about source when the wiki is enough; ingest treats raw as untrusted; lint regenerates directory indexes and reports mermaid heuristics.
- Domain wiki skills no longer route to or name coding-skills workflows. They only compile `wiki/` and do not author product specs or other documentation trees.
- Renamed `devflow-knowledge-*` / `knowledge-skills/` to `domain-wiki-*` / `domain-wiki-skills/`. The compiled wiki root is `wiki/`.

### Removed

- Removed the v1 router, canonical-node graph, progress/handoff schemas, promotion model, and split closeout mechanisms.
- Removed alternate artifact roots and path aliases. The current layout is a breaking contract and has no automatic migration.
- Removed active redesign narratives, superseded intermediate layouts, and obsolete workflow illustrations from user-facing instructions.

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
