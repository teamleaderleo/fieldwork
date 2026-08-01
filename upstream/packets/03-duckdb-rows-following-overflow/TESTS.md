# Tests and receipts — unit 03 ROWS FOLLOWING overflow

## In simple words

The baseline defect was executed with DuckDB's native SQLLogicTest runner and produced the wrong whole-partition frame. The one-line repair passed the same extreme query and ordinary controls on the historical source. Current-main Debug execution also compiles and passes the focused regression.

The first current-main carrier used a bare directory as the test filter and failed before producing a useful failure receipt. A corrected wildcard run selected the window tests and retained its output. The candidate test passed in three seconds. Three unrelated `.test_slow` cases then exceeded DuckDB's 600-second Debug batch timeout, and the sequential suite reached the 60-minute job limit. DuckDB's current pull-request workflow runs slow tests only when a `.test_slow` file changes. Unit 03 adds a regular `.test`, so the current successor runs every regular window SQLLogicTest and records the excluded slow-test inventory separately.

## Identity

- Exact current upstream base: `63094a6f725af5045113dda74e291c7d604f6a88`
- Exact canonical source head: `63094a6f725af5045113dda74e291c7d604f6a88` — unchanged clean base while publication remains gated
- Initial current-main carrier head: `bf703f57b15555c2db68520b1f4165e23ca737ae`
- Wildcard diagnostic carrier head: `10347a116cab489b9bd4d08d612f1c1095e6d706`
- Current ordinary-gate carrier head: `243ff3929f34fa904bb96699005ac6848aab7f38`
- Current successor run/job: `30692119355` / `91348557949`
- Test date: `2026-07-31` through `2026-08-01`
- Environment: GitHub Actions Ubuntu 24.04; CMake/Ninja Debug; DuckDB native parallel test wrapper

## Claim-to-evidence matrix

| Claim | Evidence class | Test or source | Result | Coverage limit |
| --- | --- | --- | --- | --- |
| Extreme FOLLOWING returns whole-partition results on baseline | `target-executed` | Fieldwork run [`30580996108`](https://github.com/teamleaderleo/fieldwork/actions/runs/30580996108), report [`735a2e184bc6039c64a341449d01977f4091311e`](https://github.com/teamleaderleo/fieldwork/commit/735a2e184bc6039c64a341449d01977f4091311e) | reproduced | historical source `de477da...` |
| Ordinary `1 FOLLOWING` remains correct on baseline | `target-executed` | same Fieldwork run | pass | one ordinary control |
| Partition-end repair fixes the focused extreme result | `target-executed` | historical owned run [`30595242656`](https://github.com/teamleaderleo/duckdb/actions/runs/30595242656) | pass | execution-applied patch on historical source |
| Regression reverses on source without repair | `target-executed` | Main run [`30595243144`](https://github.com/teamleaderleo/duckdb/actions/runs/30595243144), Relassert job `91057026663` | intended regression failed; 252 smoke tests passed | synthetic carrier merge without production repair |
| Current-main candidate compiles | `target-executed` | runs `30674257475` and `30689967043` | pass | materialized runner worktrees |
| Current-main focused regression passes | `target-executed` | run `30689967043`, job `91342817226` | `1 passed, 0 skipped in 3s` | focused SQLLogicTest file |
| Bare directory is an unsuitable suite filter | `target-executed` | run `30674257475`, then accepted wildcard in `30689967043` | harness invocation classified | original run retained no artifact |
| Full wildcard includes slow tests outside the ordinary PR path | `target-executed` | run `30689967043`, artifact `8815977625` | three unrelated slow tests exceeded 600 seconds; job timed out | Debug, sequential job budget |
| Ordinary regular window suite passes | `target-test-executing` | run `30692119355`, command `test/sql/window/*.test` | queued at this packet revision | Ubuntu Debug |
| Formatting passes | `target-test-executing` | successor `make format-check` | pending behind regular suite | Ubuntu only |
| Clean two-file source head exists | `target-test-executing` | successor publisher | pending behind all gates | canonical branch still clean base |

## Baseline characterization

### Command or workflow

```text
DuckDB native SQLLogicTest runner through Fieldwork workflow run 30580996108
```

### Assertions

- `INT64_MAX FOLLOWING` yields zero rows in each frame.
- ordinary `1 FOLLOWING` yields the next row and an empty final frame.

### Result

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
- Limit: patch applied during execution; PR head remained a carrier

### Historical baseline reversal through Main CI

- Exact source head: synthetic merge `914d14b862136fab1b7b4fc8c6d68bf3e55789ab`
- Command: `make smoke T="--changed-tests=/home/runner/work/_temp/changed_tests.txt"`
- Result: 252 passed, one failed; the regression produced the exact baseline whole-partition output
- Classification: expected baseline product failure caused by carrier topology

### Initial current-main run

- Upstream checkout: `63094a6f725af5045113dda74e291c7d604f6a88`
- Carrier head: `bf703f57b15555c2db68520b1f4165e23ca737ae`
- Workflow/job: `30674257475` / `91298115859`
- Materialization, configure, build, focused regression: pass
- Ordinary command: `./build/fieldwork/test/run 'test/sql/window'`
- Result: failed filter/gate invocation; formatting and publisher skipped
- Retained artifact: none
- Successor action: replace bare directory with an explicit wildcard and retain all output

### Wildcard diagnostic run

- Carrier head: `10347a116cab489b9bd4d08d612f1c1095e6d706`
- Workflow/job: [`30689967043`](https://github.com/teamleaderleo/duckdb/actions/runs/30689967043) / `91342817226`
- Build: `cmake --build build/fieldwork --target unittest --parallel 2` — pass
- Focused command: `./build/fieldwork/test/run 'test/sql/window/test_rows_following_overflow.test'`
- Focused result: `1 passed, 0 skipped in 3s`; wrapper used three workers
- Wildcard command: `./build/fieldwork/test/run 'test/sql/window/*'`
- Wildcard result: accepted and executed; job reached the 60-minute limit
- Artifact: `8815977625`
- Digest: `sha256:69ceb3c4720921b31b7b6c3ee03c61df4319fadc19538120cf0b1f5be6bd7642`
- Retained files: exact product patch, focused log, changed-file receipt, partial window-suite log
- Slow timeouts recorded:
  - `test/sql/window/window_partition_paging.test_slow`
  - `test/sql/window/test_fill.test_slow`
  - `test/sql/window/test_quantile_window.test_slow`
- Timeout detail: each reported the wrapper's `600s` batch timeout after retries; the job was cancelled at its 60-minute bound
- Classification: unrelated slow-test capacity in a Debug bounded carrier; the product candidate's focused test remained green

### Current ordinary pull-request gate

- Carrier head: `243ff3929f34fa904bb96699005ac6848aab7f38`
- Workflow/job: [`30692119355`](https://github.com/teamleaderleo/duckdb/actions/runs/30692119355) / `91348557949`
- Build: Debug native runner with four build workers
- Focused command: exact regression file
- Ordinary command: `./build/fieldwork/test/run 'test/sql/window/*.test'`
- Scope rationale: DuckDB's current Main workflow sets `run_slow_tests=true` only when `.test_slow` files change or on `main`; unit 03 adds a regular `.test`
- Additional receipt controls:
  - exact changed-file list includes production source plus the untracked regression;
  - exact expected two-file list is diffed against the observed list;
  - all excluded `.test_slow` paths are recorded;
  - candidate patch, regression file, focused log, suite log, and formatting log are retained with `if: always()`
- Status at this packet revision: queued

## Ordinary repository gates

| Gate | Exact command or workflow | Result | Notes |
| --- | --- | --- | --- |
| compile | current Debug `unittest` build | passed twice; successor pending | Ubuntu 24.04 |
| focused regression | exact `test_rows_following_overflow.test` | historical pass; current-main pass twice | extreme, ordinary, partition controls |
| ordinary affected suite | every regular `test/sql/window/*.test` | executing in `30692119355` | matches current PR slow-test policy |
| slow affected suite | `.test_slow` inventory | unchanged and excluded from ordinary PR gate | three slow Debug cases exceeded 600s in diagnostic run |
| format | `make format-check` | pending in successor | historical carrier format passed |
| complete target-declared suite | `make unit` / `make allunit` | unexecuted | outside bounded carrier |
| release/relassert | project builds on final clean source head | unexecuted | clean candidate head pending |
| platform matrix | project CI matrix | unexecuted | human-authorship stop remains |

## Reversing controls

- The regression fails on unmodified source and passes when the repair is applied.
- Ordinary `1 FOLLOWING` passes on baseline and repaired execution.
- Multi-partition extreme offsets verify each frame uses its own partition end.
- The focused test passed on current main before and after the suite-invocation correction.

## Setup and harness failures

| Attempt | Failure | Classification | Product claim affected? | Repair or stop |
| --- | --- | --- | --- | --- |
| historical early carrier linked from `#240` | initial arrangement lacked an immutable clean-source receipt | setup | no | rebuilt evidence on exact source and retained PR `#253` |
| Main run `30595243144` | regression failed because patch artifact was absent from synthetic merge | carrier topology | no; supplied baseline reversal | replaced with materialized candidate workflow |
| run `30674257475` | bare directory filter failed without useful retained output | invocation | no | explicit wildcard plus always-uploaded receipts |
| run `30689967043` | full wildcard selected `.test_slow` cases; three exceeded 600 seconds and job reached 60 minutes | bounded Debug harness capacity | no focused-candidate failure | align ordinary gate with DuckDB PR slow-test policy |

## Checks prepared but unexecuted

- Full `make unit`.
- `make allunit`.
- Release and relassert complete suites.
- macOS and Windows matrices.

## Cleanup receipt

- Canonical source branch remains the exact public base while gates execute.
- Execution-only workflow and carrier files remain confined to `exec/unit-03-window-overflow-materialize` and PR `#17`.
- Historical carrier PR `#8` remains for receipt transfer and retirement.
- Accidental Fieldwork branch `dummy-no` remains a separate cleanup item.
- No public upstream interaction occurred.

## Current test judgment

`EXECUTE / HOLD`

The focused correction is green on current main. The original red suite result is now classified as a bare-directory invocation issue. The corrected full wildcard established unrelated slow-test capacity limits and retained exact receipts. The current successor runs the ordinary regular window suite that DuckDB's pull-request policy calls for when a regular `.test` changes.

Technical clearing condition: successor `30692119355` passes materialization, Debug build, focused regression, every regular window SQLLogicTest, formatting, exact two-file fencing, and clean publication. Public clearing condition: an independent human derives, authors or reimplements, and reviews an eligible candidate, followed by explicit contact authority.
