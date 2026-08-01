# Tests and receipts — Unit 11: stabilize lifecycle fanout targets

## Identity

- base/current main: `2c931bf4eec18a234a28706567c6977f08139abd`;
- exact squashed candidate: `f4910b355d12895edf25372444f76d4def08901c`;
- validation carrier: `teamleaderleo/opentelemetry-js#19`;
- relation: ahead 1, behind 0;
- execution authority: repository GitHub Actions matrix.

## Focused assertion set

### `MultiSpanProcessor` — four tests

- shutdown direct throw attempts the later opening processor and rejects;
- shutdown removal still invokes the removed opening processor;
- force-flush direct throw attempts the later processor, reports globally, and resolves;
- force-flush removal still invokes the removed opening processor.

Cleanup restores `setGlobalErrorHandler(loggingErrorHandler())`.

### `TracerProvider.forceFlush()` — two tests

- synchronous throw attempts the later processor, preserves one-error array rejection, and leaves zero fake-clock timers;
- live removal does not shrink the provider opening set.

### Logs — four tests

Shutdown and force flush each cover direct throw and live removal. Rejection and timeout behavior remain unchanged.

### Metrics

No metrics source/tests remain. The predecessor tests depended on private collector-state mutation and did not reverse a supported runtime path.

## Exact squashed-head workflows

| Workflow | Run | Current state |
| --- | ---: | --- |
| Unit Tests | `30694264703` | queued |
| W3C Trace Context Integration | `30694264710` | queued |
| Bundler tests | `30694264711` | queued |
| Ensure API Peer Dependency | `30694264708` | queued |
| CodeQL Analysis | `30694264717` | queued |
| E2E Tests | `30694264735` | queued |
| Zizmor GitHub Actions Security Analysis | `30694264748` | queued |
| Lint | `30694264729` | queued |

No squashed-head pass is claimed until these settle. A pre-squash successor Windows build/unit job passed, but that receipt is historical after the head rewrite.

## Historical evidence and repairs

- safe-call-only generation passed gates but review found removal skipping;
- first snapshot fixture had test-only TS2322 inference failures;
- predecessor `641528c...` passed all named workflow groups;
- review `4834242586` exposed a metrics overclaim;
- deeper review removed metrics, corrected global-handler cleanup, and added public provider force-flush coverage;
- provider regression now covers opening membership, later invocation, error-array shape, and timer cleanup;
- source and packet successors were isolated after concurrent rewrites, then source was squashed to one commit.

## Changelog and judgment

Target policy requires a root changelog entry for sdk-trace and an experimental changelog entry for sdk-logs, using the real authorized upstream PR number.

Current judgment: `HOLD`. Clearing conditions are a successful exact squashed-head matrix, eligible independent acceptance, changelog packaging, final staleness/policy checks, and explicit public-contact authorization.
