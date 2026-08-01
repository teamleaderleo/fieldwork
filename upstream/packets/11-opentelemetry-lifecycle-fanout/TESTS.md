# Tests and receipts — Unit 11: snapshot lifecycle targets before concurrent fanout

## In simple words

The retained predecessor generation passed the full OpenTelemetry JS gate set at exact head `db7a0b3a2179f43bf1e0145c8352ff0367bdce79`. The clean current-base generation contains the same product behavior and assertions, with only research wording removed from test error messages. Its exact-head matrix is queued on owned PR #18.

The largest current gap is exact clean-head completion and independent review. Direct local execution was unavailable because this worker environment could not resolve `github.com` for cloning; that environment failure changes no product claim and is recorded here.

## Identity

- Exact upstream base: `2c931bf4eec18a234a28706567c6977f08139abd`;
- Exact candidate head: `641528c9786f7d027fef4f4a76ae685f7107d394`;
- Exact execution carrier: [`teamleaderleo/opentelemetry-js#18`](https://github.com/teamleaderleo/opentelemetry-js/pull/18);
- Prior executed head: `db7a0b3a2179f43bf1e0145c8352ff0367bdce79` on owned PR #6;
- Test date: 2026-08-01;
- Environment and platform: GitHub Actions repository matrix; local clone unavailable through the worker network.

## Claim-to-evidence matrix

| Claim | Evidence class | Test or source | Result | Coverage limit |
| --- | --- | --- | --- | --- |
| synchronous throw cannot stop later opening invocation | `target-executed` predecessor | six throw controls at `db7a0b3...`; current clean tests at `641528c...` | predecessor passed; clean matrix queued | same test logic, neutralized error strings |
| removing a later child cannot shrink current operation | `target-executed` predecessor | six opening-snapshot controls at `db7a0b3...` | passed | additions are source-reviewed, not separately asserted |
| mutation remains visible to future operations | `target-executed` predecessor | backing-array postcondition assertions | passed | no duplicate-child policy |
| trace force flush retains global error reporting and resolution | `target-executed` predecessor | trace force-flush error-handler test | passed | first observed error only |
| logs and metrics retain rejection | `target-executed` predecessor | `assert.rejects` controls | passed | first observed error only |
| current clean branch is direct from current public base | `source-read` | compare `2c931bf...641528c...` | six files, ahead 6, behind 0 | public main may advance later |

## Baseline characterization

### Command or workflow

```text
Source review of the six lifecycle entrypoints at public base 2c931bf4eec18a234a28706567c6977f08139abd
plus focused tests applied to the candidate.
```

### Assertions

- direct synchronous child throw interrupts construction of later promise inputs;
- live indexed iteration can skip a later child removed by an earlier callback;
- the stable-opening tests are reversing controls for the base source.

### Result

- status: baseline mechanism confirmed by source and JavaScript iteration semantics;
- test count: six current-operation controls across three packages and two lifecycle methods, plus six synchronous-throw controls;
- workflow and job: direct baseline workflow run was not created in this session;
- artifact or receipt: prior review discussion on owned PR #6 and canonical finding F194;
- observed behavior: baseline lacks a snapshot and safe-call combination.

## Candidate-focused tests

### Trace processor fanout

- Exact source head: `641528c9786f7d027fef4f4a76ae685f7107d394`;
- Command or workflow: Unit Tests run `30674494793`;
- Tests and assertions: shutdown throw, shutdown removal, force-flush throw with global error handler, force-flush removal;
- Result: queued at packet creation; predecessor assertions passed at `db7a0b3...`;
- Failure classification, if red: pending;
- Coverage limit: no settle-all aggregation and no delayed recursion.

### Log processor fanout

- Exact source head: `641528c9786f7d027fef4f4a76ae685f7107d394`;
- Command or workflow: Unit Tests run `30674494793`;
- Tests and assertions: shutdown throw/removal and force-flush throw/removal;
- Result: queued at packet creation; predecessor assertions passed;
- Failure classification, if red: pending;
- Coverage limit: timeout behavior retained by source; no timeout-expiry control added.

### Metric collector fanout

- Exact source head: `641528c9786f7d027fef4f4a76ae685f7107d394`;
- Command or workflow: Unit Tests run `30674494793`;
- Tests and assertions: shutdown throw/removal and force-flush throw/removal, including restoration before cleanup;
- Result: queued at packet creation; predecessor assertions passed;
- Failure classification, if red: pending;
- Coverage limit: one-shot shutdown and final reader collection are excluded.

## Ordinary repository gates

| Gate | Exact command or workflow | Result | Notes |
| --- | --- | --- | --- |
| format | covered by Lint workflow `30674494830` | queued | predecessor Lint `30592187969` passed |
| lint | Lint `30674494830` | queued | includes compile-bearing checks in repository workflow |
| typecheck or compile | Unit/Lint repository workflows | queued | predecessor exact head passed after explicit callback typing repair |
| focused package tests | Unit Tests `30674494793` | queued | contains all three package test files |
| complete target-declared suite | Unit `30674494793`, E2E `30674494785` | queued | predecessor both passed |
| build or generated output | Bundler `30674494832`, peer dependency `30674494801` | queued | no generated or dependency files changed |
| platform matrix | Unit and E2E matrix | queued | repository-defined runners |
| trace context integration | W3C `30674494799` | queued | predecessor passed |
| static/security | CodeQL `30674494779`, Zizmor `30674494823` | queued | predecessor passed |
| changelog | repository changelog policy | not present | add entries after a public PR number or obtain an explicit skip decision |

### Prior exact-head receipts

All of the following completed successfully on `db7a0b3a2179f43bf1e0145c8352ff0367bdce79`:

- Unit Tests `30592187966`;
- Lint `30592187969`;
- E2E Tests `30592187917`;
- Bundler tests `30592187954`;
- W3C Trace Context Integration `30592187936`;
- Ensure API Peer Dependency `30592187910`;
- CodeQL Analysis `30592187920`;
- Zizmor GitHub Actions Security Analysis `30592187924`.

The owned-fork changelog check was skipped under the research-carrier policy; upstream contribution guidance generally expects changelog entries for behavior changes.

## Reversing controls

- remove the second opening child from the live array during the first callback: baseline source can skip it; candidate snapshot invokes it;
- throw synchronously from the first child: baseline source stops construction; candidate invokes the second and returns the established package error result;
- assert the original backing array remains mutated: both intended future mutability and current snapshot behavior are distinguished;
- trace force flush checks the global handler and resolved aggregate behavior.

## Soak, leak, and cleanup controls

- iterations: not applicable to this bounded fanout change;
- resources observed: processor and collector invocation counters;
- timers/tasks/processes/files/listeners before and after: no new long-lived resources;
- cancellation or interruption behavior: not applicable;
- immediate rerun result: current exact-head workflow matrix queued.

## Setup and harness failures

| Attempt | Failure | Classification | Product claim affected? | Repair or stop |
| --- | --- | --- | --- | --- |
| `e19247b801817abaf8c9fff5a39d00783d8c38e6` | TS2322: mutation callbacks inferred as `() => never` | fixture/test typing | no | explicitly type callbacks as `() => void`; replacement head passed |
| worker local clone, 2026-08-01 | DNS resolution for `github.com` unavailable | runner/network | no | use commit-pinned GitHub reads and owned-fork workflows |

## Checks prepared but not executed

- current clean-head focused tests — queued in Unit Tests `30674494793`;
- current clean-head ordinary gates — queued in the eight workflow runs listed above;
- direct baseline checkout execution — unavailable in this worker session;
- clean-head independent complete-diff review — pending.

## Platform and integration gaps

- no production prevalence measurement;
- no separate browser or server integration path is relevant to these package-local lifecycle methods;
- no extreme child-count allocation benchmark;
- public upstream main must be rechecked immediately before any authorized submission.

## Cleanup receipt

- Temporary workflows removed from canonical source head: yes;
- Publisher or execution-only files removed: yes;
- Generated residue checked: yes, changed-file fence is six source/test files;
- Immediate rerun performed: workflow matrix triggered on clean head;
- Remaining temporary branches or PRs: owned validation base `upstream/base-2c931bf4` and draft PR #18; retain until current matrix and review settle, then close/delete as appropriate.

## Current test judgment

`HOLD`

Reason: the technical direction has full exact-head predecessor execution and an accepted prior complete-diff review. The current-base clean restack is queued for its own matrix, lacks an exact clean-head independent review, and still needs upstream changelog packaging.

Clearing condition: all required workflows complete successfully on `641528c9786f7d027fef4f4a76ae685f7107d394`, a reviewer accepts the exact six-file clean diff, and changelog handling is resolved.
