# DevFlow

[English](README.md) | [中文](README.zh-CN.md)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
![Version](https://img.shields.io/badge/version-v1.0.0-blue.svg)
![Core](https://img.shields.io/badge/core-three%20quality%20layers-green.svg)
![Adapter](https://img.shields.io/badge/adapter-OpenCode-blue.svg)

**Artifact-first SDD, gated TDD, role-separated reviews, and a rewritten internal-quality layer for AI coding agents.**

DevFlow is a development-stage workflow for AI coding agents. It takes an accepted AR / DTS / CHANGE work item through specification, design, TDD implementation, independent review, completion gating, and closeout. The next step is recovered from durable artifacts, not chat memory.

DevFlow Core maps directly to the three quality layers in [`docs/devflow-philosophy.md`](docs/devflow-philosophy.md): SDD for intent correctness, TDD for functional correctness, and a rewritten internal-quality layer for design and code quality. Language rules and domain constraints are extension skills, such as `c-coding-standards`, `cpp-coding-standards`, and `automotive-embedded-development`. See [`docs/devflow-core-architecture.md`](docs/devflow-core-architecture.md) and [`docs/devflow-internal-quality.md`](docs/devflow-internal-quality.md).

DevFlow is intentionally narrower than an idea-to-product workflow. It does not own product discovery, release operations, system / integration / acceptance testing, or runtime incident management. It starts after the team has accepted the requirement or problem report.

> **Status - vNext architecture work**: DevFlow Core is being separated from platform adapters and language/domain extensions. OpenCode remains the first supported adapter.

---

## Command Intents

OpenCode v1 uses natural language plus automatic skill discovery. The `commands/` directory documents slash-style intents that teams can wire into their client, but every command is a bias, not a bypass: `using-devflow` first applies the family-level DevFlow principles and discovery rules, while `devflow-router` owns repository-evidence checks and runtime next-node decisions.

| What you're doing | Command intent | Key principle |
|---|---|---|
| Enter or resume DevFlow | [`/devflow`](commands/devflow.md) | Route from artifacts |
| Define what to build | [`/devflow-specify`](commands/devflow-specify.md) | Spec before design or code |
| Plan how to build it | [`/devflow-design`](commands/devflow-design.md) | Design options before a chosen design |
| Build one active task | [`/devflow-build`](commands/devflow-build.md) | RED -> GREEN -> REFACTOR with fresh evidence |
| Review design / code / test (standalone or in-flow) | [`/devflow-review`](commands/devflow-review.md) | Intent-driven, independent reviewer, never self-review |
| Close engineering work | [`/devflow-ship`](commands/devflow-ship.md) | Reviews and gates before closeout |
| Fix a DTS / hotfix | [`/devflow-fix`](commands/devflow-fix.md) | Reproduce, root-cause, then make the minimal safe fix |

Reviews are never self-review shortcuts. The one invariant is an **independent reviewer subagent** for spec, component-design, AR-design, test, and code reviews — never the author or parent session. In-flow reviews are dispatched by `devflow-router`; the standalone [`/devflow-review`](commands/devflow-review.md) command can run on any target the user names and dispatches the same independent reviewer directly (per the dispatch protocol's "router or upstream leaf").

---

## Quick Start

### OpenCode

OpenCode is the first supported adapter. You can keep the skill pack as a sibling repository or vendor it into the component repository where work items live. There is no plugin to install: OpenCode discovers every `SKILL.md` under `skills/` automatically, and the shared conventions and behavior contract live in [`using-devflow`](skills/using-devflow/SKILL.md), not in a copied root file.

#### Option A - Sibling Skill Pack

```bash
git clone https://github.com/hujianbest/devflow.git ~/devflow
cd /path/to/your-component-repo
ln -s ~/devflow/skills .opencode-skills   # or add ~/devflow/skills as an extra OpenCode skills root
```

Then point OpenCode at the linked `skills/` directory.

#### Option B - Vendored

```bash
cd /path/to/your-component-repo
git subtree add --prefix .devflow https://github.com/hujianbest/devflow.git v1.0.0 --squash
```

Then point OpenCode at `.devflow/skills/`.

#### Optional - Project overrides

DevFlow does not ship a root `AGENTS.md`. If your component repository needs to override DevFlow's default artifact paths, templates, coding standards, or execution mode, create your own `AGENTS.md` with a `## Project overrides` section in the component repository root; `using-devflow` reads it and lets it override the equivalent defaults. Without it, the defaults baked into `using-devflow` apply.

More setup detail: [`docs/guides/opencode-setup.md`](docs/guides/opencode-setup.md).

### Try It

```text
Use DevFlow from this repo. Start with using-devflow.
I want to clarify AR12345 for the notifications component.
Do not jump straight to code.
```

If process artifacts already exist:

```text
Continue AR12345 with DevFlow. Read features/AR12345-*/progress.md and route me to the next step.
```

---

## See It Work

```text
You:       Use DevFlow to clarify AR12345.

DevFlow:   Enters through using-devflow, writes or revises the requirement
           artifact, and routes to independent spec review.

You:       Use DevFlow to design the approved AR.

DevFlow:   Checks whether component-impact design is required, records design
           options, writes the AR implementation design with embedded test
           design, and routes both designs through independent reviews.

You:       Use DevFlow to build the current active task.

DevFlow:   Locks one Current Active Task, prepares an Implementer Context Pack,
           runs RED -> GREEN -> REFACTOR, and records evidence in task-board,
           implementation-log, and evidence paths.

You:       Use DevFlow to verify and close this work.

DevFlow:   Dispatches test review, code review, completion gate, and finalize.
           It promotes long-term AR assets only during closeout.
```

For a DTS or hotfix, DevFlow first reproduces the issue and records root cause in `devflow-problem-fix`, then returns to the same design / build / review / gate chain as needed.

---

## Skill Catalog

DevFlow ships one public entry meta-skill, 13 canonical `devflow-*` runtime nodes, and third-layer extension skills. The roles are distinct:

- **Meta (`using-devflow`)** discovers which skill applies, carries the always-on behavior constitution, and hosts the shared conventions every other skill follows.
- **Runtime router (`devflow-router`)** turns artifact evidence into the single next canonical node.
- **Internal quality core** defines generic design and code quality in [`docs/devflow-internal-quality.md`](docs/devflow-internal-quality.md).
- **Coding standards skills** such as `c-coding-standards` and `cpp-coding-standards` provide language-specific rules.
- **Domain constraint skills** such as `automotive-embedded-development` provide domain-specific constraints across the full flow.

### Meta And Routing

| Skill | What it does | Use when |
|---|---|---|
| [`using-devflow`](skills/using-devflow/SKILL.md) | Public entry principles and DevFlow skill discovery | Starting a session or expressing a high-level DevFlow intent |
| [`devflow-router`](skills/devflow-router/SKILL.md) | Evidence-based runtime router and recovery controller | Continuing from artifacts or consuming review / gate outcomes |

### Define

| Skill | What it does | Use when |
|---|---|---|
| [`devflow-specify`](skills/devflow-specify/SKILL.md) | Turns AR / DTS / CHANGE intent into testable requirements | Writing or revising a reviewable spec |
| [`devflow-spec-review`](skills/devflow-spec-review/SKILL.md) | Reviews specs for clarity, completeness, and testability | A spec artifact is ready for independent review |

### Plan

| Skill | What it does | Use when |
|---|---|---|
| [`devflow-component-design`](skills/devflow-component-design/SKILL.md) | Writes or revises component implementation design | An AR has component-impact (touches SOA interfaces, dependencies, or state machines) |
| [`devflow-component-design-review`](skills/devflow-component-design-review/SKILL.md) | Reviews component design with role separation | Component design needs an independent verdict |
| [`devflow-ar-design`](skills/devflow-ar-design/SKILL.md) | Produces AR implementation design with embedded test design | Approved requirements need code-level design before TDD |
| [`devflow-ar-design-review`](skills/devflow-ar-design-review/SKILL.md) | Reviews AR design and test design | AR design is ready for independent review |

### Build, Verify, And Close

| Skill | What it does | Use when |
|---|---|---|
| [`devflow-tdd-implementation`](skills/devflow-tdd-implementation/SKILL.md) | Implements one active task with task preflight, RED/GREEN/REFACTOR, and evidence | A reviewed design is ready for TDD implementation |
| [`devflow-test-review`](skills/devflow-test-review/SKILL.md) | Reviews test effectiveness and fail-first evidence | TDD evidence is ready for independent test review |
| [`devflow-code-review`](skills/devflow-code-review/SKILL.md) | Reviews implementation quality, coding standards, and domain constraints | Code is ready for independent review |
| [`devflow-completion-gate`](skills/devflow-completion-gate/SKILL.md) | Decides whether evidence is sufficient to complete or continue | Reviews are present and a completion decision is needed |
| [`devflow-finalize`](skills/devflow-finalize/SKILL.md) | Writes closeout and promotes long-term assets | Completion gate allows closeout |
| [`devflow-problem-fix`](skills/devflow-problem-fix/SKILL.md) | Reproduces, root-causes, and scopes DTS / hotfix work | A shipped-behavior defect or urgent problem needs controlled recovery |

### Internal Quality Extensions

These are **not** flow nodes. They provide third-layer quality constraints consumed by design / build / review / gate nodes. They never write `progress`/handoff, never produce a verdict, and never change the flow topology.

| Skill | What it does | Invoked by |
|---|---|---|
| [`docs/devflow-internal-quality.md`](docs/devflow-internal-quality.md) | Generic internal-quality model for design and code quality | Design, implementation, code review, completion gate |
| [`c-coding-standards`](skills/c-coding-standards/SKILL.md) | C coding standards, tooling, static analysis, pointer/memory/resource rules | C work items |
| [`cpp-coding-standards`](skills/cpp-coding-standards/SKILL.md) | C++ coding standards, RAII/lifetime/templates/ABI rules | C++ work items |
| [`automotive-embedded-development`](skills/automotive-embedded-development/SKILL.md) | Automotive embedded domain constraints across the full DevFlow lifecycle | Automotive embedded work items |

---

## The DevFlow Method

DevFlow is not a prompt collection. It is a controlled engineering workflow for agents.

| Layer | DevFlow method | Why it matters |
|---|---|---|
| Intent | Spec-anchored SDD | Keeps scope, constraints, and acceptance criteria in reviewable files |
| Planning | Design options and review gates | Makes architecture, interfaces, risks, and test design explicit before code |
| Internal quality | Internal-quality core + coding standards + domain constraints | Keeps code and design maintainable, readable, evolvable, and reviewable |
| Execution | Gated TDD | Requires fail-first evidence, GREEN verification, and one active task at a time |
| Routing | Artifact-based recovery | Lets another agent resume from `progress.md`, reviews, evidence, and completion records |
| Review | Role-separated subagents | Prevents authoring and approval from collapsing into one session |
| Verification | Test review, code review, completion gate | Separates "tests ran" from "evidence is sufficient" |
| Closeout | Long-term asset promotion | Syncs accepted specs and designs into `docs/` only when the gate allows it |

---

## How Skills Work

Each skill is a self-contained operating procedure:

```text
SKILL.md
├── Frontmatter classifier
├── Overview and trigger conditions
├── Hard gates and object contract
├── Step-by-step workflow
├── Required artifacts and evidence
├── Review or gate contract
├── Red flags and common rationalizations
├── Verification checklist
└── Local DevFlow conventions
```

Key design choices:

- **Evidence over memory.** Routing reads files such as `features/<id>/progress.md`, reviews, approvals, evidence, and completion records.
- **Canonical names only.** `Next Action Or Recommended Skill` must be one of the canonical `devflow-*` nodes; `using-devflow`, coding standards skills, and domain constraint skills are never written into runtime handoff fields.
- **Single source of truth for conventions.** Artifact layout, progress fields, handoff fields, profiles, and the canonical node list live once in the [`using-devflow`](skills/using-devflow/SKILL.md) meta-skill's "DevFlow 共同约定" section; every skill references it instead of copying boilerplate.
- **Internal quality as extensions, not stages.** Internal-quality constraints raise the bar inside existing nodes without adding flow stages or breaking artifact compatibility.
- **Controlled subagents.** `devflow-router` is the only reviewer dispatcher; `devflow-tdd-implementation` is the only implementer dispatcher.
- **No self-verification.** Authoring skills write artifacts and hand off; independent reviewers return verdicts and do not edit production artifacts.
- **Local references.** Each skill owns its `references/`; there is no shared `skills/docs/` dependency.

---

## Artifact Model

Default process artifacts live under the component repository's `features/<id>/` directory:

```text
features/<id>/
  README.md
  progress.md
  requirement.md
  ar-design-draft.md
  component-design-draft.md
  tasks.md
  task-board.md
  traceability.md
  implementation-log.md
  reviews/
  evidence/
  completion.md
  closeout.md
```

Long-term assets live under the component repository's `docs/` directory:

```text
docs/
  component-design.md
  ar-specs/                  # AR requirement specs promoted from features/<id>/requirement.md
  ar-designs/                # AR implementation designs promoted from features/<id>/ar-design-draft.md
  interfaces.md              # optional, read-on-presence
  dependencies.md            # optional, read-on-presence
  runtime-behavior.md        # optional, read-on-presence
```

Project-level `AGENTS.md` may override equivalent paths and templates. Closed work items stay under `features/<id>/` so traceability links remain stable.

---

## Project Structure

```text
devflow/
├── commands/                         # Slash-style command intent definitions
├── agents/                           # Reviewer / implementer role mirrors
├── skills/                           # 1 meta + 13 canonical devflow-* nodes + extension skills
│   ├── using-devflow/                #   Meta: discovery + behavior constitution + shared conventions
│   ├── devflow-router/               #   Runtime evidence router
│   ├── devflow-specify/
│   ├── devflow-spec-review/
│   ├── devflow-component-design/
│   ├── devflow-component-design-review/
│   ├── devflow-ar-design/
│   ├── devflow-ar-design-review/
│   ├── devflow-tdd-implementation/
│   ├── devflow-test-review/
│   ├── devflow-code-review/
│   ├── devflow-completion-gate/
│   ├── devflow-finalize/
│   ├── devflow-problem-fix/
│   ├── c-coding-standards/           #   Coding standards extension: C
│   ├── cpp-coding-standards/         #   Coding standards extension: C++
│   └── automotive-embedded-development/
├── docs/
│   ├── devflow-core-architecture.md  # DevFlow Core architecture
│   ├── devflow-internal-quality.md   # Rewritten internal-quality layer
│   └── guides/
│       └── opencode-setup.md
├── CHANGELOG.md
├── CONTRIBUTING.md
├── LICENSE
└── README.zh-CN.md
```

Each skill owns its `SKILL.md` plus a local `references/` directory; the shared conventions (artifact layout, `progress.md` / handoff fields, profiles, and the canonical node list) live once in [`using-devflow`](skills/using-devflow/SKILL.md) and every other skill references them instead of copying boilerplate.

---

## Why DevFlow?

AI coding agents often jump from request to implementation. DevFlow gives them a narrower, harder path: clarify the accepted work item, design before slicing work, prove behavior with TDD, separate reviewers from authors, and close the loop with durable evidence.

DevFlow also draws a clear boundary around shipping. It can close engineering work and produce traceable handoff artifacts, but deployment, rollout, monitoring, rollback, and post-launch operations stay with the project's production systems.

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). Keep skills specific, verifiable, artifact-first, independently installable, and role-separated.

## License

[MIT](LICENSE) - use these skills in your projects, teams, and tools.
