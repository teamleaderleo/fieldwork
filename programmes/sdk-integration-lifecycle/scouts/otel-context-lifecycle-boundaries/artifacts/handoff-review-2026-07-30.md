# Exact-head review — OpenTelemetry synthesis handoff

## In simple words

This review checks whether Fieldwork PR #32 is ready to move from a durable research archive into repository promotion. The packet now contains a current polished report and a restartable handoff, but the branch is 107 commits behind current Fieldwork main and has accumulated a large historical diff. The correct disposition is **HOLD**: preserve it as evidence, then materialize the retained packet on a fresh current-main branch and perform an independent complete-diff review.

## Scope

- Repository: `teamleaderleo/fieldwork`
- Pull request: #32
- Reviewed issue or decision body generation: `not applicable` to the HOLD disposition. Issues #19, #194, #216, #225, and #226 were read as live coordination references, but their bodies do not define the invariant, authority, or clearing condition under review.
- Reviewed live metadata generation: `not applicable` to the HOLD disposition. State text and labels were checked for coordination consistency only.
- Work class: `evidence/documentation` with supporting `upstream-fork research`
- Canonical branch: `fieldwork/opentelemetry-js/otel-async-retry-correlation`
- Exact reviewed packet head: `d424993641195d4056ee2c47098afcae66f5c854`
- Receipt commits: the commits after the reviewed packet head add or clarify this review file only; they do not modify the reviewed report, handoff, source evidence, or fork state.
- Current-main SHA: `13481ab6cce6039f5f8c127d5a0509d657f517d8`
- Merge base: `09fe47ac92ec9c0c333b4979011f6321795deff2`
- Current-main relation: diverged; packet is 57 commits ahead and 107 commits behind
- Changed-file fence: complete PR #32 diff through `d424993641195d4056ee2c47098afcae66f5c854`, with emphasis on `report.md`, `artifacts/handoff-2026-07-30.md`, and the retained artifact index
- Author eligible to accept or merge: `no` for final repository promotion; self-review only
- Upstream contact authorized: `no`

## Claim-scoped evidence

| Claim or invariant | Evidence class | Exact receipt, source, or artifact | Coverage limits |
| --- | --- | --- | --- |
| Ordinary Node async context propagation is healthy in the retained cases | `model-executed` | `artifacts/async-retry-probe.js` and output | Reduced Node model; no installed target package |
| Baseline lifecycle failures are represented by 30 native tests | `target-test-prepared` | fork PR #1 at `026855a81e3f4bb0bca4c46610446648a92a9372` | Prepared tests are not executed failures |
| NodeSDK startup/shutdown coordination works at the reviewed fork head | `target-executed` | fork PR #7 at `d5abec0e6c979c5152346bf36b2991bdf0aa3d52` | Owned fork exact head; no upstream acceptance |
| Metrics one-shot, fanout, final collection, and diagnostics compose successfully | `target-executed` | fork PR #9 at `f3740eb9bda8ec22ae81941adcdaf0de0aa3c764` | Compatibility direction remains issue-first; timeout aftermath separate |
| Direct logs provider lifecycle reentry is contained | `target-executed` | fork PR #8 at `7d49735173c8467a88afab426a4bf02910a3dd62` | Direct synchronous reentry only |
| Delayed logs and metrics same-owner lifecycle recursion forms a self-dependency | `target-executed` | fork PR #10 at `6bbd0f34b1e8579840033c7ded88ff8059afbb3f`; PR #12 at `f2682bd4bacfa9999139aad29b02ab2055da0a4a` | Does not select a portable production repair |
| Trace provider one-shot state passes the current product matrix | `target-executed` | fork PR #4 at `fb40c7abb98bc65681b222004ed86619872eca9e` | Changelog-only failure separate; delivery composition unresolved |
| Trace delayed-reentry composition passes the current matrix | `target-executed` | fork PR #15 at `b3e3ec49ae27bb2c5e6bf32ceb1f868473af24f4` | Clean merge composition; final linear restack required |
| Existing-span trace shutdown boundary has a native characterization | `target-test-prepared` | fork PR #16 at `73380c9d2675ba69c812f2bc5a82383faa18a835` | Matrix queued at handoff time; no contract selected |
| Attempt-all fanout still has a mutation hole | `source-read` | Fieldwork issue #225; report and handoff repair note | Requires native mutation control and repaired exact head |
| Failed `startNodeSDK()` setup cleanup preserves the primary error in the candidate | `source-read` and `target-test-prepared` | fork PR #3 at `2482d8c49c8b6e01a282a36da55e48b4a4dc8747` | No retained exact-head target execution |
| PR #32 is not promotion-ready | `source-read` | compare current main `13481ab...` to packet `9a9f917...` and later packet-only commits | Relation may change; fresh materialization remains required |

- Commands or workflow runs: exact fork runs are recorded on their respective pull requests and summarized in `report.md` and `artifacts/handoff-2026-07-30.md`.
- Platforms and runtimes: fork GitHub Actions matrices plus Node `v22.16.0` for retained models; see individual receipts for exact matrix coverage.
- Focused tests: package-native NodeSDK, trace, logs, and metrics cases as named in the fork pull-request descriptions.
- Named full repository gate or command set: not claimed for Fieldwork PR #32 beyond its earlier integrity and reference-policy checks; fork product matrices are `target-executed`, not a Fieldwork `full-gate` claim.
- Material paths not exercised by that gate: upstream maintainer review, real application integration, ecosystem frequency, installation disposal, trace existing-span policy, timeout aftermath, and delayed-recursion runtime repair.
- Checks skipped, not triggered, or still running: fork PR #16 matrix was queued at handoff time; PR #3 exact-head target execution remains absent; PR #2 standalone execution remains absent.
- Retained artifacts or receipts: `report.md`, `artifacts/handoff-2026-07-30.md`, the exact fork pull requests listed above, and the live coordination issues as non-dispositive discovery surfaces.

## Self-review before handoff

- Strongest claim traced to exact support: `yes`
- Intended assertion actually ran: `yes` for claims marked `target-executed`; `not applicable` for source-only and prepared claims
- Harness, setup, fixture, installation, and product failures separated: `yes`
- Candidate or theory rewritten after contradictory execution: `yes`; metrics final collection and fanout mutation are retained examples
- Live issue, report, pull-request description, receipt, and queue entry synchronized: `yes` for the report, handoff, PR description, scout handoff comment, and signals-worker correction; Delivery Desk ownership is coordinator-only and not part of this review transition

## Complete-diff review

- Invariant or contract under review: the packet must preserve accurate evidence classes, current exact heads, negative results, active dependencies, and a restartable clearing condition without implying merge or upstream readiness.
- Strongest positive evidence: exact-head target execution for fork PRs #4, #7, #8, #9, #10, #12, and #15; current live coordination in #19 and #194.
- Negative controls: metrics predecessor E2E failure, healthy unrelated lifecycle join, cross-owner nesting, direct versus delayed reentry, and the live-array mutation counterexample.
- Compatibility controls: released diagnostic order, final metrics collection, first-caller timeout ownership, failed-shutdown terminal state, and ordinary concurrent promise sharing.
- Error, cleanup, retry, authority, and recovery paths examined: setup cleanup, primary-error preservation, async cleanup rejection, partial global publication, provider/reader failure, timeout, late physical cleanup, recursive lifecycle promises, child mutation, and process-global disposal.
- Diff-quality concerns: PR #32 has a large historical packet, is 107 commits behind main, and includes superseded snapshots alongside current artifacts. That is acceptable as an archive but not as a merge-ready diff.
- Evidence or claims that remain unsupported: ecosystem prevalence, production frequency, upstream acceptance, a portable delayed-recursion repair, the trace existing-span policy, timeout-aftermath reporting, reader-constructor transaction repair, and ownership-aware global disposal.

## Coordination state

- Dependencies: #194, #216, #221, #225, #226, fork PRs #3, #4, #6, #15, and #16
- Supersedes: the stale synthesis in the previous `report.md`
- Superseded by: none; a future current-main materialization should supersede PR #32 as the canonical merge surface
- Execution carriers to close: none identified on the current PR #32 branch; historical temporary execution workflow was removed without a receipt
- Issue `State:` text agrees with labels: `yes` for the live surfaces checked at handoff time; non-dispositive to this HOLD review
- Pull-request description is current for the handoff head: `yes`
- Current-main relation is known: `yes`

## Disposition

Disposition: **HOLD**

Accepted transition or clearing condition:

1. preserve PR #32 as the durable archive;
2. create a fresh synthesis branch from current Fieldwork main;
3. copy only retained report and artifact content, plus current live-head summaries;
4. exclude obsolete execution machinery and clearly mark historical branches;
5. run Fieldwork integrity and reference-policy checks;
6. perform a new independent complete-diff review;
7. then decide whether to replace, close, or retain PR #32.

## Uncertainty

The technical work still has open contract decisions for trace spans already recording at shutdown, delayed same-owner recursion, metrics physical cleanup after public timeout, cached metrics objects, reader binding transactionality, and process-global installation disposal. The operational frequency and ecosystem consequence are not measured. No upstream acceptance or maintainer position is claimed.

## Expiry

This review applies to packet head `d424993641195d4056ee2c47098afcae66f5c854`. Later commits are review-receipt-only clarifications unless the report, handoff, source evidence, or fork-state summary changes. A packet-content change, current-main relation change relevant to the clearing condition, dependency change, policy change, or contradictory execution expires the disposition unless semantic identity is proved within the reviewed fence. Unrelated issue comments do not expire this review because issue bodies and metadata are not disposition inputs.