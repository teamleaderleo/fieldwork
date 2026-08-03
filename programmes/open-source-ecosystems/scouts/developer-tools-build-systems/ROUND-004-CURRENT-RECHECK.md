# Developer tools scout round 004 — current target recheck

Date: 2026-08-03  
Programme: #207  
Scout lane: #210  
Owner: `chatgpt:gpt-5.6-thinking`  
State: `public-record recheck and owned-fork review characterization`  
Upstream contact authorized: `false`

## In simple words

Helix remains an unoccupied owned-fork implementation-research lane.

Turborepo now has an active upstream repair pull request. The owned fork therefore pivots from independent production implementation toward review characterization. A new test records a likely edge case in the proposed repair without commenting upstream.

## Turborepo public recheck

### Issue

- issue: https://github.com/vercel/turborepo/issues/13636
- state: open
- assignees: none
- comments: two
- latest issue update shown by GitHub: 2026-08-01

No new issue discussion appeared after the reproduction was supplied.

### Active repair

- pull request: https://github.com/vercel/turborepo/pull/13639
- title: `fix: Respect filters in task-level affected runs`
- state: open, ready for review, mergeable
- base: `c6fbc97bb8841f9c87d106af2d89ce11e97ea56c`
- head: `983e2a4aeb64d606072db369153826788c1e7e2a`
- author: `omidsaffari`
- requested reviewer: `tknickman`
- reviews: none at recheck
- inline review threads: none at recheck
- changed files: three
- additions: `114`

The visible GitHub workflow runs concluded `action_required`, and Vercel statuses show authorization failures. Those states do not provide a test verdict for the Rust repair.

## Upstream repair design

The proposed repair:

1. resolves explicit package filters again with package-level affectedness disabled;
2. performs task-input affected pruning;
3. calls `engine.task_ids_for_packages(scoped_packages)` on the already-pruned engine;
4. calls `retain_filtered_tasks` on those surviving package tasks.

The patch includes:

- an independent-package filter case;
- a selected app retaining an upstream build dependency.

This covers the original report and ordinary dependency closure.

## Likely review gap

`task_ids_for_packages` returns every surviving task node belonging to the selected packages. After `retain_affected_tasks`, a selected package can survive in the engine solely because one of its tasks is a dependency of an affected root in an outside package.

That dependency-support node is not proof that the selected package has an affected task root.

Potential false-positive transition:

1. `alpha#test` is directly affected;
2. `alpha#test` requires `beta#build`;
3. `beta` itself is unaffected;
4. `--filter=beta` should yield no work;
5. affected pruning retains `beta#build` only as support for `alpha#test`;
6. selecting every surviving beta task can reinterpret `beta#build` as a filtered root and retain it.

This is a source-derived review hypothesis. It has not been executed.

## Owned-fork review characterization

Turborepo fork:

- repository: https://github.com/teamleaderleo/turborepo
- branch: `research/affected-filter-intersection`
- base: `c6fbc97bb8841f9c87d106af2d89ce11e97ea56c`
- head: `665cab53b9f118faaf474a06c609905c62adbe2c`
- relation: `7 commits ahead, 0 behind`
- production changes: none

New file:

- `crates/turborepo/tests/affected_task_filter_unaffected_selected_test.rs`

The fixture makes `alpha` depend on `beta`. Only an alpha source file changes. `alpha#test` requires `beta#build` through `^build`. The command filters to beta and expects an empty task list.

```text
turbo run test --affected --filter=beta --dry=json
```

The test distinguishes affected selected roots from dependency-only nodes already present in the affected engine.

## Turborepo disposition

`PIVOT — ACTIVE UPSTREAM REPAIR REVIEW`

- Do not create a competing production implementation while PR #13639 is active.
- Retain and extend owned-fork tests as a review harness.
- No upstream comment or review is authorized.
- Recheck the PR before any further source claim.

## Helix public recheck

- issue: https://github.com/helix-editor/helix/issues/16111
- state: open
- assignees: none
- comments: zero
- matching open repair pull request found: none

Helix fork remains:

- branch: `research/final-window-command-sequence`
- head: `87972f36c950169ed0caeaab5a5a60dcafa488cb`
- production changes: none

## Helix disposition

`CONTINUE — OWNED-FORK IMPLEMENTATION RESEARCH`

The current source candidate remains a matched-sequence check of `Editor::should_close()` after each complete command lifecycle.

## Current boundary

No public issue comment, review, reaction, pull request, or other upstream interaction was made.
