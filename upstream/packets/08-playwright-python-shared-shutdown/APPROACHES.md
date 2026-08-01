# Unit 08 approaches ledger

## In simple words

Several repairs can make a cancelled first caller stop blocking later shutdown attempts. The selected design keeps the existing cleanup operation intact and changes ownership from a boolean to the operation's task. The alternatives either permit duplicate cleanup, introduce more states than the mechanism requires, or hide an abandoned failure.

## Selected approach — one shielded task with waiter-owned observation

Source: [`teamleaderleo/playwright-python#8`](https://github.com/teamleaderleo/playwright-python/pull/8) at `54c17acaa1189bca3cf66da0bd9c22dae224b1ec`.

Properties:

- one `Connection.stop_async()` task;
- `asyncio.shield()` around every wait;
- active waiter count;
- same success or failure for all callers;
- one deferred event-loop report when failure has no observer;
- pending report cancelled by a late waiter;
- no temporary workflow in the clean source.

Why selected:

- directly represents the completion callers need to join;
- preserves the existing request-stop → transport completion → cleanup owner;
- caller cancellation and cleanup cancellation remain separate;
- focused paired execution distinguishes it from the silent baseline;
- state remains bounded to one terminal task and one possible report.

## Accepted foundation, rejected final policy — shared task with silent exception retention

Historical source: [`teamleaderleo/playwright-python#3`](https://github.com/teamleaderleo/playwright-python/pull/3) at `dbbc8834acd69dc1f7f122ba1d3f49360565e7ef`.

Mechanism:

- one `_stop_task`;
- all callers await through `asyncio.shield()`;
- done callback calls `task.exception()` to suppress an unhandled-task warning.

What it proved:

- retry after cancellation;
- one operation for concurrent callers;
- one cancelled waiter leaves another alive;
- repeated success is idempotent;
- failure remains shared after cancellation.

Why final policy lost:

When every waiter cancels and the task later fails, the done callback retrieves the exception and no observer receives it. PR #5's paired controls produced exactly three failures, one for each browser parameter, solely on the missing loop-exception report.

Reopening trigger:

- explicit maintainer preference for silent retained failure, with a documented observation route elsewhere.

## Viable alternative — explicit shutdown state machine

Possible states:

- idle;
- stopping;
- stopped;
- failed.

Possible transitions would retain a future/task for stopping and terminal outcome for stopped/failed.

Why deferred:

- the task already represents stopping plus terminal success/failure;
- separate state duplicates task state and creates consistency obligations;
- no tested behavior requires restart after terminal failure;
- more code would broaden the review surface without improving the selected invariant.

Reopening trigger:

- a future requirement for retry after underlying cleanup failure;
- multiple ordered cleanup phases with independently resumable ownership;
- a public lifecycle status API.

## Rejected easy answer — reset `_exit_was_called` when cancellation occurs

Concept:

Catch `CancelledError`, reset the guard, then allow a later caller to run `stop_async()` again.

Why rejected:

- cancellation can occur while the first cleanup continues below the caller;
- resetting permits duplicate transport-stop or cleanup operations;
- the later caller lacks a stable completion to join;
- failure from the first operation can race with a second operation.

Reopening trigger:

- only if `Connection.stop_async()` becomes explicitly cancel-safe, restartable, and idempotent across every phase, with exact concurrency tests. Current evidence supports one operation instead.

## Rejected easy answer — swallow caller cancellation until cleanup finishes

Concept:

Ignore cancellation, await cleanup to completion, then return normally or re-raise later.

Why rejected:

- changes caller cancellation latency and semantics;
- forces one caller to own cleanup rather than sharing completion;
- concurrent callers still need a stable outcome owner;
- masking cancellation can interfere with task-group shutdown.

Reopening trigger:

- an explicit public contract that shutdown is uncancellable and caller cancellation must wait for completion.

## Rejected easy answer — keep boolean and call `cleanup()` on retry

Concept:

A later call detects partial shutdown and invokes `Connection.cleanup()` directly.

Why rejected:

- bypasses transport completion ordering;
- duplicates ownership knowledge from `Connection.stop_async()`;
- can race with the original stop task;
- forces the context manager to understand connection internals.

## Executed negative control — lifecycle tests on silent baseline

PR #5 head: `13848d073c9d23629a9a8300c89262a4d8b42411`.

Run `30595155697`, job `91045840683`:

- 33 tests collected across Chromium, Firefox, WebKit;
- 30 passed;
- three failed exactly at `test_unjoined_stop_failure_reaches_loop_exception_handler`;
- Black and diff hygiene passed.

This result accepts the shared-task ownership and rejects only silent abandoned failure.

## Executed selected repair

PR #6 head: `beb025b6ee98e4b15b80335039f5d0afec5a7efd`.

Run `30595174700`, job `91045896030`:

- 33 passed;
- 2 warnings;
- 7.20 seconds;
- Black passed;
- tracked diff hygiene passed;
- independent exact-head review `4827700772`: ACCEPT for the bounded focused mechanism.

## Harness approaches and corrections

### First lifecycle run — invalid setup evidence

Run `30590715257`, job `91032218906` installed the editable package without assembling the driver. Existing tests failed at startup and the first new control timed out. The run was cancelled and classified as setup evidence.

Correction:

- run `python -m build --wheel`;
- disable automatic reruns;
- use verbose output and long tracebacks.

### Base-drift pull request — invalid comparison surface

Owned PR #7 compared the current-base source branch against stale fork `main` at `9a10128...`, producing a 31-file diff. It was closed and replaced by PR #8 against exact base branch `upstream/base-3b7c24c` at `3b7c24c...`.

## Adjacent questions excluded

- connection callback cleanup bug in public issue #2581;
- browser-process termination guarantees;
- retries after an underlying stop failure;
- sync API shutdown ownership;
- general event-loop logging policy outside this one retained task;
- broader task-group cancellation behavior in protocol callbacks.
