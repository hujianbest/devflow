# Contributing to DevFlow

Thanks for your interest in DevFlow. This document describes how to contribute to the skill suite, what makes a good change, and how to keep skills mutually consistent.

## Scope

DevFlow is intentionally narrow:

- It targets the **development stage**: from an accepted requirement through specification, design, TDD implementation, and independent review.
- It is organized as **phase skills** (`devflow-specify`, `devflow-design`, `devflow-tdd`, `devflow-review`, `devflow-ship`, `devflow-fix`, plus the `using-devflow` entry), **overlay skills** (`devflow-clean-code`, the `<language>-coding-standards` family, and domain development skills discovered by description), and **tooling skills** (`coding-standards-creator`).
- New language standards are created with `coding-standards-creator` and must satisfy its structural contract (`skills/coding-standards-creator/references/coding-standards-skill-contract.md`); phase skills reference language standards by convention, so adding a language must not require touching them.
- It does **not** cover product discovery, system / integration / acceptance testing, release operations, or runtime incident response.

The architecture spec is [`docs/devflow-core-architecture.md`](docs/devflow-core-architecture.md); the philosophy (north star) is [`docs/devflow-philosophy.md`](docs/devflow-philosophy.md). When an implementation choice conflicts with the philosophy, the philosophy wins.

## What a good DevFlow skill looks like

DevFlow 2.0 follows two principles. Every change should be judged against them:

1. **Minimal process** — keep only process that produces quality (phase artifacts, human checkpoints, TDD discipline, independent review). Do not add status files, routing layers, handoff schemas, or role machinery.
2. **Maximal substance** — the body of a skill is actionable engineering judgment. Prefer a concrete rule with a before/after code example over an abstract principle. "高内聚低耦合" alone is not a contribution; an operational check for it is.

Concretely, a skill should be:

- **Specific** — rules a model can act on, with examples; not vague advice.
- **Example-driven** — good/bad contrast pairs for anything non-obvious. C/C++ examples are the house style; mark the principle as language-neutral when it is.
- **Verifiable** — a closing checklist with conditions checkable from artifacts and code, not "looks right".
- **Lean** — SKILL.md under ~400 lines; details and templates go to `references/` with clear pointers (progressive disclosure).
- **Independently installable** — references live under each skill's own `references/`; no shared folders other skills must load.

## Skill structure

A `SKILL.md` starts with YAML frontmatter:

- `name` — must equal the directory name.
- `description` — **triggering conditions only** (when to load this skill), not a workflow summary. Front-load concrete trigger keywords; include negative triggers ("不用于…") when adjacent skills overlap.

The body has no mandatory section schema. Recommended shape: overview (core principle in a few sentences) → the substantive judgment sections (with examples) → rationalization rebuttals (3–8 rows, tied to this skill's real decision points) → verification checklist → references table. Write in Chinese (the suite's working language); keep code identifiers and quoted terms in English.

## Cross-skill consistency

- The three-layer model and workflow live in `using-devflow`; other skills reference it instead of restating it.
- Boundaries between skills: specification carries no implementation detail; design decisions are not re-made in TDD; language rules live in coding-standards skills, domain risks in domain skills. When you move a rule, update both sides in the same PR.
- Review criteria live in `skills/devflow-review/references/*-rubric.md` and must stay consistent with the author-side skill they check.

## Validation

Run before submitting:

```bash
python3 scripts/validate_devflow.py
python3 -m pytest tests/
```

The validator checks markdown links, skill frontmatter, the required skill set, and whether active instructions use the current lifecycle vocabulary, paths, and state contract.

## Pull request expectations

- One logical change per PR.
- Update both `README.md` and `README.zh-CN.md` when you change user-facing surface area.
- Update `CHANGELOG.md` under the `Unreleased` heading.
- New rules should cite the failure they prevent (a real bad output, a known LLM rationalization, a class of bugs). Rules without a failure story are candidates for rejection.

## Repository hygiene

- Skill directories: phase skills are `devflow-<verb/noun>`; coding standards are `<language>-coding-standards`; domain constraints are `<domain>-development`. Reference files are `kebab-case.md`.
- Packaged skills must not reference repo-level `docs/` files (they must be deployable standalone).
- Don't add editor-specific directories at the repository root unless part of a deliberate integration release.

## License

By contributing, you agree your contributions are licensed under the [MIT License](LICENSE).
