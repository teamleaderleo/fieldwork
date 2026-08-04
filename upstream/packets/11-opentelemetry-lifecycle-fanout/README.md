# Unit 11 — fix: stabilize lifecycle fanout targets

## In simple words

OpenTelemetry trace and logs shutdown/flush code can skip a processor that was present when the operation started. The repair snapshots that opening set and converts only direct synchronous throws into rejected promises, so later processors are still attempted through the existing error paths.

The candidate has now been rebased onto current public `main`. Upstream added a per-call trace force-flush timeout after the earlier review; the rebased code preserves that API and updates the provider tests to exercise it. Fresh exact-head workflows are running, so the old technical acceptance is no longer presented as acceptance of the new SHA.

## Current state

`UPSTREAM PREPARATION IN PROGRESS — CURRENT-MAIN REBASE COMPLETE — EXACT-HEAD CI RUNNING`

Last refreshed: `2026-08-05`  
Priority-zero parent: `teamleaderleo/fieldwork#435`  
Public upstream contact authorized: `no`

## Contribution

`MultiSpanProcessor` and `MultiLogRecordProcessor` traverse retained mutable processor arrays while invoking lifecycle methods. A processor can remove a later opening processor or throw synchronously before returning its declared promise, preventing later invocation.

Public `TracerProvider.forceFlush()` performs a separate direct fanout. Live mutation can skip a later processor there, and a synchronous throw can bypass the normal timeout-clearing promise path.

The candidate:

- snapshots the processors present when each lifecycle operation begins;
- invokes each child eagerly through a local `try`/`catch` helper;
- converts only direct synchronous throws into rejected promises;
- preserves each surface's existing settlement and timeout policy;
- preserves the newly merged per-call trace timeout option from upstream PR #6929.

Metrics remains excluded because the comparable collector list is internally constructed and the earlier mutation control required private-state access.

## Exact identities

- target: `open-telemetry/opentelemetry-js`;
- refreshed public-main base: `f278e3b8427c406c271b8cba2c0f1a9c47c2f15e`;
- canonical source branch: `teamleaderleo/opentelemetry-js:upstream/unit-11-lifecycle-fanout-v2`;
- exact prepared source head: `f4cb44bcccffbc0eb39e774284655e0f965cfce1`;
- owned source preview: `teamleaderleo/opentelemetry-js#19`;
- source relation: ahead 1, behind 0;
- packet branch: `p0/435-unit-11-opentelemetry-lifecycle-fanout-current`;
- proposed title: `fix(sdk-trace, sdk-logs): invoke all lifecycle processors`.

## Final code boundary

1. `packages/sdk-trace/src/MultiSpanProcessor.ts`
2. `packages/sdk-trace/src/TracerProvider.ts`
3. `packages/sdk-trace/test/common/MultiSpanProcessor.attempt-all.test.ts`
4. `packages/sdk-trace/test/common/TracerProvider.attempt-all.test.ts`
5. `experimental/packages/sdk-logs/src/MultiLogRecordProcessor.ts`
6. `experimental/packages/sdk-logs/test/common/MultiLogRecordProcessor.attempt-all.test.ts`

No metrics, dependency, lock, generated, publisher, or temporary workflow file is present.

## Current-main and overlap refresh

- public `main` was three commits ahead of the earlier base;
- two commits were dependency/workflow maintenance;
- upstream PR #6929 changed `TracerProvider.forceFlush()` to accept a per-call timeout;
- that nearby change is complementary, not duplicative, and is retained in the prepared branch;
- current issue and PR searches found no equivalent synchronous-throw/opening-set repair;
- current contribution guidance requires unit tests and changelog entries for behavior changes.

## Exact-head execution

Fresh workflows were started for `f4cb44bcccffbc0eb39e774284655e0f965cfce1`:

- Unit Tests `30956029453`;
- Lint `30956029480`;
- W3C Trace Context Integration Test `30956029456`;
- Bundler tests `30956029470`;
- Ensure API Peer Dependency `30956029447`;
- CodeQL Analysis `30956029506`;
- E2E Tests `30956029462`;
- Zizmor GitHub Actions Security Analysis `30956029460`;
- Old Node.js Compatibility `30956029502`.

The eight green runs and technical acceptance attached to `db3d9e5e43d5abc6622784acf0ef87f3b038ac91` remain useful historical evidence, but they do not substitute for fresh exact-head evidence after the rebase.

## Remaining preparation work

1. Classify the fresh exact-head workflow matrix.
2. Perform a fresh complete-diff review on the rebased SHA.
3. Insert the assigned public PR number into the root and experimental changelog entries after filing is explicitly authorized.
4. Reconfirm public `main` and overlap immediately before filing.

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
