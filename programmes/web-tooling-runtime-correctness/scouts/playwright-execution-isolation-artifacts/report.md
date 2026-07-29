# Playwright cleanup recovery, shutdown ownership, outcome accounting, and artifact receipts

- Assignment: #26
- Programme: #15, `web-tooling-runtime-correctness`
- Target hub: #10, Playwright
- Central review candidates: #141, #142, #149, and #153
- State: `ready-for-synthesis`
- Original target revision: `microsoft/playwright@0b2088e58e398106445c39fd3e5ec4cb85ef8bbb`
- Original package version: `1.63.0-next`
- Execution dates: 2026-07-29 through 2026-07-30
- Upstream contact authorized: `false`

No upstream contact occurred.

## In simple words

Four independent lifecycle problems survived exact execution.

1. **Fixture cleanup:** Playwright can erase a cleanup chore without running it when the shared timer is empty.
2. **Expected failures:** A test saying “I am expected to fail” can accidentally excuse a separate cleanup failure.
3. **Python shutdown:** A cancelled caller can leave an “already stopping” sign behind, causing the next caller to leave before cleanup finishes.
4. **MCP video receipts:** One video can reach disk, a second can fail, and the tool can report only the failure while forgetting the completed file.

These touch different owners and should not become one patch.

## Evidence vocabulary

- **Executed target reproduction** — the exact target test ran in an owned fork with retained workflow evidence.
- **Source-confirmed** — pinned implementation and repository history directly support the mechanism.
- **Prepared target test** — a focused test exists but has no retained execution result.
- **Probe-reproduced model** — a controlled model demonstrates part of the mechanism without executing the exact target path.
- **Candidate contract** — a desired invariant proposed for review; current code is not assumed to promise it.

## Candidate index

| Candidate | Boundary | Evidence | Review decision |
| --- | --- | --- | --- |
| #141 | test fixture registry, timeout slots, `afterAll`, reporter completion | executed runner controls and three-platform scheduler | accept, revise, execute final combined platform stack, or hold |
| #142 | expected body status, cleanup errors, retries, final outcome | executed negative runner test | accept as distinct result-model work, revise, or hold |
| #149 | Python async context manager, transport stop, connection cleanup | executed Python 3.10 and 3.14 regression | accept, revise, or hold for shutdown-state design |
| #153 | MCP multi-page video finalization and tool receipt | executed Ubuntu/Node 20/Chrome regression | accept, revise, or hold for per-recording result design |

## #141 — bounded test-fixture recovery

### Confirmed mechanism

A test-scoped fixture without its own timeout shares the After Hooks slot.

When that slot is exhausted before teardown begins, Playwright skips the fixture body but still removes dependency usage and deletes the instance from the registry. Later cleanup cannot find it.

Potential consequences include omitted custom finalizers, BrowserContext closure, service shutdown, artifact finalization, and attachments that never reach the result.

### Causal controls

| Experiment | Result | Decision |
| --- | --- | --- |
| retain never-started fixtures | later finalizer becomes reachable | retention is necessary |
| one shared fallback slot | first slow callback starves later finalizers | rejected |
| equal per-fixture shares | independent finalizers progress | useful but incomplete |
| dependency safety control | timed-out child continues while parent closes | equal shares rejected |
| connected dependency-group shares | parent does not begin while child remains active | scheduler retained |
| retry only in later Worker Cleanup | `afterAll` reuses the retained fixture | late placement rejected |
| same bounded slot before `afterAll` | fresh hook fixture restored | current lead placement |

### Three-platform scheduler result

Eight tests passed with Node 22 and one worker:

- Ubuntu 24.04: 16.1s;
- macOS 26.4 arm64: 14.8s;
- Windows Server 2025: 19.8s.

### Rejected late placement

Owned execution PR `teamleaderleo/playwright#23`, run `30485904509`, job `90691366536`, observed:

```text
resource-setup-1
test-resource-1
afterAll-resource-1
afterAll-saw-test-resource-closed-false
resource-teardown-1
```

`afterAll` reused the failed test's live fixture before teardown.

### Corrected placement

Owned source and execution PRs `teamleaderleo/playwright#24/#25`, run `30486881047`, job `90694673635`:

- 11 campaign tests passed in 22.9s;
- the repository's existing fresh-`afterAll` fixture regression passed in 4.5s;
- source change: 17 additions and 5 deletions in `workerMain.ts`;
- the same cleanup slot is reused rather than adding another deadline.

### Internal receipt

Owned source and execution PRs `teamleaderleo/playwright#26/#27`, run `30487474207`, job `90696663923`:

- 11 tests passed in 22.8s;
- attachment `_fixture-cleanup`;
- phase `deferred-test-fixture-recovery`;
- opaque registration id, human name, source location, and budget;
- states `completed`, `failed-after-start`, `timed-out-after-start`, and `not-started-budget-exhausted`.

### Lead invariant

> Retain only never-started shared-slot test fixture finalizers, recover them by connected dependency group within one existing cleanup budget before `afterAll`, reuse the remainder for worker cleanup, and emit an internal receipt before `testEnd`.

This is bounded recovery, not a guarantee that every stalled callback completes. Cleanup needing an independent allowance should continue to use an explicit fixture timeout.

## #142 — cleanup failure after an expected body failure

Owned PRs `teamleaderleo/playwright#28/#29`, run `30487755057`, job `90697590797`, combined:

- `test.fail()`;
- an expected body failure;
- fixture cleanup throwing `cleanup exploded`;
- one configured retry.

Observed:

```text
cleanup-0-worker-0
1 passed
```

Only attempt zero ran. No fresh worker appeared. The nested exit code was zero.

The dispatcher and final outcome compare public `status` with `expectedStatus`. A worker-stop bit can replace a contaminated process but cannot by itself make the result retryable or unexpected.

Candidate #142 asks for a separate internal unexpected-cleanup dimension reaching:

- worker replacement;
- retry selection;
- retained errors;
- final outcome.

No implementation is selected. Public status mutation solely to force retry is out of scope.

## #149 — Python async stop cancellation

Owned PRs `teamleaderleo/playwright-python#1/#2`, run `30492906544`, assembled the repository driver and ran the focused regression on Ubuntu 24.04:

| Python | Job | Result |
| --- | --- | --- |
| 3.10 | `90714870057` | intended assertion failure |
| 3.14 | `90714870025` | intended assertion failure |

Both versions observed:

```text
await playwright.stop()
assert manager._connection._closed_error is not None
E assert None is not None
```

`PlaywrightContextManager.__aexit__` sets `_exit_was_called` before awaiting asynchronous shutdown. Cancellation leaves the guard set. After transport shutdown completes, a later `stop()` returns without completing connection cleanup.

Candidate #149 requires shutdown to remain joinable or resumable while preserving:

- one authoritative cleanup operation;
- caller cancellation;
- idempotent repeated stop;
- original errors for later callers;
- direct stop and context-manager exit behavior.

No repair is selected.

## #153 — MCP partial video finalization receipt

Owned PRs `teamleaderleo/playwright-mcp#1/#2`, final run `30493907347`, job `90718154318`, used Ubuntu 24.04, Node 20, Chrome, and one worker.

Scenario:

1. create an initial page;
2. start recording to `video.webm`;
3. create a directory at the derived second-page destination `video-1.webm`;
4. open a second page;
5. stop recording.

The second page records to an internal temporary file. Its destination fails during final copy, not screencast startup.

Before the final receipt assertion, the test proved:

- `video.webm` exists;
- it is a regular file;
- it contains non-zero bytes.

The second copy failed with `EISDIR`. The stop response contained only that error and omitted the completed `video.webm` path.

Supported conclusion:

> `browser_stop_video` can collapse partial finalization into an all-error response, making a completed recording undiscoverable through the tool receipt.

This does not claim the file was deleted. The file exists; the receipt is incomplete.

Candidate #153 asks for per-recording outcomes:

- completed paths remain discoverable;
- failed finalizations retain individual errors;
- one failure does not erase earlier successes;
- the overall call may still signal partial failure;
- repeated stop does not duplicate completed files.

The earlier failed-start hypothesis was rejected. Run `30493430429` was a harness miss. Run `30493678395` located the failure at final copy. Only run `30493907347` supports the candidate.

## Repository intentions and anti-patterns

Durable repository-history review: `fixture-teardown-repository-intent-review-2026-07-30.md`.

Avoid:

- unbounded cleanup extension;
- full project timeout per fixture;
- independent timeout races across dependencies;
- retrying failed-test fixtures only after `afterAll`;
- process-exit stdout as reporter evidence;
- ordinary visible attachments for internal scheduling data;
- public status mutation solely to force retries;
- one-way shutdown guards that cannot distinguish started from completed;
- duplicate concurrent shutdown operations;
- all-error aggregation that erases completed artifacts;
- deleting completed artifacts to regain apparent atomicity;
- combining all four candidates into one patch.

## Lower-confidence retained findings

### Crash-resilient blob reporting

**Evidence:** source-confirmed candidate plus prepared exact runner test.

Blob events are accumulated in memory and the durable ZIP is created during `onEnd`. A hard exit before or during that phase can leave no replayable blob. The next useful evidence is a deterministic phase-interruption matrix.

### Worker heartbeat hard kill

**Evidence:** bounded open probe with counterevidence.

A library-level SIGKILL probe found no surviving observed driver or Chromium processes. The exact Playwright Test heartbeat-loss path remains worth one bounded process-tree probe, but no defect is claimed.

### Playwright CLI video behavior

**Evidence:** source-related prepared test.

The CLI has a related recording flow, but it has not been re-executed against the corrected partial-finalization scenario. Do not generalize #153 to the CLI without a separate run.

## Review packets

### #141

Verify skip-and-delete, starvation and dependency controls, same-budget pre-`afterAll` recovery, receipt timing, and the final combined macOS/Windows decision.

### #142

Verify body and cleanup failures are independent and trace the smallest signal through reporter, serial-suite, max-failure, retry, and final-outcome paths.

### #149

Compare shared shutdown task, explicit state machine, and resumable cleanup designs. Require concurrency, error, platform, and Python-version controls.

### #153

Confirm completed-file assertions precede the receipt failure. Compare fail-fast aggregation with all-settled per-recording results. Require all-success, mixed-success, repeated-stop, and platform controls.

## Durable evidence index

- `fixture-teardown-deep-dive-2026-07-30.md`
- `fixture-teardown-component-cross-platform-2026-07-30.md`
- `fixture-teardown-cleanup-receipt-run-2026-07-30.md`
- `fixture-teardown-recovery-diagnostics-state-matrix-2026-07-30.md`
- `fixture-teardown-repository-intent-review-2026-07-30.md`
- `fixture-teardown-repository-alignment-run-2026-07-30.md`
- `python-async-stop-cancellation-run-2026-07-30.md`
- `mcp-partial-video-finalization-run-2026-07-30.md`
- `follow-up-2026-07-30.md`
- retained probes under `probe/`

## Handoff

- Parent scout: #26
- Fixture recovery: #141
- Outcome accounting: #142
- Python shutdown ownership: #149
- MCP video receipt: #153
- Fieldwork review PR: #49
- Upstream contact: unauthorized

No upstream contact occurred.
