# Upstream issue draft — lifecycle fanout can skip opening processors

Draft status: `fallback only — direct PR preferred`  
Public interaction authorized: `no`

## Summary

Trace and logs lifecycle fanouts can skip a later processor when an earlier callback removes it from the retained processor array during shutdown or force flush.

Direct processor calls can also throw before returning their declared promise, interrupting later invocation. Public `TracerProvider.forceFlush()` performs a separate fanout from `MultiSpanProcessor.forceFlush()` and can leave its per-processor timeout armed after a synchronous throw.

## Expected behavior

Every processor present when the lifecycle operation starts should be attempted. Mutations should affect future operations without shrinking the current opening set. Existing error behavior should remain unchanged, and synchronous failure should not leave an obsolete timeout armed.

## Affected entrypoints

- `MultiSpanProcessor.shutdown()` / `forceFlush()`;
- `TracerProvider.forceFlush()`;
- `MultiLogRecordProcessor.shutdown()` / `forceFlush()`.

Metrics is excluded: `MeterProvider` creates an internal collector list, does not retain the supplied readers array, and prior mutation controls required private-state access.

## Candidate direction

- snapshot each opening processor list;
- convert direct synchronous processor throws into rejected promises using an eager helper;
- let the existing provider force-flush `.catch()` clear its timeout and record the error;
- retain `Promise.all`, timeout, global-handler, and outward rejection behavior;
- retain the current per-call trace force-flush timeout API introduced by PR #6929.

## Compatibility

- no new public API/type changes;
- current `ForceFlushOptions` retained;
- eager invocation retained;
- one shallow copy per affected lifecycle operation;
- future mutation retained;
- aggregate/provider/logs error policies retained;
- no metrics behavior change.

## Limits

No settle-all aggregation, cancellation, retry, idempotence, delayed recursion, or post-shutdown admission changes.

## Environment and prior art

- refreshed current-main base: `f278e3b8427c406c271b8cba2c0f1a9c47c2f15e`;
- exact prepared candidate: `f4cb44bcccffbc0eb39e774284655e0f965cfce1`;
- repository-supported Actions matrix;
- focused two-processor throw/removal fixtures and fake-timer provider control;
- refreshed open and closed issue/PR searches found no equivalent repair;
- historical PR #802 introduced span-processor force-flush fanout but not stable opening membership or synchronous-failure cleanup;
- merged PR #6929 adds per-call trace timeout configuration and is complementary.

## Filing checklist

- [x] current-main and duplicate search refreshed on `2026-08-05`;
- [x] focused controls rebased onto the then-current revision;
- [x] metrics private-state-only behavior excluded;
- [x] prevalence and severity claims limited to available evidence;
- [x] current contribution and changelog policy checked;
- [ ] refresh again immediately before filing;
- [ ] record explicit public-contact authority.
