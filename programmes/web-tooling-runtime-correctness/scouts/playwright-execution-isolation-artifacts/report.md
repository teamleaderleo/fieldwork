# Playwright execution, isolation, teardown, and artifacts scout

- Assignment: #26
- Programme: #15, `web-tooling-runtime-correctness`
- Target hub: #10, Playwright
- Worker: `chatgpt:gpt-5.6-thinking`
- State: `ready-for-synthesis`
- Target repository: https://redirect.github.com/microsoft/playwright
- Target revision: [`microsoft/playwright@0b2088e58e398106445c39fd3e5ec4cb85ef8bbb`](https://redirect.github.com/microsoft/playwright/commit/0b2088e58e398106445c39fd3e5ec4cb85ef8bbb)
- Target package version at that revision: `1.63.0-next`
- Target browser pin: Playwright Chromium revision `1235`, Chrome for Testing `151.0.7922.47`
- Fieldwork base: `teamleaderleo/fieldwork@09fe47ac92ec9c0c333b4979011f6321795deff2`
- Retrieval and probe date: `2026-07-29`
- Claim scope supported: mechanism and interface
- Integration context: proposed Elatura trial; trial has yet to begin
- Upstream contact authorized: `false`

## In simple words

Playwright Test divides execution across runner tasks, dispatchers, worker processes, fixtures, browser processes, contexts, pages, artifact recorders, and reporters. The runner owns scheduling and final status. Workers own hooks and fixtures. The default browser lives for a worker, while default contexts and pages live for one test attempt. Artifacts cross several completion boundaries before reporters see the finished result.

The broad map shows a deliberate normal failure path: hooks, test fixtures, worker fixtures, context closure, and trace packaging complete before the runner reports an attempt. A failed job then retires its worker. Retry behaviour is one child of this wider ownership model.

The map identified fixture teardown as the strongest focused candidate. All test-fixture teardowns share an after-hooks time slot. Once one teardown consumes that slot, later fixtures skip their teardown bodies. The runner still removes those fixtures from its registry, so the later worker-cleanup pass has nothing left to retry. One hanging teardown can therefore suppress independent cleanup callbacks, including callbacks that close external resources or finish diagnostics.

Two other valuable candidates concern incomplete runs. Blob reports are assembled only during reporter `onEnd`, and screenshot or video finalization failures can disappear through silent catches. Abrupt cancellation can leave users with little evidence about which artifacts completed and which failed.

## Evidence labels

- **Normative**: repository protocols and public Playwright option semantics.
- **Documented**: comments and tests in the pinned Playwright source.
- **Observed**: outputs from the retained local probes.
- **Inferred**: consequences derived from pinned source flow and awaiting a target-version reproduction.
- **Illustrative**: proposed campaign interventions and Elatura trial design.
- **Unknown**: exact runtime behavior of `1.63.0-next` in this container.

## Exact source map

| Area | Primary owners at the pinned revision | Relevant tests | Evidence |
| --- | --- | --- | --- |
| Retries and worker replacement | `packages/playwright/src/runner/dispatcher.ts`, `packages/playwright/src/worker/workerMain.ts` | `tests/playwright-test/playwright.trace.spec.ts`, `tests/playwright-test/playwright.artifacts.spec.ts` | Documented |
| Fixture setup and teardown | `packages/playwright/src/worker/fixtureRunner.ts`, `packages/playwright/src/worker/workerMain.ts` | `tests/playwright-test/timeout.spec.ts` | Documented, Inferred |
| Browser and context cleanup | `packages/playwright/src/index.ts`, `packages/utils/processLauncher.ts`, `packages/playwright/src/runner/processHost.ts` | artifact and timeout suites | Documented, Observed |
| Test trace lifecycle | `packages/playwright/src/worker/testTracing.ts`, `packages/playwright/src/index.ts` | `tests/playwright-test/playwright.trace.spec.ts`, artifact suite | Documented, Observed |
| Screenshots and page snapshots | `packages/playwright/src/index.ts` (`SnapshotRecorder`, `ArtifactsRecorder`) | `tests/playwright-test/playwright.artifacts.spec.ts` | Documented, Observed |
| Video lifecycle | `packages/playwright/src/index.ts` (`_contextFactory`) | option-level coverage plus artifact suites | Documented, Observed |
| Reports | `packages/playwright/src/reporters/internalReporter.ts`, `packages/playwright/src/reporters/blob.ts`, `packages/playwright/src/runner/tasks.ts` | reporter suites | Documented, Inferred |
| Cancellation and global timeout | `packages/playwright/src/runner/taskRunner.ts`, `packages/playwright/src/runner/testRunner.ts`, `packages/playwright/src/runner/dispatcher.ts` | timeout and runner suites | Documented, Inferred |
| Worker and child-process stop | `packages/playwright/src/runner/processHost.ts`, `packages/utils/processLauncher.ts` | runner/process tests | Documented, Observed |

## Execution and ownership map

| Owner | State and responsibility | Lifetime | Failure boundary |
| --- | --- | --- | --- |
| `TaskRunner` and `TestRun` | configuration, project phases, overall status, cancellation, reporter completion | whole invocation | global timeout, SIGINT, programmatic stop, setup or reporter error |
| `Dispatcher` | test groups, worker slots, retry jobs, max-failure stop, stdout/stderr routing | one phase | failed job, worker exit, max failures |
| `WorkerMain` | suites loaded in the process, hooks, fixture runner, active test, worker cleanup | one worker process | unexpected test failure, fatal hook/fixture error, stop request |
| Fixture runner | dependency graph and fixture instances for test or worker scope | scope-specific | setup timeout, teardown timeout, dependency failure |
| Browser fixture or manual browser | browser server/process and launch options | usually one worker | fixture teardown, graceful close, process kill |
| Browser context and page | cookies, storage, pages, video source, context tracing | usually one attempt | test timeout, hook failure, context close |
| Artifact recorders | screenshots, snapshots, context trace chunks, video save, test trace merge | one attempt with cross-context inputs | capture failure, close failure, cancellation, output I/O |
| Reporters | attempt events, attachments, final status, durable report files | whole invocation | `onEnd`/`onExit` failure or abrupt process exit |

This ownership map explains the useful follow-up boundary: resources can be correctly isolated during ordinary execution while cleanup evidence still disappears when time or cancellation crosses from one owner to the next.

## Compatibility and realistic-use observations

- The pinned source expects Playwright Chromium revision `1235` and Chrome for Testing `151.0.7922.47`.
- The local probe used Playwright Python `1.57.0` with Debian Chromium `144.0.7559.96`. Those observations establish library-level mechanisms only.
- Browser-specific conclusions require the exact Playwright Test revision and browser bundle because launch flags, process trees, FFmpeg packaging, and artifact formats can differ.
- Existing Playwright tests provide strong ordinary-path coverage across retry trace modes, screenshots, persistent contexts, serial suites, hooks, and fixture timeouts.
- Elatura is a plausible owned realistic-use trial because it exercises a browser sidecar, session cleanup, retries, cancellation, and artifact evidence without production data.
- This scout collected artifact sizes and process survivors. It did not claim comparative performance. A later campaign can measure teardown duration, browser relaunch cost, trace merge time, video close time, and report finalization latency at the exact target revision.

## Lifecycle walk

1. The dispatcher chooses a compatible worker or creates one.
2. `WorkerMain` constructs `TestInfoImpl` with the attempt’s retry number and starts test tracing when configured.
3. Before hooks and required fixtures run. Default browser is worker-scoped; default context and page are test-scoped.
4. The test body runs. Timeout or an unexpected failure interrupts the current test.
5. Playwright runs the finish callback, `afterEach`, test-fixture teardown, applicable `afterAll`, and full worker cleanup after failure.
6. Context closure finalizes videos. Artifact recording stops context traces, captures screenshots, and writes error context. Test tracing then merges and attaches `trace.zip`.
7. `testEnd` crosses to the dispatcher. Attachments arriving after that event are discarded because the dispatcher has removed the attempt record.
8. A failed job retires its worker. Retry candidates enter a new job, either with remaining tests under the immediate strategy or in an isolated retry job.
9. Once task cleanup finishes, reporters receive `onEnd` and `onExit`.

## Findings by area

### Retries

**Documented.** An unexpected attempt failure marks the worker for shutdown. The dispatcher stops failed workers and creates replacements before the next job. This gives retries fresh worker fixtures and fresh default browser processes.

**Documented.** Immediate retries can share the next job with tests left in the file. The alternate retry strategy queues isolated retries after ordinary jobs. Serial suites retry as a unit.

**Consequence.** Campaigns should assert both isolation and ordering. A single `retry === 1` assertion says little about pending tests, serial-suite replay, worker indices, and artifacts from attempt zero.

### Fixtures

**Documented.** Teardown order follows fixture dependencies and continues after errors, retaining the first teardown error.

**Inferred lead finding.** `Fixture.teardown()` checks the shared time slot before starting its teardown body. Its `finally` block removes the fixture from dependency tracking and `instanceForId` even when the body never starts. The later worker-cleanup call to `teardownScope('test')` therefore cannot find that fixture. Existing timeout coverage demonstrates ordinary teardown timeout behavior; the scout found no focused assertion that an independent later fixture’s callback still runs after shared-slot exhaustion.

### Browser cleanup

**Documented.** The default browser fixture closes its browser after `use()`. Graceful worker shutdown also calls `gracefullyCloseAll()` to cover browsers launched manually in tests, hooks, and internal tools.

**Documented.** Browser processes launch in their own process groups on Unix. Browser force-kill targets the whole process group and waits for temporary-directory cleanup.

**Unknown edge.** `ProcessHost` force-kills only the worker PID when heartbeats stop. The exact Playwright Test path deserves a bounded process-tree campaign because browsers sit in separate process groups. A local library-level parent-kill check produced no surviving observed Playwright driver or Chromium processes, so this candidate ranks below the finalization campaigns.

### Traces

**Documented.** Trace modes explicitly distinguish every attempt, the first retry, all retries, first failure, failure retention, and failure-plus-retry retention. Trace recording names include retry ordinals.

**Documented.** Context trace chunks stop before context closure, while test trace packaging happens after worker cleanup. `testEnd` follows packaging, preserving the ordinary attachment path.

**Risk boundary.** Test trace source reads and attachment reads are best effort. A valid trace can omit requested resources without a direct artifact-completion record.

### Screenshots

**Documented.** Screenshots can be captured at test-function completion and again temporarily as contexts close. Temporary screenshots are promoted after the final result is known.

**Risk boundary.** Snapshot errors are swallowed. This protects the test result from diagnostic failures while leaving reporters unable to distinguish “capture disabled,” “page unavailable,” “write failed,” and “capture succeeded.”

### Videos

**Documented.** Video capture begins with context creation. A usable video becomes available only after context close. Playwright then calls `saveAs()` and attaches the resulting WebM file according to the selected retention mode.

**Risk boundary.** Empty or failed video saves are silently caught. The local probe also exposed FFmpeg as a concrete runtime dependency: the installed client expected its bundled executable path before a supplied system FFmpeg adapter was available.

### Reports

**Documented.** Reporter `onEnd` and `onExit` run after task cleanup. A reporter error can change a passing run to failed.

**Inferred risk.** `BlobReporter` buffers report events and creates the ZIP only in `onEnd`. A second interrupt, hard exit, or process crash before or during `onEnd` can leave no replayable blob, even when earlier attachments already exist on disk.

### Cancellation

**Documented.** Task execution races the task loop against programmatic cancellation, SIGINT, and global timeout. Teardown tasks are registered in reverse order.

**Documented sharp edge.** Global timeout cleanup reuses the already-expired deadline. The source comment states that cleanup exits immediately at that point. SIGINT and programmatic cancellation have more room to run cleanup, while a second interrupt can force browser termination.

### Worker lifecycle

**Documented.** A worker captures stdout and stderr into the active trace and attempt. Output emitted during failed-worker teardown remains visible for debugging but is kept away from the next retry’s result.

**Documented.** Worker stop sends an IPC stop request and accepts heartbeats during long graceful teardown. Heartbeat silence eventually triggers a forced kill.

## Retained runnable probe

Files:

- `probe/retry_artifact_probe.py`
- `probe/result.json`
- `probe/hard-kill-result.json`

Run:

```bash
python probe/retry_artifact_probe.py \
  --output /tmp/playwright-retry-artifacts \
  --chromium /usr/bin/chromium \
  --ffmpeg /usr/bin/ffmpeg
```

The focused probe emerged after the ownership map identified context isolation and artifact completion as useful distinguishing properties. It uses the installed Playwright Python client `1.57.0` and two fresh browser attempts. Attempt zero is labelled failed and attempt one passed. The orchestration remains outside Playwright Test, so the result supports browser/context/artifact mechanisms rather than the pinned runner’s retry scheduler.

Observed results:

- fresh context removed the prior page global and cookie;
- both attempts produced a PNG, trace ZIP, and WebM;
- both trace ZIPs contained `trace.trace`, `trace.network`, and `trace.stacks`;
- both browser process sets had zero survivors after explicit close;
- the overall probe introduced zero Chromium processes that remained at the final check;
- a separate library-level SIGKILL check found zero surviving observed Playwright driver or Chromium processes after three seconds.

Environment limits:

- the exact `1.63.0-next` package was unavailable in the local runtime;
- local network navigation was blocked by the execution environment, so the probe uses synthetic page content and context cookies;
- the SIGKILL result covers the Python library driver path and leaves Playwright Test `ProcessHost` force-kill open.

## Ranked campaign candidates

### 1. `playwright-fixture-teardown-resumption`

**Claim to test:** every independent fixture whose teardown body has yet to start receives a later cleanup opportunity after a peer fixture exhausts the shared teardown slot.

**Deterministic case pack:**

1. Define two independent test-scoped fixtures, `blocker` and `sentinel`.
2. Make `blocker` consume the entire after-hooks slot during teardown.
3. Make `sentinel` write a marker, close a manual context, and finish a small artifact.
4. Fail or time out the test with `retries: 1`.
5. Assert the marker, context closure, process count, retry worker index, and attempt artifact matrix.
6. Repeat with reversed fixture declaration and dependency order.

**Current-source prediction:** `sentinel` can skip its teardown body and disappear from the fixture registry before worker cleanup.

**Smallest candidate intervention:** retain fixtures whose teardown body never started and retry them during worker cleanup with a dedicated bounded slot. An alternative gives each independent fixture its own teardown allowance.

**Promotion threshold:** reproduce on the pinned target revision or a current release with an independent cleanup callback omitted.

**Stop condition:** discard scenarios where the omitted callback depends on the blocking fixture or requires an unbounded cleanup promise.

### 2. `playwright-crash-resilient-report-journal`

**Claim to test:** interrupted runs leave a parseable report containing completed attempts, known attachments, and an explicit incomplete-run marker.

**Deterministic case pack:**

1. Run a failing test with trace, screenshot, video, and blob reporter enabled.
2. Add a bounded slow teardown and a slow custom reporter.
3. Send SIGINT at named phase offsets: test body, fixture teardown, trace merge, reporter `onEnd`.
4. Add a second SIGINT case and a global-timeout case.
5. Validate ZIP readability, event order, attachment references, completion marker, and exit status.

**Current-source prediction:** cancellation before or during blob `onEnd` can leave no durable report ZIP.

**Smallest candidate intervention:** append report events to a temporary JSONL journal during the run, then atomically finalize the ZIP and completion manifest during `onEnd`. Recovery tools can read an interrupted journal.

**Promotion threshold:** demonstrate missing or unreadable report data after at least one deterministic phase interruption.

**Stop condition:** separate user-authored reporter deadlocks from built-in reporter finalization.

### 3. `playwright-artifact-finalization-receipts`

**Claim to test:** every requested built-in artifact ends with a machine-readable state: `completed`, `abandoned-by-policy`, `capture-failed`, or `finalization-interrupted`.

**Deterministic case pack:**

- deny screenshot output writes;
- remove or terminate FFmpeg during video completion;
- fail trace resource reads or final ZIP creation;
- close pages during after hooks;
- cancel at each finalizer boundary;
- compare list, JSON, blob, and HTML reporter visibility.

**Current-source prediction:** screenshot and video failures can vanish through silent catches; trace resource gaps can remain implicit.

**Smallest candidate intervention:** emit an artifact-finalization record with artifact kind, attempt, phase, state, path, and concise error. Reporters decide how prominently to render it.

**Promotion threshold:** produce a requested artifact failure with no reporter-visible explanation.

**Stop condition:** retain best-effort artifact behavior; campaign only the missing completion signal.

### 4. `playwright-worker-hard-kill-process-tree`

**Claim to test:** forced worker termination cannot leave browser process groups or profile directories behind.

**Deterministic case pack:**

1. Launch a browser in a Playwright Test worker.
2. block the worker event loop so heartbeats stop;
3. set a small `PWTEST_CHILD_PROCESS_TIMEOUT`;
4. let the runner force-kill the worker;
5. inspect descendant process groups, browser profile directories, and retry startup.

**Current-source reason:** worker kill targets the worker PID, while browser processes use separate process groups.

**Counterevidence:** the retained Python-library SIGKILL check found no survivors.

**Promotion threshold:** exact Playwright Test reproduction at the pinned revision or a current release.

**Disposition:** bounded probe before campaign expansion.

## Proposed Elatura trial

- Testbed: Elatura
- Testbed revision: `teamleaderleo/elatura@bbea414c6e400ba748d053caedb777ecee1cc381`
- Proposed branch: `fieldwork/playwright/retry-teardown-artifact-ledger`
- State: proposed; no `testbed:*` label added

Scenario:

1. Add a Playwright harness on the experimental branch around a synthetic local Elatura session.
2. Run a failed first attempt and passing retry.
3. Use two independent cleanup owners: session cleanup and artifact-ledger finalization.
4. Introduce one bounded teardown stall and one SIGINT case.
5. Record browser PIDs, profile directories, session markers, screenshots, traces, videos, and report completion.
6. Remove the branch and generated outputs after the trial unless the harness earns retention as a regression case.

The trial can establish behavior in a realistic owned browser sidecar. It cannot establish ecosystem demand or upstream intent.

## Failed hypotheses and negative results

- Normal context and browser close produced complete trace, screenshot, and video artifacts with zero surviving launched Chromium processes in the local probe.
- Fresh contexts cleared the synthetic cookie and page global.
- The local Python-library parent-SIGKILL case left zero observed Playwright driver or Chromium survivors after three seconds.
- Existing Playwright tests already cover ordinary retry trace modes, screenshot retention modes, multiple contexts, persistent contexts, serial suites, after hooks, and ordinary fixture teardown timeout.
- Container navigation policy prevented external or local-server navigation. Those failures were excluded from target conclusions.
- The scout did not execute the exact pinned JavaScript runner because that package revision was unavailable locally.

## Recommendation

Open `playwright-fixture-teardown-resumption` first. It has the clearest source-level mechanism, a compact deterministic case pack, and a direct cleanup consequence.

Run `playwright-crash-resilient-report-journal` next and `playwright-artifact-finalization-receipts` in parallel. Both improve evidence preservation across failures and cancellation.

Keep `playwright-worker-hard-kill-process-tree` as a bounded exact-runner probe until a survivor appears.

## Upstream contact

No upstream contact occurred. External contact remains unauthorized.
