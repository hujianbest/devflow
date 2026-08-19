# Bootstrap domain candidate proposal

- Action: create
- Baseline: `440bf01d2ea2f0b65813790e0c1febcadf04410e`
- Generated: `2026-08-19T17:10:00Z`
- Status: applied as `draft`; human confirmation remains required

## Proposed concepts

1. `domains/billing-accounting/overview`
   - Claim (Inferred): billing ledger behavior is a candidate `billing-accounting` Bounded Context.
   - Evidence: `billing-readme`, `billing-account-code`.
2. `domains/billing-accounting/glossary/account`
   - Claim (Inferred): within this candidate Context, `Account` means a billing ledger account identified by `billing_account_id`.
   - Evidence: `billing-readme` states the meaning; `billing-account-code` implements matching fields.
3. `domains/identity-access/overview`
   - Claim (Inferred): authentication-subject behavior is a candidate `identity-access` Bounded Context.
   - Evidence: `identity-readme`, `identity-account-code`.
4. `domains/identity-access/glossary/account`
   - Claim (Inferred): within this candidate Context, `Account` means a login subject identified by `subject_id`.
   - Evidence: `identity-readme` states the meaning; `identity-account-code` implements matching fields.
5. Context-local rule candidates for charging and authentication.
   - Claim (Observed): the two functions implement their documented predicates.
   - Claim (Inferred): those predicates may represent business rules.

## Separation decision

Do not create a global `Account` definition. Keep the two terms at separate Context-qualified paths and cross-link them as homonyms. No evidence establishes an identity-to-billing mapping or a shared identifier.

## Effects

- Adds both Contexts and terms to indexes as `[draft]`.
- Adds review item `RQ-001`.
- Does not invalidate existing verified knowledge because this is a cold start.
- Required reviewers: billing domain owner and identity/access domain owner.
