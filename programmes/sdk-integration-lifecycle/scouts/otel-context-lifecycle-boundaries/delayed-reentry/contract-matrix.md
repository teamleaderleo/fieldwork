# Delayed lifecycle reentry contract matrix

## Decision criteria

A viable contract must satisfy all of these at once:

1. direct synchronous same-owner recursion cannot deadlock;
2. delayed same-owner recursion cannot remain pending forever;
3. an unrelated concurrent caller receives the shared shutdown result;
4. cross-owner nesting remains legal when the dependency graph is acyclic;
5. every timeout or abandoned cleanup is visible;
6. custom processors, readers, and exporters remain within the stated boundary;
7. the mechanism works in Node and browser packages without requiring a global promise hook.

## Compared directions

| Direction | Breaks delayed cycle | Preserves unrelated join | Portable | Main cost | Disposition |
| --- | --- | --- | --- | --- | --- |
| Keep the current synchronous invocation flag | No | Yes | Yes | delayed self-dependency remains possible | Insufficient alone |
| Resolve every in-flight recursive-looking call immediately | Yes | No | Yes | external concurrent callers lose the shared result and failure | Reject |
| Compare returned child promise with the owner promise | No | Yes | Yes | an `async` child returns a distinct adopting promise, so identity misses the cycle | Reject |
| Add a caller-local `Promise.race` timeout | No | Yes | Yes | only the caller stops waiting; the owner operation remains pending | Reject as lifecycle repair |
| Add an operation-owned timeout to the shared result | Yes | Yes | Yes | slow valid cleanup becomes a terminal timeout; trace and logs lack a shutdown timeout contract | Viable only as an explicit API policy |
| Track provenance with Node `AsyncLocalStorage` | Yes | Yes | No | Node-only ambient mechanism in browser-facing SDK packages | Reject |
| Track provenance through the OpenTelemetry context API | Potentially | Potentially | Conditional | requires an installed context manager during shutdown and mixes internal lifecycle control with user context | Reject for the first slice |
| Pass an explicit internal lifecycle owner token | Yes | Yes | Yes | arbitrary custom lifecycle interfaces do not currently carry such a token | Correct model; requires interface or adapter redesign |
| Explicitly forbid a child from awaiting its owner lifecycle method | Contract only | Yes | Yes | misuse can still hang at runtime; needs tests and documentation | Minimum compatible contract, not a runtime repair |
| Redesign fanout so owner completion does not await children | Yes | Yes | Yes | violates shutdown completion and failure propagation | Reject |

## Important distinction

An operation-owned timeout and a caller-local timeout are different:

```text
caller-local timeout:
  caller stops waiting
  owner promise remains pending
  child/owner cycle remains

operation-owned timeout:
  shared owner promise rejects
  every joined caller receives that rejection
  the adopting child promise unwinds from the same rejection
```

`MetricReader.shutdown({ timeoutMillis })` already has an operation-owned timeout path. The equivalent is absent from `LoggerProvider.shutdown()` and `TracerProvider.shutdown()`, and an optional metric timeout does not define whether unfinished cleanup may continue safely.

## Current recommendation

1. Retain the synchronous guard because it correctly contains direct reentry.
2. Add target-native delayed-reentry characterizations for trace, logs, `MeterProvider`, and `MetricReader` with and without timeout.
3. State the minimum compatible rule: a lifecycle child must not await the lifecycle promise of its own owner.
4. Keep runtime implementation on hold until either:
   - a portable explicit provenance channel exists for arbitrary custom children; or
   - each provider adopts a deliberate operation-owned timeout and unfinished-cleanup policy.
5. Preserve legitimate external joining as a hard negative control for every candidate.
