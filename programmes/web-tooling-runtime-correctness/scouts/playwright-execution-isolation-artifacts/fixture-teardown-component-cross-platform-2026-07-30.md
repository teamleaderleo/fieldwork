# Playwright dependency-group scheduler cross-platform matrix — 2026-07-30

## Result

The eight-test dependency-group cleanup scheduler suite passed on Ubuntu, macOS, and Windows under Node 22.

| OS | Runner image | Job | Result | Test duration |
|---|---|---:|---|---:|
| Ubuntu | Ubuntu 24.04 | `90674152906` | 8 passed | 16.1s |
| macOS | macOS 26.4 arm64 | `90674152868` | 8 passed | 14.8s |
| Windows | Windows Server 2025 | `90674153002` | 8 passed | 19.8s |

| Field | Value |
|---|---|
| Repository | `teamleaderleo/playwright` |
| Cross-platform execution PR | `#13` |
| Workflow run | `30480815771` |
| Scheduler | `fieldwork/fixture-teardown-component-budget@8197f236d0911401882eb9b8f624f39f42589324` |
| Node | 22 |
| Workers | 1 |

No upstream contact occurred.

## Passed invariants on every OS

- never-started final-test fixture retention;
- Worker Cleanup retry on attempt 0 and retry 1;
- distinct retry worker indices;
- custom attachments present before `testEnd`;
- dependency and independent fixture cleanup order;
- `afterEach` slot exhaustion;
- expected body failure plus cleanup-debt worker replacement;
- fresh hook-local fixtures across consecutive `afterAll` hooks;
- independent deferred-finalizer fairness;
- unused recovery-budget carry-forward;
- child finalizer completion while root dependency remains open;
- root teardown after child completion.

## Interpretation

The dependency-group intervention is not dependent on one operating system's timer scheduling or process behavior. The tested component accounting and dependency-safe ordering hold across Linux, macOS arm64, and Windows.

This makes the current lead intervention materially stronger than the earlier candidates:

| Candidate | Evidence |
|---|---|
| one shared retry slot | exact negative control: attachments lost before `testEnd` |
| equal per-fixture shares | cross-platform independent fairness pass, exact dependency-safety failure |
| dependency-group weighted shares | eight-test pass on all three operating systems |

## Remaining work

- explicit cleanup receipts for timed-out and unstarted fixtures in an exhausted group;
- distinct diagnostic wording for scheduler allocations;
- cancellation during Worker Cleanup;
- BrowserContext, trace, video, and child-process ownership cases;
- status model for expected body failures followed by cleanup debt;
- broader runner regression suite and performance measurement.
