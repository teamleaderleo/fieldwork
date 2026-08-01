# Unit 16 — Bind confirmation modification to the correlated call

## In simple words

Gemini CLI can hold more than one tool call awaiting approval. A confirmation response carries a correlation ID for one call, while the baseline inline and editor modification paths selected `state.firstActiveCall`. That could feed call A's authority and arguments into call B's response path.

The owned candidate follows the confirmation loop's exact `callId`, requires the call to remain `AwaitingApproval`, passes that call into the modifier, and revalidates the same waiting generation after asynchronous modification before rebuilding or publishing arguments. It rejects removal, status loss, and same-ID generation replacement.

The repair now sits on current public main as one clean four-file commit. A new scheduler-level test drives two simultaneous approvals and resolves call 2 before call 1. Current execution is running through the owned carrier; the prior current-main attempt is retained as a pre-test lint failure.

## Current disposition

`REPAIR`

Last verified: `2026-08-01`  
Worker: `chatgpt:gpt-5.6-thinking`  
Priority-zero parent: [`teamleaderleo/fieldwork#435`](https://github.com/teamleaderleo/fieldwork/issues/435)  
Upstream contact authorized: `no`

## Contribution

- Target project: `google-gemini/gemini-cli`
- Proposed upstream destination: `google-gemini/gemini-cli:main`
- Proposed title: `fix(scheduler): bind confirmation modification to correlated call`
- Contribution synopsis: bind inline and editor modification authority to the response-correlated call, revalidate the approval generation after modifier awaits, and prove isolation with two concurrent approvals resolved out of order.
- Work class: `upstream-fork research`

## Exact identities

- Current public and fork base: [`f47d6c6f7a1308d81f9f57acf7d279f0928c5249`](https://github.com/google-gemini/gemini-cli/commit/f47d6c6f7a1308d81f9f57acf7d279f0928c5249)
- Owned target fork: `teamleaderleo/gemini-cli`
- Canonical source branch: [`fix/scheduler-confirmation-call-affinity`](https://github.com/teamleaderleo/gemini-cli/tree/fix/scheduler-confirmation-call-affinity)
- Canonical source head: [`0c3a86b0555e152b50ca55fd5f8dc53608571cbe`](https://github.com/teamleaderleo/gemini-cli/commit/0c3a86b0555e152b50ca55fd5f8dc53608571cbe)
- Source relationship: one commit ahead, zero behind current base
- Owned clean review PR: [`teamleaderleo/gemini-cli#24`](https://github.com/teamleaderleo/gemini-cli/pull/24)
- Source composition PR: merged [`teamleaderleo/gemini-cli#23`](https://github.com/teamleaderleo/gemini-cli/pull/23), squash result `0c3a86b0555e152b50ca55fd5f8dc53608571cbe`
- Active execution carrier: [`teamleaderleo/gemini-cli#6`](https://github.com/teamleaderleo/gemini-cli/pull/6), head `5daf74fccef0fda01ca75f5ef17254102cb2d64e`, run `30691280000`
- Fallback carrier: [`teamleaderleo/gemini-cli#22`](https://github.com/teamleaderleo/gemini-cli/pull/22), head `e41dd92ab680f5eb05370bf7d5263a70f6897e34`, run `30690739632`
- Corrected integration-test provenance: `6804d0b87c196b265c42276f2939573edaf6d89c`
- Predecessor clean source: `b359ece8a2bd059aef870a084ab9494eff16fa8f`
- Baseline defect evidence: closed [`teamleaderleo/gemini-cli#2`](https://github.com/teamleaderleo/gemini-cli/pull/2), head `a7f5cc934446849e19a08cc8f4527473ada74401`
- Fieldwork packet branch: [`p0/435-unit-16-gemini-confirmation-call-affinity`](https://github.com/teamleaderleo/fieldwork/tree/p0/435-unit-16-gemini-confirmation-call-affinity)
- Fieldwork packet PR: [`teamleaderleo/fieldwork#443`](https://github.com/teamleaderleo/fieldwork/pull/443)
- Exact packet tip: recorded in the latest #435 handoff; a tracked file cannot contain the SHA of its own commit.

## Current code and tests

### Product code

- [`confirmation.ts`](https://github.com/teamleaderleo/gemini-cli/blob/0c3a86b0555e152b50ca55fd5f8dc53608571cbe/packages/core/src/scheduler/confirmation.ts) — exact-ID waiting-call lookup and pre/post-await generation validation for inline and editor paths.

### Target-native tests

- [`confirmation.affinity.repair.test.ts`](https://github.com/teamleaderleo/gemini-cli/blob/0c3a86b0555e152b50ca55fd5f8dc53608571cbe/packages/core/src/scheduler/confirmation.affinity.repair.test.ts) — six focused authority and stale-generation controls.
- [`confirmation.test.ts`](https://github.com/teamleaderleo/gemini-cli/blob/0c3a86b0555e152b50ca55fd5f8dc53608571cbe/packages/core/src/scheduler/confirmation.test.ts) — eight adjacent confirmation controls with a stateful validating-to-waiting fixture.
- [`scheduler.confirmation-affinity.test.ts`](https://github.com/teamleaderleo/gemini-cli/blob/0c3a86b0555e152b50ca55fd5f8dc53608571cbe/packages/core/src/scheduler/scheduler.confirmation-affinity.test.ts) — real Scheduler, state manager, and message bus with two simultaneous approvals resolved in reverse order.

### Required generated or dependency files

- Not applicable.

## Changed-file fence

| Path | Role | Keep upstream? |
| --- | --- | --- |
| `packages/core/src/scheduler/confirmation.ts` | production | yes |
| `packages/core/src/scheduler/confirmation.affinity.repair.test.ts` | focused regression | yes, subject to maintainer preference on test placement |
| `packages/core/src/scheduler/confirmation.test.ts` | adjacent fixture correction | yes |
| `packages/core/src/scheduler/scheduler.confirmation-affinity.test.ts` | scheduler integration regression | yes, subject to maintainer preference on test placement |

## Evidence summary

| Claim | Evidence class | Exact receipt | Limit |
| --- | --- | --- | --- |
| Baseline inline modification can receive call A while the response owns call B | `target-executed` | PR #2 run `30505534210` | focused inline harness |
| Predecessor candidate binds inline/editor modification and rejects stale authority | `target-executed` | run `30595253180`, job `91046140436`, 14/14 | predecessor base and stateful unit harness |
| Current-main source is one clean four-file commit | `source-read` | compare `f47d6c6...0c3a86b` and PR #24 | execution still pending |
| Real scheduler ordering control exists at the exact source head | `target-test-prepared` | `scheduler.confirmation-affinity.test.ts` at `0c3a86b` | executor/modifier controlled; target run pending |
| First current-main attempt failed before product execution | `target-executed harness` | run `30690542009`, job `91344358931` | two unused declarations; no product claim affected |
| Full current-main focused/typecheck/preflight gate | `execution pending` | run `30691280000` | hosted-runner queue at this revision |

## Packet navigation

- [Deep dive](./DEEP_DIVE.md)
- [Approaches](./APPROACHES.md)
- [Tests and receipts](./TESTS.md)
- [Current-main repair receipt](./receipts/2026-08-01-current-main-repair.md)
- [Upstream issue draft](./UPSTREAM_ISSUE.md)
- [Upstream pull-request draft](./UPSTREAM_PR.md)
- [Review and human inspection guide](./REVIEW.md)

## Duplicate and prior-art result

- Search date: `2026-08-01`
- Current upstream issues, pull requests, branches, and commits were searched for confirmation call affinity, wrong-call modification, `firstActiveCall`, and editor correlation.
- Equivalent implementation found: `no`
- Relationship to prior work: independent candidate developed from Fieldwork #22, Fieldwork PR #45, target hub #5, portfolio PR #269, evidence PR #2, and repair carriers #6/#22.

## Repair history

1. Baseline target test reached the wrong-call assertion.
2. First source generation fixed exact-call selection and passed focused controls.
3. Adjacent tests exposed an impossible static mock state; the fixture became stateful.
4. Complete-diff review added same-ID approval-generation replacement rejection.
5. Predecessor source passed 14/14 plus core build/typecheck and clean publication.
6. Current-main attempt 1 generated the dual-call test transiently but stopped at two unused declarations before product execution.
7. The corrected dual-call test was committed, the four-file source was materialized, and PR #23 squashed it onto current main as `0c3a86b`.
8. Carrier #6 now validates the immutable source directly.

## Remaining work

Complete in this order:

1. Classify run `30691280000` at its first failing gate or retain its complete green receipt.
2. When green, record exact test counts, core typecheck, full preflight, clean-tree, and publication output.
3. Perform complete-diff self-review at `0c3a86b`; obtain eligible independent review.
4. Refresh public duplicate search immediately before any authorized contact.
5. Follow the target's issue-first contribution process after explicit authority.

## Blockers and limits

- Active carrier execution is queued at this packet revision.
- Full preflight has not yet completed on `0c3a86b`.
- Independent exact-head review remains required for promotion.
- The target contribution policy requires issue-first maintainer alignment.
- Public upstream contact remains unauthorized.
- This session's local network cannot resolve GitHub; execution evidence comes from retained Actions runs.

## Latest handoff

State: `REPAIR`  
Exact source head: `0c3a86b0555e152b50ca55fd5f8dc53608571cbe`  
Exact source base: `f47d6c6f7a1308d81f9f57acf7d279f0928c5249`  
Exact packet head: latest branch tip recorded on #435  
Tests: predecessor `14/14` green; current-main immutable-source run `30691280000` pending  
Temporary machinery remaining: carrier PRs #6 and #22; clean source PR #24 contains no workflow  
Next worker action: classify run `30691280000`, then synchronize every packet file and #435  
Public upstream interaction: none
