# Unit 11 — fix: stabilize lifecycle fanout targets

## In simple words

OpenTelemetry trace and logs shutdown/flush code could skip a processor that was present when the operation started. The source repair is complete on one clean commit. No additional reviewer is being treated as the final authority: this packet is prepared for the repository owner’s decision, with exact-head CI still queued and clearly separated from the completed code repair.

## Current state

`READY FOR OWNER DECISION — source repaired; exact-head workflows queued`

Last refreshed: `2026-08-03`  
Priority-zero parent: `teamleaderleo/fieldwork#435`  
Public upstream contact authorized: `no`

## Contribution

`MultiSpanProcessor` and `MultiLogRecordProcessor` retain mutable processor arrays and previously invoked lifecycle methods while traversing those live arrays. A processor could remove a later opening processor, or throw synchronously before returning its declared promise, preventing later invocation.

Public `TracerProvider.forceFlush()` performs a separate direct fanout. Live mutation could also skip a later processor there, and a synchronous throw bypassed the normal timeout cleanup path.

Metrics is excluded. `MeterProvider` constructs and owns its collector list internally, the earlier mutation controls required private-state access, and `MetricCollector` lifecycle methods are already async.

## Exact identities

- target: `open-telemetry/opentelemetry-js`;
- public base/current-main snapshot: `2c931bf4eec18a234a28706567c6977f08139abd`;
- canonical source branch: `teamleaderleo/opentelemetry-js:upstream/unit-11-lifecycle-fanout-v2`;
- exact clean source head: `db3d9e5e43d5abc6622784acf0ef87f3b038ac91`;
- reviewed pre-squash tree source: `987a2bde097fe2e44531830e38c7c15a59c35c23`;
- owned validation PR: `teamleaderleo/opentelemetry-js#19`;
- superseded source carrier: closed PR #18;
- source relation: ahead 1, behind 0;
- packet branch: `p0/435-unit-11-opentelemetry-lifecycle-fanout`;
- proposed title: `fix(sdk-trace, sdk-logs): invoke all lifecycle processors`.

The squash reused the exact six file blobs from the reviewed pre-squash head. It changed history and identity only, not code or tests.

## Final code boundary

| Area | Production change | Focused tests |
| --- | --- | --- |
| trace multi-processor | snapshot opening processors and eagerly convert direct synchronous throws to rejections | shutdown/force-flush throw and live-removal controls; global-handler cleanup |
| public trace provider | snapshot force-flush targets; route sync throws through existing timeout/error cleanup | later processor attempted, rejection shape retained, timeout cleared, live-removal and real-timeout controls |
| logs | snapshot opening processors and eagerly convert direct synchronous throws while retaining timeout wrapping | shutdown/force-flush throw and live-removal controls |

Changed files:

1. `packages/sdk-trace/src/MultiSpanProcessor.ts`
2. `packages/sdk-trace/src/TracerProvider.ts`
3. `packages/sdk-trace/test/common/MultiSpanProcessor.attempt-all.test.ts`
4. `packages/sdk-trace/test/common/TracerProvider.attempt-all.test.ts`
5. `experimental/packages/sdk-logs/src/MultiLogRecordProcessor.ts`
6. `experimental/packages/sdk-logs/test/common/MultiLogRecordProcessor.attempt-all.test.ts`

No metrics, workflow, dependency, lock, generated, publisher, or research-only file is present.

## Repairs completed

- added stable opening-set snapshots for trace aggregate, public trace provider, and logs;
- normalized direct synchronous lifecycle throws without deferring eager invocation;
- routed provider synchronous failure through existing timer cleanup and error-array handling;
- added the genuine pending-operation timeout control;
- repaired global error-handler test cleanup;
- removed the unsupported private-state metrics path;
- collapsed the source branch from four commits to one commit directly on the pinned base;
- synchronized the owned source PR to the new canonical identity.

## Exact-head workflows

Queued for `db3d9e5e43d5abc6622784acf0ef87f3b038ac91`:

- Unit Tests `30756036668`;
- Lint `30756036660`;
- W3C Trace Context Integration `30756036656`;
- Bundler tests `30756036678`;
- Ensure API Peer Dependency `30756036662`;
- CodeQL Analysis `30756036671`;
- E2E Tests `30756036639`;
- Zizmor GitHub Actions Security Analysis `30756036691`.

Earlier heads provide mechanism and repository-gate evidence, but they are historical rather than exact-head promotion receipts. Queued infrastructure is not being treated as an unresolved code repair.

## Owner decision surface

The code and packet are ready for the repository owner to judge. Before any authorized public filing, refresh public main, duplicate/overlap, contribution policy, and disclosure requirements; then add the root sdk-trace and experimental sdk-logs changelog entries using the real upstream PR number.

## Packet navigation

- [Deep dive](./DEEP_DIVE.md)
- [Approaches](./APPROACHES.md)
- [Tests and receipts](./TESTS.md)
- [Upstream issue fallback](./UPSTREAM_ISSUE.md)
- [Upstream PR draft](./UPSTREAM_PR.md)
- [Review](./REVIEW.md)
- [Handoff](./HANDOFF.md)

## Contact boundary

Public upstream interaction authorized: `false`.  
Public upstream interaction performed: `false`.
