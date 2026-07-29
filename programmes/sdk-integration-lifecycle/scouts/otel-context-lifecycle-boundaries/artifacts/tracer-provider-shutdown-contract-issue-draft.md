# Potential issue draft: TracerProvider shutdown is not provider-level one-shot

## Title

`TracerProvider.shutdown()` can invoke custom processors repeatedly and allow post-shutdown spans

## Scope

- Package: `@opentelemetry/sdk-trace`
- Characterized through: `@opentelemetry/sdk-node`
- Pinned revision: `7b06368b7362a30ca69c178f43bd94dfbb36f85d`
- Draft only; not submitted

## What happened?

The base JavaScript `TracerProvider` delegates every `shutdown()` call directly to its internal processor collection. It does not record provider shutdown state.

As a result:

1. calling `NodeSDK.shutdown()` twice can invoke a custom span processor's `shutdown()` twice; and
2. after shutdown resolves, the globally retained provider can continue returning functional tracers, allowing spans to reach a custom processor.

Built-in processors can conceal the second behavior because some processors independently stop accepting spans after their own shutdown. A custom processor demonstrates that the provider itself is not enforcing the shutdown contract.

Current implementation:

https://redirect.github.com/open-telemetry/opentelemetry-js/blob/7b06368b7362a30ca69c178f43bd94dfbb36f85d/packages/sdk-trace/src/TracerProvider.ts#L148-L150

## Minimal characterization

```ts
class TrackingProcessor implements SpanProcessor {
  shutdownCalls = 0;
  endedSpans = 0;

  onStart(): void {}
  onEnd(): void {
    this.endedSpans += 1;
  }
  forceFlush(): Promise<void> {
    return Promise.resolve();
  }
  shutdown(): Promise<void> {
    this.shutdownCalls += 1;
    return Promise.resolve();
  }
}

const processor = new TrackingProcessor();
const provider = new TracerProvider({ spanProcessors: [processor] });
trace.setGlobalTracerProvider(provider);

await provider.shutdown();
await provider.shutdown();

trace.getTracer('example').startSpan('after-shutdown').end();

assert.strictEqual(processor.shutdownCalls, 2);
assert.strictEqual(processor.endedSpans, 1);
```

The retained fork characterization uses NodeSDK and a custom processor to demonstrate the same boundary.

## Expected result

Provider shutdown should be enforced by the provider, not delegated as an assumption to every processor implementation.

A coherent contract would be:

- the first shutdown call begins shutdown;
- concurrent or later calls share the same result or safely no-op;
- each registered processor receives shutdown at most once;
- after shutdown, new tracers or new spans are no-op;
- cached tracers also stop producing recording spans.

## Actual result

- every provider shutdown call delegates again;
- the provider has no shutdown-state check when returning tracers;
- custom processors can receive both repeated shutdown and post-shutdown spans.

## Cross-language precedent

Go documents that all provider methods are no-op after shutdown and uses atomic state plus per-processor one-shot guards:

https://redirect.github.com/open-telemetry/opentelemetry-go/blob/2776cee15126f0841bd65ad205f576b240883a24/sdk/trace/provider.go#L297-L328

Rust uses atomic state, returns `AlreadyShutdown` on repetition, and produces a no-op tracer after shutdown:

https://redirect.github.com/open-telemetry/opentelemetry-rust/blob/0e78170d712e5046b8ed93b6f99b2b003af15cd7/opentelemetry-sdk/src/trace/provider.rs#L245-L298

Java's aggregate SDK makes shutdown one-shot:

https://redirect.github.com/open-telemetry/opentelemetry-java/blob/6ffe557f36f6d1150556c9e95bfea9fc20e3a49e/sdk/all/src/main/java/io/opentelemetry/sdk/OpenTelemetrySdk.java#L101-L117

Python currently has a related open test-flakiness report containing repeated-provider warnings and repeated-shutdown executor errors. This is contextual evidence, not proof of an identical implementation defect:

https://redirect.github.com/open-telemetry/opentelemetry-python/issues/5113

## Resolution options

### Option A — provider-level state and shared shutdown promise

Record `active`, `shutting-down`, and `shutdown` state. The first call stores a promise; later calls return it.

### Option B — provider-level state and later no-op

The first call performs shutdown; later calls resolve immediately.

### Option C — reject repeated shutdown

Return or throw an explicit already-shutdown error. This is clearest but more disruptive.

## Recommended direction

Use provider-level state and a shared first-shutdown result. Make tracer/span creation no-op after shutdown.

This matches the specification intent while avoiding a new failure from harmless repeated cleanup paths.

## Tests

- two sequential shutdown calls;
- two concurrent shutdown calls;
- recursive shutdown from a custom processor;
- new tracer after shutdown;
- cached tracer after shutdown;
- custom processor receives shutdown once;
- custom processor receives no spans after shutdown.

## Out of scope

- unregistering the global trace provider;
- NodeSDK instrumentation disposal;
- supporting process-level restart;
- metric and log provider shutdown behavior.

## Supplemental deep dive

After explicit authorization, the issue may link to:

https://redirect.github.com/teamleaderleo/fieldwork/pull/32

The issue should remain independently reproducible without requiring the deep-dive link.

## Contact boundary

No upstream issue or PR has been created.