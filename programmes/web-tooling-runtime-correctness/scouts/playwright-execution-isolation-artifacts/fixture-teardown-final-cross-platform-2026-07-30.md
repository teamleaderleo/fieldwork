# Playwright fixture cleanup — final stacked cross-platform gate

Date: 2026-07-30

Fieldwork candidate: #141

Canonical source PRs: `teamleaderleo/playwright#24` plus receipt refinement `#26`

Canonical source branch: `fieldwork/fixture-teardown-internal-receipt`

Canonical source head: `dfdb02284c26a179f8266a2dfe10b4787035d024`

Upstream contact authorized: `false`

No upstream contact occurred.

## In simple words

The final Playwright cleanup candidate has now run on Linux, macOS, and Windows.

All three platforms passed the same eleven tests against the same source head. The stack combines bounded dependency-group fixture recovery before `afterAll` with the internal `_fixture-cleanup` receipt.

This completes the named cross-platform execution gate. It does not provide the independent exact-head acceptance required for delivery.

## Exact source identity

The canonical source head is `dfdb02284c26a179f8266a2dfe10b4787035d024`.

The Ubuntu execution carrier PR #27 used that exact head as its base. The later macOS/Windows carrier PR #31 also used that exact head as its base. Both carriers changed only workflow configuration.

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

## What the eleven tests cover

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

## Self-review

The final source stack still uses one existing full-cleanup slot. The test-fixture recovery phase spends part of that slot before `afterAll`, and later Worker Cleanup reuses the remainder. The candidate does not add one timeout per fixture or a second project-timeout allowance.

Only never-started finalizers are retained. A callback that began and then failed or timed out is not started again.

The expected-failure result-accounting question remains separate under #142. Passing this matrix does not resolve retry or final outcome when an expected body failure coexists with an independent cleanup error.

## Disposition

Evidence class: **target-executed, cross-platform focused gate**

Self-review disposition: **execution gate complete; independent exact-head disposition still required**

Clearing condition for Delivery Desk D1:

1. transfer this receipt to canonical PRs #24 and #26;
2. close execution carrier PR #31;
3. obtain an eligible complete-diff review of canonical exact head `dfdb02284c26a179f8266a2dfe10b4787035d024` and the current issue invariant.

This is not a full repository gate and not an upstream submission decision.
