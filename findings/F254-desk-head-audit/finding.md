# F254-desk-head-audit: detect expired pull-request heads in the review and delivery desks

Finding state: `research-active`

Workstream: `A / I`  
Canonical Fieldwork issue: `#254`  
Canonical finding path: `findings/F254-desk-head-audit/finding.md`  
Canonical implementation: draft PR #274  
Exact implementation head: `f0660030a2b9346a8d4033d9843678919841e8dc`  
Exact base revision: `teamleaderleo/fieldwork@896a617c4b4dd9fb9493d05f801c7baf9ade3`  
Strongest evidence class: `target-test-prepared`  
Reviewed inputs: live Review Queue #213 and Delivery Desk #160 after 2026-07-31 successor cleanup  
Current review disposition: `EXECUTE`  
Desk routing: none; this tool validates desk routing  
Upstream contact authorized: `no`

## In simple words

Fieldwork's review queue and delivery desk tell people which exact pull-request commits are ready for review, delivery, or merge. Several entries stayed on old commits or old successor relationships after branches moved and partial pull requests were replaced.

The proposed audit reads hidden exact-head markers from #213 and #160, fetches the named owned pull requests, and fails when a marker is stale, missing, duplicated, conflicting, closed, or merged. It reports drift only and cannot update or promote anything.

The desks now carry markers only for active promotion or delivery entries: Fieldwork PRs #231, #238, and #252. Repair PR #281 and execution carrier #273 remain visible in prose without promotion markers.

## Why we care

An exact-head disposition describes one immutable code generation and reviewed input set. A stale marker can direct a reviewer toward the wrong diff, retain expired tests, or tell a person to merge code that differs from the accepted candidate.

The observed cleanup found several forms of drift:

- PR #249 retained old locked and review-ready states after later parser defects;
- PR #259 retained queued/review wording after completed workflows and later gained a composed successor;
- PR #252 retained an older R1 head after meaningful source and decision changes;
- partial PRs #257/#259 remained live after PR #273 became the single composed continuation.

## Current finding

The queue and desk need explicit machine-readable references for active owned pull requests. A read-only evaluator should compare the expected head with live PR state and fail closed on malformed or expired routing data.

Marker form:

```text
<!-- fieldwork:desk-ref repo=teamleaderleo/fieldwork pr=231 head=<40-hex-sha> lane=R3 -->
```

Markers carry routing identity only. Canonical findings and implementation PRs explain evidence, defects, limits, and transitions.

### Claim table

| Claim | Evidence class | Exact support | Limit |
| --- | --- | --- | --- |
| Review/delivery prose can retain expired exact heads or successors. | `source-read` | PRs #249, #252, #257, and #259 compared with live branch and successor state during #254 cleanup. | Observed examples do not measure full history. |
| Explicit markers can be checked with read-only GitHub access. | `target-test-prepared` | `scripts/audit_desk_heads.py` and workflow permissions. | Exact workflow remains queued. |
| Live 404 responses become `missing_pull_request` findings. | `source-read` | `AuditNotFound` handling at head `f0660030...`. | Other transport failures remain blocked execution. |
| The audit cannot issue a promotion or write. | `source-read` | JSON-only report path and read-only contents/issues/pull-request permissions. | Repository administrators still control workflows and issue edits. |

## System and ownership map

- Human entrypoints: Review Queue #213 and Delivery Desk #160.
- Technical authority: canonical findings and exact implementation PRs.
- Machine input: `fieldwork:desk-ref` HTML comments in issue bodies.
- Live state source: owned GitHub pull-request `state`, `merged`, and `head.sha`.
- Evaluator: `scripts/audit_desk_heads.py`.
- Regressions: `scripts/test_audit_desk_heads.py`.
- Execution: `.github/workflows/desk-head-audit.yml`.
- Side effect: workflow pass or failure and JSON output only.
- Recovery: synchronize or remove the marker after technical reclassification.

## Historical precedent

### Exact-head review protocol

`REVIEWING.md` requires code-head and reviewed-input movement to expire a disposition. Generated queues without validated exact states are snapshots.

Important difference: the protocol is manual; this finding adds one narrow detector for owned PR head and state drift.

### Coordination compiler

`scripts/coordination_compiler.py` shows that deterministic read-only evaluators can validate explicit coordination inputs and fail closed.

Important difference: the compiler evaluates retained graph fixtures; this audit reads live issue markers and PR metadata.

## Approaches considered

### Retained: explicit markers plus read-only live comparison

The issue remains readable while the evaluator receives exact fields without scraping historical prose.

### Declined: infer the active SHA from nearby prose

Issue bodies contain parent, repair, source, evidence, superseded, and historical heads. Guessing can select the wrong generation.

### Declined: automatically replace stale heads

A new commit can change semantics or evidence. Automatic replacement would hide the need for review and reclassification.

### Declined: automatic demotion or promotion

The evaluator cannot decide semantic equivalence, repair sufficiency, review eligibility, or delivery authority.

### Deferred: receipt, issue-generation, and label audits

Workflow conclusions, issue invariants, dependencies, labels, and canonical finding revisions can also expire review. This slice owns PR head/state drift only.

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
| Workflow conclusion drift | Receipt-audit finding with exact head binding. |
| Issue body versus label disagreement | Metadata evaluator. |
| Semantic identity after head movement | Complete-diff human or independent review. |
| Auto-remediation | Remains prohibited. |

## Exact execution

| Repository/head | Workflow | Current result | Evidence class |
| --- | --- | --- | --- |
| PR #274 `f0660030...` | focused syntax and fixture matrix | queued in `30586315692` | `target-test-prepared` |
| same | live #213/#160 comparison | queued in `30586315692` | `target-test-prepared` |
| same | Fieldwork integrity | queued in `30586315701` | `target-test-prepared` |

## Complete-diff and authority review

- Complete file fence: audit script, focused tests, read-only workflow, and this finding.
- Workflow permissions: `contents: read`, `issues: read`, `pull-requests: read`.
- Checkout credentials are disabled.
- Marker comments do not alter rendered issue prose.
- Exit behavior: clean `0`, drift `1`, invalid input `2`, transport block `3`.
- Current live marker set references PR #231 and #238 in both desks and PR #252 in #160, with identical expected heads across duplicate references.
- Known remaining gate: exact workflow execution and independent complete-diff review.

## Current disposition

- Finding state: `research-active`
- Review disposition: `EXECUTE`
- Exact next transition: complete audit `30586315692` and integrity `30586315701`
- Clearing condition: focused fixtures and live desk comparison pass at the exact head, followed by complete-diff review confirming read-only authority
- Non-delegable human decision: none

## Changes to the conclusion

| Date | Record | Change |
| --- | --- | --- |
| 2026-07-31 | first desk pass | Found expired PR #249/#252 heads and stale PR #259 workflow wording. |
| 2026-07-31 | `f0660030...` | Added explicit markers, live/snapshot evaluator, 404 classification, tests, and read-only workflow. |
| 2026-07-31 | successor cleanup | Removed closed PR #259 from promotion markers; retained repair and execution carriers as prose-only active state. |

## References

- initiative #254
- Review Queue #213
- Delivery Desk #160
- PR #274
- active marked PRs #231, #238, and #252
- repair PR #281 and execution carrier #273 as intentionally unmarked states
- `REVIEWING.md`
- `COORDINATION.md`
- `scripts/audit_desk_heads.py`
- `scripts/test_audit_desk_heads.py`
- `.github/workflows/desk-head-audit.yml`
