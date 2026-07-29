# Playwright fixture recovery diagnostics and receipt state matrix — 2026-07-30

## Decision

The dependency-group recovery prototype now has both a human-facing diagnostic contract and a machine-readable four-state cleanup receipt.

No upstream contact occurred.

## Recovery-specific diagnostic

| Field | Value |
|---|---|
| Negative invariant | `teamleaderleo/playwright#17` |
| Intervention | `#18` |
| Execution PR | `#19` |
| Workflow run | `30483082918` |
| Job | `90681870939` |
| Result | 9 passed |
| Duration | 19.9 seconds |
| Runner | GitHub-hosted Ubuntu 24.04 / Node 22 / one worker |

The temporary fixture slot now carries an internal recovery marker. Timeout formatting uses that marker to produce:

```text
Fixture recovery allocation of <N>ms was exhausted while tearing down "<fixture>".
```

The test requires that wording and rejects:

```text
Tearing down "<fixture>" exceeded the test timeout of <N>ms.
```

The intervention changes no scheduling, receipt states, error class, timeout value, fixture title, or location.

## Four-state receipt matrix

| Field | Value |
|---|---|
| State test PR | `teamleaderleo/playwright#20` |
| Execution PR | `#21` |
| Workflow run | `30483290211` |
| Job | `90682588025` |
| Result | 10 passed |
| Duration | 22.1 seconds |
| Runner | GitHub-hosted Ubuntu 24.04 / Node 22 / one worker |

The new case creates two independent deferred fixtures:

1. `failedFixture` starts teardown and throws `cleanup exploded`;
2. `completedFixture` still receives its recovery opportunity and finishes.

The receipt contains:

```json
[
  { "name": "failedFixture", "state": "failed-after-start" },
  { "name": "completedFixture", "state": "completed" }
]
```

Together with the earlier dependency-group exhaustion case, the prototype receipt states are now:

| State | Meaning |
|---|---|
| `completed` | Teardown callback started and returned successfully. |
| `failed-after-start` | Teardown callback started and threw a non-timeout error. |
| `timed-out-after-start` | Teardown callback started but exceeded its recovery allocation. |
| `not-started-budget-exhausted` | Teardown callback was deliberately not started because its dependency group had no remaining allocation. |

The initial final-test pass uses an internal `deferred` state. That state means Worker Cleanup still owes the callback an attempt; it is not part of the Worker Cleanup receipt.

## What is now validated

- skipped finalizers remain registered for Worker Cleanup;
- independent groups receive bounded opportunities;
- dependencies share one recovery slot and retain child-before-root ordering;
- attachments and cleanup receipts arrive before `testEnd`;
- original cleanup errors remain reported;
- later independent finalizers continue after a cleanup error;
- recovery timeout wording identifies runner policy accurately;
- the four receipt outcomes are distinguishable in JSON;
- the complete ten-test stack passes on Ubuntu/Node 22.

## Remaining design work

1. Decide whether to emit a receipt when every deferred callback completes successfully.
2. Add stable fixture identity beyond `registration.name` for duplicate or overridden fixture names.
3. Decide whether allocation and elapsed timing belong in the stable schema or diagnostic-only fields.
4. Add cancellation and second-interrupt states if Worker Cleanup itself is interrupted.
5. Replace the expected-failure `status = timedOut` experiment with an explicit cleanup-debt signal that still drives retry and worker replacement.
6. Run the settled ten-test receipt stack on macOS and Windows.

## Current fork stack

- `#10` — dependency-group recovery scheduler
- `#12` — missing receipt negative invariant
- `#15` — receipt implementation
- `#17` — misleading timeout wording invariant
- `#18` — recovery wording implementation
- `#20` — four-state receipt test matrix

Execution-only drafts: `#11`, `#13`, `#14`, `#16`, `#19`, and `#21`.

All remain fork-only drafts and are excluded from upstream submission.
