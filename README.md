# DevFlow

[English](README.md) | [中文](README.zh-CN.md)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
![Version](https://img.shields.io/badge/version-v2.0.0-blue.svg)
![Core](https://img.shields.io/badge/core-three%20quality%20layers-green.svg)

**A development-workflow skill suite for AI coding agents. The goal in one sentence: produce Clean Code under the SDD paradigm — not code that merely runs.**

The default path of AI coding jumps from a vague one-liner straight to code, reliably producing three failure modes: building the wrong thing (guessed requirements), building it wrong (unverified code), and building it badly (runs, but rots). DevFlow counters them with a three-layer quality model, from the outside in:

| Layer | Question it answers | Carried by |
|---|---|---|
| **Layer 1 SDD (spec-driven)** | Are we building the right thing? | `devflow-specify` |
| **Layer 2 TDD (test-driven)** | Is it proven functionally correct? | `devflow-tdd` |
| **Layer 3 Clean Code** | Is the code itself well made? | `devflow-design` + `devflow-clean-code` |

The collaboration stance is **human-on-the-loop**: the AI does the work; the human reviews the key artifacts (spec, design, tests, code). Philosophy: [`docs/devflow-philosophy.md`](docs/devflow-philosophy.md). Architecture: [`docs/devflow-core-architecture.md`](docs/devflow-core-architecture.md).

## Design stance

DevFlow 2.0 follows two principles (and this is what distinguishes it from typical "process frameworks"):

- **Minimal process**: keep only the process that produces quality — phase artifacts, human checkpoints, TDD discipline, independent review. No state machine, no router, no multi-field status files; progress is recovered from on-disk artifacts.
- **Maximal substance**: the body of every skill is actionable engineering judgment — rules, good/bad code examples, rebuttals to rationalizations, verification checklists — not process boilerplate.

## Workflow

```text
specify ──review──> design ──review──> tdd ──review──> ship ──[human]──> done
 testable spec +    component-level +    per-case        DoD check,
 plan skeleton +    work-item design:    RED→GREEN→      promotion of
 traceability       contracts / error    REFACTOR        long-term assets
                    model / test design
Defect path: fix (reproduce → root cause → minimal fix) → tdd → review → ship
```

Every phase output passes an independent `devflow-review` gate with an on-disk record before the next phase starts. At workflow start the **run mode** is confirmed once: `attended` (default — human approves after each review) or `unattended` (runs continuously for long sessions — independent reviews, records, and critical-finding blocking still happen; the human audits `reviews/` afterwards).

Per-work-item artifacts (`features/<id>-<slug>/`): `spec.md`, `traceability.md`, `design.md` (plus `component-design-draft.md` when component boundaries are affected), `plan.md` (run mode, gate states, self-contained task breakdown with evidence lines — the single entry point for interrupted-work recovery), `reviews/` (one record per review round, findings + resolution closure), `closeout.md` (`fix.md` for defects). Long-term assets (`docs/component-design.md`, `docs/ar-specs/`, `docs/ar-designs/`) are promoted at the ship phase. The next step is always recovered from artifact state, never from chat memory.

## Skill catalog

### Phase skills

| Skill | What it does |
|---|---|
| [`using-devflow`](skills/using-devflow/SKILL.md) | Entry: three-layer model, workflow map, artifact conventions, behavior rules |
| [`devflow-specify`](skills/devflow-specify/SKILL.md) | Turn intent into a testable spec: EARS statements, BDD acceptance, NFR QAS, change baselines |
| [`devflow-design`](skills/devflow-design/SKILL.md) | Two-level software design (component + work-item, enterprise templates with quality supplements): responsibility boundaries, coupling checks, abstraction discipline, interface contracts, error model, test design |
| [`devflow-tdd`](skills/devflow-tdd/SKILL.md) | Test-first implementation: RED→GREEN→REFACTOR, assertion strength, mock boundaries; dispatches an implementer subagent per task by default, with on-disk evidence lines |
| [`devflow-review`](skills/devflow-review/SKILL.md) | Independent review: four rubrics (spec/design/test/code); authors never self-review |
| [`devflow-ship`](skills/devflow-ship/SKILL.md) | Closeout: Definition-of-Done check, promotion of long-term assets, closeout record |
| [`devflow-fix`](skills/devflow-fix/SKILL.md) | Defect handling: reproduce → three-level root cause → minimal fix boundary → TDD fix |

### Overlay skills (quality constraints across all phases)

| Skill | What it does |
|---|---|
| [`devflow-clean-code`](skills/devflow-clean-code/SKILL.md) | Clean code standards: naming, functions, control flow, error handling, comments, refactoring catalog (with before/after) |
| [`c-coding-standards`](skills/c-coding-standards/SKILL.md) | C rules: pointer ownership, memory & resources, buffers, integers, macros, headers |
| [`cpp-coding-standards`](skills/cpp-coding-standards/SKILL.md) | C++ rules: RAII, ownership in signatures, class design, error strategy, template discipline, ABI |
| [`embedded-development`](skills/embedded-development/SKILL.md) | Embedded constraints: memory, interrupts, real-time, hardware boundaries, evidence strategy |
| [`automotive-development`](skills/automotive-development/SKILL.md) | Automotive constraints: ASIL, vehicle lifecycle, SOA, DTC, SELinux, cross-ECU |

Language standards extend via the `<language>-coding-standards` naming convention (java, python, etc. planned): phase skills reference them by convention, so new languages plug in with zero changes elsewhere; every language skill follows the same [structural contract](skills/coding-standards-creator/references/coding-standards-skill-contract.md).

### Tooling skills

| Skill | What it does |
|---|---|
| [`coding-standards-creator`](skills/coding-standards-creator/SKILL.md) | Turns an internal team coding standard document into a new `<language>-coding-standards` skill: rule ownership triage (language / generic / domain / process), rule distillation (judgeable + failure class + good/bad examples), registration, human sign-off |

## Quick start

OpenCode auto-discovers every `SKILL.md` under `skills/` (see [`docs/guides/opencode-setup.md`](docs/guides/opencode-setup.md)); the same applies to any runtime that supports Agent Skills (Claude Code, Cursor, etc.).

```bash
# Option A: sibling skill pack
git clone https://github.com/hujianbest/devflow.git ~/devflow
cd /path/to/your-repo && ln -s ~/devflow/skills .opencode-skills

# Option B: vendor into your repo
git subtree add --prefix .devflow https://github.com/hujianbest/devflow.git --squash main
```

Try it:

```text
Use DevFlow: add a retry mechanism to the notifications component.
Clarify the requirements first; do not jump straight to code.
```

Slash-style phase entries are available under [`commands/`](commands/README.md): `/devflow`, `/devflow-specify`, `/devflow-design`, `/devflow-build`, `/devflow-review`, `/devflow-ship`, `/devflow-fix`.

Project overrides: create an `AGENTS.md` with a `## Project overrides` section at your repo root to override artifact paths and templates; without it, built-in defaults apply.

## Project layout

```text
devflow/
├── skills/            # 7 phase skills + 5 overlay skills + 1 tooling skill (see tables above)
├── commands/          # slash-style phase entries (platform adapter)
├── agents/            # devflow-reviewer / devflow-implementer subagent personas
├── docs/
│   ├── devflow-philosophy.md         # core philosophy (north star)
│   ├── devflow-core-architecture.md  # architecture mapping
│   └── guides/opencode-setup.md
├── scripts/           # repository consistency checks
└── tests/
```

## Scope

DevFlow covers the engineering segment from an accepted requirement to a reviewed implementation. It does not cover product discovery, release operations, system/integration/acceptance testing, or incident management; nor does it make business, priority, acceptance-threshold, or architecture-boundary decisions on behalf of the team — those belong to humans.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). Keep skills concrete, verifiable, example-driven, and keep process boilerplate minimal.

## License

[MIT](LICENSE)
