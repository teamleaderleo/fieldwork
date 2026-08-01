# Deep dive — Unit 12 terminal async-response close

## In simple words

`Response.aclose()` owns the public transition from a readable streamed response to released resources. The delegated stream may be third-party code, so HTTPX cannot assume that a second `aclose()` is harmless after the first call committed work and then raised.

The current candidate uses one event to coordinate callers, blocks reads when close begins, marks successful completion only after delegated cleanup returns, and turns escaped cleanup failure into a terminal unknown outcome. That direction survives the main failure, cancellation, observer, traceback, and garbage-collection cases.

Two exact-head defects remain. The event stores no owner identity, so same-task re-entry waits on itself. The client wrapper samples elapsed after delegated cleanup, so successful cleanup latency silently changes an existing measurement. The retained repair adds owner-task detection and restores pre-cleanup elapsed sampling while delaying publication until success.

## Governing invariant

> Once arbitrary `AsyncByteStream.aclose()` begins, HTTPX must avoid repeating unknown cleanup, preserve the initiating result, release unrelated observers, avoid making the owner wait on itself, and avoid redefining existing elapsed timing.

## Current behavior

### Public base

At `b5addb64f0161ff6bfe94c124ef76f6a1fba5254`, `Response.aclose()` sets `is_closed = True` before awaiting `stream.aclose()`. A failure or cancellation can leave public state ahead of cleanup. Concurrent close callers can return while delegated cleanup remains in progress.

`BoundAsyncStream.aclose()` samples and publishes elapsed before awaiting stream cleanup. This means failed cleanup can publish elapsed, while successful elapsed excludes cleanup latency.

### Current candidate

- entrypoint: `Response.aclose()`
- state owner: `Response`, through `_async_close_started`, `_async_close_state`, `_async_close_failed`, and `is_closed`
- caller-visible result: owner receives the original escaped `BaseException`; observers receive fresh neutral `CloseError` objects after failure
- side effect: arbitrary `self.stream.aclose()` runs once
- cleanup owner: the first admitted caller
- publication boundary: `is_closed` and client `elapsed` publish only after delegated cleanup succeeds
- concurrency ordering: other tasks wait on `_AsyncCloseState.event`
- failure ordering: the owner sets terminal failure and signals the event before re-raising
- retry ordering: later close calls receive a fresh neutral error and never re-enter the stream
- re-entry flaw: the owning task is indistinguishable from an unrelated waiter
- elapsed flaw: the current wrapper awaits stream cleanup before sampling elapsed

## Source map

| Area | Exact path and symbol | Responsibility | Relevant tests |
| --- | --- | --- | --- |
| response close state | [`httpx/_models.py::_AsyncCloseState`](https://github.com/teamleaderleo/httpx/blob/18256f10d1b306bdf87a1bab24b214c15839147b/httpx/_models.py#L57-L61) | event and failed settlement bit; currently no owner identity | terminal unknown/cancellation tests |
| observer diagnostic | [`_new_async_close_error`](https://github.com/teamleaderleo/httpx/blob/18256f10d1b306bdf87a1bab24b214c15839147b/httpx/_models.py#L64-L74) | fresh neutral outer failure and fresh neutral cause | terminal unknown/cancellation tests |
| response state initialization | [`Response.__init__`](https://github.com/teamleaderleo/httpx/blob/18256f10d1b306bdf87a1bab24b214c15839147b/httpx/_models.py#L562-L570) | open/started/in-flight/failed state | pickle and public-state controls |
| read barrier | [`Response.aiter_raw`](https://github.com/teamleaderleo/httpx/blob/18256f10d1b306bdf87a1bab24b214c15839147b/httpx/_models.py#L1076-L1088) | rejects body reads once close starts | terminal unknown/cancellation tests |
| close operation | [`Response.aclose`](https://github.com/teamleaderleo/httpx/blob/18256f10d1b306bdf87a1bab24b214c15839147b/httpx/_models.py#L1104-L1137) | admission, delegation, settlement, and observers | all current response-close tests |
| elapsed publication | [`BoundAsyncStream.aclose`](https://github.com/teamleaderleo/httpx/blob/18256f10d1b306bdf87a1bab24b214c15839147b/httpx/_client.py#L179-L183) | current code samples after successful cleanup | current failed-close regression; proposed successful timing control |
| retained repair | [`0001-fix-reentrant-close-and-elapsed-sampling.patch`](./patches/0001-fix-reentrant-close-and-elapsed-sampling.patch) | owner task ID, immediate re-entry failure, elapsed sample ordering, and tests | local repaired execution |

## Reproduction and characterization

### Exact identities

- upstream revision: `b5addb64f0161ff6bfe94c124ef76f6a1fba5254`
- current candidate revision: `18256f10d1b306bdf87a1bab24b214c15839147b`
- current production blobs:
  - `_models.py`: `3ccb5290ceb95d96e24047bcec2897c52de16176`
  - `_client.py`: `79934d050cd77414fb6f9c1024f42f6029c924e0`
- target execution: executor run `30631155839` and direct Test Suite `30631127167`
- new local environment: Python `3.13.5`, AnyIO `4.13.0`, asyncio backend

### Baseline retry result

Owned research PR #1 executed a commit-then-raise custom stream. Retry ownership caused two close calls and two committed cleanup effects. The public base also publishes `is_closed` before delegated cleanup settles.

### Current candidate exact-blobs result

The two current production files were reconstructed to their exact Git blob SHAs. Running the five new/retained target tests against those files produced:

```text
4 failed, 1 passed in 3.28s
```

The three re-entry cases timed out. The deterministic elapsed control reported `10.0` seconds where the pre-cleanup sample was `2.0` seconds.

Direct output:

```text
REENTRY_TIMEOUT 1 False True
ELAPSED_SECONDS 10.0
```

### Repaired patch result

The retained patch changes four files and adds one new test file. The local repaired package produced:

```text
5 passed in 0.12s
```

`py_compile` also passed for both production files.

This is repaired-package execution under asyncio/Python 3.13, not a direct source-branch or complete repository receipt.

## Failure model A — same-task re-entry

1. Caller A enters `Response.aclose()` with no current state.
2. Caller A creates `_AsyncCloseState`, records close-started, and awaits `self.stream.aclose()`.
3. The delegated stream invokes `await response.aclose()` in Caller A's task.
4. The inner call sees the existing state and executes `await state.event.wait()`.
5. The event can only be set by the outer call's success or failure settlement.
6. The outer call cannot resume until the inner call returns.
7. External cancellation eventually reaches the outer `except BaseException` path and marks the response terminal-failed.

Steps 1–6 follow from the exact current source and exact-blob package execution. Step 7 depends on an external cancellation source; without one, the cycle remains pending.

## Failure model B — elapsed semantic drift

1. `_send_single_request()` records request start time.
2. The current candidate enters `BoundAsyncStream.aclose()`.
3. It awaits arbitrary stream cleanup.
4. Only after cleanup returns does it sample `perf_counter()`.
5. It publishes elapsed including cleanup duration.

The public base sampled before cleanup. The candidate fixed failed publication by moving the entire sample-and-assignment block after cleanup, changing successful semantics. The repair samples before the await and assigns after success.

## Consequence and claim boundary

### Established

- A public custom stream can commit an effect before raising; generic retry can duplicate that effect.
- The current candidate stores no owner identity.
- The current event path creates a same-task dependency cycle.
- A deadline cancellation breaks the cycle and leaves the response terminal-failed.
- The current candidate includes delegated cleanup latency in successful elapsed.
- Existing focused and full tests omit both discriminators.
- The retained repair passes the five local target tests under asyncio/Python 3.13.

### Inferred

- A real custom transport or callback path with access to the response could trigger the same cycle.
- Immediate owner-reentry failure preserves unrelated task joining while preventing the exact cycle.
- Restoring pre-cleanup sampling avoids an undocumented elapsed behavior change.

### Unknown or unmeasured

- Real-world frequency.
- Whether maintainers want to support re-entry, reject it explicitly, or use broader callback provenance.
- Minimum AnyIO version and type-check compatibility for task identity.
- Trio and Python 3.9 behavior on the repaired patch.
- Descendant task cycles created inside delegated cleanup.
- Real transport elapsed sensitivity to cleanup duration.

## Selected implementation

### Terminal outcome-unknown

Keep the current one-attempt event and terminal failed bit:

- admission blocks reads;
- one owner invokes arbitrary cleanup;
- unrelated external callers join;
- success publishes closed state;
- escaped owner failure/cancellation remains original to the owner;
- observers receive fresh neutral errors;
- arbitrary owner exceptions and tracebacks are not retained;
- later calls never repeat uncertain cleanup.

### Exact same-task cycle detection

The retained patch records `anyio.get_current_task().id` when `_AsyncCloseState` is created. Before an existing-state caller waits, it compares the current task ID with the owner ID.

On a match it raises a request-associated `CloseError` immediately without changing shared state. If the stream catches that error and completes, the owner and external waiters settle successfully. If it escapes, the outer owner receives that original failure and the response becomes terminal outcome-unknown.

This patch detects the executed same-task cycle. A context-provenance design that also rejects inherited child tasks is a broader alternative and remains a review question.

### Elapsed sampling

The retained patch uses:

```python
elapsed = time.perf_counter() - self._start
await self._stream.aclose()
self._response.elapsed = datetime.timedelta(seconds=elapsed)
```

This preserves the existing successful measurement while preventing failed cleanup from publishing elapsed.

## Compatibility analysis

- public API: no new method or attribute
- source compatibility: private state changes only
- binary or wire compatibility: not applicable
- persistence: pickle continues omitting transient close coordination and restores an inert closed response
- platform: owner identity must work under supported AnyIO asyncio and Trio backends and Python 3.9+
- performance: one integer task ID per active async close; negligible beside the event allocation
- cancellation/retry: arbitrary delegated close remains at-most-once; external waiters remain joinable; same-task re-entry fails immediately
- elapsed: successful timing keeps its previous pre-cleanup boundary; failed cleanup leaves elapsed unavailable
- generated output: not applicable
- migration: none
- rollback: revert the private state, timing order, and tests

## Adversarial and edge controls

- request-bound same-task re-entry returns promptly
- requestless same-task re-entry returns promptly without invented request state
- stream catches re-entry failure and completes while external waiter succeeds
- escaping re-entry terminalizes once and later observers are neutral
- observer cancellation does not cancel owner attempt
- owner cancellation preserves backend-native identity
- ordinary commit-then-raise remains terminal and one-shot
- successful blocking close keeps elapsed unavailable while pending and publishes pre-cleanup sample after success
- failed cleanup leaves elapsed unavailable
- pickle omits active state and owner task ID
- GC releases event/state/stream and frame-local objects after references clear

## Review risks

### Task identity portability

AnyIO 3.0 already exported `get_current_task()` and task IDs, but the exact supported dependency range and current Mypy behavior still need target execution. Storing the integer avoids retaining a task/coroutine object.

### Descendant provenance

A child task spawned and awaited by delegated cleanup may inherit a dependency cycle while having another task ID. The retained patch stays within the exact demonstrated same-task defect. Review should decide whether a ContextVar provenance token is justified before widening.

### New immediate error

Re-entry currently hangs. A prompt `CloseError` is observable behavior and should receive maintainer direction through a Potential Issue discussion.

### Public state vocabulary

`is_closed == False` after failed cleanup while reads and retries remain blocked is intentionally unusual. A private enum could clarify states, but that refactor widens the patch without an additional demonstrated defect.

### Exception precedence

A stream can catch the re-entry error and later raise another cleanup error. The later error should remain the owner's original failure. Add this control if review considers it necessary.

## Reversing evidence

Reopen the selected direction if:

- the public stream contract guarantees repeated close after arbitrary interruption;
- current HTTPX main adopts equivalent terminal, re-entry, and elapsed handling;
- target tests show task identity is unavailable or unstable in the supported AnyIO range;
- maintainers require background authoritative cleanup or a different public state model;
- descendant-task cycles make exact task-ID detection insufficient for the accepted contract;
- elapsed is intentionally redefined to include cleanup latency.

## Adjacent work excluded

- synchronous `Response.close()` settlement — Fieldwork #185 / owned PR #2
- HTTPCore HTTP/1.1 and HTTP/2 delegated retirement — Fieldwork #227 / owned PR #3
- same-socket reuse and transport-capacity recovery — HTTPCore lane
- `AsyncClient.aclose()` across main and mounted transports — Fieldwork #177
- broad state-enum or ContextVar provenance refactor — deferred pending review
- release, merge, or public upstream interaction — separately authorized actions
