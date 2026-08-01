# Unit 11 — fix: snapshot lifecycle targets before concurrent fanout

## In simple words

OpenTelemetry JS trace, logs, and metrics send shutdown and force-flush calls to lists of child processors or readers. The baseline code iterates those live lists while calling children. A synchronous child exception can stop later calls, and a child can remove a later entry before iteration reaches it.

The proposed change snapshots each opening list and converts synchronous child throws into rejected promises. Every opening child is attempted, existing concurrent fanout and error behavior remain, and mutations still affect future operations.

A predecessor exact head passed the full repository gate set and received an accepted complete-diff review. The current contribution is an upstream-clean six-file restack on the latest inspected public base. Its exact-head workflows are queued on owned PR #18.

## Current disposition

`HOLD`

Last verified: `2026-08-01`  
Worker: `chatgpt:gpt-5.6-thinking`  
Priority-zero parent: [`teamleaderleo/fieldwork#435`](https://github.com/teamleaderleo/fieldwork/issues/435)  
Upstream contact authorized: `no`

## Contribution

- Target project: `open-telemetry/opentelemetry-js`
- Proposed upstream destination: `open-telemetry/opentelemetry-js:main`
- Proposed title: `fix: snapshot lifecycle targets before concurrent fanout`
- Contribution synopsis: snapshot trace processors, log processors, and metric collectors before lifecycle invocation; convert synchronous child throws to rejected promises; preserve eager `Promise.all` fanout, package-specific error behavior, and future collection mutation.
- Work class: `patch-series preparation`

## Exact identities

- Public upstream base inspected: [`2c931bf4eec18a234a28706567c6977f08139abd`](https://github.com/open-telemetry/opentelemetry-js/commit/2c931bf4eec18a234a28706567c6977f08139abd)
- Owned target fork: [`teamleaderleo/opentelemetry-js`](https://github.com/teamleaderleo/opentelemetry-js)
- Canonical source branch: [`upstream/unit-11-lifecycle-fanout`](https://github.com/teamleaderleo/opentelemetry-js/tree/upstream/unit-11-lifecycle-fanout)
- Canonical source head: [`641528c9786f7d027fef4f4a76ae685f7107d394`](https://github.com/teamleaderleo/opentelemetry-js/commit/641528c9786f7d027fef4f4a76ae685f7107d394)
- Fieldwork packet branch: [`p0/435-unit-11-opentelemetry-lifecycle-fanout`](https://github.com/teamleaderleo/fieldwork/tree/p0/435-unit-11-opentelemetry-lifecycle-fanout)
- Fieldwork packet head: exact tip recorded in the final issue #435 handoff
- Execution carriers: owned draft PR [`teamleaderleo/opentelemetry-js#18`](https://github.com/teamleaderleo/opentelemetry-js/pull/18); predecessor PR [`#6`](https://github.com/teamleaderleo/opentelemetry-js/pull/6)
- Superseded carriers: predecessor source head `db7a0b3a2179f43bf1e0145c8352ff0367bdce79` remains the executed/reviewed evidence generation; earlier safe-call-only and test-typing generations are historical.

## Current code and tests

### Product code

- [`MultiSpanProcessor.ts`](https://github.com/teamleaderleo/opentelemetry-js/blob/641528c9786f7d027fef4f4a76ae685f7107d394/packages/sdk-trace/src/MultiSpanProcessor.ts) — snapshot trace processors and safely construct shutdown/force-flush promise inputs.
- [`MultiLogRecordProcessor.ts`](https://github.com/teamleaderleo/opentelemetry-js/blob/641528c9786f7d027fef4f4a76ae685f7107d394/experimental/packages/sdk-logs/src/MultiLogRecordProcessor.ts) — snapshot log processors around timeout-wrapped flush and shutdown.
- [`MeterProvider.ts`](https://github.com/teamleaderleo/opentelemetry-js/blob/641528c9786f7d027fef4f4a76ae685f7107d394/packages/sdk-metrics/src/MeterProvider.ts) — snapshot metric collectors and safely invoke reader lifecycle calls.

### Target-native tests

- [`MultiSpanProcessor.attempt-all.test.ts`](https://github.com/teamleaderleo/opentelemetry-js/blob/641528c9786f7d027fef4f4a76ae685f7107d394/packages/sdk-trace/test/common/MultiSpanProcessor.attempt-all.test.ts) — trace shutdown/force-flush synchronous throw, opening-set mutation, and global error-handler compatibility.
- [`MultiLogRecordProcessor.attempt-all.test.ts`](https://github.com/teamleaderleo/opentelemetry-js/blob/641528c9786f7d027fef4f4a76ae685f7107d394/experimental/packages/sdk-logs/test/common/MultiLogRecordProcessor.attempt-all.test.ts) — logs shutdown/force-flush synchronous throw and opening-set mutation.
- [`MeterProvider.attempt-all.test.ts`](https://github.com/teamleaderleo/opentelemetry-js/blob/641528c9786f7d027fef4f4a76ae685f7107d394/packages/sdk-metrics/test/MeterProvider.attempt-all.test.ts) — metrics shutdown/force-flush synchronous throw, opening-set mutation, and cleanup restoration.

### Required generated or dependency files

- none;
- root and experimental changelog entries remain a packaging decision before authorized submission.

## Changed-file fence

| Path | Role | Keep upstream? |
| --- | --- | --- |
| `packages/sdk-trace/src/MultiSpanProcessor.ts` | production | yes |
| `packages/sdk-trace/test/common/MultiSpanProcessor.attempt-all.test.ts` | regression | yes |
| `experimental/packages/sdk-logs/src/MultiLogRecordProcessor.ts` | production | yes |
| `experimental/packages/sdk-logs/test/common/MultiLogRecordProcessor.attempt-all.test.ts` | regression | yes |
| `packages/sdk-metrics/src/MeterProvider.ts` | production | yes |
| `packages/sdk-metrics/test/MeterProvider.attempt-all.test.ts` | regression | yes |

Complete compare: [`2c931bf...641528c`](https://github.com/teamleaderleo/opentelemetry-js/compare/2c931bf4eec18a234a28706567c6977f08139abd...641528c9786f7d027fef4f4a76ae685f7107d394).

## Evidence summary

| Claim | Evidence class | Exact receipt | Limit |
| --- | --- | --- | --- |
| every opening child is attempted after synchronous throw | `target-executed` predecessor | exact head `db7a0b3...`, Unit `30592187966` | clean-head matrix queued |
| opening membership survives live removal | `target-executed` predecessor | six mutation controls at `db7a0b3...` | additions source-reviewed only |
| ordinary repository gates pass for the accepted generation | `full-gate` predecessor | Lint `30592187969`, E2E `30592187917`, Bundler `30592187954`, W3C `30592187936`, peer `30592187910`, CodeQL `30592187920`, Zizmor `30592187924` | predecessor base `7b06368...` |
| clean source is direct from current inspected public base | `source-read` | compare base `2c931bf...` to head `641528c...`: ahead 6, behind 0, six files | public main can advance |
| exact clean-head workflows are active | `target-test-prepared` | PR #18 runs `30674494779` through `30674494832` | queued at last refresh |
| predecessor complete diff accepted | `source-reviewed` | review `4824609621` on `db7a0b3...` | clean head needs exact review |

## Packet navigation

- [Deep dive](./DEEP_DIVE.md)
- [Approaches](./APPROACHES.md)
- [Tests and receipts](./TESTS.md)
- [Upstream issue draft](./UPSTREAM_ISSUE.md)
- [Upstream pull-request draft](./UPSTREAM_PR.md)
- [Review and human inspection guide](./REVIEW.md)

## Duplicate and prior-art result

- Search date: `2026-08-01`
- Current upstream issues/PRs checked: PR #802, PR #1296, issue #4611, issue #4922, plus searches for `snapshot lifecycle processors`, `MultiSpanProcessor shutdown`, synchronous lifecycle fanout, and the affected symbols.
- Equivalent implementation found: `no`
- Relationship to prior work: historical lifecycle fanout support is complementary; current reports involve different exporter or suppression behavior.

## Remaining work

Complete in this order:

1. settle and classify the eight exact-head workflows on `641528c9786f7d027fef4f4a76ae685f7107d394`;
2. obtain independent complete-diff review of the exact clean compare;
3. recheck public main, duplicate search, contribution policy, AI disclosure, and changelog handling immediately before any authorized submission;
4. squash the six GitHub-contents commits if required by maintainer preference;
5. request explicit authority before any public upstream interaction.

## Blockers and limits

- current clean-head workflows are queued;
- exact clean-head independent review is pending;
- upstream changelog handling is unresolved pending a public PR number or skip decision;
- direct local clone/tests were blocked by worker-network DNS, so current execution uses owned GitHub Actions;
- public upstream interaction remains unauthorized;
- provider one-shot state, delayed recursion, final metrics collection, pre-existing spans, and global disposal are separate units.

## Latest handoff

State: `HOLD`  
Exact source head: `641528c9786f7d027fef4f4a76ae685f7107d394`  
Exact packet head: final issue #435 handoff  
Tests: predecessor full gate pass; current clean-head eight-workflow matrix queued  
Temporary machinery remaining: owned validation base branch `upstream/base-2c931bf4` and draft PR #18  
Next worker action: refresh PR #18 workflow conclusions and update `TESTS.md`, `REVIEW.md`, this README, and issue #435 with the exact results  
Public upstream interaction: `none`
