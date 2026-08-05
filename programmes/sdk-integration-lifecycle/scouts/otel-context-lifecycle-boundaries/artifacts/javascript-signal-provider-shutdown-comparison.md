# JavaScript signal-provider shutdown comparison

## In simple words

OpenTelemetry JavaScript already implements most of the desired provider shutdown contract in logs and part of it in metrics. Trace is the outlier: it has no provider shutdown state, does not return a no-op tracer after shutdown, does not suppress cached tracers, and delegates every shutdown call again.

This is stronger design evidence than a cross-language analogy because the precedent exists inside the same repository and follows the same OpenTelemetry provider specifications.

## Pinned scope

- repository: `open-telemetry/opentelemetry-js`
- revision: `7b06368b7362a30ca69c178f43bd94dfbb36f85d`
- packages:
  - `@opentelemetry/sdk-trace`
  - `@opentelemetry/sdk-logs`
  - `@opentelemetry/sdk-metrics`
- characterization branch: `fieldwork/nodesdk-shutdown-lifecycle-characterization`
- characterization head at this comparison: `767d90c0da1a7be0abf1b722fd98513cdcfb1b2b`

## Specification baseline

The trace, logs, and metrics SDK specifications use closely aligned provider shutdown language:

- shutdown is called once per provider;
- later provider acquisition is not allowed;
- SDKs should return a valid no-op signal object after shutdown when possible;
- provider shutdown must invoke shutdown on all registered processors or readers.

References:

- trace SDK: https://opentelemetry.io/docs/specs/otel/trace/sdk/#shutdown
- logs SDK: https://opentelemetry.io/docs/specs/otel/logs/sdk/#shutdown
- metrics SDK: https://opentelemetry.io/docs/specs/otel/metrics/sdk/#shutdown

The specifications explicitly constrain new tracer/logger/meter acquisition after shutdown. They are less explicit about signal objects obtained before shutdown, so cached-object behavior should be described as repository precedent and lifecycle coherence rather than quoted as a universal specification requirement.

## Trace provider

Source:

https://redirect.github.com/open-telemetry/opentelemetry-js/blob/7b06368b7362a30ca69c178f43bd94dfbb36f85d/packages/sdk-trace/src/TracerProvider.ts#L39-L150

Current behavior:

- no shutdown-state field;
- no one-shot future or stored shutdown promise;
- `getTracer()` always returns or creates a real SDK `Tracer`;
- cached tracers hold the active processor through their provider-created options;
- every `shutdown()` call delegates again to `MultiSpanProcessor.shutdown()`;
- force flush and shutdown have independent ad hoc aggregation behavior.

Direct prepared characterization:

`packages/sdk-trace/test/common/TracerProvider.shutdown-characterization.test.ts`

It demonstrates:

- two provider shutdown calls reach the custom processor twice;
- a tracer obtained before shutdown still creates recording spans afterward;
- a tracer first obtained after shutdown also creates recording spans;
- both paths continue reaching a custom processor.

## Logs provider

Sources:

- provider: https://redirect.github.com/open-telemetry/opentelemetry-js/blob/7b06368b7362a30ca69c178f43bd94dfbb36f85d/experimental/packages/sdk-logs/src/LoggerProvider.ts#L31-L126
- logger: https://redirect.github.com/open-telemetry/opentelemetry-js/blob/7b06368b7362a30ca69c178f43bd94dfbb36f85d/experimental/packages/sdk-logs/src/Logger.ts#L23-L125

Current behavior:

- `BindOnceFuture` stores the first shutdown operation and result;
- repeated shutdown returns the stored promise;
- new `getLogger()` calls after shutdown return a no-op logger;
- provider shutdown sets shared `hasShutdown` state before processor shutdown;
- cached loggers consult that shared state through `enabled()` and stop emitting;
- force flush after shutdown returns the shutdown promise rather than invoking processors again.

This is the closest JavaScript-internal precedent for the trace-provider candidate.

## Metrics provider

Sources:

- provider: https://redirect.github.com/open-telemetry/opentelemetry-js/blob/7b06368b7362a30ca69c178f43bd94dfbb36f85d/packages/sdk-metrics/src/MeterProvider.ts#L42-L123
- meter: https://redirect.github.com/open-telemetry/opentelemetry-js/blob/7b06368b7362a30ca69c178f43bd94dfbb36f85d/packages/sdk-metrics/src/Meter.ts#L37-L182
- synchronous instruments: https://redirect.github.com/open-telemetry/opentelemetry-js/blob/7b06368b7362a30ca69c178f43bd94dfbb36f85d/packages/sdk-metrics/src/Instruments.ts#L29-L131

Current behavior:

- provider has a boolean `_shutdown` state;
- the state is set before reader shutdown begins;
- repeated shutdown warns and returns without calling readers again;
- new `getMeter()` calls after shutdown return a no-op meter;
- force flush after shutdown warns and returns;
- cached `Meter` and instrument objects do not visibly consult provider shutdown state before registering storage or recording measurements.

The specification clearly requires no-op behavior for new meter acquisition after shutdown. It does not explicitly state in the provider shutdown section whether previously returned meters and instruments must become no-op. Therefore cached-meter recording is retained as an ambiguity, not promoted as a defect without further contract review and execution.

## Cross-signal fanout difference

All three signals still have a separate aggregate-fanout concern when custom children throw synchronously:

- trace may throw before returning a promise and skip later processors;
- logs returns a rejected promise through its async wrapper but skips later processors;
- metrics returns a rejected promise through its async wrapper but skips later readers;
- metrics sets provider terminal state before the failed fanout, so skipped readers cannot be reached by a later shutdown call.

Prepared package-level tests cover shutdown and force flush for all three signals.

## Recommended trace direction

Use the logs provider as the primary implementation precedent:

1. store a one-shot shutdown future or equivalent shared promise;
2. mark shared provider state before invoking child shutdown;
3. return a no-op tracer from `getTracer()` after shutdown;
4. make cached tracers consult shared provider state so they stop creating recording spans;
5. keep aggregate child-fanout robustness as a separately reviewable concern unless maintainers prefer one combined shutdown contract.

Metrics provides additional precedent for setting provider terminal state before child shutdown and returning no-op objects after shutdown.

## Compatibility questions

- Should repeated trace shutdown return the first promise, resolve independently, or report already-shutdown?
- Should a failed first shutdown remain the shared terminal result?
- Should force flush during or after shutdown return the shutdown result, reject, or no-op?
- How should shutdown reentered from a custom processor behave?
- Should cached tracers stop immediately when shutdown begins or only after it resolves?

The logs implementation answers most of these by making shutdown one-shot from the beginning and suppressing cached logger emission immediately.

## Contact boundary

No upstream issue, pull request, comment, review, reaction, or direct backlink was created.
