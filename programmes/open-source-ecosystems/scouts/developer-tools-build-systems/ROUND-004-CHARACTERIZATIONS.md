# Developer tools scout round 004 — prepared characterizations

Date: 2026-08-03  
Programme: #207  
Scout lane: #210  
Owner: `chatgpt:gpt-5.6-thinking`  
State: `test-only branches prepared; execution pending`  
Upstream contact authorized: `false`

## In simple words

Both owned research branches contain target-native tests derived from current source and existing contracts. GitHub-side investigation and editing continue directly in the forks. Actual test execution remains a separate evidence step.

No runtime result is claimed here. No target pull request or public upstream interaction occurred.

## Review recheck

Fieldwork PR #495 was rechecked on 2026-08-03.

- No independent review submission was present.
- No inline review thread was present.
- Existing comments and review submissions were exact-head self-reviews.

## Turborepo characterizations

- Repository: https://github.com/teamleaderleo/turborepo
- Branch: `research/affected-filter-intersection`
- Base: `c6fbc97bb8841f9c87d106af2d89ce11e97ea56c`
- Head: `6d4785a34b70143f1ecc8fb9c19c161edb09a344`
- Ahead/behind: `6/0`
- Production source changes: none
- Added files:
  - `crates/turborepo/tests/affected_task_filter_intersection_test.rs`
  - `crates/turborepo/tests/affected_task_filter_dependency_closure_test.rs`
  - `crates/turborepo/tests/affected_task_filter_legacy_entrypoint_test.rs`
- Final diff: `511 additions`

### Selector authority controls

Independent `alpha#test` and `beta#test` tasks are both affected by a global dependency change.

- `--filter=beta` expects only `beta#test`.
- `--filter=beta --parallel` expects the same task list after the alternate engine rebuild.
- exclude-only `--filter=!alpha` expects only `beta#test`.

### Same-name dependency closure

`beta` depends on `alpha`, and `test` declares `dependsOn: ["^test"]`.

The filtered run must retain:

- selected root `beta#test`;
- required dependency `alpha#test`.

This rejects pruning by package identity and pruning by requested task name.

### Strict policy controls

Selected package `beta` has no executable `test` script.

- strict flag off: expected task list contains `beta#test` under legacy behavior;
- strict flag on: expected task list is empty.

The repair must preserve this explicit feature distinction.

### Planned focused commands

```text
cargo test -p turbo --test affected_task_filter_intersection_test -- --nocapture
cargo test -p turbo --test affected_task_filter_dependency_closure_test -- --nocapture
cargo test -p turbo --test affected_task_filter_legacy_entrypoint_test -- --nocapture
```

### Review notes

- Tests use the existing `common::{git, run_turbo}` harness.
- Assertions inspect engine-backed dry-run `taskId` values.
- Minimal npm v3 workspace lockfiles follow nearby test patterns.
- Fixture discovery, compilation, formatting, and execution remain unverified.

## Helix characterizations

- Repository: https://github.com/teamleaderleo/helix
- Branch: `research/final-window-command-sequence`
- Base: `079a789e8cb08ead67f19e1971a1b7438b37354b`
- Head: `87972f36c950169ed0caeaab5a5a60dcafa488cb`
- Ahead/behind: `5/0`
- Production source changes: none
- Added file: `helix-term/tests/test/command_sequences.rs`
- Registered module in: `helix-term/tests/integration.rs`
- Final diff: `132 additions`

### Final-close controls

- Single insert-mode `wclose` exits cleanly.
- Insert-mode sequence `wclose`, `normal_mode` exits cleanly.
- Normal-mode sequence `wclose`, `move_char_right` exits cleanly.

The normal-mode case proves the lifecycle question is generic and not tied to completion handling.

### Continuation controls

- Ordinary non-closing sequence `insert_mode`, `normal_mode` runs fully.
- With two views, closing one view allows the following command to run against the remaining view.
- With one modified view, refused close allows the following command to run and preserves the error status.

These controls require a terminal-state check rather than a command-name check.

### Planned focused commands

```text
cargo integration-test single_command_final_window_close_exits_cleanly
cargo integration-test command_sequence_after_final_window_close_exits_cleanly
cargo integration-test normal_mode_sequence_after_final_window_close_exits_cleanly
cargo integration-test ordinary_command_sequence_runs_to_completion
cargo integration-test command_sequence_continues_when_another_window_remains
cargo integration-test refused_final_window_close_keeps_sequence_context_alive
```

### Review notes

- Tests use `AppBuilder::with_config` and `test_key_sequence`.
- Custom keymaps are parsed through `ConfigRaw` and merged over defaults.
- `Editor::should_close()` is the same predicate used by the application event loop.
- The inspected completion `PostCommand` hook does not appear to dereference the missing view for `wclose`; the following view-dependent command is the narrower suspected failure.
- Compilation, formatting, and execution remain unverified.

## Prototype design reference

See `ROUND-004-PROTOTYPE-DESIGNS.md` for candidate transitions and rejected approaches.

## Current disposition

`PREPARED / UNEXECUTED / CONTINUING IN OWNED FORKS`

The next durable execution update must record one of:

- failing characterization with exact output or panic;
- passing characterization;
- compile or setup failure requiring test repair.

No public upstream interaction is authorized.
