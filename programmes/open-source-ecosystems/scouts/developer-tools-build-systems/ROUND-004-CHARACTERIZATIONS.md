# Developer tools scout round 004 — prepared characterizations

Date: 2026-08-03  
Programme: #207  
Scout lane: #210  
Owner: `chatgpt:gpt-5.6-thinking`  
State: `test-only branches prepared; execution pending`  
Upstream contact authorized: `false`

## In simple words

Both owned research branches now contain narrow tests that ask the source-led questions recorded in the fork follow-up.

The tests have not been run. The available local runtime could not resolve GitHub for cloning, and no target workflow or pull request was created. These commits are prepared characterization inputs, not proof that the reported behavior occurs or that the test code passes target gates.

## Turborepo characterization

- Repository: https://github.com/teamleaderleo/turborepo
- Branch: `research/affected-filter-intersection`
- Base: `c6fbc97bb8841f9c87d106af2d89ce11e97ea56c`
- Head: `8d27b2b4a080f28fe35b8eab559176b713c88483`
- Ahead/behind: `1/0`
- Production source changes: none
- Added file: `crates/turborepo/tests/affected_task_filter_intersection_test.rs`
- Diff size: `159 additions`

### Question encoded by the test

The fixture has independent `alpha` and `beta` workspaces, each with a `test` task. It enables `futureFlags.affectedUsingTaskInputs`, declares `shared.txt` as a global dependency, commits the initial repository, then changes `shared.txt` so both tasks are affected.

It runs:

```text
turbo run test --affected --filter=beta --dry=json
```

The expected contract is:

- package reporting is exactly `beta`;
- executable task reporting is exactly `beta#test`.

This isolates package-selector authority without introducing dependency closure. A later control must add a real dependency from the selected task to another package so a repair cannot solve the independent-workspace case by deleting all outside-package tasks.

### Planned focused command

```text
cargo test -p turbo --test affected_task_filter_intersection_test -- --nocapture
```

Follow with the target's ordinary Rust and integration gates only after the characterization compiles and distinguishes current behavior.

### Review notes

- The test is target-native and uses the repository's existing `common::{git, run_turbo}` harness.
- The package-lock fixture is a minimal npm v3 workspace lockfile consistent with nearby tests.
- The test asserts engine-backed dry-run `taskId` values rather than console display text.
- The current test intentionally has no production candidate.
- Execution and formatting remain unverified.

## Helix characterization

- Repository: https://github.com/teamleaderleo/helix
- Branch: `research/final-window-command-sequence`
- Base: `079a789e8cb08ead67f19e1971a1b7438b37354b`
- Head: `c041c58c24e8ab6987cdfcda20cd0e8c859474ef`
- Ahead/behind: `2/0`
- Production source changes: none
- Added file: `helix-term/tests/test/command_sequences.rs`
- Registered module in: `helix-term/tests/integration.rs`
- Diff size: `64 additions`

### Questions encoded by the tests

The tests install an insert-mode binding equivalent to:

```toml
[keys.insert]
C-q = ["wclose", "normal_mode"]
```

Three cases are prepared:

1. one clean view — the application should exit cleanly;
2. two views — the close removes one view and `normal_mode` continues against the remaining view;
3. one modified view — the refused close leaves one view, the sequence continues to normal mode, and the existing error status remains visible.

The first case exercises the full current dispatcher boundary, including post-command event dispatch after `wclose`. A panic in the second command or a hook should fail the characterization.

### Planned focused command

```text
cargo integration-test command_sequence_after_final_window_close_exits_cleanly
```

If the target task runner does not accept a name filter in that position, run the repository-declared `cargo integration-test` and record the exact command rather than rewriting history.

### Review notes

- The test uses the existing `AppBuilder::with_config` and `test_key_sequence` harness.
- The custom keymap is parsed through the target's public `ConfigRaw` format and merged over defaults by the existing builder.
- The two-view and refused-close cases prevent an unconditional “stop every sequence after wclose” patch.
- The test does not yet isolate `PostCommand` from the following command. If the one-view test fails, the first repair step is to identify which boundary panics.
- Execution, formatting, and compilation remain unverified.

## Current disposition

`PREPARED / UNEXECUTED`

The next durable update must record one of these outcomes for each exact head:

- failing characterization with exact panic or task-list output;
- passing characterization, which weakens or retires the suspected behavior;
- setup or compile failure, which requires repairing the test before drawing a product conclusion.

No production fix should be written until the exact characterization is executed and reviewed. No public upstream interaction is authorized.