# Upstash Box cancellation receipt target materialization

Issue: #388  
Parent comparison: PR #372  
Exact target: `upstash/box@b55d832d6e3ae0156e32d21ea3863e231dfff9cd`  
State: `target-materialization-active`  
Upstream contact authorized: no

## In simple words

The current TypeScript and Python SDKs both suppress cancellation endpoint errors and then set the public run status to `cancelled`. That turns a local request attempt into a confirmed remote outcome. Concurrent TypeScript and async Python callers also have no shared request owner.

This carrier tests a compatibility-preserving source repair across all three public clients:

- TypeScript;
- async Python, which is the Python source of truth;
- generated synchronous Python.

It uses mocked/local requests only. It never calls the hosted Box API.

## Exact source findings

### TypeScript

`Run.cancel()`:

1. aborts the local controller;
2. sends `POST /runs/<id>/cancel`;
3. suppresses every request failure;
4. assigns `status = "cancelled"`.

The method returns `Promise<void>`, and existing unit coverage expects the terminal assignment.

### Python

`AsyncRun.cancel()` performs the same request suppression and terminal assignment. `Run.cancel()` is mechanically generated from that async source.

The sync generator strips `async`/`await` and performs configured symbol replacements. It cannot mechanically convert `asyncio.Task` ownership into thread-safe sync ownership. The repository explicitly permits shared or fallback code for constructs that do not generate cleanly.

### Public parity

`PARITY.md` currently lists the false-terminal behavior as a mirrored quirk. Any source repair must update that contract and the old tests rather than leaving them as contradictory precedent.

## API comparison

### Shape 1 — change `cancel()` to return a receipt

Advantage: smallest public surface.

Declined for the candidate. TypeScript callers that store or implement `() => Promise<void>` can reject a `Promise<Receipt>` signature even though ordinary callers ignore returned values. Python type contracts also change from `None`.

### Shape 2 — keep `cancel()` void and expose only a settled property

Advantage: preserves the method signature.

Declined as the sole API. A property gives later observation but does not provide one obvious awaitable/requesting operation for concurrent callers.

### Shape 3 — add `requestCancel()` / `request_cancel()` and retain legacy `cancel()`

Selected for execution.

- `requestCancel()` / `request_cancel()` returns the immutable shared receipt;
- legacy `cancel()` delegates and discards it;
- existing return signatures remain unchanged;
- later callers join the settled attempt without replay;
- `Run.status` stays authoritative and unchanged until a server update arrives.

## Receipt contract

TypeScript:

```ts
type RunCancellationReceipt = Readonly<{
  requestState: "accepted" | "failed";
  outcomeState: "unknown";
  diagnostic?: "cancellation request failed";
}>;
```

Python uses a frozen dataclass with equivalent snake-case fields.

`accepted` means the local HTTP request completed successfully. It does not mean the remote run reached a terminal cancelled state. A failed request retains fixed diagnostic prose and no provider response text.

## Runtime ownership

### TypeScript

One private Promise is assigned before the request begins. Every caller receives the same Promise and receipt object. Promise consumers cannot cancel the shared request by abandoning their own wait.

### Async Python

One private `asyncio.Task` owns the request. Every waiter uses `asyncio.shield`, so cancelling one waiter does not cancel the shared task or another waiter.

### Sync Python

One thread-safe `Future` and lock select a single request owner. Other threads wait on the same result. The generated client references the sync coordinator through one generator symbol replacement.

## Controls

The carrier injects target-native tests for:

- one request under concurrent TypeScript callers;
- one request under concurrent async Python callers;
- survival after one async waiter is cancelled;
- one request under concurrent sync threads;
- immutable/frozen receipt identity;
- fixed failure prose without provider detail;
- no false terminal status;
- later authoritative status replacement;
- no replay for later callers;
- legacy void/None return behavior;
- deterministic sync generation;
- JavaScript build, formatting, focused and full tests;
- Python focused/full tests, parity, Ruff, MyPy, and generated-sync diff.

## Candidate files in exact target

The transformation is expected to touch:

- `packages/sdk/src/client.ts`;
- `packages/sdk/src/types.ts`;
- `packages/sdk/src/index.ts`;
- `packages/sdk/src/__tests__/run.test.ts`;
- `packages/python-sdk/upstash_box/types.py`;
- `packages/python-sdk/upstash_box/_cancellation.py`;
- `packages/python-sdk/upstash_box/_async/client.py`;
- generated `packages/python-sdk/upstash_box/_sync/client.py`;
- `packages/python-sdk/upstash_box/__init__.py`;
- `packages/python-sdk/scripts/generate_sync.py`;
- `packages/python-sdk/tests/_async/test_run.py`;
- `packages/python-sdk/PARITY.md`;
- injected Fieldwork target controls.

## Evidence boundary

A passing carrier would be target-executed evidence for exact public source, mocked request behavior, TypeScript/Python API compatibility, and repository-declared local gates. It would not establish hosted endpoint semantics, provider idempotency, server-side outcome truth, billing, production concurrency, or public maintainer acceptance.

The retained candidate diff is internal research. No public upstream pull request, issue comment, review, reaction, or backlink is authorized.
