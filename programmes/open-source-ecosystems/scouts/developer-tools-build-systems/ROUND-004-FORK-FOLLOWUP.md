# Developer tools scout round 004 — owned-fork follow-up

Date: 2026-08-03  
Programme: #207  
Scout lane: #210  
Owner: `chatgpt:gpt-5.6-thinking`  
State: `source-read continuation; owned fork branches claimed; no target execution`  
Claim scope: `mechanism`  
Upstream contact authorized: `false`

## In simple words

The Turborepo and Helix forks are now controlled research surfaces. We can inspect them, add tests, compare candidate designs, and retain negative results without waiting for an upstream issue to define the work.

The first source pass found a concrete missing composition test in Turborepo and a command-dispatch lifecycle boundary in Helix. No target code has changed yet, no test has been claimed as executed, and no public upstream interaction occurred.

## Authority and research method

The user explicitly authorized research and writing in:

- `teamleaderleo/fieldwork`;
- owned repositories under `teamleaderleo/*`;
- the newly created Turborepo and Helix forks.

The user explicitly withheld authorization for upstream issues, comments, reactions, pull requests, or other public contact.

Open upstream issues are supplementary evidence. They do not define the research agenda. Questions may be discovered directly from implementation, tests, contracts, and owned-fork experiments.

Before this continuation, the worker reread the Fieldwork policy set required by `START_HERE.md`, the developer-tools programme and scout records, the current Round 004 report, and each target's local contribution and test instructions.

## Exact owned-fork identities

### Turborepo

- Owned fork: https://github.com/teamleaderleo/turborepo
- Default branch: `main`
- Pinned fork base: `c6fbc97bb8841f9c87d106af2d89ce11e97ea56c`
- Research branch: `research/affected-filter-intersection`
- Branch start: `c6fbc97bb8841f9c87d106af2d89ce11e97ea56c`
- Current source changes: none
- Work class: `upstream-fork research`

### Helix

- Owned fork: https://github.com/teamleaderleo/helix
- Default branch: `master`
- Pinned fork base: `079a789e8cb08ead67f19e1971a1b7438b37354b`
- Research branch: `research/final-window-command-sequence`
- Branch start: `079a789e8cb08ead67f19e1971a1b7438b37354b`
- Current source changes: none
- Work class: `upstream-fork research`

The user called the second fork “Helios.” Repository lookup found no `teamleaderleo/helios`; the available fork is `teamleaderleo/helix`, matching the Round 004 target and source revision.

## Execution boundary

The local execution runtime could not resolve `github.com`, so it could not clone either fork. GitHub repository reads and writes remained available.

Evidence in this record is therefore limited to:

- `source-read`;
- `target-test-design`;
- exact owned-fork branch identity.

No command, test, build, lint, or target workflow is described as executed.

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
6. the package selectors represented by `filtered_pkgs` are not passed into that affected-task pruning operation;
7. the later entrypoint selection does not establish the same package-selector intersection represented by the reported package list;
8. the final `Run` retains both the package list derived from `filtered_pkgs` and the separately pruned executable engine.

This creates a real composition boundary: package reporting can describe one selected package set while the executable task engine retains a broader affected set.

## Test map and newly identified blind spot

Primary target-native file:

- `crates/turborepo/tests/affected_test.rs`

Current coverage already includes:

- ordinary package-level `--affected` behavior;
- ordinary `--affected --filter=<package>` intersection;
- task-input affected detection under `futureFlags.affectedUsingTaskInputs`;
- task-input controls for global dependencies, root package changes, task names, and nonexistent tasks.

The inspected test file does not combine all three conditions:

1. `affectedUsingTaskInputs = true`;
2. `--affected`;
3. `--filter=<package>`.

That is the exact branch-composition gap in the implementation. It is useful independently of any upstream issue report.

## Bounded question

When task-input affected detection and package selectors are active together, which authority should define the final executable graph?

The candidate invariant is:

> The final task graph is the intersection of selector-authorized entrypoints and task-input affectedness, while retaining only dependency tasks required to execute those selected entrypoints.

## First target-native probe

Use the existing `affected_tasks_inputs` fixture or a smaller two-workspace fixture. Add a matrix that records both dry-run tasks and actual marker execution:

| Task-input affected | `--affected` | package selector | Expected result |
| --- | --- | --- | --- |
| off | on | selected package | ordinary package-level intersection |
| on | off | selected package | selected package tasks |
| on | on | absent | all affected task entrypoints plus required dependencies |
| on | on | selected package | selected affected task entrypoints plus only required dependencies |

Required controls:

- an affected task outside the selected package does not execute merely because it is affected;
- a dependency task required by the selected task remains in the graph;
- an unaffected selected package produces no selected work;
- exclude-only selectors preserve their declared behavior;
- the `--parallel` rebuild path applies the same authority rule;
- dry-run package reporting and executable task reporting agree.

## Candidate design comparison

Compare at least these locations before editing production code:

1. route package selectors and affected constraints through the existing combined task-filter path;
2. carry selector-authorized entrypoints into `retain_affected_tasks` or a neighboring engine operation;
3. intersect after affected pruning while explicitly restoring only dependency closure for selected entrypoints.

A display-only correction is rejected because it leaves execution broader than the user-visible scope. Blindly deleting every task outside the selected package is also rejected because it can remove required dependency work.

## Turborepo stop condition

Stop or reframe if target-native tests establish that package filters are intentionally informational in this flag combination, or if required dependency semantics cannot be represented without a broader task-filter design decision.

A failing characterization test may be retained without a production candidate. A candidate must not be selected until the dependency-closure control is explicit.

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

The lifecycle boundary is therefore wider than “skip the second command.” Event hooks dispatched immediately after the closing command may also need a valid post-close contract.

## Existing integration-test support

`helix-term/tests/test/helpers.rs` already provides:

- an `Application` builder;
- custom configuration through `AppBuilder::with_config`;
- key-sequence execution;
- an explicit `should_exit` assertion;
- editor inspection before closeout.

`helix-term/tests/test/splits.rs` already contains multi-view lifecycle tests, final-view exit assertions, and view-count controls. A target-native reproduction does not require a new test framework.

## Bounded question

What owns termination of a configured command sequence after one command makes the editor unable to execute view-dependent commands?

Competing contracts:

1. the sequence dispatcher checks a stable editor terminal state after every command;
2. command execution returns an explicit continuation result;
3. the application event loop owns terminal transition and command dispatch must stop immediately;
4. final-view close is deferred until the sequence finishes.

The fourth contract conflicts with the current immediate close path and should remain a reversing hypothesis until tested.

## First target-native probe

Create a custom test key binding equivalent to:

```toml
[keys.insert]
C-q = ["wclose", "normal_mode"]
```

Required cases:

1. **one view, clean buffer** — the application exits cleanly; no later view-dependent command or hook panics;
2. **two views** — `wclose` removes one view and the following command runs against the remaining view;
3. **one view, modified buffer** — refused close leaves the view alive; record whether the sequence continues under existing command semantics;
4. **single-command close** — existing final-window exit remains unchanged;
5. **post-command dispatch** — determine whether `PostCommand` and `OnModeSwitch` may safely run after final-view removal.

The test should distinguish “sequence stopped because the editor exited” from “individual commands defensively ignored missing state.”

## Candidate design comparison

Prefer a central lifecycle contract. Compare:

- a stable `Editor` or `Application` terminal predicate checked immediately after each command;
- a `CommandResult` or continuation enum returned by command execution;
- a dispatcher helper that owns command execution plus event dispatch and knows whether post-command hooks remain valid.

Avoid adding scattered current-view guards to individual commands. That approach leaves the next command and future commands exposed and hides the component that owns sequence continuation.

## Helix stop condition

Stop or reframe if integration tests establish that final shutdown is intentionally deferred until a complete sequence finishes, or if the panic originates solely in an event hook with a separate documented lifecycle contract.

Retain the lifecycle finding even if the eventual repair belongs in event dispatch rather than the command loop.

# Current disposition

`CONTINUE — TWO OWNED-FORK CHARACTERIZATION LANES`

Next transitions:

1. Turborepo: add the missing task-input-affected plus package-filter integration characterization on `research/affected-filter-intersection`.
2. Helix: add the final-window command-sequence integration characterization on `research/final-window-command-sequence`.
3. Run the smallest target-declared focused commands when an execution environment with repository access is available.
4. Record exact heads, commands, results, failures, and negative controls in this Fieldwork path.
5. Select no production fix until each characterization distinguishes the competing authority or lifecycle contracts.

No target fork pull request is required for private research coordination. No upstream packet or public interaction is authorized.