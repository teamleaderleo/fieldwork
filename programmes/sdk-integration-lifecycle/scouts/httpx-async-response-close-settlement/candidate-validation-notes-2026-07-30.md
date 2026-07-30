# HTTPX async response close candidate validation notes

Date: `2026-07-30`

Fieldwork issue: #171

Fieldwork scout PR: #173

Owned fork PR: `teamleaderleo/httpx#1`

Exact fork head: `89c1a6e1a3c31669e1f95cbb56add0148ee59035`

Pinned fork base: `b5addb64f0161ff6bfe94c124ef76f6a1fba5254`

Evidence class: `target-test-prepared`

Upstream contact authorized: `false`

## Candidate shape

The current fork remains a patch-applied experiment, not a direct production-source branch.

It contains four files:

1. exact source patch for response close ownership and elapsed ordering;
2. eleven backend-neutral response/state regressions;
3. one default-transport pool-slot recovery integration control;
4. a read-only Python 3.9/3.13 workflow.

## Self-review additions

The initial seven-test matrix was expanded after review to cover:

- entry with cancellation already active;
- repeated successful close idempotence;
- cancelled `AsyncClient.stream()` context exit;
- elapsed remaining unavailable after a failed close;
- real default-transport pool-slot recovery.

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

- Fieldwork close-settlement workflow: `30502260929` — queued;
- repository Test Suite: `30502260922` — queued.

No pass or failure is claimed yet.

## Adjacent lane

Fieldwork #177 records client-level shutdown separately. `Client.close()`, `AsyncClient.aclose()`, and context exits publish `ClientState.CLOSED` before the main transport and mounted transports settle. That is a multi-owner teardown policy and must not be folded into the one-response candidate.

## Next disposition gate

Do not promote the fork candidate until:

- the exact patch applies;
- Python 3.9 and 3.13 pass under asyncio and Trio;
- adjacent response/client controls pass;
- Ruff, Mypy, and `git diff --check` pass;
- the default-transport pool control passes;
- complete-diff review finds no public-state, pickle, or cancellation regression.

No upstream interaction occurred.
