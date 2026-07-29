# Playwright cleanup recovery, shutdown ownership, outcome accounting, and artifacts

- Assignment: #26
- Programme: #15, `web-tooling-runtime-correctness`
- Target hub: #10, Playwright
- Central review candidates: #141, #142, and #149
- Worker: `chatgpt:gpt-5.6-thinking`
- State: `ready-for-synthesis`
- Original target revision: `microsoft/playwright@0b2088e58e398106445c39fd3e5ec4cb85ef8bbb`
- Original target package version: `1.63.0-next`
- Exact executed revisions: retained by the owned-fork pull requests and workflow runs named below
- Retrieval and execution dates: 2026-07-29 through 2026-07-30
- Upstream contact authorized: `false`

## In simple words

Three reviewable questions survived the scout.

First, Playwright is a robot with a cleanup checklist. When the shared cleanup timer is already empty, it can erase a fixture cleanup without running it. The current recovery candidate keeps only never-started chores, gives related chores one bounded turn before `afterAll` enters, and writes a private receipt describing what happened.

Second, a test marked with `test.fail()` can absorb an unrelated cleanup exception because both use the public `failed` status. The run can then be counted as expected without retrying.

Third, Python async shutdown is like locking a shop. If the first caller starts shutdown and gets cancelled, a later caller can see an “already started” guard and return even though connection cleanup did not finish.

These are different ownership boundaries and should not be combined into one patch.

## Review decisions

### Candidate #141 — bounded fixture recovery

Review whether Playwright should retain never-started shared-slot fixture finalizers, recover them by dependency group within one existing cleanup budget before `afterAll`, reuse the remaining budget for worker cleanup, and emit an internal receipt before `testEnd`.

### Candidate #142 — unexpected cleanup failure after `test.fail()`

Review how an independent cleanup, hook, fixture, or runner failure should reach worker replacement, retry selection, and final outcome without casually changing the public status model.

### Candidate #149 — Python async stop cancellation

Review how asynchronous shutdown should remain joinable or resumable after caller cancellation while preserving one authoritative cleanup operation, idempotency, cancellation, and original errors.

## Evidence vocabulary

- **Executed target reproduction** — the exact target test ran in an owned fork with retained workflow evidence.
- **Source-confirmed** — pinned implementation and repository history directly support the mechanism.
- **Prepared target test** — a focused test exists but has no retained execution result.
- **Probe-reproduced model** — a controlled model demonstrates part of the mechanism without executing the exact target path.
- **Candidate contract** — a desired invariant is proposed; current code is not assumed to promise it.

The report does not upgrade prepared tests or source analysis into executed defects.

## Ownership map

| Owner | Responsibility | Lifetime | Completion boundary |
| --- | --- | --- | --- |
| Runner and dispatcher | scheduling, retries, final outcome, reporter dispatch | invocation or phase | worker result and `testEnd` |
| `WorkerMain` | hooks, fixture runner, active test, worker shutdown | worker process | After Hooks, `afterAll`, Worker Cleanup |
| Fixture runner | fixture graph, instances, setup and teardown order | test or worker scope | shared slot or custom fixture slot |
| Browser/context fixtures | browser process, contexts, pages, video source | worker or attempt | fixture teardown and context close |
| Artifact recorders | screenshot, trace, video, error context | attempt | context closure, packaging, attachment dispatch |
| Reporters | result events and durable reports | invocation | `onEnd` and `onExit` |
| Python async context manager | driver connection start and stop ownership | context-manager lifetime | transport stop plus connection cleanup |

## Candidate #141 — fixture cleanup recovery

### Confirmed mechanism

A test-scoped fixture without its own timeout uses the runnable's shared After Hooks slot.

When that slot is already exhausted before teardown begins, the fixture body is skipped. Cleanup still removes dependency usage and deletes the fixture from `instanceForId`. The later cleanup pass cannot find the fixture and cannot give its finalizer another bounded opportunity.

Potential consequences include omitted custom finalizers, BrowserContext closure, local service shutdown, artifact finalization, and attachments that never reach the result.

### Causal experiment stack

| Step | Experiment | Result | Decision |
| --- | --- | --- | --- |
| 1 | Retain never-started fixtures | Later finalizer becomes reachable | Retention is necessary |
| 2 | One shared fallback slot | First slow callback consumes it; later receipt is absent before `testEnd` | One shared slot rejected |
| 3 | Equal per-fixture shares | Independent finalizers progress | Useful fairness property |
| 4 | Dependency safety control | Timed-out child keeps running while parent closes | Equal shares rejected |
| 5 | Connected dependency-group shares | Parent does not begin while child remains active | Scheduler retained |
| 6 | Retry only in later Worker Cleanup | `afterAll` reuses the retained fixture | Late placement rejected |
| 7 | Spend the same slot before `afterAll` | Fresh hook fixture restored | Current lead placement |
| 8 | Internal receipt convention | Four states, stable identity, and source location retained | Reporting refinement retained |

### Dependency-group scheduler

Connected fixtures share one recovery slot, preserving teardown order. Independent groups receive bounded shares weighted by fixture count. Unused reservation returns to the remaining pool.

Eight exact runner tests passed with Node 22 and one worker:

| Platform | Result |
| --- | --- |
| Ubuntu 24.04 | 8 passed in 16.1s |
| macOS 26.4 arm64 | 8 passed in 14.8s |
| Windows Server 2025 | 8 passed in 19.8s |

This validates the scheduler cases across the three platform families. The final combined pre-`afterAll` ordering and internal-receipt stack still needs a macOS/Windows decision.

### Rejected late placement

Owned probe PR `teamleaderleo/playwright#22` and execution PR `#23` tested retry only in later Worker Cleanup.

Workflow run `30485904509`, job `90691366536`, observed:

```text
resource-setup-1
test-resource-1
afterAll-resource-1
afterAll-saw-test-resource-closed-false
resource-teardown-1
```

`afterAll` received the failed test's still-live fixture. A fresh second fixture was never created.

### Corrected pre-`afterAll` placement

Owned source PR `teamleaderleo/playwright#24` spends one existing full-cleanup slot before `afterAll` when cleanup debt exists, then reuses the same slot during later Worker Cleanup. It does not add another deadline.

Execution PR `teamleaderleo/playwright#25`, workflow run `30486881047`, job `90694673635`:

```text
11 passed (22.9s)
```

The repository's existing fresh-`afterAll` fixture regression passed separately:

```text
1 passed (4.5s)
```

The source diff is limited to `workerMain.ts`: 17 additions and 5 deletions. It moves recovery without changing the dependency-group algorithm.

### Internal cleanup receipt

The tested receipt records:

- `completed`
- `failed-after-start`
- `timed-out-after-start`
- `not-started-budget-exhausted`

Owned source PR `teamleaderleo/playwright#26` uses:

- attachment `_fixture-cleanup`;
- phase `deferred-test-fixture-recovery`;
- opaque registration id;
- human fixture name;
- source location;
- recovery budget fields;
- one cleanup state.

Execution PR `teamleaderleo/playwright#27`, workflow run `30487474207`, job `90696663923`, passed eleven tests in 22.8 seconds on Ubuntu 24.04, Node 22, and one worker.

The receipt arrives before `testEnd`. Late process output cannot repair an already-delivered result.

### Current lead invariant

> When a shared-slot test fixture finalizer has not started because the normal slot is exhausted, retain only that fixture instance, recover retained fixtures by connected dependency group within one existing cleanup budget before `afterAll`, reuse the remaining budget for worker cleanup, and emit an internal receipt before `testEnd`.

The promise is narrow:

- bounded recovery opportunity;
- dependency order preserved;
- no failed-test fixture crossing into `afterAll`;
- incomplete cleanup made explicit;
- no indefinite wait;
- no full extra timeout for every fixture.

Critical cleanup that needs an independent allowance should continue to use an explicit fixture timeout.

## Candidate #142 — expected-failure outcome accounting

Owned probe PR `teamleaderleo/playwright#28` combines:

- a body marked with `test.fail()`;
- an expected body failure;
- a fixture teardown that throws `cleanup exploded`;
- one configured retry.

Execution PR `teamleaderleo/playwright#29`, workflow run `30487755057`, job `90697590797`, printed:

```text
cleanup-0-worker-0
1 passed
```

Only attempt zero ran. No fresh worker appeared. The nested exit code was zero.

The dispatcher and final outcome compare public `status` with `expectedStatus`. A worker-stop flag can protect future tests but cannot make this result retryable or unexpected.

Candidate #142 asks for a separate internal unexpected-cleanup dimension that reaches:

- worker replacement;
- retry selection;
- retained errors;
- final outcome.

No implementation is selected. Rewriting public status strings solely to force retry is out of scope.

## Candidate #149 — Python async stop cancellation

### Confirmed mechanism

`PlaywrightContextManager.__aexit__` sets `_exit_was_called` before awaiting asynchronous transport shutdown.

The owned test blocks `wait_until_stopped()`, cancels the first `playwright.stop()`, lets transport shutdown finish, then retries `stop()` and requires connection cleanup to set `_closed_error`.

Execution PR `teamleaderleo/playwright-python#2`, workflow run `30492906544`, assembled the repository driver and ran the test on Ubuntu 24.04:

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

The second stop returned through the already-set exit guard even though connection cleanup remained incomplete.

Durable detail is in `python-async-stop-cancellation-run-2026-07-30.md`.

### Proposed invariant

Async Playwright shutdown must remain joinable and retryable after caller cancellation.

A later caller should await the one authoritative shutdown operation or safely resume incomplete cleanup. It must not return merely because an earlier cancelled caller set an entry guard.

### Design constraints

- preserve caller cancellation;
- avoid duplicate concurrent transport shutdown;
- do not mark shutdown complete before connection cleanup;
- keep repeated successful stop idempotent;
- preserve the original shutdown error for later callers;
- cover direct stop and async context-manager exit.

### Required regression matrix

- two concurrent stop callers;
- cancellation before transport stop;
- cancellation after transport stop but before connection cleanup;
- transport failure;
- connection cleanup failure;
- repeated successful stop;
- Linux, macOS, and Windows;
- oldest and newest supported Python versions.

No repair has been implemented or selected.

## Repository precedent and intentions

The history review found these constraints:

- timeout bounds are deliberate;
- custom-timeout fixtures own independent slots;
- attempted teardown must not be repeated merely because it failed;
- test fixtures should be gone before `afterAll` resolves its own fixtures;
- worker fixtures remain after `afterAll`;
- runner changes need focused hermetic tests on Linux, macOS, and Windows;
- prospective changes should remain small, issue-led, and reviewed before upstream work.

Durable detail is in `fixture-teardown-repository-intent-review-2026-07-30.md`.

## Anti-patterns rejected

- unbounded teardown extension;
- multiplying project timeout by fixture count;
- independent timeout races across dependencies;
- retrying callbacks that already began and failed;
- retaining every fixture rather than only never-started finalizers;
- retrying retained test fixtures only after `afterAll`;
- process-exit stdout as reporter evidence;
- ordinary visible attachments for internal scheduling data;
- fixture name as the only receipt identity;
- public status mutation solely to force retries;
- a one-way shutdown guard that cannot distinguish started from completed;
- duplicate concurrent shutdown operations;
- combining scheduler, receipt, outcome accounting, and Python shutdown changes.

## Other retained findings

### Playwright MCP and CLI video receipts

**Evidence class:** source-confirmed mechanism plus prepared target tests.

The video flow can record a derived filename before screencast startup succeeds. Page-created startup failures are suppressed, so a stop response can advertise a recording whose screencast never started.

Owned fork tests exist in `teamleaderleo/playwright-mcp#1` and `teamleaderleo/playwright-cli#1`. They still need exact execution before promotion.

### Crash-resilient blob reporting

**Evidence class:** source-confirmed candidate.

Blob report events are accumulated in memory and the durable ZIP is created during `onEnd`. A hard exit before or during `onEnd` can leave no replayable blob even when attempt artifacts exist.

A journal prototype exists, but the next useful evidence is a deterministic phase-interruption matrix rather than another implementation variant.

### Worker heartbeat hard kill

**Evidence class:** bounded open probe with counterevidence.

A library-level SIGKILL probe found no surviving observed Playwright driver or Chromium processes. The exact Playwright Test heartbeat-loss path remains worth one bounded process-tree probe, but no defect is claimed.

## Review packets

### #141

Verify skip-and-delete, no-budget starvation, equal-share dependency races, connected-component safety, `afterAll` ordering, same-budget correction, receipt timing, and final cross-platform need.

Disposition: **accept**, **revise**, **execute**, **hold**, or **reject/stop**.

### #142

Verify body and cleanup failures are independent, only attempt zero runs despite one retry, and trace the smallest internal signal through reporter, serial-suite, max-failure, retry, and final-outcome paths.

Disposition: **accept as separate candidate**, **revise**, or **hold for result-model design**.

### #149

Verify the two-version cancellation reproduction, compare shared shutdown task, explicit state machine, and reset-on-cancellation designs, and require the concurrency/error/platform matrix before implementation promotion.

Disposition: **accept**, **revise**, or **hold for shutdown-state design**.

## Durable evidence index

- `fixture-teardown-deep-dive-2026-07-30.md`
- `fixture-teardown-negative-control-2026-07-30.md`
- `fixture-teardown-dependency-safety-run-1-2026-07-30.md`
- `fixture-teardown-dependency-safety-run-2-2026-07-30.md`
- `fixture-teardown-component-budget-2026-07-30.md`
- `fixture-teardown-component-cross-platform-2026-07-30.md`
- `fixture-teardown-cleanup-receipt-negative-2026-07-30.md`
- `fixture-teardown-cleanup-receipt-run-2026-07-30.md`
- `fixture-teardown-recovery-diagnostics-state-matrix-2026-07-30.md`
- `fixture-teardown-repository-intent-review-2026-07-30.md`
- `fixture-teardown-repository-alignment-run-2026-07-30.md`
- `python-async-stop-cancellation-run-2026-07-30.md`
- `follow-up-2026-07-30.md`
- retained probes under `probe/`

## Handoff

- Parent scout: #26
- Fixture recovery: #141
- Outcome accounting: #142
- Python shutdown ownership: #149
- Fieldwork review PR: #49
- Primary fixture source PRs: `teamleaderleo/playwright#24` and `#26`
- Expected-failure probe: `teamleaderleo/playwright#28`
- Python stop probe: `teamleaderleo/playwright-python#1`
- Upstream contact: unauthorized

No upstream contact occurred.