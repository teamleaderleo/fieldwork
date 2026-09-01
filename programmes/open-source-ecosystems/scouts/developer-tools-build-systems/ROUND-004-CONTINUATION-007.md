# Developer tools scout round 004 — continuation 007

Date: 2026-08-05  
Programme: #207  
Scout lane: #210  
Owner: `chatgpt:gpt-5.6-thinking`  
State: `executed Helix replay defects; clean owned review surfaces; Turborepo execution pending`  
Upstream contact authorized: `false`

## In simple words

The deeper Helix pass established three real replay defects beyond the active upstream command-sequence repair. The fork was then cleaned so only one test review pull request and one execution-only carrier remain.

Several temporary production-candidate trigger pull requests and default-branch workflow experiments were closed or removed because they did not produce a source commit. Helix `master` is restored to its upstream workflow content.

Turborepo's package-qualified task precedence question remains queued for target-native execution. Its likely source boundary is documented without a defect claim.

## Helix durable evidence

Canonical owned review:

- repository: https://github.com/teamleaderleo/helix
- pull request: https://github.com/teamleaderleo/helix/pull/3
- base: upstream repair head `85e9b90b66e614e10ace01f50e03d5abc0908b1d`
- head: `4b750d6db183c199f648ff1079b7cf1eac59e57c`
- changed files: one test module plus integration registration
- production changes: none

Executed run:

- workflow: `Build`
- run: `30981560017`
- failing job: `92226916213`
- workspace tests: passed
- integration result: `183 passed; 3 failed`

Confirmed failures:

- configured keymap macro dispatch after final-view close;
- recorded-register macro dispatch after final-view close;
- counted dot-repeat after its first replay closes the editor.

Each reaches the empty-view tree panic at `helix-view/src/tree.rs:327:18`.

Passing controls establish that replay must continue while another view remains and stop only after an actual terminal transition.

## Helix candidate boundary

The source-owned candidate remains:

1. break configured macro key replay after `Editor::should_close()`;
2. break recorded macro key and count replay after `Editor::should_close()`, then clear replay state;
3. break counted last-insert replay after `Editor::should_close()`, then clear command count.

The candidate was encoded in an execution-only workflow with exact replacement uniqueness checks, formatting, focused integration tests, workspace tests, and a two-file diff fence.

Canonical execution carrier:

- pull request: https://github.com/teamleaderleo/helix/pull/2
- base: `execution-base/16136-replay`
- head branch: `execution/final-window-command-sequence`
- head: `b52e0c96130d78ddf1cba3d3ebb6a359fb63b5b4`
- carrier diff: one temporary workflow only
- production changes: none

The workflow has not produced a new candidate receipt in this pass. The absence of a source commit is recorded rather than treated as passing evidence.

## Helix cleanup

Closed without merge:

- `teamleaderleo/helix#4` — experimental workflow-driven source candidate;
- `teamleaderleo/helix#5` — duplicate execution carrier;
- `teamleaderleo/helix#6` — clean workflow-trigger experiment.

The fork default branch was restored:

- `.github/workflows/build.yml` matches the upstream fork content again;
- temporary default-branch replay workflows were removed.

The canonical review branch was reset to exact executed test head `4b750d6db183c199f648ff1079b7cf1eac59e57c`.

## Turborepo current state

Owned verification:

- repository: https://github.com/teamleaderleo/turborepo
- pull request: https://github.com/teamleaderleo/turborepo/pull/3
- merged-fix base: `0b1f46670fc4ea8687416549fb583585846c80a5`
- head: `e8bdd25fdf7db5de27b33524d215f6fad5fbd429`
- production changes: none

Focused workflow:

- run: `30981301116`
- job: `92226109918`
- state at record time: queued

The matrix includes:

- parallel package-filter composition;
- exclude-only package filters;
- same-name dependency closure;
- strict and legacy entrypoint policies;
- package-qualified task authority across `filterUsingTasks` and `affectedUsingTaskInputs`.

The probable source boundary for package-qualified task inclusion is documented in `ROUND-004-TURBOREPO-PACKAGE-TASK-DESIGN.md`. Execution must distinguish the two paths before a production edit.

## Current disposition

- Helix replay defects: `EXECUTED / CONFIRMED`.
- Helix production candidate: `DESIGNED / NOT EXECUTED`.
- Turborepo package-task question: `EXECUTION QUEUED`.
- Public upstream interaction: `false`.

No result is claimed beyond the exact receipts above.
