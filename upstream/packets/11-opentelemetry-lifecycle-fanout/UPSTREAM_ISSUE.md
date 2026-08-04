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
- retain `Promise.all`, timeout, global-handler, and outward rejection behavior.

## Compatibility

- no public API/type changes;
- eager invocation retained;
- one shallow copy per affected operation;
- future mutation retained;
- aggregate/provider/logs error policies retained;
- no metrics behavior change.

## Limits

No settle-all aggregation, cancellation, retry, idempotence, delayed recursion, or post-shutdown admission changes.

## Environment and prior art

- base/current main during repair: `2c931bf4eec18a234a28706567c6977f08139abd`;
- repository-supported Actions matrix;
- focused two-processor throw/removal fixtures and fake-timer provider control;
- refreshed open issue/PR searches found no equivalent current repair;
- historical PR #802 introduced span-processor force-flush fanout but not stable opening membership or synchronous-failure cleanup.

## Filing checklist

- [ ] repeat current-main and duplicate search at filing time;
- [ ] confirm focused controls on the then-current revision;
- [x] exclude metrics private-state-only behavior;
- [x] avoid prevalence/severity claims beyond evidence;
- [ ] recheck contribution and AI-disclosure policy;
- [ ] record explicit public-contact authority.
