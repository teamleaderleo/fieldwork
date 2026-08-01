# Upstream issue draft — lifecycle fanout can skip opening processors

Draft status: `fallback only — direct PR preferred`  
Public interaction authorized: `no`

## Summary

Trace, logs, and metrics lifecycle fanouts can skip a later child when an earlier callback removes it from the live collection during shutdown or force flush.

Trace and logs have direct processor-call paths where a synchronous throw can interrupt later invocation. Public `TracerProvider.forceFlush()` has its own fanout, separate from `MultiSpanProcessor.forceFlush()`, and also leaves its per-processor timeout armed when a processor throws synchronously.

## Expected behavior

Every child present when the lifecycle operation starts should be attempted. Mutations should affect future operations without shrinking the current opening set. Existing package-specific error behavior should remain unchanged, and synchronous failure should not leave an obsolete timeout armed.

## Affected entrypoints

- `MultiSpanProcessor.shutdown()` / `forceFlush()`;
- `TracerProvider.forceFlush()`;
- `MultiLogRecordProcessor.shutdown()` / `forceFlush()`;
- `MeterProvider.shutdown()` / `forceFlush()`.

## Candidate direction

- snapshot each opening processor/collector list;
- protect direct trace/log processor calls with eager try/catch;
- in `TracerProvider.forceFlush()`, clear the already-armed timeout on synchronous invocation failure and feed the error through the existing per-processor result path;
- call async metrics collectors directly;
- retain existing `Promise.all`, timeout, and outward error policies.

## Compatibility

- no public API/type changes;
- one shallow copy per affected operation;
- eager invocation retained;
- future mutation retained;
- trace aggregate and provider error policies retained;
- first-rejection/result behavior retained.

## Scope limits

No settle-all aggregation, cancellation, retry, idempotence, final metrics collection, delayed recursion, or post-shutdown telemetry admission changes.

## Environment and prior art

- baseline/current main during repair: `2c931bf4eec18a234a28706567c6977f08139abd`;
- repository-supported Actions matrix;
- two-child direct-throw/removal fixtures and fake-timer provider control;
- refreshed open issue/PR searches found no equivalent current repair;
- historical PR #802 introduced span-processor force-flush fanout but not stable opening membership or synchronous-failure cleanup.

## Filing checklist

- [ ] repeat current-main and duplicate search at filing time;
- [ ] confirm focused controls on the then-current revision;
- [x] distinguish provider, aggregate, logs, and metrics async boundaries;
- [x] avoid prevalence/severity claims beyond evidence;
- [ ] recheck contribution and AI-disclosure policy;
- [ ] record explicit public-contact authority.
