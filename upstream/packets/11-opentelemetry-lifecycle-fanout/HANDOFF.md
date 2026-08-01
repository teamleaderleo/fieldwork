# Handoff — Unit 11: snapshot lifecycle targets before concurrent fanout

## Current disposition

`HOLD — source repair complete`

The bounded repair is applied. The exact repaired head is running its complete repository workflow set. Independent acceptance, source-history cleanup, changelog packaging, final current-main/duplicate refresh, and public-contact authority remain open.

## Exact identities

- public upstream base/current main: `2c931bf4eec18a234a28706567c6977f08139abd`;
- owned source branch: `teamleaderleo/opentelemetry-js:upstream/unit-11-lifecycle-fanout`;
- exact repaired source head: `1b7609141e87ad226e64bb0238ef602e76812896`;
- validation carrier: `teamleaderleo/opentelemetry-js#18`;
- packet branch: `p0/435-unit-11-opentelemetry-lifecycle-fanout`;
- packet path: `upstream/packets/11-opentelemetry-lifecycle-fanout/`;
- exact packet head: record in issue #435 after the final packet write.

## Repair completed

1. Metrics keeps opening `.slice()` snapshots but maps directly to async `MetricCollector.shutdown()` / `forceFlush()`.
2. Metrics synchronous-throw tests were removed; mutation tests remain as reversing controls.
3. Trace retains safe-call and snapshot behavior but restores the baseline outer `new Promise` / `globalErrorHandler` scaffolding.
4. Trace test cleanup now installs `loggingErrorHandler()` rather than the factory function.
5. Packet and validation PR claims now distinguish trace/log direct-call behavior from the metrics async boundary.
6. Public main was rechecked and remained identical to the pinned base.
7. Open public issue/PR searches found no replacement contribution during the repair pass.

## Final source boundary

- trace: snapshot plus eager direct-call protection;
- logs: snapshot plus eager direct-call protection and unchanged timeout wrapping;
- metrics: snapshot only;
- six source/test files;
- no workflows, dependency files, generated output, publishers, or research residue.

The source compare is ahead 10, behind 0. The ten commits are contents-API writes and should be squashed before authorized filing.

## Current exact-head validation

Queued on source head `1b7609141e87ad226e64bb0238ef602e76812896`:

- Unit Tests `30693695553`;
- E2E Tests `30693695548`;
- Lint `30693695562`;
- Bundler tests `30693695536`;
- W3C Trace Context Integration `30693695557`;
- Ensure API Peer Dependency `30693695533`;
- CodeQL Analysis `30693695552`;
- Zizmor GitHub Actions Security Analysis `30693695550`.

The prior exact head passed all named groups, but those receipts are superseded for promotion by source movement.

## Changelog packaging

Target contribution guidance requires:

- root `CHANGELOG.md` Unreleased Bug Fixes entry for sdk-trace/sdk-metrics;
- `experimental/CHANGELOG.md` Unreleased Bug Fixes entry for sdk-logs.

`UPSTREAM_PR.md` preserves draft wording. Final entries must use the real upstream PR number and current link format.

## Continuation steps

1. Refresh the eight repaired-head workflow conclusions and inspect any failure at job/log level.
2. If all pass, update `TESTS.md`, `REVIEW.md`, `README.md`, this handoff, PR #18, and issue #435 with exact success receipts.
3. Obtain eligible independent complete-diff review of `1b760914...`; self-review is not final acceptance.
4. Squash the source commit series before public submission.
5. Repeat current-main, duplicate/overlap, contribution-policy, and AI-disclosure checks immediately before filing.
6. After explicit authorization and a real upstream PR number, add both changelog entries and update all identities.

## Contact boundary

Public upstream interaction authorized: `false`.  
Public upstream interaction performed: `false`.
