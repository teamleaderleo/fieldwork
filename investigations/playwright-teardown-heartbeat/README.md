# Playwright worker teardown heartbeat watchdog

Tracks Fieldwork issue #654.

## Exact source

- Playwright: `teamleaderleo/playwright@beaf223604b5c199b25287cd3c66bb8a9801a30c`
- heartbeat change: `63ff5dc1b3a379a07da51315ff439dcea3bc479b`
- child path: `packages/playwright/src/common/process.ts`
- parent path: `packages/playwright/src/runner/processHost.ts`

## Question

Can a normal parent-requested worker stop hang indefinitely when fixture teardown never settles but the child event loop remains responsive enough to emit heartbeats?

## Probe design

The hosted workflow injects one runner-only test into Playwright's existing `tests/playwright-test` suite.

### Finite control

- worker teardown sleeps for four seconds;
- `PWTEST_CHILD_PROCESS_TIMEOUT=2000`;
- heartbeat traffic must prevent force kill;
- the run must exit successfully and print the teardown completion marker.

### Stuck discriminator

- worker teardown awaits a Promise that never settles;
- fixture timeout is explicitly zero;
- `PWTEST_CHILD_PROCESS_TIMEOUT=2000`;
- `PWTEST_FORCE_EXIT_TIMEOUT=3000`;
- the normal `__stop__` path does not arm the force-exit timer;
- an outer GNU `timeout` terminates the command after 12 seconds;
- protocol logging must show multiple `__heartbeat__` messages;
- logs must not show the parent force-killed diagnostic before the outer deadline.

## Interpretation

- finite passes; stuck exits 124 with repeated heartbeats: confirmed watchdog suppression;
- finite is force-killed: regression fixture or heartbeat path is not active;
- stuck exits internally before the outer deadline: a separate watchdog exists and the source inference is incomplete;
- stuck emits no heartbeat: event-loop or fixture design issue, not the target case.

No upstream interaction is authorized or made.
