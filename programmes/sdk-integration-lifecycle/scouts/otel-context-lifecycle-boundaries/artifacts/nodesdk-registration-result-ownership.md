# NodeSDK registration-result ownership map

## Status

- Date: 2026-07-30
- OpenTelemetry JS revision: `7b06368b7362a30ca69c178f43bd94dfbb36f85d`
- Upstream contact: none

## Question

Why can `NodeSDK` believe it owns one component while the process-global OpenTelemetry APIs continue using another component?

## Result

`NodeSDK.start()` and its setup helpers invoke several registration functions that explicitly report whether registration succeeded, but the results are not used to establish ownership or trigger cleanup.

This is the common mechanism beneath the repeated-start and second-instance lifecycle findings.

## Registration matrix

| Component | Registration result | Current NodeSDK handling | Divergence consequence |
|---|---|---|---|
| Instrumentations | `registerInstrumentations()` returns an unload function | Return value discarded | SDK cannot undo the patches it requested |
| Context manager | `context.setGlobalContextManager()` returns `boolean` | Setup helper ignores the boolean | A newly enabled manager can fail to become global; NodeSDK does not know which manager is active |
| Propagator | `propagation.setGlobalPropagator()` returns `boolean` | Setup helper ignores the boolean | Requested propagator can fail to become global without changing NodeSDK flow |
| Meter provider | `metrics.setGlobalMeterProvider()` returns `boolean` | NodeSDK stores the newly created provider and ignores the boolean | SDK-owned provider can differ from global provider |
| Tracer provider | `trace.setGlobalTracerProvider()` returns `boolean` | NodeSDK stores the newly created provider and ignores the boolean | Trace proxy can remain delegated to provider A while SDK field points to provider B |
| Logger provider | `logs.setGlobalLoggerProvider()` returns the provider that is globally active | NodeSDK ignores the returned provider and stores the newly created provider | Global logs can retain provider A while SDK field points to provider B |

## Source paths

- `experimental/packages/opentelemetry-sdk-node/src/sdk.ts`
- `experimental/packages/opentelemetry-sdk-node/src/utils.ts`
- `experimental/packages/opentelemetry-instrumentation/src/autoLoader.ts`
- `api/src/api/context.ts`
- `api/src/api/propagation.ts`
- `api/src/api/metrics.ts`
- `api/src/api/trace.ts`
- `experimental/packages/api-logs/src/api/logs.ts`

Pinned source links should use the redirect domain when cited outside the fork:

- https://redirect.github.com/open-telemetry/opentelemetry-js/blob/7b06368b7362a30ca69c178f43bd94dfbb36f85d/experimental/packages/opentelemetry-sdk-node/src/sdk.ts
- https://redirect.github.com/open-telemetry/opentelemetry-js/blob/7b06368b7362a30ca69c178f43bd94dfbb36f85d/experimental/packages/opentelemetry-sdk-node/src/utils.ts
- https://redirect.github.com/open-telemetry/opentelemetry-js/blob/7b06368b7362a30ca69c178f43bd94dfbb36f85d/experimental/packages/opentelemetry-instrumentation/src/autoLoader.ts

## Lifecycle examples

### Same instance started twice

1. First startup creates provider A and registers it globally.
2. Second startup creates provider B.
3. Global registration reports failure or returns the existing provider A.
4. NodeSDK ignores that result and stores provider B.
5. Global calls use A while `shutdown()` uses B.

### New instance after first shutdown

1. SDK A registers global components and later shuts down its providers.
2. Globals remain registered.
3. SDK B creates new components and attempts registration.
4. Registration reports duplicate failure, but SDK B continues and stores its own components.
5. Global APIs remain attached to A's shutdown components while SDK B owns unreachable components.

### Metric failure during repeated startup

1. Instrumentation, context, propagation, and resource setup begin again.
2. A second `MeterProvider` is constructed with the original reader.
3. The reader rejects a second binding.
4. `start()` throws without rollback of preceding work.

## Classification

There are two separable defects or contract gaps:

1. **Repeated call on one SDK instance:** narrow and locally fixable with an instance start-state guard before side effects.
2. **Global registration ownership across SDK instances or restart:** broader. NodeSDK needs either transactional ownership handling, explicit process-singleton behavior, or a separate disposal lifecycle.

The start-state guard should be promoted first because it prevents a clear same-object invariant violation without requiring an immediate decision about process-global teardown.

## Stronger future candidate

A later campaign can test a registration transaction model:

1. retain the instrumentation disposer;
2. make context and propagation setup report success and ownership;
3. check trace and metric registration booleans;
4. use the logger provider returned by global registration;
5. clean up newly created providers when registration fails;
6. define rollback behavior if a later signal fails during startup;
7. ensure `shutdown()` only shuts components actually owned by the SDK instance.

This broader change carries more compatibility risk and should remain separate from the minimal repeated-start guard.

## Negative result

The ignored results do not prove that multiple live NodeSDK instances or restart are supported. They do prove that failed registration is not converted into a clean, explicit ownership decision.