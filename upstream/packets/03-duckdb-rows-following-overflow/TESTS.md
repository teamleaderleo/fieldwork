# Tests and receipts — unit 03 ROWS FOLLOWING overflow

## In simple words

The baseline defect was executed with DuckDB's native SQLLogicTest runner and produced the wrong whole-partition frame. The one-line repair passed the same extreme query and ordinary controls on the historical source. A current-main worktree also compiled and passed the focused regression. Its complete `test/sql/window` run failed, so the workflow withheld formatting and clean-branch publication. The exact failing window case remains the next evidence task.

## Identity

- Exact current upstream base: `63094a6f725af5045113dda74e291c7d604f6a88`
- Exact canonical source head: `63094a6f725af5045113dda74e291c7d604f6a88` — unchanged clean base because publication was skipped
- Exact execution carrier head: `bf703f57b15555c2db68520b1f4165e23ca737ae`
- Current-main run: `30674257475`
- Current-main job: `91298115859`
- Test date: `2026-07-31` through `2026-08-01`
- Environment and platform: GitHub Actions Ubuntu 24.04; CMake/Ninja Debug current-main worktree; historical DuckDB native runner on GitHub Actions Ubuntu

## Claim-to-evidence matrix

| Claim | Evidence class | Test or source | Result | Coverage limit |
| --- | --- | --- | --- | --- |
| Extreme FOLLOWING returns whole-partition results on baseline | `target-executed` | Fieldwork run [`30580996108`](https://github.com/teamleaderleo/fieldwork/actions/runs/30580996108) and report [`735a2e184bc6039c64a341449d01977f4091311e`](https://github.com/teamleaderleo/fieldwork/commit/735a2e184bc6039c64a341449d01977f4091311e) | reproduced | historical source `de477da...` |
| Ordinary `1 FOLLOWING` remains correct on baseline | `target-executed` | same Fieldwork run | pass | one ordinary control |
| Partition-end repair fixes the focused extreme result | `target-executed` | historical owned run [`30595242656`](https://github.com/teamleaderleo/duckdb/actions/runs/30595242656) | pass | execution-applied patch on historical source |
| Regression reverses on source without repair | `target-executed` | Main run [`30595243144`](https://github.com/teamleaderleo/duckdb/actions/runs/30595243144), Relassert job `91057026663` | intended regression failed; 252 smoke tests passed | synthetic carrier merge without production repair |
| Current-main candidate compiles | `target-executed` | run [`30674257475`](https://github.com/teamleaderleo/duckdb/actions/runs/30674257475), job `91298115859` | pass | materialized runner worktree only |
| Current-main focused regression passes | `target-executed` | same run/job | pass | focused SQLLogicTest file |
| Current-main complete window directory passes | `target-executed` | same run/job | fail | exact failing case was unavailable from connector-visible logs in this session |
| Current-main formatting passes | `target-test-prepared` | `make format-check` in same workflow | skipped | prior gate failed |
| Clean two-file source head exists | `target-test-prepared` | publisher step in same workflow | skipped | branch remains at clean base |

## Baseline characterization

### Command or workflow

```text
DuckDB native SQLLogicTest runner through Fieldwork workflow run 30580996108
```

### Assertions

- `INT64_MAX FOLLOWING` yields zero rows in each frame.
- ordinary `1 FOLLOWING` yields the next row and an empty final frame.

### Result

- status: defect reproduced
- workflow: `30580996108`
- artifact: `8775602128`
- digest: `sha256:1a5643009c07488c685ce498bf5203ec72286ae742edbc44c472c2f495749d5c`
- observed behavior: rows one and two returned count `3` and list `[0, 1, 2]`

## Candidate-focused tests

### Historical one-line repair

- Exact source: `de477da7606fc2d857f81117f0140d0550a5c42c` plus patch blob [`9376f3413b252253a7388883b3fd4d3cde1aa00d`](https://github.com/teamleaderleo/duckdb/blob/2cfe22d250f5501a097b5f994ca01498513b939c/fieldwork/window_rows_following_overflow.patch)
- Workflow: [`30595242656`](https://github.com/teamleaderleo/duckdb/actions/runs/30595242656)
- Assertions: exact extreme reproduction, ordinary bounded control, partition isolation
- Result: pass
- Limit: the source patch was applied during execution; PR head itself remained a carrier

### Historical baseline reversal through Main CI

- Exact source head: synthetic merge `914d14b862136fab1b7b4fc8c6d68bf3e55789ab`
- Command: `make smoke T="--changed-tests=/home/runner/work/_temp/changed_tests.txt"`
- Result: 252 passed, one failed; the regression produced the exact baseline whole-partition output
- Classification: expected baseline product failure caused by carrier topology
- Limit: proves the test reverses; it does not evaluate the source repair

### Current-main clean-candidate worktree

- Upstream checkout: `63094a6f725af5045113dda74e291c7d604f6a88`
- Carrier checkout: `bf703f57b15555c2db68520b1f4165e23ca737ae`
- Workflow: [`30674257475`](https://github.com/teamleaderleo/duckdb/actions/runs/30674257475)
- Job: `91298115859`
- Materialization: patch applied and regression copied successfully
- Configure: pass
- Build: `cmake --build build/fieldwork --target unittest --parallel 2` — pass
- Focused command: `./build/fieldwork/test/run 'test/sql/window/test_rows_following_overflow.test'` — pass
- Ordinary affected-suite command: `./build/fieldwork/test/run 'test/sql/window'` — fail
- Formatting: skipped after the failed suite
- Publisher: skipped after the failed suite
- Failure classification: unresolved until the exact failing case/output is extracted or reproduced
- Limit: candidate existed only in the runner worktree; no commit identifies the materialized two-file tree

## Ordinary repository gates

| Gate | Exact command or workflow | Result | Notes |
| --- | --- | --- | --- |
| format | historical Main `Check format`; current `make format-check` | historical pass; current skipped | complete window gate stopped the job |
| lint | historical Main `Lint CI` and Tidy Check | pass on historical carrier | current candidate has no new lint construct beyond one assignment |
| compile | current `cmake --build build/fieldwork --target unittest --parallel 2` | pass | Ubuntu Debug |
| focused regression | exact `test_rows_following_overflow.test` | historical pass; current-main pass | includes extreme, ordinary, and partition controls |
| affected suite | complete `test/sql/window` | fail | exact failing case remains unextracted |
| complete target-declared suite | `make unit` / `make allunit` | not run | outside the current carrier |
| release/relassert | project builds on final clean source head | not run | clean candidate head absent |
| platform matrix | project CI matrix | not run | human-authorship stop also remains |

## Reversing controls

- The regression fails on the unmodified source and passes when the repair is applied.
- Ordinary `1 FOLLOWING` passes on baseline and repaired execution.
- Multi-partition extreme offsets verify each frame uses its own partition end.
- The complete window directory exposed a remaining red gate on current main.

## Setup and harness failures

| Attempt | Failure | Classification | Product claim affected? | Repair or stop |
| --- | --- | --- | --- | --- |
| historical early carrier linked from `#240` | initial arrangement lacked an immutable clean-source receipt | setup | no | rebuilt evidence on exact source and retained PR `#253` |
| Main run `30595243144` | regression failed because the patch artifact was absent from the synthetic merge | carrier topology | no; supplied baseline reversal | replaced with materialized candidate workflow |
| current run `30674257475` | complete `test/sql/window` failed after focused success | unresolved product/test interaction | yes, blocks clean publication | extract exact failure, classify, repair or rerun |

## Checks prepared but not executed

- `make format-check` on current candidate — skipped after suite failure.
- Full `make unit` — outside the bounded carrier.
- `make allunit` — outside the bounded carrier.
- macOS and Windows matrices — remain for an eligible human-owned candidate.

## Cleanup receipt

- Temporary workflows removed from canonical source head: yes; canonical source branch remains the upstream base
- Publisher or execution-only files removed from canonical source head: yes; none were published there
- Generated residue checked: publisher had a two-path fence but never ran
- Immediate rerun performed: historical yes; current focused pass followed by window-directory failure
- Remaining temporary branches or PRs: `exec/unit-03-window-overflow-materialize`, owned PR `#17`, historical PR `#8`, accidental Fieldwork branch `dummy-no`

## Current test judgment

`HOLD`

Reason: the defect and one-line correction retain strong historical evidence, and the focused current-main regression passes. The complete current-main window-directory gate is red, so no clean candidate head was published. The exact failure requires classification before any technical acceptance. DuckDB's current AI contribution policy separately requires independent human authorship or reimplementation for any public submission.

Clearing condition: identify the exact failure from run `30674257475`, repair the candidate or invocation as required, rerun focused regression plus complete `test/sql/window` plus formatting, publish an exact clean two-file head, and obtain independent human authorship/review and contact authority.
