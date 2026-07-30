# F254-desk-head-audit: fail when review and delivery desks point at expired pull-request heads

Finding state: `research-active`

Workstream: `A`  
Canonical Fieldwork issue: `#254`  
Canonical finding path: `findings/F254-desk-head-audit/finding.md`  
Canonical implementation: draft Fieldwork pull request on `ops/desk-head-audit-2026-07-31`  
Exact implementation head: recorded by the pull request after this file is committed  
Exact base revision: `teamleaderleo/fieldwork@896a617c4b4dd8dd9fb9493d05f801c7baf9ade3`  
Strongest evidence class: `target-test-prepared`  
Reviewed input generation: Review Queue #213 and Delivery Desk #160 after 2026-07-31 exact-head synchronization  
Current review disposition: `EXECUTE`  
Desk routing: `none — the audit validates the desks`  
Upstream contact authorized: `no`

## In simple words

Fieldwork's review queue and delivery desk tell people which exact pull-request commits are ready for review, a decision, or merge. Several entries stayed on old commits after their branches moved. One old entry even kept telling people to merge a commit after later review found a concrete defect.

The proposed audit reads hidden exact-head markers from #213 and #160, fetches the named owned pull requests, and fails when a marker is stale, missing, duplicated, conflicting, closed, or merged. It only reports problems. It cannot approve, promote, merge, or contact upstream.

The implementation and focused fixtures are prepared. Exact-head workflow execution is the next gate.

## Why we care

An exact-head review is a statement about one immutable code generation. When a queue points at an older head, a reviewer can inspect the wrong diff, rely on expired tests, or merge code that differs from the accepted candidate. Manual prose is easy to miss because branch names stay the same while commits move.

This failure appeared three times in the current desk pass:

- PR #249 remained in the queue and D0 at an old locked head after a later parser defect and repair;
- PR #259 remained described as CI-queued after all exact-head gates completed;
- PR #252 remained at an older R1 head after four commits added meaningful read-invalidation behavior and changed the remaining question to a retention-policy decision.

## What happens if we leave it alone

Observed consequences include expired signoff, misleading merge instructions, incorrect workflow status, and review questions attached to code that no longer exists at the branch tip. The frequency across all Fieldwork records is unknown because current desks are prose-driven and lack an automatic comparison.

## Current finding

The queue and desk need an explicit machine-readable reference for each active owned pull request. A read-only evaluator should compare that expected head with live pull-request metadata and fail closed on stale or malformed routing data.

The proposed marker is:

```text
<!-- fieldwork:desk-ref repo=teamleaderleo/fieldwork pr=231 head=<40-hex-sha> lane=R3 -->
```

The marker carries only routing identity. Narrative prose and canonical findings continue to explain evidence, limits, and decisions.

### Claim table

| Claim | Evidence class | Exact support | Limit |
| --- | --- | --- | --- |
| #213/#160 can retain an expired exact head after a branch moves. | `source-read` | Live PR #249 and PR #252 metadata compared with their desk text before repair. | Two observed owned-repository examples do not measure total historical frequency. |
| A stale desk head can preserve expired review or merge wording. | `source-read` | PR #249 old D0 entry versus later binary-block defect and repaired head. | Human behavior after reading the stale entry was not measured. |
| Explicit markers can be compared with live pull-request heads without write authority. | `target-test-prepared` | `scripts/audit_desk_heads.py` and `.github/workflows/desk-head-audit.yml`. | Exact workflow has not run at this finding generation yet. |
| The audit does not issue promotion decisions. | `source-read` | Script output is JSON findings only; workflow permissions are read-only. | Repository administrators still control workflow and issue edits. |

## System and ownership map

- Human entrypoints: Review Queue #213 and Delivery Desk #160.
- Durable reasoning: canonical finding files and implementation pull requests.
- Machine-readable input: hidden `fieldwork:desk-ref` markers in issue bodies.
- Live authority source: GitHub pull-request state and `head.sha` for owned repositories.
- Evaluator: `scripts/audit_desk_heads.py`.
- Focused regressions: `scripts/test_audit_desk_heads.py`.
- Execution surface: `.github/workflows/desk-head-audit.yml` with read-only contents, issues, and pull-request permissions.
- Side effect: workflow pass or failure only.
- Recovery: update or remove the stale desk marker and synchronize the narrative record.
- Human authority: acceptance, promotion, design choice, merge, and upstream contact remain outside the evaluator.

## Historical precedent

### Fieldwork exact-head review protocol

- Source: `REVIEWING.md`.
- Revision: `896a617c4b4dd8dd9fb9493d05f801c7baf9ade3`.
- Principle supported: code-head movement or reviewed-input generation change expires a disposition; queues must carry exact referenced states and a validation timestamp to claim currency.
- Important difference: the current protocol is manual. This finding implements one narrow detector for pull-request head and state drift.

### Coordination compiler

- Source: `scripts/coordination_compiler.py` and `.github/workflows/coordination-compiler.yml`.
- Revision: `896a617c4b4dd8dd9fb9493d05f801c7baf9ade3`.
- Principle supported: read-only deterministic evaluators can validate explicit coordination inputs and fail closed on malformed or stale state.
- Important difference: the compiler evaluates retained graph fixtures. The desk audit reads live issue markers and pull-request metadata.

## Approaches considered

### Retained approach: explicit hidden markers plus read-only live audit

The issue body remains readable, and the evaluator receives exact fields without parsing headings or prose. A changed head fails until a coordinator synchronizes the desk.

### Declined: scrape every SHA near a pull-request number

Prose contains historical, removed, superseded, target-source, and evidence heads. Guessing which SHA is active would create false positives and could silently select the wrong generation.

### Declined: auto-update desk heads

A new commit can invalidate semantics, evidence, or review. Automatically replacing the SHA would launder head movement instead of forcing reclassification.

### Declined: auto-demote or promote issues

The evaluator lacks authority to decide whether new code is equivalent, repairable, accepted, or mergeable. It reports drift only.

### Deferred: verify every evidence receipt and issue-body generation

Workflow runs, issue invariants, labels, dependencies, and canonical finding revisions also expire reviews. This first slice owns pull-request head/state drift only.

## Edge cases covered by prepared fixtures

| Edge case or control | Expected result |
| --- | --- |
| Multiple valid markers in one issue | Parsed and audited. |
| Issue with no markers | Invalid input. |
| Malformed SHA or marker fields | Invalid input. |
| Duplicate pull request in one issue | Invalid input. |
| Live head differs from expected head | `stale_head`. |
| Pull request missing from the snapshot or API | `missing_pull_request`. |
| Closed active entry | `closed_active_entry`. |
| Merged active entry | `merged_active_entry`. |
| Same pull request carries conflicting heads across issues | `conflicting_expected_heads`. |
| Current open pull request at the exact head | Pass. |

## Edge cases deferred or outside scope

| Edge case | Why deferred | Owning next record or reopening trigger |
| --- | --- | --- |
| External public upstream pull requests | Public upstream interaction and trust boundaries differ. | Add only after explicit authority and reference-policy design. |
| Workflow conclusion drift | Requires binding named receipts to exact heads and claim classes. | Separate receipt-audit finding. |
| Issue body and label disagreement | Existing integrity rule; separate metadata evaluator. | Extend after exact-head slice proves useful. |
| Semantic identity after head movement | Requires complete-diff review. | Human or independent reviewer. |
| Auto-remediation | Could overwrite a valid demotion or hide new code. | Remains prohibited. |

## Prepared execution

| Repository/head | Command or workflow | Platform/environment | Current result | Evidence class |
| --- | --- | --- | --- | --- |
| branch `ops/desk-head-audit-2026-07-31` | `python3 -m py_compile scripts/audit_desk_heads.py scripts/test_audit_desk_heads.py` | GitHub Actions Ubuntu 24.04 | prepared | `target-test-prepared` |
| same | `python3 scripts/test_audit_desk_heads.py` | GitHub Actions Ubuntu 24.04 | prepared | `target-test-prepared` |
| same | live audit of #213 and #160 with read-only token | GitHub Actions Ubuntu 24.04 | prepared | `target-test-prepared` |

## Complete-diff and compatibility review

- Complete changed-file fence: audit script, focused tests, read-only workflow, and this finding.
- Base relationship: clean branch from current Fieldwork main `896a617c...`.
- API surface: public GitHub REST reads for owned repository issues and pull requests.
- Permissions: `contents: read`, `issues: read`, `pull-requests: read`.
- Marker compatibility: markers are HTML comments and do not alter rendered issue prose.
- Failure behavior: malformed inputs exit 2, live transport failures exit 3, detected drift exits 1, clean audit exits 0.
- Known implementation risk: exact workflow execution and complete-diff review remain pending.

## Current disposition and desk routing

- Finding state: `research-active`
- Review disposition: `EXECUTE`
- Exact next transition: open the draft pull request and run focused plus live exact-head audit.
- Clearing condition: workflow passes against the current #213/#160 markers and complete-diff review finds no write or silent-promotion path.
- Required subgates: fixture matrix, live read-only API comparison, Fieldwork integrity, permission review.
- User decision requested: none.

## Changes to the canonical conclusion

| Date | Pull request or commit | Change in conclusion |
| --- | --- | --- |
| 2026-07-31 | desk synchronization pass | Found stale PR #249 and PR #252 heads plus completed PR #259 checks. |
| 2026-07-31 | branch `ops/desk-head-audit-2026-07-31` | Prepared explicit marker parser, live comparator, focused fixtures, and read-only workflow. |

## References

- `https://github.com/teamleaderleo/fieldwork/issues/254`
- `https://github.com/teamleaderleo/fieldwork/issues/213`
- `https://github.com/teamleaderleo/fieldwork/issues/160`
- `https://github.com/teamleaderleo/fieldwork/pull/249`
- `https://github.com/teamleaderleo/fieldwork/pull/252`
- `https://github.com/teamleaderleo/fieldwork/pull/259`
- `REVIEWING.md`
- `COORDINATION.md`
- `scripts/coordination_compiler.py`
- `scripts/audit_desk_heads.py`
- `scripts/test_audit_desk_heads.py`
- `.github/workflows/desk-head-audit.yml`
