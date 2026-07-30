# HTTPCore delegated response-close follow-up

Date: `2026-07-30`

Parent scout: #171  
Candidate lane: #227  
Owned characterization: `teamleaderleo/httpx#3`  
Exact current fork head: `0d9bbf8c8137102931d75fdf041980c67d22ab46`  
Pinned HTTPX base: `b5addb64f0161ff6bfe94c124ef76f6a1fba5254`  
Pinned HTTPCore source analysis: `10a658221deb38a4c5b16db55ab554b0bf731707`  
Upstream contact authorized: `false`

## Why this follow-up exists

The accepted HTTPX async response candidate establishes truthful wrapper completion when interruption occurs before the wrapped stream has completed cleanup.

That result does not automatically settle the next owner down the stack.

HTTPCore has separate HTTP/1.1 and HTTP/2 response byte-stream objects. Both set a private `_closed` flag before awaiting their connection or stream release operation. Once that private flag is set, another call to the same byte stream returns without re-entering release.

The correctness boundary is therefore layered:

```text
HTTPX Response.aclose ownership
  -> HTTPX bound stream
     -> HTTPCore response byte stream
        -> HTTP/1.1 connection release or HTTP/2 stream-capacity release
```

A truthful outer wrapper cannot retry work that an inner owner has already classified as terminal.

## Source ownership map

### HTTP/1.1

`HTTP11ConnectionByteStream.aclose()`:

1. checks `_closed`;
2. sets `_closed = True`;
3. enters the asynchronous `response_closed` trace scope;
4. awaits `AsyncHTTP11Connection._response_closed()`.

The delegated operation may:

- wait for the connection state lock;
- return the h11 connection to `IDLE` and start a new cycle;
- or await full network-stream close.

### HTTP/2

`HTTP2ConnectionByteStream.aclose()`:

1. checks `_closed`;
2. sets `_closed = True`;
3. enters the asynchronous `response_closed` trace scope;
4. awaits `AsyncHTTP2Connection._response_closed(stream_id)`.

The delegated operation:

- returns one max-concurrent-stream semaphore slot;
- removes the stream event queue;
- waits for the connection state lock;
- may move the connection to `IDLE`;
- and may close the connection after termination or stream-ID exhaustion.

Direct byte-stream close is not wrapped in HTTPCore's cancellation shield. Selected exception-handling paths do use the shield, so ordinary explicit close and cleanup-during-error currently have different cancellation ownership.

## Asynchronous trace callback boundary

HTTPCore awaits the request's asynchronous trace extension inside the `response_closed` scope.

Current behavior sets `_closed=True` before invoking the `response_closed.started` callback. If that callback calls and awaits the same byte stream's `aclose()`, the nested call returns immediately and the outer close can continue.

That current passing behavior is not evidence that early terminal publication is correct. It is an anti-regression constraint on one proposed repair:

```text
outer shared close operation P
  -> awaits trace callback Q
     -> callback awaits same close and receives P
```

Without explicit same-owner reentry handling, Q can wait for P while P waits for Q. An unrelated external caller still needs to join P, so suppressing every call during close would be overbroad.

The characterization therefore includes a bounded passing control for same-stream close from `response_closed.started`. A future shared-operation repair must preserve that control through provenance, typed reentry handling, different trace ordering, or another explicit contract.

## Prepared target characterization

HTTPX PR #3 adds backend-neutral tests against installed `httpcore==1.0.9`.

For both `HTTP11ConnectionByteStream` and `HTTP2ConnectionByteStream`, it records:

1. cancellation after delegated release begins, followed by a second close that does not re-enter release;
2. ordinary delegated release failure, followed by a second close that does not retry;
3. a second concurrent close caller returning before the first delegated release finishes;
4. a strict expected failure for retryable lower-layer completion;
5. a passing bounded trace-callback reentry control.

The concurrency control uses an explicit completion event rather than assuming one scheduler turn is sufficient. The trace control uses an operation watchdog so a future lifecycle cycle fails boundedly instead of hanging the suite.

The workflow runs Python 3.9 and 3.13 with AnyIO's asyncio and Trio backends, adjacent HTTPX response tests, Ruff, Mypy, and `git diff --check`.

Current exact-head runs:

- focused delegated-close workflow `30548021859` — queued at the last check;
- ordinary HTTPX Test Suite `30548021848` — queued at the last check.

No target result is claimed until those exact tests execute.

## Contract choices

### 1. Shield delegated release

The caller may receive cancellation only after cleanup completes.

Advantages:

- one underlying attempt completes authoritatively;
- no retry or duplicate-release decision;
- matches selected HTTPCore exception-cleanup paths.

Risks:

- cancellation latency can become unbounded on a broken transport, callback, or lock;
- caller intent and operation completion become coupled;
- late cleanup failure still needs observation.

### 2. Publish lower-layer completion only after success

Keep `_closed` false until delegated release succeeds, with a separate permanent body-consumption barrier if needed.

Advantages:

- explicit retry remains possible;
- private state matches actual release completion.

Risks:

- a second caller can invoke destructive release concurrently without a separate owner mechanism;
- HTTP/2 semaphore/event cleanup may be only partly complete;
- retry safety differs by failure point.

### 3. Shared lower-layer release operation

One close attempt owns the release and other callers join it. Caller cancellation does not necessarily cancel the operation.

Advantages:

- truthful completion and concurrent ownership;
- can separate waiter cancellation from authoritative release.

Risks:

- backend-neutral operation ownership must be designed;
- failure retention and later retry policy must be explicit;
- trace callbacks and other same-owner reentry can form owner/child promise cycles;
- provenance must distinguish self-reentry from unrelated external joiners.

### 4. Explicit retirement by another owner

Treat response-byte-stream close interruption as abandoning reuse, while a connection-pool or connection owner guarantees eventual retirement.

Advantages:

- avoids retrying partially completed stream release;
- may be appropriate for damaged protocol state.

Risks:

- requires a real durable retirement owner;
- public response completion must not falsely imply release already happened;
- pool capacity may remain unavailable until retirement settles.

## Protocol-specific questions

### HTTP/1.1

- Did cancellation occur before or after the h11 state reached a reusable cycle?
- Is connection retirement safer than retry once state transition begins?
- Can the exact socket identity be observed before and after a successful retry?
- What happens if cancellation lands in the trace callback, while waiting for `_state_lock`, or during network close?

### HTTP/2

- Was the max-stream semaphore slot returned before cancellation?
- Was the stream removed from `_events`?
- Can retry double-release the semaphore or delete the stream twice?
- Does interrupted cleanup reduce future stream capacity while leaving the connection otherwise active?
- Should an interrupted stream close send a reset, merely forget local state, or retire the full connection?
- Can trace-callback reentry occur before any stream-capacity cleanup starts?

## Evidence and non-claims

Current evidence:

- HTTPCore ownership, trace ordering, and close publication: `source-read`;
- HTTPX pre-delegation pool-slot recovery: `integration-executed` under #171;
- HTTPCore characterization: `target-test-prepared` on HTTPX PR #3.

Not established:

- permanent socket leakage;
- permanent HTTP/2 capacity loss;
- same-socket reuse;
- safe universal retry;
- a selected shielding or ownership repair;
- released trace-callback reentry impact beyond the prepared target control;
- direct HTTPCore source modification.

## Breadcrumbs

1. Process PR #3 exact-head runs and retain the exact assertions reached.
2. Preserve the trace-callback passing control in every shared-operation design.
3. Add real HTTP/1.1 instrumentation after the synthetic byte-stream result.
4. Add real HTTP/2 capacity/event-map instrumentation separately.
5. Inject interruption at named trace, lock, release, and network-close transitions.
6. Compare explicit close with HTTPCore's shielded error-cleanup paths.
7. Do not broaden HTTPX PR #1; it has an accepted wrapper-level contract and needs a clean direct source branch.
8. Obtain an independent disposition before selecting shield, retry, shared ownership, or retirement.

Public upstream remains read-only. No upstream interaction occurred.
