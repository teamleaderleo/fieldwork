# Tests and receipts — Unit 11: OpenTelemetry lifecycle fanout

## Final evidence state

`FINAL SIGNED HEAD GREEN ON OWNED FORK`

- final head: `1e5bd20fb823a9c47a2b2ccc974e18d88b765f16`
- upstream PR: [open-telemetry/opentelemetry-js#6980](https://redirect.github.com/open-telemetry/opentelemetry-js/pull/6980)
- changed files: three production files, three test files, and two changelogs
- regression tests: eleven

## Regression set

### `MultiSpanProcessor` — four tests

- shutdown direct throw still attempts the later opening processor and rejects;
- shutdown mutation still invokes the removed opening processor;
- force-flush direct throw still attempts the later processor, reports globally, and resolves;
- force-flush mutation still invokes the removed opening processor.

### `TracerProvider.forceFlush()` — three tests

- direct throw still attempts the second processor, preserves the error-array rejection, and clears its timer;
- mutation does not shrink the opening set;
- a genuinely non-settling processor still times out and leaves no timer afterward.

### Logs — four tests

Shutdown and force flush each cover direct throw and opening-set mutation while preserving rejection and timeout behavior.

## Final owned-fork workflow receipts

| Workflow | Run | Result |
| --- | ---: | --- |
| Unit Tests | `31073507119` | success |
| Lint | `31073507124` | success |
| E2E Tests | `31073507094` | success |
| Bundler tests | `31073507109` | success |
| W3C Trace Context Integration Test | `31073507096` | success |
| CodeQL Analysis | `31073507092` | success |
| Ensure API Peer Dependency | `31073507111` | success |
| Zizmor GitHub Actions Security Analysis | `31073507376` | success |
| changelog | `31073507108` | success |

## Upstream workflow state

The upstream workflow runs currently report `action_required` with no jobs. A maintainer must approve execution for the fork-originated pull request. This is an execution gate, not a test failure.

## Current judgment

The final signed head has complete owned-fork validation. The remaining validation step belongs to upstream workflow approval and execution.
