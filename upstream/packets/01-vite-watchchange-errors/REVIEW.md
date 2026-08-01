# Review — Vite `watchChange` error isolation

## In simple words

Review the exact two-file source diff, then confirm current-head execution. The key question is whether the server can report every plugin notification failure and still complete the file-event work Vite owns, without changing generic hook behavior.

## Review fence

- Public base: `e6b6b167afa0a80548829d1f24a0712f9194389a`
- Canonical source head: `a2ab7ca6183ad74d64066d6706e57a546e355224`
- Canonical branch: `fix/fieldwork-25-watchchange-error-isolation`
- Canonical source PR: [`teamleaderleo/vite#4`](https://github.com/teamleaderleo/vite/pull/4)
- Expected relation: two commits ahead, zero behind
- Expected changed files: exactly two
- Current self-review receipt: [`comment 5148481573`](https://github.com/teamleaderleo/vite/pull/4#issuecomment-5148481573)

Any head movement expires this review fence.

## Complete diff inventory

### Implementation

[`packages/vite/src/node/server/index.ts`](https://github.com/teamleaderleo/vite/blob/a2ab7ca6183ad74d64066d6706e57a546e355224/packages/vite/src/node/server/index.ts)

Expected semantic diff:

- one `notifyWatchChange` helper;
- `Promise.allSettled` over current environments;
- one logger call per rejected result;
- change path calls helper with `update`;
- add path calls helper with `create`;
- unlink path calls helper with `delete`;
- existing later work remains in its previous order.

### Test

[`packages/vite/src/node/__tests__/server/watchChange-error-isolation.spec.js`](https://github.com/teamleaderleo/vite/blob/a2ab7ca6183ad74d64066d6706e57a546e355224/packages/vite/src/node/__tests__/server/watchChange-error-isolation.spec.js)

Expected semantic coverage:

- change stale-cache reproduction and refreshed-content assertion;
- exact error object reaches logger;
- change reaches `hotUpdate`;
- add maps to create and reaches `hotUpdate` after rejection;
- unlink maps to delete and reaches `hotUpdate` after rejection;
- bounded timeouts prevent silent hangs;
- temporary project/server cleanup is registered.

## Source review checklist

### Ownership and flow

- [x] The helper sits in server orchestration, which owns environment fanout and later Vite work.
- [x] Generic plugin-container behavior remains unchanged.
- [x] All current environments are invoked once for each event.
- [x] Vite waits for every notification to settle before later work.
- [x] Every rejected result is logged.
- [ ] Independent reviewer confirms logger-failure behavior is acceptable under current Vite logger expectations.
- [x] Change invalidation remains before HMR.
- [x] Add public-file bookkeeping remains before HMR.
- [x] Unlink deletion graph work remains before HMR.
- [x] Config/env restart handling remains governed by existing HMR code.

### Compatibility

- [x] Successful hooks observe unchanged ordering and arguments.
- [x] Rejected hooks remain visible.
- [ ] Independent reviewer confirms the multiple-environment logging policy.
- [x] Continuing after a hook rejection matches Vite ownership of cache coherence.
- [x] No inspected supported contract grants the rejecting hook veto authority over invalidation/HMR.
- [x] Experimental bundled-development behavior is outside the claim.

### Error handling

- [x] The listener-level catches from #22188 remain present.
- [x] Later errors from invalidation/public-file/HMR still propagate to the listener catch under existing behavior.
- [x] Unit 01 isolates only `watchChange` rejection; it does not swallow unrelated later failures.
- [x] Error values accepted by the logger match existing Vite practice.
- [x] `EnvironmentPluginContainer.watchChange` exposes synchronous throws and asynchronous rejections as rejected environment promises.

### Test quality

- [x] The change test would fail on the exact public base because cached `alpha` survives.
- [x] The change test proves refreshed content, not only hook reachability.
- [x] Add and unlink tests would fail on the exact public base because `hotUpdate` is skipped.
- [x] Add and unlink tests assert the Rollup event and HMR event types independently.
- [x] Promise resolvers and timeouts are scoped to the exact state file.
- [x] Test cleanup is registered through `onTestFinished`.
- [ ] Independent reviewer confirms cleanup ordering cannot mask a product failure.
- [x] The test file location matches Vite unit-test discovery.

## Exact-head execution checklist

- [x] Zizmor run [`30674314445`](https://github.com/teamleaderleo/vite/actions/runs/30674314445) passed at `a2ab7ca6183ad74d64066d6706e57a546e355224`.
- [x] CI lint job [`91298285154`](https://github.com/teamleaderleo/vite/actions/runs/30674314447/job/91298285154) passed at the exact head.
- [x] Repository build passed inside the lint job.
- [x] Repository lint passed inside the lint job.
- [x] Formatting check passed inside the lint job.
- [x] Typecheck passed inside the lint job.
- [x] Documentation tests and workflow-file checks passed inside the lint job.
- [ ] CI run [`30674314447`](https://github.com/teamleaderleo/vite/actions/runs/30674314447) completes.
- [ ] Focused regression passes at the final head through Build&Test or a direct retained command.
- [ ] Supported Node unit matrix passes or each failure is classified.
- [ ] macOS and Windows results are inspected.
- [ ] Serve/build/bundled-development results are inspected according to the workflow.
- [x] Current completed workflow links and job IDs are copied into `TESTS.md`.

Queued Build&Test job IDs at this review revision:

- Linux Node 20: `91298369819`
- Linux Node 22: `91298369798`
- Linux Node 24: `91298369795`
- Linux Node 26: `91298369809`
- macOS Node 24: `91298369799`
- Windows Node 24.15: `91298369805`

## Prior-art and duplicate checklist

- [x] Read merged upstream PR [`vitejs/vite#22188`](https://github.com/vitejs/vite/pull/22188), its diff, comments, and reviews.
- [x] Confirm #22188 added error-reporting catches and all-event logging tests.
- [x] Confirm current public main retains fail-fast inner `Promise.all` before later work.
- [x] Search current Vite issues and pull requests for overlapping `watchChange` invalidation/HMR error work.
- [x] Record unit 01 as a distinct continuation fix.
- [ ] Repeat duplicate search immediately before public submission.

## Packet consistency checklist

- [x] `README.md` disposition matches live source and workflow state at this packet head.
- [x] `DEEP_DIVE.md` exact links point to the current source head.
- [x] `APPROACHES.md` retains losing and rejected options.
- [x] `TESTS.md` separates predecessor execution from current-head execution.
- [x] `UPSTREAM_ISSUE.md` route remains appropriate.
- [ ] `UPSTREAM_PR.md` test section is refreshed after final Build&Test results.
- [x] `teamleaderleo/vite#4` body names the current base, head, tests, and limits.
- [ ] Fieldwork #435 has the final compact handoff for this packet head.
- [x] No material finding from this session remains chat-only.

## Temporary machinery and branch hygiene

- [x] Canonical source diff contains no workflow files.
- [x] Canonical source diff contains no research directory.
- [x] Canonical source diff contains no dependency or lock changes.
- [x] Replay carrier [`teamleaderleo/vite#15`](https://github.com/teamleaderleo/vite/pull/15) is merged and retained only as history.
- [ ] Temporary work branch `unit-01/watchchange-rebase-work` may be deleted after final receipts and branch references are reconciled.
- [ ] Exact-base mirror should remain while the packet cites it.

## Human inspection guide

A reviewer should inspect in this order:

1. compare the public base to the canonical head and verify only two files changed;
2. read the public-base watcher handlers to see the abort point;
3. read the helper and confirm it changes only environment failure aggregation;
4. trace change/add/unlink from watcher callback through later Vite work;
5. read the stale-cache reproduction and add/unlink continuation controls;
6. inspect current-head CI and focused test output;
7. check the PR draft for claim inflation and stale receipts;
8. confirm public upstream interaction remains pending explicit authority.

## Current self-review result

`REPAIR`

Source-read review found no blocking product-code defect in the exact two-file diff. Current-head Zizmor and the CI lint job passed, including dependency installation, build, lint, formatting, typecheck, docs, and workflow-file checks. Six cross-platform Build&Test jobs remain queued, so current-head target execution and independent acceptance remain open.

The author performed this self-review and is not the eligible independent final accepter.

## Promotion criteria

Promote to `READY` only when:

- the final exact source head and public base are named;
- complete diff review finds no blocking defect;
- current-head focused regression passes;
- ordinary gates complete with accepted classifications;
- packet and PR draft match the final head;
- temporary execution machinery is absent from the canonical source;
- independent final review is recorded;
- the only remaining action is an explicitly authorized public submission.
