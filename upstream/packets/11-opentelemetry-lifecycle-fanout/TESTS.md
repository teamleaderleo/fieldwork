# Tests and receipts — Unit 11: stabilize lifecycle fanout targets

## Current evidence state

`CURRENT-MAIN EXACT-HEAD MATRIX RUNNING`

The prepared source is one commit over current public `main`. Eleven focused assertions remain in the six-file fence. Because the head changed during the rebase, the earlier green workflow matrix is historical evidence only until the new runs complete.

## Identity

- refreshed base: `f278e3b8427c406c271b8cba2c0f1a9c47c2f15e`;
- source branch: `upstream/unit-11-lifecycle-fanout-v2`;
- exact prepared candidate: `f4cb44bcccffbc0eb39e774284655e0f965cfce1`;
- source PR: `teamleaderleo/opentelemetry-js#19`;
- relation: ahead 1, behind 0;
- changed files: three production files and three focused tests.

## Rebase-specific compatibility control

Upstream PR #6929 added `TracerProvider.forceFlush({ timeoutMillis })` after the previous base was pinned. The rebased implementation preserves that option. The provider regression tests now pass the timeout per call rather than introducing new use of the deprecated constructor option.

## Focused assertion set

### `MultiSpanProcessor` — four tests

- shutdown synchronous throw still attempts the later opening processor and rejects;
- shutdown removal still invokes the removed opening processor;
- force-flush synchronous throw still attempts the later processor, reports globally, and resolves;
- force-flush removal still invokes the removed opening processor.

### `TracerProvider.forceFlush()` — three tests

- synchronous throw still attempts the second processor, preserves the one-element error-array rejection, and leaves no fake timer armed;
- live removal does not shrink the opening set;
- a genuinely non-settling processor still times out using the per-call timeout option and leaves no timer afterward.

### Logs — four tests

Shutdown and force flush each cover synchronous throw and live removal while retaining existing rejection and timeout behavior.

### Metrics — intentionally absent

The earlier metrics controls reached private provider state. No supported public mutation path was established, and async metric collector methods already normalize reader throws.

## Fresh exact-head workflow receipts

Started for `f4cb44bcccffbc0eb39e774284655e0f965cfce1`:

| Workflow | Run | Current recorded state |
| --- | ---: | --- |
| Unit Tests | `30956029453` | queued at refresh |
| Lint | `30956029480` | queued at refresh |
| W3C Trace Context Integration Test | `30956029456` | queued at refresh |
| Bundler tests | `30956029470` | queued at refresh |
| Ensure API Peer Dependency | `30956029447` | queued at refresh |
| CodeQL Analysis | `30956029506` | queued at refresh |
| E2E Tests | `30956029462` | queued at refresh |
| Zizmor GitHub Actions Security Analysis | `30956029460` | queued at refresh |
| Old Node.js Compatibility | `30956029502` | queued at refresh |

## Historical exact-head receipts

The previous head `db3d9e5e43d5abc6622784acf0ef87f3b038ac91` passed the then-current eight-workflow matrix and received a complete-diff technical acceptance. Those receipts support the unchanged mechanism but are not claimed as fresh validation of the rebased SHA.

## Current judgment

`EXECUTION UNDER SCRUTINY — NOT YET FINAL FILING DECISION`

Return this packet to a filing decision only after the fresh matrix is classified and the complete rebased diff receives a new exact-head review.
