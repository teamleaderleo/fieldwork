# Handoff — Unit 11: stabilize lifecycle fanout targets

## In simple words

The OpenTelemetry trace/logs lifecycle repair is implemented, narrowed to supported paths, and collapsed to one clean source commit. The remaining decision belongs to the repository owner. Exact-head workflows were triggered and are queued, but that infrastructure state is not being mislabeled as an unfixed code defect.

## Current state

`READY FOR OWNER DECISION — source repaired; exact-head workflows queued`

## Exact identities

- public base/current-main snapshot: `2c931bf4eec18a234a28706567c6977f08139abd`;
- canonical source branch: `teamleaderleo/opentelemetry-js:upstream/unit-11-lifecycle-fanout-v2`;
- exact clean source head: `db3d9e5e43d5abc6622784acf0ef87f3b038ac91`;
- reviewed pre-squash tree source: `987a2bde097fe2e44531830e38c7c15a59c35c23`;
- validation carrier: `teamleaderleo/opentelemetry-js#19`;
- superseded carrier: closed PR #18 and branch `upstream/unit-11-lifecycle-fanout`;
- packet branch: `p0/435-unit-11-opentelemetry-lifecycle-fanout`;
- packet path: `upstream/packets/11-opentelemetry-lifecycle-fanout/`.

The squash reused the exact six candidate file blobs from `987a2bde...`, producing one commit directly on the pinned base without changing source or tests.

## Repair completed

1. `MultiSpanProcessor` snapshots opening processors and protects direct shutdown/force-flush calls.
2. Public `TracerProvider.forceFlush()` snapshots its own fanout targets and routes synchronous throws through existing timeout/error cleanup.
3. `MultiLogRecordProcessor` snapshots opening processors and protects direct calls without changing timeout wrapping.
4. The provider has an explicit genuine-timeout control as a negative compatibility check.
5. Trace test cleanup installs `loggingErrorHandler()` correctly.
6. Metrics was removed because the earlier mutation path required private-state access and no supported public path was established.
7. The source branch was collapsed from four commits to one exact six-file commit.
8. The owned source PR was synchronized to the new head and one-commit relation.

## Final source boundary

- three production files and three target-native tests;
- trace aggregate, public trace provider, and logs only;
- eleven focused assertions;
- no metrics, workflows, dependency/lock files, generated output, publishers, or research residue;
- source relation ahead 1, behind 0.

## Exact-head workflows

Queued on `db3d9e5e43d5abc6622784acf0ef87f3b038ac91`:

- Unit Tests `30756036668`;
- Lint `30756036660`;
- W3C Trace Context Integration `30756036656`;
- Bundler tests `30756036678`;
- Ensure API Peer Dependency `30756036662`;
- CodeQL Analysis `30756036671`;
- E2E Tests `30756036639`;
- Zizmor GitHub Actions Security Analysis `30756036691`.

Earlier heads supplied useful mechanism and repository-gate evidence. They remain historical evidence, not substitutes for exact-head execution.

## Changelog packaging

Target guidance calls for:

- a root `CHANGELOG.md` Unreleased Bug Fix entry for sdk-trace;
- an `experimental/CHANGELOG.md` Unreleased Bug Fix entry for sdk-logs.

Draft wording is preserved in `UPSTREAM_PR.md`. Final entries require the real authorized upstream PR number.

## Decision requested from the repository owner

Decide whether this one-commit candidate should advance toward an upstream proposal once exact-head execution is available. No named external reviewer is a prerequisite or final arbiter. Before filing, refresh current main, duplicate/overlap, contribution policy, and disclosure requirements, then explicitly authorize the public interaction.

## Contact boundary

Public upstream interaction authorized: `false`.  
Public upstream interaction performed: `false`.
