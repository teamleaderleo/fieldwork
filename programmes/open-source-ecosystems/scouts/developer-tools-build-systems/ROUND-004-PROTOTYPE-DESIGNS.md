# Developer tools scout round 004 — prototype designs

Date: 2026-08-03  
Programme: #207  
Scout lane: #210  
Owner: `chatgpt:gpt-5.6-thinking`  
State: `source-reviewed prototype designs; no production edits`  
Upstream contact authorized: `false`

## In simple words

The characterization branches now cover the main failure, alternate graph paths, and the compatibility behavior a real repair must preserve.

The source reads narrow each candidate to one decision point:

1. Turborepo must preserve package-selected affected task roots, then rebuild their required dependency closure without changing strict-entrypoint policy.
2. Helix must stop a matched command sequence after a command makes `Editor::should_close()` true.

These are reviewed prototype designs. Production files remain unchanged and no test result is claimed.

## Exact fork identities

### Turborepo

- repository: https://github.com/teamleaderleo/turborepo
- branch: `research/affected-filter-intersection`
- base: `c6fbc97bb8841f9c87d106af2d89ce11e97ea56c`
- head: `6d4785a34b70143f1ecc8fb9c19c161edb09a344`
- relation: `6 commits ahead, 0 behind`
- changed files: three added integration-test files
- additions: `511`
- production changes: none

### Helix

- repository: https://github.com/teamleaderleo/helix
- branch: `research/final-window-command-sequence`
- base: `079a789e8cb08ead67f19e1971a1b7438b37354b`
- head: `87972f36c950169ed0caeaab5a5a60dcafa488cb`
- relation: `5 commits ahead, 0 behind`
- changed files: one added integration-test module and one registration line
- additions: `132`
- production changes: none

# Turborepo prototype

## Current transition

In `crates/turborepo-lib/src/run/builder.rs`:

1. package scope resolution produces `filtered_pkgs` and package-derived entrypoint exclusions;
2. `affectedUsingTaskInputs` selects the separate affected path when `filterUsingTasks` is inactive;
3. that path builds an all-packages engine and clears the original package entrypoint exclusions;
4. `retain_affected_tasks` expands affected tasks through dependents and dependencies;
5. `select_engine_task_entrypoints` recomputes exclusions from the already-pruned engine;
6. the final `Run` reports `filtered_pkgs` while executing the separately pruned engine.

The lost fact is which affected task nodes were selector-authorized roots. An outside-package task may be either an unwanted affected root or a required dependency of a selected root.

## Existing engine operations

- `retain_affected_tasks` retains affected roots, dependents, and dependencies.
- `retain_filtered_tasks` retains selected roots and their dependencies, without adding dependents.
- `expand_with_siblings` preserves edge-less `with` relationships.
- `retain_strict_task_graph` applies strict command-presence policy and must stay feature-gated.

The combined `filterUsingTasks` path already intersects selector results with affected tasks and then uses filtered-task dependency closure. The separate affected path should converge on that authority rule without implicitly enabling its other feature gates.

## Current test matrix

### Selector authority

- `--filter=beta` with both independent tasks affected keeps only `beta#test`.
- `--parallel` must produce the same result after its separate engine rebuild.
- exclude-only `--filter=!alpha` must also keep only `beta#test`.

### Dependency closure

- `beta` depends on `alpha`.
- `test` depends on `^test`.
- selected `beta#test` must retain required `alpha#test`.

The selected root and dependency share the same task name. Package deletion and task-name deletion both fail this control.

### Entrypoint policy

- strict flag off: selected no-script `beta#test` remains under legacy behavior;
- strict flag on: selected no-script `beta#test` is pruned.

The repair must preserve the explicit flag distinction.

## Candidate transition

Apply selector authority only when:

- `use_task_level_affected` is active;
- explicit filter patterns are present;
- the combined `filterUsingTasks` path is inactive.

Then:

1. identify requested task roots belonging to the package-filter result;
2. preserve explicit package-qualified task requests under current rules;
3. intersect roots with task IDs remaining after affected pruning;
4. expand `with` siblings;
5. call `retain_filtered_tasks` to restore all required upstream task dependencies;
6. run strict command-presence pruning only when `strictTaskEntrypointSelection` is enabled.

Conceptual pseudocode:

```rust
if use_task_level_affected && !filter_patterns.is_empty() {
    let selected_roots = selector_authorized_command_tasks(
        &engine,
        filtered_pkgs.keys(),
        &self.opts.run_opts.tasks,
    );
    let selected_roots = expand_with_siblings(&engine, selected_roots);
    engine = engine.retain_filtered_tasks(&selected_roots);
}
```

The exact helper and placement remain open. The invariant is selected roots plus required dependencies.

## Rejected Turborepo approaches

- Delete every task outside `filtered_pkgs`: breaks `^test` dependency closure.
- Delete outside-package tasks sharing the requested task name: same failure.
- Reuse strict pruning unconditionally: changes legacy no-script behavior.
- Correct only dry-run rendering: execution remains broader.
- Apply package restriction without explicit filters: suppresses legitimate task-input affected results.

## Remaining Turborepo controls

- explicit `package#task` requests;
- `with` siblings;
- unaffected selected root;
- package/task reporting agreement under every selector form.

# Helix prototype

## Current transition

`EditorView::handle_keymap_event` executes every command in `MatchedSequence`:

```rust
for command in commands {
    execute_command(command);
}
```

`execute_command` performs command execution, `PostCommand`, possible `OnModeSwitch`, and insert-history bookkeeping.

`wclose` removes the final view after unsaved-buffer checks. `Editor::should_close()` then becomes true. The application event loop uses that predicate to stop before another event, but the complete matched sequence executes inside the current event.

## Hook boundary

The inspected completion `PostCommand` hook does not require a current view for the `wclose` reproduction. The following `normal_mode` command dereferences current view state. A normal-mode control with `move_char_right` confirms the question is generic.

## Current test matrix

1. `wclose` alone exits cleanly.
2. Insert-mode sequence `wclose`, `normal_mode` exits cleanly.
3. Normal-mode sequence `wclose`, `move_char_right` exits cleanly.
4. Ordinary non-closing sequence `insert_mode`, `normal_mode` runs to completion.
5. With another view remaining, the following command runs.
6. When final close is refused, the following command runs and the error remains.

## Candidate transition

Use the existing editor shutdown predicate after each complete command lifecycle:

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

Checking after `execute_command` preserves single-command `PostCommand` and mode-switch behavior. The loop stops only after actual terminal transition.

## Rejected Helix approaches

- Stop every sequence after `wclose`: breaks two-view continuation.
- Stop when `wclose` is invoked: breaks refused-close continuation.
- Add guards to individual view-dependent commands: duplicates lifecycle policy indefinitely.
- Rely only on the application event loop: control returns there after the sequence finishes.
- Skip `PostCommand` after final close without evidence: changes ordinary command lifecycle.

## Remaining Helix controls

- macro/replay path;
- callbacks queued during the closing command;
- count/register cleanup after terminal sequence;
- pending-key behavior.

# Current disposition

`PROTOTYPE DESIGNS READY; PRODUCTION SOURCE UNCHANGED`

Next evidence should come from exact-head target execution or a compile/setup failure. No public upstream interaction is authorized.
