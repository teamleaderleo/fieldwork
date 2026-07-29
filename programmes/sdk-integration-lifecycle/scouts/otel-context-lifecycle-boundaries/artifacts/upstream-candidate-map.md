# Upstream candidate map: OpenTelemetry JS lifecycle findings

## Purpose

This file decomposes the Fieldwork findings into reviewable upstream candidates. It is not a request to submit anything yet. Upstream contact remains unauthorized.

The findings should not be submitted as one mega-issue or one mega-PR. They occur at different abstraction layers, have different compatibility risks, and require different maintainers to evaluate them.

## Current evidence and review state

- target revision: `open-telemetry/opentelemetry-js@7b06368b7362a30ca69c178f43bd94dfbb36f85d`
- characterization fork head: `85f8a928dc2385cf506445ed9794c453b70803e3`
- prepared characterization cases: 28
  - 18 NodeSDK/helper cases;
  - 10 direct trace, logs, and metrics package cases;
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

1. An issue in `@opentelemetry/sdk-trace` describing the provider-level contract mismatch.
2. A separate trace SDK PR after maintainers agree on behavior.

### Problem

The JavaScript `TracerProvider` has no shutdown state. It delegates every `shutdown()` call again, always returns or creates a real SDK tracer, and lets cached tracers retain their processor path.

Direct prepared package tests demonstrate:

- repeated provider shutdown reaches a custom processor repeatedly;
- a cached tracer creates recording spans after shutdown;
- a newly requested tracer creates recording spans after shutdown;
- both paths reach a custom processor.

### Specification and same-repository precedent

The trace SDK specification directs implementations to return a no-op tracer after shutdown when possible.

JavaScript logs already implements the stronger lifecycle:

- `BindOnceFuture` stores one shutdown operation and result;
- new logger requests return no-op after shutdown;
- cached loggers consult shared shutdown state and stop emitting.

JavaScript metrics also sets provider terminal state before reader shutdown and returns no-op meters for new requests.

Detailed record:

`artifacts/javascript-signal-provider-shutdown-comparison.md`

### Proposed behavior

- provider shutdown is one-shot;
- concurrent and later calls share the first result or safely no-op;
- new tracers after shutdown are no-op;
- cached tracers stop creating recording spans after shutdown begins;
- each registered processor receives shutdown at most once;
- force flush during and after shutdown has a deterministic contract.

### Why separate

Provider lifecycle state answers whether shutdown and telemetry production can continue. Aggregate fanout answers whether every child is attempted during the one allowed lifecycle operation. They may share implementation infrastructure but should not be conflated automatically.

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

NodeSDK cannot safely repair an object whose constructor did not return. The defect belongs in the metrics SDK. It is also separate from metric shutdown concurrency.

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

Two target-native characterization cases exist in fork PR #1 at head `85f8a928dc2385cf506445ed9794c453b70803e3`, but they have not run in this environment.

Fieldwork record:

`artifacts/nodesdk-shutdown-start-interleaving.md`

### Source-predicted behavior

- `shutdown()` before first `start()` resolves because no provider fields exist;
- a later `start()` still installs live providers;
- instrumentation can synchronously reenter `shutdown()` during `start()` before providers exist;
- that shutdown promise resolves while startup continues and installs providers afterward.

### Why it is not promoted yet

The narrow start guard does not answer the contract. A real solution may require explicit `starting`, `shutting-down`, and terminal states. The characterization should run and the compatibility choice should be framed first: terminal early shutdown, deferred shutdown, explicit invalid ordering, or documented unsupported ordering.

### Required invariant

After a shutdown promise resolves, the same helper object should not subsequently install newly running providers.

## Retained lead G — lifecycle fanout after synchronous child exceptions

### Evidence state

Prepared direct tests now cover shutdown and force flush at the owning package boundaries:

- `MultiSpanProcessor`: synchronous throw before a promise is returned; later trace processors skipped;
- `MultiLogRecordProcessor`: rejected promise through async wrapper; later log processors skipped;
- `MeterProvider`: rejected promise through async wrapper; later readers skipped;
- NodeSDK: a synchronous trace shutdown failure prevents later signal-provider shutdown calls.

The tests are in fork PR #1 at head `85f8a928dc2385cf506445ed9794c453b70803e3`. They have not run in this environment.

Fieldwork record:

`artifacts/shutdown-fanout-synchronous-throw.md`

### Why it is not promoted yet

The correct review unit is unresolved. It could be:

- a trace-only `MultiSpanProcessor` correction;
- parallel per-signal fixes;
- a NodeSDK aggregate-shutdown correction;
- or a shared cross-signal fanout helper and error contract.

The desired error policy also needs agreement: fail-fast rejection after attempting every child, or complete error aggregation.

## Retained lead H — metric provider and reader shutdown concurrency

### Evidence state

Prepared tests exist at fork head `85f8a928dc2385cf506445ed9794c453b70803e3`.

Fieldwork record:

`artifacts/metric-shutdown-concurrency.md`

### Source-predicted behavior

- `MeterProvider` sets `_shutdown` before readers finish;
- a concurrent second provider shutdown resolves successfully while the first remains pending and may later reject;
- `MetricReader` sets `_shutdown` only after `onShutdown()` resolves;
- two concurrent reader shutdown calls can therefore invoke `onShutdown()` twice.

### Proposed direction

Use one shared one-shot future for both provider and reader shutdown so all callers receive one result and child cleanup starts once.

### Why it is not promoted yet

The tests must run, and the review boundary must be chosen: one metrics lifecycle issue with provider and reader changes, or two patches under one agreed contract. This must remain separate from reader-constructor transactionality.

## Ambiguity retained — cached metrics objects after shutdown

New `getMeter()` calls return a no-op meter after provider shutdown. Previously returned meters and instruments hold storage directly and do not visibly consult provider shutdown state.

The metrics shutdown specification clearly addresses new meter acquisition but is less explicit about objects obtained before shutdown. Cached-meter recording is therefore retained as a contract question, not claimed as a defect.

## Negative lead — logger startup ordering

A concern that instrumentations might remain bound to a no-op logger provider was checked and rejected. The logs API uses a proxy logger provider, and first global registration sets its delegate. Existing proxy logger references can retarget.

## Recommended submission order

1. Candidate A: same-object start guard.
2. Candidate B: repaired failed function-setup cleanup.
3. Run and decide retained lead F without expanding Candidate A silently.
4. Candidate C: trace-provider shutdown contract.
5. Run and classify retained lead G; decide whether it belongs with Candidate C or a cross-signal proposal.
6. Run and classify retained lead H as metrics lifecycle work.
7. Candidate D: metric-reader binding transactionality.
8. Candidate E: global installation and disposal design.

Candidates A and B are small implementation candidates but still require target execution. Candidates C and D are lower-level correctness issues. Candidate E is the umbrella design discussion. Leads F, G, and H are deliberately not counted as promoted proposals yet.

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
