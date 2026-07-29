# OpenTelemetry JS async context and retry correlation

## In simple words

OpenTelemetry JS keeps context reliably across ordinary Node.js promises, `async`/`await`, timers, and async resources created while a context is active. It cannot infer ownership for work consumed by an older shared worker, queue, promise, or callback. That boundary needs an explicit captured context or carrier.

The SDK creates parent-child trace relationships from the context supplied at span start. It does not define one universal identity for a logical operation with several retries. Applications and library instrumentations choose that topology: one operation span around the loop, child spans per attempt, events on one span, or links where parentage would misrepresent causality.

The strongest branch candidate is NodeSDK lifecycle teardown. `NodeSDK.start()` registers instrumentations, context, propagation, and providers. `NodeSDK.shutdown()` shuts down providers only. The instrumentation registration disposer is discarded, globals stay registered, and tests clear globals manually before each case. A start → shutdown → start lifecycle therefore has an unowned cleanup boundary that deserves a focused campaign or a documented negative decision.

## Assignment

- Fieldwork issue: #19
- Programme: #13
- Target hub: #4
- Owned path: `programmes/sdk-integration-lifecycle/scouts/otel-async-retry-correlation/report.md`
- Fieldwork branch: `fieldwork/opentelemetry-js/otel-async-retry-correlation`
- Upstream contact authorized: `false`

## Exact revisions and retrieval boundary

- OpenTelemetry JS: `open-telemetry/opentelemetry-js@7b06368b7362a30ca69c178f43bd94dfbb36f85d`
- Revision link: https://redirect.github.com/open-telemetry/opentelemetry-js/commit/7b06368b7362a30ca69c178f43bd94dfbb36f85d
- Retrieved: 2026-07-29
- Fieldwork base: `teamleaderleo/fieldwork@09fe47ac92ec9c0c333b4979011f6321795deff2`
- Local probe runtime: Node.js `v22.16.0`, Linux `6.12.13 x86_64`
- Source execution limit: the work container had no network route and no preinstalled OpenTelemetry packages. The retained probe uses Node's exact `AsyncLocalStorage` primitive and a source-equivalent copy of the pinned retry scheduler. Full upstream package tests remain a falsification step for any promoted campaign.

## Code map

| Boundary | Owning code | Observed contract |
|---|---|---|
| Global context API | [`api/src/api/context.ts`](https://github.com/open-telemetry/opentelemetry-js/blob/7b06368b7362a30ca69c178f43bd94dfbb36f85d/api/src/api/context.ts) | Delegates `active`, `with`, and `bind` to one global manager; falls back to no-op; `disable()` disables and unregisters the manager. |
| Global registration | [`api/src/internal/global-utils.ts`](https://github.com/open-telemetry/opentelemetry-js/blob/7b06368b7362a30ca69c178f43bd94dfbb36f85d/api/src/internal/global-utils.ts) | Rejects duplicate registration unless override is explicitly allowed. |
| Node context storage | [`AsyncLocalStorageContextManager.ts`](https://github.com/open-telemetry/opentelemetry-js/blob/7b06368b7362a30ca69c178f43bd94dfbb36f85d/packages/opentelemetry-context-async-hooks/src/AsyncLocalStorageContextManager.ts) | `active()` reads the current store; `with()` uses `AsyncLocalStorage.run`; `disable()` disables the store. |
| Explicit callback binding | [`AbstractAsyncHooksContextManager.ts`](https://github.com/open-telemetry/opentelemetry-js/blob/7b06368b7362a30ca69c178f43bd94dfbb36f85d/packages/opentelemetry-context-async-hooks/src/AbstractAsyncHooksContextManager.ts) | Wraps functions with `with(context, ...)`; patches one EventEmitter instance so listeners run in the bound context. |
| Legacy Node manager | [`AsyncHooksContextManager.ts`](https://github.com/open-telemetry/opentelemetry-js/blob/7b06368b7362a30ca69c178f43bd94dfbb36f85d/packages/opentelemetry-context-async-hooks/src/AsyncHooksContextManager.ts) | Copies the active stack entry during async resource `init`; deprecated in favour of AsyncLocalStorage. |
| Inter-process propagation API | [`api/src/api/propagation.ts`](https://github.com/open-telemetry/opentelemetry-js/blob/7b06368b7362a30ca69c178f43bd94dfbb36f85d/api/src/api/propagation.ts) | Injection and extraction are explicit carrier operations delegated to one global propagator. |
| W3C trace carrier | [`W3CTraceContextPropagator.ts`](https://github.com/open-telemetry/opentelemetry-js/blob/7b06368b7362a30ca69c178f43bd94dfbb36f85d/packages/opentelemetry-core/src/trace/W3CTraceContextPropagator.ts) | Injects valid unsuppressed span context; extraction marks the result remote and installs it in a derived context. |
| Span parenting and activation | [`packages/sdk-trace/src/Tracer.ts`](https://github.com/open-telemetry/opentelemetry-js/blob/7b06368b7362a30ca69c178f43bd94dfbb36f85d/packages/sdk-trace/src/Tracer.ts) | Uses the supplied or active context as parent; preserves trace ID for valid parents; accepts links; `startActiveSpan` activates the new span context. |
| Span lifecycle | [`packages/sdk-trace/src/Span.ts`](https://github.com/open-telemetry/opentelemetry-js/blob/7b06368b7362a30ca69c178f43bd94dfbb36f85d/packages/sdk-trace/src/Span.ts) | Calls processors on start and end; the caller owns `end()`, status, exception recording, and timing. |
| Node tracer registration | [`NodeTracerProvider.ts`](https://github.com/open-telemetry/opentelemetry-js/blob/7b06368b7362a30ca69c178f43bd94dfbb36f85d/packages/opentelemetry-sdk-trace-node/src/NodeTracerProvider.ts) | Registers a default AsyncLocalStorage manager and W3C trace+baggage propagator when configuration is undefined. |
| Combined Node SDK lifecycle | [`experimental/packages/opentelemetry-sdk-node/src/sdk.ts`](https://github.com/open-telemetry/opentelemetry-js/blob/7b06368b7362a30ca69c178f43bd94dfbb36f85d/experimental/packages/opentelemetry-sdk-node/src/sdk.ts) | Starts instrumentations and global components; shutdown awaits tracer, logger, and meter providers only. |
| Instrumentation registration | [`autoLoader.ts`](https://github.com/open-telemetry/opentelemetry-js/blob/7b06368b7362a30ca69c178f43bd94dfbb36f85d/experimental/packages/opentelemetry-instrumentation/src/autoLoader.ts) | Returns an unload function that disables every registered instrumentation. |
| Instrumentation patch ownership | [`platform/node/instrumentation.ts`](https://github.com/open-telemetry/opentelemetry-js/blob/7b06368b7362a30ca69c178f43bd94dfbb36f85d/experimental/packages/opentelemetry-instrumentation/src/platform/node/instrumentation.ts) | `enable()` installs hooks and patches loaded modules; `disable()` runs unpatch functions. |
| Concrete HTTP request spans | [`instrumentation-http/src/http.ts`](https://github.com/open-telemetry/opentelemetry-js/blob/7b06368b7362a30ca69c178f43bd94dfbb36f85d/experimental/packages/opentelemetry-instrumentation-http/src/http.ts) | Creates one client span for one concrete request, injects its context, binds callbacks and request/response emitters, and ends on response/error/close. |
| Export suppression | [`opentelemetry-core/src/internal/exporter.ts`](https://github.com/open-telemetry/opentelemetry-js/blob/7b06368b7362a30ca69c178f43bd94dfbb36f85d/packages/opentelemetry-core/src/internal/exporter.ts) | Runs exporter calls in a context with tracing suppressed to prevent export recursion. |
| Batch processor shutdown | [`BatchSpanProcessorBase.ts`](https://github.com/open-telemetry/opentelemetry-js/blob/7b06368b7362a30ca69c178f43bd94dfbb36f85d/packages/sdk-trace/src/export/BatchSpanProcessorBase.ts) | Stops accepting ended spans after shutdown begins, flushes buffered spans, then shuts down the exporter. |
| OTLP retry scheduler | [`retrying-transport.ts`](https://github.com/open-telemetry/opentelemetry-js/blob/7b06368b7362a30ca69c178f43bd94dfbb36f85d/experimental/packages/otlp-exporter-base/src/retrying-transport.ts) | Retries the same serialized payload with jittered backoff and a common deadline; the retry timer is not tracked separately by `shutdown()`. |
| OTLP exporter shutdown | [`otlp-export-delegate.ts`](https://github.com/open-telemetry/opentelemetry-js/blob/7b06368b7362a30ca69c178f43bd94dfbb36f85d/experimental/packages/otlp-exporter-base/src/otlp-export-delegate.ts) | Awaits all queued export promises before calling transport shutdown, so ordinary exporter shutdown waits for an in-progress retry chain. |

## Ownership map

| Concern | SDK or instrumentation owns | Application or library integration owns |
|---|---|---|
| Active context in ordinary async descendants | AsyncLocalStorage storage and activation | Initializing the manager before work begins |
| Pre-existing worker, queue, promise, or callback | Explicit `context.bind` and `context.with` tools | Capturing context when enqueueing and restoring it when consuming |
| Trace parenting | Valid parent inheritance, trace ID generation, links | Selecting the logical parent and deciding whether attempts are children, events, or linked spans |
| Cross-process propagation | W3C inject/extract algorithms | Calling inject/extract for custom carriers and preserving headers through retry libraries |
| Concrete HTTP attempt | HTTP instrumentation span, header injection, callback binding, close/error handling | Higher-level logical operation and attempt numbering |
| Span completion | Processor callbacks after `span.end()` | Calling `end()` exactly once after owned work completes; recording status/errors |
| Export retry | Same payload, backoff, deadline, diagnostic messages | Exporter configuration and process shutdown deadline |
| Background work during shutdown | Provider flush and exporter shutdown | Stopping intake and awaiting owned work before SDK shutdown |
| Instrumentation and global teardown | Individual APIs expose disable/unregister; registration returns an unload function | Current NodeSDK leaves combined teardown unowned; process-only users often exit immediately |

## Deterministic probe

Retained files:

- `artifacts/async-retry-probe.js`
- `artifacts/async-retry-probe-output.json`

Run:

```bash
node programmes/sdk-integration-lifecycle/scouts/otel-async-retry-correlation/artifacts/async-retry-probe.js
```

The probe has two parts:

1. A promise consumer created before the logical operation resolves under `ROOT`. Explicitly restoring the captured operation store makes the consumer observe `logical-op-19`. This models a shared queue or worker whose async resource predates the operation.
2. A source-equivalent retry wrapper schedules its retry inside `logical-op-19`. Both sends observe that operation. Calling direct transport `shutdown()` between attempts does not cancel the retry timer, so the second send occurs after the shutdown call.

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

- Creation-time AsyncLocalStorage propagation works across retry timers.
- A detached consumer requires explicit context capture. That is an application or instrumentation boundary.
- Direct retry transport shutdown has no cancellation state. The complete OTLP exporter normally awaits the retry promise before transport shutdown, which prevents a second send after the exporter shutdown promise resolves.

## Test map

### Existing coverage

- [`AsyncHooksContextManager.test.ts`](https://github.com/open-telemetry/opentelemetry-js/blob/7b06368b7362a30ca69c178f43bd94dfbb36f85d/packages/opentelemetry-context-async-hooks/test/AsyncHooksContextManager.test.ts) runs the same suite against AsyncLocalStorage and legacy AsyncHooks. It covers nested `with`, `async`/`await`, timers, concurrent operations, bound functions, EventEmitter listener removal, disable, and instance isolation.
- [`Tracer.test.ts`](https://github.com/open-telemetry/opentelemetry-js/blob/7b06368b7362a30ca69c178f43bd94dfbb36f85d/packages/sdk-trace/test/common/Tracer.test.ts) covers valid-parent inheritance, root spans, links, suppression, active spans, sampler context, and processor context.
- [`retrying-transport.test.ts`](https://github.com/open-telemetry/opentelemetry-js/blob/7b06368b7362a30ca69c178f43bd94dfbb36f85d/experimental/packages/otlp-exporter-base/test/common/retrying-transport.test.ts) covers success, failure, rejection, retryable responses, retry limits, and deadline refusal.
- [`sdk.test.ts`](https://github.com/open-telemetry/opentelemetry-js/blob/7b06368b7362a30ca69c178f43bd94dfbb36f85d/experimental/packages/opentelemetry-sdk-node/test/sdk.test.ts) covers registration and provider shutdown calls. Its `beforeEach` manually disables context, trace, propagation, metrics, and logs, so the suite does not establish cleanup after `NodeSDK.shutdown()`.

### Missing boundary tests

- One logical operation with several attempt spans across promise and timer retries.
- A retry dispatched through an async consumer created before the operation.
- `NodeSDK.start()` → `shutdown()` → second `NodeSDK.start()` in one process.
- Instrumentation enable/disable counts and module unpatching during NodeSDK shutdown.
- OTLP retry backoff concurrent with shutdown, including the guarantee that no send occurs after the top-level shutdown promise resolves.
- Shutdown while an application span or request attempt remains open.

## Application mistakes separated from SDK behaviour

### Application or integration mistakes

1. Starting the SDK after instrumented modules are already loaded.
2. Registering the SDK twice through both preload auto-instrumentation and application code. A prior report of duplicate context, propagation, and trace registration was confirmed as double startup: https://redirect.github.com/open-telemetry/opentelemetry-js/issues/4804
3. Expecting a shared worker or promise created before an operation to acquire that operation's context automatically.
4. Omitting `span.end()` or ending the logical parent before owned retry/background work completes.
5. Starting every attempt as an unrelated root span and expecting the SDK to infer a retry group.
6. Calling SDK shutdown while requests, retries, or background tasks can still create or end spans.
7. Expecting W3C propagation across a custom queue or store without explicit carrier injection and extraction.

### SDK or instrumentation behaviour

1. AsyncLocalStorage preserves context for async resources created while the operation is active.
2. `startSpan` inherits a valid parent; `startActiveSpan` activates the child and leaves end ownership to the callback.
3. HTTP instrumentation creates and closes one span per concrete network request, binds user callbacks to the parent context, and injects the request span context.
4. Exporter calls run with tracing suppressed.
5. OTLP retries reuse the same serialized payload and stay inside one deadline.
6. NodeSDK provider shutdown flushes and closes configured providers.
7. NodeSDK does not currently retain the instrumentation unload function or disable registered global context and propagation during shutdown.

## Ranked branch candidates

### 1. `sdk-node-shutdown-registration-lifecycle`

**Question:** Should `NodeSDK.shutdown()` own the components that `NodeSDK.start()` registered, or should restart and teardown remain explicitly unsupported?

**Why this deserves a campaign:**

- `start()` calls `registerInstrumentations()` and discards its unload function.
- `start()` registers context and propagation globals.
- `shutdown()` only awaits tracer, logger, and meter provider shutdown.
- Global registration rejects a second registration.
- NodeSDK tests manually disable globals before each case, masking lifecycle residue.

**Observable consequence:** instrumentations can remain patched after telemetry providers are shut down; a second SDK instance can hit duplicate registration or continue using stale globals. This affects test runners, plugin hosts, development reloaders, and long-lived processes that rotate telemetry configuration.

**Falsification test:**

1. Create a fake instrumentation with enable/disable counters.
2. Create a spy context manager and propagator.
3. Start SDK A, emit a span, and call `shutdown()`.
4. Assert the intended post-shutdown state: instrumentation disabled or explicitly documented as retained; owned context disabled or explicitly retained; global registration state defined.
5. Start SDK B and assert either clean registration or an intentional documented rejection with no leaked enabled manager.

**Possible outcomes:**

- Add owned teardown to NodeSDK with explicit ordering and tests.
- Add a distinct `stop()`/`dispose()` lifecycle while preserving provider `shutdown()` semantics.
- Record a negative decision that NodeSDK is process-singleton and restart is unsupported, then add tests and documentation that make the contract explicit.

**Likely owning boundary:** `experimental/packages/opentelemetry-sdk-node`, with API-global implications requiring careful review.

### 2. `otlp-retry-shutdown-deadline`

**Question:** Are retry backoff timers always awaited or cancelled within the exporter shutdown deadline, across fetch and Node transports?

**Why retain it:** the retry wrapper tracks no timer handle and direct `shutdown()` delegates immediately. The normal OTLP delegate awaits queued sends first, which appears to preserve the top-level shutdown guarantee. A test should lock that behaviour down and cover long `Retry-After` values, timeout expiry, rejection, and transport shutdown ordering.

**Observable consequence:** an implementation regression could allow telemetry egress after shutdown resolves or keep a process alive through an unexpected backoff window.

**Falsification test:** start a retryable export with fake time, call exporter shutdown during backoff, advance the clock, and assert that every send happens before shutdown resolution and within the configured deadline.

**Likely owning boundary:** `experimental/packages/otlp-exporter-base`.

### 3. `retry-correlation-instrumentation-fixture`

**Question:** Does a specific retrying client library expose enough hooks for its instrumentation to represent one logical operation plus attempt spans without duplicate roots?

**Promotion gate:** choose one real retrying library and reproduce detached or misleading attempt spans. Core OpenTelemetry cannot infer the logical retry group from separate HTTP requests alone.

**Testbed form:** one operation span, deterministic failed attempt, timer backoff, successful attempt, and a detached shared consumer. Assert trace IDs, parent span IDs, attempt count, failure status, header propagation, and shutdown ordering.

**Likely owning boundary:** the specific contrib instrumentation or the application integration. Keep this out of core until a concrete library boundary fails.

## Stensibly trial definition

State: proposed only. No Stensibly branch or label was started.

Scenario:

1. Wrap one Stensibly task execution in `stensibly.operation`.
2. Force attempt 1 to fail, schedule attempt 2 through a timer, and force attempt 2 to succeed.
3. Run the same work once through a pre-existing shared consumer.
4. Record attempt spans with `attempt.number`, outcome, and the same logical operation context.
5. Stop intake, await the operation and attempts, call SDK shutdown, and assert zero spans arrive afterward.

Comparison:

- Baseline: current task execution and telemetry.
- Variant A: active parent span around the retry loop.
- Variant B: explicit context capture at enqueue/dequeue.
- Expected evidence: deterministic span tree and shutdown event ordering.

Add `testbed:stensibly` only after an owned trial branch and retained result exist.

## Negative results and dead ends

1. No core AsyncLocalStorage propagation defect was found for promises, `async`/`await`, timers, or concurrent descendants created inside an active context.
2. Retry correlation has no universal SDK owner. The logical operation and attempt model depends on application or library semantics.
3. The direct retry transport shutdown ordering does not prove that the complete OTLP exporter sends after its shutdown promise resolves; the delegate awaits queued retry promises first.
4. HTTP instrumentation correctly owns one concrete request span. Hidden library retries require a library-specific reproduction.
5. Missing `span.end()`, premature shutdown, double SDK startup, and absent custom-carrier propagation are caller errors under the current contracts.
6. A naming-only retry attribute or semantic-convention proposal would fail this lane's stop condition without a concrete consumer and owning boundary.

## Recommendation

Retain this scout as a finding and open one focused campaign for `sdk-node-shutdown-registration-lifecycle`. Treat `otlp-retry-shutdown-deadline` as a subordinate probe or test addition. Hold the retry-correlation instrumentation branch until a real retrying library or the Stensibly trial demonstrates detached or misleading spans.

Upstream contact remains unauthorized.