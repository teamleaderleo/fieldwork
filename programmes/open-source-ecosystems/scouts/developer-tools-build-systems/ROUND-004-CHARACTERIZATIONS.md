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
- Head: `119e86a88e0ac9c2fe6a161e60297b4b73ebcb45`
- Ahead/behind: `4/0`
- Production source changes: none
- Added files:
  - `crates/turborepo/tests/affected_task_filter_intersection_test.rs`
  - `crates/turborepo/tests/affected_task_filter_dependency_closure_test.rs`
  - `crates/turborepo/tests/affected_task_filter_legacy_entrypoint_test.rs`
- Final diff: `481 additions`

### A — independent selected root

Independent `alpha#test` and `beta#test` tasks are both affected by a global dependency change.

```text
turbo run test --affected --filter=beta --dry=json
```

Expected task list: `beta#test` only.

This tests whether package selection remains an execution authority in the separate task-input affected path.

### B — same-name required dependency

`beta` depends on `alpha`, and `test` declares `dependsOn: ["^test"]`.

The same command must retain:

- selected root `beta#test`;
- required dependency `alpha#test`.

This control rejects deletion by package identity and deletion by requested task name. The selected root and required outside-package dependency have the same task name.

### C — legacy non-strict entrypoint

`strictTaskEntrypointSelection` is false, and selected package `beta` has no executable `test` script.

Expected task list: `beta#test`.

This control requires `affectedUsingTaskInputs` to preserve legacy package-filter entrypoint behavior rather than silently enabling strict pruning.

### Planned focused commands

```text
cargo test -p turbo --test affected_task_filter_intersection_test -- --nocapture
cargo test -p turbo --test affected_task_filter_dependency_closure_test -- --nocapture
cargo test -p turbo --test affected_task_filter_legacy_entrypoint_test -- --nocapture
```

### Review notes

- Tests use the existing `common::{git, run_turbo}` harness.
- Assertions inspect engine-backed dry-run `taskId` values.
- The same-name dependency control sorts task IDs because ordering is outside the question.
- Minimal npm v3 workspace lockfiles follow nearby test patterns.
- Fixture discovery, compilation, formatting, and execution remain unverified.

## Helix characterizations

- Repository: https://github.com/teamleaderleo/helix
- Branch: `research/final-window-command-sequence`
- Base: `079a789e8cb08ead67f19e1971a1b7438b37354b`
- Head: `bee45f3356202158a03941b3d21aa15dc4cb63fb`
- Ahead/behind: `4/0`
- Production source changes: none
- Added file: `helix-term/tests/test/command_sequences.rs`
- Registered module in: `helix-term/tests/integration.rs`
- Final diff: `104 additions`

### A — single-command final close

Insert-mode `C-q = "wclose"` closes the only clean view and exits.

This isolates close plus ordinary `PostCommand` dispatch without a following command.

### B — insert-mode sequence after final close

```toml
[keys.insert]
C-q = ["wclose", "normal_mode"]
```

The application must exit without executing unsafe continuation against missing view state.

### C — normal-mode sequence after final close

```toml
[keys.normal]
C-q = ["wclose", "move_char_right"]
```

The second command requires a current view. This proves the lifecycle question is generic and does not depend on insert-mode completion hooks.

### D — another view remains

With two views, the insert-mode sequence closes one view and runs `normal_mode` against the remaining view.

This rejects an unconditional stop based on command identity.

### E — close is refused

With one modified view, `wclose` is refused. The view remains, the following command runs, and the existing error status remains visible.

This distinguishes terminal transition from ordinary command refusal.

### Planned focused commands

```text
cargo integration-test single_command_final_window_close_exits_cleanly
cargo integration-test command_sequence_after_final_window_close_exits_cleanly
cargo integration-test normal_mode_sequence_after_final_window_close_exits_cleanly
cargo integration-test command_sequence_continues_when_another_window_remains
cargo integration-test refused_final_window_close_keeps_sequence_context_alive
```

### Review notes

- Tests use `AppBuilder::with_config` and `test_key_sequence`.
- Custom keymaps are parsed through `ConfigRaw` and merged over defaults by the existing builder.
- Source review found `Editor::should_close()` already represents the application shutdown predicate.
- The inspected completion `PostCommand` hook does not appear to dereference the missing view for `wclose`; the following view-dependent command is the narrower suspected failure.
- Compilation, formatting, and execution remain unverified.

## Prototype design reference

See `ROUND-004-PROTOTYPE-DESIGNS.md` for exact candidate transitions and rejected approaches.

## Current disposition

`PREPARED / UNEXECUTED / CONTINUING IN OWNED FORKS`

The next durable execution update must record one of:

- failing characterization with exact output or panic;
- passing characterization;
- compile or setup failure requiring test repair.

No public upstream interaction is authorized.
