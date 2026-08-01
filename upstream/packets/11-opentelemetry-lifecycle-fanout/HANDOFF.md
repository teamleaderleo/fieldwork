# Handoff — Unit 11: stabilize lifecycle fanout targets

## Current disposition

`HOLD — clean successor validating`

The supported-path repair is complete and clean. Exact-head workflows are queued. Independent acceptance, changelog packaging, final staleness checks, and public-contact authority remain open.

## Exact identities

- public base/current main: `2c931bf4eec18a234a28706567c6977f08139abd`;
- canonical source branch: `teamleaderleo/opentelemetry-js:upstream/unit-11-lifecycle-fanout-v2`;
- exact clean source head: `f4910b355d12895edf25372444f76d4def08901c`;
- validation carrier: `teamleaderleo/opentelemetry-js#19`;
- superseded carrier: closed PR #18 and branch `upstream/unit-11-lifecycle-fanout`;
- packet branch: `p0/435-unit-11-opentelemetry-lifecycle-fanout`;
- packet path: `upstream/packets/11-opentelemetry-lifecycle-fanout/`;
- exact packet head: record in issue #435 after the final packet write.

## Repair completed

1. `MultiSpanProcessor` snapshots opening processors and protects direct shutdown/force-flush calls.
2. Public `TracerProvider.forceFlush()` snapshots its own fanout targets and routes synchronous throws through existing timeout/error cleanup.
3. `MultiLogRecordProcessor` snapshots opening processors and protects direct calls without changing timeout wrapping.
4. Trace test cleanup installs `loggingErrorHandler()` correctly.
5. Metrics was removed: provider collector mutation required private-state access and no supported public path was established.
6. Public main remained identical to the pinned base and refreshed overlap searches found no replacement contribution.
7. Successor history was collapsed to one commit.

## Final source boundary

- three production files and three target-native tests;
- trace aggregate, public trace provider, and logs only;
- no metrics, workflows, dependency/lock files, generated output, publishers, or research residue;
- source relation ahead 1, behind 0.

## Current exact-head validation

Queued on `f4910b355d12895edf25372444f76d4def08901c`:

- Unit `30694264703`;
- W3C `30694264710`;
- Bundler `30694264711`;
- API peer dependency `30694264708`;
- CodeQL `30694264717`;
- E2E `30694264735`;
- Zizmor `30694264748`;
- Lint `30694264729`.

No successor-head pass is claimed until these settle. Earlier green receipts are historical only.

## Changelog packaging

Target guidance requires:

- root `CHANGELOG.md` Unreleased Bug Fix entry for sdk-trace;
- `experimental/CHANGELOG.md` Unreleased Bug Fix entry for sdk-logs.

Draft wording is preserved in `UPSTREAM_PR.md`. Final entries require the real authorized upstream PR number.

## Continuation steps

1. Refresh all successor workflow conclusions and inspect any failure at job/log level.
2. If all pass, update packet receipts, PR #19, and issue #435 with exact results.
3. Obtain eligible independent complete-diff review of `f4910b355...`; self-review is not final acceptance.
4. Repeat current-main, duplicate/overlap, contribution-policy, and AI-disclosure checks immediately before filing.
5. After explicit authorization and a real upstream PR number, add both changelog entries and update all identities.

## Contact boundary

Public upstream interaction authorized: `false`.  
Public upstream interaction performed: `false`.
