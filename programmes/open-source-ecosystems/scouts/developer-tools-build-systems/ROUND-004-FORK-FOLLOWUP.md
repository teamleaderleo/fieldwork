# Developer tools scout round 004 — owned-fork follow-up

Date: 2026-08-03  
Programme: #207  
Scout lane: #210  
Owner: `chatgpt:gpt-5.6-thinking`  
State: `source-read continuation; owned fork branches active`  
Claim scope: `mechanism`  
Upstream contact authorized: `false`

## In simple words

The Turborepo and Helix forks are controlled research surfaces. Source reading, branch edits, test preparation, commit review, and durable notes proceed directly through GitHub in the owned repositories.

A local checkout is only needed for actual build and test execution. It is not a prerequisite for continuing source investigation or writing in the forks.

Open upstream issues remain supplementary evidence. They do not define the research agenda. Questions may be discovered directly from implementation, tests, contracts, and owned-fork experiments.

No public upstream interaction occurred.

## Authority and research method

The user explicitly authorized research and writing in:

- `teamleaderleo/fieldwork`;
- owned repositories under `teamleaderleo/*`;
- the Turborepo and Helix forks.

The user explicitly withheld authorization for upstream issues, comments, reactions, pull requests, or other public contact.

Before this continuation, the worker reread the Fieldwork policy set required by `START_HERE.md`, the developer-tools programme and scout records, the current Round 004 report, and each target's local contribution and test instructions.

## Exact owned-fork identities

### Turborepo

- Owned fork: https://github.com/teamleaderleo/turborepo
- Default branch: `main`
- Pinned fork base: `c6fbc97bb8841f9c87d106af2d89ce11e97ea56c`
- Research branch: `research/affected-filter-intersection`
- Current research head: `41341da9164e5e13e921f888ca196e8c77c9105e`
- Branch relation to base: `2 commits ahead, 0 behind`
- Current production source changes: none
- Work class: `upstream-fork research`

### Helix

- Owned fork: https://github.com/teamleaderleo/helix
- Default branch: `master`
- Pinned fork base: `079a789e8cb08ead67f19e1971a1b7438b37354b`
- Research branch: `research/final-window-command-sequence`
- Current research head: `d3352b57ed3b3f1527184e42afe23700b4371e43`
- Branch relation to base: `3 commits ahead, 0 behind`
- Current production source changes: none
- Work class: `upstream-fork research`

The user called the second fork “Helios.” Repository lookup found no `teamleaderleo/helios`; the available fork is `teamleaderleo/helix`, matching the Round 004 target and source revision.

## Evidence boundary

Evidence in this record includes:

- exact GitHub source reads;
- test and source-path design;
- owned-fork branch creation and commits;
- exact branch comparisons;
- Fieldwork review and note updates.

No build, lint, or test result is claimed. Those require target execution and will be recorded separately.

# Turborepo continuation

## Project instructions read

At the pinned fork revision, the worker read:

- `AGENTS.md`;
- `CONTRIBUTING.md`;
- `crates/turborepo/ARCHITECTURE.md`;
- the relevant run-builder implementation;
- the current affected integration tests.

Important target requirements include normal repository hooks, conventional pull-request titles, Rust checks, target integration tests, and an architecture-document review when core run-builder or task-graph behavior changes.

## Source model

Relevant implementation:

- `crates/turborepo-lib/src/run/builder.rs`
- `crates/turborepo-lib/src/run/task_filter.rs`
- `crates/turborepo-lib/src/task_change_detector.rs`
- `crates/turborepo-engine/src/lib.rs`

At the pinned revision:

1. package scope is first resolved into `filtered_pkgs`;
2. task-level combined filtering is enabled only when `futureFlags.filterUsingTasks` is active;
3. task-input affected detection has a separate path when `affectedUsingTaskInputs` is active and the combined task-filter path is inactive;
4. that separate path sets `needs_all_packages`, so the initial executable engine contains task nodes for every package;
5. `filter_engine_to_affected_tasks` computes affected task IDs and calls `Engine::retain_affected_tasks`;
6. package selectors represented by `filtered_pkgs` are not passed into that affected-task pruning operation;
7. later entrypoint selection does not establish the same package-selector intersection represented by the reported package list;
8. the final `Run` retains both the package list derived from `filtered_pkgs` and the separately pruned executable engine.

This creates a composition boundary: package reporting can describe one selected package set while the executable task engine retains a broader affected set.

## Prepared tests

The branch now contains two target-native test files:

1. `affected_task_filter_intersection_test.rs` — independent `alpha` and `beta` workspaces; both affected; only `beta#test` authorized.
2. `affected_task_filter_dependency_closure_test.rs` — `beta#test` requires `alpha#build`; expected graph retains `alpha#build` while excluding `alpha#test`.

The second control rejects a simple outside-package deletion that would break required dependency work.

## Candidate design comparison

Compare at least these locations before editing production code:

1. route package selectors and affected constraints through the existing combined task-filter path;
2. carry selector-authorized entrypoints into `retain_affected_tasks` or a neighboring engine operation;
3. intersect after affected pruning while explicitly restoring only dependency closure for selected entrypoints.

A display-only correction is rejected because it leaves execution broader than the user-visible scope.

## Turborepo stop condition

Stop or reframe if target-native execution establishes that package filters are intentionally informational in this flag combination, or if required dependency semantics cannot be represented without a broader task-filter design decision.

# Helix continuation

## Project instructions read

At the pinned fork revision, the worker read:

- `README.md`;
- `docs/CONTRIBUTING.md`;
- the keymap sequence dispatcher;
- the `wclose` command;
- integration-test helpers and split lifecycle tests.

Helix asks code contributors to add integration tests. The declared commands are `cargo test --workspace` and `cargo integration-test`, with optional `HELIX_LOG_LEVEL` for test diagnostics.

## Source model

Relevant implementation:

- `helix-term/src/ui/editor.rs`;
- `helix-term/src/commands.rs`;
- `helix-view/src/editor.rs`;
- `helix-term/src/application.rs`;
- `helix-term/tests/test/helpers.rs`;
- `helix-term/tests/test/splits.rs`.

At the pinned revision:

1. key lookup can return `KeymapResult::MatchedSequence(commands)`;
2. `EditorView::handle_keymap_event` loops over every command and invokes the same `execute_command` closure;
3. the loop has no continuation or terminal-state check between commands;
4. `wclose` checks unsaved-buffer policy when only one view remains, then calls `Editor::close` for the current view;
5. the next command in the sequence still executes even when the first command removed the final view;
6. `execute_command` also dispatches `PostCommand` and may dispatch `OnModeSwitch` after each command.

The lifecycle boundary is wider than “skip the second command.” Event dispatch immediately after the closing command also needs a defined post-close contract.

## Prepared tests

The branch now contains four cases in `helix-term/tests/test/command_sequences.rs`:

1. single-command final close exits cleanly;
2. two-command final close exits cleanly;
3. two-view close continues against the remaining view;
4. refused final close preserves the view, runs the next command, and retains the error status.

The single-command control separates close plus `PostCommand` from command-sequence continuation.

## Candidate design comparison

Prefer a central lifecycle contract. Compare:

- a stable `Editor` or `Application` terminal predicate checked immediately after each command;
- a `CommandResult` or continuation enum returned by command execution;
- a dispatcher helper that owns command execution plus event dispatch and knows whether post-command hooks remain valid.

Avoid scattered current-view guards in individual commands.

## Helix stop condition

Stop or reframe if integration execution establishes that final shutdown is intentionally deferred until a complete sequence finishes, or if the panic belongs solely to an event hook with a separate documented lifecycle contract.

# Current disposition

`CONTINUE — TWO OWNED-FORK CHARACTERIZATION LANES`

Next transitions:

1. continue source-path investigation in both forks;
2. execute the exact test heads when a target runner is available;
3. record exact results or compile failures in Fieldwork;
4. select no public upstream action without separate authorization.
