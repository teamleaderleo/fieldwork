# Tests and receipts — Unit 02: BusyBox-safe relocatable launchers

## In simple words

Two prior focused runs establish the defect and the synchronized source correction on base `1da26a`. A current-head carrier rebases the same exact replacement counts onto public uv `79bbface`, runs formatting, affected-crate compilation, the native shebang test, and the GNU/BusyBox matrix, and retains the complete modified files for clean publication.

## Identity

- Original executed base: `1da26a68629be6ae5fd7f924a7d49ff54763a7df`
- Current public base: `79bbface771210df216b738e9bdc7df95e5a9e6b`
- Prior candidate carrier head: `0aad1cc1fc9aa03fc5705da44112671101e20624`
- Current execution carrier head: `1e1a66d96b4ef827ef470848cd19c504a6bdd739`
- Current clean candidate head: recorded in packet `README.md` after materialization
- Test dates: 2026-07-31 and 2026-08-01
- Environments: GitHub-hosted Ubuntu 24.04; `alpine:3.22` container with BusyBox 1.37.0

## Claim-to-evidence matrix

| Claim | Evidence class | Test or source | Result | Coverage limit |
| --- | --- | --- | --- | --- |
| BusyBox baseline emits `realpath: --` while launcher succeeds | integration-executed | workflow [`30625826268`](https://github.com/teamleaderleo/uv/actions/runs/30625826268), job `91140735058` | pass, 6/6 baseline cases | Alpine 3.22 BusyBox only |
| Delimiter-free fragment preserves tested GNU behavior | integration-executed | workflow `30625826268` | pass, 6/6 candidate cases | GNU environment on Ubuntu only |
| Delimiter-free fragment is quiet on BusyBox | integration-executed | workflow `30625826268` | pass, 6/6 candidate cases | six invocation forms |
| Synchronized patch changes exactly three source files | target-executed | workflow [`30650924197`](https://github.com/teamleaderleo/uv/actions/runs/30650924197), job `91223680476` | pass | base `1da26a` |
| Affected crates compile with the synchronized patch | target-executed | `cargo check -p uv-install-wheel -p uv-virtualenv -p uv` in workflow `30650924197` | pass | compile gate, not full test suite |
| Current public source retains all three owners | source-read | public base `79bbface` code links in `DEEP_DIVE.md` | confirmed | source observation |
| Current-head candidate passes declared gates | target-executed | workflow [`30674680508`](https://github.com/teamleaderleo/uv/actions/runs/30674680508), job `91299352922` | pending at initial packet write; final status recorded below | exact carrier head `1e1a66d` |

## Baseline characterization

### Command or workflow

```text
/bin/sh scripts/fieldwork/relocatable-launcher-portability.sh gnu
docker run --rm --volume "$PWD:/source:ro" alpine:3.22 \
  /bin/sh /source/scripts/fieldwork/relocatable-launcher-portability.sh busybox
```

### Assertions

- exit status 0;
- resolved executable is the sibling fake `python`;
- argument `probe` arrives;
- GNU stderr is empty;
- BusyBox current stderr contains `realpath: --`;
- BusyBox candidate stderr is empty.

### Result

- status: passed;
- test count: 24/24;
- workflow/job: `30625826268` / `91140735058`;
- observed behavior: GNU current 6/6, GNU candidate 6/6, BusyBox current 6/6 with expected diagnostic, BusyBox candidate 6/6 clean.

## Candidate-focused tests

### Synchronized three-owner candidate on original base

- Exact source carrier head: `0aad1cc1fc9aa03fc5705da44112671101e20624`
- Workflow/job: `30650924197` / `91223680476`
- Commands and checks:
  - exact-head carrier fence;
  - exact generated changed-path fence;
  - `git diff --check`;
  - `cargo check -p uv-install-wheel -p uv-virtualenv -p uv`;
  - GNU matrix;
  - Alpine 3.22 BusyBox matrix;
  - result marker verification.
- Result: passed.
- Artifact: `8801371654`, digest `sha256:ff4221a734d356250aa38ed97d0b194635f6ef3847a24d0a652ec4b3912bbb97`.
- Coverage limit: old base `1da26a`; no complete repository suite.

### Current-head materialization

- Exact carrier head: `1e1a66d96b4ef827ef470848cd19c504a6bdd739`
- Workflow/job: `30674680508` / `91299352922`
- Intended commands:
  - `cargo fmt --all --check`;
  - `cargo check -p uv-install-wheel -p uv-virtualenv -p uv`;
  - `cargo test -p uv-install-wheel test_shebang`;
  - GNU six-case baseline/candidate matrix;
  - Alpine 3.22 BusyBox six-case baseline/candidate matrix;
  - exact three-source-file and 5/7 replacement fences.
- Final result: see the `Current-head final receipt` section added after completion.

## Ordinary repository gates

| Gate | Exact command or workflow | Result | Notes |
| --- | --- | --- | --- |
| format | `cargo fmt --all --check` in current carrier | pending initial write | current public base candidate |
| lint | full project clippy | not run | larger than focused carrier |
| typecheck or compile | `cargo check -p uv-install-wheel -p uv-virtualenv -p uv` | passed on prior candidate; current run pending initial write | affected crates |
| focused package tests | `cargo test -p uv-install-wheel test_shebang` | pending initial write | native generated-shebang assertion |
| complete target-declared suite | ordinary `CI` workflow on carrier | queued/pending; source diff carrier includes unrelated upstream history against stale fork main | never treat carrier-wide result as a clean source-branch diff |
| build or generated output | exact shebang snapshot changed by replacement | prepared and fenced | no separate generated file |
| platform matrix | GNU and Alpine BusyBox | prior pass; current run pending initial write | macOS/BSD absent |

## Reversing controls

- baseline BusyBox emits the diagnostic and candidate BusyBox does not;
- GNU current and candidate both execute cleanly;
- external symlink selects the sibling interpreter in both candidates;
- `./-tool`, spaces, relative, PATH, and absolute cases retain status and argument delivery.

## Soak, leak, and cleanup controls

- iterations: one execution per variant × case × platform in each focused run;
- resources observed: temporary files and child processes only;
- cleanup: shell trap removes the unique temporary root;
- interruption behavior: EXIT, HUP, INT, and TERM traps;
- immediate rerun result: separate prior source-candidate run repeated the same 24-case result.

## Setup and harness failures

| Attempt | Failure | Classification | Product claim affected? | Repair or stop |
| --- | --- | --- | --- | --- |
| broad CI `30625826344` on PR #2 | generated documentation/OpenAPI check failed outside the two evidence files; run later remained queued in connector state | setup/repository gate | no for launcher matrix; yes for whole-repository green claim | retain focused result and avoid broad-green claim |
| first PR #5 base | fork `main` was at `1da26a`, making a 244-file carrier comparison | setup | no | retargeted/fenced against public source `79bbface`; recorded in PR body |
| first custom-trigger attempt | workflow was absent until PR close/reopen event | runner/trigger | no | closed and reopened PR #5; current workflow `30674680508` queued |

## Checks prepared but not executed

- macOS/BSD execution of the corrected fragment — human or CI platform required;
- a supported bare option-like `$0` invocation — reproduction unavailable;
- complete project suite on a source-only PR against a synchronized fork base — fork default branch requires update or a dedicated base branch.

## Platform and integration gaps

- macOS 13+ native utilities;
- FreeBSD and other BSD-family utilities;
- persisted old launcher recognition after uv upgrades;
- real package installation on Alpine at current source head beyond the controlled shell fixture.

## Cleanup receipt

- Temporary workflows removed from canonical source head: final source branch must show `yes` in `README.md`;
- Publisher or execution-only files removed: final source branch must show `yes`;
- Generated residue checked: exact changed-file fence;
- Immediate rerun performed: prior candidate repeated the matrix; current run recorded below;
- Remaining temporary branches or PRs: `teamleaderleo/uv#2`, `#3`, and `#5` are evidence carriers until final closeout.

## Current-head final receipt

Pending at initial creation. This section must be updated with the exact workflow conclusion, artifact, clean source head, and source-only changed-file fence before the packet can leave `HOLD`.

## Current test judgment

`HOLD`

Reason: prior behavior and compile evidence are strong, while current-head execution and clean-branch publication are still being completed. Public submission also requires independent human ownership under uv's AI policy.

Clearing condition: current workflow succeeds, exact tested blobs become one clean source-only commit, and a human reviews the source and packet.
