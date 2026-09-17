# F149: Share Playwright Python async shutdown across callers

Finding state: `research-active`

Workstream: `B — Browser, web tooling, and runtime boundaries`  
Canonical Fieldwork issue: `#149`  
Canonical implementation: `teamleaderleo/playwright-python#3`  
Exact implementation head: `dbbc8834acd69dc1f7f122ba1d3f49360565e7ef`  
Exact base revision: `9a10128e0ffc7c7429da3779283a2400c2707575`  
Strongest evidence class: mixed `target-executed` and incomplete repository CI  
Current review disposition: `REPAIR + EXECUTE`  
Desk routing: `Review Queue #213; Delivery Desk #160 remains D1 only after missing controls are added`  
Upstream contact authorized: `no`

## In simple words

Stopping Playwright is one cleanup job. If the first caller gets cancelled, another caller should still be able to join the same cleanup and learn whether it succeeded or failed.

The current library uses a boolean that says shutdown already started. Cancellation can leave that boolean set before cleanup finishes, so a later `stop()` returns too early. The candidate replaces the boolean with one shared task and shields the task from caller cancellation.

## Why we care

Returning from `stop()` before connection cleanup completes can leave transport and connection state inconsistent. Starting duplicate shutdown operations would also be unsafe. A shared completion task gives every caller one authoritative result while preserving each caller's own cancellation.

## What happens if we leave it alone

A cancelled first `playwright.stop()` can poison later retries: transport shutdown may finish, yet a second call exits through the old guard while `_closed_error` remains unset. Callers can believe cleanup completed when it did not.

## Current finding

One private `_stop_task` awaited through `asyncio.shield()` is the strongest ownership model. It prevents caller cancellation from cancelling shutdown, lets concurrent and later callers join the same result, preserves idempotent success, and preserves the original failure object.

The current exact head still needs three lifecycle controls before acceptance:

1. immediate cancellation before the shared task gets its first timeslice;
2. direct async-context-manager exit coverage;
3. explicit policy and test for a shutdown failure that occurs after the only waiter is cancelled and never rejoins.

## Historical precedent

### Python `asyncio.shield`

- Source: https://docs.python.org/3/library/asyncio-task.html#shielding-from-cancellation
- Principle supported: caller cancellation can propagate while the underlying task continues.
- Important difference: shielding alone does not define ownership, repeated-call behavior, or how an eventual background failure is observed.

### Existing Playwright connection shutdown sequence

- Source: `playwright/_impl/_connection.py` at the pinned base
- Principle supported: shutdown is one ordered operation: request transport stop, await transport completion, then run connection cleanup.
- Important difference: the context manager's boolean guard does not represent completion of that ordered operation.

## Approaches considered

### Retained approach: one shared task

The first caller creates the task before any suspension. Every caller awaits it through `shield`. This avoids duplicate cleanup and makes success or failure stable.

### Declined: reset the boolean after cancellation

Resetting can start a second `stop_async()` while the first operation still runs, duplicating transport stop and cleanup.

### Declined: swallow caller cancellation until cleanup ends

That changes the caller's cancellation contract and can make task cancellation unresponsive.

### Deferred: retry after authoritative shutdown failure

The candidate treats an underlying shutdown failure as terminal and shared. Restarting cleanup after failure needs a separate state-machine decision.

## Edge cases covered

| Edge case or control | Evidence | Result |
| --- | --- | --- |
| Cancel blocked first caller, then retry | Candidate test | Later caller joins cleanup |
| Two concurrent stop callers | Candidate test | `stop_async()` invoked once |
| Cancel one of two waiters | Candidate test | Surviving waiter completes; shared task continues |
| Repeated successful stop | Candidate test | Completed task reused |
| Concurrent and later failure | Candidate test | Same failure object returned |
| Failure after first waiter cancellation, followed by later joiner | Candidate test | Same failure reaches later caller |

## Edge cases deferred or outside scope

| Edge case | Why deferred | Owning next record or reopening trigger |
| --- | --- | --- |
| Immediate cancellation before the stop coroutine starts | Missing control | Add before acceptance |
| `async with async_playwright()` exit ownership and exception precedence | Public lifecycle path lacks direct test | Add before acceptance |
| Background shutdown failure with no later caller | Current callback retrieves and silences task exception | Select explicit observability policy |
| Retry after authoritative shutdown failure | Different ownership model | Separate design decision |
| Full macOS/Windows acceptance after repaired head | Current CI run cancelled with mixed unrelated results | Fresh exact-head ordinary gate |

## Exact execution and receipts

| Repository/head | Command or workflow | Platform/environment | Result | Evidence class |
| --- | --- | --- | --- | --- |
| Negative reproduction head | Workflow `30492906544` | Python 3.10 and 3.14, Ubuntu | Intended assertion failed; poisoned retry confirmed | `target-executed` |
| `dbbc8834acd69dc1f7f122ba1d3f49360565e7ef` | Repository CI `30497487411` | Multi-platform Python matrix | Candidate tests passed in inspected jobs; overall run cancelled and two unrelated Windows Chromium jobs had failed earlier | incomplete gate |

## Current disposition and desk routing

- Finding state: `research-active`
- Review disposition: `REPAIR + EXECUTE`
- Review Queue entry: #213
- Delivery lane: retain as `D1` only as a bounded repair/execution item, never as land-ready
- Exact next transition: add the three missing lifecycle/observability controls, then run fresh ordinary CI at the new head
- Clearing condition: repaired exact head, complete-diff review, and current repository gate
- User decision requested: choose the background-failure observability policy if the implementation team cannot establish one from project convention

## References

- https://github.com/teamleaderleo/fieldwork/issues/149
- https://github.com/teamleaderleo/playwright-python/pull/3
- https://docs.python.org/3/library/asyncio-task.html#shielding-from-cancellation
- Workflow `30492906544`
- CI run `30497487411`
