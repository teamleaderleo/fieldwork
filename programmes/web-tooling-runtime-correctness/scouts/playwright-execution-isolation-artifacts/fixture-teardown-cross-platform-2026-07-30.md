# Playwright fixture teardown cross-platform matrix — 2026-07-30

## Result

The seven-test budgeted-fairness suite passed on Ubuntu, macOS, and Windows under Node 22.

| OS | GitHub runner image | Job | Result | Test duration |
|---|---|---:|---|---:|
| Ubuntu | Ubuntu 24.04 | `90662976399` | 7 passed | 13.6s |
| macOS | macOS 26.4 arm64 | `90662976239` | 7 passed | 15.2s |
| Windows | Windows Server 2025 | `90662976288` | 7 passed | 17.7s |

| Field | Value |
|---|---|
| Repository | `teamleaderleo/playwright` |
| Execution PR | `#7` |
| Workflow run | `30477558791` |
| Prototype | `fieldwork/fixture-teardown-budgeted-fairness@424b81b4352cfaca14f1ded145dab53f1fdf6b82` |
| Node | 22 |
| Workers | 1 |
| Command | targeted `ttest` for resumption and fairness specs |

No upstream contact occurred.

## Passed controls on every OS

- retained fixture teardown after a peer consumes the shared slot;
- retry worker replacement with distinct worker indices;
- sentinel attachments present before `testEnd`;
- retained dependency plus independent fixture teardown;
- `afterEach` exhaustion before fixture cleanup;
- cleanup debt after an expected body failure;
- fresh fixture instances across consecutive `afterAll` hooks;
- one slow deferred fixture followed by a later sentinel;
- one slow deferred fixture followed by two quick finalizers with attachment order preserved.

## Interpretation

The tested mechanism is not an Ubuntu timer accident. The current retention and equal-share budget prototype behaves consistently across:

- Linux process and timer scheduling;
- macOS arm64 scheduling;
- Windows process and timer scheduling;
- platform-specific path and attachment handling.

This raises confidence in the source mechanism and basic budget accounting.

It does **not** establish that equal per-fixture allocation is the correct production policy. A separate dependency-safety probe tests whether an allocated child teardown can time out and continue running while its root dependency begins cleanup.

## Remaining platform work

- run the dependency-group scheduler on all three systems after its Ubuntu control passes;
- inspect timeout wording and stack locations across path formats;
- add browser/context process-survivor checks where custom fixtures own actual browser contexts;
- test abrupt cancellation during the recovery pass.
