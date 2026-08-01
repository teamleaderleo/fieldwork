# Upstream issue draft — lifecycle fanout can skip opening processors

Draft status: `fallback only — direct PR preferred`  
Public interaction authorized: `no`

## Summary

Trace and logs lifecycle fanouts retain mutable processor arrays while starting shutdown or force flush. An earlier processor can remove a later indexed processor before iteration reaches it, causing an opening processor to be skipped.

The aggregate trace and logs paths also invoke processor interfaces directly. A processor can throw before returning its declared promise and stop construction of later promise inputs.

Public `TracerProvider.forceFlush()` has a separate direct fanout. A synchronous processor throw there leaves the processor timeout armed until expiry unless the throw is routed through the existing cleanup path.

## Reproduction

- configure two processors;
- have the first remove the second from the retained array during shutdown or force flush;
- observe that the second opening processor is skipped on the baseline.

For the direct-call aggregate paths, make the first processor throw synchronously and observe that later processor invocation is interrupted. For public trace provider force flush, the later processor is attempted by map semantics, but the first processor's timeout remains armed.

## Expected behavior

Every processor present when lifecycle work begins should be attempted. Current-operation membership should remain stable while future operations observe mutations. A synchronous provider force-flush failure should not leave its timeout active.

## Proposed direction

- snapshot opening processor arrays in `MultiSpanProcessor`, `MultiLogRecordProcessor`, and public `TracerProvider.forceFlush()`;
- convert direct synchronous processor throws into rejected promises without deferring eager invocation;
- preserve existing package-specific error behavior and timeout/result structures.

## Scope

Affected entrypoints:

- `MultiSpanProcessor.shutdown()` / `forceFlush()`;
- `MultiLogRecordProcessor.shutdown()` / `forceFlush()`;
- `TracerProvider.forceFlush()`.

Metrics is excluded: its collector list is internally owned, no supported mutation route was found, and collector lifecycle methods are already async.

## Compatibility

- no public API or type changes;
- one shallow array copy per repaired lifecycle call;
- future mutations remain visible;
- existing trace/log rejection and global-error behavior remains;
- provider force flush retains its current error-array rejection;
- no settle-all aggregation, cancellation, retry, or idempotence change.

## Environment and prior art

- repository revision: `2c931bf4eec18a234a28706567c6977f08139abd`;
- public main matched that revision during repair;
- repository GitHub Actions matrix;
- open issue/PR searches found no equivalent current fix during the repair pass;
- historical PR #802 is context for trace force flush but not an equivalent stable-opening or timer-cleanup repair.

## Filing checklist

- [ ] repeat current-main and duplicate search immediately before filing;
- [ ] confirm reproduction on the then-current public revision;
- [x] exclude unsupported metrics-private-state claims;
- [x] avoid prevalence/severity claims beyond evidence;
- [ ] recheck contribution and AI-disclosure policy;
- [ ] record explicit authority before public interaction.
