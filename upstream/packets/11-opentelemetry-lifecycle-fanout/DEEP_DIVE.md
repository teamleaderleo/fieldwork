# Deep dive — Unit 11: snapshot lifecycle targets before concurrent fanout

## In simple words

OpenTelemetry JS trace, logs, and metrics aggregate lifecycle calls across child processors or readers. The baseline implementations build those calls from live arrays. A child can throw synchronously before the promise list is complete, or mutate the live array and remove a later child before iteration reaches it.

The selected correction copies the opening child list before invoking any child and routes every invocation through a small synchronous safe-call helper. Every opening child is attempted, current-operation membership stays stable, eager `Promise.all` fanout remains, and mutations remain visible to future operations.

The owned-fork predecessor passed the full repository gate set and received an accepted complete-diff review. The upstream-clean restack is on current public base `2c931bf4eec18a234a28706567c6977f08139abd`; its exact-head matrix is queued on owned PR #18.

## Governing invariant

> A lifecycle aggregate attempts every child in its opening membership set while preserving package-specific outward failure behavior and future membership mutation.

## Current behavior

- entrypoints: `MultiSpanProcessor.shutdown()`, `MultiSpanProcessor.forceFlush()`, `MultiLogRecordProcessor.shutdown()`, `MultiLogRecordProcessor.forceFlush()`, `MeterProvider.shutdown()`, and `MeterProvider.forceFlush()`;
- state owner: the trace processor array, public logs processor array, and metrics shared-state collector array;
- caller-visible result: trace shutdown rejects; trace force flush reports through the global error handler and resolves; logs and metrics reject;
- side effects: child lifecycle methods begin eagerly while promise inputs are constructed;
- cleanup owner: each child processor or reader;
- persistence or publication boundary: not applicable;
- relevant ordering: baseline direct iteration can stop on synchronous throw and live iteration can skip a deleted indexed child.

## Source map

| Area | Exact path and symbol | Responsibility | Relevant tests |
| --- | --- | --- | --- |
| trace | [`MultiSpanProcessor`](https://github.com/teamleaderleo/opentelemetry-js/blob/641528c9786f7d027fef4f4a76ae685f7107d394/packages/sdk-trace/src/MultiSpanProcessor.ts) | fan out shutdown and force flush while retaining trace error policy | [`MultiSpanProcessor.attempt-all.test.ts`](https://github.com/teamleaderleo/opentelemetry-js/blob/641528c9786f7d027fef4f4a76ae685f7107d394/packages/sdk-trace/test/common/MultiSpanProcessor.attempt-all.test.ts) |
| logs | [`MultiLogRecordProcessor`](https://github.com/teamleaderleo/opentelemetry-js/blob/641528c9786f7d027fef4f4a76ae685f7107d394/experimental/packages/sdk-logs/src/MultiLogRecordProcessor.ts) | fan out timeout-wrapped flush and shutdown across public processor membership | [`MultiLogRecordProcessor.attempt-all.test.ts`](https://github.com/teamleaderleo/opentelemetry-js/blob/641528c9786f7d027fef4f4a76ae685f7107d394/experimental/packages/sdk-logs/test/common/MultiLogRecordProcessor.attempt-all.test.ts) |
| metrics | [`MeterProvider`](https://github.com/teamleaderleo/opentelemetry-js/blob/641528c9786f7d027fef4f4a76ae685f7107d394/packages/sdk-metrics/src/MeterProvider.ts) | fan out shutdown and force flush across metric collectors | [`MeterProvider.attempt-all.test.ts`](https://github.com/teamleaderleo/opentelemetry-js/blob/641528c9786f7d027fef4f4a76ae685f7107d394/packages/sdk-metrics/test/MeterProvider.attempt-all.test.ts) |

## Reproduction or characterization

### Setup

- exact upstream revision: `2c931bf4eec18a234a28706567c6977f08139abd`;
- environment: repository GitHub Actions matrix; direct local clone was unavailable in this worker session because the execution environment could not resolve `github.com`;
- fixture: two child processors/readers where the first either throws synchronously or removes the second from the backing array;
- command family: package unit tests through the repository `Unit Tests` workflow, plus ordinary repository gates.

### Baseline result

Source and JavaScript array-iteration analysis establish two independent failure paths:

1. direct child invocation throws before the remaining promise inputs are constructed;
2. safe-call over a live array still allows a first child to delete a later indexed child, causing the iterator to skip it.

The retained cross-review on owned PR #6 found the second path after the first safe-call-only generation had passed product gates.

### Candidate result

The predecessor exact head `db7a0b3a2179f43bf1e0145c8352ff0367bdce79` passed Unit, Lint, E2E, Bundler, W3C, API peer-dependency, CodeQL, and workflow-security checks. Its tests prove later opening children are invoked after synchronous throws and after removal from the live backing array. The clean restack preserves the product logic and assertions while removing research-only error-message wording.

## Failure model

1. A provider or multi-processor begins shutdown or force flush.
2. Iteration reads directly from the mutable child array while synchronously invoking each child.
3. The first child throws, or removes a later child before the iterator reaches that index.
4. A later opening child receives no lifecycle call, leaving buffered telemetry or child cleanup unattempted.

Steps 1–3 are source-confirmed. The exact production prevalence and downstream consequence frequency remain unmeasured.

## Consequence and claim boundary

### Established

- synchronous child throws can stop later invocation during promise-list construction;
- live indexed iteration can skip a removed later child;
- a shallow opening snapshot plus synchronous safe-call preserves every opening invocation across all six entrypoints;
- trace, logs, and metrics retain their existing outward failure policy in the focused controls;
- child calls remain eagerly concurrent through `Promise.all`.

### Inferred

- skipping a lifecycle child can leave buffered telemetry or resources pending for that child;
- user-defined or retained mutable processor arrays make the mechanism reachable.

### Unknown or unmeasured

- ecosystem frequency;
- production impact magnitude;
- performance effect for unusually large child arrays;
- maintainer preference for a shared helper versus three local helpers.

## Selected implementation

Each lifecycle entrypoint takes a shallow `.slice()` of its child array before the first child call. Mapping occurs over that snapshot. `callLifecycle()` catches synchronous throws and converts them into rejected promises, allowing the map to continue constructing every promise input.

The aggregate still uses `Promise.all`:

- it retains eager concurrent invocation;
- it retains first-rejection outward behavior rather than aggregating every asynchronous error;
- trace force flush still reports one failure through `globalErrorHandler` and resolves;
- trace shutdown, logs, and metrics still reject.

The original arrays remain mutable. A removal during the operation changes later operations while leaving the current opening set intact.

## Compatibility analysis

- public API: unchanged;
- source compatibility: unchanged exported types and method signatures;
- binary or wire compatibility: not applicable;
- persistence or format compatibility: not applicable;
- platform behavior: standard ECMAScript array copy and promise behavior;
- performance and allocation: one shallow array allocation per affected lifecycle entrypoint, linear in child count;
- cancellation, retry, and recovery: unchanged; `Promise.all` still reports the first observed rejection and does not cancel siblings;
- generated output: none;
- migration or rollback: revert the six-file contribution.

## Adversarial and edge controls

- synchronous throw from the first child during all affected shutdown and force-flush paths;
- removal of the second child by the first child during all affected paths;
- original backing collection remains mutated after the operation;
- trace force-flush global error reporting remains active;
- logs and metrics rejection remains active;
- later child is invoked once;
- additions after operation start stay outside the snapshot by source semantics.

## Review risks

- **Trace force-flush refactor:** the implementation becomes `Promise.all(...).then(success, failure)`. Review must confirm it resolves after error handling exactly as before.
- **Logs timeout ordering:** `processor.forceFlush()` remains inside the safe-call callback, so synchronous throws become rejections before timeout wrapping can return.
- **Allocation:** every lifecycle call copies the child list. The copy is bounded by configured child count and occurs only on shutdown or force flush.
- **Async rejection scope:** the change attempts every child but still exposes only the first `Promise.all` rejection. The packet states this limit throughout.
- **Mutable public logs array:** snapshotting current membership changes only already-started operations; future operations still observe mutation.

## Reversing evidence

Reopen the conclusion if:

- current upstream replaces these fanout paths with equivalent stable-membership semantics;
- project policy requires live mutation to alter an already-started lifecycle operation;
- exact-head tests show changed outward failure behavior;
- measured allocation cost is material for realistic processor counts;
- maintainers require settle-all aggregation as part of the same contract.

## Adjacent work excluded

- provider and reader one-shot shutdown state — owned PRs #5 and #9;
- periodic reader final collection during shutdown — owned PR #9;
- delayed same-owner lifecycle recursion — Fieldwork #216 and owned PRs #10–#12;
- trace spans ending after provider shutdown begins — owned PR #16;
- process-global installation disposal;
- aggregation of every asynchronous child failure;
- duplicate-child policy.
