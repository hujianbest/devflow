# DevFlow

[English](README.md) | [中文](README.zh-CN.md)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
![Version](https://img.shields.io/badge/version-v2.0.0-blue.svg)
![Core](https://img.shields.io/badge/core-three%20quality%20layers-green.svg)

**A development-workflow skill suite for AI coding agents: SDD for the right thing, TDD for proven behavior, and Clean Code for code worth keeping.**

DevFlow packages a disciplined AI-assisted engineering workflow into self-contained Markdown skills: specification, design, test-first implementation, independent review, defect handling, closeout, and language/domain quality overlays.

![DevFlow workflow loop](docs/asserts/devflow-2-workflow-loop-v3.png)

---

## Commands

DevFlow provides slash-style phase entries as a thin platform adapter. The authoritative workflow lives in `skills/<name>/SKILL.md`; commands only express intent and load the right skill.

| What you're doing | Command | Skill | Key principle |
|-------------------|---------|-------|---------------|
| Enter or resume DevFlow | `/devflow` | `using-devflow` | Recover from artifacts |
| Define what to build | `/devflow-specify` | `devflow-specify` | Spec before code |
| Plan how to build it | `/devflow-design` | `devflow-design` | Design before implementation |
| Build with tests | `/devflow-build` | `devflow-tdd` | RED -> GREEN -> REFACTOR |
| Review an artifact | `/devflow-review` | `devflow-review` | Authors do not self-review |
| Close engineering work | `/devflow-ship` | `devflow-ship` | DoD before closeout |
| Fix a defect | `/devflow-fix` | `devflow-fix` | Reproduce before repair |

`devflow-clean-code`, language standards, and domain standards do not have separate commands. They are quality overlays consumed inside design, implementation, and review.

---

## Quick Start

Point your Agent Skills runtime at this repository's `skills/` directory, or vendor DevFlow into the target project. OpenCode setup details are in [docs/guides/opencode-setup.md](docs/guides/opencode-setup.md); the same model applies to runtimes that support Agent Skills, including Cursor and Claude Code.

```bash
# Option A: keep DevFlow as a sibling skill pack
git clone https://github.com/hujianbest/devflow.git ~/devflow
cd /path/to/your-repo && ln -s ~/devflow/skills .opencode-skills

# Option B: vendor DevFlow into your repository
git subtree add --prefix .devflow https://github.com/hujianbest/devflow.git --squash main
```

Try it:

```text
Use DevFlow from this repo.
I want to add a retry mechanism to the notifications component.
Clarify the requirements first; do not jump straight to code.
```

Project overrides: create an `AGENTS.md` with a `## Project overrides` section at the target repository root to override artifact paths and templates. Without it, built-in defaults apply.

---

## See It Work

```text
You:    Use DevFlow from this repo. Add rate limiting to the notifications API.
        Do not jump straight to code.

DF:     Starts with `using-devflow`, confirms the run mode, resolves the target
        component root, then routes into `devflow-specify` because no approved
        spec exists.

You:    Continue with DevFlow once the spec is ready.

DF:     Runs an independent `devflow-review` gate. If the spec passes and the
        run mode allows progress, `devflow-design` writes component/work-item
        design, interface contracts, error model, and test design.

You:    Build the approved design.

DF:     `devflow-tdd` refines `plan.md`, implements one task at a time with
        RED -> GREEN -> REFACTOR evidence, applies `devflow-clean-code` plus
        language/domain standards, and updates evidence lines on disk.

You:    Verify and close the work.

DF:     `devflow-review` checks tests and code from an independent context.
        `devflow-ship` runs the Definition of Done, promotes durable docs, and
        writes `closeout.md` for human final confirmation.
```

At workflow start DevFlow records one run mode: `attended` by default, where review verdicts pause for human confirmation, or `unattended`, where long sessions keep moving while independent reviews, records, critical-finding stops, and later human audit still remain mandatory.

---

## All Skills

DevFlow currently ships 13 core skills: 7 phase skills, 5 quality overlays, and 1 tooling skill.

### Phase Skills

| Skill | What it does | Use when |
|-------|--------------|----------|
| [using-devflow](skills/using-devflow/SKILL.md) | Entry, workflow map, artifact conventions, recovery rules, behavior rules | Starting, resuming, or asking what DevFlow should do next |
| [devflow-specify](skills/devflow-specify/SKILL.md) | Turns intent into a testable spec with EARS, BDD acceptance, NFR QAS, and traceability | A feature/change needs requirements before design or code |
| [devflow-design](skills/devflow-design/SKILL.md) | Produces component/work-item design, boundaries, contracts, error model, tradeoffs, and test design | An approved spec needs technical design |
| [devflow-tdd](skills/devflow-tdd/SKILL.md) | Implements with RED -> GREEN -> REFACTOR, task evidence, assertion quality, and mock-boundary discipline | Design is approved and implementation starts |
| [devflow-review](skills/devflow-review/SKILL.md) | Independently reviews specs, designs, tests, or code with findings and verdicts | A phase artifact is ready to pass a gate |
| [devflow-ship](skills/devflow-ship/SKILL.md) | Checks Definition of Done, promotes long-term assets, and writes closeout | Reviews are closed and engineering work is ready to finish |
| [devflow-fix](skills/devflow-fix/SKILL.md) | Handles defects through reproduction, root cause, minimal fix boundary, and TDD repair | A regression, bug, hotfix, or shipped-behavior defect appears |

### Quality Overlays

| Skill | What it does | Use when |
|-------|--------------|----------|
| [devflow-clean-code](skills/devflow-clean-code/SKILL.md) | Language-neutral clean code standards: naming, functions, control flow, errors, comments, refactoring | Writing, refactoring, or reviewing implementation and test code |
| [c-coding-standards](skills/c-coding-standards/SKILL.md) | C-specific rules for ownership, memory/resources, buffers, integers, macros, headers, and error returns | Work touches C source, headers, or C tests |
| [cpp-coding-standards](skills/cpp-coding-standards/SKILL.md) | C++ rules for RAII, ownership signatures, class design, errors, templates, and ABI | Work touches C++ source, classes, templates, or C++ tests |
| [embedded-development](skills/embedded-development/SKILL.md) | Embedded constraints around memory, interrupts, real time, hardware boundaries, and evidence | Firmware, drivers, HAL, RTOS, or constrained-device work |
| [automotive-development](skills/automotive-development/SKILL.md) | Automotive constraints around ASIL, vehicle lifecycle, SOA, DTC, SELinux, and cross-ECU coordination | ECU, domain-controller, vehicle-service, or platform work |

### Tooling

| Skill | What it does | Use when |
|-------|--------------|----------|
| [coding-standards-creator](skills/coding-standards-creator/SKILL.md) | Converts internal team coding standards into a new `<language>-coding-standards` skill | A team needs to add or revise a language standard |

Language standards extend by convention: work touching language X can load `<x>-coding-standards` when present. New language skills follow the shared [structural contract](skills/coding-standards-creator/references/coding-standards-skill-contract.md), so phase skills do not need to be rewritten for each language.

---

## The DevFlow Method

DevFlow is not a prompt collection. It is a small, evidence-based workflow for getting AI agents to produce code that can be reviewed, trusted, and maintained.

| Layer | DevFlow method | Why it matters |
|-------|----------------|----------------|
| Intent | Spec-driven development | Prevents the agent from guessing requirements |
| Planning | Component/work-item design | Makes boundaries, contracts, errors, and tests explicit before code |
| Execution | Test-driven development | Separates "it looks right" from behavior proven by tests |
| Internal quality | Clean Code overlays | Keeps code readable, simple, maintainable, and reviewable |
| Review | Independent gates | Keeps authorship and judgment separate |
| Recovery | Artifact-first state | Lets another agent or human resume from files, not chat memory |
| Closeout | DoD and promotion | Records what changed, what passed, and which docs became durable assets |

DevFlow's collaboration stance is **human-on-the-loop**: the AI does the work, and humans review the key artifacts and decisions. See [docs/devflow-philosophy.md](docs/devflow-philosophy.md) and [docs/devflow-core-architecture.md](docs/devflow-core-architecture.md).

---

## How Skills Work

Each skill is a self-contained operating procedure:

```text
SKILL.md
├── Trigger conditions
├── Workflow steps
├── Required artifacts
├── Evidence and review contracts
├── Quality rules and examples
├── Red flags and rationalization traps
└── Verification checklist
```

Key design choices:

- **Minimal process.** DevFlow keeps the phase artifacts, human checkpoints, TDD discipline, and independent reviews that produce quality.
- **Maximal substance.** The body of each skill is engineering judgment: rules, examples, failure modes, checklists, and review rubrics.
- **Evidence over memory.** Progress is recovered from `plan.md`, `reviews/`, `traceability.md`, and the artifact files themselves.
- **Authors do not self-review.** The agent that creates an artifact does not approve it.

---

## Project Structure

```text
devflow/
├── skills/                         # 13 core skills
│   ├── using-devflow/              # Entry and recovery rules
│   ├── devflow-specify/            # Testable specs and traceability
│   ├── devflow-design/             # Component/work-item design
│   ├── devflow-tdd/                # Test-first implementation
│   ├── devflow-review/             # Independent review gates
│   ├── devflow-ship/               # DoD, promotion, closeout
│   ├── devflow-fix/                # Defect path
│   ├── devflow-clean-code/         # Language-neutral clean code
│   ├── c-coding-standards/         # C overlay
│   ├── cpp-coding-standards/       # C++ overlay
│   ├── embedded-development/       # Embedded overlay
│   ├── automotive-development/     # Automotive overlay
│   └── coding-standards-creator/   # Language-standard generator
├── commands/                       # Slash-style phase entries
├── agents/                         # devflow-reviewer and devflow-implementer personas
├── docs/
│   ├── devflow-philosophy.md
│   ├── devflow-core-architecture.md
│   ├── devflow-internal-quality.md
│   ├── guides/
│   └── asserts/
├── scripts/                        # Repository consistency checks
├── tests/
├── CONTRIBUTING.md
└── README.zh-CN.md
```

Per-work-item artifacts live in the target component repository, normally under `features/<id>-<slug>/`: `spec.md`, `traceability.md`, `design.md`, `plan.md`, `reviews/`, and `closeout.md` or `fix.md`. Long-term assets such as `docs/component-design.md`, `docs/ar-specs/`, and `docs/ar-designs/` are promoted during `devflow-ship`.

---

## Scope

DevFlow covers the engineering segment from an accepted requirement to a reviewed implementation and closeout. It does not cover product discovery, release operations, system/integration/acceptance testing, incident management, or production rollout. It also does not make business direction, priority, acceptance-threshold, or architecture-boundary decisions on behalf of the team.

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). Keep skills concrete, verifiable, example-driven, and light on process boilerplate.

---

## License

[MIT](LICENSE)
