# cmux copy reflow current-main refresh

Date: 2026-08-10  
Programme: high-leverage-open-source  
Upstream contact authorized: `false`

## In simple words

cmux still has an open copy bug where visually wrapped terminal text can paste with real newlines. There is already a serious upstream fix candidate, PR #6923, rather than an empty patch lane. Its author and reviewers worked through the copy semantics and regression matrix, and the current PR reports 94 focused reflow tests.

The Fieldwork probe executed against current cmux `main` and the existing candidate head. Git can auto-merge every touched source, settings, localization, workspace, and workflow surface. The **only merge conflict is `cmux.xcodeproj/project.pbxproj`**. The existing candidate is therefore still a viable refresh target; it is not presently blocked by a broad source-code conflict.

## Question

What is the exact current-main merge surface for the already-reviewed cmux copy-reflow candidate, and is there evidence of a remaining design blocker beyond branch drift?

## Exact upstream state

Repository: `manaflow-ai/cmux`  
Issue: https://redirect.github.com/manaflow-ai/cmux/issues/3096  
Existing candidate: https://redirect.github.com/manaflow-ai/cmux/pull/6923  
Current-main revision pinned for this scout: `e49e7cdf300ad6eff38aef21145cd1183636e76c`  
Candidate head pinned for this scout: `1516fc0c2e64bc21772b88738377f360c53cea03`

At inspection time:

- issue #3096 remained open;
- PR #6923 remained open and was reported by GitHub as not mergeable;
- the PR discussion explicitly records that checks were green on its current head but the branch had become conflicting against `main` after the July 16 maintainer pass;
- the PR author offered to rebase the existing branch rather than replace it;
- all currently listed review threads were resolved;
- the candidate's own description reports 94 focused `CmuxCopyReflow` tests after later review repairs.

## Source-confirmed boundary

cmux now uses its `manaflow-ai/ghostty` fork rather than the old SwiftTerm backend referenced in the original issue triage note.

The current Ghostty selection C API documents clipboard-equivalent formatting as plain output with both `unwrap` and `trim` enabled. In other words, Ghostty already intends ordinary terminal soft-wrap boundaries to disappear during native clipboard formatting.

PR #6923 describes its extra reflow layer as addressing residual application-emitted hard wrapping, terminal padding, paragraph reconstruction, and related copied-output cases after Ghostty selection text is obtained. That is a broader problem than simply toggling Ghostty's soft-wrap unwrapping.

## Existing candidate quality signal

The upstream review history is unusually useful rather than ceremonial. The candidate was iterated against concrete failures including:

- wrapped command continuations beginning with flags and paths;
- shell pipes versus Markdown table detection;
- URL continuation spacing;
- preservation of Ghostty mixed clipboard representations;
- rectangular selection ambiguity in the current Ghostty C ABI;
- large-input table scanning complexity;
- deterministic correctness tests instead of wall-clock assertions;
- historical terminal-width padding versus authored Markdown hard breaks.

The latest visible threads for these findings are resolved. No unresolved review thread currently demonstrates a remaining functional rejection of the reflow idea.

## Executed merge probe

Path: `programmes/high-leverage-open-source/scouts/cmux-copy-reflow-refresh/probe.sh`  
Retained receipt: `execution-receipt-31373822591.json`

Exact execution:

- Fieldwork head executed: `fe0d804a2ab69271f5a70478e551ab81079e4f56`;
- workflow run: `31373822591`;
- target current-main: `e49e7cdf300ad6eff38aef21145cd1183636e76c`;
- candidate head: `1516fc0c2e64bc21772b88738377f360c53cea03`;
- `git merge-tree --write-tree` exit: `1`;
- result: not directly mergeable;
- exact conflict file: `cmux.xcodeproj/project.pbxproj`.

Git auto-merged the other touched surfaces reported by the merge, including `Sources/GhosttyTerminalView.swift`, settings and shortcut files, the workspace file, schema/localization files, and the copy candidate's related workflow/test surfaces.

The merge-tree receipt therefore narrows the current refresh problem to Xcode project-file integration. It does not prove the refreshed application builds or that the GUI clipboard path passes #3096 after rebasing; those remain the next execution gates.

## Claim-scoped evidence

- Upstream source, issue, PR, review threads: `source-read`.
- Exact current-main merge surface: `target-executed` through workflow run `31373822591`.
- cmux GUI clipboard reproduction on the operator machine: observed in the surrounding operator session, but not retained as a Fieldwork execution receipt.
- Refreshed candidate build/test on current main: absent.
- Upstream submission or modification: absent and prohibited for Fieldwork agents.

## Current conclusion

The highest-value contribution lane is a **refresh and verification of the existing PR**, not a competing implementation.

The current-main conflict is narrow: only `cmux.xcodeproj/project.pbxproj`. A human or operator-owned fork can rebase/refresh the existing candidate, resolve that project-file conflict deliberately, then run the existing focused reflow suite and the original #3096 clipboard-byte reproduction. The pure Swift reflow code and its reviewed source integration did not conflict in the merge audit.

This is enough to stop the scout. A new lane should be opened only for an owned-fork refresh, current-main build/test execution, or retained end-to-end GUI clipboard proof.

## Stop condition

Satisfied. The exact merge surface was executed and recorded. Do not post, comment, push, rerun, or otherwise mutate `manaflow-ai/cmux` from Fieldwork automation.
