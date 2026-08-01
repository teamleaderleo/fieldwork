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

- [ ] The helper sits in server orchestration, which owns environment fanout and later Vite work.
- [ ] Generic plugin-container behavior remains unchanged.
- [ ] All current environments are invoked once for each event.
- [ ] Vite waits for every notification to settle before later work.
- [ ] Every rejected result is logged.
- [ ] A logger failure cannot create an unexplained partial continuation path; inspect current logger expectations.
- [ ] Change invalidation remains before HMR.
- [ ] Add public-file bookkeeping remains before HMR.
- [ ] Unlink deletion graph work remains before HMR.
- [ ] Config/env restart handling remains governed by existing HMR code.

### Compatibility

- [ ] Successful hooks observe unchanged ordering and arguments.
- [ ] Rejected hooks remain visible.
- [ ] Multiple environment failures have an acceptable logging policy.
- [ ] Continuing after a hook rejection matches Vite ownership of cache coherence.
- [ ] No supported contract grants the rejecting hook veto authority over invalidation/HMR.
- [ ] Experimental bundled-development behavior is outside the claim.

### Error handling

- [ ] The listener-level catches from #22188 remain present.
- [ ] Later errors from invalidation/public-file/HMR still propagate to the listener catch under existing behavior.
- [ ] Unit 01 isolates only `watchChange` rejection; it does not swallow unrelated later failures.
- [ ] Error values accepted by the logger match existing Vite practice.

### Test quality

- [ ] The change test would fail on the exact public base because cached `alpha` survives.
- [ ] The change test proves refreshed content, not only hook reachability.
- [ ] Add and unlink tests would fail on the exact public base because `hotUpdate` is skipped.
- [ ] Add and unlink tests assert the Rollup event and HMR event types independently.
- [ ] Promise resolvers and timeouts cannot resolve from unrelated server activity.
- [ ] Test cleanup cannot close the server twice in a harmful way.
- [ ] Temporary directory cleanup runs after server shutdown without masking the product result.
- [ ] The test file location and command match Vite's unit-test discovery.

## Exact-head execution checklist

- [x] Zizmor run [`30674314445`](https://github.com/teamleaderleo/vite/actions/runs/30674314445) passed at `a2ab7ca6183ad74d64066d6706e57a546e355224`.
- [ ] CI run [`30674314447`](https://github.com/teamleaderleo/vite/actions/runs/30674314447) completes.
- [ ] Focused regression passes at the final head.
- [ ] Build passes at the final head.
- [ ] Formatter check passes for both files.
- [ ] ESLint passes for both files.
- [ ] Supported Node unit matrix passes or each failure is classified.
- [ ] macOS and Windows results are inspected.
- [ ] Serve/build/bundled-development jobs are inspected according to the workflow.
- [ ] Current-head workflow links and job counts are copied into `TESTS.md`.

## Prior-art and duplicate checklist

- [x] Read merged upstream PR [`vitejs/vite#22188`](https://github.com/vitejs/vite/pull/22188), its diff, comments, and reviews.
- [x] Confirm #22188 added error-reporting catches and all-event logging tests.
- [x] Confirm current public main retains fail-fast inner `Promise.all` before later work.
- [x] Search current Vite issues and pull requests for overlapping `watchChange` invalidation/HMR error work.
- [x] Record unit 01 as a distinct continuation fix.
- [ ] Repeat duplicate search immediately before public submission.

## Packet consistency checklist

- [ ] `README.md` disposition matches live source and workflow state.
- [ ] `DEEP_DIVE.md` exact links point to the final source head.
- [ ] `APPROACHES.md` retains losing and rejected options.
- [ ] `TESTS.md` separates predecessor execution from current-head execution.
- [ ] `UPSTREAM_ISSUE.md` route remains appropriate.
- [ ] `UPSTREAM_PR.md` test section reflects final accepted receipts.
- [ ] `teamleaderleo/vite#4` body names the final base, head, tests, and limits.
- [ ] Fieldwork #435 has one compact final handoff.
- [ ] No finding exists only in chat.

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

Source-read review finds a coherent, bounded two-file candidate on current public main. Zizmor passed. Current-head CI and focused execution remain open, and the expanded test requires exact-head review after those results.

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
