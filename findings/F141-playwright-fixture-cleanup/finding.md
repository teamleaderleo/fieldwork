# F141: Separate Playwright fixture-cleanup safety from result accounting

Finding state: `review-ready`

Workstream: `B — Browser, web tooling, and runtime boundaries`  
Canonical Fieldwork issue: `#141`  
Canonical finding path: `findings/F141-playwright-fixture-cleanup/finding.md`  
Canonical implementation: `teamleaderleo/playwright#35`  
Exact implementation head: `14bb90c8881576f8d39137e4fd0a6c12c21d25e6`  
Exact base revision: `dfdb02284c26a179f8266a2dfe10b4787035d024`  
Strongest evidence class: `target-executed` focused gate  
Current review disposition: `ACCEPT for #141 worker-safety scope`  
Desk routing: `Review Queue #213; Delivery Desk #160 D1 after acceptance synchronization`  
Upstream contact authorized: `no`

## In simple words

A Playwright test can run out of cleanup time while tearing down a fixture. The recovery work needs to protect the next test from inheriting a dirty worker.

An earlier candidate also changed whether the current test counted as failed or retried. That mixed two separate questions. The clean candidate now does one job: when cleanup remains incomplete, retire the worker before another test uses it. A different finding owns retry and final-result policy.

## Why we care

A worker can retain partially cleaned test state after timeout or cleanup failure. Reusing that worker risks cross-test contamination, misleading results, and cascading failures. At the same time, changing public result status merely to force worker replacement can distort expected-failure semantics and create retries for the wrong reason.

The selected split protects lifecycle safety while keeping result accounting independently reviewable.

## What happens if we leave it alone

Without bounded recovery, a timed-out fixture finalizer may never run and the next test can inherit live state. With the older mixed candidate, an expected body failure could be rewritten to `timedOut`, forcing a retry and changing public outcome semantics even when deferred cleanup later completed.

Frequency across real suites remains unmeasured. The focused tests establish the mechanism and the candidate behavior.

## Current finding

Playwright should record incomplete deferred fixture cleanup as an internal worker-safety signal. It should stop the worker before later tests when recovery finishes failed, timed out, or unable to start. It should avoid rewriting public test status inside this finding.

### Claim table

| Claim | Evidence class | Exact support | Limit |
| --- | --- | --- | --- |
| Deferred cleanup can require worker replacement after an expected body failure. | `target-executed` | Workflow `30579698560`, job `90996585965`; PR #35 tests | Ubuntu 24.04, Node 22, Chromium, one worker |
| Recovered deferred cleanup can remain an expected result without retry. | `target-executed` | Same focused run and `fixture-teardown-resumption.spec.ts` | Focused runner matrix, not full repository gate |
| The final candidate contains only four product/test files. | `source-read` | PR #35 at exact head | Does not establish broad compatibility |
| Retry and final-result semantics remain a separate question. | `source-read` and scope decision | Fieldwork #142 boundary and removed status rewrite | #142 still needs its own acceptance |

## System and ownership map

- `fixtureRunner.ts` owns fixture teardown, deferred recovery outcomes, receipts, and the incomplete-cleanup signal.
- `testInfo.ts` stores the internal signal for the current test execution.
- `workerMain.ts` owns whether the worker stops before later tests.
- The dispatcher and result model own retry and final outcome; those remain outside #141.
- `fixture-teardown-resumption.spec.ts` covers recovered cleanup and incomplete-cleanup worker replacement.

## Historical precedent

### Playwright worker teardown containment

- Source: https://github.com/microsoft/playwright/pull/42010
- Revision or date: merged before the pinned July 2026 source
- Principle supported: worker termination must respect teardown ownership and avoid unsafe lifecycle shortcuts.
- Important difference: that change addresses force-killing a worker during teardown. This finding addresses what to do after fixture cleanup debt remains and how to keep that safety signal separate from result policy.

### Existing pre-`afterAll` fixture invariant

- Source: the retained Playwright fixture tests and Fieldwork PRs #22–#26
- Principle supported: test fixtures must be recovered or isolated before `afterAll` can reuse their state.
- Important difference: the current finding removes a later result-status coupling discovered during complete-diff review.

## Approaches considered

### Retained approach: internal incomplete-cleanup signal

The signal reflects the actual lifecycle fact: cleanup remained incomplete. `WorkerMain` uses it to retire the worker. Public result classification stays unchanged.

### Declined: rewrite `status` to `timedOut`

This forced retry by changing a user-visible outcome field. It coupled worker hygiene to expected-failure policy and made #141 own behavior assigned to #142.

### Declined: always retry any expected failure with cleanup activity

Recovered cleanup can complete safely. Retrying every such test adds cost and changes semantics without an incomplete-cleanup condition.

### Deferred: separate unexpected-cleanup result dimension

A distinct internal or serialized result marker may be the right design for #142. It affects retry selection, final outcome, reporters, serial suites, and max-failure behavior, so it remains a separate finding.

## Edge cases covered

| Edge case or control | Evidence | Result |
| --- | --- | --- |
| Expected body failure; deferred cleanup later completes | Focused PR #35 test | One attempt; expected result preserved |
| Expected body failure; deferred cleanup remains incomplete | Focused PR #35 test | Current test does not retry; later test runs in fresh worker |
| Dependency-group teardown ordering | Existing focused stack | Child-before-parent safety retained |
| Independent cleanup fairness | Existing focused stack | Independent groups retain bounded shares |
| Cleanup receipt states and identity | Existing focused stack | Receipt behavior remains green |
| Fixture recovery before `afterAll` | Existing focused stack | Isolation invariant remains green |

## Edge cases deferred or outside scope

| Edge case | Why deferred | Owning next record or reopening trigger |
| --- | --- | --- |
| Whether cleanup errors should make an expected body failure unexpected | Result policy, reporter, and retry question | Fieldwork #142 |
| Serial-suite retry and max-failure accounting | Dispatcher-wide consequence | Fieldwork #142 |
| Full repository and all-browser compatibility | Focused candidate gate only | Delivery D1 gate before land-ready |
| Production frequency and suite impact | No usage measurement | Reopen with telemetry or real-suite evidence |
| Cleanup requiring a dedicated allowance | Existing explicit fixture timeout is the supported control | Separate ergonomics finding if evidence appears |

## Exact execution and receipts

| Repository/head | Command or workflow | Platform/environment | Result | Evidence class |
| --- | --- | --- | --- | --- |
| `teamleaderleo/playwright@14bb90c8881576f8d39137e4fd0a6c12c21d25e6` | Publication from tested patch; focused source run inherited from workflow `30579698560`, job `90996585965` | Ubuntu 24.04, Node 22, Chromium, one worker | Focused cleanup matrix passed | `target-executed` |

A later publication workflow failed after the source commit already removed the patch carrier. It executed no candidate test and is classified as a duplicate carrier failure.

## Complete-diff and compatibility review

Changed-file fence:

- `packages/playwright/src/worker/fixtureRunner.ts`
- `packages/playwright/src/worker/testInfo.ts`
- `packages/playwright/src/worker/workerMain.ts`
- `tests/playwright-test/fixture-teardown-resumption.spec.ts`

Temporary workflows and experiment files are absent from the exact head. Complete-diff review accepted the candidate for the bounded #141 worker-safety transition. The remaining routine gate is broader repository execution and final delivery synchronization.

## Current disposition and desk routing

- Finding state: `review-ready`
- Review disposition: `ACCEPT for the stated worker-safety scope`
- Review Queue entry: #213
- Delivery lane: `D1` once the accepted finding is linked as the canonical record
- Exact next transition: run the named broader repository gate at the exact candidate head and retain the receipt
- Clearing condition: exact-head broader gate plus current-base review
- User decision requested: none for the #141 invariant; examination and acceptance of the bounded candidate remain available

## Changes to the canonical conclusion

| Date | Pull request or commit | Change in conclusion |
| --- | --- | --- |
| 2026-07-30 | Playwright PR #26 | Recovery behavior passed cross-platform focused tests, but still included a public status rewrite |
| 2026-07-30 | Playwright PR #34 | Focused experiment proved worker safety can be separated from result accounting |
| 2026-07-30 | Playwright PR #35 / `14bb90c...` | Clean four-file source candidate published and exact-head review accepted |

## References

- https://github.com/teamleaderleo/fieldwork/issues/141
- https://github.com/teamleaderleo/playwright/pull/35
- https://github.com/teamleaderleo/playwright/pull/34
- https://github.com/teamleaderleo/playwright/pull/26
- https://github.com/microsoft/playwright/pull/42010
- Workflow `30579698560`, job `90996585965`
