# Metric provider and reader shutdown concurrency

## In simple words

The metrics SDK has two incompatible ways of trying to make shutdown one-shot.

`MeterProvider` marks itself shut down before its readers finish. A concurrent second caller therefore returns successfully without sharing the first shutdown result—even when the first caller later receives a failure.

`MetricReader` marks itself shut down only after `onShutdown()` finishes. Two concurrent callers can therefore start the reader's cleanup twice.

The provider can report success too early; the reader can perform cleanup more than once. A shared one-shot future would avoid both outcomes.

## Pinned scope

- repository: `open-telemetry/opentelemetry-js`
- revision: `7b06368b7362a30ca69c178f43bd94dfbb36f85d`
- package: `@opentelemetry/sdk-metrics`
- characterization branch: `fieldwork/nodesdk-shutdown-lifecycle-characterization`
- characterization head: `85f8a928dc2385cf506445ed9794c453b70803e3`
- evidence class: `target-test-prepared`

## Provider behavior

Source:

https://redirect.github.com/open-telemetry/opentelemetry-js/blob/7b06368b7362a30ca69c178f43bd94dfbb36f85d/packages/sdk-metrics/src/MeterProvider.ts#L91-L104

`MeterProvider.shutdown()`:

1. returns immediately if `_shutdown` is already true;
2. sets `_shutdown = true` before invoking readers;
3. awaits the first call's reader fanout.

Prepared characterization:

`packages/sdk-metrics/test/MeterProvider.fanout-characterization.test.ts`

The concurrency case:

1. starts a first provider shutdown whose reader promise remains pending;
2. calls provider shutdown again;
3. observes the second call resolve successfully because `_shutdown` is already true;
4. rejects the reader promise;
5. observes the first call reject.

The same provider therefore gives two concurrent callers contradictory terminal results for one shutdown operation.

## Reader behavior

Source:

https://redirect.github.com/open-telemetry/opentelemetry-js/blob/7b06368b7362a30ca69c178f43bd94dfbb36f85d/packages/sdk-metrics/src/export/MetricReader.ts#L287-L302

`MetricReader.shutdown()`:

1. checks `_shutdown`;
2. invokes and awaits `onShutdown()`;
3. sets `_shutdown = true` only after successful completion.

Prepared characterization:

`packages/sdk-metrics/test/export/MetricReader.shutdown-concurrency-characterization.test.ts`

Two shutdown calls made before the first `onShutdown()` resolves both pass the `_shutdown` check and invoke `onShutdown()`. The custom reader records two active cleanup operations.

## Specification pressure

The metrics SDK shutdown contract is described as a once-per-provider operation and requires SDK calls to be concurrency-safe:

https://opentelemetry.io/docs/specs/otel/metrics/sdk/#shutdown

The prepared cases are therefore not merely about an application calling an undocumented internal function. They concern public provider and reader lifecycle behavior under overlapping calls.

## JavaScript-internal precedent

`LoggerProvider` uses `BindOnceFuture`, which:

- marks the operation called before invoking the callback;
- catches synchronous throws;
- stores one shared promise;
- returns that same promise to every caller.

Sources:

- https://redirect.github.com/open-telemetry/opentelemetry-js/blob/7b06368b7362a30ca69c178f43bd94dfbb36f85d/packages/opentelemetry-core/src/utils/callback.ts#L10-L49
- https://redirect.github.com/open-telemetry/opentelemetry-js/blob/7b06368b7362a30ca69c178f43bd94dfbb36f85d/experimental/packages/sdk-logs/src/LoggerProvider.ts#L31-L126

That pattern gives concurrent callers one terminal result and starts child cleanup once.

## Consequences

Provider-level disagreement can cause one caller to proceed as though metrics cleanup completed even though another caller later observes failure. This matters when separate framework layers, signal handlers, test teardown, or application lifecycle hooks converge on the same SDK object.

Reader-level duplication can invoke exporter shutdown, timer cleanup, queue draining, or connection closure twice. Built-in readers may contain repeated calls internally, but the public reader abstraction permits custom implementations.

## Proposed contract

For both `MeterProvider` and `MetricReader`:

- the first shutdown call starts the operation;
- concurrent and later calls return the same promise;
- synchronous exceptions become rejection of that shared promise;
- child cleanup starts at most once;
- a failed first shutdown remains the terminal shared result unless the API explicitly defines retry semantics.

## Likely review units

Two implementation locations are involved:

1. `MeterProvider` provider-level one-shot result sharing;
2. `MetricReader` reader-level one-shot result sharing.

They could be one metrics lifecycle issue with two tightly coupled patches, or separate patches under one agreed contract. They should not be folded into metric-reader constructor transactionality; construction binding and concurrent shutdown are different invariants.

## Relationship to fanout

This lead is adjacent to cross-signal fanout but distinct:

- fanout asks whether every child is attempted when one throws;
- concurrency asks whether multiple callers share one lifecycle operation and result.

A shared lifecycle utility might address both eventually, but the reproductions and compatibility questions should remain separable.

## Validation boundary

The tests are committed in the user-owned fork but have not run in the current environment. No failure or passing suite is claimed.

Local commands:

```bash
npm ci
npm run compile
npm test --workspace=@opentelemetry/sdk-metrics
```

## Contact boundary

No upstream issue, pull request, comment, review, reaction, or direct backlink was created.
