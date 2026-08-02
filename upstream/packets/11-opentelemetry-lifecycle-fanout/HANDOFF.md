# Handoff — Unit 11: invoke all lifecycle processors

## Current disposition

`VALIDATING — repaired candidate and upstream drafts ready for exact-head results`

The contribution remains relevant. Current OpenTelemetry JS source still contains the aggregate early-stop, live-array iteration, and public provider timeout-cleanup mechanisms. No equivalent upstream repair was found during the latest search.

The source and writing have been tightened to avoid overclaiming: this is a specification-compliance and shutdown-reliability fix for uncommon custom-processor failure/mutation cases, not a high-severity or widespread telemetry-loss claim.

## Exact identities

- public base/current main: `2c931bf4eec18a234a28706567c6977f08139abd`;
- source branch: `teamleaderleo/opentelemetry-js:upstream/unit-11-lifecycle-fanout-v2`;
- current source head: `987a2bde097fe2e44531830e38c7c15a59c35c23`;
- source relation: ahead 4, behind 0;
- validation pull request: `teamleaderleo/opentelemetry-js#19`;
- packet branch: `p0/435-unit-11-opentelemetry-lifecycle-fanout-v2`;
- packet path: `upstream/packets/11-opentelemetry-lifecycle-fanout/`;
- public upstream authority: none.

The source branch is not yet final packaging. Squash and exact-head re-review follow current validation.

## Work completed in this pass

1. Rechecked current public source, relevant interfaces, existing tests, contribution guide, issue template, PR template, and commit-title convention.
2. Confirmed the trace and logs specifications require invoking all registered processors during shutdown and force flush.
3. Distinguished the three mechanisms accurately:
   - aggregate direct throw can stop later invocation;
   - live-array mutation can skip an opening processor in aggregate and provider paths;
   - provider direct throw already permits later `.map()` callbacks but leaves its timeout armed.
4. Retained the trace/logs repair and metrics exclusion.
5. Fixed `TracerProvider.ts` Prettier formatting after the first revised head's lint-only failure.
6. Added a provider control proving genuine pending work still times out.
7. Ran dependency-free Node.js control-flow/process-lifetime models.
8. Rewrote the owned PR, upstream issue draft, upstream PR draft, approaches, tests, review, and packet summary.

## Final intended source boundary

- three production files and three target-native tests;
- aggregate trace, public provider trace, and logs only;
- no metrics, workflows, dependencies, generated output, publishers, or Fieldwork-only files.

## Current validation

Previous candidate `f4910b355d12895edf25372444f76d4def08901c`:

- passed Unit, W3C, Bundler, API peer dependency, CodeQL, E2E, and Zizmor;
- failed Lint only for Prettier formatting in `TracerProvider.ts`.

Current candidate `987a2bde097fe2e44531830e38c7c15a59c35c23`:

- Unit `30755343888`;
- Lint `30755343692`;
- W3C `30755343695`;
- Bundler `30755343708`;
- API peer dependency `30755343685`;
- CodeQL `30755343693`;
- E2E `30755343697`;
- Zizmor `30755343702`.

These runs were queued at the last refresh. No current-head green claim has been made.

## Recommendation

Retain and prepare one upstream pull request covering sdk-trace and sdk-logs. The invariant and aggregate repair are shared, and the production boundary is small. If maintainers prefer package separation, split it into:

1. sdk-trace: `MultiSpanProcessor` plus `TracerProvider`;
2. sdk-logs: `MultiLogRecordProcessor`.

Do not reopen metrics as part of this contribution. Do not expand into settle-all aggregation, retry, cancellation, idempotence, runtime validation of invalid return values, or synchronous telemetry hooks.

## Continuation steps

1. Refresh and classify all current-head workflow conclusions.
2. Repair any source-attributable failure and rerun.
3. Squash the source branch onto the pinned public base.
4. Review the complete squashed diff and rerun exact-head workflows if the head changes.
5. Obtain eligible independent technical acceptance.
6. Repeat current-main and duplicate searches immediately before filing.
7. After explicit authorization and a real upstream PR number, add root sdk-trace and experimental sdk-logs changelog entries.

Public upstream interaction authorized/performed: `false` / `false`.
