# Unit 11 — fix: stabilize lifecycle fanout targets

## In simple words

OpenTelemetry trace and logs shutdown/flush code could skip a processor that was present when the operation started. The repaired candidate is one clean six-file commit, all eight exact-head workflows passed, and an independent exact-head technical review found no blocking defect. This is ready for the repository owner’s decision.

## Current state

`TECHNICALLY READY — OWNER DECISION REQUESTED`

Last refreshed: `2026-08-03`  
Priority-zero parent: `teamleaderleo/fieldwork#435`  
Public upstream contact authorized: `no`

## Contribution

`MultiSpanProcessor` and `MultiLogRecordProcessor` previously traversed retained mutable processor arrays while invoking lifecycle methods. A processor could remove a later opening processor, or throw synchronously before returning its declared promise, preventing later invocation.

Public `TracerProvider.forceFlush()` performs a separate direct fanout. Live mutation could skip a later processor there, and a synchronous throw bypassed normal timeout cleanup.

The candidate snapshots the opening processor set and converts only direct synchronous throws into rejected promises while preserving eager invocation and each surface’s existing settlement policy. The provider path now routes synchronous failure through its existing timeout-clearing and error-array path.

Metrics is excluded because the earlier mutation controls required private-state access and metric collector lifecycle methods are already async.

## Exact identities

- target: `open-telemetry/opentelemetry-js`;
- public base/current-main snapshot: `2c931bf4eec18a234a28706567c6977f08139abd`;
- canonical source branch: `teamleaderleo/opentelemetry-js:upstream/unit-11-lifecycle-fanout-v2`;
- exact clean source head: `db3d9e5e43d5abc6622784acf0ef87f3b038ac91`;
- owned source PR: `teamleaderleo/opentelemetry-js#19`;
- source relation: ahead 1, behind 0;
- packet branch: `p0/435-unit-11-opentelemetry-lifecycle-fanout`;
- proposed title: `fix(sdk-trace, sdk-logs): invoke all lifecycle processors`.

## Final code boundary

1. `packages/sdk-trace/src/MultiSpanProcessor.ts`
2. `packages/sdk-trace/src/TracerProvider.ts`
3. `packages/sdk-trace/test/common/MultiSpanProcessor.attempt-all.test.ts`
4. `packages/sdk-trace/test/common/TracerProvider.attempt-all.test.ts`
5. `experimental/packages/sdk-logs/src/MultiLogRecordProcessor.ts`
6. `experimental/packages/sdk-logs/test/common/MultiLogRecordProcessor.attempt-all.test.ts`

No metrics, workflow, dependency, lock, generated, publisher, or research-only file is present.

## Exact-head evidence

All workflows passed at `db3d9e5e43d5abc6622784acf0ef87f3b038ac91`:

- Unit Tests `30756036668`;
- Lint `30756036660`;
- W3C Trace Context Integration `30756036656`;
- Bundler tests `30756036678`;
- Ensure API Peer Dependency `30756036662`;
- CodeQL Analysis `30756036671`;
- E2E Tests `30756036639`;
- Zizmor GitHub Actions Security Analysis `30756036691`.

An independent exact-head technical review accepted the complete six-file fence with disposition `ACCEPT / TECHNICALLY READY`.

## Owner decision surface

Recommended decision: advance this candidate toward authorized upstream preparation. Filing-time work remains: refresh current public main and overlap, confirm current contribution/disclosure policy, add root sdk-trace and experimental sdk-logs changelog entries using the real upstream PR number, and explicitly authorize public interaction.

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
