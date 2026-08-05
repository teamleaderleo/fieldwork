# Potential issue draft: NodeSDK repeated start leaves mixed provider ownership

## Title

`NodeSDK.start()` called more than once leaves inconsistent provider ownership across traces, logs, and metrics

## Scope

- Package: `@opentelemetry/sdk-node`
- Pinned revision: `7b06368b7362a30ca69c178f43bd94dfbb36f85d`
- Current upstream `sdk.ts`: same source blob at latest recorded check
- Runtime: Node.js 20 or newer
- Upstream contact status: draft only; not submitted

## What happened?

Calling `start()` more than once on the same `NodeSDK` object does not have one consistent outcome.

For tracing and logs, the second call constructs a new provider and stores it in the NodeSDK object, but global registration keeps the provider from the first call. The SDK object and the global API therefore disagree about which provider is active. A later `shutdown()` operates on the second provider held by the SDK object instead of the first provider still used by the global API.

For metrics, the second call attempts to construct another `MeterProvider` with the same configured `MetricReader`. The reader rejects being attached twice, so the second `start()` throws after earlier startup steps have already run.

A same-object start after shutdown behaves similarly: new private providers are constructed while global APIs remain attached to the first providers, which are already shutdown.

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
const firstOwnedProvider = sdk['_tracerProvider'];

sdk.start();
const secondOwnedProvider = sdk['_tracerProvider'];

assert.notStrictEqual(secondOwnedProvider, firstOwnedProvider);
assert.strictEqual(
  (trace.getTracerProvider() as ProxyTracerProvider).getDelegate(),
  firstOwnedProvider
);

await sdk.shutdown(); // shuts secondOwnedProvider
```

After the second start, the global trace proxy still delegates to the first provider while NodeSDK shutdown targets the second provider stored in `_tracerProvider`.

### Logs

The same pattern occurs with `_loggerProvider`: the logs API keeps the first global provider while the SDK object stores the second provider and later shuts down that second provider.

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

Instrumentation registration, context setup, propagation setup, and resource processing are reached before metric-provider construction, so the second call is not transactional.

### Start after shutdown

```ts
sdk.start();
await sdk.shutdown();
sdk.start();
```

The second start creates new private providers. Duplicate global registration keeps the first shutdown providers globally installed, so telemetry does not reach the new providers and shutdown ownership diverges again.

## Expected result

`NodeSDK.start()` should have one documented state transition. A later call on the same object should either:

1. safely do nothing and retain the original providers; or
2. throw before performing registration or resource side effects.

A later shutdown should operate on the same providers used by the global APIs.

## Actual result

- Traces: the global API retains provider A while the SDK object stores provider B.
- Logs: the global API retains provider A while the SDK object stores provider B.
- Metrics: the second call throws after preceding startup work has begun.
- Instrumentation registration and global context or propagation registration are attempted again.
- Start after shutdown creates private providers that do not become global.

## Why this matters

Repeated startup is normally an application mistake, but the SDK currently turns that mistake into inconsistent ownership. This can make shutdown target a provider that was never globally active and can leave the active provider outside the SDK object's ownership.

This is especially difficult to diagnose in test runners, development reloaders, plugin hosts, and applications where initialization can be reached through more than one path.

## Narrow proposed resolution

Add a one-start-attempt guard before any startup side effect:

```ts
private _startAttempted = false;

public start(): void {
  if (this._disabled) {
    return;
  }

  if (this._startAttempted) {
    diag.warn('NodeSDK.start() may only be called once.');
    return;
  }
  this._startAttempted = true;

  // existing startup
}
```

The flag is set before registration. This blocks reentrant calls and prevents a second attempt from compounding partial state after the first attempt throws.

The user-owned fork implements this narrow trial in draft PR:

https://redirect.github.com/teamleaderleo/opentelemetry-js/pull/2

## Tests

The fix branch adds cases proving:

1. repeated start retains the first provider and performs one global registration;
2. start after shutdown does not construct another provider;
3. reentrant start is blocked before registration repeats;
4. a second call after startup failure does not repeat side effects.

The separate characterization branch retains the original failing behaviors and broader lifecycle cases:

- branch: `fieldwork/nodesdk-shutdown-lifecycle-characterization`
- draft PR: https://redirect.github.com/teamleaderleo/opentelemetry-js/pull/1

## Separate follow-up issues

The broader investigation found related but distinct problems that should not enlarge the first patch:

- separate NodeSDK objects and `startNodeSDK()` still compete for process globals;
- `startNodeSDK()` can return `NOOP_SDK` after enabling instrumentation and a context manager;
- metric-provider construction can strand readers before the constructor throws;
- trace-provider shutdown is not one-shot for custom processors;
- custom trace processors can still receive spans after provider shutdown.

These require explicit ownership, construction-transaction, or provider-level fixes.

## Contact boundary

No upstream issue, pull request, comment, review, reaction, or direct backlink has been created.
