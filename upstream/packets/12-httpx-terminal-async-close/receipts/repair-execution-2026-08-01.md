# Unit 12 repair execution receipt — 2026-08-01

## In simple words

The current HTTPX source files were reconstructed locally to their exact Git blob hashes. New target tests then proved two defects in the current candidate: same-task re-entry times out, and successful elapsed includes delegated cleanup latency.

A retained patch adds exact owner-task detection and restores pre-cleanup elapsed sampling with publication after success. The same five tests pass against the repaired local package.

## Identity

- Upstream base: `b5addb64f0161ff6bfe94c124ef76f6a1fba5254`
- Current source head: `18256f10d1b306bdf87a1bab24b214c15839147b`
- Current `_models.py` blob: `3ccb5290ceb95d96e24047bcec2897c52de16176`
- Current `_client.py` blob: `79934d050cd77414fb6f9c1024f42f6029c924e0`
- Repair patch: [`../patches/0001-fix-reentrant-close-and-elapsed-sampling.patch`](../patches/0001-fix-reentrant-close-and-elapsed-sampling.patch)
- Python: `3.13.5`
- AnyIO: `4.13.0`
- Backend: `asyncio`
- Network: unavailable
- Public upstream interaction: none

## Reconstruction method

1. Copy the installed `httpx==0.28.1` package.
2. Apply the four upstream source-line changes between tag `0.28.1` and base `b5addb64...`:
   - three `an sync` → `a sync` message corrections in `_models.py`;
   - one equivalent correction in `_client.py`.
3. Apply PR #6's current production changes.
4. Compute Git blob hashes.

Result:

```text
httpx/_models.py 3ccb5290ceb95d96e24047bcec2897c52de16176
httpx/_client.py 79934d050cd77414fb6f9c1024f42f6029c924e0
```

Both hashes match GitHub at `18256f10...`.

## Current-source discriminator run

Command:

```text
PYTHONPATH=/tmp/httpx-current pytest -q \
  tests/models/test_async_response_close_reentry.py \
  tests/client/test_async_client_terminal_close_elapsed.py
```

Result:

```text
FFF.F                                                                    [100%]
4 failed, 1 passed in 3.28s
```

Classified failures:

- requestless re-entry: `TimeoutError` after the inner call waited on `state.event`;
- request-bound re-entry: same;
- stream-caught re-entry with external waiter: same owner/event cycle;
- successful elapsed: `10.0` seconds instead of expected pre-cleanup `2.0` seconds.

Direct reduced output:

```text
REENTRY_TIMEOUT 1 False True
ELAPSED_SECONDS 10.0
```

## Repair

Production changes:

```text
_AsyncCloseState.owner_task_id = anyio.get_current_task().id
```

Before an existing-state caller waits:

```text
if state.owner_task_id == anyio.get_current_task().id:
    raise CloseError(...)
```

Elapsed ordering:

```text
elapsed = time.perf_counter() - self._start
await self._stream.aclose()
self._response.elapsed = datetime.timedelta(seconds=elapsed)
```

Tests added or updated:

- requestless escaping re-entry;
- request-bound escaping re-entry;
- caught re-entry with unrelated waiter;
- existing failed elapsed publication;
- successful blocking cleanup excludes cleanup latency.

## Repaired run

Command:

```text
PYTHONPATH=/tmp/httpx-repaired pytest -q \
  tests/models/test_async_response_close_reentry.py \
  tests/client/test_async_client_terminal_close_elapsed.py
```

Result:

```text
.....                                                                    [100%]
5 passed in 0.12s
```

Syntax command:

```text
python -m py_compile \
  /tmp/httpx-repaired/httpx/_models.py \
  /tmp/httpx-repaired/httpx/_client.py
```

Result: passed.

## Limits

- The reconstructed production files are exact; the full repository checkout was unavailable because the container had no DNS/network access.
- The repaired source is local plus a retained patch, not a GitHub source commit.
- Trio is absent locally.
- Python 3.9 is unexecuted for the repair.
- `scripts/check`, complete tests, coverage, build, and docs remain unexecuted for the repair.
- Task-ID detection covers the exact same-task cycle. Descendant-task provenance remains a review question.

## Disposition

`REPAIR`

Clearing condition: apply the retained patch to the canonical target branch, verify the six-file fence, and run the complete target matrix at one exact head.
