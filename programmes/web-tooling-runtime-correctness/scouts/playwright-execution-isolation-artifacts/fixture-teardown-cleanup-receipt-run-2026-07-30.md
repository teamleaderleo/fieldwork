# Playwright deferred cleanup receipts — 2026-07-30

## Decision

Promote a machine-readable deferred-cleanup receipt as the reporting companion to dependency-group fixture recovery.

The validated scheduler can preserve child-before-root safety by declining to start later callbacks after a group allowance is exhausted. Without a receipt, that safe decision is invisible in the test result.

No upstream contact occurred.

## Negative invariant

| Field | Value |
|---|---|
| Probe PR | `teamleaderleo/playwright#12` |
| Execution PR | `#14` |
| Workflow run | `30481142677` |
| Job | `90675247334` |
| Result | expected failure |

The nested test emitted only:

```text
child-finalizer-started
```

It did not emit `child-finalizer-finished` or `root-closed`, confirming that dependency safety held. The JSON report had no `fixture-cleanup` attachment, and the outer test failed with:

```text
Expected: application/json
Received: undefined
```

The run also reported:

```text
Tearing down "child" exceeded the test timeout of 133ms.
```

The 133ms value was a temporary scheduler allocation from the Worker Cleanup budget, not the user's configured test timeout.

## Receipt intervention

| Field | Value |
|---|---|
| Implementation PR | `teamleaderleo/playwright#15` |
| Execution PR | `#16` |
| Workflow run | `30482672617` |
| Job | `90680468972` |
| Head | `3090cb10aee0d8922b258819a7ad5190ecfd09cb` |
| Result | 9 passed |
| Duration | 19.4 seconds |
| Runner | GitHub-hosted Ubuntu 24.04 / Node 22 / one worker |

Command:

```bash
npm run ttest -- \
  tests/playwright-test/fixture-teardown-resumption.spec.ts \
  tests/playwright-test/fixture-teardown-fairness.spec.ts \
  tests/playwright-test/fixture-teardown-dependency-safety.spec.ts \
  tests/playwright-test/fixture-teardown-cleanup-receipt.spec.ts \
  --workers=1
```

## Receipt contract

The implementation records teardown outcomes for fixtures that were deferred into Worker Cleanup and attaches one versioned JSON document before `testEnd`.

```json
{
  "version": 1,
  "phase": "worker-cleanup",
  "budget": {
    "timeout": 2000,
    "elapsed": 2000
  },
  "fixtures": [
    { "name": "child", "state": "timed-out-after-start" },
    { "name": "root", "state": "not-started-budget-exhausted" }
  ]
}
```

The exact elapsed value is runtime-dependent. The stable contract in this experiment is the version, phase, fixture name, and state.

Current states:

- `completed`
- `timed-out-after-start`
- `failed-after-start`
- `not-started-budget-exhausted`

The initial final-test pass uses an internal `deferred` state but does not expose it in the receipt. The receipt covers the later Worker Cleanup attempt.

## Error preservation

The implementation changes fixture teardown from immediate propagation to outcome capture inside `Fixture.teardown`, but preserves the existing observable error path:

1. `_runWithTimeout` records the original error on `TestInfo`;
2. `_runAsStep` closes the fixture step with that error;
3. `Fixture.teardown` returns the state and original error;
4. `teardownScope` attaches the receipt;
5. `teardownScope` rethrows the same first error;
6. `WorkerMain` reaches `testEnd` with both the original error and receipt.

This ordering is why the receipt is available to live reporters rather than being appended after `testEnd`.

## Regression coverage retained

The nine-test pass includes:

- retention after a peer fixture consumes the original slot;
- retry worker replacement;
- attachments before `testEnd`;
- dependent and independent cleanup ordering;
- `afterEach` exhaustion;
- expected-failure cleanup debt;
- hook isolation;
- independent-group fairness;
- child-before-root dependency safety;
- the new cleanup receipt contract.

## Remaining work

1. Label temporary scheduler slices as fixture recovery allocations rather than test timeouts.
2. Decide whether receipts should be emitted for fully successful deferred recovery or only incomplete recovery.
3. Add receipt cases for `completed` and `failed-after-start`, not only timeout plus unstarted dependency.
4. Decide whether fixture names alone are sufficient when titles or registrations collide.
5. Replace the expected-failure status mutation with a dedicated WorkerMain cleanup-debt signal.
6. Run the receipt stack on macOS and Windows after the schema settles.

## Fork stack

- `#12` — cleanup receipt negative invariant
- `#15` — receipt implementation
- `#16` — nine-test receipt execution harness
- `#17` — recovery-specific wording invariant
- `#18` — recovery wording implementation
- `#19` — wording regression execution harness

All remain draft and fork-only.
