# Review — Unit 12 terminal async-response close

## In simple words

The selected contribution prevents HTTPX from claiming successful async response cleanup or blindly repeating arbitrary cleanup after an uncertain failure. The current GitHub source head already handles owner failure, cancellation, observers, traceback retention, and at-most-once cleanup well.

Final review should challenge two corrections captured in the retained patch: same-task re-entry must return promptly without disrupting an unrelated waiter, and successful `elapsed` must keep the pre-cleanup sample while publishing only after cleanup succeeds.

## Review subject

- Work class: `upstream-fork research`
- Target repository: `encode/httpx`
- Proposed upstream base: `master`, currently inspected at `b5addb64f0161ff6bfe94c124ef76f6a1fba5254`
- Canonical source branch: `fieldwork/171-terminal-close-source`
- Exact current source head: `18256f10d1b306bdf87a1bab24b214c15839147b`
- Retained repair patch: [`patches/0001-fix-reentrant-close-and-elapsed-sampling.patch`](./patches/0001-fix-reentrant-close-and-elapsed-sampling.patch)
- Fieldwork packet branch: `upstream/12-httpx-terminal-async-close`
- Exact packet head: use the latest unit-12 handoff on issue #435
- Current changed-file fence: five files
- Proposed repaired fence: six files, adding `tests/models/test_async_response_close_reentry.py`
- Upstream-contact authority: `none`

## Review reading order

1. [`README.md`](./README.md)
2. [`DEEP_DIVE.md`](./DEEP_DIVE.md)
3. [`APPROACHES.md`](./APPROACHES.md)
4. [`TESTS.md`](./TESTS.md)
5. [retained repair patch](./patches/0001-fix-reentrant-close-and-elapsed-sampling.patch)
6. exact current product diff from base to `18256f10...`
7. current tests and proposed repair tests
8. [`UPSTREAM_ISSUE.md`](./UPSTREAM_ISSUE.md)
9. [`UPSTREAM_PR.md`](./UPSTREAM_PR.md)

## Exact diff links

- current complete compare: `https://github.com/teamleaderleo/httpx/compare/b5addb64f0161ff6bfe94c124ef76f6a1fba5254...18256f10d1b306bdf87a1bab24b214c15839147b`
- current production: [`httpx/_models.py`](https://github.com/teamleaderleo/httpx/blob/18256f10d1b306bdf87a1bab24b214c15839147b/httpx/_models.py), [`httpx/_client.py`](https://github.com/teamleaderleo/httpx/blob/18256f10d1b306bdf87a1bab24b214c15839147b/httpx/_client.py)
- current tests: [`terminal unknown`](https://github.com/teamleaderleo/httpx/blob/18256f10d1b306bdf87a1bab24b214c15839147b/tests/models/test_async_response_close_terminal_unknown.py), [`cancellation`](https://github.com/teamleaderleo/httpx/blob/18256f10d1b306bdf87a1bab24b214c15839147b/tests/models/test_async_response_close_terminal_cancellation.py), [`elapsed`](https://github.com/teamleaderleo/httpx/blob/18256f10d1b306bdf87a1bab24b214c15839147b/tests/client/test_async_client_terminal_close_elapsed.py)
- proposed repaired diff: packet patch above
- generated or dependency files: none

## Claims requiring judgment

| Claim or design choice | Evidence | Reviewer question |
| --- | --- | --- |
| escaped arbitrary close should become terminal outcome-unknown | duplicate-effect characterization and existing exact matrix | Is at-most-once cleanup safer than generic retry at this public boundary? |
| initiating caller gets the original exception; observers get neutral errors | focused controls and GC regression | Does this preserve enough diagnostics without retaining arbitrary traceback graphs? |
| `is_closed=False` after failed terminal cleanup | source and tests | Is completion truth worth the unusual state where reads and retries remain blocked? |
| same-task re-entry gets immediate `CloseError` | current timeout failures and repaired local passes | Is task identity the correct narrow provenance boundary, or should descendant contexts also be rejected? |
| external waiter remains attached when stream catches re-entry | repaired local target test | Does the state remain unpoisoned and race-free under both AnyIO backends? |
| elapsed is sampled before cleanup and assigned after success | deterministic current/repaired comparison | Does this preserve the existing measurement contract while fixing failed publication? |
| `BaseException` terminalizes uncertain cleanup | existing cancellation/control-flow tests | Should `KeyboardInterrupt` and `SystemExit` follow the same at-most-once policy? |
| pickling restores an inert closed response | existing pickle tests | Is losing the failed-close distinction across serialization acceptable? |

## Known risks

- `anyio.get_current_task().id` must typecheck and behave consistently across the supported AnyIO range.
- Task-ID detection handles the exact same-task cycle; a child task spawned and awaited by stream cleanup may create a broader provenance cycle.
- `CloseError` for re-entry becomes a new prompt observable behavior.
- Three private state fields plus `is_closed` remain more difficult to reason about than one enum, though the retained repair stays narrow.
- Local repaired execution covered asyncio/Python 3.13 only.
- Current source CI receipts expire once the repair is applied.

## Evidence limits

- No direct repaired GitHub source head.
- No repaired Trio execution.
- No repaired Python 3.9 execution.
- No current-main refresh after `b5addb64...` because public `master` was unchanged at the inspection date; repeat before contact.
- No real transport re-entry or production-prevalence evidence.
- HTTPCore and client-wide shutdown remain separate.

## Staleness check

- Current upstream head checked: `2026-08-01`, `b5addb64f0161ff6bfe94c124ef76f6a1fba5254`
- Candidate base relationship: current source is 16 commits ahead, zero behind
- Relevant source paths changed upstream since execution: `no` at the inspection boundary
- Duplicate/overlap search date: `2026-08-01`
- Open replacement work found: none
- Packet and source PR synchronized: packet records `REPAIR`; source PR needs the final repair comment/front-page synchronization

## Source cleanliness

- [x] No Fieldwork-only files in the current target source diff.
- [x] No temporary workflows or publishers in the current source diff.
- [x] No stale execution artifacts in the current source diff.
- [x] No unrelated formatting or generated churn.
- [x] Required generated or lock changes are absent.
- [x] Current commit-pinned links resolve.
- [ ] Retained repair applied and new exact links recorded.

## Test review

- [x] Existing intended assertions ran at `18256f10...`.
- [x] Setup and product failures are separated.
- [x] Current/repaired local discriminators show opposite outcomes.
- [x] Failure, cancellation, GC, observer, requestless, and elapsed-failure paths are covered.
- [ ] Repair runs under asyncio and Trio.
- [ ] Repair runs under Python 3.9 and 3.13.
- [ ] Complete ordinary gates run at the repaired exact head.
- [ ] Coverage remains 100% after new state and tests.

## Draft review

- [x] Discussion draft avoids prevalence and real-socket claims.
- [x] PR draft describes the retained repair, not the current broken head.
- [x] Target terminology is used.
- [x] Internal workflow language is absent from the public draft body.
- [ ] Current contribution and AI-disclosure policy rechecked at filing time.
- [ ] Public links and current head refreshed before contact.

## Reviewer disposition

`REPAIR`

Reviewed source head: `18256f10d1b306bdf87a1bab24b214c15839147b`  
Reviewed packet generation: current unit-12 packet through the retained repair patch  
Reason: current source has deterministic same-task re-entry deadlocks and successful elapsed semantic drift. The retained patch passes five local discriminators but has no direct target-source or full-gate receipt.  
Clearing condition: apply the patch, run the target matrix and ordinary gates, then obtain independent complete-diff acceptance on the unchanged repaired head.  
Reviewer eligibility: `self-review only`

## Human deep-dive guide

The final human reviewer should focus on:

1. whether terminal outcome-unknown is the right generic public contract;
2. whether task-ID re-entry detection is narrow enough and sufficient;
3. whether `is_closed=False` plus blocked reads/retries is understandable and compatible;
4. whether elapsed sampling preserves the old measurement boundary;
5. whether the work should begin as one Potential Issue discussion before any source PR.

Suggested response:

`Unit 12 looks ready for repair materialization and target execution`  
—or—  
`Unit 12 concern: <specific source, test, compatibility, or discussion-framing issue>`
