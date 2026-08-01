# Upstream pull-request draft — fix: snapshot lifecycle targets before concurrent fanout

Draft status: `not ready`  
Proposed head: `teamleaderleo/opentelemetry-js:upstream/unit-11-lifecycle-fanout`  
Proposed base: `open-telemetry/opentelemetry-js:main` at `2c931bf4eec18a234a28706567c6977f08139abd`  
Public interaction authorized: `no`

The code and public-facing description are prepared. Submission remains blocked on current clean-head gates, exact clean-head independent review, changelog packaging, a fresh duplicate/current-main check, and explicit authorization.

---

## Summary

- Attempt every trace processor, log processor, and metric reader that belongs to the lifecycle operation's opening set.
- Convert synchronous child throws into rejected promises so later opening children are still invoked.
- Preserve eager concurrent fanout and existing package-specific error behavior.

## Problem

The trace, logs, and metrics lifecycle aggregators currently invoke child methods while iterating mutable arrays. A synchronous child throw can stop later promise inputs from being constructed. A child can also remove a later indexed child during iteration, causing shutdown or force flush to skip an opening child.

A lifecycle aggregate should attempt every child present when the operation begins. Mutations during the call should affect future operations while leaving the current opening set stable.

## Change

Each affected entrypoint now takes a shallow `.slice()` of its child collection before invoking any child. Each invocation passes through a local `callLifecycle()` helper that converts synchronous throws into rejected promises.

The aggregate still uses `Promise.all`:

- trace shutdown still rejects;
- trace force flush still reports through `globalErrorHandler` and resolves;
- logs and metrics still reject;
- child calls remain eager and concurrent;
- the original collections remain mutable for future operations.

Focused tests cover synchronous throw and opening-set mutation for shutdown and force flush in all three packages.

## Tests

- `Unit Tests` workflow, including:
  - `packages/sdk-trace/test/common/MultiSpanProcessor.attempt-all.test.ts`;
  - `experimental/packages/sdk-logs/test/common/MultiLogRecordProcessor.attempt-all.test.ts`;
  - `packages/sdk-metrics/test/MeterProvider.attempt-all.test.ts`.
- Lint and compile-bearing repository checks.
- E2E Tests, Bundler tests, W3C Trace Context Integration, Ensure API Peer Dependency, CodeQL, and Zizmor workflow-security analysis.

Prior exact generation `db7a0b3a2179f43bf1e0145c8352ff0367bdce79` passed all listed gates. The current clean generation `641528c9786f7d027fef4f4a76ae685f7107d394` has its own matrix queued on the owned fork.

## Compatibility

- public API: unchanged;
- existing behavior retained: package-specific resolution/rejection and global error reporting;
- platform or runtime notes: standard ECMAScript array-copy and promise semantics;
- performance or allocation notes: one shallow array allocation per affected lifecycle call;
- migration or rollback: no migration; revert the six-file patch.

## Alternatives considered

- Safe-call over live arrays still allows a first child to remove a later indexed child.
- Freezing or permanently copying arrays changes future membership behavior.
- Sequential awaiting changes eager concurrency and latency.
- Settle-all aggregation changes caller-visible failure timing and error semantics.

## Limits

- The change does not aggregate every asynchronous child failure; `Promise.all` retains first-rejection behavior.
- Delayed same-owner recursion, one-shot provider/reader state, final metrics collection, pre-existing span delivery, and process-global disposal remain separate.
- Production prevalence is unmeasured.

## Related work

- PR #802 introduced span-processor force-flush support and is historical context rather than an equivalent repair.
- Searches on 2026-08-01 found no current issue or pull request implementing stable opening snapshots for these lifecycle fanouts.

---

## Submission checklist

- [x] Branch is a direct child of public base `2c931bf4eec18a234a28706567c6977f08139abd`.
- [x] Diff contains six product/test files only.
- [x] Research wording, temporary workflows, publishers, receipts, and evidence-only files are absent.
- [ ] Every changed file receives independent review at the exact proposed head.
- [ ] Focused regressions complete on the clean candidate; baseline relationship is retained in the packet.
- [ ] Project-declared ordinary gates complete on the clean candidate.
- [x] Current duplicate and overlap search completed on 2026-08-01; repeat immediately before filing.
- [x] Commit titles follow conventional commit form; six commits should be squashed or accepted according to maintainer preference before submission.
- [ ] Add required root and experimental changelog entries once a public PR number exists, or obtain an explicit changelog-skip decision.
- [ ] Target contribution and AI-disclosure policies rechecked at filing time.
- [ ] Exact user authorization to open the pull request recorded.
