# OpenCode Adapter Setup

This guide explains how to use **DevFlow Core** through the [OpenCode](https://opencode.ai) adapter. OpenCode is the first supported runtime adapter; it is not part of the DevFlow quality core.

## Overview

OpenCode supports custom `/commands` but does not have a native plugin system or built-in slash-command marketplace. DevFlow integrates by combining these pieces:

- The [`using-devflow`](../../skills/using-devflow/SKILL.md) entry skill — DevFlow's behavior constitution, three-layer discovery, shared conventions, and extension-skill discovery.
- The built-in `skill` tool, which automatically discovers any `SKILL.md` under `skills/`.
- An optional project-level `AGENTS.md` `## Project overrides` section that you create in your own component repository to override default artifact paths, templates, coding standards, or execution mode.
- Consistent canonical node names so the agent picks the right flow node from natural language and dispatches independent reviewer subagents. Coding standards and domain constraint skills are supporting constraints, not runtime next actions.

This is an **agent-driven** workflow: skills are selected automatically by intent, not invoked through manual slash commands. It mirrors how Claude Code skills behave in practice.

---

## Installation

### Option A — Skill pack repo as a sibling

Use this when you want to keep DevFlow's source separate from your component repository.

1. Clone the DevFlow skill pack:

   ```bash
   git clone https://github.com/hujianbest/devflow.git ~/devflow
   ```

2. In your **component repository** (the repo where the work item lives), point OpenCode at the DevFlow `skills/` directory. Either symlink it:

   ```bash
   cd /path/to/your-component-repo
   ln -s ~/devflow/skills .opencode-skills
   ```

   …or configure your OpenCode workspace to add `~/devflow/skills` as an additional skills root.

3. (Optional) If your team needs to override DevFlow's default artifact paths, templates, coding standards, or execution mode, create an `AGENTS.md` with a `## Project overrides` section in your component repository's root. `using-devflow` reads it and lets it override the equivalent defaults. Without it, the defaults baked into `using-devflow` apply.

4. Confirm OpenCode discovers the skills by asking the agent:

   ```text
   List the DevFlow skills you can see, and tell me which one you would load if I asked to clarify a new AR.
   ```

   The agent should return the 13 canonical nodes, the non-canonical extension skills (`c-coding-standards`, `cpp-coding-standards`, `embedded-development`, `automotive-development`), and pick `using-devflow`.

### Option B — Vendored

Use this when you want DevFlow pinned at a known revision inside your component repository.

```bash
cd /path/to/your-component-repo
git subtree add --prefix .devflow https://github.com/hujianbest/devflow.git v1.0.0 --squash
```

Then point OpenCode at `.devflow/skills/`. Optionally add a project `AGENTS.md` `## Project overrides` section as described in Option A step 3.

---

## How it works

### 1. Skill discovery

Every skill lives at:

```
skills/<skill-name>/SKILL.md
```

OpenCode reads each file's YAML frontmatter `description` (a classifier) and uses it to decide whether to load the skill for the current request. DevFlow descriptions front-load triggering keywords for flow nodes (`spec review`, `AR implementation design`, `component design`, `test review`, `code review`) and extension skills (`C`, `C++`, `embedded`, `automotive`, `ASIL`, `SOA/MDC`, etc.).

### 2. Automatic invocation

The agent evaluates every request, maps it to a DevFlow skill, and invokes it via OpenCode's built-in `skill` tool. Examples:

| User says… | Agent invokes |
|---|---|
| "Help me clarify AR12345" | `using-devflow` → `devflow-specify` |
| "Continue AR12345" | `using-devflow` → `devflow-router` (recovers state from `features/AR12345-*/`) |
| "Review this AR design" | `using-devflow` → `devflow-router` → dispatches `devflow-ar-design-review` subagent |
| "Implement the next task with TDD" | `devflow-router` → `devflow-tdd-implementation` |
| "Fix DTS67890" | `using-devflow` → `devflow-router` (profile = `hotfix`) → `devflow-problem-fix` |
| "Can we close AR12345?" | `devflow-router` → `devflow-completion-gate` |

The user does **not** invoke skills explicitly. There are no `/spec`, `/build`, `/ship` slash commands.

### 3. Lifecycle mapping

The development lifecycle is discovered through `using-devflow` and recovered at runtime through `devflow-router`:

```
CLARIFY    devflow-specify, devflow-spec-review
DESIGN     devflow-component-design, devflow-component-design-review,
           devflow-ar-design, devflow-ar-design-review
BUILD      devflow-tdd-implementation
VERIFY     devflow-test-review, devflow-code-review
GATE       devflow-completion-gate
CLOSE      devflow-finalize
HOTFIX     devflow-problem-fix
```

Internal quality extensions are discovered alongside the flow:

```text
C code       c-coding-standards
C++ code     cpp-coding-standards
Embedded     embedded-development
Automotive   automotive-development
```

These extension skills never appear in `Next Action Or Recommended Skill`.

### 4. Reviewer subagents

Reviews are dispatched as **independent subagents** by `devflow-router`. The reviewer subagent is seeded with the corresponding skill body as its system prompt:

- `devflow-spec-review` → `skills/devflow-spec-review/SKILL.md`
- `devflow-component-design-review` → `skills/devflow-component-design-review/SKILL.md`
- `devflow-ar-design-review` → `skills/devflow-ar-design-review/SKILL.md`
- `devflow-test-review` → `skills/devflow-test-review/SKILL.md`
- `devflow-code-review` → `skills/devflow-code-review/SKILL.md`

Reviewers are read-only on the artifact under review: they return `verdict + findings + next_action`, never edit the artifact themselves. The controller routes the verdict back to the authoring leaf.

---

## Agent expectations (critical)

For DevFlow to work correctly on OpenCode, the agent MUST follow the behavior constitution in [`using-devflow`](../../skills/using-devflow/SKILL.md) (and any project `AGENTS.md` `## Project overrides`). Highlights:

- Always start non-trivial work at `using-devflow`.
- Never write `using-devflow`, a coding-standards skill, or a domain-constraint skill into `Next Action Or Recommended Skill`.
- Never inline a review. Review subagents must be dispatched independently.
- Never let `auto` Execution Mode bypass a review, gate, or approval.
- Never silently downgrade a `Workflow Profile`.
- Always surface team-role decisions (business scope, priority, architecture, interface contracts) instead of guessing.

If your agent skips any of the above, fix the agent — do not relax the rule.

---

## Limitations

- **No native slash commands.** Skills are invoked automatically via natural language and the `skill` tool. If your team prefers explicit commands, you can still wrap them as OpenCode `/commands` that simply forward an instruction like "Use DevFlow to start spec review on the current work item", but runtime routing is still done by `devflow-router`.
- **Skill invocation depends on model compliance.** A weak model may try to skip review or implement past a hard gate. The `using-devflow` behavior constitution and per-skill `## 反向理由化` tables exist precisely to push back on this.
- **No marketplace install.** Use `git clone`, `git subtree`, or a workspace symlink.

---

## Recommended workflow

Use natural language. Examples that map cleanly to DevFlow:

```text
Use DevFlow to clarify AR12345 in this component repo.
Continue AR12345 with DevFlow — read the artifacts and route me to the next step.
Use DevFlow to write the AR implementation design for AR12345 (component-impact: this changes the SOA service signature).
Use DevFlow to implement the current active task with TDD and fresh evidence.
Use DevFlow to review the tests, then the code.
Use DevFlow to decide whether AR12345 can be completed.
Use DevFlow to finalize AR12345.
Use DevFlow to reproduce DTS67890, find the root cause, and scope the minimal safe fix.
```

The agent will:

1. Enter via `using-devflow`.
2. Hand off to `devflow-router` whenever stage / profile / evidence is unclear.
3. Dispatch reviewer subagents (each seeded with the matching `devflow-*-review` skill) as needed.
4. Write process artifacts under `features/<id>/` and promote long-term assets under `docs/` only at `devflow-finalize`.

---

## Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| Agent jumps straight to writing code | `using-devflow` not loaded, or model ignored entry rule | Confirm `skills/` is on the OpenCode skills root and ask the agent to load `using-devflow`; restart the OpenCode session |
| Agent writes `Next step: implement` instead of `Next Action Or Recommended Skill: devflow-tdd-implementation` | Free-text handoff slipped through | Reject the handoff; require canonical node name |
| Agent "reviews" its own AR design inside `devflow-ar-design` | Inlined review | Discard the inlined review; ask the agent to dispatch `devflow-ar-design-review` as a subagent |
| Agent silently skips `devflow-test-review` after TDD | Hard gate violation | Block; route to `devflow-test-review` before any `devflow-code-review` |
| Skills not discovered | `skills/` not on the OpenCode skills root | Verify the symlink / config; ask the agent to "list the DevFlow skills you can see" |

---

## Summary

DevFlow on OpenCode = `using-devflow` (behavior constitution + shared conventions + extension discovery) + `skills/` (13 canonical nodes plus non-canonical extension skills) + automatic `skill`-tool invocation driven by natural language, with an optional project `AGENTS.md` `## Project overrides`. No plugins, no manual commands, full process discipline.
