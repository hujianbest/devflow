# OpenCode Adapter Setup

This guide explains how to use DevFlow through the [OpenCode](https://opencode.ai) adapter. OpenCode is the first supported runtime adapter; it is not part of the DevFlow quality core.

## Overview

DevFlow integrates with OpenCode through:

- The [`using-devflow`](../../skills/using-devflow/SKILL.md) entry skill — the three-layer quality model, workflow map, artifact conventions, and behavior rules.
- OpenCode's built-in `skill` tool, which automatically discovers any `SKILL.md` under `skills/`.
- DevFlow subagents under `agents/`, used by review and implementation phases.
- Slash-style commands under `commands/` for teams that prefer explicit phase entry.
- An optional project-level `AGENTS.md` `## Project overrides` section in your component repository to override default artifact paths and templates. Default `features/` and `docs/` paths are resolved under the target component repository root, not the DevFlow skill-pack directory or a parent workspace.

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

The agent should list the core skills (`using-devflow`, `devflow-specify`, `devflow-design`, `devflow-tdd`, `devflow-clean-code`, `devflow-review`, `devflow-ship`, `devflow-fix`), any discovered language/domain extensions (`<language>-coding-standards` and domain development skills), and the tooling skill `coding-standards-creator`, picking `using-devflow` as the entry. Slash commands such as `/devflow`, `/devflow-specify`, and `/devflow-review` should also be available after the `commands/` files are installed.

## How it works

### Skill discovery and invocation

OpenCode reads each skill's YAML frontmatter `description` (triggering conditions) and loads the skill body when the request matches. Examples:

| User says… | Agent loads |
|---|---|
| "Help me clarify AR12345" | `using-devflow` → `devflow-specify` |
| "Continue AR12345" | `using-devflow` (recovers stage from the target component root's `features/AR12345-*/` artifacts) |
| "Design the approved spec" | `devflow-design` (+ applicable language/domain skills) |
| "Implement the next task" | `devflow-tdd` + `devflow-clean-code` (+ language/domain skills) |
| "Review the tests / the code" | `devflow-review` (dispatches an independent reviewer subagent) |
| "Fix DTS67890" | `devflow-fix` |

### Lifecycle mapping

```text
SPECIFY   devflow-specify        → spec.md + traceability.md + plan.md skeleton
R1        devflow-review         → reviews/spec-review-*.md   (human confirms in attended mode)
DESIGN    devflow-design         → design.md (+ component-design-draft.md)
R2        devflow-review         → reviews/design-review-*.md (human confirms in attended mode)
BUILD     devflow-tdd            → code + tests, plan.md with task progress & evidence lines
                                   (dispatches implementer subagents by default)
R3        devflow-review         → reviews/test-review-*.md, code-review-*.md
SHIP      devflow-ship           → DoD check, promotion to component-root docs/, closeout.md
FIX       devflow-fix            → fix.md, then back through TDD + R3
```

The run mode (`attended` / `unattended`) is confirmed once at workflow start and recorded in plan.md; `unattended` removes human pauses but never removes reviews, records, or critical-finding blocking.

Overlay skills (`devflow-clean-code`, the applicable `<language>-coding-standards`, and domain skills whose descriptions match the work item) are consumed inside these phases; they are constraints, not phases. New language standards are generated from internal team documents via `coding-standards-creator`; new domain skills join by describing their trigger context in frontmatter.

### Reviewer subagents

`devflow-review` dispatches an **independent subagent** seeded with `agents/devflow-reviewer.md` plus the matching rubric from `skills/devflow-review/references/`. The reviewer is read-only on the artifact under review: it returns findings + verdict, never edits. The human confirms the verdict.

## Agent expectations

For DevFlow to work on OpenCode, the agent must follow the behavior rules in [`using-devflow`](../../skills/using-devflow/SKILL.md):

- Surface assumptions before implementing; never silently fill in vague requirements.
- Never write implementation code before a failing test exists (`devflow-tdd`).
- Never let the authoring session review its own output.
- Recover state from disk artifacts, not chat memory.
- Surface business/priority/architecture decisions to the human instead of guessing.

If your agent skips any of the above, fix the agent — do not relax the rule.

## Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| Agent jumps straight to code | `using-devflow` not loaded | Confirm `skills/` is on the skills root; ask the agent to load `using-devflow` |
| Agent "reviews" its own design inline | Self-review | Discard it; require `devflow-review` to dispatch an independent subagent |
| Tests written after implementation | TDD violation | Delete the implementation, restart from RED (`devflow-tdd` Iron Law) |
| Skills not discovered | `skills/` not on the skills root | Verify the symlink / config |
| DevFlow slash commands are missing | `commands/` files were not installed | Copy `commands/devflow*.md` into the OpenCode `commands/` directory |
| Review or build cannot dispatch a DevFlow subagent | `agents/` files were not installed | Copy `agents/*.md` into the OpenCode `agents/` directory |
