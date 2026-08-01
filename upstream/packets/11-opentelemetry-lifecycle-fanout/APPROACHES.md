# Approaches — Unit 11: snapshot lifecycle targets before concurrent fanout

## In simple words

The selected direction combines two narrow mechanisms: take a shallow copy of the opening child list, then convert synchronous child throws into rejected promises while constructing an eager `Promise.all` fanout. Safe-call alone loses children when live arrays mutate. Permanent copies or frozen arrays change future membership. Sequential awaiting changes latency and ordering. Settle-all aggregation widens the contract.

## Decision criteria

1. attempt every child present when the lifecycle operation starts;
2. preserve trace, logs, and metrics outward failure behavior;
3. keep future membership mutable;
4. retain eager concurrent fanout and a six-file review boundary;
5. use standard runtime behavior with bounded allocation.

## Selected approach

### Opening snapshot plus synchronous safe-call

- Design: `.slice()` the child collection before invocation and map the snapshot through `callLifecycle()`.
- Owning boundary: the three aggregate lifecycle implementations.
- Evidence: predecessor exact-head full gate pass, mutation and synchronous-throw tests, accepted complete-diff review `4824609621`, and clean current-base compare.
- Advantages: deterministic current membership, every opening invocation attempted, unchanged public API and future mutation semantics.
- Costs and risks: one shallow array allocation per lifecycle call; three local helper copies; asynchronous errors remain first-rejection only.
- Remaining controls: clean-head workflow completion, changelog packaging, and exact clean-head independent review.

## Viable alternatives

### Shared internal lifecycle helper

- Design: extract snapshot, safe invocation, and `Promise.all` behavior into a shared utility.
- Why it remains plausible: avoids three local copies of `callLifecycle()`.
- What it would improve: central naming and future consistency.
- What it would widen or complicate: cross-package dependency placement, exported/internal utility policy, broader review surface, and package-specific trace error handling.
- Exact discriminator: maintainer preference for shared utility ownership after reviewing the narrow direct patch.
- Reopening trigger: requested deduplication or another package needing the identical primitive.

### Settle-all with error aggregation

- Design: invoke every child and wait for every settlement, then return an aggregate error.
- Why it remains plausible: exposes every child failure and makes completion mean all child promises settled.
- What it would improve: diagnostic completeness and cleanup completion semantics.
- What it would widen or complicate: caller-visible error types, timing, trace force-flush policy, compatibility, and test matrix.
- Exact discriminator: an explicit project contract requiring all settlements or all errors.
- Reopening trigger: maintainer direction or concrete loss from first-rejection behavior.

## Executed losing approaches

### Synchronous safe-call over live arrays

- Exact branch, patch, or commit: owned PR #6 predecessor before snapshot repair; executed head `80e3b74baf42300aeab92792ce5ca4dd44c37d95`.
- What ran: Unit, Lint, E2E, CodeQL, Bundler, W3C, peer-dependency, and workflow security.
- Result: passed, then complete review found live indexed mutation could skip a later child.
- Why it lost: “attempt every child” remained false when a first child removed a later indexed entry.
- Useful evidence retained: synchronous-throw conversion and package error-policy controls.

### First snapshot test generation with inferred `never` callbacks

- Exact branch, patch, or commit: `e19247b801817abaf8c9fff5a39d00783d8c38e6`.
- What ran: hosted repository workflows.
- Result: peer dependency, CodeQL, and workflow security passed; compile-bearing gates failed on TS2322 in metrics test scaffolding.
- Why it lost: mutation callbacks initialized only by `throw` inferred as `() => never`.
- Useful evidence retained: exact setup-failure classification and proof that product lint completed before test compilation failed.

## Rejected easy answers

### Keep direct live iteration

- Temptation: smallest source diff.
- Why it is incomplete or unsafe: synchronous throw stops promise-list construction and live mutation can erase opening work.
- Negative control or source fact: the focused first-child throw and remove-second controls.

### Freeze or permanently copy processor arrays

- Temptation: eliminate mutation races globally.
- Why it is incomplete or unsafe: changes public logs-array behavior and future-operation membership.
- Negative control or source fact: tests assert the original backing arrays remain mutated after the current operation.

### Sequentially await each child

- Temptation: straightforward try/catch and deterministic completion.
- Why it is incomplete or unsafe: changes established eager concurrency and increases latency by summing child durations.
- Negative control or source fact: current implementations build promise inputs eagerly and use `Promise.all`.

### Catch only around `Promise.all`

- Temptation: one outer error handler.
- Why it is incomplete or unsafe: the synchronous throw occurs while the promise array is still being constructed, before `Promise.all` receives it.
- Negative control or source fact: direct child invocation is evaluated during map/loop construction.

## Prior upstream approaches

| Link | Approach | Status | Relationship to this unit |
| --- | --- | --- | --- |
| [PR #802](https://github.com/open-telemetry/opentelemetry-js/pull/802) | introduced span-processor force-flush fanout | merged historical work | establishes lifecycle fanout history; no stable-opening or sync-throw repair |
| [PR #1296](https://github.com/open-telemetry/opentelemetry-js/pull/1296) | exporter force-flush and shutdown callbacks | historical | adjacent lifecycle API work, independent mechanism |
| [Issue #4611](https://github.com/open-telemetry/opentelemetry-js/issues/4611) | graceful shutdown failure from a gRPC exporter | closed/historical symptom report | different exporter defect despite a stack through `MultiSpanProcessor` |
| [Issue #4922](https://github.com/open-telemetry/opentelemetry-js/issues/4922) | tracing suppression after batch flush | open/historical symptom report | different context/suppression behavior |

Searches on 2026-08-01 for `snapshot lifecycle processors`, `MultiSpanProcessor shutdown`, and synchronous lifecycle fanout found no equivalent current implementation or proposal.

## Deferred adjacent work

- one-shot provider and reader shutdown — changes state and compatibility;
- reader-owned final metrics collection — changes teardown authority;
- delayed lifecycle recursion — changes promise provenance and reentry handling;
- trace delivery after shutdown starts — changes span admission/delivery policy;
- process-global disposal — changes ownership of global registrations;
- settle-all error aggregation — changes caller-visible failure behavior.

## Decision history

| Date | Exact inputs | Decision | Reason | Reopening trigger |
| --- | --- | --- | --- | --- |
| 2026-07-30 | predecessor `80e3b74b...` plus complete review | repair | safe-call over live arrays could skip a removed later child | stable-opening controls |
| 2026-07-31 | snapshot generation `e19247b...` | repair test scaffolding | metrics mutation callback inferred as `never` | explicit `() => void` types |
| 2026-07-31 | exact head `db7a0b3...`, full gates, review `4824609621` | accept technical direction | six-file product/test diff met the invariant | current-base restack |
| 2026-08-01 | public base `2c931bf...`, clean head `641528c...` | hold for final gates | direct clean restack exists; exact-head matrix and clean-head review remain | all required gates pass and review accepts |
