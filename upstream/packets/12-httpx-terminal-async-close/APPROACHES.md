# Approaches — Unit 12 terminal async-response close

## Decision

Selected:

1. terminal outcome-unknown after escaped arbitrary cleanup;
2. inherited close-context stack for cycle detection;
3. pre-cleanup elapsed sampling with post-success publication.

This combination passed the exact Python 3.9/3.13 asyncio/Trio controls, complete HTTPX gates, and 100% coverage.

## Decision criteria

1. Arbitrary delegated cleanup runs at most once after admission.
2. The initiating caller receives its original escaped exception or cancellation.
3. Observers receive fresh bounded errors without sharing traceback-bearing exception objects.
4. Reads remain blocked once close begins.
5. Direct, descendant, and nested close cycles return promptly.
6. Unrelated callers retain ordinary waiter settlement.
7. Context cleanup is reliable under success, failure, and cancellation.
8. Successful elapsed preserves the pre-cleanup measurement boundary.
9. Failed cleanup publishes no elapsed value.
10. The source diff stays limited to HTTPX response close and its regressions.

## Selected approach

### Terminal outcome-unknown

The existing selected source design remains intact:

- one admitted delegated cleanup attempt;
- original owner failure/cancellation re-raised;
- terminal failure bit after escaped cleanup;
- fresh neutral `CloseError` instances for later observers;
- no retained owner exception or arbitrary traceback graph;
- read barrier once close starts;
- `is_closed` published only after cleanup succeeds.

### Inherited close-context stack

A module-level `contextvars.ContextVar` stores a tuple of active `_AsyncCloseState` markers.

Owner path:

1. create and publish the active close state;
2. push that state onto the inherited context stack;
3. invoke arbitrary stream cleanup;
4. publish success or terminal failure and wake waiters;
5. reset the context token in `finally`.

Waiter path:

- if the target state appears in the inherited stack, raise a prompt request-associated `CloseError` instead of waiting;
- otherwise wait on the state event and follow the established success/failure settlement.

Why a stack:

- direct owner -> same response is detected;
- owner -> descendant task -> same response is detected because context propagates;
- outer response -> inner response -> outer response is detected because the outer marker remains below the inner marker;
- unrelated callers created outside cleanup do not inherit the marker.

Retention boundary:

- the marker contains an event and failure bit only;
- it retains no response, task, request, or escaped exception;
- a descendant that outlives cleanup may retain only the lightweight marker until that task exits.

### Elapsed sample before cleanup, publish after success

`BoundAsyncStream.aclose()`:

1. samples `time.perf_counter() - start`;
2. awaits delegated stream cleanup;
3. assigns the saved sample to `response.elapsed` only after success.

This restores the previous measurement boundary without publishing elapsed after failed cleanup.

## Executed losing approaches

### Generic retry after escaped cleanup

Result: a commit-then-raise stream executed cleanup and its irreversible effect twice.

Why rejected: `AsyncByteStream` has no general idempotency guarantee.

### One shared terminal exception object

Result: concurrent/repeated callers mutated one exception's traceback state.

Why rejected: exception objects are not safe durable settlement records.

### Retain the owner's exception as observer cause

Result: the response retained the arbitrary traceback graph and delegated frame locals.

Why rejected: unbounded application-object retention.

### Publish `is_closed` before delegated cleanup

Why rejected: reports successful completion before cleanup and hides uncertainty after failure.

### Event state with no owner provenance

Exact clean source result:

```text
requestless direct re-entry: timeout
request-bound direct re-entry: timeout
caught re-entry with external waiter: timeout
```

Why rejected: the owner can wait on the event only it can settle.

### Exact task-ID detection

The first repair stored `anyio.get_current_task().id` and passed the direct controls.

A stronger stream created a child task, asked the child to close the same response, and awaited the child task group. The child had a different task ID, followed the external-waiter path, and waited for the owner event while the owner waited for the child.

Result:

```text
1 failed in 0.43s
TimeoutError
```

Why rejected: task identity does not represent inherited operation ownership.

Useful retained lesson: the cycle boundary is dynamic close context, not one task object.

### One current ContextVar marker

Plausible but rejected in favor of a stack.

Why: a single marker would cover direct and descendant self-re-entry but lose outer ancestry during nested response cleanup. The tuple stack covers outer -> inner -> outer cycles with little additional state.

### Spawn an authoritative cleanup task

Why rejected for this unit:

- widens task lifetime and orphan-cleanup policy;
- changes caller cancellation semantics;
- requires exception retrieval and shutdown ownership;
- unnecessary after inherited context solved the demonstrated cycles.

### Replace all close state with an enum

Why deferred:

- potentially clearer long-term representation;
- substantially larger rewrite and serialization review;
- current narrow repair is fully covered and race-compatible.

### Document re-entry as unsupported

Why rejected:

- public extension code would retain a silent indefinite wait;
- prompt enforcement is small and backend-neutral.

### Sample elapsed after delegated cleanup

Exact deterministic result: `10.0` seconds instead of the prior `2.0` boundary.

Why rejected: fixing failed publication silently changed successful elapsed semantics.

## Rejected easy answers

### Shield cleanup indefinitely

Arbitrary user cleanup may never finish. HTTPX has no generic deadline or orphan-retirement owner for this boundary.

### Copy or stringify arbitrary exceptions

User-defined conversion can execute code, fail, leak data, or retain application state. The selected observer error is bounded and neutral.

### Treat an old green suite as sufficient

The old suite omitted direct re-entry, descendant re-entry, nested cycles, and successful elapsed-boundary controls. The new discriminators changed the design twice before the final green matrix.

## Exact final evidence

Run `30752805069`:

- Python 3.9 focused asyncio/Trio: passed;
- Python 3.13 focused asyncio/Trio: passed;
- exact six-file fence: passed;
- Ruff format and lint: passed;
- mypy: passed;
- package/docs: passed;
- complete suite: `1445 passed, 1 skipped`;
- coverage: `8210/8210`, 100%.

## Deferred adjacent work

- synchronous response close;
- HTTPCore HTTP/1.1 and HTTP/2 retirement;
- same-socket and capacity behavior;
- client-wide multi-transport shutdown;
- broader public response-state redesign.

## Decision history

| Date | Decision | Reason |
| --- | --- | --- |
| 2026-07-30 | reject generic retry | committed cleanup duplicated |
| 2026-07-31 | select terminal unknown and fresh neutral observers | preserves owner diagnostics without duplicate effects or shared exception state |
| 2026-07-31 | drop retained owner exception | arbitrary traceback graph retention |
| 2026-07-31 | preserve pre-cleanup elapsed sample | avoid successful semantic drift |
| 2026-08-01 | require re-entry repair | exact clean source timed out |
| 2026-08-01 | provisionally select task ID | direct local controls passed |
| 2026-08-02 | reject task ID | descendant-task cycle timed out |
| 2026-08-02 | select inherited ContextVar stack | direct, descendant, nested, and external-waiter controls passed across Python 3.9/3.13 and asyncio/Trio |
| 2026-08-02 | accept complete repair diff | static checks, package/docs, 1,445 tests, and 100% coverage passed |
