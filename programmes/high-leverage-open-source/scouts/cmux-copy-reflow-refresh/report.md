# cmux copy reflow current-main refresh

Date: 2026-08-10  
Programme: high-leverage-open-source  
Upstream contact authorized: `false`

## In simple words

cmux still has an open copy bug where visually wrapped terminal text can paste with real newlines. There is already a serious upstream fix candidate, PR #6923, rather than an empty patch lane. Its author and reviewers worked through the copy semantics and regression matrix, and the current PR reports 94 focused reflow tests. The remaining visible blocker is that the branch drifted into conflicts with current `main` after the last maintainer pass.

This scout therefore does not invent a second reflow engine. It pins current cmux `main` and the existing PR head and runs a read-only Git merge audit to identify the exact refresh surface. A human or an owned fork can then refresh the existing candidate with less guesswork.

## Question

What is the exact current-main merge surface for the already-reviewed cmux copy-reflow candidate, and is there evidence of a remaining design blocker beyond branch drift?

## Exact upstream state

Repository: `manaflow-ai/cmux`  
Issue: https://github.com/manaflow-ai/cmux/issues/3096  
Existing candidate: https://github.com/manaflow-ai/cmux/pull/6923  
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

## Executable probe

Path: `programmes/high-leverage-open-source/scouts/cmux-copy-reflow-refresh/probe.sh`

The probe performs only read-only upstream operations:

1. initializes a temporary Git repository;
2. fetches the exact pinned current-main and candidate-head revisions from `manaflow-ai/cmux` with blob filtering;
3. invokes `git merge-tree --write-tree` on those exact revisions;
4. records whether Git can synthesize a merge and, on conflict, prints the exact conflict output and conflict paths.

The associated GitHub Actions workflow is `.github/workflows/cmux-copy-reflow-refresh.yml`.

## Claim-scoped evidence

- Upstream source, issue, PR, review threads: `source-read`.
- Current-main merge audit: `target-test-prepared` until the Fieldwork workflow executes this exact scout head.
- cmux GUI clipboard reproduction on the operator machine: observed in the surrounding operator session, but not yet retained as a Fieldwork execution receipt.
- Upstream submission or modification: absent and prohibited for Fieldwork agents.

## Current conclusion

The highest-value contribution lane is a **refresh and verification of the existing PR**, not a competing implementation.

If the merge audit shows a narrow conflict surface, the next useful artifact is a current-main refresh patch in an operator-owned fork or a human-performed rebase of the existing upstream branch, followed by the existing focused tests plus the original #3096 clipboard-byte reproduction.

If the conflict surface is broad or crosses rewritten clipboard architecture, re-evaluate the candidate against current source before carrying old integration glue forward. Keep the pure reflow regression corpus as reusable evidence even if the app glue changes.

## Stop condition

Stop this scout after the exact merge surface is executed and recorded. Do not post, comment, push, rerun, or otherwise mutate `manaflow-ai/cmux` from Fieldwork automation.
