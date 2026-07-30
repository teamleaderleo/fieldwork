# F244-repository-admission-authority: require complete authority evidence before fallback admission

Finding state: `review-ready`

Workstream: `A`  
Canonical Fieldwork issue: `#244`  
Canonical finding path: `findings/F244-repository-admission-authority/finding.md`  
Canonical implementation: `teamleaderleo/fieldwork#259`  
Exact implementation head: `20a3eaef6db81c15ee2e0e725d180277990cff7c`  
Exact base or source revision: `teamleaderleo/fieldwork@896a617c4b4dd8dd9fb9493d05f801c7baf9ade3`  
Strongest evidence class: `full-gate`  
Reviewed input generation: `PR #259 exact head 20a3eaef6db81c15ee2e0e725d180277990cff7c`  
Current review disposition: `none — independent complete-diff review pending`  
Desk routing: `Review Queue #213`  
Upstream contact authorized: `no`

## In simple words

Fieldwork is testing a rule for workers whose normal tool route disappears. The worker may propose another route, but the repository must compare the old and new authority before allowing it.

The first implementation could make a decision from missing evidence. An omitted authority list became an empty list, missing binding generations entered a digest as null values, and missing reversibility could pass. The first repair closed the direct allow path, yet a partial comparison could still produce “ask for approval” or “block.” Those outcomes sound conservative, but they still claim a comparison was performed when most fields were absent.

PR #259 now requires one explicit relation for every declared authority dimension before the shared classifier runs. The exact head passes all three repository workflows. The implementation is ready for independent review.

## Why we care

Fallback routing can change account, provider, approval subject, delegation, visibility, credentials, permissions, resource scope, audit behavior, idempotency, rollback, or recovery. A decision made from a partial comparison can hide an authority expansion or create an approval prompt whose stated differences are incomplete. That weakens operator understanding and can authorize the wrong route.

## What happens if we leave it alone

The observed defect is deterministic in the model: incomplete fallback inputs can reach a classifier decision. In the original carrier they could reach `allow_equivalent`; in the first replacement they could still reach approval or fail-closed results. The repository could therefore emit a confident admission receipt from an incomplete comparison. This finding does not establish production exposure because hosted Stensibly import and Codex dispatch are outside the carrier.

## Current finding

Every fallback proposal must provide exact typed input keys, non-empty operation and binding identities, strict boolean identity/reversibility receipts, and exactly one relation for all 12 declared authority dimensions before classification. The classifier may then return allow, approval, or fail-closed. Missing, duplicate, unknown, contradictory, or partial comparisons are invalid inputs rather than policy decisions.

### Claim table

| Claim | Evidence class | Exact support | Limit |
| --- | --- | --- | --- |
| The original carrier could allow a fallback with incomplete authority evidence. | `source-read` | Closed PR #251 at `17d4fc3dd17e0f7a37516aa38a8767eca9ade591`; Campaign #86 classifier defaults and evaluator call path. | Synthetic repository model; no live provider dispatch occurred. |
| The first replacement still permitted partial comparisons for approval or fail-closed outcomes. | `source-read` | PR #259 predecessor review before commit `20a3eaef...`; completeness check was invoked only for `allow_equivalent`. | Shows one remaining boundary in the replacement, not a new live incident. |
| Current head validates the complete 12-field comparison before invoking the classifier. | `source-read` | `evaluate_admission.py` at `20a3eaef...`, `REQUIRED_AUTHORITY_FIELDS`, validation before `classify_fallback`. | Trusted comparator provenance and live route identity remain outside scope. |
| The exact head passes the admission, repository integrity, and shared-classifier workflows. | `full-gate` | Runs `30581988908`, `30581988915`, `30581988967`. | Workflow success does not substitute for independent complete-diff review. |

## System and ownership map

- Entry point: `.github/workflows/issue-244-repository-admission.yml` executes the retained case matrix.
- Repository attachment: `STENSIBLY.md` declares static policy and allowed autonomous repository actions; it grants no live authority.
- Admission evaluator: `campaigns/0006-authority-aware-capability-fallback/lanes/fieldwork-repository-admission/artifacts/evaluate_admission.py` validates observations and fallback receipts.
- Shared policy owner: Campaign #86 classifier at `campaigns/0006-authority-aware-capability-fallback/artifacts/classify_fallback.py` classifies complete proposed routes.
- Evidence owner: retained `cases.json` and generated workflow receipt.
- Side effect: none in this carrier; it emits a synthetic admission decision.
- Recovery: invalid or incomplete inputs fail before a decision; missing mutation capability may degrade to read-only work only when required reads remain executable.
- Public contract: repository-local preflight candidate, not hosted runtime authority.

## Historical precedent

### Campaign #86 authority-aware fallback classifier

- Source: `https://github.com/teamleaderleo/fieldwork/tree/896a617c4b4dd8dd9fb9493d05f801c7baf9ade3/campaigns/0006-authority-aware-capability-fallback`
- Revision or date: `896a617c4b4dd8dd9fb9493d05f801c7baf9ade3`, reviewed 2026-07-31.
- Principle supported: fallback decisions must preserve operation identity and classify named authority, execution-certainty, and recovery differences.
- Important difference: the shared classifier assumes a caller supplies meaningful comparison data; this finding owns the repository-admission input contract that must validate completeness before invoking it.

### Reversion of premature admission landing

- Source: Fieldwork commits `1dc47994dfd738640fac57e345a41ded657806bf`, `a057bea7a2eaa127f7961687459c5884d4a28482`, and `33c57f7597ab1b4f6d0cb6adacf7cc7814362f35`.
- Revision or date: 2026-07-30.
- Principle supported: admission files and repository attachments do not belong on `main` before their authority contract and review path are ready.
- Important difference: the current PR is an owned draft carrier with exact-head gates; it still lacks hosted import and runtime integration.

## Approaches considered

### Retained approach: exact complete comparison before classification

The evaluator validates the full declared authority field set before calling Campaign #86. This cleanly separates malformed evidence from policy outcomes and prevents decision labels from laundering incomplete inputs.

### Declined: classifier defaults for omitted data

Defaults make the classifier reusable for exploratory cases, but they are unsafe as a repository admission boundary. Empty lists and null digest values can look like evidence of equivalence.

### Declined: enforce completeness only for `allow_equivalent`

Approval and fail-closed are conservative outcomes, yet a partial comparison still creates a misleading receipt and can omit the exact authority changes a person should evaluate.

### Deferred: trust live provider metadata directly

Live route identity, accepted attachment generation, comparator identity, credentials, and provider behavior require hosted Stensibly/Codex integration. They belong to a later integration finding.

## Edge cases covered

| Edge case or control | Evidence | Result |
| --- | --- | --- |
| Direct executable read and mutation routes | retained matrix | `ready`. |
| Missing mutation route with reads intact | retained matrix | `degraded_read_only`. |
| Complete changed account/provider comparison | retained matrix | `require_explicit_approval`. |
| Ambiguous prior mutation with complete equal authority | retained matrix | `blocked`. |
| Missing required read | retained matrix | `blocked`. |
| Complete equivalent fallback with narrower permission | retained matrix | `ready`. |
| Omitted delta key | invalid control | rejected as malformed. |
| Empty delta list | invalid control | rejected. |
| Partial read or mutation comparison | invalid controls | rejected before classification. |
| Empty binding generation | invalid control | rejected. |
| Missing reversibility | invalid control | rejected. |
| Phase becoming present after absence/unknown | invalid control | rejected. |

## Edge cases deferred or outside scope

| Edge case | Why deferred | Owning next record or reopening trigger |
| --- | --- | --- |
| Hosted Stensibly attachment import and acceptance | This carrier reads static repository files only. | New integration finding after versioned import exists. |
| Trusted comparator provenance | The evaluator imports a repository path without a signed runtime identity. | Reopen when binding to accepted attachment and comparator generation. |
| Codex dispatch and provider calls | No live dispatch occurs. | Runtime integration lane. |
| Approval UI and human interpretation | Synthetic decision JSON only. | Design/integration finding before production use. |
| Credential and provider availability changes during dispatch | Requires live generation fencing. | Runtime authority finding. |

## Exact execution and receipts

| Repository/head | Command or workflow | Platform/environment | Result | Evidence class |
| --- | --- | --- | --- | --- |
| `teamleaderleo/fieldwork@20a3eaef6db81c15ee2e0e725d180277990cff7c` | issue #244 repository admission `30581988908` | GitHub Actions | success | `target-executed` |
| same | Fieldwork integrity `30581988915` | GitHub Actions | success | `full-gate` |
| same | Campaign #86 authority fallback classifier `30581988967` | GitHub Actions | success | `full-gate` |
| predecessor local repair generation | deterministic 14-case matrix | coordinator execution | 2 ready, 1 degraded, 1 approval, 3 blocked, 7 invalid, 0 mismatches | `model-executed` |

## Complete-diff and compatibility review

- Complete changed-file fence: `STENSIBLY.md`, `.github/workflows/issue-244-repository-admission.yml`, evaluator, retained cases, and lane report.
- Current-base relationship: PR #259 is based on reviewed current main `896a617c...`; GitHub reports it mergeable and draft.
- Temporary carrier status: closed PR #251 remains unmerged, superseded evidence; PR #259 is canonical.
- Compatibility surfaces examined: direct capability, read-only degradation, missing reads, equivalent fallback, approval, ambiguous mutation certainty, malformed phases, typed input completeness, duplicate/unknown fields.
- Known source defect or routine repair remaining: none identified at `20a3eaef...` after the second complete-diff pass.
- Reviewer eligibility: independent reviewer required because the current coordinator authored the latest repair.

## Current disposition and desk routing

- Finding state: `review-ready`
- Review disposition: `none — independent review pending`
- Review Queue entry: `#213`
- Delivery lane: `not-entered`
- Exact next transition: independent complete-diff review of PR #259 at `20a3eaef...`.
- Clearing condition: exact-head ACCEPT review confirming complete input validation, case coverage, report truth, and evidence limits.
- Required subgates: complete diff, current-base relationship, three green workflows, supersession truth, hosted-runtime boundary.
- User decision requested: none; technical review comes first.

## Changes to the canonical conclusion

| Date | Pull request or commit | Change in conclusion |
| --- | --- | --- |
| 2026-07-30 | PR #251 `17d4fc3...` | Green workflows were demoted to REPAIR after incomplete fallback inputs were found. |
| 2026-07-30 | `f7a515ce...` and `5676a1af...` | Added exact keys, typed fields, non-empty deltas, and complete equivalent-route checks. |
| 2026-07-30 | `20a3eaef6db81c15ee2e0e725d180277990cff7c` | Required the full authority field set before every classifier outcome; exact-head workflows passed. |

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
