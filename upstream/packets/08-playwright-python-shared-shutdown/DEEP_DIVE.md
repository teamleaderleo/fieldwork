# Unit 08 deep dive — shared async shutdown ownership

## Problem

The upstream async context manager records that shutdown was entered, not that shutdown completed:

1. return when `_exit_was_called` is true;
2. set `_exit_was_called = True`;
3. await `Connection.stop_async()`.

Cancellation between steps 2 and completion leaves a permanent true marker with no joinable completion object. A later caller returns through the marker even though transport shutdown and `Connection.cleanup()` have not completed.

The deterministic negative test blocks `transport.wait_until_stopped()`, cancels the first `stop()` waiter, releases transport shutdown, retries `stop()`, and checks terminal connection state. Run `30492906544` failed the intended assertion on Python 3.10 and 3.14.

## Governing invariant

Async shutdown has one authoritative completion operation:

- the first caller creates it;
- caller cancellation does not cancel it;
- concurrent and later callers join it;
- success remains idempotent;
- failure remains terminal and identical;
- an abandoned failure reaches the event loop exactly once while remaining joinable.

## Source map

- `async_playwright()` returns `PlaywrightContextManager`.
- `start()` delegates to `__aenter__()`.
- `__aenter__()` creates `Connection` and assigns `playwright.stop = self.__aexit__`.
- direct `playwright.stop()` and context-manager exit therefore share one owner.
- `Connection.stop_async()` requests transport stop, waits for transport completion, and calls connection cleanup.
- `Connection.cleanup()` establishes terminal closed state and resolves or rejects pending callbacks.

The defect belongs in the context manager's representation of shutdown state. `Connection.stop_async()` already owns the correct ordered operation and should not be restarted or partially duplicated.

## Final implementation

Clean source: `4cfc6a9e3e3a5c6dcab04015a1210ce6924d4c27`.

### One task owns shutdown

The first caller creates and assigns `_stop_task` before the first suspension. Within one event loop, another caller cannot interleave before assignment and create a second task.

### Cancellation-safe join without `asyncio.shield`

Every caller captures the authoritative task and performs:

```python
await asyncio.wait({stop_task})
await stop_task
```

`asyncio.wait` waits for the supplied task but does not propagate cancellation into it. Cancelling the caller cancels only that caller's wait. When the wait completes normally, the second await returns or raises the authoritative task's exact terminal outcome.

This is intentionally not `asyncio.shield`.

### Why shield was removed

The first selected implementation used `await asyncio.shield(stop_task)`. It passed the focused matrix on Python 3.12. Exact current-head execution then exposed a supported-version semantic difference:

- Python 3.10/3.12: a cancelled shielded waiter retrieves the inner task's exception without adding another report;
- Python 3.14: shield installs an automatic inner-task exception logger, producing `RuntimeError exception in shielded future` if the inner task later fails.

The candidate also intentionally reports an abandoned cleanup failure. Python 3.14 therefore produced two handler contexts for one failure. Run `30692014938`, job `91348287797`, failed exactly three observability controls, one per browser parameter.

Replacing shield with `asyncio.wait` preserves the required cancellation boundary and leaves failure publication under one policy.

### Waiter-owned ordinary observation

`_stop_waiters` counts active joiners. A caller that receives the task failure marks it observed and cancels any pending fallback report.

### Abandoned failure observation

The task done callback retrieves and stores failure. When no waiter remains and no caller has observed it, one `call_soon` callback invokes the task loop's exception handler with:

```python
{
    "message": "Playwright stop task failed",
    "exception": self._stop_failure,
    "task": self._stop_task,
}
```

A caller arriving before publication cancels the pending callback. A caller arriving after publication still receives the same original task failure. `_stop_failure_reported` prevents a second explicit report.

## Race review

### Two first callers

Task creation and assignment happen synchronously. The second caller sees the existing task.

### One waiter cancelled, one survives

Both wait on the same task. Cancelling one `asyncio.wait` call does not cancel the task or the surviving waiter.

### Every waiter cancelled before success

The task completes successfully. No failure is stored or reported. A later caller joins the completed task and returns successfully.

### Every waiter cancelled before failure

The task done callback stores failure. When the last waiter leaves, one report is scheduled. A late caller either cancels the pending report and observes normally or arrives after publication and still receives the same failure.

### Failure while waiters remain

Each waiter eventually awaits the completed task and receives the same exception object. The first ordinary observer marks failure observed; no fallback report is emitted.

### Caller cancelled before the stop task's first timeslice

The task object already exists and remains scheduled. Cancelling the caller's wait does not cancel the task. A later caller joins the same operation.

### Context-manager body failure

Successful cleanup allows the body failure to propagate. Cleanup failure takes precedence and preserves the body failure in `__context__`.

## Typing repair

The tests monkeypatch `Connection.stop_async`. The first clean test annotated the saved bound method as a broad `Callable[[], Awaitable[None]]` and removed the method-assignment suppression on restoration. Repository mypy correctly rejected both choices.

Commit `b0509982c7cb7ef9cfeaa6a65225ec6e64a28b92` lets the bound method's exact coroutine type be inferred and keeps only the narrow `# type: ignore[method-assign]` required for monkeypatching.

## Exact final execution

Workflow `30692313951`, job `91349092242`:

- Ubuntu 24.04 ARM;
- wheel builds passed on Python 3.10.20, 3.12.13, and 3.14.6;
- full repository pre-commit passed;
- each version passed all 33 focused cases;
- total current-head focused cases: 99;
- reruns disabled;
- tracked diff hygiene passed.

The final Python 3.14 pass is the decisive compatibility receipt: the automatic shield context is absent and the intentional report remains exactly once.

## Public API and performance

- no public signature changes;
- no protocol or generated API changes;
- direct stop and context-manager exit continue sharing the same public method;
- shutdown allocates one task and a small fixed set of state fields;
- the failure fallback schedules at most one event-loop callback;
- no steady-state browser operation changes.

## Claim boundary

Supported:

- the upstream boolean can lose joinable cleanup ownership after caller cancellation;
- one retained task restores stable ownership and outcome;
- the final join works across supported Python 3.10, 3.12, and 3.14 execution;
- abandoned failure is observable exactly once in the tested policy.

Not claimed:

- measured production frequency;
- measured browser-process leakage;
- a fix for every async cancellation path in Playwright;
- recovery after external cancellation of the authoritative stop task;
- a general event-loop logging policy outside this one retained task.

## Cross-language comparison

### Playwright Node

The out-of-process wrapper keeps one `_closePromise`. Transport closure resolves that terminal promise, and `stop()` destroys the streams and awaits the same completion. This independently supports representing shutdown as one joinable terminal operation.

### Playwright Java

`PlaywrightImpl.close()` closes the connection and waits at most 30 seconds for the driver process, warning on timeout. Java therefore combines single connection ownership with bounded process termination.

### Playwright .NET

Disposal flows through one `Connection` object rather than recreating shutdown work. This again supports a single owner without requiring protocol changes.

These implementations are design context, not direct code sources for the Python patch.

## Follow-on leads outside unit 08

### Async startup task ownership

Public issue [`microsoft/playwright-python#3132`](https://github.com/microsoft/playwright-python/issues/3132) records a failed async startup path where the internal `Connection.init` task exception can be left unretrieved. The report includes a real-driver reproduction. This is adjacent lifecycle ownership work but is not part of shutdown PR #8.

### Bounded driver-process shutdown

Python `PipeTransport.run()` awaits process communication without an explicit timeout. Java uses a 30-second process wait, and public Python issue [`#2633`](https://github.com/microsoft/playwright-python/issues/2633) is adjacent process-termination history. A Python timeout must not be copied speculatively; it needs a deterministic current reproduction and careful force-termination semantics.

No public upstream interaction occurred for either lead.

## Rollback

Reverting the exact three-file candidate restores the old boolean behavior and removes the regression tests. No migration, generated output, dependency change, or persistent state exists.
