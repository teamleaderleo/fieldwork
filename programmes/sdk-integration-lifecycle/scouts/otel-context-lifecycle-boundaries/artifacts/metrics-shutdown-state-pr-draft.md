# Fix PR draft and fork trial: metrics shutdown state sharing

## In simple words

The metrics provider and reader currently disagree about when shutdown becomes terminal.

`MeterProvider` marks itself shut down before reader cleanup finishes, so a concurrent second caller can report success while the first later fails. `MetricReader` marks itself shut down only after cleanup succeeds, so two concurrent callers can start cleanup twice.

The owned fork trial gives both layers one shared shutdown operation, options set, promise, and result. It deliberately leaves reader-constructor transactionality and cross-reader fanout as separate concerns.

## Status

- owned fork PR: https://redirect.github.com/teamleaderleo/opentelemetry-js/pull/5
- branch: `fieldwork/metrics-shutdown-state`
- base: `7b06368b7362a30ca69c178f43bd94dfbb36f85d`
- exact head: `bddcd1d0cb6d75472a2987ea91e593c32a249fd0`
- package: `@opentelemetry/sdk-metrics`
- work class: upstream-fork research
- evidence class: `target-test-prepared`
- upstream issue or PR opened: `false`

## Current behavior

### MeterProvider

The provider currently:

1. checks a boolean `_shutdown` flag;
2. sets it before invoking readers;
3. returns immediately from every later shutdown call.

A concurrent second caller can therefore resolve while the first remains pending and may later reject.

### MetricReader

The reader currently:

1. checks a boolean `_shutdown` flag;
2. invokes and awaits `onShutdown()`;
3. sets the flag only after success.

Two concurrent callers can both pass the check and invoke `onShutdown()`.

A failed first reader shutdown also leaves the reader retryable, while the owning provider is already terminal.

Characterization record:

`artifacts/metric-shutdown-concurrency.md`

## Implementation trial

Both layers use `BindOnceFuture`, the existing repository primitive already used by the logs SDK.

### First caller wins

The first provider or reader caller stores `ShutdownOptions` and starts the one operation. Concurrent and later callers receive the same promise.

This makes `timeoutMillis` part of the terminal operation identity. A later caller cannot extend or shorten it.

### Shared terminal result

- success is shared;
- rejection is shared;
- synchronous throws become rejection of the shared promise;
- a timeout remains the terminal shared result even if underlying cleanup later completes.

### Terminal state starts immediately

As soon as the one-shot future is called:

- provider `getMeter()` returns a no-op meter;
- provider `forceFlush()` returns the shutdown result;
- reader `collect()` rejects as shutdown;
- reader `forceFlush()` waits for and returns the shutdown result.

### Direct synchronous reentry

A reader can synchronously call provider or reader lifecycle methods from inside shutdown. Returning the owning pending promise would create an immediate cycle.

The trial uses a synchronous invocation guard:

- recursive shutdown returns an immediate resolved no-op;
- recursive force flush returns an immediate resolved no-op;
- ordinary external callers after the synchronous invocation phase receive the shared shutdown promise.

## Prepared tests

### Provider tests

File:

`packages/sdk-metrics/test/MeterProvider.shutdown-state.test.ts`

Cases:

1. concurrent and later callers share one promise, one options set, and one reader shutdown;
2. a synchronous reader throw becomes one shared rejection;
3. new meter acquisition and force flush are blocked as soon as shutdown begins;
4. direct reader-triggered provider shutdown and force flush do not deadlock.

### Reader tests

File:

`packages/sdk-metrics/test/export/MetricReader.shutdown-state.test.ts`

Cases:

1. concurrent and later callers share one promise, one options set, and one `onShutdown()` call;
2. the first caller timeout governs the shared result;
3. a synchronous `onShutdown()` throw becomes one shared rejection;
4. collection and force flush are blocked as soon as shutdown begins;
5. direct recursive reader shutdown and force flush do not deadlock.

## Compatibility questions

This trial changes public lifecycle behavior and therefore remains issue-first.

### Failed reader shutdown becomes terminal

Current reader behavior allows a later retry after failure because `_shutdown` is only set after success. The trial shares the first failure permanently.

Questions:

- Is shutdown conceptually one attempt or retryable cleanup?
- If retry is supported, how can the provider avoid reporting a different result from the reader?
- What state is safe after a partial or timed-out cleanup attempt?

### First timeout wins

Concurrent callers currently start separate reader operations with their own timeouts. The trial gives every caller the first timeout result.

Questions:

- Should later callers be allowed only to wait longer on the same underlying operation?
- Should timeout be caller-local while cleanup ownership remains shared?
- Should the API expose both operation completion and per-caller waiting deadlines?

The narrow trial chooses one shared operation and one shared result because that matches `BindOnceFuture`, but this requires agreement.

### Force flush after failed shutdown

Current provider force flush after shutdown resolves as a no-op. The trial returns the shared shutdown rejection.

This preserves one terminal result but may surprise callers that treat force flush as best effort during teardown.

### Collection blocked when shutdown starts

Current `MetricReader.collect()` remains available until `onShutdown()` succeeds. The trial rejects collection as soon as shutdown begins, matching provider terminal state and preventing new work during cleanup.

## Unresolved asynchronous reentry

The synchronous guard does not solve an async reader that later returns the owning promise:

```ts
async onShutdown() {
  await something;
  return reader.shutdown();
}
```

The same applies to a reader that later returns `provider.shutdown()`.

A general solution may require:

- a lifecycle contract forbidding recursive ownership calls;
- an operation token passed into child cleanup;
- async call-context tracking;
- or promise-cycle detection at the aggregate layer.

The trial does not claim this is solved.

## Separate concerns

### Constructor transactionality

Reader binding during `MeterProvider` construction can partially commit before a later reader throws. That remains Candidate D and is not addressed here.

### Fanout

Provider shutdown still eagerly invokes collectors while constructing `Promise.all` input. A synchronous child throw can skip later readers. That remains the cross-signal fanout lead.

### Cached meters and instruments

Objects obtained before provider shutdown can still write collectable storage. Specification coverage is ambiguous, so this remains a separate contract question.

## Exact diff review

Production changes are limited to:

- replacing the provider boolean with one one-shot future, stored options, and a direct invocation guard;
- replacing the reader boolean with the same structure;
- changing existing terminal checks to use the one-shot state;
- returning the shutdown result from post-shutdown force flush.

Accidental comment and collection-format churn was removed before the trial was frozen.

## Validation

```bash
npm ci --ignore-scripts
npm run compile
npm test --workspace=@opentelemetry/sdk-metrics
```

No target execution receipt or passing suite is claimed.

Current disposition: `EXECUTE`, followed by independent exact-head review and contract discussion.

## Contact boundary

No upstream issue, pull request, comment, review, reaction, or direct backlink was created.
