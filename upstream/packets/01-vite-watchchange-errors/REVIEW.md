# Review — Vite `watchChange` error isolation

## In simple words

Review the exact two-file source diff and the retained execution record. The key question is whether the server can report every plugin notification failure and still complete the file-event work Vite owns, without changing generic hook behavior.

## Review fence

- Work class: upstream-fork source candidate
- Public base: `e6b6b167afa0a80548829d1f24a0712f9194389a`
- Canonical source head: `a2ab7ca6183ad74d64066d6706e57a546e355224`
- Canonical branch: `fix/fieldwork-25-watchchange-error-isolation`
- Canonical source PR: [`teamleaderleo/vite#4`](https://github.com/teamleaderleo/vite/pull/4)
- Expected relation: two commits ahead, zero behind
- Expected changed files: exactly two
- Current self-review receipt: [`comment 5148481573`](https://github.com/teamleaderleo/vite/pull/4#issuecomment-5148481573)

Any source-head movement or material reviewed-input change expires this review fence.

## Complete diff inventory

### Implementation

[`packages/vite/src/node/server/index.ts`](https://github.com/teamleaderleo/vite/blob/a2ab7ca6183ad74d64066d6706e57a546e355224/packages/vite/src/node/server/index.ts)

Reviewed semantic diff:

- one server-local `notifyWatchChange` helper;
- `Promise.allSettled` over the current environment snapshot;
- one configured-logger call per rejected result;
- change calls the helper with `update`;
- add calls it with `create`;
- unlink calls it with `delete`;
- existing later invalidation, public-file, deletion, restart, and HMR work remains in its previous order.

### Test

[`packages/vite/src/node/__tests__/server/watchChange-error-isolation.spec.js`](https://github.com/teamleaderleo/vite/blob/a2ab7ca6183ad74d64066d6706e57a546e355224/packages/vite/src/node/__tests__/server/watchChange-error-isolation.spec.js)

Reviewed coverage:

- change stale-cache reproduction and refreshed-content assertion;
- exact error object reaches the logger;
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
- [x] Change invalidation remains before HMR.
- [x] Add public-file bookkeeping remains before HMR.
- [x] Unlink deletion graph work remains before HMR.
- [x] Config/env restart handling remains governed by existing HMR code.
- [ ] Independent reviewer confirms logger-failure and multiple-environment logging expectations.

### Compatibility

- [x] Successful hooks observe unchanged ordering and arguments.
- [x] Rejected hooks remain visible.
- [x] Continuing after rejection matches Vite ownership of cache coherence.
- [x] No inspected supported contract grants a rejecting hook veto authority over invalidation/HMR.
- [x] Experimental bundled-development behavior is outside the product claim.
- [ ] Independent reviewer confirms the compatibility boundary.

### Error handling

- [x] Listener-level catches from #22188 remain present.
- [x] Later invalidation/public-file/HMR failures still propagate under existing behavior.
- [x] Unit 01 isolates only `watchChange` rejection; it does not swallow unrelated later failures.
- [x] Error values passed to the configured logger match existing Vite practice.
- [x] Synchronous hook throws and asynchronous rejections become rejected environment promises.

### Test quality

- [x] The change test fails on the exact public base because cached `alpha` survives.
- [x] The change test proves refreshed content, not only hook reachability.
- [x] Add and unlink tests fail on the exact public base because `hotUpdate` is skipped.
- [x] Add and unlink assert Rollup and HMR event types independently.
- [x] Promise resolvers and timeouts are scoped to the exact state file.
- [x] Cleanup is registered through `onTestFinished`.
- [x] The test file location matches Vite unit-test discovery.
- [ ] Independent reviewer confirms cleanup ordering cannot mask a product failure.

## Exact-head execution checklist

- [x] Zizmor run [`30674314445`](https://github.com/teamleaderleo/vite/actions/runs/30674314445) passed.
- [x] CI lint pipeline passed, including install, build, lint, formatting, typecheck, docs, and workflow checks.
- [x] Linux Node 20 Build&Test passed.
- [x] Linux Node 22 Build&Test passed.
- [x] Linux Node 24 Build&Test passed.
- [x] Linux Node 26 Build&Test passed.
- [x] macOS Node 24 Build&Test passed.
- [x] Windows repository build passed.
- [x] Windows unit suite passed.
- [x] Current focused regression passed: 3/3 tests.
- [x] Windows ordinary serve passed on rerun.
- [x] Initial Windows HMR/SSR ordinary-serve failure was inspected and classified.
- [x] Rerun Windows HMR/SSR bundled-development failures were inspected and classified.
- [ ] Supplementary third Windows full-job rerun [`91344668365`](https://github.com/teamleaderleo/vite/actions/runs/30674314447/job/91344668365) completes; its status does not alter the current source classification unless it exposes a Unit 01-linked failure.

### Accepted Windows failure classification

Attempt 1 failed in an existing `playground/hmr-ssr` timing assertion after the Unit 01 focused test passed. Attempt 2 passed ordinary serve, then failed three timing/state assertions in the same HMR/SSR family during bundled-development. The failure location moved while the Unit 01 regression stayed green; all Linux/macOS full jobs passed.

Classification: unrelated Windows HMR/SSR integration flakiness. This remains a recorded ordinary-gate limit, not a reason to modify Unit 01 source.

### Synthetic merge caveat

The PR workflow checkout used a synthetic merge containing source head `a2ab7ca6` on the owned repository's current default branch. The canonical review fence is still the explicit `e6b6b167...a2ab7ca6` source comparison. The synthetic merge is compatibility execution, not the canonical source revision.

## Prior-art and duplicate checklist

- [x] Read merged upstream PR [`vitejs/vite#22188`](https://github.com/vitejs/vite/pull/22188), its diff, comments, and reviews.
- [x] Confirm #22188 added listener-level error reporting and all-event logging tests.
- [x] Confirm inspected public main retains fail-fast inner `Promise.all` before later work.
- [x] Search current Vite issues and pull requests for overlapping continuation work.
- [x] Record Unit 01 as a distinct follow-up.
- [ ] Repeat duplicate search immediately before an authorized public submission.

## Packet consistency checklist

- [x] `README.md` disposition matches the current source and classified workflow state.
- [x] `DEEP_DIVE.md` names the current source head and ownership model.
- [x] `APPROACHES.md` retains losing and rejected options.
- [x] `TESTS.md` separates reproduction, predecessor, current-head passes, and classified failures.
- [x] `UPSTREAM_ISSUE.md` preserves the direct-PR/optional-issue route.
- [x] `UPSTREAM_PR.md` contains a polished public-facing draft and current private validation note.
- [x] `teamleaderleo/vite#4` names the current base, head, tests, limits, and disposition.
- [x] Fieldwork #435 has the final compact handoff: [`comment 5150565424`](https://github.com/teamleaderleo/fieldwork/issues/435#issuecomment-5150565424).
- [x] No material finding remains chat-only.

## Temporary machinery and branch hygiene

- [x] Canonical source diff contains no workflow files.
- [x] Canonical source diff contains no research directory.
- [x] Canonical source diff contains no dependency or lock changes.
- [x] Replay carrier [`teamleaderleo/vite#15`](https://github.com/teamleaderleo/vite/pull/15) is merged and non-canonical.
- [x] Exact-base mirror remains because the packet cites it.
- [ ] Temporary work branch `unit-01/watchchange-rebase-work` remains deletable housekeeping; it is not an active candidate or review surface.

## Human inspection guide

An independent reviewer should:

1. compare public base `e6b6b167` to source head `a2ab7ca6` and verify only two files changed;
2. read the public-base watcher handlers to see the abort point;
3. confirm the helper changes only environment failure aggregation;
4. trace change/add/unlink through later Vite-owned work;
5. read the stale-cache and add/unlink controls;
6. inspect current CI, including the exact Windows failure logs and classification;
7. check the draft for claim inflation and stale receipts;
8. confirm public upstream interaction remains pending explicit authority.

## Current self-review disposition

`ACCEPT`

The exact source candidate is suitable for independent final review. Complete-diff source review found no blocking product-code defect. Current target evidence proves the focused behavior, and ordinary gates pass across Linux and macOS plus the Windows build/unit/focused/ordinary-serve portions. The remaining Windows full-job gap is caused by inspected failures in an existing HMR/SSR integration family and is classified rather than treated as a Unit 01 defect.

The author performed this self-review and is not the sole eligible final accepter. `ACCEPT` here advances the packet to independent review; it does not authorize merge or public submission.

## Clearing conditions for the next transition

For public submission after independent acceptance:

- source head and current Vite main relation must be refreshed;
- duplicate and contribution-policy checks must be repeated;
- any material rebase must rerun focused and ordinary gates;
- the public draft must remove internal receipt language;
- the user must authorize the exact upstream interaction.
