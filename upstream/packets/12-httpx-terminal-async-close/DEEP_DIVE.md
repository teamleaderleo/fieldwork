# Deep dive — Unit 12 terminal async-response close

## In simple words

`Response.aclose()` owns the public transition from a readable streamed response to released resources. The delegated stream may be third-party code, so HTTPX cannot assume that a second `aclose()` is harmless after the first call committed work and then raised.

The candidate uses one event to coordinate callers, blocks reads when close begins, marks successful completion only after delegated cleanup returns, and turns escaped cleanup failure into a terminal unknown outcome. That direction survives the main adversarial cases. The event alone cannot distinguish a legitimate caller from the task already executing the delegated close. Same-task re-entry therefore creates a cycle.

## Governing invariant

> Once arbitrary `AsyncByteStream.aclose()` begins, HTTPX must avoid repeating unknown cleanup, preserve the initiating result, release unrelated observers, and avoid making the owner wait on itself.

## Current behavior

### Public base

At `b5addb64f0161ff6bfe94c124ef76f6a1fba5254`, `Response.aclose()` sets `is_closed = True` before awaiting `stream.aclose()`. A failure or cancellation can leave public state ahead of cleanup. Concurrent close callers can return while delegated cleanup remains in progress.

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

## Source map

| Area | Exact path and symbol | Responsibility | Relevant tests |
| --- | --- | --- | --- |
| response close state | [`httpx/_models.py::_AsyncCloseState`](https://github.com/teamleaderleo/httpx/blob/18256f10d1b306bdf87a1bab24b214c15839147b/httpx/_models.py#L57-L61) | event and failed settlement bit | terminal unknown/cancellation tests |
| observer diagnostic | [`_new_async_close_error`](https://github.com/teamleaderleo/httpx/blob/18256f10d1b306bdf87a1bab24b214c15839147b/httpx/_models.py#L64-L74) | fresh neutral outer failure and fresh neutral cause | terminal unknown/cancellation tests |
| response state initialization | [`Response.__init__`](https://github.com/teamleaderleo/httpx/blob/18256f10d1b306bdf87a1bab24b214c15839147b/httpx/_models.py#L562-L570) | open/started/in-flight/failed state | pickle and public-state controls |
| read barrier | [`Response.aiter_raw`](https://github.com/teamleaderleo/httpx/blob/18256f10d1b306bdf87a1bab24b214c15839147b/httpx/_models.py#L1076-L1088) | rejects body reads once close starts | terminal unknown/cancellation tests |
| close operation | [`Response.aclose`](https://github.com/teamleaderleo/httpx/blob/18256f10d1b306bdf87a1bab24b214c15839147b/httpx/_models.py#L1104-L1137) | owns admission, delegation, settlement, and observers | all three candidate test files |
| elapsed publication | [`AsyncResponseStream.aclose`](https://github.com/teamleaderleo/httpx/blob/18256f10d1b306bdf87a1bab24b214c15839147b/httpx/_client.py#L179-L183) | publishes elapsed after successful cleanup | client elapsed regression |

## Reproduction or characterization

### Setup

- exact upstream revision: `b5addb64f0161ff6bfe94c124ef76f6a1fba5254`
- exact candidate revision: `18256f10d1b306bdf87a1bab24b214c15839147b`
- target execution: GitHub Actions executor run `30631155839` and direct Test Suite `30631127167`
- re-entry model: Python `3.13.5`, AnyIO `4.13.0`, asyncio backend
- retained receipt: [`receipts/reentrant-close-probe.md`](./receipts/reentrant-close-probe.md)

### Baseline result

Owned research PR #1 executed a commit-then-raise custom stream. Retry ownership caused two close calls and two committed cleanup effects. The base also publishes `is_closed` before delegated cleanup settles.

### Candidate result

The exact source candidate passes its focused terminal-close matrix and repository gates. A source-equivalent re-entry model produces:

```text
TIMEOUT 1 False True
```

The stream was entered once, the response remained publicly incomplete, and deadline cancellation converted the cycle into terminal failure.

## Failure model

1. Caller A enters `Response.aclose()` with no current state.
2. Caller A creates `_AsyncCloseState`, records close-started, and awaits `self.stream.aclose()`.
3. The delegated stream invokes `await response.aclose()` in Caller A's task.
4. The inner call sees the existing state and executes `await state.event.wait()`.
5. The event can only be set by the outer call's success or failure settlement.
6. The outer call cannot resume until the inner call returns.
7. External cancellation eventually reaches the outer `except BaseException` path and marks the response terminal-failed.

Steps 1–6 follow directly from the exact source and the executed model. Step 7 depends on an external cancellation source; without one, the cycle remains pending.

## Consequence and claim boundary

### Established

- A public custom stream can call the response indirectly; the public stream interface contains no prohibition against this ownership graph.
- The exact candidate stores no owner identity.
- The event path creates a same-task dependency cycle.
- A deadline cancellation breaks the model cycle and leaves the response terminal-failed.
- Existing focused and full tests omit this discriminator.

### Inferred

- A real custom transport or trace/callback path with access to the response could trigger the same cycle.
- An immediate owner-reentry error would preserve unrelated task joining while preventing the cycle.

### Unknown or unmeasured

- Real-world frequency.
- Whether maintainers want to support re-entry, reject it explicitly, or reorder ownership to avoid it.
- Minimum AnyIO version compatibility for task identity APIs.
- Trio behavior on a repaired candidate.
- Interaction with arbitrary stream code that catches an immediate re-entry error and continues cleanup.

## Selected implementation direction

Keep the terminal outcome-unknown contract and add cycle detection to the in-flight close state.

A narrow repair can record an opaque owner-task identity when `_AsyncCloseState` is created. Before an existing-state caller waits:

1. compare the current task identity with the recorded owner;
2. on a match, raise a fresh immediate close/re-entry error associated with the request;
3. leave the shared close state untouched;
4. allow unrelated callers to keep waiting on the owner's settlement.

If the delegated stream allows that error to escape, the outer owner receives it as its original stream-close failure and terminalizes the response. If the stream catches it and completes cleanup, the owner can still settle successfully. The exact exception type and message need target-native review; the central requirement is cycle-free settlement without cancelling or poisoning unrelated waiters.

An alternative is a separately spawned authoritative close task. That widens cancellation, task lifetime, backend, and resource ownership behavior and remains larger than the current defect requires.

## Compatibility analysis

- public API: no new public method; later observer behavior stays `CloseError`-based
- source compatibility: private state changes only
- binary or wire compatibility: not applicable
- persistence or format compatibility: pickle must continue omitting transient close coordination and restoring an inert closed response
- platform behavior: owner identity must work under supported AnyIO asyncio and Trio backends and Python 3.9+
- performance and allocation: one owner identity per active async close; negligible compared with event allocation
- cancellation, retry, and recovery: arbitrary delegated close remains at-most-once; external waiters remain joinable; owner re-entry fails immediately
- generated output: not applicable
- migration or rollback: revert the private state/test commit; no persistent user data changes

## Adversarial and edge controls

- same-owner re-entry with a request: returns promptly and does not wait on itself
- same-owner re-entry without a request: valid failure with no invented request
- delegated stream catches the re-entry failure and then succeeds: response settles closed and external waiter succeeds
- delegated stream lets the re-entry failure escape: owner receives original failure, observers receive fresh terminal errors, cleanup runs once
- unrelated external waiter during re-entry: remains attached to the original attempt
- observer cancellation: does not cancel or terminalize the owner attempt
- owner cancellation during arbitrary close: owner identity preserved; observers receive neutral terminal failures
- ordinary commit-then-raise: terminal, one cleanup call
- successful blocking close: elapsed remains unavailable while pending and publishes the pre-cleanup sample only after success
- pickle after active/failure state: no event, owner identity, or failure graph retained
- GC after settlement: event/state/stream and frame-local objects become collectible when external references release them

## Review risks

### Task identity portability

AnyIO task identifiers must be inspected against the repository's supported dependency range. A task object itself may retain more state than an opaque identifier. Prefer the smallest stable identity representation that supports equality during one attempt.

### New immediate error surface

Re-entry currently hangs. A prompt error is a new observable result. The issue/discussion draft should ask maintainers whether explicit rejection is preferred over support.

### State vocabulary

`is_closed == False` after failed cleanup while reads remain blocked is intentionally unusual. The current candidate uses three private fields plus the public bit. A private enum/state object could make impossible combinations clearer, though that refactor increases the diff. The re-entry repair should stay narrow unless target review demonstrates a concrete state bug.

### Exception precedence

The re-entry failure must not replace a more relevant stream error created later during cleanup. Tests should cover a stream that catches re-entry and then raises a distinct cleanup error.

## Reversing evidence

Reopen the selected direction if:

- the public stream contract explicitly guarantees repeated close after arbitrary interruption;
- current HTTPX main adopts equivalent terminal and re-entry handling;
- target-native tests show owner identity cannot be represented portably across supported AnyIO versions;
- maintainers require an authoritative background cleanup operation or a different public state model;
- a narrower source change avoids both duplicate cleanup and re-entry without new state.

## Adjacent work excluded

- synchronous `Response.close()` settlement — Fieldwork #185 / owned PR #2
- HTTPCore HTTP/1.1 and HTTP/2 delegated retirement — Fieldwork #227 / owned PR #3
- same-socket reuse and transport-capacity recovery — HTTPCore lane
- `AsyncClient.aclose()` across main and mounted transports — Fieldwork #177
- broad state-enum refactor — deferred unless required for correctness
- release, merge, or public upstream interaction — separately authorized actions