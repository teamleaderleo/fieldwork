# Unit 08 review and human inspection guide

## Review target

- Canonical PR: [`teamleaderleo/playwright-python#8`](https://github.com/teamleaderleo/playwright-python/pull/8)
- Proposed title: `fix(async): share shutdown completion across callers`
- Public base / current upstream `main`: `3b7c24c3e67dc84f7b0eddd0c5fd2ca685705021`
- Clean source head: `4cfc6a9e3e3a5c6dcab04015a1210ce6924d4c27`
- Compare: 7 commits, exactly 3 files, 469 additions, 6 deletions
- Pre-review disposition: `ACCEPT`
- Public upstream contact authorized: `no`

## Complete-diff fence

Review only:

1. `playwright/async_api/_context_manager.py`;
2. `tests/async/test_async_stop_cancellation.py`;
3. `tests/async/test_async_stop_exit_contract.py`.

No workflow, generated API, dependency, packaging, Docker, or configuration file is present on the source branch. Historical and execution-only PRs are evidence carriers, not merge candidates.

## Governing invariant

Shutdown has one authoritative terminal operation:

- the first caller creates it before suspension;
- cancellation belongs to a waiter, not to cleanup;
- concurrent and later callers join the same operation;
- success is idempotent;
- failure is stable and identical for every caller;
- an abandoned failure is reported once and remains joinable.

## Final production review

### Task creation and ownership

- `_stop_task` is assigned synchronously before the first await, so one event loop cannot create two tasks through ordinary interleaving.
- the task directly owns `Connection.stop_async()` and therefore preserves the existing request-stop → transport completion → connection cleanup ordering.
- the context manager does not duplicate cleanup knowledge or reset a guard after cancellation.

### Cancellation-safe join

The final code joins the task in two steps:

```python
await asyncio.wait({stop_task})
await stop_task
```

Across CPython 3.10 and 3.14 source, cancelling the task awaiting `asyncio.wait` removes the wait callback but does not cancel the supplied `stop_task`. Once the wait completes, the ordinary await returns or raises the authoritative task's exact terminal outcome.

This replaced `asyncio.shield`. The replacement is consequential: Python 3.14 causes a cancelled shielded waiter to install an automatic inner-task exception logger, which duplicated the candidate's intentional loop report.

### Failure observation

- the stop-task done callback retrieves and stores failure;
- `_stop_waiters` counts active joiners;
- a caller receiving failure marks it observed;
- zero waiters plus an unobserved failure schedules one deferred callback;
- a late waiter cancels the pending callback before joining;
- a post-report caller still receives the same original task exception;
- pending, observed, and reported flags prevent both silence and duplicate publication.

### Loop exception context

The fallback context is:

```python
{
    "message": "Playwright stop task failed",
    "exception": self._stop_failure,
    "task": self._stop_task,
}
```

Tests assert exact message, exact exception identity, exact authoritative-task identity, exactly one report, and stable failure for a later caller.

### Context-manager semantics

- body error waits for successful cleanup, then propagates;
- body cancellation waits until the shared cleanup completes, then propagates cancellation;
- cleanup failure takes precedence while preserving body error in `__context__`;
- direct `playwright.stop()` and `async with` share this path.

## Defects found and repaired during pre-review

### Test typing

Run `30691401327`, job `91346660311`, reached repository mypy and found the monkeypatch restoration used a broad annotated callable and lacked the narrow method-assignment suppression. Commit `b0509982c7cb7ef9cfeaa6a65225ec6e64a28b92` preserves the bound method's inferred coroutine type and restores only `# type: ignore[method-assign]`.

### Python 3.14 duplicate reporting

Run `30692014938`, job `91348287797`, passed pre-commit and all 33 cases on Python 3.10 and 3.12. Python 3.14 failed exactly three observability cases because the handler received:

1. `RuntimeError exception in shielded future` from CPython;
2. `Playwright stop task failed` from the candidate.

Commit `4cfc6a9e3e3a5c6dcab04015a1210ce6924d4c27` replaces the shield join with `asyncio.wait` and removes that duplicate-report path.

## Exact final receipt

Workflow `30692313951`, job `91349092242`, Ubuntu 24.04 ARM:

- exact base checkout passed;
- wheel build passed on Python 3.10.20, 3.12.13, and 3.14.6;
- full repository pre-commit passed, including mypy and pyright;
- Python 3.10: `33 passed, 2 warnings in 10.10s`;
- Python 3.12: `33 passed, 2 warnings in 10.09s`;
- Python 3.14: `33 passed, 2 warnings in 10.08s`;
- reruns disabled;
- tracked diff hygiene passed.

The warnings are unrelated pyOpenSSL deprecations.

## Claim-scoped judgment

| Claim | Judgment |
| --- | --- |
| upstream boolean loses joinable completion after caller cancellation | supported by deterministic Python 3.10/3.14 negative reproduction |
| one authoritative task prevents duplicate cleanup ownership | supported by source and final three-version execution |
| waiter cancellation does not cancel cleanup | supported by `asyncio.wait` semantics and final controls |
| terminal success/failure remains stable for later callers | supported by final controls |
| abandoned failure is reported exactly once | supported by baseline failure, Python 3.14 compatibility failure, and final pass |
| context-manager precedence remains coherent | supported by final controls |
| clean scope is limited to intended files | supported by exact compare and PR metadata |
| generated or dependency changes are required | no |

## Human reviewer questions

1. Is explicit loop reporting the desired policy for a retained failed cleanup task with no active waiter?
2. Is `Playwright stop task failed` the right public-facing diagnostic message?
3. Should a caller arriving after fallback publication still receive the same failure? Current design and tests say yes.
4. Is one event-loop turn an appropriate grace period for a late observer? Current design and tests say yes.
5. Should the seven clean commits be squashed or rebuilt into one target-style commit before any authorized submission?
6. Should startup-task ownership and bounded driver-process shutdown become separate units?

## Broader findings, excluded from this diff

- Public issue `microsoft/playwright-python#3132` records a failed async startup path that can leave `Connection.init` exception unretrieved. It requires separate reproduction/repair work.
- Java bounds driver-process shutdown to 30 seconds; Python's pipe transport waits for process communication without an explicit bound. Public issue #2633 is adjacent historical evidence, but no current Python timeout change is justified without a dedicated deterministic test.
- Node and .NET both model shutdown around one terminal completion owner, supporting this design direction.

## Pre-review disposition

`ACCEPT`.

No further source change is requested by the completed pre-review. The final human decision and any authorization for public upstream interaction remain outside this packet's authority.
