# Upstream issue draft — lifecycle fanout can skip opening processors

Draft status: `fallback only — direct PR preferred`  
Public interaction authorized: `no`

## Summary

Trace, logs, and metrics lifecycle aggregates iterate mutable child arrays. A child can remove a later indexed child while shutdown or force flush is being started, causing that later child to be skipped even though it belonged to the operation's opening set.

Trace and logs have an additional direct-call path: a processor can throw before returning its declared promise, interrupting construction of later promise inputs.

## Reproduction

1. Configure two processors or metric readers.
2. Have the first lifecycle callback remove the second entry from the aggregate's backing collection.
3. Call shutdown or force flush.
4. Observe that the second opening child is not invoked on the current baseline.

For trace/logs, an equivalent reproduction makes the first processor throw synchronously before returning a promise; later processors are not invoked.

## Expected behavior

A lifecycle aggregate should attempt every child present when the operation begins. Mutations during the operation should affect future operations without shrinking the current opening set. Existing package-specific error behavior should remain unchanged.

## Proposed direction

- snapshot the opening processor/collector array before invoking children;
- for trace and logs, convert direct synchronous processor throws into rejected promises while constructing the eager fanout;
- for metrics, call the existing async `MetricCollector` lifecycle methods directly—the collector already converts reader throws into rejected promises;
- retain `Promise.all` and current trace/logs/metrics outward behavior.

## Compatibility

- no public API or type changes;
- one shallow array copy per affected lifecycle call;
- future mutations remain visible;
- first-rejection behavior remains;
- no settle-all aggregation, cancellation, retry, or idempotence change.

## Scope

Affected entrypoints:

- `MultiSpanProcessor.shutdown()` / `forceFlush()`;
- `MultiLogRecordProcessor.shutdown()` / `forceFlush()`;
- `MeterProvider.shutdown()` / `forceFlush()`.

Related one-shot shutdown state, final metrics collection, delayed recursion, and telemetry admission after shutdown are separate topics.

## Environment

- repository revision: `2c931bf4eec18a234a28706567c6977f08139abd`;
- current public `main` matched that revision during the final repair pass;
- repository-supported GitHub Actions matrix;
- focused fixtures use two children and a first-child removal or direct throw.

## Prior-art result

Open issue/PR searches during the repair pass for the affected symbols, lifecycle fanout, snapshot wording, and skipped-later-child behavior found no equivalent current fix. Historical PR #802 introduced span-processor force-flush fanout but does not address stable opening membership or direct synchronous throws.

## Filing checklist

- [ ] repeat current-main and duplicate search immediately before filing;
- [ ] confirm reproduction on the then-current public revision;
- [x] keep metrics direct-throw behavior out of the defect claim;
- [x] avoid prevalence/severity claims beyond evidence;
- [ ] recheck contribution and AI-disclosure policy;
- [ ] record explicit authority before public interaction.
