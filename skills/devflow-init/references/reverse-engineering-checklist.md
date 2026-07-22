# Read-only reverse-engineering checklist

Use this checklist to establish evidence for an existing component baseline. It does not authorize business-code edits, generated-output refreshes, deployments, migrations or stateful environment probes.

## 1. Scope and snapshot

- [ ] Resolve one `<component-root>`.
- [ ] Obtain explicit `componentMode: existing`.
- [ ] Record an immutable source revision.
- [ ] If an active AR exists, verify its `change.json.baseRevision` without changing it.
- [ ] Identify whether `specs/spec.md`, `specs/design.md`, both or neither need work.
- [ ] If only one is missing or draft, mark the other read-only and use it for cross-checking.
- [ ] List ignored, generated, vendored and inaccessible areas.
- [ ] Record tool or permission limitations before drawing conclusions.

## 2. Existing descriptions

- [ ] Component overview, ownership and boundaries.
- [ ] Upstream requirements and acceptance criteria.
- [ ] API guides, operational procedures and support contracts.
- [ ] Architecture or decision records.
- [ ] Release, upgrade, compatibility and deprecation notes.
- [ ] Known debt, incidents and limitations.

For every statement, record a `/` path and section anchor. “Documented” does not mean “current”; compare its revision and claims with other evidence.

## 3. Public API, IDL and schemas

- [ ] Exported functions, services, routes, messages and events.
- [ ] Inputs, outputs, units, ranges, defaults and optionality.
- [ ] Error codes and observable failure behavior.
- [ ] Sync/async semantics, ordering and idempotency.
- [ ] Version negotiation, compatibility and deprecation markers.
- [ ] Data schemas, persistence formats and migration definitions.
- [ ] Known providers and consumers.

An interface definition verifies shape and declared constraints. Consumer obligations, business meaning and compatibility duration remain unknown unless separately sourced.

## 4. Tests

- [ ] Unit, component, integration, contract, end-to-end and regression tests.
- [ ] Fixtures, golden files, snapshots and property tests.
- [ ] Positive, boundary, invalid-input and failure-path cases.
- [ ] Timing, capacity, resource and concurrency assertions.
- [ ] Mocks or fakes that reveal expected collaborators.
- [ ] Disabled, flaky or quarantined tests and stated reasons.
- [ ] Gaps between public paths and test coverage.

Record test name and assertion anchor. A passing or existing test verifies current encoded expectation; it does not prove that expectation is the intended requirement.

## 5. Source

- [ ] Public entry points and adapters.
- [ ] Internal units and responsibility boundaries.
- [ ] Dependency direction and external integrations.
- [ ] State machines, transitions and invariants.
- [ ] Validation and error translation.
- [ ] Data ownership, lifetime and persistence.
- [ ] Threads, tasks, callbacks, locks, queues and ordering.
- [ ] Resource acquisition, limits, exhaustion and release.
- [ ] Retry, timeout, cancellation, recovery and degradation.
- [ ] Logging, metrics, tracing and health reporting.
- [ ] Startup, shutdown and partial-initialization rollback.

Record symbol and line/range anchors where practical. Source verifies current structure and behavior, not intent, rationale or stability commitment.

## 6. Configuration

- [ ] Configuration keys, types and defaults.
- [ ] Environment variables and secret references.
- [ ] Feature flags and conditional behavior.
- [ ] Validation, precedence and reload semantics.
- [ ] Platform, locale and environment conditions.
- [ ] Values that look like thresholds or budgets.

Treat configured numbers as current values. Ask before declaring them required acceptance thresholds.

## 7. Build and dependencies

- [ ] Build entry points, targets and output artifacts.
- [ ] Source generation and generated-file ownership.
- [ ] Compile flags, platform variants and feature switches.
- [ ] Direct and transitive runtime dependencies.
- [ ] Packaging, signing and version metadata.
- [ ] Test/build separation and required toolchains.

Read definitions only. Do not run a command that may rewrite lock files, generated code or caches required to remain untouched.

## 8. Deployment and operations

- [ ] Deployment units, topology and environment variants.
- [ ] Startup order, readiness, liveness and shutdown.
- [ ] Storage, network, service-account and permission dependencies.
- [ ] Rollout, rollback and migration definitions.
- [ ] Scaling, replication and failover declarations.
- [ ] Monitoring, alerting and operational limits.

A deployment file verifies declared configuration, not actual runtime state in every environment. Do not deploy or mutate an environment during init.

## 9. Evidence normalization

For each fact, capture:

| Field | Required content |
|---|---|
| Fact ID | Stable local ID |
| Statement | One atomic claim |
| Class | `verifiable`, `human-confirmed`, or `unknown` |
| Source | Revision plus `/` path, symbol/test/config/section anchor, or human confirmation ID |
| Scope | Conditions, platform, build variant or environment |
| Normative disposition | observed-only, required, excluded or undecided |
| Conflict | Conflicting source or none |

- [ ] Split claims that need different classes.
- [ ] Do not use confidence adjectives as a substitute for a class.
- [ ] Preserve conflicting evidence; do not select a winner without authority.
- [ ] Keep the evidence ledger in the canonical document provenance sections; do not add a new component-root artifact.

## 10. Blocking questions

- [ ] Component responsibility and ownership are confirmed.
- [ ] Externally observable behavior and error semantics are confirmed.
- [ ] Interface consumers and compatibility commitments are confirmed where material.
- [ ] Security, privacy and safety boundaries are confirmed.
- [ ] Required performance, real-time, capacity and resource thresholds are confirmed.
- [ ] Persistence, migration, concurrency and recovery guarantees are confirmed.
- [ ] Source conflicts affecting contract or architecture are resolved.
- [ ] Every blocking question names an owner and the decision it blocks.

Ask questions in small related groups. Include verified context and impact, but do not imply a preferred answer without evidence.

## 11. Final consistency

- [ ] Every canonical normative statement has human confirmation.
- [ ] Every observed-only statement is visibly non-normative.
- [ ] Every design element maps to a specification ID or is labeled implementation detail.
- [ ] Every specification ID has design coverage or an explicit no-design-impact rationale.
- [ ] Names, units, ranges, defaults, states and errors agree across both documents.
- [ ] Both documents cite the same source revision.
- [ ] No blocking unknown remains before independent review.
