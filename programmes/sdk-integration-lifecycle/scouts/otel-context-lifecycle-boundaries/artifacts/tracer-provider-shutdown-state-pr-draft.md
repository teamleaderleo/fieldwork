# Fix PR draft and fork trial: TracerProvider shutdown state

## In simple words

The JavaScript trace provider is the signal-provider lifecycle outlier. Logs already shares one shutdown promise and suppresses cached loggers; metrics has provider terminal state for new meters. Trace has neither, so repeated shutdown reaches processors repeatedly and cached or newly requested tracers continue creating recording spans.

The owned fork trial adds one provider-level shutdown future and one shared state check in SDK tracers. It deliberately leaves aggregate processor fanout as a separate issue.

## Status

- owned fork PR: https://redirect.github.com/teamleaderleo/opentelemetry-js/pull/4
- branch: `fieldwork/tracer-provider-shutdown-state`
- base: `7b06368b7362a30ca69c178f43bd94dfbb36f85d`
- exact head: `50cd262e326c2a24419bad53c932a688b42224a4`
- work class: upstream-fork research
- evidence class: `target-test-prepared`
- upstream issue or PR opened: `false`

## Proposed title

`fix(sdk-trace): make TracerProvider shutdown one-shot`

## Implementation

### Provider one-shot state

`TracerProvider` uses the same `BindOnceFuture` primitive already exported by `@opentelemetry/core` and used by the logs SDK.

The first shutdown call:

1. marks the one-shot future called before processor shutdown begins;
2. invokes processor shutdown once;
3. stores one promise and terminal result;
4. converts synchronous processor throws into rejection of that promise.

Concurrent and later callers receive the same promise.

### Cached tracer suppression

The internal, non-exported `TracerOptions` gains one callback:

```ts
isShutdown: () => boolean;
```

Every SDK `Tracer` checks that state before sampling, ID generation, trace self-metrics, or span-processor invocation. When shutdown has begun, `startSpan()` returns a non-recording span with the invalid span context.

This covers:

- tracers obtained before shutdown;
- tracers requested while shutdown is pending;
- tracers requested after shutdown resolves or rejects;
- `startActiveSpan()`, because it delegates to `startSpan()`.

A tracer requested after shutdown is behaviorally no-op, though it remains an SDK `Tracer` rather than the API package's internal `NoopTracer` class.

### Force flush after shutdown

Once shutdown begins, provider `forceFlush()` returns the shared shutdown promise rather than invoking processors again. This matches the current logs provider direction.

### Direct synchronous reentry

A custom processor can call `provider.shutdown()` or `provider.forceFlush()` from inside its own synchronous shutdown callback. Returning the provider's pending shutdown promise would otherwise create a direct promise cycle.

The trial uses a synchronous invocation guard:

- recursive shutdown returns an immediate resolved no-op;
- recursive force flush returns an immediate resolved no-op;
- external calls after the synchronous processor-invocation phase receive the shared shutdown promise.

## Prepared tests

File:

`packages/sdk-trace/test/common/TracerProvider.shutdown-state.test.ts`

Cases:

1. concurrent and later shutdown callers receive the same promise and processor shutdown runs once;
2. a synchronous processor throw becomes one shared rejection;
3. a processor returning recursive provider shutdown does not deadlock;
4. a processor force-flushing the provider during shutdown does not deadlock;
5. cached and newly requested tracers become non-recording as soon as shutdown starts;
6. force flush after shutdown begins returns the shutdown result without invoking processor force flush.

## Exact diff review

Production files:

- `packages/sdk-trace/src/TracerProvider.ts`
- `packages/sdk-trace/src/Tracer.ts`
- `packages/sdk-trace/src/types.ts`

The diff was repaired after self-review removed accidental documentation and formatting churn:

- `Tracer.ts` now contains only one field, one assignment, and one early shutdown guard;
- `types.ts` contains one internal option line;
- provider changes are limited to the one-shot state, no-op acquisition behavior, force-flush boundary, and direct reentry guard.

## Unresolved edge

An asynchronously delayed processor can still create a self-cycle if it later returns `provider.shutdown()` after the provider's synchronous invocation guard has cleared:

```ts
async shutdown() {
  await something;
  return provider.shutdown();
}
```

At that point the provider returns the shared outer promise, while the outer promise is waiting for the processor.

A general solution would require one of:

- a processor contract forbidding provider lifecycle recursion;
- fanout-level detection that a child returned the provider's own promise;
- portable async call-context tracking;
- or a different policy for repeated calls that does not share the first result.

The trial does not claim that asynchronous reentry is solved.

## Separate fanout concern

`MultiSpanProcessor.shutdown()` can still stop before later processors when one child throws synchronously. One-shot provider state does not repair that. It may make a failed partial shutdown terminal, which increases the importance of fixing fanout separately.

Do not silently merge the provider-state and fanout proposals without an explicit review decision.

## Validation

```bash
npm ci --ignore-scripts
npm run compile
npm test --workspace=@opentelemetry/sdk-trace
```

No target execution receipt or passing test suite is claimed.

Current disposition: `EXECUTE`, followed by independent exact-head review.

## Contact boundary

No upstream issue, pull request, comment, review, reaction, or direct backlink was created.
