# OpenTelemetry JS context and lifecycle boundaries

## In simple words

OpenTelemetry JS divides responsibility across several layers. The API stores global providers and exposes context, tracing, metrics, and propagation. Runtime context managers carry values through asynchronous work. SDK providers create telemetry and pass completed data to processors, readers, and exporters. Instrumentation packages patch libraries and own the lifecycle of the spans or metrics they create. Applications still own initialization order, custom queue boundaries, manual span completion, logical retry grouping, and stopping work before shutdown.

The broad survey found healthy context propagation across ordinary Node.js promises, `async`/`await`, timers, and concurrent descendants created while a context is active. Shared consumers created before an operation require explicit capture and restoration. Retry correlation therefore becomes one example of a wider ownership rule, rather than the starting hypothesis.

The strongest evidence-backed follow-up is NodeSDK lifecycle teardown. `NodeSDK.start()` registers instrumentations, context, propagation, and telemetry providers. `NodeSDK.shutdown()` shuts down providers only. The instrumentation disposer is discarded, global context and propagation remain registered, and tests clear globals manually before each case. A focused campaign should define whether combined teardown belongs to NodeSDK, a separate disposal method, or an explicit process-singleton contract.

## Assignment and correction

- Fieldwork issue: #19
- Programme: #13
- Target hub: #4
- Owned path: `programmes/sdk-integration-lifecycle/scouts/otel-context-lifecycle-boundaries/report.md`
- Fieldwork branch: `fieldwork/opentelemetry-js/otel-async-retry-correlation`
- Issue correction applied: the previous retry-first framing is withdrawn. This report starts with package, API, context, telemetry, instrumentation, export, shutdown, and test boundaries. Retry behavior appears only where target evidence makes it relevant.
- Upstream contact authorized: `false`

## Exact revisions and retrieval boundary

- OpenTelemetry JS: `open-telemetry/opentelemetry-js@7b06368b7362a30ca69c178f43bd94dfbb36f85d`
- Revision link: https://redirect.github.com/open-telemetry/opentelemetry-js/commit/7b06368b7362a30ca69c178f43bd94dfbb36f85d
- Retrieved: 2026-07-29
- Fieldwork base at claim time: `teamleaderleo/fieldwork@09fe47ac92ec9c0c333b4979011f6321795deff2`
- Local probe runtime: Node.js `v22.16.0`, Linux `6.12.13 x86_64`
- Execution limit: the work container had no network route and no preinstalled OpenTelemetry packages. The retained probe uses Node's exact `AsyncLocalStorage` primitive and a source-equivalent copy of the pinned retry scheduler. Full upstream package tests remain a falsification step for any promoted campaign.

## Package and public-entrypoint map

| Layer | Representative code | Ownership |
|---|---|---|
| API globals | [`api/src/api/context.ts`](https://github.com/open-telemetry/opentelemetry-js/blob/7b06368b7362a30ca69c178f43bd94dfbb36f85d/api/src/api/context.ts), [`api/src/api/propagation.ts`](https://github.com/open-telemetry/opentelemetry-js/blob/7b06368b7362a30ca69c178f43bd94dfbb36f85d/api/src/api/propagation.ts), [`api/src/internal/global-utils.ts`](https://github.com/open-telemetry/opentelemetry-js/blob/7b06368b7362a30ca69c178f43bd94dfbb36f85d/api/src/internal/global-utils.ts) | One process-global implementation per API type; no-op fallback before registration; duplicate registration is rejected. |
| Node async context | [`AsyncLocalStorageContextManager.ts`](https://github.com/open-telemetry/opentelemetry-js/blob/7b06368b7362a30ca69c178f43bd94dfbb36f85d/packages/opentelemetry-context-async-hooks/src/AsyncLocalStorageContextManager.ts), [`AbstractAsyncHooksContextManager.ts`](https://github.com/open-telemetry/opentelemetry-js/blob/7b06368b7362a30ca69c178f43bd94dfbb36f85d/packages/opentelemetry-context-async-hooks/src/AbstractAsyncHooksContextManager.ts) | Active-context storage, `with`, function binding, and EventEmitter binding. |
| Legacy Node context | [`AsyncHooksContextManager.ts`](https://github.com/open-telemetry/opentelemetry-js/blob/7b06368b7362a30ca69c178f43bd94dfbb36f85d/packages/opentelemetry-context-async-hooks/src/AsyncHooksContextManager.ts) | Async-resource map and stack; deprecated in favour of AsyncLocalStorage. |
| Trace SDK | [`packages/sdk-trace/src/TracerProvider.ts`](https://github.com/open-telemetry/opentelemetry-js/blob/7b06368b7362a30ca69c178f43bd94dfbb36f85d/packages/sdk-trace/src/TracerProvider.ts), [`Tracer.ts`](https://github.com/open-telemetry/opentelemetry-js/blob/7b06368b7362a30ca69c178f43bd94dfbb36f85d/packages/sdk-trace/src/Tracer.ts), [`Span.ts`](https://github.com/open-telemetry/opentelemetry-js/blob/7b06368b7362a30ca69c178f43bd94dfbb36f85d/packages/sdk-trace/src/Span.ts) | Tracer caching, sampling, IDs, parent inheritance, links, processor callbacks, force-flush, and provider shutdown. |
| Metric SDK | [`packages/sdk-metrics/src/MeterProvider.ts`](https://github.com/open-telemetry/opentelemetry-js/blob/7b06368b7362a30ca69c178f43bd94dfbb36f85d/packages/sdk-metrics/src/MeterProvider.ts), [`MetricReader.ts`](https://github.com/open-telemetry/opentelemetry-js/blob/7b06368b7362a30ca69c178f43bd94dfbb36f85d/packages/sdk-metrics/src/export/MetricReader.ts) | Meter caching, views, readers, collection, force-flush, and shutdown. A shut-down provider returns no-op meters. |
| Node defaults | [`NodeTracerProvider.ts`](https://github.com/open-telemetry/opentelemetry-js/blob/7b06368b7362a30ca69c178f43bd94dfbb36f85d/packages/opentelemetry-sdk-trace-node/src/NodeTracerProvider.ts) | Default AsyncLocalStorage manager plus W3C trace-context and baggage propagation. |
| Combined Node SDK | [`experimental/packages/opentelemetry-sdk-node/src/sdk.ts`](https://github.com/open-telemetry/opentelemetry-js/blob/7b06368b7362a30ca69c178f43bd94dfbb36f85d/experimental/packages/opentelemetry-sdk-node/src/sdk.ts), [`utils.ts`](https://github.com/open-telemetry/opentelemetry-js/blob/7b06368b7362a30ca69c178f43bd94dfbb36f85d/experimental/packages/opentelemetry-sdk-node/src/utils.ts) | Configuration, resource detection, instrumentation registration, global setup, provider construction, and provider shutdown. |
| Instrumentation framework | [`autoLoader.ts`](https://github.com/open-telemetry/opentelemetry-js/blob/7b06368b7362a30ca69c178f43bd94dfbb36f85d/experimental/packages/opentelemetry-instrumentation/src/autoLoader.ts), [`platform/node/instrumentation.ts`](https://github.com/open-telemetry/opentelemetry-js/blob/7b06368b7362a30ca69c178f43bd94dfbb36f85d/experimental/packages/opentelemetry-instrumentation/src/platform/node/instrumentation.ts) | Provider injection, module hooks, patching, unpatching, enable, and disable. Registration returns an unload function. |
| HTTP instrumentation | [`instrumentation-http/src/http.ts`](https://github.com/open-telemetry/opentelemetry-js/blob/7b06368b7362a30ca69c178f43bd94dfbb36f85d/experimental/packages/opentelemetry-instrumentation-http/src/http.ts) | One span per concrete request, carrier injection/extraction, callback and emitter binding, status, metrics, and span close events. |
| Trace batching | [`BatchSpanProcessorBase.ts`](https://github.com/open-telemetry/opentelemetry-js/blob/7b06368b7362a30ca69c178f43bd94dfbb36f85d/packages/sdk-trace/src/export/BatchSpanProcessorBase.ts) | Buffering, scheduling, export suppression, flush, timeout, and exporter shutdown. |
| Export recursion guard | [`opentelemetry-core/src/internal/exporter.ts`](https://github.com/open-telemetry/opentelemetry-js/blob/7b06368b7362a30ca69c178f43bd94dfbb36f85d/packages/opentelemetry-core/src/internal/exporter.ts) | Runs exporter calls with tracing suppressed. |
| OTLP transport and retry | [`retrying-transport.ts`](https://github.com/open-telemetry/opentelemetry-js/blob/7b06368b7362a30ca69c178f43bd94dfbb36f85d/experimental/packages/otlp-exporter-base/src/retrying-transport.ts), [`otlp-export-delegate.ts`](https://github.com/open-telemetry/opentelemetry-js/blob/7b06368b7362a30ca69c178f43bd94dfbb36f85d/experimental/packages/otlp-exporter-base/src/otlp-export-delegate.ts) | Same-payload retry with jitter and a deadline; queued exports are awaited before transport shutdown. |

## Representative lifecycle paths

### Manual trace path

1. Application obtains a tracer from the global API.
2. `Tracer.startSpan()` reads the supplied context or `context.active()`.
3. A valid parent supplies the trace ID and trace state; an invalid or absent parent creates a root trace.
4. The sampler receives the same context passed to the span processor.
5. `SpanImpl` calls `onStart` immediately.
6. The application records attributes, events, status, and exceptions.
7. The application calls `span.end()` exactly once.
8. The processor receives `onEnd`; batching and export follow later.

The SDK owns parent interpretation and processor delivery. The caller owns span completion and the duration of the represented operation.

### Auto-instrumented HTTP path

1. Instrumentation patches `http` and `https` before application use.
2. An outgoing request creates a client span from the active parent.
3. The request span context is injected into headers.
4. User callbacks bind to the parent context; request and response emitters are bound for lifecycle callbacks.
5. Response, error, abort, and close handlers set status and end the span.
6. HTTP duration metrics are recorded from the same concrete request lifecycle.

One network attempt receives one request span. A library that retries several requests owns the larger logical-operation model.

### Metric path

1. NodeSDK constructs a `MeterProvider` when one or more readers exist.
2. The provider installs views and connects each reader to a `MetricCollector`.
3. Instruments record into shared meter state; readers trigger collection and export.
4. `forceFlush()` calls every collector while the provider remains active.
5. `shutdown()` marks the provider shut down and awaits every collector shutdown.
6. Later `getMeter()` calls return a no-op meter.

Metrics have no span-style active-parent requirement. Exemplar or callback context behavior belongs to the metric implementation and the callback's runtime boundary, while reader/export lifecycle belongs to the provider.

### Shutdown path

1. The application stops accepting or scheduling owned work.
2. Open spans and asynchronous callbacks complete.
3. `NodeSDK.shutdown()` concurrently shuts down configured tracer, logger, and meter providers.
4. Trace processors flush and shut down exporters; metric readers shut down through collectors.
5. Current NodeSDK code leaves instrumentation patches and global context/propagation registration in place.

Provider shutdown cannot finish application operations that remain open. Application quiescence comes first.

## Context and propagation ownership

| Boundary | Library behavior | Caller responsibility |
|---|---|---|
| Promise, timer, or async resource created inside active context | AsyncLocalStorage carries the store | Initialize context management before the work begins |
| Shared worker, promise, or queue created earlier | It retains its creation context | Capture at enqueue and restore at consume, or inject/extract through a carrier |
| Function callback | `context.bind()` wraps execution in a chosen context | Bind at the ownership handoff |
| EventEmitter | Manager patches listeners on that emitter instance | Bind the emitter or listeners before events cross the boundary |
| Process or network boundary | Propagator encodes and decodes trace context and baggage | Preserve the carrier and call inject/extract for custom transports |
| Retry timer created inside operation | Context follows the timer | Keep the logical operation active for the intended retry lifetime |
| Retry through a detached scheduler | Scheduler's older context wins | Restore the captured operation context for each attempt |

## Telemetry ownership and application mistakes

### SDK and instrumentation behavior

1. AsyncLocalStorage preserves active context for descendants created under the active operation.
2. W3C propagation injects valid, unsuppressed trace context and marks extracted context remote.
3. Trace SDK preserves valid parent trace identity, supports links, and sends start/end callbacks to processors.
4. Metric SDK owns readers, collection, no-op behavior after shutdown, force-flush, and reader shutdown.
5. HTTP instrumentation owns the span and metric lifecycle of one concrete request.
6. Batch processors buffer completed spans, suppress tracing during export, flush, and shut down exporters.
7. OTLP retries reuse the serialized payload and remain bounded by one timeout deadline.
8. NodeSDK shuts down configured telemetry providers.
9. NodeSDK currently leaves instrumentation unloading and global context/propagation teardown outside its shutdown path.

### Application or integration mistakes

1. Starting instrumentation after target modules are loaded.
2. Starting telemetry twice through both a preload register hook and application code. A prior duplicate-registration report was confirmed as double startup: https://redirect.github.com/open-telemetry/opentelemetry-js/issues/4804
3. Expecting a pre-existing shared worker or promise to acquire a later operation's active context automatically.
4. Omitting `span.end()` or ending a logical parent before owned background work completes.
5. Expecting separate retry attempts to become one logical operation without a parent span, events, links, or explicit attempt metadata.
6. Calling NodeSDK shutdown while requests, callbacks, retries, or manual spans can still finish.
7. Expecting custom queues, stores, or protocols to propagate W3C context without carrier injection and extraction.
8. Reading meters or creating telemetry after provider shutdown and expecting live recording.

## Deterministic probe

Retained files:

- `artifacts/async-retry-probe.js`
- `artifacts/async-retry-probe-output.json`

Run:

```bash
node programmes/sdk-integration-lifecycle/scouts/otel-context-lifecycle-boundaries/artifacts/async-retry-probe.js
```

The probe distinguishes two async ownership cases and one retry/shutdown detail:

1. A promise consumer created before the logical operation resolves under `ROOT`.
2. Explicit restoration of the captured operation store makes the consumer observe `logical-op-19`.
3. A retry timer created inside `logical-op-19` keeps that operation context for both sends.
4. The direct source-equivalent retry wrapper has no timer cancellation in `shutdown()`, so its retry send occurs after the direct shutdown call. The complete OTLP delegate normally awaits the queued retry promise before transport shutdown.

Observed output:

```json
{
  "status": "pass",
  "events": [
    ["pre-existing-consumer", "ROOT"],
    ["explicit-capture", "logical-op-19"],
    ["send-1", "logical-op-19"],
    ["shutdown", "logical-op-19"],
    ["send-2", "logical-op-19"]
  ]
}
```

Interpretation:

- Core creation-time async propagation behaved correctly.
- Detached consumption is an application or instrumentation handoff.
- Retry correlation became relevant only after the context map exposed the detached-scheduler boundary.
- Direct transport shutdown semantics deserve a test, while the ordinary exporter path already awaits queued sends.

## Test map

### Existing coverage

- [`AsyncHooksContextManager.test.ts`](https://github.com/open-telemetry/opentelemetry-js/blob/7b06368b7362a30ca69c178f43bd94dfbb36f85d/packages/opentelemetry-context-async-hooks/test/AsyncHooksContextManager.test.ts) covers nested `with`, `async`/`await`, timers, concurrent operations, function binding, EventEmitter binding, disable, and manager isolation for both Node managers.
- [`Tracer.test.ts`](https://github.com/open-telemetry/opentelemetry-js/blob/7b06368b7362a30ca69c178f43bd94dfbb36f85d/packages/sdk-trace/test/common/Tracer.test.ts) covers parent inheritance, roots, links, suppression, active spans, sampling context, and processor context.
- [`sdk-metrics` provider and reader tests](https://github.com/open-telemetry/opentelemetry-js/tree/7b06368b7362a30ca69c178f43bd94dfbb36f85d/packages/sdk-metrics/test) cover meter creation, readers, collection, force-flush, periodic export, and shutdown behavior.
- [`retrying-transport.test.ts`](https://github.com/open-telemetry/opentelemetry-js/blob/7b06368b7362a30ca69c178f43bd94dfbb36f85d/experimental/packages/otlp-exporter-base/test/common/retrying-transport.test.ts) covers success, failure, rejection, retryable responses, retry limits, and deadline refusal.
- [`sdk.test.ts`](https://github.com/open-telemetry/opentelemetry-js/blob/7b06368b7362a30ca69c178f43bd94dfbb36f85d/experimental/packages/opentelemetry-sdk-node/test/sdk.test.ts) covers registration, configuration, resources, providers, and provider shutdown calls. Its `beforeEach` manually disables context, trace, propagation, metrics, and logs, so the suite does not establish cleanup after `NodeSDK.shutdown()`.

### Missing boundary tests

1. `NodeSDK.start()` → `shutdown()` → second `NodeSDK.start()` in one process.
2. Instrumentation enable/disable counts and module unpatching during NodeSDK shutdown.
3. Explicit post-shutdown expectations for global context and propagation.
4. Shutdown while one application span, HTTP request, metric callback, or retry operation remains active.
5. A pre-existing shared consumer with explicit context capture at enqueue/dequeue.
6. One logical operation with several concrete attempt spans across promise and timer retries.
7. OTLP backoff concurrent with shutdown, including the guarantee that no send occurs after the top-level exporter shutdown promise resolves.

## Ranked branch candidates

### 1. `sdk-node-shutdown-registration-lifecycle`

**Question:** Which components registered by `NodeSDK.start()` does `NodeSDK.shutdown()` own, and does the package support start → shutdown → start in one process?

**Evidence:**

- `start()` calls `registerInstrumentations()` and discards the returned unload function.
- `start()` installs context and propagation globals.
- `shutdown()` awaits tracer, logger, and meter provider shutdown only.
- Global registration rejects duplicate installation.
- SDK tests manually disable globals before each case.

**Consequence:** instrumentations can remain patched after providers close; a second SDK instance can encounter stale global state or duplicate registration. Test runners, plugin hosts, development reloaders, and telemetry reconfiguration flows become ambiguous.

**Falsification:** create a fake instrumentation with patch/unpatch counters, a spy context manager, and two NodeSDK instances. Run start A → telemetry → shutdown A → start B. Assert the intended state after shutdown and the intended second-start result.

**Possible decisions:**

- Make NodeSDK shutdown dispose every component it registered.
- Add a separate `stop()` or `dispose()` operation for unpatching and global teardown.
- Declare NodeSDK process-singleton behavior and add tests and documentation that reject restart cleanly.

### 2. `otel-shutdown-active-work-fixture`

**Question:** Can an integration fixture make the application-before-provider shutdown contract observable across one open span, one HTTP request, and one metric callback?

**Consequence:** applications frequently treat provider shutdown as a request-drain mechanism. A deterministic fixture can show which telemetry finishes, which data is dropped, and which ordering belongs to the application.

**Falsification:** compare shutdown after quiescence with shutdown during active work. Retain span counts, metric collections, callback completion, export timing, and post-shutdown recording behavior.

### 3. `otlp-retry-shutdown-deadline`

**Question:** Are retry backoff timers always awaited or cancelled within the exporter shutdown deadline across fetch and Node transports?

**Evidence:** the retry wrapper tracks no timer handle and direct shutdown delegates immediately. The standard export delegate awaits queued send promises before transport shutdown, so the likely result is a locked-down guarantee or a narrow negative result.

**Falsification:** use fake time, a retryable result with `Retry-After`, and exporter shutdown during backoff. Assert all sends happen before shutdown resolution and within the configured deadline.

### 4. `retry-correlation-instrumentation-fixture`

**Question:** Does one concrete retrying client library expose enough hooks for its instrumentation to represent one logical operation plus attempt spans without duplicate roots?

**Promotion gate:** choose a real library and reproduce detached or misleading attempts. Core OpenTelemetry cannot infer logical retry identity from separate requests.

**Falsification:** assert trace IDs, parent span IDs, links or events, attempt numbers, failure/success status, carrier propagation, and shutdown ordering.

## Stensibly trial definition

State: proposed only. No Stensibly branch or label was started.

1. Wrap one Stensibly task execution in `stensibly.operation`.
2. Record one successful baseline operation.
3. Force a failed attempt and timer retry.
4. Dispatch the same task once through a pre-existing shared consumer.
5. Compare implicit async inheritance with explicit context capture.
6. Record a metric counter and duration for attempts.
7. Stop intake, await owned work, call SDK shutdown, and assert zero telemetry arrives afterward.

Add `testbed:stensibly` only after an owned trial branch and retained result exist.

## Negative results and dead ends

1. No core AsyncLocalStorage propagation defect was found for ordinary promises, `async`/`await`, timers, or concurrent descendants created under an active context.
2. No universal SDK owner exists for logical retry grouping. Application or library semantics choose parent spans, attempt spans, events, or links.
3. The direct retry transport shutdown ordering does not prove that the complete OTLP exporter sends after its shutdown promise resolves; the delegate awaits queued retry promises first.
4. HTTP instrumentation correctly owns one concrete request lifecycle. Hidden library retries require a library-specific reproduction.
5. Missing span completion, late initialization, double SDK startup, absent custom-carrier propagation, and shutdown before quiescence are caller errors under current contracts.
6. A naming-only attribute or semantic-convention proposal fails the lane stop conditions without a concrete consumer and owning boundary.
7. Metric lifecycle review found a clear provider shutdown contract and no evidence-backed metric defect in this pass.

## Recommendation

Promote `sdk-node-shutdown-registration-lifecycle` as the first campaign candidate. Retain `otel-shutdown-active-work-fixture` as the integration testbed that separates application quiescence from provider behavior. Keep `otlp-retry-shutdown-deadline` as a narrower subordinate probe. Defer retry-specific instrumentation work until one real library or the proposed Stensibly trial produces a reproducible ownership failure.

Upstream contact remains unauthorized, and no upstream contact occurred.
