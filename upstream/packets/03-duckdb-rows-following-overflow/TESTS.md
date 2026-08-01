# Tests and receipts — unit 03 ROWS FOLLOWING overflow

## In simple words

The baseline was executed with DuckDB's native SQLLogicTest runner and produced the wrong whole-partition frame. The one-line repair then passed the same extreme query and an ordinary following-frame control on the historical source. The historical generic Main run also supplied a useful red control because its synthetic merge contained the test but left the production source unchanged. A clean current-main run is compiling the final two-file candidate and will execute the focused regression, the complete `test/sql/window` directory, and the formatting gate.

## Identity

- Exact upstream base: `63094a6f725af5045113dda74e291c7d604f6a88`
- Exact candidate head: pending publication by run `30674257475`
- Exact execution carrier head: `bf703f57b15555c2db68520b1f4165e23ca737ae`
- Test date: `2026-07-31` through `2026-08-01`
- Environment and platform: GitHub Actions Ubuntu 24.04, CMake/Ninja Debug for current-main carrier; historical DuckDB native runner on GitHub Actions Ubuntu

## Claim-to-evidence matrix

| Claim | Evidence class | Test or source | Result | Coverage limit |
| --- | --- | --- | --- | --- |
| Extreme FOLLOWING returns whole-partition results on baseline | target-executed | Fieldwork run [`30580996108`](https://github.com/teamleaderleo/fieldwork/actions/runs/30580996108) and report [`735a2e184bc6039c64a341449d01977f4091311e`](https://github.com/teamleaderleo/fieldwork/commit/735a2e184bc6039c64a341449d01977f4091311e) | reproduced | historical source `de477da...` |
| Ordinary `1 FOLLOWING` remains correct on baseline | target-executed | same Fieldwork run | pass | single ordinary control |
| Partition-end source repair fixes extreme result | target-executed | owned run [`30595242656`](https://github.com/teamleaderleo/duckdb/actions/runs/30595242656) | pass | historical source, execution-applied patch |
| Regression reverses on source without repair | target-executed | Main run [`30595243144`](https://github.com/teamleaderleo/duckdb/actions/runs/30595243144), Relassert job `91057026663` | intended regression failed; 252 smoke tests passed | synthetic carrier merge, not repaired source |
| Current-main candidate compiles and passes affected suite | integration-executed | run [`30674257475`](https://github.com/teamleaderleo/duckdb/actions/runs/30674257475) | pending in this revision | Ubuntu only |

## Baseline characterization

### Command or workflow

```text
DuckDB native SQLLogicTest runner through Fieldwork workflow run 30580996108
```

### Assertions

- `INT64_MAX FOLLOWING` yields zero rows in each frame.
- ordinary `1 FOLLOWING` still yields the next row and an empty final frame.

### Result

- status: defect reproduced
- test count: exact retained characterization plus ordinary control
- workflow and job: run `30580996108`; exact job retained by `teamleaderleo/fieldwork#253`
- artifact or receipt: artifact `8775602128`, digest `sha256:1a5643009c07488c685ce498bf5203ec72286ae742edbc44c472c2f495749d5c`
- observed behavior: rows one and two returned count `3` and list `[0, 1, 2]`

## Candidate-focused tests

### Historical one-line repair

- Exact source head: immutable source `de477da7606fc2d857f81117f0140d0550a5c42c` plus patch blob [`9376f3413b252253a7388883b3fd4d3cde1aa00d`](https://github.com/teamleaderleo/duckdb/blob/2cfe22d250f5501a097b5f994ca01498513b939c/fieldwork/window_rows_following_overflow.patch)
- Command or workflow: custom owned-fork run [`30595242656`](https://github.com/teamleaderleo/duckdb/actions/runs/30595242656)
- Tests and assertions: exact extreme reproduction and ordinary bounded control
- Result: pass
- Failure classification, if red: not applicable
- Coverage limit: source patch was applied during execution; PR head itself was a carrier

### Historical baseline reversal through Main CI

- Exact source head: synthetic merge `914d14b862136fab1b7b4fc8c6d68bf3e55789ab`
- Command or workflow: `make smoke T="--changed-tests=/home/runner/work/_temp/changed_tests.txt"`
- Tests and assertions: DuckDB smoke list plus the changed regression file
- Result: 252 passed, one failed; the failed regression produced the exact baseline whole-partition output
- Failure classification, if red: expected baseline product failure caused by carrier topology
- Coverage limit: proves the test reverses; does not evaluate the source repair

### Current-main clean candidate

- Exact source head: pending publication to `fix/window-rows-following-overflow`
- Command or workflow: run [`30674257475`](https://github.com/teamleaderleo/duckdb/actions/runs/30674257475)
- Tests and assertions:
  - `./build/fieldwork/test/run 'test/sql/window/test_rows_following_overflow.test'`
  - `./build/fieldwork/test/run 'test/sql/window'`
  - `make format-check`
- Result: build in progress at this packet revision
- Failure classification, if red: pending
- Coverage limit: Ubuntu Debug build; complete window SQLLogicTest directory, not complete DuckDB unit suite

## Ordinary repository gates

| Gate | Exact command or workflow | Result | Notes |
| --- | --- | --- | --- |
| format | historical Main `Check format`; current `make format-check` | historical pass; current pending | exact current candidate result required |
| lint | historical Main `Lint CI` and Tidy Check | pass on carrier | source repair line has no new lint construct |
| typecheck or compile | current `cmake --build build/fieldwork --target unittest --parallel 2` | pending | Ubuntu Debug |
| focused package tests | exact regression file | historical repair pass; current pending | includes ordinary and partition controls |
| complete target-declared suite | `make unit` / `make allunit` | not run | current carrier intentionally limits scope |
| build or generated output | native `unittest` build | historical pass; current pending | no generated output |
| platform matrix | project CI matrix | not run on clean final source head | policy and authorship stop remains |

## Reversing controls

- The regression fails on the unmodified synthetic merge and passes when the repair patch is applied.
- Ordinary `1 FOLLOWING` passes on baseline and repaired execution.
- Multi-partition extreme offsets verify each frame saturates to its own partition end.
- The complete window directory is the current unrelated-behavior control.

## Soak, leak, and cleanup controls

- iterations: deterministic retries occurred on the baseline red test; no dedicated soak needed for pure arithmetic
- resources observed: no files, processes, listeners, or persistent state owned by the product path
- timers/tasks/processes/files/listeners before and after: not applicable
- cancellation or interruption behavior: not applicable
- immediate rerun result: historical baseline failure repeated across retries; historical repaired test passed

## Setup and harness failures

| Attempt | Failure | Classification | Product claim affected? | Repair or stop |
| --- | --- | --- | --- | --- |
| historical early carrier run linked from `#240` | first workflow/harness arrangement did not give an immutable clean source receipt | setup | no | rebuilt evidence on exact source and retained PR `#253` |
| Main run `30595243144` | regression failed after successful build because source patch artifact was never applied to the synthetic merge | packaging/carrier topology | no; supplied baseline reversal | classify accurately and replace carrier with clean source branch |

## Checks prepared but not executed

- Full `make unit` — outside the current bounded carrier.
- `make allunit` — outside the current bounded carrier.
- macOS and Windows matrices — remain for an eligible human-authored upstream candidate.

## Platform and integration gaps

- macOS and Windows
- release and relassert builds on the final clean source head
- full extension and packaging matrices
- complete unit/allunit suites

## Cleanup receipt

- Temporary workflows removed from canonical source head: pending publication; intended yes
- Publisher or execution-only files removed: pending publication; intended yes
- Generated residue checked: workflow enforces a two-path tracked change before commit
- Immediate rerun performed: historical yes; current focused then complete window directory
- Remaining temporary branches or PRs: `exec/unit-03-window-overflow-materialize`, owned PR `#17`, historical carrier PR `#8`

## Current test judgment

`EXECUTE`

Reason: the defect and selected correction have strong historical native evidence, and current public main still contains the same branch. Exact current-main clean-source execution is the final technical gate. Upstream readiness remains independently blocked by DuckDB's generative-AI contribution policy.

Clearing condition: run `30674257475` publishes a clean two-file source head with focused regression, complete `test/sql/window`, and formatting success; then an independent human authors or reimplements and reviews any upstream candidate.
