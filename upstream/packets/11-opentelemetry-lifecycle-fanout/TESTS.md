# Tests and receipts — Unit 11: invoke all lifecycle processors

## Identity

- current public base: `2c931bf4eec18a234a28706567c6977f08139abd`;
- current candidate head: `987a2bde097fe2e44531830e38c7c15a59c35c23`;
- validation pull request: `teamleaderleo/opentelemetry-js#19`;
- relation at the current head: ahead 4, behind 0;
- changed-file boundary: three production files and three target-native test files;
- execution authority: repository GitHub Actions workflows.

The branch will be squashed after the current repair cycle; commit count is not being represented as final upstream packaging yet.

## Specification check

The current OpenTelemetry trace and logs specifications require provider shutdown and force flush to invoke the operation on all registered processors. The repaired behavior targets that requirement without changing each package's established outward failure policy.

## Focused assertion set

### `MultiSpanProcessor` — four regressions

- a direct synchronous shutdown throw is converted to a rejection after the later opening processor is invoked;
- synchronous removal during shutdown does not remove that processor from the current operation;
- a direct synchronous force-flush throw is reported through the global error handler after the later processor is invoked;
- synchronous removal during force flush does not shrink the current operation.

Cleanup restores `setGlobalErrorHandler(loggingErrorHandler())`.

### `MultiLogRecordProcessor` — four regressions

- shutdown and force flush each cover direct synchronous throw and live-array removal;
- later opening processors are invoked;
- existing rejection behavior is retained;
- existing `callWithTimeout` wrapping remains in place for returned promises.

### `TracerProvider.forceFlush()` — three regressions/controls

- a direct synchronous throw retains the existing one-error-array rejection and leaves zero fake-clock timers;
- synchronous removal does not shrink the provider's opening processor set;
- a processor that genuinely remains pending still reaches the configured timeout and rejects.

The provider throw test deliberately does not claim that a synchronous throw previously skipped later `.map()` callbacks: the Promise constructor already catches that throw. The provider-specific defect is timeout cleanup; live-array mutation is the provider-specific skip case.

### Metrics exclusion

No metrics source or tests remain. `MetricCollector.shutdown()` and `forceFlush()` are async, and the predecessor mutation tests depended on private collector-state casts rather than a supported post-construction registration path.

## Runtime model check

A dependency-free Node.js v22.16.0 model confirmed the JavaScript control-flow distinctions:

- direct aggregate iteration stopped at the first synchronous throw and did not invoke the later child;
- invocation inside a Promise executor continued to the later `.map()` callback;
- without explicit cleanup, the armed timeout still fired;
- with a 200 ms referenced timeout and the outward rejection handled, the process remained alive for approximately 0.22 seconds.

This model supports the mechanism and possible process-exit consequence. It is not evidence of prevalence in deployed applications.

## Previous exact-head workflow result

Head `f4910b355d12895edf25372444f76d4def08901c`:

| Workflow | Run | Result |
| --- | ---: | --- |
| Unit Tests | `30694264703` | passed |
| W3C Trace Context Integration | `30694264710` | passed |
| Bundler tests | `30694264711` | passed |
| Ensure API Peer Dependency | `30694264708` | passed |
| CodeQL Analysis | `30694264717` | passed |
| E2E Tests | `30694264735` | passed |
| Zizmor GitHub Actions Security Analysis | `30694264748` | passed |
| Lint | `30694264729` | failed — Prettier formatting in `TracerProvider.ts` |

The lint log identified formatting errors only; it did not identify a product or test failure.

## Current exact-head workflows

Head `987a2bde097fe2e44531830e38c7c15a59c35c23`:

| Workflow | Run | Current state |
| --- | ---: | --- |
| Unit Tests | `30755343888` | queued |
| Lint | `30755343692` | queued |
| W3C Trace Context Integration | `30755343695` | queued |
| Bundler tests | `30755343708` | queued |
| Ensure API Peer Dependency | `30755343685` | queued |
| CodeQL Analysis | `30755343693` | queued |
| E2E Tests | `30755343697` | queued |
| Zizmor GitHub Actions Security Analysis | `30755343702` | queued |

This head repairs formatting and adds a timeout-preservation control. No current-head pass is claimed until the workflows settle.

## Remaining validation questions

- Does the current exact head pass all ordinary workflows?
- Does complete-diff review confirm that eager call order and package-specific failure behavior are unchanged?
- Are root and experimental changelog entries correct once a real authorized upstream PR number exists?
- Has public main or an overlapping upstream proposal changed before filing?

Current judgment: `VALIDATING`. The technical direction is retained; exact-head CI, final complete-diff review, squash, changelog packaging, staleness checks, and public-contact authority remain.
