# Potential issue draft: MeterProvider construction can strand an already-bound reader

## Title

`MeterProvider` reader binding is partially committed when a later reader throws

## Scope

- Package: `@opentelemetry/sdk-metrics`
- Observed through: `@opentelemetry/sdk-node`
- Pinned revision: `7b06368b7362a30ca69c178f43bd94dfbb36f85d`
- Draft only; not submitted

## What happened?

`MeterProvider` binds configured readers sequentially in its constructor.

For each reader it:

1. creates a `MetricCollector`;
2. calls `metricReader.setMetricProducer(collector)`;
3. appends the collector to the provider's shared state.

Current implementation:

https://redirect.github.com/open-telemetry/opentelemetry-js/blob/7b06368b7362a30ca69c178f43bd94dfbb36f85d/packages/sdk-metrics/src/MeterProvider.ts#L46-L65

A `MetricReader` rejects being bound a second time. If a provider is constructed with readers `[readerA, readerB]`, and `readerB` is already bound elsewhere, the sequence can be:

1. `readerA` is successfully bound to the new provider's collector;
2. `readerB` throws;
3. the `MeterProvider` constructor does not return;
4. `readerA` remains bound to a partial provider object that the caller cannot access or shut down.

## Minimal characterization

```ts
const strandedReader = new TrackingMetricReader();
const alreadyBoundReader = new TrackingMetricReader();

const existingProvider = new MeterProvider({
  readers: [alreadyBoundReader],
});

assert.throws(
  () =>
    new MeterProvider({
      readers: [strandedReader, alreadyBoundReader],
    }),
  /MetricReader can not be bound to a MeterProvider again/
);

assert.strictEqual(strandedReader.isBound(), true);
assert.strictEqual(strandedReader.shutdownCalls, 0);

await existingProvider.shutdown();
assert.strictEqual(strandedReader.shutdownCalls, 0);
```

The retained fork characterization uses an externally visible reader subclass to prove the first reader remains attached after the constructor throws.

## Expected result

Provider construction should be atomic with respect to reader ownership:

- either all configured readers are eligible and all are bound;
- or construction fails before any reader becomes bound.

A failed constructor should not leave caller-owned readers attached to an unreachable partial object.

## Actual result

Earlier readers can be bound before a later reader throws. The constructor does not return a provider, and the earlier readers cannot be reached through the failed provider for shutdown or reuse.

## Why this matters

- a reader may retain timers, exporters, callbacks, or collector state;
- the caller loses the ability to shut down the partial provider;
- retrying construction with the same reader now fails because the reader was consumed by the failed attempt;
- NodeSDK cannot repair the failure because the provider object was never assigned to it.

## Resolution options

### Option A — prevalidate all readers

Add a non-mutating reader check such as `canBind()` or internal binding-state inspection. Reject the full configuration before creating any collectors.

**Pros:** small conceptual change; no rollback path.

**Cons:** exposes or depends on reader binding state and must be concurrency-safe.

### Option B — two-phase reserve and commit

Readers first reserve binding ownership, then the provider commits collectors after every reservation succeeds.

**Pros:** transactional and concurrency-aware.

**Cons:** larger internal protocol and more states to test.

### Option C — supported unbind rollback

If a later reader throws, detach previously bound readers.

**Pros:** retains the current sequential construction shape.

**Cons:** reader unbinding does not currently appear to be a supported lifecycle operation and may be unsafe after callbacks or timers start.

## Recommended direction

Prefer prevalidation if binding state can be checked safely before mutation. Otherwise introduce a two-phase internal binding protocol.

Do not attempt rollback from NodeSDK after constructor failure; the invariant belongs in the metrics SDK.

## Tests

- one valid reader;
- two valid readers;
- first reader already bound;
- later reader already bound;
- three readers with failure in the middle;
- concurrent attempts to bind the same reader;
- no earlier reader remains bound after failed construction;
- no reader shutdown occurs merely because validation fails.

## Historical context

The repeated NodeSDK start characterization exposed the single-reader error message, but the partial-construction case is distinct and stronger: it demonstrates mutation of an earlier reader during a constructor that ultimately fails.

Obvious issue searches did not find an existing upstream report using the exact binding error text at the time of this draft.

## Supplemental deep dive

After explicit authorization, the issue may link to:

https://redirect.github.com/teamleaderleo/fieldwork/pull/32

The issue should remain independently understandable and reproducible.

## Contact boundary

No upstream issue or PR has been created.