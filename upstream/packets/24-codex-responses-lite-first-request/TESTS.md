# Tests and receipts — unit 24 Responses Lite first request after prewarm

## In simple words

The retained three-file source has one executed historical receipt and one current-source CI attempt. Historical execution proved the exact file fence, both isolated client state controls, and the full-agent request assertion with a larger Tokio worker stack. The same full-agent assertion overflowed the default worker stack, which is recorded as a runner/runtime discriminator.

The clean current source at `2c3f21d38056d2d77215cd9dce820a680d11cfe8` has entered ordinary repository CI through draft PR [`teamleaderleo/codex#130`](https://github.com/teamleaderleo/codex/pull/130). Its inspected `repo-checks` failure comes from a stale manifest-feature exception for `codex-rs/code-mode/Cargo.toml`, outside this unit's three-file fence. Several current jobs remain red or incomplete and need classification. The three exact current-head controls remain unexecuted.

## Identity

- Exact public upstream base: `670f69416bf91c5dfd8b58669e78050b584ff053`
- Exact current candidate head: `2c3f21d38056d2d77215cd9dce820a680d11cfe8`
- Exact historical source base: `e6cfd40c3f444aadd6017c9eeab01db70f48961a`
- Exact historical source head: `e520da008366cd720ef58fa0b489efc0a2867e97`
- Exact historical execution carrier head: `40a56eefce26ea647a65779faeb783d65a84a49a`
- Historical test date: `2026-07-30`
- Current CI date: `2026-08-01`
- Environment and platform: GitHub Actions; historical exact controls on Linux; current blocking CI spans Linux, macOS, and Windows

## Claim-to-evidence matrix

| Claim | Evidence class | Test or source | Result | Coverage limit |
| --- | --- | --- | --- | --- |
| Source candidate changes exactly three intended files | target-executed | [`run 30584165709`, job `91011486628`](https://github.com/teamleaderleo/codex/actions/runs/30584165709/job/91011486628), `FIELDWORK_LITE_SOURCE_FENCE=3/3` | pass | historical source `e520da...` |
| First generated Lite request is full and later continuation uses the generated response | target-executed | `responses_lite_reuses_generated_response_after_full_first_turn` in the same job | pass | historical source `e520da...` |
| Failed first generation retries the same full request | target-executed | `responses_lite_retries_full_first_turn_after_failed_generation` in the same job | pass | historical source `e520da...` |
| Full agent path emits the complete current request after prewarm | target-executed | `websocket_first_responses_lite_turn_sends_exact_current_request_after_startup_prewarm` in the same job | default stack exit `101`; 16 MiB exit `0` | stack overflow limits ordinary-runner evidence |
| Current source is a clean direct child of current public base | source-read | [`670f694...2c3f21d`](https://github.com/teamleaderleo/codex/compare/670f69416bf91c5dfd8b58669e78050b584ff053...2c3f21d38056d2d77215cd9dce820a680d11cfe8) | one commit; three files; `+301/-1` | execution renewal pending |
| Current ordinary CI includes a repository-wide manifest failure outside the unit fence | full-gate | [`run 30674311295`, job `91298276097`](https://github.com/teamleaderleo/codex/actions/runs/30674311295/job/91298276097) | fail in `verify_cargo_workspace_manifests.py` for `codex-rs/code-mode/Cargo.toml` exception | other current red jobs need separate classification |

## Baseline characterization

### Source and fixture

The baseline path at `670f694...` retains the generic response-chain preparation state and no unit-specific control that severs the untraced warmup response before the first generated Lite request. The candidate tests observe outbound request JSON through the repository WebSocket fixture.

### Assertions

- warmup uses `generate=false`;
- warmup input starts with a nonempty `additional_tools` manifest;
- first generated request omits `previous_response_id`;
- first generated input carries the complete current prefix and user input;
- second generated turn uses `previous_response_id = resp-1` and only the incremental suffix;
- retry after a failed first generation omits `previous_response_id` and repeats the complete request.

### Result

- status: source-characterized; candidate tests supply the behavioral discriminator
- test count: three target-native tests in the candidate
- baseline failure-on-old-head: not executed as a standalone current-head negative control
- coverage limit: current public base was inspected; exact current baseline/candidate A/B execution remains open

## Candidate-focused tests

### Exact source fence

- Exact source head: `e520da008366cd720ef58fa0b489efc0a2867e97`
- Workflow: [`30584165709`](https://github.com/teamleaderleo/codex/actions/runs/30584165709)
- Assertion: changed files equal:
  - `codex-rs/core/src/client.rs`
  - `codex-rs/core/tests/suite/agent_websocket.rs`
  - `codex-rs/core/tests/suite/client_websockets.rs`
- Result: `FIELDWORK_LITE_SOURCE_FENCE=3/3`
- Coverage limit: historical exact source

### Focused client controls

- Exact source head: `e520da008366cd720ef58fa0b489efc0a2867e97`
- Command family:

```text
cargo test -p codex-core --test all --locked <resolved-full-test-name> -- --exact --nocapture
```

- Tests:
  - `responses_lite_reuses_generated_response_after_full_first_turn`
  - `responses_lite_retries_full_first_turn_after_failed_generation`
- Result: each test passed; aggregate marker `FIELDWORK_LITE_CLIENT_EXACT=2/2`
- Coverage limit: local WebSocket fixture on historical source

### Full-agent request identity

- Exact source head: `e520da008366cd720ef58fa0b489efc0a2867e97`
- Test: `websocket_first_responses_lite_turn_sends_exact_current_request_after_startup_prewarm`
- Result: default worker stack aborted with stack overflow, exit `101`; `RUST_MIN_STACK=16777216` passed, exit `0`; aggregate marker `FIELDWORK_LITE_AGENT=default:101;large:0`
- Failure classification: runner/runtime stack pressure in the broader agent path; focused client controls passed under the ordinary runner
- Coverage limit: ordinary default-stack full-agent acceptance remains absent

### Current clean-head CI

- Exact source head: `2c3f21d38056d2d77215cd9dce820a680d11cfe8`
- Draft PR: [`teamleaderleo/codex#130`](https://github.com/teamleaderleo/codex/pull/130)
- Blocking run: [`30674311295`](https://github.com/teamleaderleo/codex/actions/runs/30674311295)
- Inspected results:
  - `cargo-deny`: pass
  - `codespell`: pass
  - blob size policy: pass
  - changed-area detection: pass
  - repository manifest check: fail on `codex-rs/code-mode/Cargo.toml` stale exception, outside this unit fence
  - several Bazel, SDK, and Windows jobs: red or incomplete at inspection; exact cause unclassified here
- Coverage limit: ordinary CI does not replace the three exact current-head test commands

## Ordinary repository gates

| Gate | Exact command or workflow | Result | Notes |
| --- | --- | --- | --- |
| format | current PR `rust-ci / Format / etc` | queued at inspection | historical workflow performed formatting before the source fence |
| lint | blocking CI Bazel clippy jobs | mixed/incomplete | Windows red; Linux/macOS incomplete at inspection |
| typecheck or compile | blocking CI Bazel build/test jobs | mixed/incomplete | several platform jobs red or running |
| focused package tests | `cargo test -p codex-core --test all --locked <exact test> -- --exact --nocapture` | historical 2/2 client pass; current head pending | full-agent requires stack discriminator |
| complete target-declared suite | blocking CI `30674311295` | red/incomplete | one inspected failure is outside unit fence |
| build or generated output | Bazel release verification | mixed/incomplete | no generated files in unit |
| platform matrix | blocking CI Linux/macOS/Windows | mixed/incomplete | current failures need per-job classification |

## Reversing controls

- behavioral control: first generated request has no warmup `previous_response_id` and carries complete input
- compatibility control: post-generation continuation uses `resp-1` and sends only the new suffix
- failure-path control: failed first generation retries the same complete request without warmup state
- isolation control: exact three-file fence excludes planner, Code Mode, manifests, workflows, and generated output

## Soak, leak, and cleanup controls

- iterations: one success sequence and one failure/retry sequence per focused test
- resources observed: WebSocket handshakes and captured request bodies
- timers/tasks/processes/files/listeners before and after: no dedicated leak accounting
- cancellation or interruption behavior: no dedicated cancellation test
- immediate rerun result: historical exact tests ran once in the retained receipt

## Setup and harness failures

| Attempt | Failure | Classification | Product claim affected? | Repair or stop |
| --- | --- | --- | --- | --- |
| historical full-agent default stack | Tokio worker stack overflow | runner/runtime | limits full-agent ordinary-runner acceptance; does not erase 2/2 client result | rerun at 16 MiB passed; retain discriminator |
| current `repo-checks` job `91298276097` | stale manifest exception for `codex-rs/code-mode/Cargo.toml` | base/repository gate outside unit fence | no direct product contradiction | record and avoid modifying unrelated file |
| current Windows/Bazel/SDK red jobs | cause not fully inspected | unclassified | unknown | classify before promotion |

## Checks prepared but not executed

- [`websocket_first_responses_lite_turn_sends_exact_current_request_after_startup_prewarm`](https://github.com/teamleaderleo/codex/blob/2c3f21d38056d2d77215cd9dce820a680d11cfe8/codex-rs/core/tests/suite/agent_websocket.rs) — execute on current head under default and 16 MiB worker stacks
- [`responses_lite_reuses_generated_response_after_full_first_turn`](https://github.com/teamleaderleo/codex/blob/2c3f21d38056d2d77215cd9dce820a680d11cfe8/codex-rs/core/tests/suite/client_websockets.rs) — execute exactly on current head
- [`responses_lite_retries_full_first_turn_after_failed_generation`](https://github.com/teamleaderleo/codex/blob/2c3f21d38056d2d77215cd9dce820a680d11cfe8/codex-rs/core/tests/suite/client_websockets.rs) — execute exactly on current head

## Platform and integration gaps

- live Responses Lite provider path
- proxy and reconnect behavior outside the repository fixture
- long-running WebSocket soak
- ordinary full-agent pass with default worker stack
- complete current Linux/macOS/Windows gate classification

## Cleanup receipt

- Temporary workflows removed from canonical source head: `yes`
- Publisher or execution-only files removed: `yes`
- Generated residue checked: current source diff has none
- Immediate rerun performed: `no` on current clean head
- Remaining temporary branches or PRs: owned draft source PR `#130`; historical execution PR `#58`; accidental Fieldwork branch `tmp-do-not-use` created during packet work and awaiting deletion because the available connector exposes no branch-delete action

## Current test judgment

`REPAIR`

Reason: the selected source remains coherent and its historical exact controls passed, while the clean current head still lacks the three exact focused executions and complete classification of its current ordinary CI failures.

Clearing condition: execute all three exact tests on `2c3f21d38056d2d77215cd9dce820a680d11cfe8`, retain the default-versus-large stack discriminator for the agent test, and obtain a complete-diff review that finds no source blocker.
