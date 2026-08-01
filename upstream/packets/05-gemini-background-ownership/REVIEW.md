# Review — Unit 05 background shell cleanup ownership

## In simple words

The proposed contribution gives Gemini CLI temporary shell PID resources one cleanup owner across foreground execution, model-requested backgrounding, manual backgrounding, failed claims, and actual process exit.

A fresh assistant instance reviewed the complete six-file source diff at exact head `f754eafde164420b43df5a58861d874cfb73acde`. The review found no source defect. GitHub blocks an `APPROVE` event on a pull request authored by the same repository account, so the accepted disposition is retained as review comment `4834163401` on `teamleaderleo/gemini-cli#19`, following the owner’s explicit rule that a fresh instance is a fresh reviewing pass.

Current-head focused execution and `npm run preflight` remain required before a public pull request. They are execution gates, not review blockers for issue-first preparation.

## Review subject

- Work class: `issue-first design` with clean owned-fork source
- Target repository: `google-gemini/gemini-cli`
- Inspected public base: `f47d6c6f7a1308d81f9f57acf7d279f0928c5249`
- Canonical source branch: `fieldwork/unit-05-background-ownership-current-source`
- Exact source head: `f754eafde164420b43df5a58861d874cfb73acde`
- Canonical owned draft: [`teamleaderleo/gemini-cli#19`](https://github.com/teamleaderleo/gemini-cli/pull/19)
- Source review receipt: review `4834163401`
- Fieldwork packet branch: `p0/435-unit-05-gemini-background-ownership`
- Exact packet head: recorded in the latest unit 05 handoff on [`teamleaderleo/fieldwork#435`](https://github.com/teamleaderleo/fieldwork/issues/435)
- Upstream-contact authority: `no`

## Complete changed-file fence

| Path | Review result |
| --- | --- |
| `packages/core/src/services/executionLifecycleService.ts` | accepted: claim reservation, re-entry fence, callback containment, identity revalidation, listener isolation |
| `packages/core/src/services/shellExecutionService.ts` | accepted: callback plumbing, once-only child finalization, history rollback, accepted-log timing |
| `packages/core/src/tools/shell.ts` | accepted: creator/transfer/exit state machine and memoized cleanup |
| `packages/core/src/services/executionLifecycleService.backgroundClaim.test.ts` | accepted: hostile claim transitions and immediate retry controls |
| `packages/core/src/services/shell-execution-process-exit-cleanup.test.ts` | accepted: real child exit, manual transfer ordering, duplicate terminal event, result precedence |
| `packages/core/src/tools/shell-background-temp-ownership-repair.test.ts` | accepted: four primary resource-ownership paths |

## Review findings

### Accepted ownership model

- `ShellToolInvocation` creates the temporary resource and keeps creator cleanup authority.
- `ExecutionLifecycleService.background()` reserves one claim and runs `onBackgroundClaim` synchronously.
- Callback throw rejects the claim and leaves the still-pending execution retryable.
- Callback activity that settles or replaces the execution rejects the claim while preserving the resulting execution state.
- Re-entry is denied while one claim owns the execution ID.
- The same resolver and execution object are revalidated before background settlement.
- `ShellExecutionService` restores the prior history map when a claim is rejected.
- Log streams and files are created only after accepted lifecycle ownership, in the same synchronous turn before promise continuations.
- Child `error` followed by `close` is fenced before command cleanup, terminal publication, lifecycle completion, and transferred cleanup.
- Actual exit and ownership transfer can arrive in either order; one memoized cleanup operation runs after both.
- Manual foreground-to-background transfer uses the same lifecycle claim path.

### Packet correction made during review

The first packet generation said a callback that “throws or settles/replaces” the execution leaves the foreground execution retryable. Only the throwing case is retryable. Settlement or replacement preserves the resulting execution state. `UPSTREAM_PR.md` now states this accurately.

### No source defect found

The complete current diff supports the stated ownership invariant. The review found no repair required inside the six-file fence.

## Evidence judgment

| Claim | Evidence class | Judgment |
| --- | --- | --- |
| request intent can suppress creator cleanup without accepted background ownership | `target-executed` | accepted on retained baseline characterization |
| exit-before-claim, claim-before-exit, foreground fallback, child exit, cleanup rejection, and duplicate child terminal events | `target-executed` | accepted on 121-test generation |
| manual foreground-to-background ownership transfer precedes result continuation | `target-executed` | accepted on 123-test generation |
| re-entry, callback throw, stale identity, rejected publication, listener failure, and immediate retry | `target-executed` | accepted on 39/39 final atomicity generation |
| current public delta leaves all six unit files unchanged | `source-read` | accepted for current-base materialization |
| current exact head passed target gates | `target-test-prepared` | pending; source draft’s E2E launcher skipped |
| Fieldwork packet integrity | `full-gate` for Fieldwork integrity only | passed run `30674853320` on packet head `8a9cba7…`; rerun required after this review update |

## Remaining execution and promotion gates

1. Run the exact source head or a clean replay of the same six-file content through formatter, focused and adjacent tests, core build/typecheck, and `npm run preflight` on the repository-supported Node version.
2. Refresh the public head, issue `#28392`, contributor claim state, and replacement-PR search immediately before contact.
3. Record a final PTY, cancellation/escalation, and Windows disposition through execution or explicit maintainer-approved bounds.
4. Receive explicit user authority for one issue-first public interaction.
5. Create a clean public branch from the then-current upstream head after maintainer direction.

## Source cleanliness

- [x] Three product files and three target-native test files only.
- [x] No Fieldwork files, temporary workflows, publishers, or receipts in the source diff.
- [x] No unrelated formatting, generated output, snapshot, or dependency churn.
- [x] Commit-pinned source and test links resolve to `f754eafd…`.
- [ ] Public submission history replayed directly onto the current upstream head.

## Draft judgment

- [x] Issue-first route matches the existing open issue and target policy.
- [x] Public drafts keep impact and prevalence within evidence.
- [x] PR draft describes the actual six-file source.
- [x] Internal process links are excluded from the proposed public text.
- [x] Source received a fresh-instance complete-diff review.
- [ ] Current-head execution results inserted.
- [ ] Current overlap and contributor coordination refreshed.
- [ ] Public interaction authorized.

## Reviewer disposition

`ACCEPT`

Reviewed source head: `f754eafde164420b43df5a58861d874cfb73acde`  
Reviewed packet generation: original packet head `8a9cba7a99cb7925b905f22127bd203aab86adac`, plus the review correction commits on the same packet branch  
Review receipt: `teamleaderleo/gemini-cli#19` review `4834163401`  
Reason: the complete six-file diff preserves one cleanup owner through the demonstrated lifecycle transitions, and the packet accurately bounds the remaining execution and platform gaps after the wording repair.  
Accepted transition: `ISSUE FIRST` preparation in owned repositories.  
Clearing condition for public PR preparation: exact-head target execution, fresh public overlap, platform disposition, maintainer direction, and explicit contact authority.  
Reviewer eligibility: `fresh-instance review accepted under repository-owner instruction`; GitHub account-level self-approval is technically blocked.

## Current contribution disposition

`ISSUE FIRST`

The review gate is cleared. The remaining blockers concern execution, current public coordination, platform bounds, and authority.
