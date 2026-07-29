# Upstream candidate map: OpenTelemetry JS lifecycle findings

## Purpose

This file decomposes the Fieldwork findings into reviewable upstream candidates. It is not a request to submit anything yet. Upstream contact remains unauthorized.

The findings should not be submitted as one mega-issue or one mega-PR. They occur at different abstraction layers, have different compatibility risks, and require different maintainers to evaluate them.

## Candidate A — NodeSDK one-start-attempt guard

### Status

Implemented in the user-owned fork:

- branch: `fieldwork/nodesdk-start-state-guard`
- draft PR: https://redirect.github.com/teamleaderleo/opentelemetry-js/pull/2

### Proposed upstream unit

One focused PR in `@opentelemetry/sdk-node`.

### Problem

Calling `NodeSDK.start()` repeatedly on one object can repeat setup, replace private provider fields while global APIs retain earlier providers, throw partway through metrics setup, or recursively re-enter startup.

### Resolution

Set a `_startAttempted` guard before the first startup side effect. Later calls warn and return.

### Why separate

This prevents a proven ownership split without claiming process-level restart, global disposal, or multi-instance coordination.

## Candidate B — `startNodeSDK()` failed-creation cleanup

### Status

Implemented in the user-owned fork:

- branch: `fieldwork/start-node-sdk-failure-cleanup`
- draft PR: https://redirect.github.com/teamleaderleo/opentelemetry-js/pull/3

### Proposed upstream unit

One focused PR in `@opentelemetry/sdk-node`.

### Problem

`startNodeSDK()` currently registers supplied instrumentations before component creation. When component creation throws, it returns `NOOP_SDK` after potentially enabling instrumentation and an unreachable context manager.

### Resolution

Create components first, register instrumentation only after creation succeeds, and disable the context manager created during a failed attempt.

### Why separate

This repairs a concrete failure path without deciding duplicate successful calls or process-global ownership.

## Candidate C — trace provider shutdown contract

### Proposed upstream units

1. An issue in the trace SDK describing the provider-level contract mismatch.
2. A separate trace SDK PR after maintainers agree on behavior.

### Problem

The JavaScript `TracerProvider` delegates every `shutdown()` call directly to span processors and does not maintain shutdown state. A custom processor can therefore receive repeated shutdown calls. Because the provider remains globally reachable and can still return functional tracers, custom processors can also receive spans after provider shutdown.

### Proposed behavior

- provider shutdown is one-shot;
- repeated calls return the same result or safely no-op;
- new tracers after shutdown are no-op;
- cached tracers must not start recording spans after provider shutdown;
- tests use a custom processor so behavior is not hidden by built-in processor guards.

### Cross-language precedent

Go makes all provider methods no-op after shutdown and uses atomic state plus one-shot processor shutdown:

https://redirect.github.com/open-telemetry/opentelemetry-go/blob/2776cee15126f0841bd65ad205f576b240883a24/sdk/trace/provider.go#L297-L328

Rust records provider shutdown atomically, rejects a repeated shutdown, and returns a no-op tracer after shutdown:

https://redirect.github.com/open-telemetry/opentelemetry-rust/blob/0e78170d712e5046b8ed93b6f99b2b003af15cd7/opentelemetry-sdk/src/trace/provider.rs#L245-L298

Java's aggregate SDK makes shutdown one-shot with an `AtomicBoolean`:

https://redirect.github.com/open-telemetry/opentelemetry-java/blob/6ffe557f36f6d1150556c9e95bfea9fc20e3a49e/sdk/all/src/main/java/io/opentelemetry/sdk/OpenTelemetrySdk.java#L101-L117

## Candidate D — metric reader binding transactionality

### Proposed upstream units

1. An issue in `@opentelemetry/sdk-metrics`.
2. A metrics SDK PR after selecting prevalidation, reservation, or rollback semantics.

### Problem

`MeterProvider` binds readers sequentially in its constructor. If reader A binds successfully and later reader B throws because it is already bound, construction aborts while A remains bound to a partial provider object that the caller never receives.

### Resolution options

- prevalidate all readers before binding any;
- introduce a two-phase reserve/commit protocol;
- add supported rollback/unbind semantics.

### Why separate

NodeSDK cannot safely repair an object whose constructor did not return. The defect belongs in the metrics SDK.

## Candidate E — process-global registration ownership and disposal design

### Proposed upstream unit

A design issue, not an immediate implementation PR.

### Questions

- Are `NodeSDK` and `startNodeSDK()` process-singleton installation helpers?
- Should a second helper fail before side effects, warn and no-op, or be allowed to replace the first?
- Should provider shutdown and installation disposal be separate operations?
- How can a helper remove a global only if it still owns that exact registration?
- How can instrumentation cleanup avoid disabling instrumentation enabled by another owner?
- What lifecycle is supported in hot reloaders, notebooks, test runners, and plugin hosts?

### Why no immediate PR

The current APIs do not expose ownership tokens for globals or per-instrumentation enablement ownership. Blind cleanup can remove another component's provider or disable instrumentation that NodeSDK did not enable.

## Recommended submission order

1. Candidate A: same-object start guard.
2. Candidate B: failed function-start cleanup.
3. Candidate C: trace provider shutdown contract.
4. Candidate D: metric reader binding transactionality.
5. Candidate E: global installation and disposal design.

Candidates A and B are small, evidenced fixes. Candidates C and D are lower-level correctness issues. Candidate E is the umbrella design discussion informed by the earlier concrete fixes.

## What should link to Fieldwork

A future upstream issue can include a single optional deep-dive link to the Fieldwork synthesis rather than pasting every experiment into every issue. Each issue should still be independently understandable and contain its own minimal reproduction.

Suggested deep-dive target after explicit authorization:

https://redirect.github.com/teamleaderleo/fieldwork/pull/32

The upstream issue should describe that link as supplemental characterization, not as a prerequisite for understanding the report.

## Contact boundary

No upstream issue, pull request, comment, review, reaction, or direct backlink has been created.