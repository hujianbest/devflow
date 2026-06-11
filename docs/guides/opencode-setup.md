# OpenCode Adapter Setup

This guide explains how to use DevFlow through the [OpenCode](https://opencode.ai) adapter. OpenCode is the first supported runtime adapter; it is not part of the DevFlow quality core.

## Overview

DevFlow integrates with OpenCode through:

- The [`using-devflow`](../../skills/using-devflow/SKILL.md) entry skill — the three-layer quality model, workflow map, artifact conventions, and behavior rules.
- OpenCode's built-in `skill` tool, which automatically discovers any `SKILL.md` under `skills/`.
- Optional slash-style commands under `commands/` for teams that prefer explicit phase entry.
- An optional project-level `AGENTS.md` `## Project overrides` section in your component repository to override default artifact paths and templates.

This is an **agent-driven** workflow: skills are selected automatically by intent. Slash commands are thin pointers, not a separate mechanism.

## Installation

### Option A — Skill pack as a sibling

```bash
git clone https://github.com/hujianbest/devflow.git ~/devflow
cd /path/to/your-component-repo
ln -s ~/devflow/skills .opencode-skills   # or add ~/devflow/skills as an extra skills root
```

### Option B — Vendored

```bash
cd /path/to/your-component-repo
git subtree add --prefix .devflow https://github.com/hujianbest/devflow.git --squash main
```

Then point OpenCode at `.devflow/skills/`.

### Verify discovery

```text
List the DevFlow skills you can see, and tell me which one you would load
if I asked to start a new feature.
```

The agent should list the core skills (`using-devflow`, `devflow-specify`, `devflow-design`, `devflow-tdd`, `devflow-clean-code`, `devflow-review`, `devflow-fix`) plus the language/domain extensions (`c-coding-standards`, `cpp-coding-standards`, `embedded-development`, `automotive-development`), and pick `using-devflow` as the entry.

## How it works

### Skill discovery and invocation

OpenCode reads each skill's YAML frontmatter `description` (triggering conditions) and loads the skill body when the request matches. Examples:

| User says… | Agent loads |
|---|---|
| "Help me clarify AR12345" | `using-devflow` → `devflow-specify` |
| "Continue AR12345" | `using-devflow` (recovers stage from `features/AR12345-*/` artifacts) |
| "Design the approved spec" | `devflow-design` (+ applicable language/domain skills) |
| "Implement the next task" | `devflow-tdd` + `devflow-clean-code` (+ language/domain skills) |
| "Review the tests / the code" | `devflow-review` (dispatches an independent reviewer subagent) |
| "Fix DTS67890" | `devflow-fix` |

### Lifecycle mapping

```text
SPECIFY   devflow-specify        → spec.md      (human confirms)
DESIGN    devflow-design         → design.md    (human confirms)
BUILD     devflow-tdd            → code + tests, tasks.md
REVIEW    devflow-review         → reviews/     (human confirms verdict)
FIX       devflow-fix            → fix.md, then back through TDD
```

Overlay skills (`devflow-clean-code`, `c/cpp-coding-standards`, `embedded/automotive-development`) are consumed inside these phases; they are constraints, not phases.

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
