# F254-desk-head-audit: detect expired pull-request heads in the review and delivery desks

Finding state: `delivery-gate-ready`

Workstream: `A / I`  
Canonical Fieldwork issue: `#254`  
Canonical finding path: `findings/F254-desk-head-audit/finding.md`  
Canonical implementation: draft PR #274  
Exact target-executed implementation head: `72cf58d2a494de41603c9ec52b744539d71a26ea`  
Exact base revision: `teamleaderleo/fieldwork@896a617c4b4dd9fb9493d05f801c7baf9ade3`  
Evidence classes present: `source-read`, `target-executed`  
Reviewed inputs: live Review Queue #213 and Delivery Desk #160 at runs `30588760593` and `30588760575`  
Current review disposition: `REVIEW READY` after documentation synchronization  
Desk routing: none; this tool validates desk routing  
Upstream contact authorized: `no`

## In simple words

Fieldwork's review queue and delivery desk name exact pull-request commits for review, delivery, or merge. Manual prose and markers can survive after a branch moves or a pull request closes.

The audit reads hidden exact-head markers from #213 and #160, fetches the named owned pull requests, and fails when a marker is stale, missing, duplicated, conflicting, closed, or merged. Exact execution passed its focused fixture matrix and the live owned-desk comparison. The tool reports drift only and cannot update a marker, accept or demote work, merge, or contact upstream.

At the exact execution receipt, the desks carried markers only for Fieldwork PRs #231, #238, and #252. Repair PR #281 and execution carrier #273 remained visible in prose without promotion markers.

## Why we care

An exact-head disposition describes one immutable code generation and reviewed input set. A stale marker can direct a reviewer toward the wrong diff, retain expired tests, or tell a person to merge code that differs from the accepted candidate.

The cleanup that motivated the audit found several forms of drift:

- PR #249 retained old locked and review-ready states after later parser defects;
- PR #259 retained queued/review wording after completed workflows and later gained a composed successor;
- PR #252 retained an older R1 head after meaningful source and decision changes;
- partial PRs #257/#259 remained live after PR #273 became the single composed continuation.

## Current finding

The queue and desk need explicit machine-readable references for active owned pull requests. A read-only evaluator can compare the expected head with live PR state and fail closed on malformed or expired routing data.

Marker form:

```text
<!-- fieldwork:desk-ref repo=teamleaderleo/fieldwork pr=231 head=<40-hex-sha> lane=R3 -->
```

Markers carry routing identity only. Canonical findings and implementation PRs remain responsible for evidence, defects, limits, semantic successor relationships, and transitions.

### Claim table

| Claim | Evidence class | Exact support | Limit |
| --- | --- | --- | --- |
| Review/delivery routing can retain expired exact heads or successors. | `source-read` | PRs #249, #252, #257, and #259 compared with live branch and successor state during #254 cleanup. | The examples do not measure complete repository history. |
| Explicit markers can be checked with read-only GitHub access. | `target-executed` | PR #274 head `72cf58d...`, desk audit run `30588760593`. | Only owned PR head/state marker drift is covered. |
| Live 404 responses become `missing_pull_request` findings. | `target-executed` | Focused fixture matrix in run `30588760593`. | Other transport failures remain blocked execution, not technical negatives. |
| The audit cannot issue a promotion or write. | `source-read` and `target-executed` | JSON-only report path, read-only permissions, and successful live execution. | Repository administrators still control workflows and issue edits. |
| A passing marker audit proves semantic successor currentness. | `not claimed` | Explicit deferred boundary. | Open exact-head PR metadata can remain syntactically current while a newer semantic successor exists. |

## System and ownership map

- Human entrypoints: Review Queue #213 and Delivery Desk #160.
- Technical authority: canonical findings and exact implementation PRs.
- Machine input: `fieldwork:desk-ref` HTML comments in issue bodies.
- Live state source: owned GitHub pull-request `state`, `merged`, and `head.sha`.
- Evaluator: `scripts/audit_desk_heads.py`.
- Regressions: `scripts/test_audit_desk_heads.py`.
- Execution: `.github/workflows/desk-head-audit.yml`.
- Side effect: workflow pass or failure and JSON output only.
- Recovery: a coordinator synchronizes or removes the marker after technical reclassification.

## Historical precedent

### Exact-head review protocol

`REVIEWING.md` requires code-head and reviewed-input movement to expire a disposition. Generated queues without validated exact states are snapshots.

Important difference: the protocol owns technical review; this finding adds one narrow detector for owned PR head and state drift.

### Coordination compiler

`scripts/coordination_compiler.py` shows that deterministic read-only evaluators can validate explicit coordination inputs and fail closed.

Important difference: the compiler evaluates retained graph fixtures; this audit reads live issue markers and owned PR metadata.

## Approaches considered

### Retained: explicit markers plus read-only live comparison

The issue remains readable while the evaluator receives exact fields without scraping historical prose.

### Declined: infer the active SHA from nearby prose

Issue bodies contain parent, repair, source, evidence, superseded, and historical heads. Guessing can select the wrong generation.

### Declined: automatically replace stale heads

A new commit can change semantics or evidence. Automatic replacement would hide the need for review and reclassification.

### Declined: automatic demotion or promotion

The evaluator cannot decide semantic equivalence, repair sufficiency, review eligibility, or delivery authority.

### Deferred: receipt, issue-generation, label, and successor audits

Workflow conclusions, issue invariants, dependencies, labels, canonical finding revisions, and semantic successor relationships can also expire review. This slice owns explicit PR head/state marker drift only.

## Covered controls

| Case | Expected result |
| --- | --- |
| Multiple valid markers | parsed and audited |
| Issue with no markers | invalid input |
| Malformed SHA or fields | invalid input |
| Duplicate marker in one issue | invalid input |
| Conflicting heads across issues | `conflicting_expected_heads` |
| Live head differs | `stale_head` |
| Missing live PR / 404 | `missing_pull_request` |
| Closed active entry | `closed_active_entry` |
| Merged active entry | `merged_active_entry` |
| Current open exact head | pass |

## Deferred boundaries

| Boundary | Next owner |
| --- | --- |
| Third-party public PRs | Separate authority and reference-policy design. |
| Workflow-conclusion drift | Receipt-audit finding with exact workflow/head binding. |
| Issue-body and decision generations | Structured coordination-status reconciliation. |
| Issue body versus label disagreement | Metadata evaluator. |
| Semantic identity or successor currentness after head movement | Complete-diff technical review and canonical finding reconciliation. |
| Automatic marker replacement, demotion, or promotion | Remains prohibited. |

## Exact execution

| Repository/head | Workflow | Result | Evidence class |
| --- | --- | --- | --- |
| PR #274 `72cf58d2a494de41603c9ec52b744539d71a26ea` | focused syntax and fixture matrix | `30588760593`: success | `target-executed` |
| same | live #213/#160 marker comparison | `30588760593`: success | `target-executed` |
| same | Fieldwork integrity | `30588760575`: success | repository validation |

The exact live marker set at that receipt referenced PR #231 and #238 in both desks and PR #252 in #160, with identical expected heads across duplicate references.

A later desk edit, PR head movement, PR state change, or marker-set change requires a new live observation. The historical successful receipt remains evidence for the implementation generation but is not a permanent statement about desk currentness.

## Complete-diff and authority review

Review `4827631187` accepts the evaluator and tests within their declared boundary. Its only repair was synchronization of this finding from older head `f0660030...`, queued runs, `target-test-prepared`, and `EXECUTE` to the successful exact generation above.

Complete file fence:

- `.github/workflows/desk-head-audit.yml`;
- `scripts/audit_desk_heads.py`;
- `scripts/test_audit_desk_heads.py`;
- this finding.

Authority properties:

- workflow permissions are `contents: read`, `issues: read`, and `pull-requests: read`;
- checkout credentials are disabled;
- marker comments do not alter rendered issue prose;
- exit behavior is clean `0`, drift `1`, invalid input `2`, transport block `3`;
- there is no write, repair, acceptance, demotion, merge, or upstream-contact path.

## Current disposition

- Finding state: `delivery-gate-ready`
- Review disposition: `REVIEW READY`
- Exact next transition: run Fieldwork integrity on the documentation-repair head, then obtain renewed complete-diff review confirming that this synchronization changes no evaluator behavior or authority
- Clearing condition: green unchanged documentation head plus eligible complete-diff acceptance
- Non-delegable human decision: none

## Changes to the conclusion

| Date | Record | Change |
| --- | --- | --- |
| 2026-07-31 | first desk pass | Found expired PR #249/#252 heads and stale PR #259 workflow wording. |
| 2026-07-31 | `f0660030...` | Added explicit markers, live/snapshot evaluator, 404 classification, tests, and read-only workflow. |
| 2026-07-31 | successor cleanup | Removed closed PR #259 from promotion markers; retained repair and execution carriers as prose-only active state. |
| 2026-07-31 | `72cf58d...` | Focused matrix, live desk comparison, and Fieldwork integrity passed. |
| 2026-07-31 | finding synchronization | Promoted exact evidence to `target-executed`, retained read-only authority, and kept semantic successor/currentness checks deferred. |

## References

- initiative #254
- Review Queue #213
- Delivery Desk #160
- PR #274
- exact review `4827631187`
- exact runs `30588760593` and `30588760575`
- active marked PRs at the receipt: #231, #238, and #252
- repair PR #281 and execution carrier #273 as intentionally unmarked states at that receipt
- `REVIEWING.md`
- `COORDINATION.md`
- `scripts/audit_desk_heads.py`
- `scripts/test_audit_desk_heads.py`
- `.github/workflows/desk-head-audit.yml`
