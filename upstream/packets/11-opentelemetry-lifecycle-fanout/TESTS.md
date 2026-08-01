# Tests and receipts — Unit 11: snapshot lifecycle targets before concurrent fanout

## In simple words

The exact clean source head passed the full named OpenTelemetry JS workflow set. Those green workflows establish that the current six-file candidate builds and passes the repository matrix. Complete-diff review nevertheless found that metrics is over-fixed: metrics needs opening-list snapshots, but its existing async `MetricCollector` methods already convert synchronous reader throws into rejected promises.

The current receipts remain accurate for head `641528c9786f7d027fef4f4a76ae685f7107d394`. Any source repair creates a new head and expires them for promotion.

## Identity

- Reviewed upstream base: `2c931bf4eec18a234a28706567c6977f08139abd`;
- Exact candidate head: `641528c9786f7d027fef4f4a76ae685f7107d394`;
- Validation carrier: [`teamleaderleo/opentelemetry-js#18`](https://github.com/teamleaderleo/opentelemetry-js/pull/18);
- Test date: `2026-08-01`;
- Environment: repository GitHub Actions matrix.

## Exact-head workflow receipts

| Gate | Run | Result | Material coverage limit |
| --- | --- | --- | --- |
| Unit Tests | `30674494793` | success; 10 jobs successful | repository unit matrix across supported Node/browser/worker jobs |
| E2E Tests | `30674494785` | success; 7 jobs successful | repository-declared E2E matrix |
| Lint | `30674494830` | success | formatting, lint, and compile-bearing checks declared by workflow |
| Bundler tests | `30674494832` | success | repository bundler checks |
| W3C Trace Context Integration | `30674494799` | success | named trace-context integration only |
| Ensure API Peer Dependency | `30674494801` | success | declared peer-dependency check |
| CodeQL Analysis | `30674494779` | success | configured static analysis only |
| Zizmor GitHub Actions Security Analysis | `30674494823` | success | workflow-security analysis only |

Evidence class: `full-gate` for this named workflow set at this exact head. It does not prove independent acceptance, changelog completeness, ecosystem prevalence, or behavior outside the executed repository paths.

## Claim-to-evidence matrix

| Claim | Evidence class | Exact evidence | Judgment and limit |
| --- | --- | --- | --- |
| trace synchronous throw cannot stop later opening invocation | `target-executed` | trace throw controls in Unit `30674494793` | reversing regression for trace |
| logs synchronous throw cannot stop later opening invocation | `target-executed` | logs throw controls in Unit `30674494793` | reversing regression for logs |
| trace/logs opening membership survives live removal | `target-executed` | mutation controls in Unit `30674494793` | reversing regression for current-operation membership |
| metrics opening membership survives live removal | `target-executed` | metrics mutation controls in Unit `30674494793` | reversing regression for metrics snapshot |
| metrics later collectors run after synchronous reader throw | `target-executed compatibility control` | metrics throw controls in Unit `30674494793` | already true on baseline because `MetricCollector` lifecycle methods are async; does not justify metrics safe-call source code |
| trace force flush retains global error reporting and resolution | `target-executed compatibility control` | trace handler test in Unit `30674494793` | focused first-error behavior only |
| current branch is direct from reviewed public base | `source-read` | compare `2c931bf4...641528c` | ahead 6, behind 0; public main may later advance |

## Baseline characterization

### Trace and logs

The baseline directly invokes child lifecycle methods while constructing promise inputs from live arrays. Two independent mechanisms exist:

1. a synchronous child throw interrupts construction before later child calls;
2. removal from the live indexed array can skip a later opening child.

The candidate's safe-call plus snapshot tests reverse both mechanisms.

### Metrics

`MeterProvider` also maps a live collector array, so live removal can skip a later opening collector. The metrics mutation tests reverse this defect.

The synchronous-throw characterization differs. `MetricCollector.forceFlush()` and `MetricCollector.shutdown()` are async wrappers around reader lifecycle methods. A reader's synchronous throw becomes a rejected promise before control returns to `MeterProvider`, so later collector calls are already attempted by the baseline map. The metrics synchronous-throw test is therefore a compatibility control, not a failing baseline regression.

## Focused test files

- `packages/sdk-trace/test/common/MultiSpanProcessor.attempt-all.test.ts`;
- `experimental/packages/sdk-logs/test/common/MultiLogRecordProcessor.attempt-all.test.ts`;
- `packages/sdk-metrics/test/MeterProvider.attempt-all.test.ts`.

All ran successfully as part of Unit Tests `30674494793` at the exact candidate head.

## Reversing controls

- trace/logs: first child throws synchronously; later opening child is still invoked by the candidate;
- all three packages: first child removes the second from the backing array; snapshot still invokes the second for the current operation;
- original backing arrays remain mutated, proving future operations still observe mutation;
- trace force flush reports through the global handler and resolves;
- logs and metrics retain rejection behavior.

The metrics synchronous-throw case does not reverse the source change and must not be presented as such.

## Harness history

| Attempt | Result | Classification | Product claim affected? |
| --- | --- | --- | --- |
| `e19247b801817abaf8c9fff5a39d00783d8c38e6` | TS2322 from callbacks inferred as `() => never` | test fixture typing | no; repaired with explicit `() => void` typing |
| worker local clone | DNS resolution for `github.com` unavailable | runner/network | no; exact execution retained through owned GitHub Actions |

## Cleanup and packaging

- Temporary workflows in source diff: none;
- Publisher/evidence-only files in source diff: none;
- Generated/dependency churn: none;
- Changelog files: not yet present; required packaging remains pending a real authorized PR number and current contribution-policy check;
- Validation carrier: retain draft PR #18 until repaired evidence replaces this generation.

## Current test judgment

`REPAIR`

The exact current head is green, but green execution does not cure the metrics scope defect. Repair metrics to snapshot-only, synchronize the tests and claims, then rerun every required gate on the new exact head.
