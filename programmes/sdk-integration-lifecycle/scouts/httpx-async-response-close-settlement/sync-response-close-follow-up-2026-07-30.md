# HTTPX synchronous response close follow-up

Date: `2026-07-30`

Parent scout: #171

Candidate issue: #185

Owned fork characterization: `teamleaderleo/httpx#2`

Exact fork head: `414d64b2726c381caad6d3b53658b683e9858d2d`

Pinned source: `b5addb64f0161ff6bfe94c124ef76f6a1fba5254`

Released package executed: `httpx==0.28.1`

Python: `3.13.5`

Upstream contact authorized: `false`

## In simple words

The synchronous response path has the same early-completion publication shape as the asynchronous path, but a different ownership problem.

`Response.close()` sets `is_closed` before calling the underlying stream's `close()`. If that stream close raises, the response remains publicly terminal and a later `close()` does not retry cleanup.

## Executed release probe

The retained `sync_close_probe.py` uses a public `SyncByteStream` whose first close raises and whose second close would succeed.

Observed:

```json
{
  "after_first_failure": {
    "close_calls": 1,
    "error": "RuntimeError: sync close failed",
    "response_is_closed": true,
    "stream_cleaned": false
  },
  "after_retry": {
    "close_calls": 1,
    "response_is_closed": true,
    "stream_cleaned": false
  }
}
```

The second public close did not re-enter the stream.

Evidence class: `target-executed` for the released public response state.

## Why this is separate from async response close

Async #171 must define:

- cancellation ownership;
- concurrent task waiters;
- backend-neutral asyncio and Trio behavior;
- whether cleanup continues or retry ownership remains with callers.

Sync #185 must define:

- ordinary failure retry;
- whether body iteration remains blocked after a failed attempt;
- whether two-thread close calls are supported, serialized, or explicitly outside the contract;
- whether sync and async may expose different meanings for `is_closed`.

A shared public invariant is still desirable: `is_closed == True` should not mean only that close was entered.

## Fork characterization

HTTPX PR #2 contains no source repair.

Its focused regression records:

1. current failed-close state is terminal and non-retryable;
2. the desired retryable completion contract is a strict expected failure;
3. body iteration remains blocked after the failed attempt;
4. a `CloseError` retains request context;
5. repeated successful close remains idempotent.

The read-only workflow runs Python 3.9 and 3.13, adjacent response-close controls, Ruff, Mypy, and `git diff --check`.

Exact-head runs:

- focused sync characterization `30503934531` — queued;
- repository Test Suite `30503934542` — queued.

No passing or failing target receipt is claimed yet.

## Duplicate and history check

Targeted open, closed, and pull-request searches found no matching current HTTPX record for synchronous close failure leaving response state terminal and preventing retry.

Historical work making close errors visible remains relevant precedent, but does not settle retry or completion state.

## Correctness questions

A later repair should answer all of these explicitly:

- Does a failed close remain retryable?
- Is a stream close operation guaranteed to be safe to retry, or must retry be limited to transports that report incomplete cleanup?
- Does close-started state permanently block body reads even when `is_closed` remains false?
- Is response close expected to be thread-safe?
- Should sync and async use one shared private close-started flag?
- Does pickling discard all transient attempt state and restore a terminal unattached response?

## Boundary

This lane does not change HTTPX production source and does not broaden async PR #1.

Client-level teardown across the main transport and mounted proxies remains separately owned by #177.

No upstream interaction occurred.
