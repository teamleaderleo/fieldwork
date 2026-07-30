# HTTPX async response close settlement

State: `candidate-validating`

Fieldwork issue: #171

Programme: #13

Target: `encode/httpx`

Pinned current source: `b5addb64f0161ff6bfe94c124ef76f6a1fba5254`

Pinned released package: `httpx==0.28.1`

Owned fork candidate: `teamleaderleo/httpx#1`

Owned fork head: `368431247a74f3768ef21993a9191eba85f8d6b6`

Adjacent client-shutdown candidate: #177

Upstream contact authorized: `false`

## In simple words

HTTPX says an asynchronous response is closed as soon as close starts, not when connection-release cleanup finishes.

If that cleanup is cancelled or raises, later callers see the closed flag and return without retrying. A concurrent caller can also return successfully while the first close is still blocked. The public state and the transport lifecycle therefore disagree.

The owned fork contains a draft experiment where one caller owns each close attempt, other callers wait for that attempt, cancellation leaves retry ownership, and only successful underlying cleanup publishes `is_closed == True`.

## Source map

At the pinned current source, [`Response.aclose()`](https://redirect.github.com/encode/httpx/blob/b5addb64f0161ff6bfe94c124ef76f6a1fba5254/httpx/_models.py#L1070-L1081) sets `is_closed = True` before awaiting the stream:

```python
if not self.is_closed:
    self.is_closed = True
    await self.stream.aclose()
```

[`AsyncClient.stream()`](https://redirect.github.com/encode/httpx/blob/b5addb64f0161ff6bfe94c124ef76f6a1fba5254/httpx/_client.py#L1539-L1589) relies on `await response.aclose()` in its `finally` block.

The bound response stream sets elapsed time before awaiting underlying close, and the [default async transport](https://redirect.github.com/encode/httpx/blob/b5addb64f0161ff6bfe94c124ef76f6a1fba5254/httpx/_transports/default.py#L257-L269) forwards close into HTTPCore. Closing is therefore part of transport and connection-pool ownership, not only local response bookkeeping.

The adjacent audit also found that sync and async client shutdown mark `ClientState.CLOSED` before closing the main transport and every mounted transport. That multi-owner problem is separated into #177 rather than expanding the response candidate.

## Executed release probe

`probe.py` was executed against:

- Python `3.13.5`;
- installed `httpx==0.28.1`;
- a custom public `AsyncByteStream` with deterministic close control;
- no network request.

Command:

```sh
python3 probe.py
```

The retained output is `probe.output.json`.

### Caller cancellation

The first close enters stream cleanup and is cancelled. HTTPX immediately reports `response.is_closed == True`. A later close returns without re-entering the stream, so cleanup remains incomplete.

### Underlying close failure

The stream's first close raises a concrete error. The error is observable, but the response remains marked closed. A later close does not retry the stream.

### Concurrent close callers

The first caller blocks inside stream cleanup. A second `response.aclose()` returns successfully while the first operation is still pending and the stream is not cleaned.

## Strongest supported conclusion

For both the released package and current pinned source, `is_closed` means that response close was entered. It does not reliably mean that underlying stream close completed.

This creates three observable lifecycle gaps:

1. cancellation can strand cleanup behind a terminal public flag;
2. a close error is non-retryable through the response API;
3. concurrent callers do not join authoritative close completion.

The release probe does not prove a real HTTPCore connection remains permanently leased. That requires target integration against the default transport and pool.

## Historical context and duplicate check

No matching current issue or pull request was found for cancelled or failed `Response.aclose()` leaving response state terminal and cleanup non-retryable.

Historical [PR #1465](https://redirect.github.com/encode/httpx/pull/1465) deliberately made close exceptions observable. That established that close can fail at the public boundary, but it did not define retryable or completed state after failure.

Historical [PR #1355](https://redirect.github.com/encode/httpx/pull/1355) explored removing response close-state tracking as part of a larger breaking request-context redesign. It is not a current repair candidate.

## Selected fork experiment

Draft fork PR: `teamleaderleo/httpx#1`

Branch: `fieldwork/171-async-response-close-settlement`

Exact head: `368431247a74f3768ef21993a9191eba85f8d6b6`

The branch stages an exact source patch rather than replacing the large core files through the connected editor. Its workflow is read-only: it applies the patch to a clean checkout, copies the focused regression into the repository test tree, and runs the matrix without committing or pushing.

### Per-attempt join point

The candidate uses an AnyIO event for one close attempt rather than an `asyncio.Task`.

- the first caller owns `stream.aclose()`;
- concurrent callers wait on that attempt;
- successful cleanup sets `is_closed` and releases waiters;
- ordinary close failure is shared with callers already waiting;
- a later explicit caller may retry after failure;
- active or pre-existing owner cancellation clears attempt ownership without publishing completion;
- cancelling a waiter does not cancel the owner.

This keeps the candidate backend-neutral for asyncio and Trio and avoids a detached background task whose failure could become unobserved.

### Close-started read barrier

Moving `is_closed` to completion time would otherwise create a window where body iteration could begin while close is already in progress.

The candidate therefore retains a separate private `close started` barrier. Once asynchronous close begins, new body iteration raises `StreamClosed` even if public `is_closed` remains false because cleanup has not completed. After cancellation or failure, the response is retryable for close but not reopened for body consumption.

### Elapsed completion ordering

The current `BoundAsyncStream` publishes `response.elapsed` before awaiting the underlying close. The candidate moves elapsed publication after successful underlying cleanup. Elapsed remains unavailable while close is pending and after a failed attempt, then becomes available after a successful retry.

## Focused regression matrix

The owned fork test covers:

1. active cancellation followed by successful retry;
2. already-cancelled entry followed by successful retry;
3. ordinary close failure followed by successful retry;
4. two concurrent close callers sharing one underlying attempt;
5. cancelling one waiter without cancelling the owner;
6. one ordinary failure being shared with current waiters;
7. body iteration remaining blocked after close starts and after a cancelled attempt;
8. repeated successful close remaining idempotent;
9. cancelled `AsyncClient.stream()` context exit leaving the response retryable;
10. elapsed remaining unavailable until underlying close completes;
11. elapsed remaining unavailable after failure until retry succeeds.

The workflow runs Python `3.9` and `3.13`. Every `pytest.mark.anyio` test runs through the repository's asyncio and Trio backends. It also runs adjacent response/client streaming controls, Ruff, Mypy, and `git diff --check` after applying the exact patch.

## Current validation state

Fork workflow `30501982281` and repository `Test Suite` run `30501982293` are queued on exact head `368431247a74f3768ef21993a9191eba85f8d6b6`.

No candidate pass is claimed yet.

## Remaining target controls

1. patch applies cleanly on the pinned fork base;
2. focused asyncio and Trio matrix passes on Python 3.9 and 3.13;
3. adjacent existing response/client streaming controls pass;
4. read-to-completion automatic close remains correct;
5. default HTTPCore connection release and subsequent reuse are exercised after interrupted close;
6. sync `Response.close()` exception ordering is characterized separately;
7. the final candidate is applied directly or retained explicitly as a patch experiment before any landing decision.

## Current disposition

Retain the per-attempt AnyIO join design as the leading fork experiment, not as an accepted fix.

A boolean reorder alone fixes retry state but allows duplicate underlying close calls. A permanent shared task provides stronger single-operation ownership but introduces backend/task-lifetime and unobserved-failure questions. The per-attempt event is the narrowest current design that serializes close, preserves caller cancellation, shares current-attempt outcomes, and permits controlled retry.

Promotion requires successful target execution and a real HTTPCore pool/reuse control.

## Evidence classification

- current source and history: `source-read`;
- installed released public API probe: `target-executed` for response-state semantics;
- owned fork implementation: `target-test-prepared`;
- fork execution: queued, not yet established;
- default transport and connection-pool consequence: unexecuted integration gate.

## Boundaries

- no public upstream write or contact;
- no live network or credential use in the release probe;
- no claim that every interrupted close leaks a socket;
- no fix is described as upstream-ready;
- the owned fork PR remains draft.