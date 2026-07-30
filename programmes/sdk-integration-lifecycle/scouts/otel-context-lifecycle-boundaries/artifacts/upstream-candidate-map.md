# Upstream candidate map: OpenTelemetry JS lifecycle findings

## Purpose

This file decomposes the Fieldwork findings into reviewable upstream candidates. It is not a request to submit anything yet. Upstream contact remains unauthorized.

The findings should not be submitted as one mega-issue or one mega-PR. They occur at different abstraction layers, have different compatibility risks, and require different maintainers to evaluate them.

## Current evidence and review state

- target revision: `open-telemetry/opentelemetry-js@7b06368b7362a30ca69c178f43bd94dfbb36f85d`
- characterization fork head: `026855a81e3f4bb0bca4c46610446648a92a9372`
- prepared characterization cases: 30
  - 19 NodeSDK/helper cases;
  - 11 direct trace, logs, and metrics package cases;
- `NodeSDK` start-guard fork head: `14b524ff0c0d8e39321c31be218b0c9ee0ca0b78`
- repaired `startNodeSDK()` cleanup fork head: `2482d8c49c8b6e01a282a36da55e48b4a4dc8747`
- trace-provider shutdown-state fork head: `50cd262e326c2a24419bad53c932a688b42224a4`
- Fieldwork synthesis PR #32: draft and held for reconciliation with current main
- target execution for the fork tests: not retained

Evidence classes:

- source maps, specification reading, and implementation review: `source-read`;
- retained dependency-free async/retry probe: `model-executed`;
- fork characterization and fix tests: `target-test-prepared`;
- target package execution: not claimed;
- full gate: not claimed.

A temporary read-only workflow was created on a separate execution-carrier branch from exact characterization source `026855a81e3f4bb0bca4c46610446648a92a9372` and then removed. The available connector could not enumerate its push-triggered run and no commit status appeared. It produced no accepted execution receipt.

## Promoted candidates

The promoted list remains five units. Additional findings below are retained as leads until their tests run and their preferred review boundaries are clearer.

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

The branch is current against the pinned fork base and remains narrow. No target execution receipt exists yet.

## Candidate B — `startNodeSDK()` failed-setup cleanup

### Status

Implemented and repeatedly self-review-repaired in the user-owned fork:

- branch: `fieldwork/start-node-sdk-failure-cleanup`
- draft PR: https://redirect.github.com/teamleaderleo/opentelemetry-js/pull/3
- exact head: `2482d8c49c8b6e01a282a36da55e48b4a4dc8747`
- current disposition: `EXECUTE`

### Problem

`startNodeSDK()` originally registered supplied instrumentations before component creation. When component creation threw, it returned `NOOP_SDK` after potentially enabling instrumentation and an unreachable context manager.

The first fork repair moved registration after global publication. Exact-head self-review found that ordering introduced another failure: if instrumentation registration threw, newly created providers could remain process-global even though the function returned no shutdown handle.

A later self-review found that cleanup itself could replace the primary setup error or create an unhandled rejection.

### Current resolution

1. create SDK components;
2. register instrumentation against the newly created trace, metric, and log providers explicitly;
3. publish process globals only after registration succeeds;
4. on setup failure, disable the created context manager and request provider shutdown;
5. catch synchronous cleanup failures and attach rejection handlers to asynchronous cleanup;
6. report cleanup errors without replacing the primary setup or registration error.

### Why separate

This repairs concrete setup failure paths without deciding duplicate successful calls, process-global replacement, or ownership-aware uninstallation.

### Remaining boundary

The helper is synchronous. It can start asynchronous cleanup but cannot wait for completion. Arbitrary partial side effects inside a throwing instrumentation remain outside its ownership model.

Detailed record:

`artifacts/start-node-sdk-failure-cleanup-pr-draft.md`

## Candidate C — trace provider shutdown contract

### Status

Issue-first candidate with an isolated implementation trial in the user-owned fork:

- issue draft: `artifacts/tracer-provider-shutdown-contract-issue-draft.md`
- branch: `fieldwork/tracer-provider-shutdown-state`
- draft PR: https://redirect.github.com/teamleaderleo/opentelemetry-js/pull/4
- exact head: `50cd262e326c2a24419bad53c932a688b42224a4`
- current disposition: `EXECUTE`, then independent exact-head review

### Problem

The JavaScript `TracerProvider` has no shutdown state. It delegates every `shutdown()` call again, always returns or creates a recording SDK tracer, and lets cached tracers retain their processor path.

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

Detailed comparison:

`artifacts/javascript-signal-provider-shutdown-comparison.md`

### Fork-trial behavior

The isolated trial:

- uses `BindOnceFuture` for one shared shutdown operation and result;
- converts synchronous processor throws into one shared rejection;
- makes cached and newly requested tracers non-recording as soon as shutdown begins;
- returns the shutdown promise instead of force flushing afterward;
- contains direct synchronous provider shutdown or force-flush reentry from a processor.

Detailed record:

`artifacts/tracer-provider-shutdown-state-pr-draft.md`

### Unresolved edge

An asynchronously delayed processor that later returns `provider.shutdown()` can still form a self-referential promise dependency. A general fix may require a processor contract or fanout-level detection of a child returning the provider's own promise.

### Why separate

Provider lifecycle state answers whether shutdown and telemetry production can continue. Aggregate fanout answers whether every child is attempted during the one allowed lifecycle operation. They may share infrastructure but should not be conflated automatically.

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

### New direct evidence: partial function-helper publication

A prepared characterization now proves that one `startNodeSDK()` call can create a mixed installation:

1. a pre-existing global tracer provider owns tracing;
2. the helper successfully publishes its context manager;
3. the helper's trace registration is rejected;
4. the helper returns a shutdown handle for its private, non-global tracer provider;
5. shutdown targets that private provider;
6. the pre-existing global provider remains active and continues receiving spans.

Record:

`artifacts/start-node-sdk-partial-global-publication.md`

### Questions

- Are `NodeSDK` and `startNodeSDK()` process-singleton installation helpers?
- Should a second or conflicting helper fail before side effects, warn and no-op, or support partial installation?
- Should provider shutdown and installation disposal be separate operations?
- How can a helper remove a global only if it still owns that exact registration?
- How can instrumentation cleanup avoid disabling instrumentation enabled by another owner?
- Should startup report per-signal registration outcomes if partial installation remains supported?
- What lifecycle is supported in hot reloaders, notebooks, test runners, and plugin hosts?
- What should happen when shutdown is requested before or during startup?

### Why no immediate PR

The current APIs do not expose ownership tokens, compare-and-remove globals, transaction reservations, or per-instrumentation enablement ownership. Blind cleanup can remove another component's provider or disable instrumentation that NodeSDK did not enable.

## Retained lead F — start/shutdown interleaving

### Evidence state

Two target-native characterization cases exist in fork PR #1 at head `026855a81e3f4bb0bca4c46610446648a92a9372`, but they have not run in this environment.

Record:

`artifacts/nodesdk-shutdown-start-interleaving.md`

### Source-predicted behavior

- `shutdown()` before first `start()` resolves because no provider fields exist;
- a later `start()` still installs live providers;
- instrumentation can synchronously reenter `shutdown()` during `start()` before providers exist;
- that shutdown promise resolves while startup continues and installs providers afterward.

### Why it is not promoted yet

The narrow start guard does not answer the contract. A real solution may require explicit `starting`, `shutting-down`, and terminal states. The characterization should run and the compatibility choice should be framed first.

### Required invariant

After a shutdown promise resolves, the same helper object should not subsequently install newly running providers.

## Retained lead G — lifecycle fanout after synchronous child exceptions

### Evidence state

Prepared direct tests at fork head `026855a81e3f4bb0bca4c46610446648a92a9372` cover shutdown and force flush at owning package boundaries:

- `MultiSpanProcessor`: synchronous throw before a promise is returned; later trace processors skipped;
- `MultiLogRecordProcessor`: rejected promise through async wrapper; later log processors skipped;
- `MeterProvider`: rejected promise through async wrapper; later readers skipped;
- NodeSDK: a synchronous trace shutdown failure prevents later signal-provider shutdown calls.

Record:

`artifacts/shutdown-fanout-synchronous-throw.md`

### Why it is not promoted yet

The correct review unit is unresolved. It could be a trace-only correction, equivalent per-signal fixes, a NodeSDK correction, or a shared cross-signal fanout helper.

The desired error policy also needs agreement: fail-fast rejection after attempting every child, or complete error aggregation.

## Retained lead H — metric provider and reader shutdown concurrency

### Evidence state

Prepared tests exist at fork head `026855a81e3f4bb0bca4c46610446648a92a9372`.

Record:

`artifacts/metric-shutdown-concurrency.md`

### Source-predicted behavior

- `MeterProvider` sets `_shutdown` before readers finish;
- a concurrent second provider shutdown resolves successfully while the first remains pending and may later reject;
- `MetricReader` sets `_shutdown` only after `onShutdown()` resolves;
- two concurrent reader shutdown calls can therefore invoke `onShutdown()` twice.

### Proposed direction

Use one shared one-shot future for both provider and reader shutdown so all callers receive one result and child cleanup starts once.

### Why it is not promoted yet

The tests must run, and the review boundary must be chosen: one metrics lifecycle issue with provider and reader changes, or two patches under one agreed contract. This remains separate from reader-constructor transactionality.

## Ambiguity retained — cached metrics objects after shutdown

A direct prepared test now shows that a meter obtained before shutdown can create instruments and update collectable storage afterward. An internal collector can observe those measurements.

New `getMeter()` calls return a no-op meter after provider shutdown, but the specification text is less explicit about objects obtained before shutdown. Cached-meter recording therefore remains a contract question, not a promoted defect.

## Negative lead — logger startup ordering

A concern that instrumentations might remain bound to a no-op logger provider was checked and rejected. The logs API uses a proxy logger provider, and first global registration sets its delegate. Existing proxy logger references can retarget.

## Recommended submission order

1. Candidate A: same-object start guard.
2. Candidate B: repaired failed function-setup cleanup.
3. Run and decide retained lead F without expanding Candidate A silently.
4. Candidate C: discuss the trace-provider contract; use fork PR #4 as supplemental implementation evidence.
5. Run and classify retained lead G; decide whether it belongs with Candidate C or a cross-signal proposal.
6. Run and classify retained lead H as metrics lifecycle work.
7. Candidate D: metric-reader binding transactionality.
8. Candidate E: global installation and disposal design.

Candidates A and B are small implementation candidates but still require target execution. Candidate C now has an isolated fork trial but remains issue-first because its force-flush, failure, and asynchronous reentry contracts need agreement. Candidate D is a lower-level construction issue. Candidate E is the umbrella ownership discussion. Leads F, G, and H are deliberately not counted as promoted proposals yet.

## Current Fieldwork review disposition

Fieldwork PR #32 is draft and held because its branch diverged substantially from current main. The target, programme, and scout issue bodies remain the current discovery surfaces while the synthesis branch is reconciled.

A new complete-diff review is required after reconciliation. The builder is not eligible to be the sole final accepter of a consequential upstream packet.

## What should link to Fieldwork

A future upstream issue can include one optional deep-dive link to the Fieldwork synthesis. Each issue must still be independently understandable and contain its own minimal reproduction.

Suggested deep-dive target after explicit authorization and current-main reconciliation:

https://redirect.github.com/teamleaderleo/fieldwork/pull/32

## Contact boundary

No upstream issue, pull request, comment, review, reaction, or direct backlink has been created.
