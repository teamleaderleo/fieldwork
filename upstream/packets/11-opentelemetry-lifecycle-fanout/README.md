# Unit 11 — OpenTelemetry lifecycle fanout

## Current state

`SUBMITTED — UPSTREAM PR OPEN — WAITING ON REVIEWERS`

Last refreshed: `2026-08-06`

- live issue: [open-telemetry/opentelemetry-js#6977](https://redirect.github.com/open-telemetry/opentelemetry-js/issues/6977)
- live pull request: [open-telemetry/opentelemetry-js#6980](https://redirect.github.com/open-telemetry/opentelemetry-js/pull/6980)
- owned source preview: [teamleaderleo/opentelemetry-js#19](https://github.com/teamleaderleo/opentelemetry-js/pull/19)
- final source head: `1e5bd20fb823a9c47a2b2ccc974e18d88b765f16`
- upstream base at submission: `7f3e7eaa9f6bbc9622136479ed846f98c760a408`
- packet branch: `p0/435-unit-11-opentelemetry-lifecycle-fanout-current`

The issue was filed first. The pull request followed after the review window, with `Fixes #6977`, two changelog entries, a signed commit, a signed CLA, and an `Assisted-by: ChatGPT GPT-5.6 Thinking` trailer.

## Contribution

The patch preserves the processor set present when lifecycle work begins:

```text
opening processors = snapshot(current processors)

call every processor in the snapshot
route direct throws into the existing promise path
preserve the existing result and timeout policy
```

The production change is limited to:

- shallow snapshots in trace and log lifecycle fanout;
- a small direct-throw adapter;
- provider timeout cleanup through the existing catch path.

Metrics remains outside the patch. Public APIs, configuration, dependencies, and normal telemetry processing remain unchanged.

## Final code boundary

1. `CHANGELOG.md`
2. `experimental/CHANGELOG.md`
3. `packages/sdk-trace/src/MultiSpanProcessor.ts`
4. `packages/sdk-trace/src/TracerProvider.ts`
5. `packages/sdk-trace/test/common/MultiSpanProcessor.attempt-all.test.ts`
6. `packages/sdk-trace/test/common/TracerProvider.attempt-all.test.ts`
7. `experimental/packages/sdk-logs/src/MultiLogRecordProcessor.ts`
8. `experimental/packages/sdk-logs/test/common/MultiLogRecordProcessor.attempt-all.test.ts`

## Validation

All workflows on the owned fork passed for the final signed head:

- Unit Tests `31073507119`
- Lint `31073507124`
- E2E Tests `31073507094`
- Bundler tests `31073507109`
- W3C Trace Context Integration Test `31073507096`
- CodeQL Analysis `31073507092`
- Ensure API Peer Dependency `31073507111`
- Zizmor GitHub Actions Security Analysis `31073507376`
- changelog `31073507108`

The upstream workflows currently show `action_required` because a maintainer must approve workflow execution for the fork-originated pull request. No upstream test job has failed.

EasyCLA passes. The pull-request dashboard reports `Waiting on reviewers`.

## Packet navigation

- [Submitted issue record](./UPSTREAM_ISSUE.md)
- [Submitted pull-request record](./UPSTREAM_PR.md)
- [Deep dive](./DEEP_DIVE.md)
- [Approaches and rejected designs](./APPROACHES.md)
- [Tests and receipts](./TESTS.md)
- [Final review](./REVIEW.md)
- [Handoff and lessons](./HANDOFF.md)

## Contact record

Public upstream interaction authorized: `true`  
Public upstream interaction performed: `true`
