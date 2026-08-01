# Review — unit 17 confirmation waiting ownership

## In simple words

The candidate repairs two ownership failures in Gemini CLI's confirmation-wait callback: rejected waits can skip their leave transition, and direct boolean callbacks can report idle during overlapping waits. The repair uses guaranteed per-call cleanup plus a scheduler-owned count while preserving the existing boolean API.

The final reviewer should challenge the error-precedence behavior, counted callback semantics when observers throw, current IDE fallback compatibility, and the choice to open an issue before any source pull request.

## Review subject

- Work class: current-head source materialization from a proved staged repair
- Target repository: `google-gemini/gemini-cli`
- Proposed upstream base: `f47d6c6f7a1308d81f9f57acf7d279f0928c5249`
- Canonical source branch: `teamleaderleo/gemini-cli:fix/scheduler-confirmation-waiting-ownership`
- Exact source head: `SOURCE_HEAD_PENDING_30674864738`
- Fieldwork packet branch: `p0/435-unit-17-gemini-confirmation-waiting`
- Exact packet head: recorded in the final handoff on Fieldwork issue #435
- Complete changed-file fence: three production files and three test files listed below
- Upstream-contact authority: `false`
- Current disposition: `ISSUE FIRST`

## Review reading order

1. [`README.md`](./README.md)
2. [`DEEP_DIVE.md`](./DEEP_DIVE.md)
3. [`APPROACHES.md`](./APPROACHES.md)
4. [`TESTS.md`](./TESTS.md)
5. exact product diff
6. exact test diff
7. [`UPSTREAM_ISSUE.md`](./UPSTREAM_ISSUE.md)
8. [`UPSTREAM_PR.md`](./UPSTREAM_PR.md)

## Complete changed-file fence

Production:

- `packages/core/src/scheduler/confirmation-wait-tracker.ts`
- `packages/core/src/scheduler/confirmation.ts`
- `packages/core/src/scheduler/scheduler.ts`

Tests:

- `packages/core/src/scheduler/confirmation-wait-tracker.test.ts`
- `packages/core/src/scheduler/confirmation.waiting-state.repair.test.ts`
- `packages/core/src/scheduler/confirmation.waiting-state.test.ts`

## Exact diff links

- Complete owned compare: `https://github.com/teamleaderleo/gemini-cli/compare/f47d6c6f7a1308d81f9f57acf7d279f0928c5249...SOURCE_HEAD_PENDING_30674864738`
- Production files: resolve from the compare above after the source receipt is finalized
- Tests: resolve from the compare above after the source receipt is finalized
- Generated or dependency files: none expected

## Claims requiring judgment

| Claim or design choice | Evidence | Reviewer question |
| --- | --- | --- |
| Every entered confirmation wait needs one leave attempt after success or failure. | Target-negative run `30504716033`, job `90751825412`; staged run `30581298716`. | Does the helper cover every actual wait exit without changing the bus/IDE race? |
| Per-call cleanup alone cannot represent global overlap with a boolean callback. | Retained probe result `[true, true, false]` with one wait still pending. | Is a scheduler-owned count the smallest compatible owner, or should call identity become public? |
| A primary confirmation failure should outrank a secondary clear-callback failure. | Repair tests and explicit error-precedence table in `DEEP_DIVE.md`. | Should cleanup failure be logged and suppressed only on an already-failed wait? |
| A successful wait followed by a failing clear callback should surface the callback error. | Repair test. | Does preserving current observer-failure visibility create an undesirable confirmation failure after approval? |
| IDE rejection should keep current fallback behavior and allow the bus to finish the wait. | Current `confirmation.ts` at `f47d6c6f…`; current-head test. | Does this test accurately preserve the intended IDE/bus ownership contract? |
| The first external `true` callback must succeed before the tracker records an active wait. | Tracker test. | Is retrying a later enter after observer failure preferable to marking an invisible active wait? |
| The final wait remains removed internally if the external `false` callback throws. | Tracker implementation and helper error test. | Is internal ownership accuracy preferable to retrying the final external clear? |

## Known risks

- The count relies on all scheduler confirmation waits using the tracker. The current source has two call sites, and both are fenced by the transform and tests.
- A throwing final clear leaves the external observer with stale state even though the internal count is zero. The operation surfaces that failure so the owner can react.
- Future direct uses of `resolveConfirmation` could bypass scheduler aggregation. The call-scoped helper still balances each direct wait, while overlap aggregation remains the scheduler's responsibility.
- The focused suite proves lifecycle behavior inside Linux GitHub Actions. Full `preflight` and broader platform coverage remain open.
- Upstream source can advance before authorization; refresh and rerun before publication.

## Evidence limits

- Full `npm run preflight` has not executed on the clean current source head.
- The clean-head run is pending under `30674864738` until this packet is refreshed with its exact receipt.
- No manual two-approval subagent timeout exercise has been retained.
- No public maintainer feedback exists because upstream contact remains unauthorized.

## Staleness check

- Current upstream head checked: `f47d6c6f7a1308d81f9f57acf7d279f0928c5249` on 2026-08-01
- Candidate base relationship: clean branch created directly from that exact head
- Relevant source paths changed upstream since the original `3499c84f…` execution base: `yes`; `scheduler.ts` now has two confirmation call sites, both included in the current transform
- Duplicate/overlap search date: 2026-08-01
- Open replacement work found: no exact repair found; merged PR #18415 is the callback origin and adjacent reports cover different confirmation concerns
- Packet and target carrier descriptions synchronized: current carrier state recorded; final source receipt pending

## Source cleanliness

- [x] Intended clean diff contains no Fieldwork-only files.
- [x] Intended clean diff contains no temporary workflows or publishers.
- [x] Intended clean diff contains no stale execution artifacts.
- [x] Intended clean diff contains no unrelated formatting or generated churn.
- [x] No snapshot, lock, or dependency change is expected.
- [ ] Commit-pinned source links await the final clean source head.

## Test review

- [x] The original intended assertion ran.
- [x] Baseline/candidate relationship is explicit.
- [x] Setup and product failures are separated.
- [x] Cancellation and callback-failure paths are covered.
- [x] Existing confirmation controls are present.
- [x] Platform and broader-suite limits are explicit.
- [x] Ordinary target gate `npm run preflight` is named as unevaluated.
- [ ] Final current-head source receipt awaits run `30674864738`.

## Draft review

- [x] Issue draft describes the lifecycle contract without prevalence claims.
- [x] PR draft follows the current target headings.
- [x] Target terminology and focused validation commands are used.
- [x] Public drafts exclude internal process history from their sendable bodies.
- [x] AI-assisted development disclosure is included for human verification.
- [ ] Approved issue number and maintainer direction remain pending.

## Reviewer disposition

`ACCEPT FOR ISSUE-FIRST PREPARATION`

Reviewed source head: `SOURCE_HEAD_PENDING_30674864738`  
Reviewed packet head: final handoff revision pending  
Reason: the narrow repair is coherent and its staged behavior is executed; target policy and public-contact authority require an issue before a source PR.  
Clearing condition: finalize the current clean source receipt, run `npm run preflight` on that exact head, obtain authorization, and post the issue draft for maintainer direction.  
Reviewer eligibility: self-review only; independent review required before public submission.

## Human deep-dive guide

The final human reviewer should focus on:

1. whether observer-error precedence preserves the right primary failure;
2. whether count-based aggregation behaves correctly when enter or final-leave callbacks throw;
3. whether current IDE rejection fallback remains byte-for-byte compatible in effect;
4. whether issue-first discussion is the right route under the target contribution policy.

Suggested response:

`Unit 17 looks ready for issue-first upstream preparation`  
— or —  
`Unit 17 concern: <specific source, test, compatibility, or framing issue>`
