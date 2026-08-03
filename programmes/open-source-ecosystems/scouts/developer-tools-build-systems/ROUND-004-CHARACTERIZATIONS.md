# Developer tools scout round 004 — prepared characterizations

Date: 2026-08-03  
Programme: #207  
Scout lane: #210  
Owner: `chatgpt:gpt-5.6-thinking`  
State: `test-only branches prepared; execution pending`  
Upstream contact authorized: `false`

## In simple words

Both owned research branches contain narrow tests derived from source and target contracts. Work in the forks does not depend on cloning them into this chat runtime: GitHub-side source reading, branch creation, file edits, commit review, and Fieldwork recording all proceed directly in the owned repositories.

Running the target tests is a separate evidence step. It requires a runner with the repository contents and declared toolchain. No test result is claimed here.

The second review pass added two reversing controls:

1. Turborepo must retain a required cross-package dependency task while excluding an unrelated affected entrypoint.
2. Helix must distinguish a safe single-command final-window close from a failing multi-command continuation after the same close.

No target pull request was created and no public upstream interaction occurred.

## Review recheck

Fieldwork PR #495 was rechecked on 2026-08-03.

- No independent review submission was present.
- No inline review thread was present.
- Existing comments and review submissions were the repository owner's own exact-head reviews.

This review state does not block continued research in the owned forks.

## Turborepo characterizations

- Repository: https://github.com/teamleaderleo/turborepo
- Branch: `research/affected-filter-intersection`
- Base: `c6fbc97bb8841f9c87d106af2d89ce11e97ea56c`
- Head: `41341da9164e5e13e921f888ca196e8c77c9105e`
- Ahead/behind: `2/0`
- Production source changes: none
- Added files:
  - `crates/turborepo/tests/affected_task_filter_intersection_test.rs`
  - `crates/turborepo/tests/affected_task_filter_dependency_closure_test.rs`
- Diff size: `332 additions`

### Characterization A — independent workspaces

The fixture has independent `alpha` and `beta` workspaces, each with a `test` task. It enables `futureFlags.affectedUsingTaskInputs`, declares `shared.txt` as a global dependency, commits the initial repository, then changes `shared.txt` so both tasks are affected.

It runs:

```text
turbo run test --affected --filter=beta --dry=json
```

The expected contract is:

- package reporting is exactly `beta`;
- executable task reporting is exactly `beta#test`.

This asks whether a package selector remains an execution authority when task-input affected detection runs through its separate all-packages engine path.

### Characterization B — required dependency closure

The second fixture makes `beta` depend on `alpha`. `beta#test` declares `dependsOn: ["^build"]`, and `alpha` provides both `build` and `test` scripts. A global dependency change marks the task set affected.

The same filtered command should produce exactly:

- `beta#test` as the selector-authorized entrypoint;
- `alpha#build` as required dependency work;
- no `alpha#test` entrypoint.

This rejects two bad outcomes:

1. retaining every affected task and ignoring package authorization;
2. deleting every task outside `beta` and breaking required dependency execution.

### Planned focused commands

```text
cargo test -p turbo --test affected_task_filter_intersection_test -- --nocapture
cargo test -p turbo --test affected_task_filter_dependency_closure_test -- --nocapture
```

Follow with the target's ordinary Rust and integration gates only after both characterizations compile and distinguish current behavior.

### Review notes

- Both tests use the repository's existing `common::{git, run_turbo}` integration harness.
- Both assert engine-backed dry-run `taskId` values rather than console display text.
- The dependency control sorts task IDs before comparison because task-list ordering is not the behavior under test.
- The minimal npm v3 workspace lockfiles follow patterns already present in nearby target tests.
- The dependency fixture and lockfile still require target execution to verify that npm workspace relationship discovery accepts the minimal representation.
- No production candidate has been selected.
- Execution, formatting, and compilation remain unverified.

## Helix characterizations

- Repository: https://github.com/teamleaderleo/helix
- Branch: `research/final-window-command-sequence`
- Base: `079a789e8cb08ead67f19e1971a1b7438b37354b`
- Head: `d3352b57ed3b3f1527184e42afe23700b4371e43`
- Ahead/behind: `3/0`
- Production source changes: none
- Added file: `helix-term/tests/test/command_sequences.rs`
- Registered module in: `helix-term/tests/integration.rs`
- Diff size: `86 additions`

### Characterization A — single-command final close

A custom insert-mode binding maps `C-q` directly to `wclose`.

Required result:

- closing the only clean view exits the application without panic.

Because the common command wrapper dispatches `PostCommand` after every mapped command, this case asks whether close plus its immediate post-command dispatch is safe without a following command.

### Characterization B — sequence after final close

A second binding maps:

```toml
[keys.insert]
C-q = ["wclose", "normal_mode"]
```

Required result:

- one clean view exits without running unsafe continuation against missing view state.

Comparing this case with the single-command control distinguishes the basic close/post-command path from sequence continuation.

### Characterization C — another view remains

With two views, the same sequence must:

- close one view;
- retain one view;
- execute `normal_mode` against the remaining view;
- leave no error status.

This rejects an unconditional rule that stops every sequence after `wclose`.

### Characterization D — close is refused

With one modified view, `wclose` is refused by existing unsaved-buffer policy. The test records the current expected sequence behavior:

- one view remains;
- `normal_mode` runs;
- the close error status remains visible.

This distinguishes terminal transition from an ordinary command refusal.

### Planned focused commands

```text
cargo integration-test single_command_final_window_close_exits_cleanly
cargo integration-test command_sequence_after_final_window_close_exits_cleanly
cargo integration-test command_sequence_continues_when_another_window_remains
cargo integration-test refused_final_window_close_keeps_sequence_context_alive
```

If the target task runner does not accept a name filter in that position, run the repository-declared `cargo integration-test` and record the exact command and result.

### Review notes

- Tests use the existing `AppBuilder::with_config` and `test_key_sequence` harness.
- Custom keymaps are parsed through `ConfigRaw` and merged over defaults by the existing builder.
- The single-command control narrows the likely boundary if the sequence test fails.
- A remaining failure may occur in the following command, `PostCommand`, `OnModeSwitch`, or application exit observation; exact execution is needed before choosing ownership.
- No production candidate has been selected.
- Execution, formatting, and compilation remain unverified.

## Exact-head review checkpoint

The target branch comparisons were re-read after the second control commits:

- Turborepo: two commits ahead, two added integration-test files, no production source changes.
- Helix: three commits ahead, one added integration-test module plus registration, no production source changes.

No weak control requiring immediate removal was found. The remaining uncertainty is execution evidence, not repository ownership or source access.

## Current disposition

`PREPARED / UNEXECUTED / CONTINUING IN OWNED FORKS`

The next durable update must record one of these outcomes for each exact head:

- failing characterization with exact panic or task-list output;
- passing characterization, which weakens or retires the suspected behavior;
- setup or compile failure, which requires repairing the test before drawing a product conclusion.

No public upstream interaction is authorized.
