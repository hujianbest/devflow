# OpenCode Adapter Setup

This guide explains how to use DevFlow through the [OpenCode](https://opencode.ai) adapter. OpenCode is the first supported runtime adapter; it is not part of the DevFlow quality core.

## Overview

DevFlow integrates with OpenCode through:

- The [`using-devflow`](../../skills/using-devflow/SKILL.md) entry skill — the three-layer quality model, workflow map, artifact conventions, and behavior rules.
- OpenCode's built-in `skill` tool, which automatically discovers any `SKILL.md` under `skills/`.
- DevFlow subagents under `agents/`, used by review and implementation phases.
- Slash-style commands under `commands/` for teams that prefer explicit phase entry.
- An optional project-level `AGENTS.md` section for extra constraints and template requirements. Canonical docs, active changes, and archives always remain under the target component root's `specs/` directory.

This is an **agent-driven** workflow: skills are selected automatically by intent. Slash commands are thin pointers, not a separate mechanism.

## Installation

### Option A — User-level install

```bash
# Clone DevFlow into the OpenCode user config directory.
git clone https://github.com/hujianbest/devflow.git ~/.config/opencode/devflow

# Install DevFlow skills, agents, and commands into OpenCode's global directories.
mkdir -p ~/.config/opencode/skills ~/.config/opencode/agents ~/.config/opencode/commands
cp -R ~/.config/opencode/devflow/skills/* ~/.config/opencode/skills/
cp ~/.config/opencode/devflow/agents/*.md ~/.config/opencode/agents/
cp ~/.config/opencode/devflow/commands/devflow*.md ~/.config/opencode/commands/
```

### Option B — Vendored

```bash
cd /path/to/your-component-repo
git subtree add --prefix .devflow https://github.com/hujianbest/devflow.git --squash main

mkdir -p .opencode/skills .opencode/agents .opencode/commands
cp -R .devflow/skills/* .opencode/skills/
cp .devflow/agents/*.md .opencode/agents/
cp .devflow/commands/devflow*.md .opencode/commands/
```

The vendored option keeps DevFlow project-scoped. Update the copied `.opencode/` resources when you update `.devflow`.

### Verify discovery

```text
List the DevFlow skills you can see, and tell me which one you would load
if I asked to start a new feature.
```

The agent should list the core skills (`using-devflow`, `devflow-init`, `devflow-specify`, `devflow-design`, `devflow-tdd`, `devflow-clean-code`, `devflow-review`, `devflow-ship`, `devflow-fix`), any discovered language/domain extensions, and `coding-standards-creator`, picking `using-devflow` as the normal entry. Slash commands including `/devflow-init` should be available after the command files are installed.

## How it works

### Skill discovery and invocation

OpenCode reads each skill's YAML frontmatter `description` (triggering conditions) and loads the skill body when the request matches. Examples:

| User says… | Agent loads |
|---|---|
| "Help me clarify AR12345" | `using-devflow` → `devflow-specify` |
| "Initialize docs for this existing component" | `using-devflow` → `devflow-init` |
| "Continue AR12345" | `using-devflow` (recovers from `specs/changes/AR12345-*/change.json` and `tasks.md`) |
| "Design the approved spec" | `devflow-design` (+ applicable language/domain skills) |
| "Implement the next task" | `devflow-tdd` + `devflow-clean-code` (+ language/domain skills) |
| "Review the tests / the code" | `devflow-review` (dispatches an independent reviewer subagent) |
| "Write the SRS / design / closeout" | the phase skill + `writing-readable-doc` (auto-loaded whenever a document is produced) |
| "这份 spec/design 看不懂，改一下" | `writing-readable-doc` (expression layer only; vague thresholds go back to specify/design) |
| "Fix DTS67890" | `devflow-fix` |

### Lifecycle mapping

```text
PREFLIGHT using-devflow           → create/read change.json; check componentMode and canonical baseline
INIT      devflow-init            → specs/spec.md + specs/design.md (existing components only)
SPECIFY   devflow-specify         → srs.md + delta-spec.md + traceability.md
R1        devflow-review          → reviews/r1-review-*.md
DESIGN    devflow-design          → delta-design.md
R2        devflow-review          → reviews/r2-review-*.md
BUILD     devflow-tdd             → code + tests, tasks.md progress and evidence
                                   (dispatches implementer subagents by default)
R3        devflow-review          → reviews/r3-review-*.md
SHIP      devflow-ship           → DoD, intelligent canonical sync, closeout, archive
FIX       devflow-fix            → defect SRS/delta → R1/R2 → TDD + R3
```

The run mode (`attended` / `unattended`) is confirmed once and recorded in `change.json`; `unattended` removes human pauses but never removes reviews, records, critical-finding blocking, canonical diff review, or final archive confirmation.

Overlay skills (`devflow-clean-code`, `writing-readable-doc`, the applicable `<language>-coding-standards`, and domain skills whose descriptions match the work item) are consumed inside these phases; they are constraints, not phases. New language standards are generated from internal team documents via `coding-standards-creator`; new domain skills join by describing their trigger context in frontmatter.

### DevFlow subagents

DevFlow ships two subagent definitions under `agents/`:

| Agent file | OpenCode agent name | Dispatched by | Role |
|---|---|---|---|
| `agents/devflow-implementer.md` | `devflow-implementer` | `devflow-tdd` (BUILD phase) | Executes one RED→GREEN→REFACTOR task from a packed Context Pack |
| `agents/devflow-reviewer.md` | `devflow-reviewer` | `devflow-review` (R1/R2/R3 and canonical sync) | Independent read-only reviewer; returns findings + verdict |

Each file carries a YAML frontmatter with `description`, `mode: subagent`, and `permission` — these are required for OpenCode to register and discover the agent via its `task` tool.

**How dispatch works on OpenCode**: when a DevFlow skill says "dispatch the `devflow-implementer` subagent", the primary agent (Build) invokes the built-in `task` tool with the agent name `devflow-implementer` and a prompt containing the Context Pack. OpenCode matches the name against registered subagents and spawns a fresh context. The `description` in the agent frontmatter is what lets the model pick the right subagent — without it, OpenCode cannot route the dispatch.

`devflow-review` dispatches an **independent subagent** named `devflow-reviewer`, seeded with the agent definition plus the matching rubric from `skills/devflow-review/references/`. The reviewer is read-only on the artifact under review (`edit: deny` in frontmatter): it returns findings + verdict, never edits. The human confirms the verdict.

## Agent expectations

For DevFlow to work on OpenCode, the agent must follow the behavior rules in [`using-devflow`](../../skills/using-devflow/SKILL.md):

- Surface assumptions before implementing; never silently fill in vague requirements.
- For an existing component without baseline-ready canonical docs, stop and use `devflow-init`; clarify rather than fabricate.
- Never write implementation code before a failing test exists (`devflow-tdd`).
- Never let the authoring session review its own output.
- Recover state from disk artifacts, not chat memory.
- Surface business/priority/architecture decisions to the human instead of guessing.

If your agent skips any of the above, fix the agent — do not relax the rule.

## Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| Agent jumps straight to code | `using-devflow` not loaded | Confirm `skills/` is on the skills root; ask the agent to load `using-devflow` |
| Existing component starts an AR without canonical docs | Baseline preflight was skipped | Stop the AR and run `/devflow-init` |
| Agent "reviews" its own design inline | Self-review | Discard it; require `devflow-review` to dispatch an independent subagent |
| Tests written after implementation | TDD violation | Delete the implementation, restart from RED (`devflow-tdd` Iron Law) |
| Skills not discovered | `skills/` not on the skills root | Verify the symlink / config |
| DevFlow slash commands are missing | `commands/` files were not installed | Copy `commands/devflow*.md` into the OpenCode `commands/` directory |
| Review or build dispatches a generic subagent instead of the DevFlow agent | Agent file missing required frontmatter (`description`, `mode: subagent`) | Ensure `agents/*.md` files have YAML frontmatter; re-copy into OpenCode's `agents/` directory |
| OpenCode cannot find `devflow-implementer` / `devflow-reviewer` | `agents/` files were not installed to OpenCode's discovery path | Copy `agents/*.md` into `~/.config/opencode/agents/` (global) or `.opencode/agents/` (project) |
