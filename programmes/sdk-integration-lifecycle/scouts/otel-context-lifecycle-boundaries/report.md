# OpenTelemetry JS context and lifecycle boundaries

## In simple words

OpenTelemetry JavaScript carries context and telemetry through several independently owned layers: process-global APIs, context managers, SDK providers, processors and readers, exporters, instrumentation, and application shutdown. Ordinary Node.js context propagation is healthy in the retained Promise, `async`/`await`, timer, and concurrent-descendant probe. The consequential findings are lifecycle and ownership failures: repeated or conflicting startup, partial global publication, non-transactional construction, inconsistent shutdown state, skipped children after synchronous failure, final collection during teardown, lifecycle promise recursion, and unclear separation between provider shutdown and installation disposal.

Several bounded fork trials now have exact-head target execution. They do not form one mega-fix. The useful outcome is a set of separately reviewable contracts, with explicit compatibility questions and a clear handoff for the remaining work.

## Assignment

- Fieldwork issue: #19
- Programme: #13
- Target hub: #4
- Signals worker: #194
- Synthesis packet: #32
- Delayed-reentry lane: #216
- Timeout-aftermath lane: #226
- Owned path: `programmes/sdk-integration-lifecycle/scouts/otel-context-lifecycle-boundaries/report.md`
- Fieldwork branch: `fieldwork/opentelemetry-js/otel-async-retry-correlation`
- Upstream contact authorized: `false`

## Source and evidence boundary

- Pinned OpenTelemetry JS source: `7b06368b7362a30ca69c178f43bd94dfbb36f85d`
- Retained local model runtime: Node.js `v22.16.0`, Linux `6.12.13 x86_64`
- Claim scope supported: primarily `mechanism` and `interface`; no ecosystem-impact claim
- Evidence classes used:
  - `source-read` for implementation, tests, specification, and history review;
  - `model-executed` for the async-context probe and delayed-reentry promise graph;
  - `target-test-prepared` for native tests without retained execution;
  - `target-executed` for exact fork heads with retained product-gate runs.

Green CI is not treated as a compatibility decision, and a changelog-only policy failure is separated from product validation.

## System and ownership map

| Boundary | Current owner | Important lifecycle responsibility |
| --- | --- | --- |
| API globals | `@opentelemetry/api` and `@opentelemetry/api-logs` | One process-global implementation per signal; duplicate registration is rejected. |
| Node context | async-hooks context manager | Carries context through descendants created while a context is active. |
| NodeSDK | `@opentelemetry/sdk-node` | Registers instrumentation, context, propagation, and signal providers; later shuts down providers. |
| Function helper | `startNodeSDK()` | Creates components, registers instrumentation, publishes globals, and returns a shutdown handle. |
| Trace provider | `@opentelemetry/sdk-trace` | Tracer admission, processor delivery, force flush, and shutdown. |
| Logs provider | `@opentelemetry/sdk-logs` | Logger admission, processor delivery, and one-shot provider shutdown. |
| Metrics provider and reader | `@opentelemetry/sdk-metrics` | Meter admission, reader binding, collection, final export, force flush, timeout, and shutdown. |
| Signal aggregates | span/log processors and metric collectors | Invoke every owned child and preserve the signal's outward error policy. |
| Application | caller | Stop intake, await owned work, end spans, and choose when provider shutdown may begin. |

Provider shutdown and installation disposal remain different operations. Shutting down exporters or readers does not automatically prove ownership-aware removal of globals, context, propagation, or instrumentation patches.

## Established negative result: ordinary async context

The retained probe and source review found no core AsyncLocalStorage propagation defect for:

- promises created under an active context;
- `async`/`await` descendants;
- timers created under an active context;
- concurrent descendants created while the context is active.

A consumer or scheduler created before the logical operation keeps its older creation context. Explicit capture and restoration at enqueue/dequeue is therefore an application or instrumentation handoff, not a core propagation bug.

Retained files:

- `artifacts/async-retry-probe.js`
- `artifacts/async-retry-probe-output.json`

## Baseline characterization packet

Owned fork PR #1 at `026855a81e3f4bb0bca4c46610446648a92a9372` contains 30 prepared native cases:

- 19 NodeSDK and helper cases;
- 11 direct trace, logs, and metrics cases.

The packet covers repeated start, restart, function setup failure, partial global publication, reader construction, provider shutdown, startup/shutdown interleaving, cross-signal fanout, trace post-shutdown recording, metrics concurrency, and cached-meter behavior. These cases remain `target-test-prepared`; they are not described as executed failures.

## Executed lifecycle directions

### NodeSDK startup and shutdown coordination — fork PR #7

Exact head: `d5abec0e6c979c5152346bf36b2991bdf0aa3d52`

Evidence: `target-executed`; Unit, Lint, E2E, CodeQL, Bundler, W3C, API peer-dependency, and workflow-security passed.

The executed contract is:

- one `NodeSDK` object gets one startup attempt;
- shutdown before start is terminal for later start calls;
- repeated shutdown callers share one promise;
- shutdown requested synchronously during startup waits until startup leaves its critical section;
- providers created before startup completes or throws are included in that shutdown operation;
- synchronous startup failure and asynchronous teardown failure retain separate ownership.

This does not remove process globals or dispose instrumentation/context installation.

### Metrics composed shutdown — fork PR #9

Exact head: `f3740eb9bda8ec22ae81941adcdaf0de0aa3c764`

Evidence: `target-executed`; Unit, Lint, E2E, CodeQL, Bundler, W3C, API peer-dependency, and workflow-security passed.

The accepted issue-first direction provides:

- one provider and reader shutdown operation and result;
- first-caller option and timeout ownership;
- attempt-all reader invocation after synchronous failure;
- terminal public collection from shutdown start;
- protected reader-owned final collection while physical teardown remains unsettled;
- final collection after an overlapping active export;
- preservation of the released unbound-reader diagnostic order;
- no public retry after failed or timed-out shutdown.

A predecessor composition passed most gates but failed E2E across every runtime because one-shot reader state blocked `PeriodicExportingMetricReader` from its final collection. Logs and traces exported while metrics were absent with `MetricReader is shutdown`. That failure is retained as contract evidence for the protected teardown-only collection path.

Durable record: `artifacts/metrics-final-collection-ownership.md`.

### Logs direct synchronous lifecycle reentry — fork PR #8

Exact head: `7d49735173c8467a88afab426a4bf02910a3dd62`

Evidence: `target-executed`; product gates passed, with a changelog-only policy failure recorded separately.

A processor that directly calls and returns `LoggerProvider.shutdown()` or `forceFlush()` during its lifecycle callback no longer receives the aggregate's own pending promise. Ordinary external callers retain the shared one-shot result. Delayed reentry after an async boundary remains separate.

### Logs delayed lifecycle reentry characterization — fork PR #10

Exact head: `6bbd0f34b1e8579840033c7ded88ff8059afbb3f`

Evidence: `target-executed`; the full product matrix passed.

A processor that crosses one async boundary and then returns the same provider's shutdown or post-shutdown force-flush promise creates a pending self-dependency. An unrelated caller joins that same canonical promise and is trapped. The processor is invoked once. This proves the direct synchronous guard is necessary but insufficient for delayed same-owner recursion.

### Metrics delayed lifecycle reentry characterization — fork PR #12

Exact head: `f2682bd4bacfa9999139aad29b02ab2055da0a4a`

Evidence: `target-executed`; the full product matrix passed.

Without timeout, delayed reader/provider recursion remains pending. The metrics reader's operation-owned timeout rejects the shared result and unwinds the observed dependency for every joiner. The underlying cleanup may continue, so late physical settlement and error ownership are now the separate question in issue #226.

## Executed but requiring repair or composition

### Cross-signal attempt-all fanout — fork PR #6

Exact executed head: `80e3b74baf42300aeab92792ce5ca4dd44c37d95`

Evidence: `target-executed`; product gates passed, with a changelog-only policy failure separate.

The safe-call mechanism correctly converts a synchronous child throw into a rejected promise while continuing iteration and preserving each signal's outward error policy. Exact-head review later found a stronger mutation boundary: the implementation maps over live mutable processor or collector arrays. A first child can delete a later entry and make the live iteration skip it.

Disposition: **REPAIR**. “Attempt every opening child” requires a stable opening snapshot before invocation. Green CI on the current branch does not establish that stronger invariant.

### Trace provider one-shot shutdown — fork PR #4

Current head: `fb40c7abb98bc65681b222004ed86619872eca9e`

Evidence: `target-executed` for the current product matrix. Unit, Lint, E2E, CodeQL, Bundler, W3C, API peer-dependency, and workflow-security passed; the changelog-only gate failed because the owned research branch carries no release note.

The provider-state direction now includes:

- one shared provider shutdown operation and result;
- terminal admission for cached and newly requested tracers after shutdown starts;
- post-shutdown tracer construction without consulting the configured user meter provider;
- direct synchronous shutdown and force-flush reentry containment;
- failed-shutdown controls showing admission remains closed and later callers retain the same rejected result.

Delivery remains held pending:

1. composition with repaired attempt-all processor fanout;
2. an explicit contract for spans created before shutdown and ended during or after processor shutdown;
3. final treatment of delayed same-owner lifecycle recursion.

### Trace delayed-reentry characterization — fork PR #15

Current head: `b3e3ec49ae27bb2c5e6bf32ceb1f868473af24f4`

Evidence: `target-executed` for the current clean merge composition; Unit, Lint, E2E, CodeQL, Bundler, W3C, API peer-dependency, and workflow-security passed.

The one-file characterization covers delayed shutdown recursion, delayed force-flush recursion, an unrelated joiner during a self-cycle, a healthy pending-shutdown join and settlement, and cross-provider nesting. The branch was cut before the latest provider-base control, so it still needs one final linear restack after PR #4 stabilizes before it becomes a standalone exact-head receipt.

### Existing spans across trace shutdown — fork PR #16

Current head: `73380c9d2675ba69c812f2bc5a82383faa18a835`

Evidence: `target-test-prepared`; the current workflow matrix is queued.

The prepared tests record current ownership for spans created before shutdown and ended:

- before shutdown as the healthy control;
- while processor shutdown is pending;
- after processor shutdown settles.

The tests characterize current `onEnd` delivery. They do not select whether provider shutdown should await, drop, buffer, reject, or delegate late span completion.

## Source-reviewed or prepared units

### One-start-attempt base — fork PR #2

Head: `14b524ff0c0d8e39321c31be218b0c9ee0ca0b78`

The narrow guard remains useful source evidence, but it has no standalone retained workflow receipt. PR #7 executes the broader stacked startup/shutdown contract.

### Failed `startNodeSDK()` setup cleanup — fork PR #3

Head: `2482d8c49c8b6e01a282a36da55e48b4a4dc8747`

Evidence: `source-read` and `target-test-prepared`; retained exact-head target execution is absent.

The trial creates components, registers instrumentation against the created providers before global publication, and performs best-effort cleanup on failure while preserving the primary setup error. It catches synchronous cleanup failures and observes asynchronous cleanup rejection. It cannot synchronously await cleanup completion or roll back arbitrary side effects inside instrumentation that throws.

### Metrics one-shot base — fork PR #5

Head: `bddcd1d0cb6d75472a2987ea91e593c32a249fd0`

This branch is historical mechanism evidence. PR #9 supersedes it for composition, compatibility, and execution because the base alone blocked final metrics collection and lacked attempt-all fanout.

## Additional promoted design findings

### Metric-reader construction transactionality

`MeterProvider` binds readers sequentially. If a later reader throws because it is already bound, an earlier reader may remain bound to a provider object whose constructor never returned. NodeSDK cannot repair an object it never receives.

Required decision: prevalidation, two-phase reservation/commit, or supported rollback/unbind semantics.

Durable record: `artifacts/meter-provider-reader-binding-issue-draft.md`.

### Process-global installation ownership and disposal

A helper call can publish one component, fail to replace another process-global provider, and return a shutdown handle for private components that are not actually global. Provider shutdown also does not prove ownership-aware removal of context, propagation, providers, or instrumentation patches.

Required decision: define process-singleton installation, installation receipts or ownership tokens, compare-and-remove semantics, and the relationship between shutdown and disposal.

Durable records:

- `artifacts/start-node-sdk-partial-global-publication.md`
- `artifacts/sdk-global-installation-ownership-issue-draft.md`

## Delayed lifecycle recursion contract

Fieldwork issue #216 and PR #221 retain the model and target characterization.

The minimum compatible rule is:

> A lifecycle child must not await the shutdown or force-flush promise of the same owner whose lifecycle callback is awaiting that child.

This is currently a contract boundary, not a portable runtime repair.

Rejected as complete solutions:

- holding the direct synchronous guard active for all asynchronous settlement;
- comparing promise identity;
- caller-local watchdogs;
- suppressing every concurrent call;
- Node-only async context for browser-facing packages;
- detached child completion;
- arbitrary timeouts without a late-cleanup contract.

Credible future directions are explicit lifecycle provenance/capability or a deliberate operation-owned timeout plus unfinished-cleanup and late-error policy where the public API already owns a timeout.

## Timeout aftermath

Issue #226 is ready and unclaimed. Metrics can return a public timeout while physical reader cleanup continues. The required distinction is:

```text
reported_shutdown_result: success | failure | timeout
physical_cleanup_state: pending | succeeded | failed
physical_cleanup_error: retained internally when failed
```

The next worker must characterize late success, late collection/flush/shutdown failure, multiple readers, post-timeout force flush, teardown authority closure, unhandled rejection, duplicate reporting, and process exit before settlement. No retry authority is implied.

## Ambiguities and negative results

- Ordinary Node async context propagation is healthy for the retained cases.
- The logs API proxy behavior rejects the early suspicion that existing logger references are permanently stuck on a no-op provider after first registration.
- Cached meter and instrument recording after provider shutdown is observable, but the specification is not explicit enough about previously returned objects to promote it as a defect.
- Core OpenTelemetry cannot infer one logical retry operation from separate concrete requests without application- or library-specific identity.
- Provider shutdown cannot finish application work that remains open; application quiescence comes first.
- A green repository matrix does not decide compatibility policy, ownership authority, or delayed lifecycle recursion.

## Current decision map

| Unit | Current disposition | Clearing condition |
| --- | --- | --- |
| NodeSDK startup/shutdown coordination | ACCEPT as executed issue-first direction | independent delivery review and upstream authorization if ever submitted |
| Metrics composed shutdown | ACCEPT as executed issue-first direction | timeout-aftermath decision remains separate |
| Logs direct reentry | ACCEPT within direct synchronous boundary | delayed recursion remains separate |
| Cross-signal attempt-all | REPAIR | snapshot opening child collections and add mutation controls |
| Trace provider one-shot | HOLD for delivery | compose repaired fanout, decide existing-span boundary, preserve delayed-reentry hold |
| Trace delayed reentry | EXECUTED characterization; restack required | linearly restack on stable trace provider head |
| Existing trace span boundary | EXECUTE | allow queued PR #16 matrix to settle, then decide ownership contract |
| Failed function setup cleanup | EXECUTE | obtain retained exact-head target receipt |
| Reader construction transactionality | HOLD for design | choose transaction semantics |
| Global installation disposal | HOLD for design | define ownership-aware installation and removal |
| Metrics timeout aftermath | READY | claim issue #226 and execute its matrix |

## Durable artifact index

- `artifacts/upstream-candidate-map.md`
- `artifacts/nodesdk-shutdown-lifecycle-characterization.md`
- `artifacts/nodesdk-start-state-guard-pr-draft.md`
- `artifacts/start-node-sdk-failure-cleanup-pr-draft.md`
- `artifacts/start-node-sdk-partial-global-publication.md`
- `artifacts/tracer-provider-shutdown-contract-issue-draft.md`
- `artifacts/tracer-provider-shutdown-state-pr-draft.md`
- `artifacts/javascript-signal-provider-shutdown-comparison.md`
- `artifacts/lifecycle-fanout-attempt-all-pr-draft.md`
- `artifacts/metric-shutdown-concurrency.md`
- `artifacts/metrics-shutdown-state-pr-draft.md`
- `artifacts/metrics-final-collection-ownership.md`
- `artifacts/meter-provider-reader-binding-issue-draft.md`
- `artifacts/sdk-global-installation-ownership-issue-draft.md`
- `artifacts/lifecycle-reentry-promise-graph.md`
- `artifacts/review-audit-2026-07-30.md`
- `artifacts/review-audit-continued-2026-07-30.md`

## Handoff and repository state

PR #32 is the durable evidence archive, not a merge-ready branch. At review time:

- PR #32 head: `9a9f917f1a6de778fe267c26236ea73e20d2a586`;
- current Fieldwork main: `13481ab6cce6039f5f8c127d5a0509d657f517d8`;
- relation: diverged, 57 commits ahead and 107 commits behind;
- merge base: `09fe47ac92ec9c0c333b4979011f6321795deff2`.

Do not mark PR #32 ready or merge it directly. Materialize the accepted report and artifacts onto a fresh branch from current main, preserve exact evidence classes, exclude obsolete execution machinery, then perform a complete-diff independent review.

The compact restart packet is `artifacts/handoff-2026-07-30.md`.

## Suggested next actions

1. Claim #226 and execute the metrics timeout-aftermath matrix.
2. Let PR #16 settle; decide the pre-existing trace-span ownership boundary.
3. Repair PR #6 with stable opening snapshots and mutation controls.
4. Compose trace provider state with repaired trace processor fanout.
5. Linearly restack PR #15 after PR #4 stabilizes.
6. Obtain exact-head execution for PR #3; run PR #2 standalone only if the narrower base still serves a review purpose.
7. Materialize the synthesis packet onto current Fieldwork main and perform an independent complete-diff review.
8. Keep each eventual upstream item independently understandable and separately authorized.

No upstream issue, pull request, comment, review, reaction, branch, email, or message was created or changed.