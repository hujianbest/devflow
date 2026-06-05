# AGENTS.md — DevFlow on OpenCode

This file is the **hard contract** for any OpenCode agent that loads DevFlow skills. It is read by OpenCode at session start.

The DevFlow skill family ships under [`skills/`](skills/). High-risk skills carry an `evals/` directory enumerating misuse scenarios they MUST refuse. User-facing setup instructions live in [`docs/guides/opencode-setup.md`](docs/guides/opencode-setup.md).

If you are using DevFlow inside a **component repository** (where the work item lives), copy this file to that repository's root and override paths via the `## Project overrides` section at the bottom.

---

## What DevFlow is

DevFlow is a development-stage workflow for AI coding agents. It takes an accepted SR / AR / DTS / CHANGE work item through specification, design, TDD implementation, independent review, completion gating, and closeout. It is **artifact-first**: the next step is recovered from `features/<id>/progress.md`, `reviews/`, `evidence/`, and `completion.md` — never from chat memory.

DevFlow 2.0 is **decentralized**: the happy path is driven by each skill's `Entry Gate` (self-checks upstream evidence) + `Exit Handoff` (declares the unique next node per the transition table) + evidence self-routing. `devflow-router` is no longer a mandatory hop — it is an **optional arbitration** skill for hard cases only. All cross-skill conventions (paths, fields, profiles, canonical node list, transition table, hard stops, reviewer dispatch) live in a single source of truth: [`references/devflow-conventions.md`](references/devflow-conventions.md). Each skill references it via a one-line `## 约定` section instead of restating it.

DevFlow is **not**:

- a product-discovery workflow (do not invent requirement direction),
- a system / integration / acceptance test workflow (downstream `test-flow` owns that),
- a release / runtime incident workflow,
- a substitute for the team's module architect, dev lead, or developer judgement.

---

## Canonical skills

There are exactly 13 canonical DevFlow nodes. The agent MUST use these names verbatim in any `next_action_or_recommended_skill` field, in `progress.md`, in handoff blocks, and in routing decisions. Free-text next-step labels are forbidden.

```
using-devflow                         (public entry meta-skill; never written into runtime handoff)
devflow-router                        (optional arbitration for hard cases; NOT a default hop)
devflow-specify
devflow-spec-review
devflow-component-design
devflow-component-design-review
devflow-ar-design
devflow-ar-design-review
devflow-tdd-implementation
devflow-test-review
devflow-code-review
devflow-completion-gate
devflow-finalize
devflow-problem-fix
```

The legal `Workflow Profile` set is exactly: `requirement-analysis`, `standard`, `component-impact`, `hotfix`, `lightweight`. The legal `Execution Mode` set is exactly: `interactive`, `auto`.

---

## Skill discovery and invocation

OpenCode automatically discovers every `skills/*/SKILL.md` and exposes them via the built-in `skill` tool. The agent MUST:

1. Read `SKILL.md` frontmatter `description` to decide whether a skill applies.
2. When a skill applies, invoke it via the `skill` tool and follow the body verbatim — including hard gates, workflow steps, output contract, and verification.
3. Never paraphrase or summarise a skill's workflow when invoking it.

For a new session or an ambiguous high-level intent, the **first** skill to load is `using-devflow` (a thin meta-skill: discovery tree + common operating behaviors). From there:

- `using-devflow` maps the intent to a single canonical leaf → enter that leaf's `Entry Gate` in the same turn.
- Continuing an in-flight work item → read `features/<id>/progress.md` (`Current Stage` + `Next Action Or Recommended Skill`) and enter the indicated leaf directly (evidence self-routing); you do **not** need to pass through a router.
- After a leaf finishes, follow its `Exit Handoff` (which declares the unique next node per `references/devflow-conventions.md` §8) and, for reviews, dispatch the reviewer subagent as the orchestrator.
- Only for **hard cases** — evidence conflict, cross-subgraph suspicion, profile-escalation ambiguity, multiple `in_progress` tasks / non-unique next-ready task, or a verdict that cannot map to a unique next step → load the optional `devflow-router` to arbitrate.

---

## Hard rules (non-negotiable)

These rules apply at all times, across every DevFlow skill. Violating any of them is a release blocker.

### 1. Entry discipline

- New session or ambiguous intent → start at `using-devflow`. Do not jump straight to a leaf.
- `using-devflow` is the public entry only. **Never** write `using-devflow` into `Next Action Or Recommended Skill` or any handoff field.
- Continuation / recovery normally proceeds by evidence self-routing (`progress.md`) + the prior leaf's `Exit Handoff`. Only escalate to the optional `devflow-router` when the next step cannot be uniquely determined (hard case).

### 2. Evidence-first

- Decisions are based on disk artifacts (`features/<id>/progress.md`, `reviews/`, `evidence/`, `completion.md`, the long-term `docs/`), not on chat memory.
- When chat history and disk artifacts conflict, the disk artifacts win and the conflict is logged in `progress.md` `Blockers`.

### 3. Role separation — no self-verification

- Reviewers (`devflow-spec-review`, `devflow-component-design-review`, `devflow-ar-design-review`, `devflow-test-review`, `devflow-code-review`) MUST be dispatched as **independent subagents** by the orchestrator (the phase command / session controller; or the optional `devflow-router` when arbitrating). They MUST NOT be inlined into the controller or into the authoring leaf. The `devflow-test-review → devflow-code-review` chain is gated and runs **sequentially** (never parallel fan-out).
- Authoring leaves (`devflow-specify`, `devflow-component-design`, `devflow-ar-design`, `devflow-tdd-implementation`, `devflow-problem-fix`) MUST NOT review their own output. They write artifacts and hand off.
- The `devflow-test-review` and `devflow-code-review` reviewer subagents MUST NOT modify production code or tests. They return findings and hand off.

### 4. Profile discipline

- Profile first-judgment is made by `devflow-specify` (and `devflow-problem-fix` for `hotfix`) and written into `progress.md`; downstream leaves read it and do not silently change it. Ambiguous escalation is arbitrated by the optional `devflow-router`.
- Profile escalation is one-directional: `standard → component-impact` and `standard / component-impact → hotfix` are allowed; downgrades are forbidden.
- Cross-subgraph switching is forbidden: a single work item never moves between `requirement-analysis` and any implementation profile. SR-derived candidate ARs require **new** AR work items.
- `requirement-analysis` profile is forbidden from routing to `devflow-ar-design`, `devflow-ar-design-review`, `devflow-tdd-implementation`, `devflow-test-review`, `devflow-code-review`, `devflow-completion-gate`, `devflow-problem-fix`.

### 5. Gate discipline

- AR design without an embedded test-design section → MUST NOT enter `devflow-tdd-implementation`. Return to `devflow-ar-design`.
- TDD complete without a `devflow-test-review` verdict → MUST NOT enter `devflow-code-review`.
- `devflow-code-review` verdict missing → MUST NOT enter `devflow-completion-gate`.
- `devflow-completion-gate` not passed → MUST NOT enter `devflow-finalize` (implementation closeout).
- Component-impact work with missing `docs/component-design.md` → blocked until `devflow-component-design` runs.
- Implementation closeout requires `docs/ar-specs/AR<id>-<slug>.md` (promoted from `features/<id>/requirement.md`) and `docs/ar-designs/AR<id>-<slug>.md` (promoted from `features/<id>/ar-design-draft.md`) to exist or be promoted by `devflow-finalize`.
- `auto` Execution Mode does **not** waive any review, gate, approval, or evidence requirement. It only changes whether the controller pauses for human confirmation between nodes.

### 6. Subagent context discipline

- DevFlow uses a controlled two-track subagent model:
  - Reviewer subagents are dispatched by the orchestrator (the phase command / session controller; or the optional `devflow-router` when arbitrating). Authoring leaves never dispatch reviewers of their own output.
  - `devflow-tdd-implementation` is the only dispatcher for implementer subagents.
  No leaf may spawn coordinators or nested personas; personas never invoke other personas.
- The controller session must stay small. When `devflow-tdd-implementation` dispatches an implementer subagent, it MUST pass the curated **Implementer Context Pack** (see `skills/devflow-tdd-implementation/SKILL.md`) and not the full chat history.
- Implementer subagents return one of `DONE`, `DONE_WITH_CONCERNS`, `NEEDS_CONTEXT`, `BLOCKED`. `NEEDS_CONTEXT` stays inside `devflow-tdd-implementation` (re-pack and retry). Only routing / profile / scope blockers escalate to the optional `devflow-router`.

### 7. Anti-rationalization

Each DevFlow leaf carries a `## 反向理由化（Common Rationalizations）` table. When the agent finds itself reaching for one of those excuses ("I'll add the test design later", "the design is obvious", "the user said `auto` so I can skip review"), it MUST stop, name the rationalization, and follow the documented counter-action — not push past it.

### 8. Team-role boundary

DevFlow does not make business, scope, priority, architecture, or interface-contract decisions. When such a decision is required, the agent stops and surfaces the question to the responsible team role (requirement owner, module architect, dev lead). It does not silently choose.

---

## Canonical fields

`features/<id>/progress.md` MUST use these exact field names:

- `Work Item Type` — `SR | AR | DTS | CHANGE`
- `Work Item ID` — e.g. `SR1234`, `AR12345`, `DTS67890`, `CHANGE123`
- `Owning Component` — required for `AR | DTS | CHANGE`
- `Owning Subsystem` — required for `SR`
- `Workflow Profile` — one of the five legal values above
- `Execution Mode` — `interactive | auto`
- `Current Stage` — current canonical DevFlow node
- `Pending Reviews And Gates`
- `Last Verdict` — the most recent review / gate conclusion (input to evidence self-routing)
- `Next Action Or Recommended Skill` — exactly one canonical node, never `using-devflow`, never free text
- `Blockers`
- `Last Updated`

For implementation profiles, `progress.md` additionally carries `Current Active Task`, `Task Plan Path`, `Task Board Path`. Multiple `in_progress` tasks or ambiguous next-ready tasks are workflow blockers and force `reroute=true`.

The authoritative definition of every field, profile, the transition table, and hard stops is [`references/devflow-conventions.md`](references/devflow-conventions.md).

Handoff blocks MUST use these field names:

```
current_node
work_item_id
owning_component | owning_subsystem
result | verdict
artifact_paths
record_path                 # when a review/gate/verification record exists
evidence_summary
traceability_links
blockers
next_action_or_recommended_skill
reroute                     # boolean (legacy alias: reroute_via_router)
```

---

## Default artifact layout

Component repository layout (project `AGENTS.md` may override):

```text
<component-repo>/
  docs/
    component-design.md           # long-term component design
    ar-specs/                     # long-term AR requirement specs
      AR<id>-<slug>.md
    ar-designs/                   # long-term AR designs
      AR<id>-<slug>.md
    interfaces.md                 # optional, read-on-presence
    dependencies.md               # optional, read-on-presence
    runtime-behavior.md           # optional, read-on-presence
  features/
    SR<id>-<slug>/                # SR analysis process artifacts
    AR<id>-<slug>/                # AR implementation process artifacts
    DTS<id>-<slug>/               # defect / hotfix process artifacts
    CHANGE<id>-<slug>/            # lightweight change process artifacts
```

**Read-on-presence**:

- Component-impact work blocks if `docs/component-design.md` is missing.
- Implementation closeout blocks if `docs/ar-specs/AR<id>-<slug>.md` is missing or out of date (promoted from `features/<id>/requirement.md`).
- Implementation closeout blocks if `docs/ar-designs/AR<id>-<slug>.md` is missing or out of date (promoted from `features/<id>/ar-design-draft.md`).
- Optional assets (`docs/interfaces.md`, `docs/dependencies.md`, `docs/runtime-behavior.md`) are loaded only if the project enables them; absence is recorded as `N/A (project optional asset not enabled)` and is not a blocker.
- Closed work items stay under `features/<id>/`. Do **not** move them to `features/archived/` — it breaks traceability links.

---

## Reviewer dispatch

When the orchestrator (the phase command / session controller; or the optional `devflow-router` when arbitrating) reaches a review node, it MUST:

1. Construct a minimal review request (`target_skill`, `work_item_id`, `owning_component`, `primary_artifact`, `supporting_context`, `agents_md_anchor`, `expected_return_contract`).
2. Dispatch an **independent subagent** seeded with the matching reviewer skill as its system prompt:
   - `devflow-spec-review` → `skills/devflow-spec-review/SKILL.md`
   - `devflow-component-design-review` → `skills/devflow-component-design-review/SKILL.md`
   - `devflow-ar-design-review` → `skills/devflow-ar-design-review/SKILL.md`
   - `devflow-test-review` → `skills/devflow-test-review/SKILL.md`
   - `devflow-code-review` → `skills/devflow-code-review/SKILL.md`
3. Consume the structured reviewer return (`verdict`, `findings`, `next_action_or_recommended_skill`, `reroute`).
4. Never let the controller "score" the artifact alongside the reviewer — that is inlined review and is forbidden.
5. Keep the gated chain sequential: dispatch `devflow-code-review` only after `devflow-test-review` returns a passing verdict. The detailed protocol is [`references/reviewer-dispatch-protocol.md`](references/reviewer-dispatch-protocol.md).

---

## Common failure modes (stop and re-route)

| Symptom | Required action |
|---|---|
| Agent jumps to `devflow-tdd-implementation` because the user said "build it" | Re-enter `using-devflow` / read `progress.md`; `devflow-tdd-implementation`'s `Entry Gate` confirms a reviewed AR design with embedded test design exists, else returns to `devflow-ar-design` |
| Agent inlines a "quick review" of its own AR design | Discard the inlined review, dispatch `devflow-ar-design-review` as an independent subagent |
| Agent treats `auto` Execution Mode as permission to skip a review | Stop; `auto` only removes inter-node confirmations, not review/gate/approval evidence |
| Agent silently downgrades `component-impact` back to `standard` after design lands | Forbidden; profile is monotonic upward within an implementation work item |
| Agent enters `devflow-ar-design` for an SR work item | Forbidden cross-subgraph; SR closes via `devflow-finalize` (analysis closeout); candidate ARs become **new** AR work items |
| Agent writes a free-text `Next step: ...` instead of a canonical node | Reject the handoff; require one canonical `devflow-*` node |

---

## Project overrides

Component repositories that consume DevFlow MAY override the defaults below in their own `AGENTS.md`:

- Long-term asset paths (`docs/component-design.md`, `docs/ar-designs/`, optional sub-assets).
- Process artifact paths (`features/<id>/...`).
- Required template paths (`requirement.md`, `ar-design-draft.md`, `component-design-draft.md`, `progress.md`).
- Coding standards, static-analysis tools, MISRA / CERT subset enforcement.
- Team role names (the canonical roles are *requirement owner*, *module architect*, *dev lead*, *developer*; equivalents like *tech lead*, *module owner*, *IC engineer*, *SRE* map onto these).
- Additional `Pending Reviews And Gates` entries required by team policy.

Overrides MUST be additive or substitutive on equivalent paths. Overrides that weaken hard gates (e.g., "skip code review for hotfix") are forbidden.
