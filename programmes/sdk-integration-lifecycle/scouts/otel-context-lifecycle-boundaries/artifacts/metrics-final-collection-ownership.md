# Metrics final collection ownership

Status: exact-head executed  
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

- an external caller receives `MetricReader is shutdown` once shutdown begins;
- the reader-owned shutdown operation still waits for an active export, collects final metrics, flushes the exporter, and shuts the exporter down;
- a caller timeout does not silently revoke an underlying cleanup operation that the API documents as able to continue.

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

Fork PR #9 separates public and teardown collection paths.

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

The target-native control creates a real meter and periodic reader, then:

1. begins one force flush;
2. holds the first export open;
3. starts provider shutdown while that export is active;
4. proves public `reader.collect()` rejects after shutdown begins;
5. releases the active export;
6. proves shutdown performs a second, reader-owned final export containing the recorded metric.

This exercises the asynchronous wait boundary that a synchronous-only authorization flag would miss.

## Exact repaired head

```text
5bb520f141759ce003dc002196c43cda4fe96551
```

Exact-head results:

- Unit Tests: passed;
- Lint: passed;
- E2E Tests: passed;
- CodeQL: passed;
- Bundler tests: passed;
- W3C integration: passed;
- API peer dependency: passed;
- workflow security analysis: passed.

The E2E gate that failed on the predecessor now passes on every supported runtime, confirming that the final metric collection is restored while terminal public collection remains enforced.

Evidence class:

- base failure: target-executed product-contract evidence;
- repair mechanism and complete seven-file diff: source-reviewed;
- focused regression and repository matrix: target-executed on the exact repaired head;
- compatibility choices below: held for an explicit review decision.

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

1. receive an independent exact-head disposition on the complete PR #9 contract;
2. keep PR #5 classified as the isolated compatibility-sensitive base;
3. keep PR #9 as the active composition carrier;
4. synchronize #4, #19, #32, #194, and Archive #192 to this exact head and evidence class;
5. decide the remaining compatibility questions without importing #216;
6. no upstream contact occurs without a separate authorization decision.
