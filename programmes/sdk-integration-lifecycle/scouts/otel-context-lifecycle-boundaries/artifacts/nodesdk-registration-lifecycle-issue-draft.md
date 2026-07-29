# Potential issue draft: NodeSDK repeated start leaves mixed provider ownership

## Title

`NodeSDK.start()` called more than once leaves inconsistent provider ownership across traces, logs, and metrics

## Scope

- Package: `@opentelemetry/sdk-node`
- Pinned revision: `7b06368b7362a30ca69c178f43bd94dfbb36f85d`
- Runtime: Node.js 20 or newer
- Upstream contact status: draft only; not submitted

## What happened?

Calling `start()` more than once on the same `NodeSDK` instance does not have one consistent outcome.

For tracing and logs, the second call constructs a new provider and stores it in the `NodeSDK` instance, but global registration keeps the provider from the first call. The SDK object and the global API therefore disagree about which provider is active. A later `shutdown()` operates on the second provider held by the SDK object instead of the first provider still used by the global API.

For metrics, the second call attempts to construct another `MeterProvider` with the same configured `MetricReader`. The reader rejects being attached twice, so the second `start()` throws after earlier startup steps have already run.

The result is mixed or partially mutated state rather than a deterministic no-op or a failure before side effects.

## Steps to reproduce

### Tracing

```ts
const sdk = new NodeSDK({
  autoDetectResources: false,
  spanProcessors: [new SimpleSpanProcessor({ exporter })],
  textMapPropagator: null,
});

sdk.start();
const firstProvider = trace.getTracerProvider();

sdk.start();
const sdkOwnedProvider = sdk['_tracerProvider'];

assert.notStrictEqual(sdkOwnedProvider, firstProvider);
assert.strictEqual(trace.getTracerProvider(), firstProvider);

await sdk.shutdown();
```

After the second `start()`, the global trace API still uses the first provider while `NodeSDK.shutdown()` targets the second provider stored in `_tracerProvider`.

### Logs

The same pattern occurs with `_loggerProvider`: the logs API keeps the first global provider while the SDK instance stores the second provider and later shuts down that second provider.

### Metrics

```ts
const reader = new PeriodicExportingMetricReader({ exporter });
const sdk = new NodeSDK({
  autoDetectResources: false,
  metricReaders: [reader],
  textMapPropagator: null,
});

sdk.start();
sdk.start(); // throws: MetricReader can not be bound to a MeterProvider again.
```

Instrumentation registration, context setup, propagation setup, and resource processing are reached before metric provider construction, so the second call is not transactional.

## Expected result

`NodeSDK.start()` should have one documented state transition. A repeated call should either:

1. safely do nothing and retain the original providers; or
2. throw before performing registration or resource side effects.

A later `shutdown()` should operate on the same providers used by the global APIs.

## Actual result

- Traces: the global API retains provider A while the SDK object stores provider B.
- Logs: the global API retains provider A while the SDK object stores provider B.
- Metrics: the second call throws after preceding startup work has begun.
- Instrumentation registration and global context or propagation registration are attempted again.

## Why this matters

Repeated startup is normally an application mistake, but the SDK currently turns that mistake into inconsistent ownership. This can make shutdown target a provider that was never globally active and can leave the active provider outside the SDK object's ownership.

This is especially difficult to diagnose in test runners, development reloaders, plugin hosts, and applications where initialization can be reached through more than one path.

## Narrow proposed resolution

Add an instance start-state guard before any startup side effect:

```ts
private _started = false;

public start(): void {
  if (this._disabled) {
    return;
  }
  if (this._started) {
    diag.warn('NodeSDK.start() called more than once. Ignoring.');
    return;
  }
  this._started = true;

  // existing startup
}
```

Add trace-only, log-only, metric-only, and mixed-signal tests proving that a second call does not create providers, rebind readers, repeat instrumentation registration, or change shutdown ownership.

Whether a new `NodeSDK` instance may start after another instance shuts down is a separate lifecycle question and does not need to be solved by this narrow change.

## Reproduction artifacts

The user-owned fork contains source-pinned characterization tests on branch `fieldwork/nodesdk-shutdown-lifecycle-characterization`.

Draft fork PR: https://redirect.github.com/teamleaderleo/opentelemetry-js/pull/1

No upstream issue, pull request, comment, review, reaction, or direct backlink has been created.