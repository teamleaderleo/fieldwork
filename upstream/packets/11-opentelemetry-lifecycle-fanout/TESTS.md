# Tests and receipts — Unit 11: stabilize lifecycle fanout targets

## In simple words

The exact one-commit candidate passed every named repository workflow. Eleven focused assertions exercise direct synchronous throws, opening-set mutation, provider error shape and timer cleanup, genuine timeout behavior, and trace/log compatibility.

## Identity

- base/current-main snapshot: `2c931bf4eec18a234a28706567c6977f08139abd`;
- source branch: `upstream/unit-11-lifecycle-fanout-v2`;
- exact candidate: `db3d9e5e43d5abc6622784acf0ef87f3b038ac91`;
- source PR: `teamleaderleo/opentelemetry-js#19`;
- relation: ahead 1, behind 0.

## Focused assertion set

### `MultiSpanProcessor` — four tests

- shutdown synchronous throw still attempts the later opening processor and rejects;
- shutdown removal still invokes the removed opening processor;
- force-flush synchronous throw still attempts the later processor, reports globally, and resolves;
- force-flush removal still invokes the removed opening processor.

### `TracerProvider.forceFlush()` — three tests

- synchronous throw still attempts the second processor, preserves the one-element error-array rejection, and leaves no fake timer armed;
- live removal does not shrink the opening set;
- a genuinely non-settling processor still times out and rejects, with no timer left afterward.

### Logs — four tests

Shutdown and force flush each cover synchronous throw and live removal while retaining existing rejection and timeout behavior.

### Metrics — intentionally absent

The earlier metrics controls reached private provider state. No supported public mutation path was established, and async metric collector methods already normalize reader throws.

## Exact-head workflow receipts

| Workflow | Run | Result |
| --- | ---: | --- |
| Unit Tests | `30756036668` | passed |
| Lint | `30756036660` | passed |
| W3C Trace Context Integration | `30756036656` | passed |
| Bundler tests | `30756036678` | passed |
| Ensure API Peer Dependency | `30756036662` | passed |
| CodeQL Analysis | `30756036671` | passed |
| E2E Tests | `30756036639` | passed |
| Zizmor GitHub Actions Security Analysis | `30756036691` | passed |

Evidence class: target-executed across the named repository workflow matrix. These receipts do not claim behavior outside those gates.

## Review result

Independent exact-head review of the complete six-file fence found no blocking source defect and recorded `ACCEPT / TECHNICALLY READY`.

## Current judgment

`TECHNICALLY READY — OWNER DECISION REQUESTED`

Filing-time work is limited to current-main/overlap and policy refresh, changelog entries tied to the real upstream PR number, and explicit public-contact authorization.
