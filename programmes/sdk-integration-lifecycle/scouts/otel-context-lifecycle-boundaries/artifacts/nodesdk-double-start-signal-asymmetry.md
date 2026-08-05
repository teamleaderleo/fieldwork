# NodeSDK repeated-start signal asymmetry

## Status

- Date: 2026-07-30
- OpenTelemetry JS revision: `7b06368b7362a30ca69c178f43bd94dfbb36f85d`
- Fork branch: `fieldwork/nodesdk-shutdown-lifecycle-characterization`
- Draft fork PR: https://redirect.github.com/teamleaderleo/opentelemetry-js/pull/1
- Upstream contact authorized: `false`
- Upstream contact performed: `false`

## Question

Does calling `NodeSDK.start()` twice fail or split ownership consistently across traces, metrics, and logs?

## Result

No. The three signals have different repeated-start behavior.

### Traces: silent ownership split

The tracing API globally registers a proxy provider. The first successful registration sets provider A as the proxy delegate. A second `NodeSDK.start()` constructs provider B and overwrites the SDK's private `_tracerProvider` field, but duplicate global registration fails and the proxy continues delegating to A.

`NodeSDK.shutdown()` then shuts B down because B is the provider currently stored in the SDK object. Provider A remains globally active but outside the SDK object's ownership.

Pinned sources:

- https://redirect.github.com/open-telemetry/opentelemetry-js/blob/7b06368b7362a30ca69c178f43bd94dfbb36f85d/api/src/api/trace.ts
- https://redirect.github.com/open-telemetry/opentelemetry-js/blob/7b06368b7362a30ca69c178f43bd94dfbb36f85d/api/src/trace/ProxyTracerProvider.ts
- https://redirect.github.com/open-telemetry/opentelemetry-js/blob/7b06368b7362a30ca69c178f43bd94dfbb36f85d/experimental/packages/opentelemetry-sdk-node/src/sdk.ts

Executable characterization:

`experimental/packages/opentelemetry-sdk-node/test/lifecycle-double-start-characterization.test.ts`

### Logs: silent ownership split

The logs API keeps the first globally registered logger provider. A repeated `NodeSDK.start()` constructs logger provider B and overwrites `_loggerProvider`, while `logs.getLoggerProvider()` continues returning provider A.

`NodeSDK.shutdown()` therefore targets B and leaves A globally installed and outside the SDK object's provider field.

Pinned sources:

- https://redirect.github.com/open-telemetry/opentelemetry-js/blob/7b06368b7362a30ca69c178f43bd94dfbb36f85d/experimental/packages/api-logs/src/api/logs.ts
- https://redirect.github.com/open-telemetry/opentelemetry-js/blob/7b06368b7362a30ca69c178f43bd94dfbb36f85d/experimental/packages/sdk-logs/src/LoggerProvider.ts
- https://redirect.github.com/open-telemetry/opentelemetry-js/blob/7b06368b7362a30ca69c178f43bd94dfbb36f85d/experimental/packages/opentelemetry-sdk-node/src/sdk.ts

Executable characterization:

`experimental/packages/opentelemetry-sdk-node/test/lifecycle-double-start-logs-characterization.test.ts`

### Metrics: synchronous failure after partial startup work

A `MetricReader` must throw if it is attached to a second `MeterProvider`. `NodeSDK` stores configured reader instances and reuses them on a repeated `start()`. The second `MeterProvider` construction therefore throws `MetricReader can not be bound to a MeterProvider again.`

This failure happens after `start()` has already called instrumentation registration, context-manager setup, propagator setup, resource detection or merging, and other preceding work. Repeated startup therefore is not transactional: metrics can fail the call after earlier startup side effects have occurred.

Pinned sources:

- https://redirect.github.com/open-telemetry/opentelemetry-js/blob/7b06368b7362a30ca69c178f43bd94dfbb36f85d/api/src/api/metrics.ts
- https://redirect.github.com/open-telemetry/opentelemetry-js/blob/7b06368b7362a30ca69c178f43bd94dfbb36f85d/packages/sdk-metrics/src/export/MetricReader.ts
- https://redirect.github.com/open-telemetry/opentelemetry-js/blob/7b06368b7362a30ca69c178f43bd94dfbb36f85d/experimental/packages/opentelemetry-sdk-node/src/sdk.ts

Executable characterization:

`experimental/packages/opentelemetry-sdk-node/test/lifecycle-double-start-metrics-characterization.test.ts`

## Consequence

Repeated startup begins as an application mistake, but NodeSDK does not handle the mistake as one clear state transition:

- traces silently retain the first global provider while the SDK owns the second;
- logs silently retain the first global provider while the SDK owns the second;
- metrics throw during the second call after earlier startup work has already executed;
- context and propagation duplicate registration also occurs before or around these signal-specific outcomes;
- instrumentation registration is invoked again and its disposer remains unowned.

The result is a mixed state rather than a deterministic no-op or a clean failure before mutation.

## Candidate resolution

The narrowest evidence-backed candidate is a start-state guard on `NodeSDK`:

1. mark successful startup;
2. reject or safely no-op any later `start()` before registration work begins;
3. define behavior after `shutdown()` separately;
4. add tests for trace-only, log-only, metric-only, and mixed-signal configurations;
5. keep any broader instrumentation/global disposal decision separate unless restart is explicitly supported.

This candidate does not require deciding immediately whether `shutdown()` must unregister every process global. It first prevents one SDK object from silently replacing its owned providers while the global APIs retain different providers.

## Validation status

- Source and type-shape review: complete.
- Four fork characterization test files now exist across shutdown/restart and repeated-start cases.
- GitHub Actions runs visible for the fork commits: none at recorded checks.
- Full package execution remains unperformed because the work container cannot install the monorepo dependencies.

Local command:

```bash
npm ci
npm run compile
npm test --workspace=@opentelemetry/sdk-node
```

No upstream issue, pull request, comment, review, reaction, or direct backlink was created.
