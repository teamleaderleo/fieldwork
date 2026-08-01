# Approaches — Unit 12 terminal async-response close

## In simple words

The leading design treats an escaped arbitrary stream close as terminal outcome-unknown: cleanup runs once, the owner receives the original failure, and later observers receive fresh neutral errors. That design defeated retry duplication, shared exception state, and traceback retention.

The current exact source still has two losing details. Its event cannot distinguish the owning task from a normal waiter, and its elapsed sample moved after delegated cleanup. The retained repair records the owner task ID and restores sample-before-cleanup/assign-after-success ordering.

## Decision criteria

1. Arbitrary delegated cleanup runs at most once after admission.
2. Successful completion, failed outcome, and body-read admission remain distinguishable.
3. Owner exception/cancellation identity is preserved without retaining its traceback graph.
4. Unrelated concurrent callers settle without shared mutable exception identity.
5. Same-owner re-entry returns promptly and cannot create an owner/event cycle.
6. Successful elapsed keeps its existing pre-cleanup measurement while failed cleanup publishes nothing.
7. The implementation remains backend-neutral for AnyIO asyncio and Trio on Python 3.9+.
8. The source diff stays reviewable and excludes HTTPCore, sync close, and client multi-owner shutdown.

## Selected approach

### Terminal outcome-unknown with exact owner-task detection

- Design: retain the current one-attempt event and terminal failed bit; add an integer owner-task ID and reject same-task waiting immediately.
- Owning boundary: `Response.aclose()` and its private in-flight state.
- Evidence: retry duplication executed on PR #1; five-file candidate focused/full execution; GC and fresh-exception controls; exact reconstructed current production timeout failures; repaired local target passes.
- Advantages: prevents duplicate arbitrary cleanup, preserves original owner outcome, avoids arbitrary traceback retention, keeps unrelated waiter joining, and repairs the exact cycle locally.
- Costs and risks: task identity compatibility across AnyIO versions; descendant task provenance remains separate; new prompt failure for re-entry.
- Remaining controls: asyncio/Trio, Python 3.9/3.13, target Mypy, complete ordinary gates, and renewed independent review.

### Pre-cleanup elapsed sample with post-success publication

- Design: sample elapsed immediately on wrapper close entry, await delegated cleanup, assign the sample only after success.
- Owning boundary: `BoundAsyncStream.aclose()`.
- Evidence: base ordering; review `4827924287`; exact current deterministic control reports `10.0`; repaired patch reports `2.0`.
- Advantages: failed cleanup leaves elapsed unavailable while successful behavior keeps its previous measurement boundary.
- Costs and risks: one local variable survives the await; negligible.
- Remaining controls: target-native Python/backend matrix and existing elapsed tests.

## Viable alternatives

### ContextVar close provenance

- Design: mark the delegated-close context with an attempt token and reject re-entry from the owner or inherited child contexts.
- Why it remains plausible: detects a wider callback/descendant cycle family than task ID alone.
- What it would improve: provenance across child tasks spawned during delegated cleanup.
- What it would widen or complicate: context propagation semantics, retained tokens in long-lived child tasks, and a broader unsupported boundary.
- Exact discriminator: a target-native child-task cycle that task-ID detection misses and that maintainers want to prevent generically.
- Reopening trigger: exact task-ID repair proves insufficient in an accepted supported scenario.

### Spawn an authoritative cleanup task

- Design: create a backend task that owns cleanup independently of caller cancellation; callers await its result.
- Why it remains plausible: separates operation lifetime from waiter cancellation and supplies one joinable object.
- What it would improve: explicit operation identity and potentially broader re-entry provenance.
- What it would widen or complicate: task lifetime, cancellation delivery, orphan cleanup, exception retrieval, context propagation, and shutdown.
- Exact discriminator: cancellation/re-entry/stuck-close tests showing bounded, leak-free ownership across asyncio and Trio.
- Reopening trigger: current event model cannot represent the accepted contract.

### Private close-state enum

- Design: replace three booleans/state pointer with `OPEN | CLOSING(owner,event) | CLOSED | FAILED`.
- Why it remains plausible: makes impossible combinations and terminal semantics clearer.
- What it would improve: maintainability and future property reasoning.
- What it would widen or complicate: larger rewrite and pickle migration for a narrow repair.
- Exact discriminator: a target-native test exposing another current state transition defect.
- Reopening trigger: repair becomes awkward or error-prone with the current fields.

### Explicit unsupported re-entry contract

- Design: document that streams must avoid re-entering their response.
- Why it remains plausible: zero runtime overhead.
- Why it currently loses: leaves a silent indefinite wait in public extension code and provides no enforcement.
- Reopening trigger: explicit maintainer declaration that this graph is outside the supported transport interface and hangs are acceptable.

## Executed losing approaches

### Retry after escaped cleanup failure

- Exact branch/commit: owned PR #1, including `b3083e7ce6a6ace1756d3cf1e4ec5371663c2c55` history.
- What ran: commit-then-control-flow stream with owner/waiter retry ownership; focused and repository workflows.
- Result: two stream-close calls and two committed cleanup effects.
- Why it lost: `AsyncByteStream` offers no generic idempotency guarantee.
- Useful evidence retained: deterministic duplicate-effect proof.

### One shared terminal exception object

- Exact carrier predecessor: `5bb3142b048bbf3067a9469dab297d1f0b0908d3`.
- What ran: concurrent and repeated observer paths.
- Result: one exception instance accumulated mutable traceback state across callers.
- Why it lost: exception objects cannot safely serve as shared durable terminal records.
- Useful evidence retained: fresh-per-observer error requirement.

### Retain the original owner exception as observer cause

- Exact source predecessor: `f0cef321536fc93a1d06597abfb9941531f9a8b1`.
- Result: response retained the arbitrary exception and its traceback graph.
- Why it lost: a retained response could retain delegated-frame locals and application objects indefinitely.
- Useful evidence retained: GC regression and neutral bounded cause requirement.

### Sample elapsed after delegated cleanup

- Exact current source: `18256f10d1b306bdf87a1bab24b214c15839147b`.
- What ran: deterministic blocking custom transport and clock.
- Result: elapsed was `10.0` seconds instead of the existing pre-cleanup `2.0` sample.
- Why it lost: solving failed publication silently redefined successful measurement.
- Useful evidence retained: sample before await, assign after success.

### Current event state without owner identity

- Exact current source: `18256f10d1b306bdf87a1bab24b214c15839147b`.
- What ran: requestless, request-bound, and caught-reentry/external-waiter tests against exact reconstructed production blobs.
- Result: three timeout failures; cancellation terminalized the response.
- Why it lost: a joinable operation needs owner provenance or cycle detection.
- Useful evidence retained: exact failing tests and original model receipt.

## Rejected easy answers

### Mark `is_closed = True` before delegation

- Temptation: preserve simple idempotence and avoid concurrency state.
- Why incomplete: reports successful completion before cleanup and makes failure invisible to later calls.
- Negative control: released base behavior and scout probe.

### Shield arbitrary cleanup indefinitely

- Temptation: guarantee one cleanup attempt reaches completion despite caller cancellation.
- Why incomplete: arbitrary user code may hang forever; no generic deadline, retirement owner, or unfinished-cleanup policy exists.
- Negative control: prior comparison matrix and separate HTTPCore lane.

### Copy or stringify arbitrary exceptions

- Temptation: retain diagnostics while dropping traceback.
- Why incomplete: user-defined copying or string conversion can execute code, retain mutable identity, leak data, or fail.
- Negative control: selected neutral bounded diagnostic avoids inspecting arbitrary exceptions.

### Treat green full CI as sufficient

- Temptation: source head has successful direct and exact executor matrices.
- Why incomplete: the suite contains no same-owner re-entry or successful elapsed-boundary control.
- Negative control: exact reconstructed source fails four new tests.

## Prior upstream and owned approaches

| Link | Approach | Status | Relationship to this unit |
| --- | --- | --- | --- |
| [HTTPX Discussion #2370](https://github.com/encode/httpx/discussions/2370) | cancellation may be translated during request handling | answered | adjacent cancellation context; no response-close settlement contract |
| [HTTPX API docs](https://github.com/encode/httpx/blob/b5addb64f0161ff6bfe94c124ef76f6a1fba5254/docs/api.md) | documents `Response.aclose()` and elapsed | current | public surface and elapsed compatibility context |
| [Owned PR #1](https://github.com/teamleaderleo/httpx/pull/1) | retryable per-attempt close | research | executed losing retry design and duplicate-effect evidence |
| [Owned PR #4](https://github.com/teamleaderleo/httpx/pull/4) | exact-head execution carrier | closed | retained execution only; never source candidate |
| [Owned PR #6](https://github.com/teamleaderleo/httpx/pull/6) | terminal unknown source candidate | open | canonical source, now REPAIR for re-entry and elapsed |
| [Fieldwork PR #173](https://github.com/teamleaderleo/fieldwork/pull/173) | broad scout packet | closed | superseded evidence source |
| [Fieldwork PR #309](https://github.com/teamleaderleo/fieldwork/pull/309) | canonical finding stack | open draft | historical finding text is stale against current exact defects |

## Deferred adjacent work

- synchronous close retry/state — separate owner and thread policy
- HTTPCore HTTP/1.1/HTTP/2 retirement — lower-layer side effects and trace callback re-entry
- client shutdown — multiple transport owners and aggregate outcomes
- socket reuse/capacity — protocol-specific integration evidence
- broad public state redesign — maintainer direction first

## Decision history

| Date | Exact inputs | Decision | Reason | Reopening trigger |
| --- | --- | --- | --- | --- |
| 2026-07-30 | base plus PR #1 execution | reject generic retry | committed cleanup duplicated | public idempotency guarantee |
| 2026-07-31 | source predecessors and reviews | select terminal unknown + fresh neutral observers | avoids retry and shared exception state | safe narrower contract |
| 2026-07-31 | `f0cef321...` review | drop retained owner exception | traceback graph retention | bounded safe exception representation |
| 2026-07-31 | `206b8f50...` review | preserve pre-cleanup elapsed sample | avoid semantic drift | intentional documented elapsed change |
| 2026-08-01 | exact `18256f10...` blobs and new tests | `REPAIR` re-entry and elapsed | three timeouts and `10.0` versus `2.0` | direct repaired head and target gates |
| 2026-08-01 | retained patch local execution | retain task-ID plus timing-order repair | five controls passed | target matrix disproves portability or semantics |
