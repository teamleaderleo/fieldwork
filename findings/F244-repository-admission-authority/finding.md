# F244-repository-admission-authority: require complete authority evidence and executable read work

Finding state: `research-active`

Workstream: `A`  
Canonical Fieldwork issue: `#244`  
Canonical finding path: `findings/F244-repository-admission-authority/finding.md`  
Canonical implementation: `teamleaderleo/fieldwork#259`  
Exact implementation head: `c3582f97bbe9ee10cde1cb7084912241075fed3b`  
Exact repair source commit: `63ced110236929841a3afd1b9d9642627498ab24`  
Exact base or source revision: `teamleaderleo/fieldwork@896a617c4b4dd8dd9fb9493d05f801c7baf9ade3`  
Strongest evidence class: `target-test-prepared` for the current repair; prior authority-completeness generation is `full-gate`  
Reviewed input generation: `PR #259 exact head 20a3eaef6db81c15ee2e0e725d180277990cff7c`  
Current review disposition: `REPAIR — same-head execution and fresh complete-diff review required`  
Desk routing: `Review Queue #213 repair-active`  
Upstream contact authorized: `no`

## In simple words

Fieldwork is testing a rule for workers whose normal tool route disappears. A worker may propose another route only after the repository compares the old and new authority.

The carrier has now exposed and repaired three separate evidence problems:

1. omitted authority facts could look equivalent;
2. partial comparisons could still become approval or blocked receipts;
3. a mutation-only request could claim `degraded_read_only` even when zero read routes were executable.

The current source requires complete 12-field authority evidence and permits degradation only when at least one required read capability is directly executable or admitted through an authority-equivalent fallback. Same-head workflows and a fresh independent review remain before promotion.

## Why we care

Fallback routing can change account, provider, approval subject, delegation, visibility, credentials, permissions, resource scope, audit behavior, idempotency, rollback, or recovery. A partial comparison can hide an authority expansion or create an incomplete approval prompt.

A degradation label also carries authority. It says useful read-only work may continue. Emitting that label with zero executable read routes creates an admission receipt for work that does not exist and can mislead dispatch or coordination code.

## What happens if we leave it alone

At reviewed head `20a3eaef...`, a request containing only one absent `potential_mutation` capability, no fallback, and no read capability returns `degraded_read_only`. The report and repository attachment define degradation as continuing executable reads, so the result overstates the remaining surface.

The current repair blocks that request with `mutation_capability_missing:no_executable_read_only_work`. Production exposure remains unproved because hosted Stensibly import and Codex dispatch are outside this carrier.

## Governing invariant

**Every fallback decision uses a complete declared authority comparison, and read-only degradation requires at least one admitted required read capability.**

Malformed or incomplete evidence is invalid input. Missing mutation capability may degrade only when required read work remains directly executable or authority-equivalent. Otherwise the request blocks.

## Current finding

Every fallback proposal must provide exact typed input keys, non-empty operation and binding identities, strict boolean identity/reversibility receipts, and exactly one relation for all 12 declared authority dimensions before classification.

The evaluator tracks admitted required read capabilities. A direct executable read or an `allow_equivalent` read fallback counts. Approval, fail-closed, absent, or unknown reads do not count. Unresolved mutation capability with zero admitted reads becomes blocked.

### Claim table

| Claim | Evidence class | Exact support | Limit |
| --- | --- | --- | --- |
| The original carrier could allow a fallback with incomplete authority evidence. | `source-read` | Closed PR #251 at `17d4fc3dd17e0f7a37516aa38a8767eca9ade591`; Campaign #86 classifier defaults and evaluator call path. | Synthetic repository model; no live provider dispatch. |
| The first replacement still permitted partial comparisons for approval or fail-closed outcomes. | `source-read` | PR #259 predecessor before `20a3eaef...`; completeness was checked after classification. | Shows an input-contract defect in the replacement. |
| Head `20a3eaef...` validates all 12 authority fields before classification. | `full-gate` | Runs `30581988908`, `30581988915`, `30581988967`. | Those runs predate the degradation repair. |
| Head `20a3eaef...` can degrade a mutation-only request with zero admitted reads. | `source-read` plus durable discriminator | Review `4823835807`; `mutation_only_absence_case.json` added at `831ba998...`. | Current repair execution pending. |
| Repair source `63ced110...` requires admitted read work before degradation. | `source-read` | `admitted_reads` tracking and explicit no-read-only-work block. | Same-head workflows and independent review remain. |

## System and ownership map

- Entry point: `.github/workflows/issue-244-repository-admission.yml` executes the primary matrix and mutation-only discriminator.
- Repository attachment: `STENSIBLY.md` declares static policy and allowed autonomous repository actions; it grants no live authority.
- Admission evaluator: `campaigns/0006-authority-aware-capability-fallback/lanes/fieldwork-repository-admission/artifacts/evaluate_admission.py` validates observations, fallback receipts, and degradation eligibility.
- Shared policy owner: Campaign #86 classifier at `campaigns/0006-authority-aware-capability-fallback/artifacts/classify_fallback.py` classifies complete proposed routes.
- Evidence owner: `cases.json`, `mutation_only_absence_case.json`, and exact workflow receipts.
- Side effect: none in this carrier; it emits synthetic admission decisions.
- Recovery: invalid or incomplete inputs fail before a decision; unavailable mutation work blocks when no admitted reads remain.
- Public contract: repository-local preflight candidate, not hosted runtime authority.

## Historical precedent

### Campaign #86 authority-aware fallback classifier

- Source: `https://github.com/teamleaderleo/fieldwork/tree/896a617c4b4dd8dd9fb9493d05f801c7baf9ade3/campaigns/0006-authority-aware-capability-fallback`
- Revision: `896a617c4b4dd8dd9fb9493d05f801c7baf9ade3`, reviewed 2026-07-31.
- Principle supported: fallback decisions preserve operation identity and classify named authority, execution-certainty, and recovery differences.
- Difference: the shared classifier assumes meaningful comparison data; this finding owns completeness and admission composition.

### Repository attachment boundary

- Source: `STENSIBLY.md` in PR #259.
- Principle supported: repository text is display and policy context; live capability and execution authority stay server-owned.
- Consequence: a decision label must accurately describe executable work proven by the receipt.

## Decision criteria

1. Reject incomplete authority evidence before any policy outcome.
2. Preserve fail-closed precedence for missing reads and ambiguous mutation outcomes.
3. Permit degradation only when useful required read work remains admitted.
4. Keep direct and equivalent read authority visible in the receipt.
5. Preserve deterministic output and exact case reproduction.
6. Avoid claims about hosted integration absent target execution.

## Approaches considered

### Selected: explicit admitted-read tracking

Track direct executable reads and read fallbacks classified `allow_equivalent`. Require a non-empty admitted set before unresolved mutation capability can degrade.

Benefit: directly matches the attachment and report contract, preserves positive degradation, and yields inspectable receipts.

### Declined: infer read work from request operation kind

The top-level operation kind does not prove that a required read route exists. A potential-mutation request can contain only mutation capability.

### Declined: treat every missing mutation as degradation

This was the reviewed defect. It creates a read-only label without read-only work.

### Deferred: validate live comparator and provider provenance

Accepted attachment generation, comparator identity, credentials, and live provider state require hosted integration.

## Edge cases covered

| Edge case or control | Evidence | Expected result |
| --- | --- | --- |
| Direct executable read and mutation routes | primary matrix | `ready`. |
| Missing mutation route with direct read intact | primary matrix | `degraded_read_only`. |
| Mutation-only request with missing mutation route | standalone discriminator | `blocked`. |
| Complete changed account/provider comparison | primary matrix | `require_explicit_approval`. |
| Ambiguous prior mutation with complete equal authority | primary matrix | `blocked`. |
| Missing required read | primary matrix | `blocked`. |
| Complete equivalent fallback with narrower permission | primary matrix | `ready`. |
| Omitted, empty, partial, duplicate, unknown, or contradictory authority input | invalid controls and validator | rejected before classification. |
| Empty binding generation or missing reversibility | invalid controls | rejected. |
| Phase becoming present after absence/unknown | invalid control | rejected. |

## Edge cases deferred or outside scope

| Edge case | Reason | Next record or trigger |
| --- | --- | --- |
| Equivalent read fallback plus missing mutation | Current source supports it; dedicated positive case absent. | Add before hosted integration or when receipt schema becomes contractual. |
| Several missing mutations with one admitted read | Decision composition is deterministic but minimally covered. | Expand matrix before production use. |
| Hosted Stensibly attachment import and acceptance | Static repository carrier only. | Integration finding after versioned import exists. |
| Trusted comparator provenance | Repository path import lacks signed runtime identity. | Bind to accepted attachment and comparator generation. |
| Codex dispatch and provider calls | No live dispatch occurs. | Runtime integration lane. |
| Approval UI and human interpretation | Synthetic JSON only. | Design/integration finding. |
| Capability changes during dispatch | Requires live generation fencing. | Runtime authority finding. |

## Exact execution and receipts

| Repository/head | Command or workflow | Result | Evidence class |
| --- | --- | --- | --- |
| `teamleaderleo/fieldwork@20a3eaef6db81c15ee2e0e725d180277990cff7c` | issue #244 admission `30581988908` | success | `target-executed` for complete-comparison generation |
| same | Fieldwork integrity `30581988915` | success | `full-gate` |
| same | Campaign #86 classifier `30581988967` | success | `full-gate` |
| `831ba998af5c9ffd811b9f3352853c63b4ecf6cd` | mutation-only discriminator | prepared to expose degradation defect | `target-test-prepared` |
| current head `c3582f97bbe9ee10cde1cb7084912241075fed3b` | issue #244, Fieldwork integrity, Campaign #86 workflows | queued after source and report repair | `target-test-prepared` |

Primary matrix: 14 cases — 2 ready, 1 degraded, 1 approval, 3 blocked, 7 invalid. Standalone discriminator: 1 blocked mutation-only case.

## Complete-diff and compatibility review

- Current changed-file fence: `STENSIBLY.md`, admission workflow, evaluator, primary cases, mutation-only case, and lane report.
- Current-base relationship: PR #259 remains based on reviewed main `896a617c...`; exact head moved after review and all earlier disposition expired.
- Temporary carrier status: closed PR #251 remains unmerged and superseded; PR #259 is canonical.
- Compatibility surfaces examined: direct capability, positive read-only degradation, mutation-only absence, missing reads, equivalent fallback, approval, ambiguous mutation certainty, malformed phases, typed input completeness, duplicate/unknown fields.
- Output addition: `admitted_read_capabilities` makes degradation evidence inspectable.
- Reviewer eligibility: fresh independent complete-diff review is required after same-head workflows pass because the current repair followed review `4823835807`.

## Current disposition and desk routing

- Finding state: `research-active`
- Review disposition: `REPAIR — execution pending`
- Review Queue entry: `#213 repair-active`
- Delivery lane: `not-entered`
- Exact next transition: complete current-head workflows on `c3582f97...`, inspect outputs, then perform fresh independent complete-diff review.
- Clearing condition: all three same-head workflows pass, the mutation-only discriminator reports blocked, the positive degradation case remains degraded, report claims match receipts, and review accepts the complete six-file diff.
- Non-delegable human decision: none.

## Changes to the canonical conclusion

| Date | Pull request or commit | Change in conclusion |
| --- | --- | --- |
| 2026-07-30 | PR #251 `17d4fc3...` | Green workflows demoted after incomplete fallback evidence was found. |
| 2026-07-30 | `f7a515ce...` and `5676a1af...` | Added exact keys, typed fields, and initial completeness checks. |
| 2026-07-30 | `20a3eaef...` | Required all 12 authority fields before every classifier outcome; workflows passed. |
| 2026-07-31 | review `4823835807` | Demoted review-ready after mutation-only degradation was found. |
| 2026-07-31 | `831ba998...` | Added durable mutation-only blocked discriminator. |
| 2026-07-31 | `63ced110...` / `c3582f97...` | Added admitted-read guard, receipt, and synchronized report; current-head execution pending. |

## References

- `https://github.com/teamleaderleo/fieldwork/issues/244`
- `https://github.com/teamleaderleo/fieldwork/pull/251`
- `https://github.com/teamleaderleo/fieldwork/pull/259`
- `https://github.com/teamleaderleo/fieldwork/actions/runs/30581988908`
- `https://github.com/teamleaderleo/fieldwork/actions/runs/30581988915`
- `https://github.com/teamleaderleo/fieldwork/actions/runs/30581988967`
- `STENSIBLY.md`
- `.github/workflows/issue-244-repository-admission.yml`
- `campaigns/0006-authority-aware-capability-fallback/artifacts/classify_fallback.py`
- `campaigns/0006-authority-aware-capability-fallback/lanes/fieldwork-repository-admission/artifacts/evaluate_admission.py`
- `campaigns/0006-authority-aware-capability-fallback/lanes/fieldwork-repository-admission/artifacts/cases.json`
- `campaigns/0006-authority-aware-capability-fallback/lanes/fieldwork-repository-admission/artifacts/mutation_only_absence_case.json`
