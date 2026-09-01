# Developer tools scout round 004 — continuation 005

Date: 2026-08-05  
Programme: #207  
Scout lane: #210  
Owner: `chatgpt:gpt-5.6-thinking`  
State: `upstream resolution recorded; merged-fix controls retained; exploration continues`  
Upstream contact authorized: `false`

## In simple words

The first Turborepo repair was not stale. It was opened on 2026-08-02 and closed without merge on 2026-08-04 after roughly forty-five hours. The maintainer called the implementation incorrect.

A maintainer replacement was opened nineteen minutes later and merged within the hour. That replacement directly implements the provenance rule identified by the owned-fork review: package scope is applied to affected entrypoints before upstream execution dependencies are restored.

The obsolete owned review pull request is closed. The remaining distinct tests now sit directly on top of the merged repair in a clean fork-local verification pull request.

Helix remains a separate active research lane.

## Turborepo resolution

### Rejected repair

- upstream pull request: https://github.com/vercel/turborepo/pull/13639
- opened: `2026-08-02T15:28:25Z`
- closed without merge: `2026-08-04T12:24:57Z`
- maintainer disposition: implementation described as incorrect and closed

This was an active but short-lived attempt, not an abandoned queue item.

### Merged replacement

- upstream pull request: https://github.com/vercel/turborepo/pull/13656
- opened: `2026-08-04T12:44:26Z`
- merged: `2026-08-04T13:43:12Z`
- merge commit: `0b1f46670fc4ea8687416549fb583585846c80a5`

The merged repair:

1. computes directly affected tasks and their affected dependents;
2. intersects those affected entrypoints with package scope;
3. expands `with` siblings;
4. restores only required upstream execution dependencies;
5. derives reported packages from selected affected entrypoints.

Its target-native tests explicitly include the dependency-only false-positive case under `test_task_level_affected_filter_does_not_promote_execution_dependency`.

The previously recorded review hypothesis is therefore addressed by current upstream main.

## Owned Turborepo records

### Superseded review PR

- pull request: https://github.com/teamleaderleo/turborepo/pull/2
- state: closed without merge
- reason: its base was the rejected upstream implementation

The branch and test remain historical evidence only.

### Merged-fix verification PR

- pull request: https://github.com/teamleaderleo/turborepo/pull/3
- base branch: `review-base/13656`
- base revision: `0b1f46670fc4ea8687416549fb583585846c80a5`
- head branch: `verify/13656-round-004-controls`
- head revision: `7294960909691cc1888ef155d0cd9a05fb9e604c`
- production changes beyond merged upstream: none
- changed files: three target-native integration-test files

Distinct controls retained beyond the merged repair tests:

- `--parallel` engine rebuild;
- exclude-only package selectors;
- same-name cross-package task dependency closure;
- legacy non-strict entrypoint behavior;
- explicit strict entrypoint behavior.

These controls are prepared and unexecuted. No remaining Turborepo defect is claimed.

## Turborepo next transition

1. Treat the original selector/affectedness defect as resolved upstream.
2. Execute the five retained compatibility controls when a target runner is available.
3. If they pass, close the verification lane as a negative result and select a fresh source-derived question.
4. If one fails, record exact command and output before considering upstream contact.

## Helix continuation

The Helix lane remains active at:

- repository: https://github.com/teamleaderleo/helix
- branch: `research/final-window-command-sequence`
- head: `87972f36c950169ed0caeaab5a5a60dcafa488cb`
- owned draft pull request: https://github.com/teamleaderleo/helix/pull/1

Current candidate contract:

> A matched command sequence stops after a completed command lifecycle when `Editor::should_close()` becomes true.

The current tests remain prepared and unexecuted. Further source exploration should examine adjacent command-sequence lifecycle state rather than widening the patch into per-command missing-view guards.

## Current boundary

No public upstream issue comment, pull-request review, reaction, or new upstream pull request was created.
