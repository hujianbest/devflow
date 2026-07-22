# Canonical baseline review checklist

This review is independent: the reviewer did not author the canonical draft, receives no hidden author reasoning, and does not edit the reviewed files.

## Review input

- [ ] Exact source revision.
- [ ] New or revised canonical draft.
- [ ] Other canonical document used for cross-checking.
- [ ] Source/provenance index with fact classification and confirmation anchors.
- [ ] Human questions, answers, confirmer and scope.
- [ ] Remaining unknowns and their blocking classification.
- [ ] If only one document was missing, a clear statement that the existing document was not modified.

If evidence cannot be read at the recorded revision, return `blocked`; do not review from summaries alone.

## 1. Provenance

- [ ] Every material claim has a source or explicit `unknown`.
- [ ] File anchors use `/` and include symbols, tests, keys or sections where practical.
- [ ] Evidence scope records platform, build variant and environment conditions.
- [ ] Generated, vendored, stale or conflicting sources are identified.
- [ ] Human-confirmed claims include confirmer, time and confirmation scope.
- [ ] No source is cited more broadly than it proves.

## 2. Fact classification

- [ ] Every fact is exactly `verifiable`, `human-confirmed` or `unknown`.
- [ ] Inference and confidence language do not act as hidden fourth classes.
- [ ] Current implementation facts are not automatically written as requirements.
- [ ] Tests are treated as encoded expectations, not unquestionable business intent.
- [ ] Constants and measured behavior are not promoted to required thresholds without human confirmation.
- [ ] Design structure is separated from unverified rationale.
- [ ] Error behavior is separated from unverified semantic or compatibility commitments.

Any invented intent, reason, threshold, historical decision or owner is a blocking finding.

## 3. Canonical specification

- [ ] Scope, non-scope, responsibility and consumers are explicit.
- [ ] Stable requirement IDs are unique and usable by future deltas.
- [ ] Functional/interface requirements have observable scenarios; quality requirements have complete QAS; constraints have executable verification.
- [ ] Interface inputs, outputs, units, ranges, errors, ordering and compatibility are explicit or unknown.
- [ ] Quality requirements preserve stimulus source, stimulus, environment, response and confirmed response measure.
- [ ] Observed-only behavior is visibly separate from confirmed requirements.
- [ ] Blocking unknowns cover unresolved contract decisions.

## 4. Canonical design

- [ ] Component template chapter paths, function numbers, interface/software-unit row keys and base excerpts can uniquely address future deltas.
- [ ] Component boundary, internal units and dependency direction match evidence.
- [ ] Interface realization matches canonical specification semantics.
- [ ] State, data ownership, lifecycle and persistence are explicit.
- [ ] Concurrency, ordering, resource limits and exhaustion behavior are explicit or unknown.
- [ ] Error translation, recovery, degradation and failure-state guarantees are explicit or unknown.
- [ ] Build, configuration and deployment claims stay within what definitions prove.
- [ ] Test seams and known coverage gaps are recorded.
- [ ] Full function baseline, development/runtime views, key functions and software-unit details are reconstructed or explicitly unknown.
- [ ] Database/persistence, UI, interfaces, applicable domain scenarios and software cost sections contain evidence or auditable N/A.
- [ ] Reviewer has evaluated responsibility boundaries, error/degradation, ownership/lifecycle and abstraction/evolution cost from chapters 1–8; no separate “high-quality design” chapter is required.
- [ ] No rationale or trade-off is fabricated to complete the template.

## 5. Spec-design consistency

- [ ] Every normative specification ID maps to a component design chapter/entity anchor, no-design-impact statement or blocking gap.
- [ ] Every externally observable design behavior maps back to a specification ID.
- [ ] Names, types, units, ranges, defaults and optionality agree.
- [ ] State and error semantics agree.
- [ ] Ownership, lifecycle and compatibility claims agree.
- [ ] Both documents use the same source revision and component identity.
- [ ] If only one document was created, it does not silently redefine the existing document.

## 6. Unknown triage

- [ ] Contract, ownership, threshold, safety/security, persistence, concurrency, recovery and architecture unknowns are blocking.
- [ ] Non-blocking unknowns truly cannot alter the current contract or design boundary.
- [ ] Every unknown states impact, owner and next question.
- [ ] Conflicting sources remain visible until an authorized human resolves them.

## Verdict

Use one verdict:

- `passed`: no blocking finding or unknown; provenance and cross-consistency are sufficient for human confirmation.
- `rework`: evidence exists and the author can correct classification, coverage or consistency.
- `blocked`: required evidence, authority, tool access or human decision is missing.

Record:

```markdown
## Baseline review record

- Reviewer:
- Independence basis:
- Reviewed source revision:
- Reviewed document revision / hash:
- Verdict: passed / rework / blocked
- Findings:
  - BR-001:
- Resolution:
  - BR-001:
- Remaining non-blocking unknowns:
```

Put the record in the generated document's `Baseline review and confirmation` section.
When init is routed from an active AR, a full record is mandatory at
`specs/changes/ARXXX-<topic>/reviews/baseline-init-review-YYYY-MM-DD[-rN].md`;
both canonical documents and `change.json.gates.baselinePreflight.evidence` point to it.
Only standalone init with no active AR may keep the record solely inside the canonical documents.

## Human confirmation

After `passed`, present the canonical content or diff, provenance summary, review record and remaining non-blocking unknowns to a human.

- [ ] Human confirmation is explicit, not inferred from silence or an earlier request to run init.
- [ ] Confirmation names the documents and scope.
- [ ] Confirmation identity and time are recorded.
- [ ] Only generated or repaired draft documents are marked `baseline-ready`.
- [ ] When both documents were generated, both are updated together.
- [ ] Any late content change invalidates the verdict and requires re-review.

Without independent pass plus explicit human confirmation, `baselineStatus` remains `draft`.
