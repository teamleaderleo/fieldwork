# HTTPX async response close candidate validation notes

Date: `2026-07-30`

Fieldwork issue: #171

Fieldwork scout PR: #173

Owned fork PR: `teamleaderleo/httpx#1`

Exact fork head: `f601c2981d1bf2c9d036b8ce91e46fa11529cd87`

Pinned fork base: `b5addb64f0161ff6bfe94c124ef76f6a1fba5254`

Evidence class: `target-test-prepared`

Upstream contact authorized: `false`

## Candidate shape

The current fork remains a patch-applied experiment, not a direct production-source branch.

It contains six files:

1. exact source patch for response close ownership and elapsed ordering;
2. eleven backend-neutral response/state regressions;
3. one focused control-flow ownership regression;
4. one in-progress pickle-state regression;
5. one default-transport pool-slot recovery integration control;
6. a read-only Python 3.9/3.13 workflow.

## Self-review findings and repairs

### Patch application metadata

The first staged source patch had inconsistent unified-diff hunk counts and downstream new-line offsets. The code proposal was readable, but `git apply --check` would have rejected the artifact before compilation or tests.

The current patch corrects:

- the top-level helper hunk count;
- every later new-file line offset affected by that count;
- the final `Response.aclose()` old/new line counts.

This is a harness/transport repair. It supplies no product evidence until the exact patch applies in the target workflow.

### Control-flow exception ownership

The first candidate distinguished the active backend's cancellation class from every other `BaseException`. It therefore stored and replayed a non-cancellation control-flow signal such as `KeyboardInterrupt`, `SystemExit`, or another direct `BaseException` into callers waiting on the close attempt.

The repaired rule is:

- ordinary `Exception` failures are shared with current waiters;
- cancellation and other control-flow `BaseException` values remain owned by the interrupted caller;
- waiters are awakened and may take retry ownership rather than receiving a duplicated control-flow signal.

A dedicated concurrent owner/waiter test uses a synthetic `BaseException` subclass. The owner receives it once, the waiter retries the underlying stream close, and only successful retry publishes `is_closed`.

### Pickle-state ownership

`Response.__getstate__()` must not serialize the AnyIO event or an in-progress close-attempt object. `Response.__setstate__()` already restores responses as closed with an unattached stream.

The new test pickles a response while its underlying close is blocked and requires the restored response to be:

- publicly closed;
- marked close-started;
- free of transient attempt state;
- unable to resume body consumption.

The original response remains incomplete and retryable after its owner is cancelled. This separates serialization safety from the live response's close ownership.

## Earlier matrix additions

The initial seven-test matrix was expanded after review to cover:

- entry with cancellation already active;
- repeated successful close idempotence;
- cancelled `AsyncClient.stream()` context exit;
- elapsed remaining unavailable after a failed close;
- real default-transport pool-slot recovery;
- non-cancellation control-flow interruption remaining owner-scoped;
- serialization while close remains in progress.

The tests use AnyIO rather than `asyncio.Task`, so the same contract is exercised under asyncio and Trio.

## Default-transport control

The integration control uses the repository's local Uvicorn server and HTTPX's default transport with:

```python
httpx.Limits(max_connections=1, max_keepalive_connections=1)
httpx.Timeout(5.0, pool=0.2)
```

The first streaming response wraps its real bound transport stream with a deterministic close blocker.

1. First close enters the blocker.
2. Caller cancellation occurs before close delegates to HTTPCore.
3. Public response completion remains false.
4. Retry delegates to the real bound stream and completes.
5. A follow-up request succeeds through the one-slot pool.

This proves recovery of the pool slot for the tested interruption point. It does not prove same-socket reuse or every interruption point inside HTTPCore.

## Current execution state

Exact-head runs:

- Fieldwork close-settlement workflow: `30504179169` — queued;
- repository Test Suite: `30504179155` — queued.

All earlier queued receipts bind superseded heads. No pass or failure is claimed yet.

## Protocol review result

The current Fieldwork protocol split remains appropriate:

- PR #143 owns exact-head evidence and independent-review semantics;
- issue #160 / PR #161 own finish-line routing;
- issue #138 owns the future read-only evaluator.

The HTTPX node is a useful invalidation case: the released-package reproduction remains valid, while prepared candidates and queued receipts become stale whenever complete-diff review changes the patch, tests, or workflow.

Issue #138's HTTPX dogfood record and issue #87's human review record now separate async response, sync response, and client multi-transport ownership.

## Adjacent lanes

Fieldwork #185 records synchronous response close failure separately. The released sync path becomes terminal before stream cleanup succeeds and refuses public retry.

Fieldwork #177 records client-level shutdown separately. `Client.close()`, `AsyncClient.aclose()`, and context exits publish `ClientState.CLOSED` before the main transport and mounted transports settle. That is a multi-owner teardown policy and must not be folded into the one-response candidate.

## Next disposition gate

Do not promote the fork candidate until:

- the exact patch applies;
- Python 3.9 and 3.13 pass under asyncio and Trio;
- adjacent response/client controls pass;
- Ruff, Mypy, and `git diff --check` pass;
- the control-flow ownership regression passes;
- the pickle-state regression passes;
- the default-transport pool control passes;
- complete-diff review finds no public-state, serialization, cancellation, failure-sharing, or elapsed-ordering regression.

No upstream interaction occurred.
