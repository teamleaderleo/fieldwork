# Developer tools and build systems scout — round 004

Date: 2026-08-02  
Programme: #207  
Scout lane: #210  
State: `source-read routing; no target implementation claimed`  
Upstream contact authorized: `false`

## In simple words

This round keeps two current defects for deeper work:

1. Turborepo can report that a package filter selected one workspace while still scheduling an executable task from another workspace when task-input-based affected detection is enabled.
2. Helix can continue executing a multi-command key binding after the first command closes the final editor window, so the next command reaches editor state that no longer has a view and panics.

The round also records several attractive issues that are already owned, explicitly on hold, fixed on current code, or awaiting current-version reproduction. Those are exclusions, not contribution recommendations.

No public issue comment, reaction, pull request, branch, release, or other upstream interaction was made.

## Policy and evidence boundary

Before this round, the worker read the repository-required policy set on the active Fieldwork intake branch:

- `AGENTS.md`;
- `START_HERE.md`;
- `CHARTER.md`;
- `CODE_FIRST.md`;
- `PLAIN_LANGUAGE.md`;
- `METHOD.md`;
- `REFERENCE_POLICY.md`;
- `PROGRAMMES.md`;
- `TARGET_HUBS.md`;
- `EXPERIMENTS.md`;
- `TESTBEDS.md`;
- `INTEGRATION_CONTEXT.md`;
- `COORDINATION.md`;
- `REVIEWING.md`;
- `BATCHES.md`;
- `programmes/registry.yml`;
- `targets/hubs.yml`.

The applicable rules are quiet research, code-first qualification, narrow evidence labels, explicit stop conditions, durable repository records, and no third-party contact without separate authorization.

Evidence classes in this report:

- **source-read** — current target instructions and implementation paths were read at an exact public commit;
- **public-record verified** — issue, comment, assignment, and pull-request metadata were checked, without target execution;
- **revalidation-first** — consequence is credible, but current-version reproduction must precede implementation selection;
- **excluded** — active development, explicit maintainer hold, upstream ownership, or current-main repair prevents a clean claim.

No target repository was cloned or executed in this round. Reproduction commands below are proposed next probes, not retained execution receipts.

## Ranking

| Rank | Target | Finding | Current disposition |
| ---: | --- | --- | --- |
| 1 | Turborepo | `--filter` package reporting can diverge from the executable task graph under task-input affected detection | `PROMOTE — deterministic source-read implementation probe` |
| 2 | Helix | a command sequence continues after closing the final window and the next command panics | `PROMOTE — deterministic lifecycle implementation probe` |
| 3 | GitButler | upstream integration can leave refs, metadata, workspace commit, and worktree in different generations | `REVALIDATE — current nightly first; overlapping active repairs` |
| 4 | Rolldown | raw dev resolver cache retains deleted or newly created path state across watch rounds | `MONITOR — failing test already lives on an upstream-owned branch` |

## Lead A — Turborepo filter and affected-task intersection

### Public record

- Repository: https://github.com/vercel/turborepo
- Issue: https://github.com/vercel/turborepo/issues/13636
- Retrieval state: open, unassigned, two comments, no matching open repair pull request found.
- Reporter supplied a clean two-workspace repository and verified the result on stable `2.10.7` and canary `2.10.8-canary.4`.

### User-visible consequence

With `futureFlags.affectedUsingTaskInputs` enabled, this command can report only package `beta` while the executable graph contains both `alpha#test` and `beta#test`:

```text
turbo run test --affected --filter=beta --dry=json
```

A filtered command can therefore execute work outside the package set shown to the caller. This affects CI scoping, local targeted runs, resource usage, and any task with side effects.

### Exact source snapshot and instructions read

- Source snapshot: `vercel/turborepo@c6fbc97bb8841f9c87d106af2d89ce11e97ea56c`
- Read `AGENTS.md`.
- Read `CONTRIBUTING.md`.
- Read `crates/turborepo/ARCHITECTURE.md`.
- Read the relevant run-builder path in `crates/turborepo-lib/src/run/builder.rs`.

Target instructions require conventional PR titles, normal hooks, repository Rust checks, and architecture-document review when core run, engine, or task-graph behavior changes.

### Source map

The source read supports the report’s behavior:

1. `use_task_level_filter` is enabled only when `futureFlags.filterUsingTasks` is enabled and filter or affected selectors are present.
2. `use_task_level_affected` is separately enabled when `affectedUsingTaskInputs` is active and `use_task_level_filter` is false.
3. Task-level affected mode sets `needs_all_packages`, so the initial engine contains tasks from all packages.
4. `filter_engine_to_affected_tasks` computes affected tasks from changed files and calls `Engine::retain_affected_tasks`.
5. In this path, the package filter is not passed into that affected-task pruning step.
6. A later entrypoint-selection pass does not establish the same package-filter intersection represented by the reported `packages` list.

This is a run-builder composition defect rather than a dry-run rendering-only defect: the executable engine itself retains the extra task.

### First discriminating experiment

Recreate the reporter’s two independent workspaces as a target-native integration fixture and capture four controls:

| `affectedUsingTaskInputs` | `--affected` | `--filter=beta` | Expected executable tasks |
| --- | --- | --- | --- |
| off | on | on | `beta#test` |
| on | off | on | `beta#test` |
| on | on | absent | `alpha#test`, `beta#test` |
| on | on | on | `beta#test` |

The test must inspect the engine-backed dry-run task list and, where practical, execute marker commands proving only `beta` ran.

### Candidate repair boundary

The required invariant is:

> When package selectors and task-input affected detection are both active, the final executable task graph is the intersection of the selector-authorized graph and the affected-task closure, plus only the dependencies required by selected executable tasks.

Candidate locations to compare:

- promote combined selector handling into the task-filter path even when only `affectedUsingTaskInputs` is enabled;
- apply a package-authority constraint before or during `retain_affected_tasks`;
- avoid a late display-only correction that leaves the execution engine broad.

The repair must preserve transitive dependencies needed to execute the selected task. A simple package-name deletion after graph closure is unsafe if `beta#test` legitimately depends on an upstream task.

### Negative controls

- filtering an unaffected workspace yields no work;
- explicit package-qualified tasks remain selectable according to existing semantics;
- dependency tasks required by a selected task remain present;
- exclude-only selectors retain their documented behavior;
- `--parallel` rebuild path applies the same final intersection;
- ordinary package-level `--affected` behavior is unchanged;
- dry-run package reporting and executable task reporting agree.

### Stop condition

Stop and change this lead to `ISSUE FIRST` if the current target contract intentionally defines `--filter` as display-only in this flag combination. The existing control behavior and architecture text currently point the other way, but maintainer intent must be checked before publishing a source repair.

### Promotion output

A promoted packet should contain:

- current exact default-branch SHA;
- target-native failing integration test;
- source and test map;
- comparison of at least two graph-intersection locations;
- proof that required dependency closure survives;
- focused test and ordinary Rust gate receipts;
- architecture-document disposition;
- fresh issue, pull-request, and branch duplicate sweep;
- concise proposed PR body;
- upstream-contact state, still `false` until separately authorized.

## Lead B — Helix command sequence after final-window close

### Public record

- Repository: https://github.com/helix-editor/helix
- Issue: https://github.com/helix-editor/helix/issues/16111
- Retrieval state: open, unassigned, zero comments, no matching open repair pull request found.
- Reproduction uses a custom key binding such as:

```toml
[keys.insert]
C-q = ["wclose", "normal_mode"]
```

The panic occurs when the binding runs against the final remaining window. The reporter also reproduced it with other commands after `wclose`, including from normal mode.

### User-visible consequence

A valid configured command sequence can close the editor and then panic during the same key event. The defect is broader than `normal_mode`: any command that assumes a current view may run after the sequence’s earlier command removed the final view.

### Exact source snapshot and instruction search

- Source snapshot: `helix-editor/helix@079a789e8cb08ead67f19e1971a1b7438b37354b`
- No root or `.github` `CONTRIBUTING.md` was present at the checked paths.
- Relevant implementation files read:
  - `helix-term/src/ui/editor.rs`;
  - `helix-term/src/commands.rs`;
  - `helix-view/src/editor.rs`;
  - issue-reported panic location in `helix-view/src/tree.rs`.

### Source map

The source path is narrow:

1. Keymap lookup can return `KeymapResult::MatchedSequence(commands)`.
2. `EditorView` iterates the entire sequence and calls `execute_command(command)` for every item.
3. The loop has no guard for the editor having entered its terminal/no-view state after an earlier command.
4. `wclose` treats the last view specially, checks unsaved buffers, and then closes the final window/editor path.
5. The following `normal_mode` command calls `Editor::enter_normal_mode`.
6. Commands and editor helpers commonly assume a current view; after the final view is gone, tree access reaches an unreachable state and panics.

This is command-dispatch lifecycle ownership: the sequence runner owns whether later commands may execute after the editor becomes terminal.

### First discriminating experiment

Add a target-native command-dispatch test with a one-view editor and a two-command sequence:

1. a first command that closes the last view;
2. a second command instrumented to record whether it ran.

Required result: the editor exits cleanly, the second command does not run, and no panic occurs.

Controls:

- the same sequence with two views continues and runs the second command against the remaining view;
- a close command refused because of unsaved buffers does not terminate the sequence unless current command semantics already require that;
- a sequence that changes mode without closing a view still runs fully;
- macros and ordinary single-command key bindings retain current behavior;
- callbacks queued before terminal state are handled according to existing shutdown rules.

### Candidate repair boundary

Prefer a dispatcher-owned termination check between commands. Candidate forms include:

- make command execution return an explicit continuation/terminal result;
- inspect a stable editor exit or view-availability state after each command;
- centralize the check in the sequence runner so every command benefits.

Avoid scattering defensive `current view` checks through individual commands. That would miss future commands and hide lifecycle ownership.

### Stop condition

Stop and reframe if `wclose` is intended to defer final shutdown until after the complete key sequence. Current behavior and the single-command close path suggest immediate terminal state, but this must be proven in tests before selecting the final API.

### Promotion output

A promoted packet should contain:

- current exact master SHA;
- target-native failing dispatcher test;
- command sequence and final-window lifecycle map;
- comparison of explicit command result versus stable editor-state guard;
- controls for two-view, refused-close, macro, and callback behavior;
- focused and ordinary test receipts;
- fresh duplicate and branch sweep;
- concise proposed PR body;
- upstream-contact state, still `false` until separately authorized.

## Revalidation lane — GitButler upstream-integration transactionality

### Public records

- Main family: https://github.com/gitbutlerapp/gitbutler/issues/14848
- Related stale-parent wedge: https://github.com/gitbutlerapp/gitbutler/issues/14497
- Related rebase-engine assertion: https://github.com/gitbutlerapp/gitbutler/issues/14831

The reports describe serious state-generation divergence: branch refs and metadata can advance while the workspace commit remains old, or the target tree can advance while many clean worktree files retain superseded content.

### Why it is not promoted now

- Maintainer response asked for verification on current nightly because major fixes had landed after the reported release.
- Active pull requests overlap checkout and upstream-integration behavior, including conflict-marker materialization and stale-HEAD handling.
- The strongest reports were captured on `0.21.0`; current stable/nightly behavior has not been established in this round.

### Bounded next probe

Use a scratch repository with:

- one or more applied stacks;
- a dirty worktree containing a local edit in file `L`;
- an upstream base advance changing clean file `F` that no stack touches.

Capture before and after identities for:

- target/base commit and tree;
- `gitbutler/workspace` commit and parents;
- every applied stack head;
- persisted stack metadata;
- worktree blobs for `L` and `F`;
- oplog snapshot tree.

Required invariant: either the operation commits one coherent new generation across these authorities, or it fails while preserving the complete old generation. A mixed generation is the defect.

### Stop condition

Retire this lane if current nightly passes the dirty-worktree/base-advance matrix repeatedly and the relevant active repairs explain the old reports. Open a separate lead only for a reproducible current failure with a named transition boundary.

## Monitor lane — Rolldown raw-dev resolver cache invalidation

### Public record

- Issue: https://github.com/rolldown/rolldown/issues/10487

The report is technically strong: deleting a still-imported file produces a silent `Noop`, the running graph serves old content, and a cold restart reports `UNRESOLVED_IMPORT`. It also maps stale-positive and stale-negative cache directions and identifies the current whole-cache invalidation API.

### Why it is not promoted now

The failing desired-behavior test already exists on an upstream-owned branch in the Rolldown repository. Even without an open repair pull request, that branch is evidence of existing target ownership. Fieldwork should not create a competing source branch while that work is current.

### Recheck condition

Revisit only if the upstream branch becomes stale, is closed without a repair, or maintainers explicitly request an independent implementation or characterization.

## Exclusion ledger

The following attractive items were checked and excluded:

| Target | Public record | Exclusion reason |
| --- | --- | --- |
| GitButler | issue 12795 | merge-commit diff work has active PR 12796 and unresolved first-parent versus combined-diff policy |
| GitButler | issue 12748 | hook-manager coexistence has active PR 14698 |
| GitButler | issue 12750 | stale workspace HEAD report is closed completed |
| Rolldown | issue 10195 | re-entrant `this.load()` deadlock has active PR 10229 |
| Rolldown | issue 10407 | maintainers explicitly marked it on hold to stop contributors until import-attribute design is solved |
| Rolldown | issue 10504 | labeled upstream-owned; likely Babel/plugin transform boundary rather than a clean Rolldown repair |
| Rolldown | issue 10472 | reporter stated intent to take the plugin-attribution fix |
| Rolldown | issue 9175 | active PR 10445 |
| Helix | issue 16076 | diagnostic duplication already has PR 16071 |
| Helix | issue 16119 | grammar source and failure behavior were already repaired on master through earlier PRs |
| Helix | issue 15701 | contributor supplied root cause and stated intent to submit the completion repair |
| Helix | issue 15627 | active PR 16128 |
| Bevy | issue 25224 | active repair PR 25225 |
| Rspack | issues 14864 and 14865 | active repair PRs 14944 and 15034 |
| Wasmtime | WASI `initial-cwd` lead | current repair and older prior work already exist |
| rust-analyzer | macro-performance lead | current optimization pull request exists |

## Proposed execution order

1. Turborepo issue 13636: pin current head, add the four-way selector/affected fixture, and settle dependency-closure semantics.
2. Helix issue 16111: pin current master, add a one-view command-sequence test, and settle the dispatcher termination contract.
3. GitButler transactionality family: run current-nightly scratch-repository characterization before reading toward a repair.
4. Rolldown issue 10487: monitor upstream-owned test branch; do not compete.

## Disposition

Current disposition: `TWO PROMOTED LEADS; TWO REVALIDATION/MONITOR LANES`.

This round does not assign numbered upstream contribution units. A lead becomes a unit only after an owned Fieldwork packet pins the current target revision, retains a failing target-native test or complete issue-first evidence, performs a fresh duplicate sweep, and records an explicit implementation or issue-first disposition.
