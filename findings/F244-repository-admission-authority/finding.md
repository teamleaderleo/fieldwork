# F244-repository-admission-authority: require complete authority evidence and executable recovery before admission

Finding state: `research-active`

Workstream: `A`  
Canonical Fieldwork issue: `#244`  
Canonical finding path: `findings/F244-repository-admission-authority/finding.md`  
Canonical continuation: execution carrier PR #273  
Current carrier head: `c429808260839bd30f78d4346ee73a98334896a8`  
Complete-authority input: closed PR #259 at `20a3eaef6db81c15ee2e0e725d180277990cff7c`  
Readable-recovery input: closed PR #257 at `61915028c97a0317d277c62a2258443b71e70563`  
Exact Fieldwork main reviewed: `896a617c4b4dd8dd9fb9493d05f801c7baf9ade3`  
Strongest current evidence class: `target-test-prepared` for the composed carrier; each partial rule has source and execution evidence  
Reviewed input generation: issue #244, PRs #257/#259, and PR #273 current body/head  
Current review disposition: `EXECUTE`  
Desk routing: none until a source-only exact head exists  
Upstream contact authorized: `no`

## In simple words

Fieldwork is testing a rule for workers whose normal route disappears. A worker may continue through another route only when the repository has complete evidence about how authority changes and when the route still performs the operation that the degraded mode promises.

Two partial repairs established those requirements separately:

- PR #259 requires one explicit relation for every declared authority dimension before allow, approval, or blocked classification;
- PR #257 requires a direct or authority-equivalent executable read route before missing mutation capability may be called degraded read-only operation.

PR #273 composes both rules, rejects boolean schema versions, and is currently an execution carrier. The next valid result is a later source-only head with temporary workflows and its trigger marker removed.

## Why we care

Fallback routing can change account, provider, approval subject, delegation, credentials, permissions, resource scope, audit behavior, idempotency, rollback, or recovery. Complete authority evidence still fails to justify continuation when the proposed route cannot perform the required read. Conversely, an executable route cannot justify continuation when its authority comparison is partial.

A confident policy label from either incomplete authority evidence or a nonexistent recovery route misleads operators and can select the wrong execution path.

## What happens if we leave it alone

Observed model defects were deterministic:

- omitted authority facts could reach `allow_equivalent`;
- a partial authority list could still reach approval or fail-closed classification;
- missing mutation capability could be described as degraded read-only work even when no direct or equivalent read route remained.

The repository could therefore emit a confident admission receipt from incomplete operational evidence. Hosted import and live Codex dispatch remain outside the current carrier, so production exposure is unestablished.

## Current finding

A valid repository-admission decision requires both:

1. **complete comparison evidence** — exact typed input keys, non-empty operation and binding identities, strict boolean identity/reversibility receipts, and exactly one relation for all 12 declared authority dimensions;
2. **executable recovery** — degraded read-only continuation requires at least one direct or authority-equivalent read route that is actually present.

Malformed evidence fails before policy classification. Missing read and mutation routes block. Boolean schema versions fail primitive-version validation.

### Claim table

| Claim | Evidence class | Exact support | Limit |
| --- | --- | --- | --- |
| The original carrier could allow a fallback with incomplete authority evidence. | `source-read` | Closed PR #251 and evaluator/classifier call path. | Synthetic repository model; no live dispatch. |
| The first completeness repair still allowed partial comparisons to become approval or blocked receipts. | `source-read` | PR #259 review history before `20a3eaef...`. | One partial carrier generation. |
| PR #259 requires the complete 12-field comparison before every classifier result. | `target-executed` | Head `20a3eaef...`; runs `30581988908`, `30581988915`, `30581988967`. | Does not prove a recovery route exists. |
| PR #257 requires executable read recovery before degraded read-only continuation. | `source-read` plus retained candidate evidence | Head `61915028...` and its case matrix. | Partial carrier; not the composed result. |
| PR #273 composes both invariants and rejects boolean versions. | `source-read` | Carrier head `c4298082...`. | Temporary workflows and marker remain; source result pending. |
| Four composed exact-head workflows are queued. | `target-test-prepared` | Runs `30585478385`, `30585478433`, `30585478372`, `30585478454`. | Queued status carries no successful execution claim. |

## System and ownership map

- Repository attachment: `STENSIBLY.md` declares static policy and grants no live authority.
- Admission workflow: `.github/workflows/issue-244-repository-admission.yml`.
- Admission evaluator: lane artifact `evaluate_admission.py` validates observations, authority evidence, and recovery routes.
- Shared classifier: Campaign #86 `classify_fallback.py` classifies only validated proposals.
- Evidence: retained cases and generated receipts.
- Execution carrier: PR #273 temporarily owns composition workflows and a trigger marker.
- Recovery: invalid input fails before classification; missing executable reads block degraded continuation.
- Runtime boundary: hosted import, provider identity, credentials, dispatch, and approval UI remain separate.

## Historical precedent

### Campaign #86 authority-aware fallback classifier

- Principle supported: operation identity and authority differences must be explicit before fallback selection.
- Important difference: the shared classifier assumes meaningful comparison data; repository admission owns validation and route-executability checks before invoking it.

### Reversion of premature admission landing

- Fieldwork commits `1dc47994dfd738640fac57e345a41ded657806bf`, `a057bea7a2eaa127f7961687459c5884d4a28482`, and `33c57f7597ab1b4f6d0cb6adacf7cc7814362f35` removed premature admission files.
- Principle supported: policy attachment and admission machinery remain off `main` until their authority contract and review path are complete.
- Important difference: PR #273 remains an owned execution carrier and claims no landed source result.

## Approaches considered

### Retained: compose validation and executability before classification

Validate exact evidence and recovery capability in the repository-admission layer, then call the shared classifier. This separates malformed or impossible routes from policy outcomes.

### Declined: classifier defaults for omitted evidence

Empty lists and null digest values can look like equivalence. Admission inputs require explicit complete receipts.

### Declined: complete authority evidence without executable recovery

A route may preserve authority while failing to provide the operation promised by the degraded mode.

### Declined: infer read-only recovery from missing mutation alone

Absence of mutation authority says nothing about whether any read route remains.

### Deferred: trust live provider metadata directly

Accepted attachment generation, comparator provenance, provider identity, credentials, and live behavior need a hosted integration finding.

## Composed controls

| Case | Required result |
| --- | --- |
| Direct read and mutation routes | `ready`. |
| Missing mutation, direct read present | `degraded_read_only`. |
| Missing mutation, authority-equivalent read fallback present | `degraded_read_only`. |
| Missing mutation, zero executable reads | blocked with `read_only_recovery_capability_unavailable`. |
| Missing read and mutation routes | blocked. |
| Complete changed account/provider comparison | `require_explicit_approval`. |
| Ambiguous prior mutation with complete evidence | blocked. |
| Omitted, empty, partial, duplicate, unknown, or contradictory authority fields | invalid before classification. |
| Empty binding generation or missing reversibility | invalid. |
| Boolean schema version | invalid. |

## Deferred boundaries

| Boundary | Next owner |
| --- | --- |
| Hosted Stensibly attachment import and acceptance | Versioned hosted integration finding. |
| Trusted comparator and route provenance | Accepted attachment/runtime identity work. |
| Codex dispatch and provider calls | Runtime integration lane. |
| Approval UI and operator interpretation | Product/design integration finding. |
| Credential or provider generation changes during dispatch | Runtime generation-fencing finding. |

## Exact execution and receipts

| Repository/head | Workflow | Result | Evidence class |
| --- | --- | --- | --- |
| PR #259 `20a3eaef...` | issue #244 admission `30581988908` | success | `target-executed` |
| same | Fieldwork integrity `30581988915` | success | `full-gate` for that partial carrier |
| same | Campaign #86 classifier `30581988967` | success | `full-gate` for that partial carrier |
| PR #273 `c4298082...` | Campaign #86 `30585478385` | queued | `target-test-prepared` |
| same | issue #244 `30585478433` | queued | `target-test-prepared` |
| same | Fieldwork integrity `30585478372` | queued | `target-test-prepared` |
| same | composition materialization `30585478454` | queued | `target-test-prepared` |

## Complete-diff and compatibility review

- PRs #257 and #259 are closed unmerged as superseded partial inputs.
- PR #273 is the sole continuation and remains an execution carrier.
- Temporary composition workflows and one trigger marker must be absent from a later exact head before the carrier can expose a source result.
- A future review must inspect the complete source-only diff, current-base relationship, complete authority matrix, readable-recovery matrix, primitive-version controls, report truth, and receipt transfer.
- Execution-carrier success never grants R1/R2/R3, D0, merge, or upstream authority.

## Current disposition and routing

- Finding state: `research-active`
- Review disposition: `EXECUTE`
- Review Queue entry: none
- Delivery lane: none
- Exact next transition: materialize a source-only composed head from PR #273, prove temporary machinery absent, transfer exact receipts, and request independent complete-diff review
- Clearing condition: composed source and tests pass named gates at one exact head with no temporary carrier files
- Non-delegable human decision: none

## Changes to the canonical conclusion

| Date | Record | Change |
| --- | --- | --- |
| 2026-07-30 | PR #251 | Incomplete fallback inputs found despite green workflows. |
| 2026-07-30 | PR #259 `20a3eaef...` | Complete authority field set required before every classifier outcome. |
| 2026-07-31 | PR #257 `61915028...` | Added executable readable-recovery requirement. |
| 2026-07-31 | PR #273 `c4298082...` | Composed both invariants and primitive schema validation in one execution carrier. |

## References

- issue #244
- superseded PRs #251, #257, and #259
- composed carrier PR #273
- partial-carrier runs `30581988908`, `30581988915`, `30581988967`
- composed queued runs `30585478385`, `30585478433`, `30585478372`, `30585478454`
- `STENSIBLY.md`
- `.github/workflows/issue-244-repository-admission.yml`
- Campaign #86 classifier
- repository-admission evaluator and cases
