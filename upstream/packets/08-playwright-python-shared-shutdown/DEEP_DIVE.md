# Unit 08 deep dive — shared async shutdown ownership

## In simple words

The old async context manager uses a boolean to remember that shutdown started. The boolean says nothing about whether shutdown completed. A cancelled caller can therefore leave the boolean set while cleanup remains unfinished, and every later caller is sent away.

The selected repair stores the shutdown operation itself. Every caller joins that same task through `asyncio.shield()`. Cancellation belongs to the caller; cleanup completion belongs to the shared task.

## Governing invariant

Async Playwright shutdown has one authoritative completion operation:

- the first caller creates it;
- cancellation of a waiter does not cancel it;
- concurrent and later callers join it;
- success remains idempotent;
- failure remains terminal and identical for every caller;
- an abandoned failure reaches the event loop once while remaining joinable.

## Current behavior

At public upstream base [`3b7c24c3e67dc84f7b0eddd0c5fd2ca685705021`](https://github.com/microsoft/playwright-python/commit/3b7c24c3e67dc84f7b0eddd0c5fd2ca685705021), [`PlaywrightContextManager.__aexit__`](https://github.com/microsoft/playwright-python/blob/3b7c24c3e67dc84f7b0eddd0c5fd2ca685705021/playwright/async_api/_context_manager.py) performs:

1. return when `_exit_was_called` is already true;
2. set `_exit_was_called = True`;
3. await `Connection.stop_async()`.

`Connection.stop_async()` requests transport stop, waits for the transport, then runs connection cleanup. Cancellation during the wait exits `__aexit__` while the boolean remains true. A retry returns before cleanup.

## Source map

- Public entry: `async_playwright()` returns `PlaywrightContextManager`.
- `start()` delegates to `__aenter__()`.
- `__aenter__()` creates the connection and assigns `playwright.stop = self.__aexit__`.
- Both direct `playwright.stop()` and context-manager exit therefore enter the same shutdown owner.
- `Connection.stop_async()` owns the ordered transport-stop and cleanup sequence.
- `Connection.cleanup()` sets terminal connection error state and resolves/rejects pending callbacks.

## Deterministic reproduction

The original target test blocks `transport.wait_until_stopped()`, starts `playwright.stop()`, cancels that caller, releases the transport, then retries `stop()` and checks `_closed_error`.

Exact run `30492906544`:

- Python 3.10 job `90714870057`: intended assertion failed;
- Python 3.14 job `90714870025`: intended assertion failed;
- dependency installation and driver assembly completed;
- no browser launched.

Both versions observed a retry return while `_closed_error is None`.

## Selected implementation

Canonical clean source: [`54c17acaa1189bca3cf66da0bd9c22dae224b1ec`](https://github.com/teamleaderleo/playwright-python/commit/54c17acaa1189bca3cf66da0bd9c22dae224b1ec).

### One task owns shutdown

`_stop_task` replaces `_exit_was_called`. Creation and assignment occur synchronously before the first await, so two callers cannot both create the task within one event loop.

Every caller awaits `asyncio.shield(_stop_task)`. Cancelling the waiter propagates `CancelledError` to that waiter while the task continues.

### Waiters own ordinary failure observation

`_stop_waiters` counts active callers. A caller that receives the task failure marks `_stop_failure_observed` and cancels any pending fallback report.

### Abandoned failures remain visible

The task done callback retrieves and stores a failure. When no waiter remains and no waiter has observed it, one `call_soon` callback is scheduled. That callback invokes the task loop's exception handler with:

- message: `Playwright stop task failed`;
- exception: the stored failure;
- task: the authoritative stop task.

A caller arriving before publication cancels the pending callback and receives the same failure normally. A caller arriving after publication still receives that same task failure. `_stop_failure_reported` prevents duplicate reports.

## Why the implementation owns the defect

The failure originates in the context manager's representation of shutdown state. The old boolean recorded entry, while the required state is completion that callers can join. `Connection.stop_async()` already owns the ordered operation and needs no duplicate execution or reset semantics.

The selected change preserves that existing owner and changes only how callers retain and await it.

## Consequence and claim boundary

Supported consequence:

- connection cleanup can remain incomplete after caller cancellation;
- later `stop()` calls can return without joining or completing cleanup;
- concurrent shutdown callers lack one stable completion owner.

Unsupported broader claims:

- no measured frequency;
- no claim of leaked browser processes in production;
- no ecosystem prevalence claim;
- no claim that every cancellation timing produces visible resource loss.

## Compatibility

### API

No public signature changes. Both public routes already share `__aexit__`.

### Python

The code uses `asyncio.Task`, `asyncio.Handle`, `asyncio.shield`, `call_soon`, and `call_exception_handler`, available across the project's Python 3.10+ range. Exact selected-repair execution is retained on Python 3.12. Negative reproduction covers Python 3.10 and 3.14.

### Exception handling

Cleanup failure keeps its original exception object. During `async with`, a cleanup failure takes precedence while the body failure remains in `__context__`, matching normal Python context-manager behavior.

The manual loop exception context is the remaining compatibility review item, especially for custom exception handlers that inspect keys or message text.

### Performance

Shutdown allocates one task and a small fixed set of state fields. The fallback path schedules at most one event-loop callback per failed shutdown. No steady-state browser or protocol path changes.

### Rollback

Reverting the three-file candidate restores the old boolean behavior and removes the tests. No data migration or generated output exists.

## Exact code and test links

- [Production implementation](https://github.com/teamleaderleo/playwright-python/blob/54c17acaa1189bca3cf66da0bd9c22dae224b1ec/playwright/async_api/_context_manager.py)
- [Direct stop controls](https://github.com/teamleaderleo/playwright-python/blob/54c17acaa1189bca3cf66da0bd9c22dae224b1ec/tests/async/test_async_stop_cancellation.py)
- [Context-manager and observability controls](https://github.com/teamleaderleo/playwright-python/blob/54c17acaa1189bca3cf66da0bd9c22dae224b1ec/tests/async/test_async_stop_exit_contract.py)
- [Exact-base clean PR](https://github.com/teamleaderleo/playwright-python/pull/8)

## Remaining uncertainty

- Exact clean-head ordinary gates are pending.
- Underlying cancellation of the authoritative stop task is outside the test matrix.
- The one-loop-turn fallback reporting policy is selected and tested, while custom-handler compatibility remains under review.
- Platform coverage for the final selected repair is Ubuntu; earlier PR #3 controls passed in inspected Windows jobs before unrelated suite timeouts.

## Reversal controls

Reconsider the selected policy when any of these occur:

- clean-head ordinary gates reveal a source or typing incompatibility;
- a supported Python version rejects the exception context or task typing;
- a deterministic race produces duplicate reports, silent failure, or a second cleanup task;
- maintainers prefer a simpler public logging or explicit lifecycle contract after an authorized design discussion.
