# Potential issue draft: TracerProvider shutdown is not provider-level one-shot

## Title

`TracerProvider.shutdown()` can run processors repeatedly and return recording tracers afterward

## Scope

- package: `@opentelemetry/sdk-trace`
- pinned revision: `7b06368b7362a30ca69c178f43bd94dfbb36f85d`
- direct characterization: `packages/sdk-trace/test/common/TracerProvider.shutdown-characterization.test.ts`
- supporting NodeSDK characterization: `experimental/packages/opentelemetry-sdk-node/test/lifecycle-tracer-provider-shutdown-characterization.test.ts`
- draft only; not submitted

## What happened?

The JavaScript base `TracerProvider` has no provider shutdown state. It always returns or creates a real SDK tracer, and every call to `shutdown()` delegates again to the active processor collection.

Current implementation:

https://redirect.github.com/open-telemetry/opentelemetry-js/blob/7b06368b7362a30ca69c178f43bd94dfbb36f85d/packages/sdk-trace/src/TracerProvider.ts#L39-L150

Direct prepared tests demonstrate:

1. two sequential provider shutdown calls invoke a custom processor's `shutdown()` twice;
2. a tracer obtained before shutdown still creates recording spans afterward;
3. a tracer first obtained after shutdown also creates recording spans;
4. both cached and new tracer paths continue reaching a custom processor.

Built-in processors can conceal the post-shutdown behavior because some independently stop accepting spans. A custom processor isolates the missing provider-level contract.

## Specification baseline

The tracing SDK specification says that after shutdown, later attempts to get a tracer are not allowed and SDKs should return a valid no-op tracer when possible:

https://opentelemetry.io/docs/specs/otel/trace/sdk/#shutdown

The specification also requires provider shutdown to invoke shutdown on all internal processors.

The current implementation satisfies processor delegation but not the no-op tracer direction, and it performs that delegation repeatedly rather than making the provider lifecycle one-shot.

The specification is less explicit about tracers obtained before shutdown. Cached-tracer suppression is therefore framed as lifecycle coherence and same-repository precedent rather than as a quoted universal requirement.

## JavaScript-internal precedent

### LoggerProvider

`@opentelemetry/sdk-logs` already implements the stronger provider contract:

- `BindOnceFuture` stores the first shutdown call and promise;
- repeated shutdown returns the stored promise;
- new logger requests after shutdown return a no-op logger;
- provider shutdown sets shared `hasShutdown` state before child shutdown;
- cached loggers consult shared state and stop emitting.

Sources:

- https://redirect.github.com/open-telemetry/opentelemetry-js/blob/7b06368b7362a30ca69c178f43bd94dfbb36f85d/experimental/packages/sdk-logs/src/LoggerProvider.ts#L31-L126
- https://redirect.github.com/open-telemetry/opentelemetry-js/blob/7b06368b7362a30ca69c178f43bd94dfbb36f85d/experimental/packages/sdk-logs/src/Logger.ts#L23-L125

### MeterProvider

`@opentelemetry/sdk-metrics` also has provider terminal state:

- `_shutdown` is set before reader shutdown;
- repeated shutdown does not call readers again;
- new meter requests after shutdown return a no-op meter;
- force flush after shutdown does not call readers.

Source:

https://redirect.github.com/open-telemetry/opentelemetry-js/blob/7b06368b7362a30ca69c178f43bd94dfbb36f85d/packages/sdk-metrics/src/MeterProvider.ts#L42-L123

This makes trace the provider-level lifecycle outlier inside the JavaScript repository.

Detailed comparison:

`artifacts/javascript-signal-provider-shutdown-comparison.md`

## Minimal characterization

```ts
const processor: SpanProcessor = {
  shutdownCalls: 0,
  onStart() {},
  onEnd() {
    endedSpans += 1;
  },
  forceFlush: () => Promise.resolve(),
  shutdown() {
    shutdownCalls += 1;
    return Promise.resolve();
  },
};

const provider = new TracerProvider({ spanProcessors: [processor] });
const cachedTracer = provider.getTracer('cached');

await provider.shutdown();
await provider.shutdown();

cachedTracer.startSpan('cached-after-shutdown').end();
provider.getTracer('new').startSpan('new-after-shutdown').end();

assert.strictEqual(shutdownCalls, 2);
assert.strictEqual(endedSpans, 2);
```

The retained fork uses separate direct tests with typed custom processors.

## Expected result

Provider shutdown should be enforced at the provider boundary.

A coherent JavaScript contract would be:

- the first shutdown call begins provider shutdown;
- concurrent and later calls share the first result or safely no-op;
- each registered processor receives shutdown at most once;
- `getTracer()` after shutdown returns a no-op tracer;
- cached tracers stop creating recording spans once provider shutdown begins;
- force flush during or after shutdown has an explicit, deterministic result.

## Actual result

- every provider shutdown call delegates again;
- the provider has no shutdown-state check in `getTracer()`;
- cached tracers retain a real processor path;
- custom processors can receive repeated shutdown and post-shutdown spans.

## Recommended direction

Use the logs provider pattern as the primary same-repository precedent:

1. add a one-shot shutdown future or stored promise;
2. set shared provider shutdown state before invoking child shutdown;
3. return a no-op tracer from later `getTracer()` calls;
4. make cached tracers consult shared provider state;
5. define force-flush behavior during and after shutdown.

A failed first shutdown should probably remain the shared terminal result rather than allowing a later call to retry a partially completed shutdown silently. Maintainer agreement is needed.

## Required tests

- two sequential shutdown calls;
- two concurrent shutdown calls;
- shutdown reentered from a custom processor;
- first shutdown rejection and repeated call result;
- new tracer after shutdown;
- cached tracer after shutdown;
- custom processor receives shutdown once;
- custom processor receives no spans after shutdown begins;
- force flush during shutdown;
- force flush after shutdown.

## Relationship to fanout issue

A separate cross-signal lead shows that synchronous child exceptions can skip later processors or readers during shutdown and force flush.

That concern may be reviewed separately because:

- provider one-shot state answers *whether lifecycle may run again*;
- fanout robustness answers *whether every owned child is attempted during the one allowed lifecycle operation*.

Do not silently combine them unless maintainers prefer one broader trace shutdown discussion.

## Cross-language precedent

Go makes provider methods no-op after shutdown and uses atomic state plus one-shot processor shutdown:

https://redirect.github.com/open-telemetry/opentelemetry-go/blob/2776cee15126f0841bd65ad205f576b240883a24/sdk/trace/provider.go#L297-L328

Rust records shutdown atomically, reports repeated shutdown, and returns a no-op tracer afterward:

https://redirect.github.com/open-telemetry/opentelemetry-rust/blob/0e78170d712e5046b8ed93b6f99b2b003af15cd7/opentelemetry-sdk/src/trace/provider.rs#L245-L298

Java's aggregate SDK makes shutdown one-shot:

https://redirect.github.com/open-telemetry/opentelemetry-java/blob/6ffe557f36f6d1150556c9e95bfea9fc20e3a49e/sdk/all/src/main/java/io/opentelemetry/sdk/OpenTelemetrySdk.java#L101-L117

These are supporting design precedents. The JavaScript specification and JavaScript logs/metrics implementations are the primary contract evidence.

## Out of scope

- uninstalling the global tracer provider;
- NodeSDK instrumentation disposal;
- process-level restart;
- metric cached-instrument behavior after shutdown;
- cross-signal fanout implementation unless deliberately combined.

## Supplemental deep dive

After explicit authorization, the issue may include one supplemental link to the Fieldwork synthesis:

https://redirect.github.com/teamleaderleo/fieldwork/pull/32

The issue must remain independently understandable without that link.

## Contact boundary

No upstream issue, pull request, comment, review, reaction, or direct backlink has been created.
