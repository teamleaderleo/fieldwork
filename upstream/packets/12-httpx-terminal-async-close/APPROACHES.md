# Approaches — Unit 12 terminal async-response close

## In simple words

The leading design treats an escaped arbitrary stream close as terminal outcome-unknown: cleanup runs once, the owner receives the original failure, and later observers receive fresh neutral errors. That design defeated retry duplication and traceback retention. It now needs one narrow addition so the owning task cannot join its own close event.

## Decision criteria

1. Arbitrary delegated cleanup runs at most once after admission.
2. Successful completion, failed outcome, and body-read admission remain distinguishable.
3. Owner exception/cancellation identity is preserved without retaining its traceback graph.
4. Unrelated concurrent callers settle without shared mutable exception identity.
5. Same-owner re-entry returns promptly and cannot create an owner/event cycle.
6. The implementation remains backend-neutral for AnyIO asyncio and Trio on Python 3.9+.
7. The source diff stays reviewable and excludes HTTPCore, sync close, and client multi-owner shutdown.

## Selected approach

### Terminal outcome-unknown with owner-reentry detection

- Design: retain the current one-attempt event and terminal failed bit; add an opaque owner-task identity and reject same-owner waiting immediately.
- Owning boundary: `Response.aclose()` and its private in-flight state.
- Evidence: retry duplication executed on PR #1; five-file candidate focused/full execution; GC and fresh-exception controls; source-read plus standalone re-entry model.
- Advantages: prevents duplicate arbitrary cleanup, preserves original owner outcome, avoids arbitrary traceback retention, keeps unrelated waiter joining, and repairs the cycle locally.
- Costs and risks: task identity compatibility across AnyIO versions; new prompt failure for re-entry; exact error semantics require target review.
- Remaining controls: request-bound/requestless re-entry, caught/escaping re-entry, external waiter isolation, asyncio/Trio, Python 3.9/3.13, complete target gates.

## Viable alternatives

### Spawn an authoritative cleanup task

- Design: create a backend task that owns cleanup independently of caller cancellation; callers await its result.
- Why it remains plausible: naturally separates owner operation lifetime from waiter cancellation and provides one joinable object.
- What it would improve: clearer operation identity and potentially easier re-entry provenance.
- What it would widen or complicate: task lifetime, cancellation delivery, orphan cleanup, exception retrieval, backend task creation, context propagation, and shutdown.
- Exact discriminator: cancellation/re-entry/stuck-close tests showing bounded, leak-free task ownership across asyncio and Trio.
- Reopening trigger: owner identity cannot be represented safely in the current event model.

### Explicit unsupported re-entry contract without task detection

- Design: document that streams must avoid re-entering their response.
- Why it remains plausible: smallest source change would be no change.
- What it would improve: zero runtime overhead.
- What it would widen or complicate: leaves a silent indefinite wait in public extension code and provides no enforcement.
- Exact discriminator: maintainer declaration that this ownership graph is outside the supported transport interface and hangs are acceptable.
- Reopening trigger: explicit upstream contract.

### Private close-state enum

- Design: replace three booleans/state pointer with `OPEN | CLOSING(owner,event) | CLOSED | FAILED`.
- Why it remains plausible: makes impossible combinations and terminal semantics clearer.
- What it would improve: maintainability and future property reasoning.
- What it would widen or complicate: larger rewrite and pickle migration for a narrow repair.
- Exact discriminator: a target-native test exposing a current impossible combination or state transition bug beyond re-entry.
- Reopening trigger: re-entry repair becomes awkward or error-prone with the current fields.

## Executed losing approaches

### Retry after escaped cleanup failure

- Exact branch, patch, or commit: owned PR #1, including `b3083e7ce6a6ace1756d3cf1e4ec5371663c2c55` history.
- What ran: commit-then-control-flow stream with owner/waiter retry ownership; focused and repository workflows.
- Result: two stream-close calls and two committed cleanup effects.
- Why it lost: the public `AsyncByteStream` contract offers no generic idempotency guarantee.
- Useful evidence retained: deterministic proof that retry can duplicate arbitrary effects.

### One shared terminal exception object

- Exact branch, patch, or commit: execution carrier predecessor `5bb3142b048bbf3067a9469dab297d1f0b0908d3`.
- What ran: concurrent and repeated observer paths.
- Result: one exception instance accumulated and exposed mutable traceback state across callers.
- Why it lost: exception objects own mutable tracebacks and cannot safely serve as durable shared terminal records.
- Useful evidence retained: fresh-per-observer error requirement.

### Retain the original owner exception as observer cause

- Exact source predecessor: `f0cef321536fc93a1d06597abfb9941531f9a8b1`.
- What ran: owner/observer behavior and repository matrix.
- Result: response retained the arbitrary exception and its traceback graph.
- Why it lost: a retained response could retain delegated-frame locals and application objects indefinitely.
- Useful evidence retained: GC regression and sanitized neutral cause requirement.

### Publish elapsed after delegated close using a post-close time sample

- Exact source predecessor: `206b8f50f2cb773d8854646b35f8938bf528dd83`.
- What ran: failure publication control.
- Result: failure no longer published elapsed, but successful cleanup latency changed elapsed semantics.
- Why it lost: existing elapsed measurement sampled before cleanup.
- Useful evidence retained: sample before await, assign after success.

### Current event state without owner identity

- Exact source: `18256f10d1b306bdf87a1bab24b214c15839147b`.
- What ran: source-equivalent asyncio model.
- Result: same-owner re-entry timed out while waiting on the owner's event; cancellation terminalized the response.
- Why it lost: a joinable operation needs provenance or cycle detection.
- Useful evidence retained: [`receipts/reentrant-close-probe.md`](./receipts/reentrant-close-probe.md).

## Rejected easy answers

### Mark `is_closed = True` before delegation

- Temptation: preserve simple idempotence and avoid concurrency state.
- Why it is incomplete or unsafe: reports successful completion before cleanup and makes failure invisible to later close calls.
- Negative control or source fact: released base behavior and scout probe.

### Shield arbitrary cleanup indefinitely

- Temptation: guarantee one cleanup attempt reaches completion despite caller cancellation.
- Why it is incomplete or unsafe: arbitrary user code may hang forever; no generic deadline, retirement owner, or unfinished-cleanup policy exists.
- Negative control or source fact: prior comparison matrix and separate HTTPCore lane.

### Copy or stringify arbitrary exceptions

- Temptation: retain diagnostics while dropping traceback.
- Why it is incomplete or unsafe: user-defined copying or string conversion can execute code, retain mutable identity, leak data, or fail.
- Negative control or source fact: selected neutral bounded diagnostic avoids inspecting arbitrary exceptions.

### Treat green full CI as sufficient

- Temptation: source head has successful direct and exact executor matrices.
- Why it is incomplete or unsafe: the suite contains no same-owner re-entry control.
- Negative control or source fact: model reproduces the cycle at that exact logic generation.

## Prior upstream approaches

| Link | Approach | Status | Relationship to this unit |
| --- | --- | --- | --- |
| [HTTPX Discussion #2370](https://github.com/encode/httpx/discussions/2370) | cancellation may be translated during request handling | answered | adjacent cancellation context; no response-close settlement contract |
| [HTTPX API docs](https://github.com/encode/httpx/blob/b5addb64f0161ff6bfe94c124ef76f6a1fba5254/docs/api.md) | documents `Response.aclose()` and elapsed | current | public surface and elapsed compatibility context |
| [Owned PR #1](https://github.com/teamleaderleo/httpx/pull/1) | retryable per-attempt close | research | executed losing retry design and duplicate-effect evidence |
| [Owned PR #4](https://github.com/teamleaderleo/httpx/pull/4) | exact-head execution carrier | closed | retained execution only; never source candidate |
| [Owned PR #6](https://github.com/teamleaderleo/httpx/pull/6) | terminal unknown source candidate | open | canonical source, now REPAIR for re-entry |
| [Fieldwork PR #173](https://github.com/teamleaderleo/fieldwork/pull/173) | broad scout packet | closed | superseded evidence source |
| [Fieldwork PR #309](https://github.com/teamleaderleo/fieldwork/pull/309) | canonical finding stack | open draft | historical finding text is stale against five-file source/re-entry result |

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
| 2026-07-31 | `206b8f50...` review | preserve pre-cleanup elapsed sample | avoid semantic drift | documented elapsed change |
| 2026-08-01 | `18256f10...`, review `4827972451`, executed model | `REPAIR` same-owner re-entry | owner waits on its own event | target-native cycle-free repair and gates |