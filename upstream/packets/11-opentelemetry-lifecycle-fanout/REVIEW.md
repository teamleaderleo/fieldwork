# Review — Unit 11: snapshot lifecycle targets before concurrent fanout

## In simple words

The proposed contribution makes lifecycle membership deterministic for trace processors, log processors, and metric readers. It copies the opening list, catches synchronous child throws as promise rejections, and retains the existing concurrent `Promise.all` behavior.

The prior exact generation passed the full gate set and received an accepted independent review. The current source is cleaner and based directly on the latest inspected public revision. A final reviewer should challenge the trace force-flush equivalence, package-specific error behavior, and whether upstream wants changelog entries or a skip.

## Review subject

- Work class: patch-series preparation;
- Target repository: `open-telemetry/opentelemetry-js`;
- Proposed upstream base: `main` at `2c931bf4eec18a234a28706567c6977f08139abd`;
- Canonical source branch: `teamleaderleo/opentelemetry-js:upstream/unit-11-lifecycle-fanout`;
- Exact source head: `641528c9786f7d027fef4f4a76ae685f7107d394`;
- Fieldwork packet branch: `p0/435-unit-11-opentelemetry-lifecycle-fanout`;
- Exact packet head: recorded in the final issue #435 handoff because the packet cannot self-record its own tip;
- Complete changed-file fence: six source/test files;
- Upstream-contact authority: none.

## Review reading order

1. [`README.md`](./README.md)
2. [`DEEP_DIVE.md`](./DEEP_DIVE.md)
3. [`APPROACHES.md`](./APPROACHES.md)
4. [`TESTS.md`](./TESTS.md)
5. [exact complete compare](https://github.com/teamleaderleo/opentelemetry-js/compare/2c931bf4eec18a234a28706567c6977f08139abd...641528c9786f7d027fef4f4a76ae685f7107d394)
6. production and test files linked below
7. [`UPSTREAM_ISSUE.md`](./UPSTREAM_ISSUE.md)
8. [`UPSTREAM_PR.md`](./UPSTREAM_PR.md)

## Exact diff links

- complete compare: [`2c931bf...641528c`](https://github.com/teamleaderleo/opentelemetry-js/compare/2c931bf4eec18a234a28706567c6977f08139abd...641528c9786f7d027fef4f4a76ae685f7107d394);
- production files:
  - [logs](https://github.com/teamleaderleo/opentelemetry-js/blob/641528c9786f7d027fef4f4a76ae685f7107d394/experimental/packages/sdk-logs/src/MultiLogRecordProcessor.ts);
  - [metrics](https://github.com/teamleaderleo/opentelemetry-js/blob/641528c9786f7d027fef4f4a76ae685f7107d394/packages/sdk-metrics/src/MeterProvider.ts);
  - [trace](https://github.com/teamleaderleo/opentelemetry-js/blob/641528c9786f7d027fef4f4a76ae685f7107d394/packages/sdk-trace/src/MultiSpanProcessor.ts);
- tests:
  - [logs](https://github.com/teamleaderleo/opentelemetry-js/blob/641528c9786f7d027fef4f4a76ae685f7107d394/experimental/packages/sdk-logs/test/common/MultiLogRecordProcessor.attempt-all.test.ts);
  - [metrics](https://github.com/teamleaderleo/opentelemetry-js/blob/641528c9786f7d027fef4f4a76ae685f7107d394/packages/sdk-metrics/test/MeterProvider.attempt-all.test.ts);
  - [trace](https://github.com/teamleaderleo/opentelemetry-js/blob/641528c9786f7d027fef4f4a76ae685f7107d394/packages/sdk-trace/test/common/MultiSpanProcessor.attempt-all.test.ts);
- generated or dependency files: none.

## Claims requiring judgment

| Claim or design choice | Evidence | Reviewer question |
| --- | --- | --- |
| opening membership should remain stable | six mutation controls and source invariant | should live removal alter a lifecycle call already in progress? |
| synchronous throw should not stop later invocation | six throw controls | does converting sync throw to rejection retain all package contracts? |
| trace force flush remains compatible | source diff and handler assertion | does `Promise.all(...).then(success, failure)` match prior resolve-after-handler behavior? |
| future mutation remains supported | post-operation backing-array assertions | are there any documented live-current-operation mutation semantics? |
| local helpers are preferable for this patch | six-file scope | should helper sharing be requested now or deferred? |
| first-rejection behavior remains | `Promise.all` retained | is settle-all desired as a separate contract discussion? |

## Known risks

- The clean branch has six commits because GitHub contents writes were the available repository-write path. Squash before authorized public submission unless maintainers prefer the series.
- Current exact-head workflows remain queued.
- Root and experimental changelog entries are absent pending a public PR number or explicit skip decision.
- Public main may advance after the inspected base.
- The current head differs from independently reviewed `db7a0b3...` only by current-base ancestry and removal of `fieldwork` from test error strings, yet exact-head independent review still remains appropriate.

## Evidence limits

- no production frequency or severity estimate;
- no extreme child-count benchmark;
- no separate integration environment beyond repository gates;
- direct local test execution unavailable in this worker environment;
- adjacent lifecycle state and delayed recursion excluded.

## Staleness check

- Current upstream head checked: `2c931bf4eec18a234a28706567c6977f08139abd` on 2026-08-01;
- Candidate base relationship: ahead 6, behind 0, merge base equals the inspected upstream head;
- Relevant source paths changed upstream since predecessor execution: no; the only newer upstream commit touched sampler-jaeger-remote files and changelogs;
- Duplicate/overlap search date: 2026-08-01;
- Open replacement work found: none;
- Packet and target PR descriptions synchronized: yes at packet creation.

## Source cleanliness

- [x] No research-only files in target source diff.
- [x] No temporary workflows or publishers.
- [x] No stale execution artifacts.
- [x] No unrelated formatting or generated churn.
- [x] Required snapshots or lock changes are not applicable.
- [x] Commit-pinned links resolve to the reviewed head.

## Test review

- [x] Intended assertion ran on predecessor exact head.
- [x] Baseline/candidate relationship is clear.
- [x] Setup and product failures are separated.
- [x] Synchronous failure and mutation paths are covered.
- [x] Package error-policy compatibility controls are present.
- [x] Platform and integration limits are explicit.
- [x] Ordinary target gates are named accurately.
- [ ] Current clean-head matrix completed.

## Draft review

- [x] Issue fallback avoids prevalence claims.
- [x] PR draft describes the actual current diff.
- [x] Target terminology and contribution format are used.
- [x] Internal process vocabulary and private context are absent from the public-facing sections.
- [ ] AI disclosure requirement rechecked at filing time.

## Reviewer disposition

`HOLD`

Reviewed source head: `641528c9786f7d027fef4f4a76ae685f7107d394`  
Reviewed packet head: final issue #435 handoff  
Reason: self-review finds a narrow, clean, current-base six-file candidate with strong predecessor execution. Current clean-head workflows, exact clean-head independent review, changelog handling, and submission authorization remain open.  
Clearing condition: exact clean-head matrix passes, independent review accepts the six-file compare, and changelog/submission policy is resolved.  
Reviewer eligibility: `self-review only`; prior independent review `4824609621` applies to predecessor `db7a0b3...`.

## Human deep-dive guide

The final human reviewer should focus on:

1. trace force-flush resolution and global error-handler equivalence;
2. whether opening-snapshot membership matches maintainer expectations for mutable processor arrays;
3. the clean-head matrix and changelog requirement;
4. whether direct PR remains preferable to issue-first discussion.

Suggested response:

`Unit 11 looks ready for upstream preparation`  
—or—  
`Unit 11 concern: <specific source, test, compatibility, or framing issue>`
