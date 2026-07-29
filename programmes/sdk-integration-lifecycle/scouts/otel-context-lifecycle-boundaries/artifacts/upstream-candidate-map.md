# Upstream candidate map: OpenTelemetry JS lifecycle findings

## Purpose

This file decomposes the Fieldwork findings into reviewable upstream candidates. It is not a request to submit anything yet. Upstream contact remains unauthorized.

The findings should not be submitted as one mega-issue or one mega-PR. They occur at different abstraction layers, have different compatibility risks, and require different maintainers to evaluate them.

## Current evidence and review state

- target revision: `open-telemetry/opentelemetry-js@7b06368b7362a30ca69c178f43bd94dfbb36f85d`
- characterization fork head: `548b8a4b801bbc0a9624323585179de44e44e174`
- prepared characterization cases: 18 across 7 lifecycle boundaries
- `NodeSDK` start-guard fork head: `14b524ff0c0d8e39321c31be218b0c9ee0ca0b78`
- repaired `startNodeSDK()` cleanup fork head: `482cb975f78572bc65a9b263fb677b7a274e2fff`
- Fieldwork synthesis PR #32: draft and held for reconciliation with current main
- target execution for the new fork tests: not retained

Evidence classes:

- source maps and implementation review: `source-read`;
- retained dependency-free async/retry probe: `model-executed`;
- fork characterization and fix tests: `target-test-prepared`;
- target package execution: not claimed.

## Promoted candidates

The promoted list remains five units. Additional findings below are retained as leads until their characterization runs and their preferred review boundaries are clearer.

## Candidate A — NodeSDK one-start-attempt guard

### Status

Implemented in the user-owned fork:

- branch: `fieldwork/nodesdk-start-state-guard`
- draft PR: https://redirect.github.com/teamleaderleo/opentelemetry-js/pull/2
- exact head: `14b524ff0c0d8e39321c31be218b0c9ee0ca0b78`
- current disposition: `EXECUTE`

### Proposed upstream unit

One focused PR in `@opentelemetry/sdk-node`.

### Problem

Calling `NodeSDK.start()` repeatedly on one object can repeat setup, replace private provider fields while global APIs retain earlier providers, throw partway through metrics setup, or recursively re-enter startup.

### Resolution

Set a `_startAttempted` guard before the first startup side effect. Later calls warn and return.

### Why separate

This prevents a proven ownership split without claiming process-level restart, global disposal, multi-instance coordination, shutdown-before-start policy, or a complete start/shutdown state machine.

### Review boundary

The branch is current against the pinned fork base and remains narrow: seven production additions plus one focused prepared test file. No target execution receipt exists yet.

## Candidate B — `startNodeSDK()` failed-setup cleanup

### Status

Implemented and self-review-repaired in the user-owned fork:

- branch: `fieldwork/start-node-sdk-failure-cleanup`
- draft PR: https://redirect.github.com/teamleaderleo/opentelemetry-js/pull/3
- exact head: `482cb975f78572bc65a9b263fb677b7a274e2fff`
- current disposition: `EXECUTE`

### Problem

`startNodeSDK()` originally registered supplied instrumentations before component creation. When component creation threw, it returned `NOOP_SDK` after potentially enabling instrumentation and an unreachable context manager.

The first fork repair moved registration after global publication. Exact-head self-review found that ordering introduced another failure: if instrumentation registration threw, newly created providers could remain process-global even though the function returned no shutdown handle.

### Current resolution

1. create SDK components;
2. register instrumentation against the newly created trace, metric, and log providers explicitly;
3. if registration throws, disable the created context manager, start provider cleanup, and preserve the registration error;
4. publish process globals only after registration succeeds;
5. return the shutdown handle.

### Why separate

This repairs concrete setup failure paths without deciding duplicate successful calls, process-global replacement, or ownership-aware uninstallation.

### Remaining boundary

The helper is synchronous. Cleanup can start asynchronous provider shutdown but cannot await completion. Cleanup rejection handling and arbitrary partial side effects inside a throwing instrumentation remain unsolved.

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
- What should happen when shutdown is requested before or during startup?

### Why no immediate PR

The current APIs do not expose ownership tokens for globals or per-instrumentation enablement ownership. Blind cleanup can remove another component's provider or disable instrumentation that NodeSDK did not enable.

## Retained lead F — start/shutdown interleaving

### Evidence state

Two target-native characterization cases exist in fork PR #1 at head `548b8a4b801bbc0a9624323585179de44e44e174`, but they have not run in this environment.

Fieldwork record:

`artifacts/nodesdk-shutdown-start-interleaving.md`

### Source-predicted behavior

- `shutdown()` before first `start()` resolves successfully because no provider fields exist;
- a later `start()` still installs live providers;
- instrumentation can synchronously reenter `shutdown()` during `start()` before providers exist;
- that shutdown promise resolves while startup continues and installs providers afterward.

### Why it is not promoted yet

The narrow start guard does not answer the contract. A real solution may require explicit `starting`, `shutting-down`, and terminal states. Before creating another issue, the characterization should run and the compatibility choice should be framed: terminal early shutdown, deferred shutdown, explicit invalid ordering, or documented unsupported ordering.

### Required invariant

After a shutdown promise resolves, the same helper object should not subsequently install newly running providers.

## Retained lead G — lifecycle fanout after synchronous child exceptions

### Evidence state

Two target-native NodeSDK characterization cases exist in fork PR #1 at head `548b8a4b801bbc0a9624323585179de44e44e174`.

They cover:

1. a synchronous trace-processor shutdown exception escaping before a promise is returned and preventing later trace processors and signal providers from being called;
2. synchronous log-processor and metric-reader exceptions becoming rejected promises while still skipping later log processors and metric readers.

The cases have not run in this environment. Direct package-level force-flush and aggregate tests remain absent.

Fieldwork record:

`artifacts/shutdown-fanout-synchronous-throw.md`

### Source-predicted behavior

Several aggregate lifecycle paths eagerly invoke children inside loops or `.map()` while building `Promise.all` inputs.

- trace can throw synchronously before returning a promise and skip later processors;
- a synchronous trace-provider exception can prevent NodeSDK from requesting logs and metrics shutdown;
- logs and metrics return rejected promises through `async` methods, but later processors or readers are still skipped when `.map()` aborts;
- providers may become terminal or retain rejected one-shot state without ever reaching the skipped children;
- force-flush paths have related behavior.

### Why it is not promoted yet

The correct review unit is unresolved. It could be:

- a trace-only `MultiSpanProcessor` correction;
- parallel per-signal fixes;
- a NodeSDK aggregate-shutdown correction;
- or a shared cross-signal fanout helper and error contract.

The desired error policy also needs agreement: fail-fast rejection after attempting all children, or complete error aggregation.

## Negative lead — logger startup ordering

A concern that instrumentations might remain bound to a no-op logger provider was checked and rejected. The logs API uses a proxy logger provider, and first global registration sets its delegate. Existing proxy logger references can retarget. This result remains documented so the same false lead is not reopened.

## Recommended submission order

1. Candidate A: same-object start guard.
2. Candidate B: repaired failed function-setup cleanup.
3. Run and decide retained lead F without silently expanding candidate A.
4. Candidate C: trace provider shutdown contract.
5. Run and classify retained lead G; decide whether it belongs with candidate C or a cross-signal proposal.
6. Candidate D: metric reader binding transactionality.
7. Candidate E: global installation and disposal design.

Candidates A and B are small implementation candidates but still require target execution. Candidates C and D are lower-level correctness issues. Candidate E is the umbrella design discussion informed by the earlier concrete fixes. Leads F and G are deliberately not counted as promoted proposals yet.

## Current Fieldwork review disposition

Fieldwork PR #32 is draft and held because its branch diverged substantially from current main. The target, programme, and scout issue bodies remain the current discovery surfaces while the synthesis branch is reconciled.

A new complete-diff review is required after reconciliation. The builder is not eligible to be the sole final accepter of a consequential upstream packet.

## What should link to Fieldwork

A future upstream issue can include a single optional deep-dive link to the Fieldwork synthesis rather than pasting every experiment into every issue. Each issue should still be independently understandable and contain its own minimal reproduction.

Suggested deep-dive target after explicit authorization and current-main reconciliation:

https://redirect.github.com/teamleaderleo/fieldwork/pull/32

The upstream issue should describe that link as supplemental characterization, not as a prerequisite for understanding the report.

## Contact boundary

No upstream issue, pull request, comment, review, reaction, or direct backlink has been created.
