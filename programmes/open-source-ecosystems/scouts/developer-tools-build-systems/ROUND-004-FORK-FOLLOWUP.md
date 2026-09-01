# Developer tools scout round 004 — owned-fork follow-up

Date: 2026-08-03  
Programme: #207  
Scout lane: #210  
Owner: `chatgpt:gpt-5.6-thinking`  
State: `owned-fork characterization and prototype design active`  
Claim scope: `mechanism`  
Upstream contact authorized: `false`

## In simple words

Turborepo and Helix are active owned-fork research lanes. Source reading, branch edits, test preparation, commit review, and Fieldwork notes proceed directly through GitHub.

A local checkout is only required for actual build and test execution. It is not required for continuing work in the forks.

Open upstream issues remain context. The research questions and controls now come from the target source, existing tests, and owned-fork experiments.

## Exact fork identities

### Turborepo

- repository: https://github.com/teamleaderleo/turborepo
- branch: `research/affected-filter-intersection`
- base: `c6fbc97bb8841f9c87d106af2d89ce11e97ea56c`
- head: `6d4785a34b70143f1ecc8fb9c19c161edb09a344`
- relation: `6 commits ahead, 0 behind`
- diff: three added integration-test files, `511 additions`
- production source changes: none

Current controls cover:

- direct package-filter intersection;
- `--parallel` engine rebuild;
- exclude-only selectors;
- same-name cross-package dependency closure;
- strict and legacy entrypoint behavior.

### Helix

- repository: https://github.com/teamleaderleo/helix
- branch: `research/final-window-command-sequence`
- base: `079a789e8cb08ead67f19e1971a1b7438b37354b`
- head: `87972f36c950169ed0caeaab5a5a60dcafa488cb`
- relation: `5 commits ahead, 0 behind`
- diff: one added integration-test module plus registration, `132 additions`
- production source changes: none

Current controls cover:

- single-command final close;
- insert-mode and normal-mode sequences after final close;
- ordinary non-closing sequence completion;
- two-view continuation;
- refused-close continuation.

## Current source conclusions

### Turborepo

The separate task-input affected path loses the original package-selected task roots when it builds and prunes an all-packages engine. Later code cannot distinguish an unwanted outside-package affected root from an outside-package task required by a selected root.

The repair candidate must retain selector-authorized roots and rebuild their task dependency closure. It must preserve strict-entrypoint feature gating.

### Helix

`MatchedSequence` executes every command during one key event. Removing the final view makes `Editor::should_close()` true, and the application loop uses that predicate to exit before another event. The sequence dispatcher does not check it before executing the next command.

The repair candidate is a central `should_close()` check after each complete command lifecycle.

## Durable records

- `ROUND-004.md` — original scout and source map;
- `ROUND-004-CHARACTERIZATIONS.md` — exact fork heads and test matrix;
- `ROUND-004-PROTOTYPE-DESIGNS.md` — candidate transitions and rejected approaches.

## Review state

Fieldwork PR #495 was rechecked on 2026-08-03:

- no independent review submission;
- no inline review thread;
- existing reviews are exact-head self-reviews.

## Next transitions

1. Continue source review for remaining controls.
2. Execute exact-head tests when target execution is available.
3. Record passing, failing, or compile/setup outcomes without inference.
4. Keep production source unchanged until the tests compile and distinguish the competing contracts.

No target pull request or public upstream interaction is authorized.
