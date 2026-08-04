# Upstream pull-request draft — fix(sdk-trace, sdk-logs): invoke all lifecycle processors

## Preparation status

`CURRENT-MAIN REBASE COMPLETE — EXACT-HEAD CI RUNNING — PUBLIC FILING UNAUTHORIZED`

- target: `open-telemetry/opentelemetry-js:main`;
- refreshed public-main snapshot: `f278e3b8427c406c271b8cba2c0f1a9c47c2f15e`;
- proposed head: `teamleaderleo/opentelemetry-js:upstream/unit-11-lifecycle-fanout-v2`;
- exact prepared head: `f4cb44bcccffbc0eb39e774284655e0f965cfce1`;
- relation: one commit ahead, zero behind;
- fence: three production files and three focused test files;
- owned preview PR: `teamleaderleo/opentelemetry-js#19`;
- public upstream interaction authorized/performed: `false` / `false`.

The previous exact-head acceptance at `db3d9e5e43d5abc6622784acf0ef87f3b038ac91` is historical evidence only. The current-main rebase retains the six-file mechanism, preserves upstream's newly merged per-call trace timeout option, and requires fresh exact-head workflow and review receipts.

## Current overlap and policy refresh

Refreshed on `2026-08-05`:

- no matching open or closed issue or pull request was found for the synchronous-throw/opening-set lifecycle defect;
- historical PR #802 introduced span-processor force flush but did not address stable opening membership or synchronous-failure timeout cleanup;
- merged PR #6929 adds a per-call trace force-flush timeout and is complementary; the prepared branch retains that API and updates the provider tests to use it;
- current contribution guidance requires unit coverage and changelog entries for behavior changes;
- the current PR template asks for problem, change type, tests, and checklist information.

## Upstream-facing draft

### Which problem is this PR solving?

Trace and log processor fanouts call lifecycle methods while iterating retained processor arrays.

A processor that throws synchronously can stop construction of the remaining promise inputs, so later processors are never attempted. A processor can also mutate the retained array during the call and cause another processor that was present at operation start to be skipped.

`TracerProvider.forceFlush()` has a separate timeout-wrapped fanout. A synchronous throw there can bypass the existing promise rejection path and leave that processor's timeout armed until it expires.

A current repository search found no issue or pull request covering this attempt-all lifecycle defect. The recently merged per-call trace timeout change in #6929 is complementary and is preserved by this branch.

### Short description of the changes

- Snapshot the trace and log processor lists before `forceFlush()` and `shutdown()` fanout begins.
- Invoke each child immediately through a small `try`/`catch` wrapper that converts only direct synchronous throws into rejected promises.
- Preserve the existing trace, logs, and provider settlement policies rather than introducing a new `allSettled` contract.
- Preserve log force-flush timeout wrapping and the new per-call trace timeout option.
- Route synchronous provider failures through the existing catch path so their timers are cleared and their errors retain the existing array shape.
- Add focused regression coverage for direct throws, opening-set mutation, provider timer cleanup, error shape, and genuine timeout behavior.

Metrics is intentionally out of scope: the comparable collector list is internally constructed, and reproducing the same mutation mechanism required private-state access.

### Type of change

- [x] Bug fix (non-breaking change which fixes an issue)
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

### How Has This Been Tested?

Eleven focused assertions cover:

- trace aggregate `forceFlush()` and `shutdown()`;
- log aggregate `forceFlush()` and `shutdown()`;
- synchronous throws without skipping later processors;
- mutation of the caller-retained processor array;
- provider error-array preservation and timeout cleanup;
- a genuinely non-settling processor still timing out.

Exact-head repository workflows are running on `f4cb44bcccffbc0eb39e774284655e0f965cfce1`.

### Changelog

This changes observable lifecycle behavior, so two entries are required. Insert them immediately after the public PR number is assigned:

```md
<!-- root CHANGELOG.md, Unreleased / Bug Fixes -->
* fix(sdk-trace): invoke all lifecycle processors during flush and shutdown [#PR](https://github.com/open-telemetry/opentelemetry-js/pull/PR) @teamleaderleo
```

```md
<!-- experimental/CHANGELOG.md, Unreleased / Bug Fixes -->
* fix(sdk-logs): invoke all lifecycle processors during flush and shutdown [#PR](https://github.com/open-telemetry/opentelemetry-js/pull/PR) @teamleaderleo
```

Do not invent the number on the private carrier.

### Checklist

- [x] Change is limited to one lifecycle-fanout defect.
- [x] Unit tests have been added.
- [x] Current public contribution and changelog guidance has been checked.
- [ ] Exact-head workflows pass after the current-main rebase.
- [ ] Changelog entries contain the assigned public PR number.

## Filing sequence after explicit authorization

1. Reconfirm public `main` still points to the reviewed base or rebase again if it moved materially.
2. Re-run the duplicate/overlap search.
3. Create the public upstream pull request from the prepared fork branch.
4. Use the assigned public PR number in both changelog entries and push that bounded follow-up.
5. Wait for and classify the public exact-head workflow matrix and maintainer feedback.

Creating the public PR, adding public comments, requesting reviewers, or otherwise contacting upstream still requires explicit authorization.
