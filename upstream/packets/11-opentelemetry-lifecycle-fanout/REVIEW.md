# Review — Unit 11: snapshot lifecycle targets before concurrent fanout

## In simple words

The trace and logs parts solve two real attempt-all defects: they snapshot the processors present when lifecycle work begins, and they prevent one processor's synchronous throw from stopping invocation of later opening processors.

Metrics has the same live-array mutation defect, so its opening collector list also needs a snapshot. It does **not** have the same synchronous-throw defect: `MetricCollector.forceFlush()` and `MetricCollector.shutdown()` are already `async`, so a synchronous reader throw is already returned as a rejected promise and later collectors are still invoked on the baseline. The current metrics `callLifecycle()` wrapper is therefore redundant, and the packet overstates what the metrics source change fixes.

All exact-head workflows passed. The current source still requires a narrow repair before promotion.

## Review subject

- Work class: `upstream-fork research / patch-series preparation`;
- Target repository: `open-telemetry/opentelemetry-js`;
- Reviewed base: `2c931bf4eec18a234a28706567c6977f08139abd`;
- Canonical source branch: `teamleaderleo/opentelemetry-js:upstream/unit-11-lifecycle-fanout`;
- Reviewed source head: `641528c9786f7d027fef4f4a76ae685f7107d394`;
- Packet branch: `p0/435-unit-11-opentelemetry-lifecycle-fanout`;
- Changed-file fence: three production files and three target-native test files;
- Current-main relation: ahead 6, behind 0, merge base equals the reviewed public head;
- Public upstream contact authorized: `false`.

## Exact-head validation

Every current workflow completed successfully on source head `641528c9786f7d027fef4f4a76ae685f7107d394`:

- Unit Tests `30674494793`: success, 10 jobs successful;
- E2E Tests `30674494785`: success, 7 jobs successful;
- Lint `30674494830`: success;
- Bundler tests `30674494832`: success;
- W3C Trace Context Integration `30674494799`: success;
- Ensure API Peer Dependency `30674494801`: success;
- CodeQL Analysis `30674494779`: success;
- Zizmor GitHub Actions Security Analysis `30674494823`: success.

Evidence class: `full-gate` for the named repository workflow set only. These passes do not establish public-submission authority, changelog completeness, production prevalence, or independent acceptance.

## Complete-diff findings

### Trace — accepted direction

`MultiSpanProcessor` maps a mutable processor array while directly invoking child lifecycle methods. The selected snapshot plus safe-call approach is justified:

- `.slice()` stabilizes opening membership against removal during the current operation;
- `callLifecycle()` converts a synchronous child throw into a rejected promise so mapping continues to later opening processors;
- `Promise.all` preserves eager fanout and first-rejection behavior;
- force flush retains resolve-after-`globalErrorHandler` behavior in the focused compatibility control.

### Logs — accepted direction

`MultiLogRecordProcessor` has the same two baseline mechanisms. Snapshot plus safe-call is justified while retaining the existing timeout wrapper and rejection behavior.

### Metrics — repair required

`MeterProvider` maps the live `sharedState.metricCollectors` array. Snapshotting that array is justified because a first collector can remove a later collector before indexed iteration reaches it.

The metrics safe-call claim is not justified as a baseline defect. `MetricCollector.forceFlush()` and `MetricCollector.shutdown()` are declared `async` and await the underlying reader. JavaScript async-function semantics already convert a reader's synchronous throw into a rejected promise. The existing `MeterProvider` map therefore continues constructing later collector calls after that throw.

Consequences for the current diff and packet:

- keep the two metrics `.slice()` snapshots;
- remove the metrics-local `callLifecycle()` helper and map snapshots directly to `collector.forceFlush(options)` and `collector.shutdown(options)`;
- classify metrics synchronous-throw tests as baseline compatibility controls, not regressions proving a source defect, or remove them if the smallest upstream diff is preferred;
- retain metrics mutation tests as the actual reversing controls;
- narrow `README.md`, `DEEP_DIVE.md`, `TESTS.md`, `UPSTREAM_ISSUE.md`, `UPSTREAM_PR.md`, the validation PR body, and the final handoff accordingly.

## Compatibility and packaging review

- Public API and exported types remain unchanged.
- The intended repair reduces unnecessary metrics source churn without weakening the opening-snapshot invariant.
- The six file-level commits should be squashed before public submission unless the target maintainers prefer a series.
- Current target contribution guidance requires changelog entries for affected packages. Their final names include a real PR number, so they remain a submission-packaging step rather than something to invent on the unauthorized owned-fork carrier.
- A fresh current-main and duplicate/overlap search remains required immediately before any authorized filing.

## Disposition

`REPAIR`

Required next transition:

1. repair metrics production code to snapshot-only;
2. reclassify or remove the metrics synchronous-throw controls;
3. synchronize all packet and PR claims;
4. rerun the complete exact-head workflow set because source movement expires the receipts above;
5. obtain an eligible independent complete-diff review of the repaired exact head;
6. finish changelog packaging and a final duplicate/current-main refresh before changing the unit to `READY`.

## Reviewer eligibility

This is a complete technical self-review by the worker that created the current clean branch. It is valid for finding and requiring repair, but it is **not** independent final acceptance. A separate eligible peer receipt is still required after the repaired source head is fixed and executed.

## Contact boundary

Public upstream interaction authorized: `false`.  
Public upstream interaction performed: `false`.
