# HTTPX async response close settlement

State: `source-and-release-confirmed`

Fieldwork issue: #171

Programme: #13

Target: `encode/httpx`

Pinned current source: `b5addb64f0161ff6bfe94c124ef76f6a1fba5254`

Pinned released package: `httpx==0.28.1`

Upstream contact authorized: `false`

## In simple words

HTTPX says an asynchronous response is closed as soon as close starts, not when connection-release cleanup finishes.

If that cleanup is cancelled or raises, later callers see the closed flag and return without retrying. A concurrent caller can also return successfully while the first close is still blocked. The public state and the transport lifecycle therefore disagree.

## Source map

At the pinned current source, [`Response.aclose()`](https://redirect.github.com/encode/httpx/blob/b5addb64f0161ff6bfe94c124ef76f6a1fba5254/httpx/_models.py#L1070-L1081) sets `is_closed = True` before awaiting the stream:

```python
if not self.is_closed:
    self.is_closed = True
    await self.stream.aclose()
```

[`AsyncClient.stream()`](https://redirect.github.com/encode/httpx/blob/b5addb64f0161ff6bfe94c124ef76f6a1fba5254/httpx/_client.py#L1539-L1589) relies on `await response.aclose()` in its `finally` block.

The bound response stream sets elapsed time before awaiting underlying close, and the [default async transport](https://redirect.github.com/encode/httpx/blob/b5addb64f0161ff6bfe94c124ef76f6a1fba5254/httpx/_transports/default.py#L257-L269) forwards close into HTTPCore. Closing is therefore part of transport and connection-pool ownership, not only local response bookkeeping.

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

The probe covers three cases.

### Caller cancellation

The first close enters stream cleanup and is cancelled. HTTPX immediately reports `response.is_closed == True`. A later close returns without re-entering the stream, so cleanup remains incomplete.

### Underlying close failure

The stream's first close raises a concrete error. The error is observable, but the response remains marked closed. A later close does not retry the stream.

### Concurrent close callers

The first caller blocks inside stream cleanup. A second `response.aclose()` returns successfully while the first operation is still pending and the stream is not cleaned.

The retained output is `probe.output.json`.

## Strongest supported conclusion

For both the released package and current pinned source, `is_closed` means that response close was entered. It does not reliably mean that underlying stream close completed.

This creates three observable lifecycle gaps:

1. cancellation can strand cleanup behind a terminal public flag;
2. a close error is non-retryable through the response API;
3. concurrent callers do not join authoritative close completion.

The probe does not yet prove a real HTTPCore connection remains permanently leased. That requires target integration against the default transport and pool.

## Historical context and duplicate check

No matching current issue or pull request was found for cancelled or failed `Response.aclose()` leaving response state terminal and cleanup non-retryable.

Historical [PR #1465](https://redirect.github.com/encode/httpx/pull/1465) deliberately made close exceptions observable. That established that close can fail at the public boundary, but it did not define retryable or completed state after failure.

Historical [PR #1355](https://redirect.github.com/encode/httpx/pull/1355) explored removing response close-state tracking as part of a larger breaking request-context redesign. It is not a current repair candidate.

## Candidate invariants

A completed close call should provide one of two explicit contracts:

- **completion contract:** return only after the authoritative underlying close operation settles; or
- **attempt contract:** cancellation or failure leaves the response observably retryable.

In either contract, `is_closed == True` should mean cleanup completed, not merely that one caller entered close.

Concurrent callers should not return success while authoritative cleanup is still pending.

## Design options

### Set closed after successful cleanup

Await the stream first, then set `is_closed = True`.

Advantages:

- small change;
- failure and cancellation naturally leave retry ownership;
- public flag reflects completion.

Risks:

- two concurrent callers can invoke underlying close concurrently;
- a non-idempotent transport close may race;
- elapsed time publication still needs completion ordering.

### Shared close task

Create one authoritative close task and let every caller await it, potentially through cancellation shielding.

Advantages:

- one underlying close operation;
- concurrent and later callers share success or failure;
- caller cancellation can be separated from cleanup cancellation.

Risks:

- background failure must remain observable when the initiating caller is cancelled;
- task creation binds behavior to an active event loop;
- policy is needed for whether a failed shared task is retryable or permanently retained.

### Explicit close state machine

Track open, closing, closed, and failed/retryable states.

Advantages:

- clearest lifecycle contract;
- can distinguish caller cancellation from transport failure;
- can support controlled retry.

Risks:

- largest internal change;
- compatibility implications for `is_closed` and repeated close calls.

## Required target controls

1. cancellation during stream close followed by retry;
2. transport close error followed by retry;
3. two concurrent close callers;
4. cancellation of one waiter while another remains;
5. `AsyncClient.stream()` context exit;
6. read-to-completion automatic close;
7. default HTTPCore connection release and subsequent reuse;
8. repeated successful close;
9. elapsed time publication only after authoritative close completion;
10. sync `Response.close()` exception ordering review.

## Current disposition

Promote as a distinct lifecycle candidate and prepare target-native tests before selecting an implementation.

The smallest source change—setting `is_closed` after the await—fixes retry state but does not solve concurrent close ownership. A complete decision should compare it against a shared operation rather than assuming one boolean reorder is sufficient.

## Evidence classification

- current source and history: `source-read`;
- installed released public API probe: `target-executed` for response-state semantics;
- default transport and connection-pool consequence: unexecuted integration gate;
- candidate implementation: none.

## Boundaries

- no public upstream write or contact;
- no live network or credential use;
- no claim that every interrupted close leaks a socket;
- no fix is described as upstream-ready.
