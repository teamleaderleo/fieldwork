# Unit 08 approaches ledger

## Selected approach — one shared task with cancellation-safe wait joining

Canonical source: [`teamleaderleo/playwright-python#8`](https://github.com/teamleaderleo/playwright-python/pull/8), head `4cfc6a9e3e3a5c6dcab04015a1210ce6924d4c27`.

Properties:

- one `Connection.stop_async()` task;
- callers join through `asyncio.wait({stop_task})`, then await the completed task for its exact result;
- cancellation of a caller does not cancel cleanup;
- active waiter count;
- same terminal success or failure for every caller;
- one deferred event-loop report when failure has no observer;
- a late waiter cancels a pending report;
- no workflow, generated file, dependency, or packaging change in the clean source.

Why selected:

- directly represents the completion callers need to join;
- preserves the existing request-stop → transport completion → cleanup operation;
- separates caller cancellation from cleanup ownership;
- avoids Python 3.14's automatic `asyncio.shield` failure logger;
- passed full repository pre-commit, wheel builds, and all 33 focused cases on Python 3.10, 3.12, and 3.14;
- keeps state bounded to one terminal task and one possible explicit report.

## Accepted foundation, rejected final join — `asyncio.shield`

Historical selected mechanism used one shared task and `await asyncio.shield(stop_task)`.

What it established:

- retry after cancellation;
- one operation for concurrent callers;
- cancellation of one waiter leaves cleanup and other waiters alive;
- repeated success is idempotent;
- failure remains shared and joinable;
- explicit fallback reporting closes the silent-failure gap on Python 3.12.

Why it lost:

Run `30692014938`, job `91348287797`, passed pre-commit and all 33 cases on Python 3.10 and 3.12. On Python 3.14, a cancelled shielded waiter caused CPython to publish `RuntimeError exception in shielded future` when the inner task failed. The candidate also published its intentional report, so exactly three observability cases saw duplicate contexts.

The ownership model remains selected; only the join primitive changed.

## Accepted foundation, rejected policy — silent exception retention

Historical PR #3 head: `dbbc8834acd69dc1f7f122ba1d3f49360565e7ef`.

Mechanism:

- one `_stop_task`;
- callers joined the task;
- done callback retrieved `task.exception()` only to suppress a default warning.

What it proved:

- retry, concurrency, idempotence, and shared failure semantics.

Why final policy lost:

When every waiter cancelled and cleanup later failed, no caller and no event-loop handler observed the failure. Baseline run `30595155697`, job `91045840683`, passed 30 cases and failed exactly the three abandoned-failure controls.

Reopening trigger: explicit maintainer preference for silent retained failure with another documented observation route.

## Viable alternative — explicit shutdown state machine

Possible states: idle, stopping, stopped, failed.

Why deferred:

- the task already represents stopping plus terminal success/failure;
- separate state duplicates task state and creates consistency obligations;
- no required behavior retries an underlying failed cleanup;
- more code broadens the review surface without improving the invariant.

Reopening triggers:

- resumable multi-phase cleanup;
- retry after underlying cleanup failure;
- a public lifecycle status API.

## Rejected — reset `_exit_was_called` after cancellation

Why rejected:

- cleanup may continue after caller cancellation;
- resetting permits two transport-stop/cleanup operations;
- the retry still lacks a stable completion to join;
- failure from the first operation can race with the second.

## Rejected — swallow cancellation until cleanup finishes

Why rejected:

- changes cancellation latency and semantics;
- forces one caller to own cleanup rather than sharing completion;
- concurrent callers still need one terminal outcome;
- can interfere with task-group shutdown.

## Rejected — keep the boolean and call `cleanup()` on retry

Why rejected:

- bypasses transport completion ordering;
- duplicates ownership knowledge from `Connection.stop_async()`;
- can race with the original operation;
- makes the context manager depend on connection internals.

## Rejected — manual future proxy around the task

A custom future could mirror task completion while insulating it from waiter cancellation.

Why rejected:

- `asyncio.wait` already supplies non-cancelling waiting;
- a proxy adds callback and exception-forwarding states;
- a proxy could recreate the same duplicate-observation problem found with shield;
- no executed requirement needs a second completion object.

## Typing approach correction

The observability test temporarily stored `connection.stop_async` under a broad `Callable[[], Awaitable[None]]` annotation and restored it without a method-assignment suppression. Repository mypy rejected both choices.

Final approach:

- infer the exact bound method type;
- use the narrow `# type: ignore[method-assign]` only where monkeypatching assigns or restores the method.

Receipt: run `30691401327`, job `91346660311`; repair `b0509982c7cb7ef9cfeaa6a65225ec6e64a28b92`.

## Executed comparison

| Approach | Receipt | Result |
| --- | --- | --- |
| upstream boolean | `30492906544` | intended incomplete-cleanup assertion fails on Python 3.10 and 3.14 |
| silent shared task | `30595155697` / `91045840683` | 30 passed, 3 observability failures |
| shield + explicit report | `30595174700` / `91045896030` | 33 passed on Python 3.12 |
| shield on current head | `30692014938` / `91348287797` | 3.10/3.12 green; three duplicate-report failures on 3.14 |
| `asyncio.wait` + explicit report | `30692313951` / `91349092242` | pre-commit green; 33 passed on each of 3.10, 3.12, 3.14; wheel and diff hygiene green |

## Harness corrections

- first lifecycle run omitted driver assembly and was classified as setup evidence;
- stale-base PR #7 widened comparison to 31 files and was retired;
- runs checking out PR #7 were demoted from clean-source evidence;
- Test Docker was removed as a false blocker because its path filters do not match unit 08;
- final carrier used `if: always()` for later version steps so one diagnostic could not hide remaining evidence.

## Adjacent questions excluded from this change

- failed async startup task ownership (`microsoft/playwright-python#3132`);
- bounded driver-process termination and public issue #2633;
- retries after underlying stop failure;
- external cancellation of the authoritative task itself;
- general event-loop logging outside this retained cleanup task;
- sync API shutdown changes.
