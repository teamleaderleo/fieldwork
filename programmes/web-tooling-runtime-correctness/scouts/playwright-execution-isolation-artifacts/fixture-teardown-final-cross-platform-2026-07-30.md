# Playwright fixture cleanup — final stacked cross-platform gate

Date: 2026-07-30

Fieldwork candidate: #141

Executed source PRs: `teamleaderleo/playwright#24` plus receipt refinement `#26`

Executed source branch: `fieldwork/fixture-teardown-internal-receipt`

Executed source head: `dfdb02284c26a179f8266a2dfe10b4787035d024`

Current repair experiment: `teamleaderleo/playwright#34`

Reviewed Fieldwork issue generation: #141 updated `2026-07-29T23:27:12Z`

Upstream contact authorized: `false`

No upstream contact occurred.

## In simple words

The Playwright fixture-recovery behavior passed the same focused stack on Linux, macOS, and Windows.

Complete-diff self-review then found that the executed branch also contains a temporary public status rewrite from the separate expected-failure result-accounting question.

The cross-platform receipt remains valid for the behavior at the executed head. The head is not a clean #141 landing candidate until lifecycle worker safety is separated from #142 retry and final-outcome semantics.

## Exact source identity

The executed source head is `dfdb02284c26a179f8266a2dfe10b4787035d024`.

The Ubuntu execution carrier PR #27 used that exact head as its base. The later macOS/Windows carrier PR #31 also used that exact head as its base. Both carriers changed only workflow configuration.

Complete-diff comparison against fork `main` revision `beaf223604b5c199b25287cd3c66bb8a9801a30c`:

- 33 commits ahead, zero behind;
- source files:
  - `packages/playwright/src/worker/fixtureRunner.ts` — 152 additions, 13 deletions;
  - `packages/playwright/src/worker/timeoutManager.ts` — 37 additions, 31 deletions;
  - `packages/playwright/src/worker/workerMain.ts` — 17 additions, 5 deletions;
- five focused test files — 567 additions.

The delivery review must inspect this complete fence rather than treating PR #24 or #26 in isolation.

## Exact matrix

| Platform | Workflow run | Job | Result |
| --- | --- | --- | --- |
| Ubuntu 24.04 | `30487474207` | `90696663923` | 11 passed in 22.8s |
| macOS 26.4 arm64 | `30496607480` | `90726802177` | 11 passed in 17.8s |
| Windows Server 2025 | `30496607480` | `90726802254` | 11 passed in 28.8s |

Environment shared by the matrix:

- Node 22;
- Chromium installed through the repository test action;
- one Playwright Test worker;
- exact command stack:

```text
npm run ttest --
  tests/playwright-test/fixture-teardown-resumption.spec.ts
  tests/playwright-test/fixture-teardown-fairness.spec.ts
  tests/playwright-test/fixture-teardown-dependency-safety.spec.ts
  tests/playwright-test/fixture-teardown-cleanup-receipt.spec.ts
  tests/playwright-test/fixture-teardown-afterall-isolation.spec.ts
  --workers=1
```

## What the eleven tests establish

- retention of shared-slot test fixture finalizers that never began;
- bounded allocation among independent dependency groups;
- child-before-parent safety within connected fixture groups;
- no-budget and fairness controls;
- recovery-specific diagnostics;
- `completed` cleanup receipt state;
- `failed-after-start` state;
- `timed-out-after-start` state;
- `not-started-budget-exhausted` state;
- opaque fixture registration identity, human name, and source location;
- receipt phase `deferred-test-fixture-recovery`;
- `_fixture-cleanup` internal attachment naming;
- receipt delivery before `testEnd`;
- failed-test fixture removal before `afterAll` fixture resolution.

## Complete-diff self-review

The recovery scheduler uses one existing full-cleanup slot. The test-fixture recovery phase spends part of that slot before `afterAll`, and later Worker Cleanup reuses the remainder. The candidate does not add one timeout per fixture or a second project-timeout allowance.

Only never-started finalizers are retained. A callback that began and then failed or timed out is not started again.

Connected fixtures share one recovery slot. If a child callback times out and continues running after the timeout race, the exhausted group slot prevents its parent teardown from starting concurrently. Independent groups retain separate bounded shares.

The `timeout: 0` case does not create a hidden zero-budget recovery defect. `calculateMaxTimeout()` treats either zero input as no timeout, so the After Hooks slot cannot become exhausted and create deferred cleanup debt in that configuration.

The receipt is attached during deferred recovery before `afterAll` and before `testEnd`. The source preserves the first cleanup error while recording all deferred fixture states reached by the bounded pass.

## Complete-diff blocker

The executed head still contains this temporary result-accounting workaround:

```ts
if (!testInfo._isFailure())
  testInfo.status = 'timedOut';
```

The associated test requires an expected body failure with cleanup debt to retry in a fresh worker.

That behavior belongs to #142. It changes public result status to force retry and final unexpectedness, while #141 is intended to own fixture recovery, dependency safety, receipt timing, and worker safety only.

The executed head is therefore not a clean landing candidate despite the valid focused platform receipt.

## Repair experiment

PR `teamleaderleo/playwright#34`, workflow run `30499508638`, tests this separation:

- remove the public status rewrite;
- add an internal incomplete-fixture-cleanup flag only when deferred recovery ends `failed-after-start`, `timed-out-after-start`, or `not-started-budget-exhausted`;
- use that flag only to stop the worker and protect later tests;
- expected body failure plus recovered cleanup remains expected and runs once;
- expected body failure plus incomplete cleanup does not retry the current test, but later tests run in a fresh worker;
- update the stale comment that still says retry occurs only in later Worker Cleanup;
- retain the rest of the focused cleanup stack.

The run is queued. No repair result is claimed yet.

## Disposition

Evidence class for executed head: **target-executed, cross-platform focused gate**

Corrected self-review disposition: **REPAIR**

Clearing condition for Delivery Desk D1:

1. PR #34 reaches its intended controls;
2. the repair is applied to a named source head;
3. the focused receipt is rerun or explicitly carried forward through documented semantic identity, with the two new separation controls executed;
4. an eligible exact-head disposition is recorded for the repaired head and current issue generation;
5. the repair carrier is closed after transfer.

This is not a full repository gate and not an upstream submission decision.
