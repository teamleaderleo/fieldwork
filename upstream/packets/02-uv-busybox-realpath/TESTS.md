# Tests and receipts — Unit 02: BusyBox-safe relocatable launchers

## In simple words

Two prior focused runs establish the defect and the synchronized source correction on base `1da26a`. Current-head execution at public uv `79bbface` has also produced the exact complete three-file candidate and replacement fence. Its first formatting gate stopped on a missing runner component; a repaired carrier installs `rustfmt`, runs the remaining gates, and publishes one clean source-only commit after success.

## Identity

- Original executed base: `1da26a68629be6ae5fd7f924a7d49ff54763a7df`
- Current public base: `79bbface771210df216b738e9bdc7df95e5a9e6b`
- Prior candidate carrier head: `0aad1cc1fc9aa03fc5705da44112671101e20624`
- First current-head carrier head: `1e1a66d96b4ef827ef470848cd19c504a6bdd739`
- Repaired current-head carrier head: `460a974f086fbab6347122968e7974915633b1fb`
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
| Current-head candidate generation is exact | target-executed | workflow [`30674680508`](https://github.com/teamleaderleo/uv/actions/runs/30674680508), job `91299352922` | pass through generation fence | later gates skipped after setup failure |
| Current-head focused gates and clean publication pass | target-executed | workflow [`30676398821`](https://github.com/teamleaderleo/uv/actions/runs/30676398821), job `91304457291` | queued at this packet revision | exact carrier head `460a974` |

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

### First current-head materialization

- Exact carrier head: `1e1a66d96b4ef827ef470848cd19c504a6bdd739`
- Workflow/job: `30674680508` / `91299352922`
- Passed:
  - exact carrier ancestry and changed-file fence;
  - Python and shell harness syntax checks;
  - exact current-source replacement counts;
  - `git diff --check`;
  - exact three-source-file fence;
  - complete source artifact upload.
- Setup failure: `cargo fmt --all --check` could not start because Rust 1.97.1 lacked the `rustfmt` component.
- Skipped after setup failure: affected-crate compile, native shebang test, GNU matrix, BusyBox matrix, result-marker check.
- Artifact: `8810498589`, digest `sha256:78fb757cc283506262b7d39e4cdafa5760b0656ba9560aa42886a11a68fa8272`.
- Exact artifact source blobs:
  - wheel: `1d77576b32df7f8711b29012cf380b178d87e362`;
  - virtualenv: `c04625aa40cff1fe985195fb2e0ac8ba497be215`;
  - project-run: `fa3419e21dd494a4473874f8e284d83d061c331d`.
- Artifact patch fence: five `realpath --`, seven `dirname --`, exactly three source files.

### Repaired current-head materialization and publication

- Exact carrier head: `460a974f086fbab6347122968e7974915633b1fb`
- Workflow/job: `30676398821` / `91304457291`
- Declared commands:
  - install `rustfmt`;
  - `cargo fmt --all --check`;
  - `cargo check -p uv-install-wheel -p uv-virtualenv -p uv`;
  - `cargo test -p uv-install-wheel test_shebang`;
  - GNU six-case baseline/candidate matrix;
  - Alpine 3.22 BusyBox six-case baseline/candidate matrix;
  - exact three-source-file and 5/7 replacement fences;
  - construct one Git tree from parent `79bbface` containing only the three candidate files;
  - force-push the resulting one-commit source head to `upstream/02-busybox-realpath`.
- Current result: queued at this packet revision.

## Ordinary repository gates

| Gate | Exact command or workflow | Result | Notes |
| --- | --- | --- | --- |
| format | `cargo fmt --all --check` | first attempt blocked by missing component; repaired attempt queued | source result still pending |
| lint | full project clippy | not run | larger than focused carrier |
| typecheck or compile | `cargo check -p uv-install-wheel -p uv-virtualenv -p uv` | passed on prior candidate; current attempt queued | affected crates |
| focused package tests | `cargo test -p uv-install-wheel test_shebang` | current attempt queued | native generated-shebang assertion |
| complete target-declared suite | ordinary `CI` workflow on carrier | pending; carrier includes unrelated upstream history against stale fork main | never treat carrier-wide result as a clean source-branch diff |
| build or generated output | exact shebang snapshot changed by replacement | prepared and fenced | no separate generated file |
| platform matrix | GNU and Alpine BusyBox | prior pass; current attempt queued | macOS/BSD absent |

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
| broad CI `30625826344` on PR #2 | generated documentation/OpenAPI check failed outside the two evidence files | setup/repository gate | no for launcher matrix; yes for whole-repository green claim | retain focused result and avoid broad-green claim |
| first PR #5 base | fork `main` was at `1da26a`, making a 244-file carrier comparison | setup | no | carrier fenced against public source `79bbface`; never use carrier-wide diff as source diff |
| first custom-trigger attempt | workflow was absent until PR close/reopen event | runner/trigger | no | closed and reopened PR #5 |
| current-head workflow `30674680508` | `rustfmt` component absent from runner toolchain | setup | no formatting conclusion; no source claim reversal | add `rustup component add rustfmt`, rerun as `30676398821` |
| temporary wheel object `3ddcd43820b41d6752efa1ebd3f200848aee73bc` | manual reconstruction included one unrelated formatting drift | materialization exactness | no; object rejected before clean branch use | reconstruct from commit-pinned chunks, verify base hash `9b23b523…` and target hash `1d77576b…`; artifact later confirmed exact blob |
| Fieldwork carrier PR #453 | duplicated the uv materializer and remained queued | redundant execution path | no | closed without merge after artifact `8810498589` existed |

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

- Temporary workflows removed from canonical source head: enforced by source-tree construction from public base;
- Publisher or execution-only files removed: enforced by exact three-path alternate-index commit;
- Generated residue checked: exact changed-file fence;
- Immediate rerun performed: prior candidate repeated the matrix; repaired current run recorded below;
- Remaining temporary branches or PRs: `teamleaderleo/uv#2`, `#3`, and `#5` remain evidence carriers until final closeout; Fieldwork PR #453 is closed.

## Current-head final receipt

Pending completion of workflow `30676398821`. Update this section with:

- exact workflow conclusion and step results;
- artifact ID and digest;
- exact clean source tree and commit;
- complete compare stats and three changed files;
- commit-pinned code and test links.

## Current test judgment

`HOLD`

Reason: current source bytes and exact patch fence are established, while the repaired formatting, compile, native test, matrix, and clean publication run is queued. Public submission also requires independent human ownership under uv's AI policy.

Clearing condition: repaired workflow succeeds, the exact tested blobs become one clean source-only commit, and a human reviews the source and packet.
