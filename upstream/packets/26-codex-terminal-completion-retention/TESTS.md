# Test and execution ledger

## Current status

Disposition: **REPAIR**

The strongest historical source revision passed the complete requested gate. The latest retained source passed its nine exact controls and then failed the broader library step. The current unit-owned restack has no run yet.

## Current source revision

- Public base: `670f69416bf91c5dfd8b58669e78050b584ff053`
- Source branch: `fieldwork/26-terminal-completion-retention-source`
- Source head: `a020d7bd3e7f6886c3fbc21d75b3110586df08f5`
- Source tree: `9a067c244d464e863a7b50978826ac9930df680b`
- Diff: four files, 281 additions, 52 deletions
- Current-head execution: **pending**

## Exact focused behaviors

The current source contains focused controls for these contracts:

### Process completion

- `completed_item_includes_output_emitted_before_subscription`
- `reconcile_transcript_replaces_partial_stream_with_authoritative_output`

### Producer retention and broadcast behavior

- `local_output_task_retains_stdout_before_best_effort_broadcast`
- `local_output_task_retains_invalid_utf8_when_broadcast_lags`
- late stdout delivery across a multi-second subscriber delay
- late stderr delivery across a multi-second subscriber delay
- lagged receiver recovery from retained output
- bounded retention behavior
- hard-termination promptness after receiver closure

### UTF-8 helpers present in the touched test file

- `split_valid_utf8_prefix_respects_max_bytes_for_ascii`
- `split_valid_utf8_prefix_avoids_splitting_utf8_codepoints`
- `split_valid_utf8_prefix_makes_progress_on_invalid_utf8`
- `split_valid_utf8_prefix_consumes_all_valid_bytes_before_invalid_utf8`
- `split_invalid_utf8_advances_without_shifting_remaining_bytes`

The carriers describe the terminal-retention gate as nine exact controls. The packet preserves that carrier-defined count and names only the controls confirmed from the source files and retained PR records.

## Execution table

| Record | Source/base | Tests and result | Classification |
|---|---|---|---|
| [Codex PR #6](https://github.com/teamleaderleo/codex/pull/6) | reviewed implementation head `f0265ec...`; source-only handoff `35a3d17475405cf8acb8fd9e83e8734851bc91ae` | formatting/fix/diff checks pass; new pre-subscription and reconciliation tests pass; 99 tests executed, 95 pass; four sandbox/network SIGABRT cases | Useful prototype evidence; four broad failures appear baseline/environment-like; source packaging later superseded |
| [Codex PR #49](https://github.com/teamleaderleo/codex/pull/49) | base `b545c940...`; source head `7db66fe3f235df77c36a9db521677e23379bcac5` | source-only restack and run `30546914788`; review requested target execution | Source publication evidence; later carriers supersede |
| [Codex PR #50](https://github.com/teamleaderleo/codex/pull/50) | shared exact-name/count carrier | source guards and execution flow; runner setup stopped before accepted product result | Carrier/setup evidence only |
| [Codex PR #53](https://github.com/teamleaderleo/codex/pull/53) | base `97576b1794872e342450ebd577123e052ab57626`; source `7db66fe3f235df77c36a9db521677e23379bcac5`; carrier `c4e0de2e54d804d1054afb90c30b7150a774151c` | runs `30579629635`, `30579942527`, `30580891167`, `30582012412`; failures included expected conflict setup, missing `just`, shallow history, and missing `uv` during `just fmt` | Setup failures; zero product evidence |
| [Codex PR #70](https://github.com/teamleaderleo/codex/pull/70) | base `6a6d95...`; current carrier head `220aaf936ff7445908d02ddd4df409bf4a7a9b84` | specialized four-file source/carrier path; no durable final accepted receipt in PR record | Superseded carrier evidence |
| [Fieldwork PR #268](https://github.com/teamleaderleo/fieldwork/pull/268), run [30587866332](https://github.com/teamleaderleo/fieldwork/actions/runs/30587866332) | source head `8c7ea38419d790032db459816980e6b4dd38f574`; tree `563f90f55c0ebd9454171d24697d796cba1388d4` | nine exact controls pass; full `codex-core` library gate pass; integration-target compile pass | **Authoritative historical pass** |
| [Codex PR #86](https://github.com/teamleaderleo/codex/pull/86) | base `a192652...`; carrier head `4e12c3a...` | materialized authoritative artifact and drift guard; no later durable full receipt | Materialization lineage |
| [Codex PR #91](https://github.com/teamleaderleo/codex/pull/91) | base `bd28d2519910b014b6898e314a6c97fceec8ddad`; source head `aabb0249e56e42fe21b1204b305e90e0296d5ee6` | four-file source publication; target execution requested | Source lineage |
| [Codex PR #93](https://github.com/teamleaderleo/codex/pull/93) | base `4642370542739d5dd080b0c87a9de06a6435d3db`; head `7f15307fd2c157d8a139310d2e8243f3f2b391a4` | exact four-file repair; 294 additions, 57 deletions | Source lineage |
| [Codex PR #94](https://github.com/teamleaderleo/codex/pull/94) | base `464237...`; carrier `2edcead676e367ba630f452c7c6e0d26b9c76e44` | run `30635705417` failed source-branch consistency guard before product tests | Setup failure; zero product evidence |
| [Codex PR #125](https://github.com/teamleaderleo/codex/pull/125) | base `3d1d26915a303c3b4765828f973f5464f8c28c5c`; live source `ee605985012dc1b768f03f6b450db16dd5c0467e` | local receipt in PR body: `just fmt`; `cargo fmt --all -- --check` | Formatting receipt; target execution supplied by PR #126 |
| [Codex PR #126](https://github.com/teamleaderleo/codex/pull/126), run [30651607704](https://github.com/teamleaderleo/codex/actions/runs/30651607704), job [91225943920](https://github.com/teamleaderleo/codex/actions/runs/30651607704/job/91225943920) | carrier `4c6352df86602b35e3ec9547530295a8cd9752c0`; guarded source `ee605985012dc1b768f03f6b450db16dd5c0467e` | setup pass; source guard pass; baseline build pass; nine exact controls pass; broader focused `codex-core` gate fail; integration compile not reached | Current retained-head focused pass; broader failure unclassified |
| Unit 26 clean restack | base `670f69416bf91c5dfd8b58669e78050b584ff053`; head `a020d7bd3e7f6886c3fbc21d75b3110586df08f5` | no execution yet | Current blocker |

## Authoritative artifact receipt

From Fieldwork PR #268:

- run: [`30587866332`](https://github.com/teamleaderleo/fieldwork/actions/runs/30587866332)
- artifact id: `8777460316`
- artifact digest: `sha256:9c6c4f6741ee2514e995849ca2bed9caf0f80b80fdbb3a9ea31565df3ebda2dd`
- executed source head: `8c7ea38419d790032db459816980e6b4dd38f574`
- executed source tree: `563f90f55c0ebd9454171d24697d796cba1388d4`

## Latest broader-gate failure

Run `30651607704` reached real product execution. The retained step record confirms the nine exact controls passed and the broader focused library step failed. The connector did not expose the complete failure line in its retained response. This packet therefore avoids guessing whether the cause belongs to source, baseline, runner, or carrier.

Required continuation action:

1. rerun on `a020d7bd3e7f6886c3fbc21d75b3110586df08f5` with complete logs retained as an artifact;
2. use paired baseline/source target directories;
3. preserve command lines, exit codes, failing test names, and stderr;
4. compare any failing test against the public-base checkout;
5. classify the result explicitly.

## Current-head command plan

Use the current Codex repository instructions and a clean carrier pinned to both revisions.

```text
base:   670f69416bf91c5dfd8b58669e78050b584ff053
source: a020d7bd3e7f6886c3fbc21d75b3110586df08f5
```

Run, in order:

```bash
just fmt
cargo fmt --all -- --check
# nine exact terminal-retention controls, with exact names pinned in the carrier
cargo test -p codex-core --lib
# compile the relevant integration target without widening source scope
```

The carrier should keep baseline and source build directories separate, verify the exact four-file source fence, and publish a machine-readable receipt containing SHAs, commands, exit codes, test counts, and artifact digest.

## Exit criteria

Unit 26 can move beyond REPAIR when:

- the current unit-owned source head passes the nine exact controls;
- full `codex-core` library testing passes or every shared failure is baseline-classified with receipts;
- the integration target compiles;
- an independent reviewer accepts the four-file diff and risk map;
- source and packet heads remain exact and published;
- public-upstream contact remains invitation-gated.
