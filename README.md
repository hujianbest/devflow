# DevFlow

[English](README.md) | [中文](README.zh-CN.md)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
![Version](https://img.shields.io/badge/version-v2.0.0-blue.svg)
![Core](https://img.shields.io/badge/core-three%20quality%20layers-green.svg)

**A development-workflow skill suite for AI coding agents: SDD for the right thing, TDD for proven behavior, and Clean Code for code worth keeping.**

DevFlow packages a disciplined AI-assisted engineering workflow into self-contained Markdown skills: specification, design, test-first implementation, independent review, defect handling, closeout, and language/domain quality overlays.

## Project Introduction

DevFlow is a reusable workflow layer for teams that use AI coding agents in real software projects. It turns engineering discipline into executable skill instructions, so an agent can move from requirements to design, implementation, review, and closeout without losing the context and evidence humans need to trust the work.

The project is runtime-agnostic by design. You can use it as a standalone skill pack, vendor it into a repository, or adapt its skills to platforms that support Markdown-based agent instructions. Each skill is intentionally small enough to inspect, revise, and combine with project-specific conventions.

## Project Advantages

- **Structured work instead of prompt drift**: DevFlow gives agents phase boundaries, artifact rules, and recovery behavior, reducing the chance that a session jumps from vague intent straight to code.
- **Three quality layers working together**: SDD clarifies what should be built, TDD proves behavior while implementation evolves, and Clean Code keeps the resulting code maintainable.
- **Independent review built into the flow**: Specs, designs, tests, and code pass through explicit review gates, with authorship separation and recorded findings.
- **Adaptable to real project constraints**: Language standards and domain overlays help the same workflow fit backend, frontend, embedded, automotive, safety-critical, and other specialized work.

![DevFlow workflow loop](docs/asserts/devflow-2-workflow-loop-v3.png)

---

## Commands

DevFlow provides slash-style phase entries as a thin platform adapter. The authoritative workflow lives in `skills/<name>/SKILL.md`; commands only express intent and load the right skill.

| What you're doing | Command | Skill | Key principle |
|-------------------|---------|-------|---------------|
| Enter or resume DevFlow | `/devflow` | `using-devflow` | Recover from artifacts |
| Initialize an existing component | `/devflow-init` | `devflow-init` | Clarify rather than fabricate |
| Define what to build | `/devflow-specify` | `devflow-specify` | Spec before code |
| Plan how to build it | `/devflow-design` | `devflow-design` | Design before implementation |
| Build with tests | `/devflow-build` | `devflow-tdd` | RED -> GREEN -> REFACTOR |
| Review an artifact | `/devflow-review` | `devflow-review` | Authors do not self-review |
| Close engineering work | `/devflow-ship` | `devflow-ship` | DoD before closeout |
| Fix a defect | `/devflow-fix` | `devflow-fix` | Reproduce before repair |

`devflow-clean-code`, language standards, and domain standards do not have separate commands. They are quality overlays consumed inside design, implementation, and review.

---

## Quick Start

Install DevFlow into OpenCode's user-level skills directory so every project can discover it automatically. OpenCode loads global skills from `~/.config/opencode/skills/*/SKILL.md`; setup details are in [docs/guides/opencode-setup.md](docs/guides/opencode-setup.md).

```bash
# Clone DevFlow into the OpenCode user config directory
git clone https://github.com/hujianbest/devflow.git ~/.config/opencode/devflow

# Install all DevFlow skills, agents, and commands
mkdir -p ~/.config/opencode/skills ~/.config/opencode/agents ~/.config/opencode/commands
cp -R ~/.config/opencode/devflow/skills/* ~/.config/opencode/skills/
cp ~/.config/opencode/devflow/agents/*.md ~/.config/opencode/agents/
cp ~/.config/opencode/devflow/commands/devflow*.md ~/.config/opencode/commands/
```

Try it:

```text
Use DevFlow from this repo.
I want to add a retry mechanism to the notifications component.
Clarify the requirements first; do not jump straight to code.
```

Project overrides may add constraints and template requirements through `AGENTS.md`, but the artifact roots stay fixed under the component's `specs/` directory.

---

## See It Work

```text
You:    Use DevFlow from this repo. Add rate limiting to the notifications API.
        Do not jump straight to code.

DF:     Starts with `using-devflow`, resolves the component root, and checks
        change.json. An existing component without baseline-ready spec.md and
        design.md is routed to `devflow-init`; a new component can continue.

You:    Continue with DevFlow once the spec is ready.

DF:     `devflow-specify` writes srs.md and delta-spec.md. After R1,
        `devflow-design` writes delta-design.md with contracts, error model,
        decisions, risks, and test design.

You:    Build the approved design.

DF:     `devflow-tdd` refines `tasks.md`, implements one task at a time with
        RED -> GREEN -> REFACTOR evidence, applies `devflow-clean-code` plus
        language/domain standards, and updates evidence lines on disk.

You:    Verify and close the work.

DF:     `devflow-review` checks tests and code from an independent context.
        `devflow-ship` runs the DoD, intelligently syncs both deltas into
        specs/spec.md and specs/design.md, reviews the canonical diff, then
        moves the complete AR from specs/changes/ to specs/archive/.
```

At workflow start DevFlow records one run mode: `attended` by default, where review verdicts pause for human confirmation, or `unattended`, where long sessions keep moving while independent reviews, records, critical-finding stops, and later human audit still remain mandatory.

---

## All Skills

DevFlow currently ships 18 bundled skills: 8 workflow/entry skills, several quality overlays, and 1 tooling skill. Quality overlays are discovered by convention and by their descriptions, so new overlays can be added without changing the phase skills.

### Phase Skills

| Skill | What it does | Use when |
|-------|--------------|----------|
| [using-devflow](skills/using-devflow/SKILL.md) | Entry, workflow map, artifact conventions, recovery rules, behavior rules | Starting, resuming, or asking what DevFlow should do next |
| [devflow-init](skills/devflow-init/SKILL.md) | Reverse-engineers baseline spec/design from an existing component without inventing unknown intent | An existing component lacks baseline-ready canonical documents |
| [devflow-specify](skills/devflow-specify/SKILL.md) | Produces a testable SRS and delta spec with EARS, BDD acceptance, NFR QAS, and traceability | A feature/change needs requirements before design or code |
| [devflow-design](skills/devflow-design/SKILL.md) | Produces a delta design with boundaries, contracts, error model, tradeoffs, and test design | An approved delta spec needs technical design |
| [devflow-tdd](skills/devflow-tdd/SKILL.md) | Implements with RED -> GREEN -> REFACTOR, task evidence, assertion quality, and mock-boundary discipline | Design is approved and implementation starts |
| [devflow-review](skills/devflow-review/SKILL.md) | Independently reviews specs, designs, tests, or code with findings and verdicts | A phase artifact is ready to pass a gate |
| [devflow-ship](skills/devflow-ship/SKILL.md) | Checks DoD, intelligently syncs canonical docs, writes closeout, and archives the change | Reviews are closed and engineering work is ready to finish |
| [devflow-fix](skills/devflow-fix/SKILL.md) | Handles defects through reproduction, root cause, minimal fix boundary, and TDD repair | A regression, bug, hotfix, or shipped-behavior defect appears |

### Quality Overlays

| Skill | What it does | Use when |
|-------|--------------|----------|
| [devflow-clean-code](skills/devflow-clean-code/SKILL.md) | Language-neutral clean code standards: naming, functions, control flow, errors, comments, refactoring | Writing, refactoring, or reviewing implementation and test code |
| `<language>-coding-standards` skills | Language-level rules, idioms, tooling discipline, and examples | Work touches that language's source, tests, or build scripts; discovered by naming convention |
| `<domain>-development` / domain skills | Domain-specific design constraints, implementation red lines, and evidence requirements | Work context matches a domain skill's frontmatter description |

### Tooling

| Skill | What it does | Use when |
|-------|--------------|----------|
| [coding-standards-creator](skills/coding-standards-creator/SKILL.md) | Converts internal team coding standards into a new `<language>-coding-standards` skill | A team needs to add or revise a language standard |

Language standards extend by convention: work touching language X can load `<x>-coding-standards` when present. New language skills follow the shared [structural contract](skills/coding-standards-creator/references/coding-standards-skill-contract.md), so phase skills do not need to be rewritten for each language. Domain skills trigger from their own frontmatter descriptions; a new domain skill becomes part of the Quality Stack by clearly describing its context, boundaries, and near-misses.

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
| Closeout | DoD, canonical sync, archive | Updates the current truth and preserves the complete change history |

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
- **Evidence over memory.** Phase state comes from `change.json`; task progress comes from `tasks.md`; reviews and traceability verify both.
- **Authors do not self-review.** The agent that creates an artifact does not approve it.

---

## Project Structure

```text
devflow/
├── skills/                         # 18 bundled skills
│   ├── using-devflow/              # Entry and recovery rules
│   ├── devflow-init/               # Existing-component baseline initialization
│   ├── devflow-specify/            # SRS, delta spec, traceability
│   ├── devflow-design/             # Delta design and test design
│   ├── devflow-tdd/                # Test-first implementation
│   ├── devflow-review/             # Independent review gates
│   ├── devflow-ship/               # DoD, canonical sync, archive
│   ├── devflow-fix/                # Defect path
│   ├── devflow-clean-code/         # Language-neutral clean code
│   ├── *-coding-standards/         # Language overlays, discovered by naming convention
│   ├── *-development/              # Domain overlays, discovered by description
│   └── coding-standards-creator/   # Language-standard generator
├── commands/                       # Slash-style phase entries
├── agents/                         # devflow-reviewer and devflow-implementer personas
├── docs/
│   ├── devflow-philosophy.md
│   ├── devflow-core-architecture.md
│   ├── devflow-delivery-contract-redesign.md
│   ├── devflow-internal-quality.md
│   ├── guides/
│   └── asserts/
├── scripts/                        # Repository consistency checks
├── tests/
├── CONTRIBUTING.md
└── README.zh-CN.md
```

Component truth and change history live together under the target component's `specs/` directory:

```text
specs/
├── spec.md
├── design.md
├── changes/ARXXX-<topic>/
│   ├── change.json
│   ├── srs.md
│   ├── delta-spec.md
│   ├── delta-design.md
│   ├── tasks.md
│   ├── traceability.md
│   ├── reviews/
│   └── closeout.md
└── archive/YYYY-MM-DD-ARXXX-<topic>/
```

---

## Scope

DevFlow covers the engineering segment from an accepted requirement to a reviewed implementation and closeout. It does not cover product discovery, release operations, system/integration/acceptance testing, incident management, or production rollout. It also does not make business direction, priority, acceptance-threshold, or architecture-boundary decisions on behalf of the team.

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). Keep skills concrete, verifiable, example-driven, and light on process boilerplate.

---

## License

[MIT](LICENSE)
