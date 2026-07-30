# Metrics final collection ownership

Status: repairing exact head under execution  
Target: `teamleaderleo/opentelemetry-js`  
Base trial: fork PR #5  
Composition and repair: fork PR #9  
Fieldwork lane: #19  
Signals worker: #194  
Delayed-recursion follow-up: #216  
Upstream contact authorized: `false`

## Question

How can `MetricReader` publish terminal shutdown state immediately while still allowing `PeriodicExportingMetricReader` to perform the final collection that belongs to its own teardown operation?

The public and teardown authorities must remain distinct:

- an external caller must receive `MetricReader is shutdown` once shutdown begins;
- the reader-owned shutdown operation must still wait for an active export, collect final metrics, flush the exporter, and shut the exporter down;
- a caller-local timeout must not silently revoke an underlying cleanup operation that the API documents as able to continue.

## Base-trial failure

Fork PR #5 replaced metrics provider and reader booleans with shared one-shot futures. This corrected contradictory concurrent shutdown outcomes, but it used the shared future's `isCalled` state as the public `collect()` guard.

`PeriodicExportingMetricReader.onShutdown()` performs:

1. interval removal;
2. final force flush;
3. final collection and export;
4. exporter shutdown.

Because the reader's one-shot state is published before `onShutdown()` runs, that internal final collection reached the same public guard as an external caller and rejected with:

```text
MetricReader is shutdown
```

## Exact predecessor evidence

Composition head:

```text
e635de6f2c3e75f4743c8b364cdef8222b3fb4a1
```

Repository results:

- Unit Tests: passed;
- Bundler tests: passed;
- CodeQL: passed;
- W3C integration: passed;
- API peer dependency: passed;
- workflow security analysis: passed;
- Lint: failed on six inherited PR #5 formatting/style findings;
- E2E: failed across every runtime.

Every E2E runtime produced the same contract result:

- logs exported;
- traces exported;
- metrics absent;
- the periodic reader's final collection failed after terminal state publication.

This is retained as product-contract evidence, not harness noise.

## Repair contract

Fork PR #9 now separates public and teardown collection paths.

### Public path

`MetricReader.collect()` checks the shared shutdown state. Once shutdown starts, it rejects immediately and does not reach producers.

### Teardown path

`MetricReader` exposes one protected collection method for subclass-owned shutdown work. It is authorized only while the underlying `onShutdown()` operation remains unsettled.

`PeriodicExportingMetricReader` passes that authority only to its final shutdown run. Normal interval and public force-flush paths continue using public collection.

### Timeout ownership

The teardown authorization follows the underlying `onShutdown()` promise, not the optional timeout wrapper returned to the first caller. If the caller's timeout fires, the documented underlying cleanup may continue with its final collection authority intact.

### Fanout composition

The same stacked branch applies attempt-all safe calls to `MeterProvider.shutdown()` and `forceFlush()`. A synchronous reader throw becomes a rejected promise while later readers are still invoked. The outward aggregate remains fail-first rather than collecting every error.

## Focused regression

The new target-native control creates a real meter and periodic reader, then:

1. begins one force flush;
2. holds the first export open;
3. starts provider shutdown while that export is active;
4. proves public `reader.collect()` rejects after shutdown begins;
5. releases the active export;
6. proves shutdown performs a second, reader-owned final export containing the recorded metric.

This exercises the asynchronous wait boundary that a synchronous-only authorization flag would miss.

## Current exact head

```text
5bb520f141759ce003dc002196c43cda4fe96551
```

Current state at this record:

- workflow security: passed;
- W3C integration: passed;
- Bundler: passed;
- API peer dependency: passed;
- CodeQL: passed;
- Unit, Lint, and E2E: running.

No final passing claim is made until all current exact-head gates settle.

## Remaining compatibility decisions

The repair does not settle:

- terminal versus retryable reader failure;
- first-caller timeout ownership versus caller-local timeout;
- post-failure force-flush behavior;
- full error aggregation versus fail-first rejection;
- asynchronously delayed same-owner lifecycle recursion.

Delayed recursion is separated into Fieldwork #216 so the metrics final-collection repair stays bounded.

## Promotion boundary

Before any production or upstream packet:

1. exact-head Unit, Lint, and E2E must pass;
2. the complete seven-file diff must receive an exact-head review;
3. PR #5 must remain classified as the isolated compatibility-sensitive base;
4. PR #9 must remain the active composition carrier;
5. #4, #19, #32, #194, and Archive #192 must carry the same exact head and evidence class;
6. no upstream contact occurs without a separate authorization decision.
