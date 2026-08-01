# Handoff — Unit 11: snapshot lifecycle targets before concurrent fanout

## Current disposition

`REPAIR`

The exact clean candidate passed every named repository workflow group. Complete-diff review found one bounded source and framing defect: metrics needs opening-list snapshots, but its added synchronous safe-call helper is redundant because `MetricCollector.shutdown()` and `forceFlush()` are already async. Trace and logs retain the snapshot-plus-safe-call direction.

## Exact identities

- Reviewed public base: `2c931bf4eec18a234a28706567c6977f08139abd`;
- Owned source branch: [`upstream/unit-11-lifecycle-fanout`](https://github.com/teamleaderleo/opentelemetry-js/tree/upstream/unit-11-lifecycle-fanout);
- Reviewed source head: [`641528c9786f7d027fef4f4a76ae685f7107d394`](https://github.com/teamleaderleo/opentelemetry-js/commit/641528c9786f7d027fef4f4a76ae685f7107d394);
- Validation PR: [`teamleaderleo/opentelemetry-js#18`](https://github.com/teamleaderleo/opentelemetry-js/pull/18);
- Packet branch: [`p0/435-unit-11-opentelemetry-lifecycle-fanout`](https://github.com/teamleaderleo/fieldwork/tree/p0/435-unit-11-opentelemetry-lifecycle-fanout);
- Packet path: `upstream/packets/11-opentelemetry-lifecycle-fanout/`;
- Final packet head: record in the issue #435 handoff after this file is committed.

## Exact-head workflow result

All completed successfully on source head `641528c9786f7d027fef4f4a76ae685f7107d394`:

- Unit Tests `30674494793` — 10 jobs successful;
- E2E Tests `30674494785` — 7 jobs successful;
- Lint `30674494830`;
- Bundler `30674494832`;
- W3C Trace Context Integration `30674494799`;
- Ensure API Peer Dependency `30674494801`;
- CodeQL `30674494779`;
- Zizmor `30674494823`.

These receipts expire for promotion when the source repair moves the head.

## Complete-diff review result

### Keep

- Trace opening snapshots and synchronous safe-call protection.
- Logs opening snapshots and synchronous safe-call protection.
- Metrics opening snapshots.
- Mutation controls for all three packages.
- Trace/logs synchronous-throw regressions and trace handler compatibility control.

### Repair

- Remove the metrics-local `callLifecycle()` helper and wrappers.
- Invoke snapshot collectors directly through existing async `MetricCollector` lifecycle methods.
- Treat metrics synchronous-throw tests as baseline compatibility controls or remove them.
- Ensure no packet or PR wording claims metrics lacked synchronous-throw normalization.

## Why metrics differs

`MetricCollector.forceFlush()` and `MetricCollector.shutdown()` are async methods. A synchronous throw from the underlying reader is already returned as a rejected promise, so `MeterProvider` continues mapping later collectors on the baseline. The actual metrics defect is only live-array mutation during current-operation fanout.

## Continuation steps

1. Repair `packages/sdk-metrics/src/MeterProvider.ts` to snapshot-only.
2. Reclassify or remove metrics throw controls while retaining the mutation regressions.
3. Synchronize validation PR #18 and all packet claims to the new exact source head.
4. Rerun Unit, E2E, Lint, Bundler, W3C, API peer-dependency, CodeQL, and Zizmor workflows.
5. Obtain an eligible independent complete-diff review of the repaired exact head. The current review was performed by the branch builder and is not independent final acceptance.
6. Refresh public main and duplicate/overlap search immediately before authorized filing.
7. Squash the file-level commits if appropriate and add required changelog files using the real PR number.
8. Obtain explicit authority before any public upstream interaction.

## Contact boundary

Public upstream interaction authorized: `false`.  
Public upstream interaction performed: `false`.
