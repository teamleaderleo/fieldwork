# Developer tools scout round 004 — prototype designs

Date: 2026-08-03  
Programme: #207  
Scout lane: #210  
Owner: `chatgpt:gpt-5.6-thinking`  
State: `source-reviewed prototype designs; no production edits`  
Upstream contact authorized: `false`

## In simple words

The characterization branches now cover the easy failure cases and the controls that a real repair must preserve.

The source reads also narrowed each candidate to one local decision point:

1. Turborepo must preserve the original package-selected task roots while rebuilding their required task dependency closure after task-input affected detection.
2. Helix must stop a matched command sequence when `Editor::should_close()` becomes true after a command.

These are prototype designs, not executed fixes. Production files have not changed.

## Exact fork identities

### Turborepo

- repository: https://github.com/teamleaderleo/turborepo
- branch: `research/affected-filter-intersection`
- base: `c6fbc97bb8841f9c87d106af2d89ce11e97ea56c`
- head: `119e86a88e0ac9c2fe6a161e60297b4b73ebcb45`
- relation: `4 commits ahead, 0 behind`
- changed files: three added integration-test files
- additions: `481`
- production changes: none

### Helix

- repository: https://github.com/teamleaderleo/helix
- branch: `research/final-window-command-sequence`
- base: `079a789e8cb08ead67f19e1971a1b7438b37354b`
- head: `bee45f3356202158a03941b3d21aa15dc4cb63fb`
- relation: `4 commits ahead, 0 behind`
- changed files: one added integration-test module and one registration line
- additions: `104`
- production changes: none

# Turborepo prototype

## Current source transition

The relevant build sequence in `crates/turborepo-lib/src/run/builder.rs` is:

1. package scope resolution produces `filtered_pkgs`, `filter_mode`, and package-derived entrypoint exclusions;
2. `affectedUsingTaskInputs` selects the separate `use_task_level_affected` path when `filterUsingTasks` is inactive;
3. that path sets `needs_all_packages`;
4. the all-packages engine is built with an empty entrypoint-exclusion set;
5. task input matching produces affected task IDs;
6. `Engine::retain_affected_tasks` expands affected tasks through dependents and dependencies;
7. `select_engine_task_entrypoints` recomputes exclusions from the already-pruned engine;
8. the final `Run` reports packages from `filtered_pkgs` while executing the independently pruned engine.

The defect is loss of the original selector-authorized task roots. By step 7, the engine can no longer distinguish an outside-package affected entrypoint from an outside-package task required as a dependency of a selected entrypoint.

## Existing engine operations

The engine already provides the two different closures needed to reason about the repair:

- `retain_affected_tasks` — affected roots, transitive dependents, and transitive dependencies;
- `retain_filtered_tasks` — selected roots and transitive dependencies, without dependent expansion.

The separate task-filter path already uses `retain_filtered_tasks` after resolving selectors and intersecting an affected constraint. That behavior is the closest existing contract.

## Characterization matrix

The branch contains three files:

1. `affected_task_filter_intersection_test.rs`
   - independent `alpha#test` and `beta#test`;
   - both affected by a global dependency change;
   - `--filter=beta` must retain only `beta#test`.

2. `affected_task_filter_dependency_closure_test.rs`
   - `beta` depends on `alpha`;
   - `test` depends on `^test`;
   - `--filter=beta` must retain `beta#test` and required `alpha#test`;
   - package identity or task-name deletion would fail this control.

3. `affected_task_filter_legacy_entrypoint_test.rs`
   - `strictTaskEntrypointSelection` is false;
   - selected package `beta` has no executable `test` script;
   - `beta#test` must remain under legacy semantics;
   - the repair must not silently enable strict entrypoint pruning.

## Candidate transition

Apply selector authority only when all of these are true:

- task-input affected detection is active through `use_task_level_affected`;
- explicit package filter patterns are present;
- the command is not already using the combined `filterUsingTasks` path.

At that point:

1. compute or retain the task roots authorized by the original package-filter result and requested task names;
2. preserve explicit package-qualified task requests according to existing rules;
3. intersect those roots with the affected engine’s surviving task IDs;
4. expand `with` siblings using the existing task-filter helper;
5. call `retain_filtered_tasks` so every selected root retains its complete upstream task dependency closure;
6. leave strict command-presence pruning gated by `strictTaskEntrypointSelection` exactly as it is now.

Conceptual pseudocode:

```rust
if use_task_level_affected && !filter_patterns.is_empty() {
    let selected_roots = command_task_ids_for_packages(
        &engine,
        filtered_pkgs.keys(),
        &self.opts.run_opts.tasks,
    );
    let selected_roots = expand_with_siblings(&engine, selected_roots);
    engine = engine.retain_filtered_tasks(&selected_roots);
}
```

The helper name and exact placement remain open. The important contract is selected roots plus required dependencies, not package-wide deletion.

## Rejected Turborepo approaches

### Delete all tasks outside `filtered_pkgs`

Rejected because `alpha#test` may be required by selected `beta#test` through `^test`.

### Delete outside-package tasks with the requested task name

Rejected for the same reason: a required dependency can have the same task name as the selected root.

### Reuse `retain_strict_task_graph` unconditionally

Rejected because existing tests require non-strict missing-command task nodes when `strictTaskEntrypointSelection` is false.

### Correct only dry-run package rendering

Rejected because the executable engine remains broader.

### Apply package selection when no explicit filters exist

Rejected because task-input affected detection intentionally starts from all packages and can identify tasks outside package-level affectedness.

## Additional Turborepo controls before production edit

- exclude-only package selectors;
- explicit `package#task` requests;
- `--parallel` engine rebuild;
- `with` siblings;
- an unaffected selected root;
- strict entrypoint selection on and off;
- package list and task list agreement.

# Helix prototype

## Current source transition

`EditorView::handle_keymap_event` receives `KeymapResult::MatchedSequence(commands)` and currently executes every command:

```rust
for command in commands {
    execute_command(command);
}
```

The shared command wrapper performs:

1. `command.execute(cxt)`;
2. `PostCommand` dispatch;
3. mode comparison;
4. possible `OnModeSwitch` dispatch;
5. insert-history bookkeeping.

`wclose` removes the current view after unsaved-buffer checks. Removing the final view makes `Editor::should_close()` true. The application event loop uses this same predicate to stop before processing another event.

The current sequence loop does not check it, so a following view-dependent command runs during the same key event.

## Hook boundary

The registered completion `PostCommand` hook for the insert-mode reproduction does not require a current view for `wclose`; it cancels or clears completion state. The following `normal_mode` command calls `Editor::enter_normal_mode`, which dereferences the current view after switching mode.

A normal-mode control now uses `move_char_right` as the second command, proving the lifecycle issue is generic and not tied to completion or insert-mode bookkeeping.

## Characterization matrix

`helix-term/tests/test/command_sequences.rs` now contains:

1. single-command final close — `wclose` alone exits cleanly;
2. insert-mode final close sequence — `wclose`, then `normal_mode`;
3. normal-mode final close sequence — `wclose`, then `move_char_right`;
4. two-view continuation — the following command runs against the remaining view;
5. refused final close — the following command runs because the editor remains open.

## Candidate transition

Use the existing public editor shutdown predicate in the matched-sequence loop:

```rust
KeymapResult::MatchedSequence(commands) => {
    for command in commands {
        execute_command(command);
        if cxt.editor.should_close() {
            break;
        }
    }
}
```

The check belongs after `execute_command` so the closing command retains the same `PostCommand` and mode-switch lifecycle as a single mapped command. The loop stops only after an actual terminal transition.

## Rejected Helix approaches

### Stop every sequence after `wclose`

Rejected because closing one of multiple views must allow later commands to operate on the remaining view.

### Stop when `wclose` is invoked

Rejected because unsaved-buffer policy may refuse the close; the editor remains valid and current sequence behavior continues.

### Add missing-view guards to `normal_mode` or movement commands

Rejected because every future view-dependent command would need the same defensive check.

### Move the shutdown check into the application event loop only

Rejected because the complete command sequence executes inside one event before control returns to that loop.

### Skip `PostCommand` after final close without evidence

Rejected because single-command mapped commands currently dispatch `PostCommand`, and the inspected hook does not appear to cause the reported panic.

## Additional Helix controls before production edit

- macro/replay path using a mapped sequence;
- a sequence where the first command changes mode without closing;
- callback state queued by the closing command;
- command count/register cleanup after a terminal sequence;
- ordinary single-command and pending-key behavior.

# Current disposition

`PROTOTYPE DESIGNS READY; PRODUCTION SOURCE UNCHANGED`

Next evidence should come from exact-head target execution or a compile/setup failure. Until then, these designs remain reviewed hypotheses in owned repositories.

No public upstream interaction is authorized.
