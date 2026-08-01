# Review — Unit 05 background shell cleanup ownership

## In simple words

The proposed contribution gives Gemini CLI’s temporary shell PID resources one explicit cleanup owner across foreground execution, model-requested backgrounding, manual backgrounding, failed claims, and actual process exit. The selected code is clean and current-base relative, and its identical file content has strong focused execution on the immediately preceding public base.

A final reviewer should challenge three things above all: whether the synchronous claim callback is the right internal contract, whether history/log publication is fully atomic around rejected and re-entrant claims, and whether the evidence justifies one six-file contribution before real PTY/cancellation/Windows execution. Current-head ordinary gates and independent acceptance remain open, so this review records `EXECUTE / ISSUE FIRST`, not submission readiness.

## Review subject

- Work class: `issue-first design` with clean owned-fork source
- Target repository: `google-gemini/gemini-cli`
- Proposed upstream base: public `main`; inspected exact base `f47d6c6f7a1308d81f9f57acf7d279f0928c5249`
- Canonical source branch: `fieldwork/unit-05-background-ownership-current-source`
- Exact source head: `f754eafde164420b43df5a58861d874cfb73acde`
- Canonical owned draft: [`teamleaderleo/gemini-cli#19`](https://github.com/teamleaderleo/gemini-cli/pull/19)
- Fieldwork packet branch: `p0/435-unit-05-gemini-background-ownership`
- Exact packet head: current branch head recorded in the latest unit 05 handoff on [`teamleaderleo/fieldwork#435`](https://github.com/teamleaderleo/fieldwork/issues/435)
- Complete changed-file fence: three product files and three target-native test files listed below
- Upstream-contact authority: `no`

## Review reading order

1. [`README.md`](./README.md)
2. [`DEEP_DIVE.md`](./DEEP_DIVE.md)
3. [`APPROACHES.md`](./APPROACHES.md)
4. [`TESTS.md`](./TESTS.md)
5. [exact product/test compare](https://github.com/teamleaderleo/gemini-cli/compare/fieldwork/upstream-f47-background-ownership-base...fieldwork/unit-05-background-ownership-current-source)
6. [`UPSTREAM_ISSUE.md`](./UPSTREAM_ISSUE.md)
7. [`UPSTREAM_PR.md`](./UPSTREAM_PR.md)
8. public issue and prior approaches: [`#28392`](https://github.com/google-gemini/gemini-cli/issues/28392), [`#28394`](https://github.com/google-gemini/gemini-cli/pull/28394), [`#28496`](https://github.com/google-gemini/gemini-cli/pull/28496)

## Exact diff links

- complete compare: [`f47d6c6…f754eafd`](https://github.com/teamleaderleo/gemini-cli/compare/fieldwork/upstream-f47-background-ownership-base...fieldwork/unit-05-background-ownership-current-source)
- production files:
  - [`executionLifecycleService.ts`](https://github.com/teamleaderleo/gemini-cli/blob/f754eafde164420b43df5a58861d874cfb73acde/packages/core/src/services/executionLifecycleService.ts)
  - [`shellExecutionService.ts`](https://github.com/teamleaderleo/gemini-cli/blob/f754eafde164420b43df5a58861d874cfb73acde/packages/core/src/services/shellExecutionService.ts)
  - [`shell.ts`](https://github.com/teamleaderleo/gemini-cli/blob/f754eafde164420b43df5a58861d874cfb73acde/packages/core/src/tools/shell.ts)
- tests:
  - [`executionLifecycleService.backgroundClaim.test.ts`](https://github.com/teamleaderleo/gemini-cli/blob/f754eafde164420b43df5a58861d874cfb73acde/packages/core/src/services/executionLifecycleService.backgroundClaim.test.ts)
  - [`shell-execution-process-exit-cleanup.test.ts`](https://github.com/teamleaderleo/gemini-cli/blob/f754eafde164420b43df5a58861d874cfb73acde/packages/core/src/services/shell-execution-process-exit-cleanup.test.ts)
  - [`shell-background-temp-ownership-repair.test.ts`](https://github.com/teamleaderleo/gemini-cli/blob/f754eafde164420b43df5a58861d874cfb73acde/packages/core/src/tools/shell-background-temp-ownership-repair.test.ts)
- generated or dependency files: `not applicable`

## Complete changed-file fence

| Path | Review purpose |
| --- | --- |
| `packages/core/src/services/executionLifecycleService.ts` | claim reservation, callback ordering, identity revalidation, listener isolation |
| `packages/core/src/services/shellExecutionService.ts` | adapter callback plumbing, once-only child finalization, history rollback, log timing |
| `packages/core/src/tools/shell.ts` | creator/transfer/exit state machine and one cleanup promise |
| `packages/core/src/services/executionLifecycleService.backgroundClaim.test.ts` | hostile claim transitions and same-PID retry |
| `packages/core/src/services/shell-execution-process-exit-cleanup.test.ts` | actual child exit, manual transition ordering, duplicate terminal callback, result precedence |
| `packages/core/src/tools/shell-background-temp-ownership-repair.test.ts` | invocation resource lifetime across four primary ownership paths |

## Claims requiring judgment

| Claim or design choice | Evidence | Reviewer question |
| --- | --- | --- |
| ownership should transfer on lifecycle acceptance rather than request intent | baseline #9, public PR #28394 diff/review, invocation tests | Does every supported background entrypoint pass through the chosen claim authority? |
| `onBackgroundClaim` must run synchronously before result settlement | manual ordering test and lifecycle source | Could any current caller require asynchronous transfer, or can callback scope remain local and bounded? |
| callback throw should reject backgrounding and permit retry | atomicity test and `backgroundClaims` source | Does any side effect occur before the throw that exact rollback cannot reverse? |
| resolver/execution identity must be revalidated after callback activity | callback-settlement test | Are there other mutable lifecycle identities or generation tokens that require comparison? |
| history may be staged before claim and restored on rejection | exact snapshot source and immediate-retry test | Does restoring a copied map preserve unrelated concurrent/same-session activity under JavaScript event ordering? |
| logs should be created after lifecycle acceptance but before promise continuation | final repair and retry regression | Can any synchronous listener or continuation observe accepted background state before the log stream exists? |
| one `exited` guard should protect generic process-exit cleanup | deterministic child error/close test | Does PTY finalization have an equivalent duplicate guard or need one? |
| cleanup rejection stays secondary to execution result | service test and `runProcessExitCleanup` | Should deletion failure receive stronger telemetry or a retained diagnostic without changing result precedence? |
| six files belong in one contribution | complete compare and approach history | Would maintainers review lifecycle atomicity and temp ownership together, or prefer a staged issue/PR sequence? |
| current base replay is semantically unchanged | no-overlap compare and exact six-file current diff | Does current `main` introduce behavior outside these files that changes the test assumptions? |

## Known risks

- Future `onBackgroundClaim` registrations could perform irreversible work before throwing. Current code comments and review must keep callbacks synchronous and claim-local.
- A session history snapshot copies the current map and restores it on rejected claims. Review event-loop ordering and same-session re-entry carefully.
- PTY cleanup callback invocation exists in source, while the retained actual-exit proof focuses on child processes.
- Current source history includes an internal merge commit. Public history needs a clean replay/rebase after maintainer direction.
- Public issue #28392 remains open; another contributor stated work had begun. Closed PR #28394 overlaps the defect and #28496 is a zero-file attempt. Fresh coordination is essential.
- The candidate has no retained exact-head `npm run preflight` receipt.

## Evidence limits

- Current exact head `f754eafd…`: source-read current-base relation; E2E launcher skipped; no ordinary checks.
- Executed file content: Linux GitHub runners on predecessor base; focused/adjacent package scope.
- Full repository preflight, lint, integration/E2E, real PTY, cancellation/escalation, Windows, abrupt CLI death, and long-duration leak measurement remain absent.
- Existing self/same-account reviews cannot provide eligible independent final acceptance.
- Operational prevalence and severity beyond the local mechanism come from the public report and remain unmeasured here.

## Staleness check

- Current upstream head checked: `f47d6c6f7a1308d81f9f57acf7d279f0928c5249` on `2026-08-01`
- Candidate base relationship: `f754eafd…` contains public base `f47d6c6…`; compare is six files, four commits
- Relevant source paths changed upstream since execution: `no` between executed base `d55e366…` and inspected public head `f47d6c6…`
- Duplicate/overlap search date: `2026-08-01`
- Open replacement work found: issue #28392 remains open; no open equivalent PR found in the search; closed #28394 and #28496 reviewed
- Packet and target PR descriptions synchronized: `yes` for exact heads, file fence, evidence class, and current gate as of packet completion

## Source cleanliness

- [x] No Fieldwork-only files in target source diff.
- [x] No temporary workflows or publishers in target source diff.
- [x] No stale execution artifacts in target source diff.
- [x] No unrelated formatting or generated churn.
- [x] Required snapshots or lock changes are `not applicable`.
- [x] Commit-pinned links resolve to source head `f754eafd…`.
- [ ] Public submission history is a clean direct replay/rebase of current upstream rather than the internal merge commit.

## Test review

- [x] Intended assertions ran on the executed predecessor-identical blobs.
- [x] Baseline/candidate relationship is explicit.
- [x] Setup, fixture, runner, review, and product failures are separated.
- [x] Claim failure, rejection rollback, actual-exit cleanup, duplicate terminal callbacks, and cleanup-result precedence are covered.
- [x] Foreground and adjacent lifecycle/shell compatibility controls are present.
- [x] Platform and integration limits are explicit.
- [x] Ordinary target gates are named accurately.
- [ ] Current-head focused/adjacent execution passed.
- [ ] Current-head `npm run preflight` passed.

## Draft review

- [x] Issue draft keeps impact and prevalence within evidence.
- [x] PR draft describes the actual six-file current diff.
- [x] Target terminology and issue-first contribution route are used.
- [x] Proposed public text omits internal process vocabulary and private context.
- [x] AI disclosure is marked for filing-time policy review.
- [ ] Maintainer direction and exact user authority exist.

## Self-review disposition

`EXECUTE`

Reviewed source head: `f754eafde164420b43df5a58861d874cfb73acde`  
Reviewed packet head: current packet branch generation; exact final head recorded on issue #435  
Reason: the current diff is clean, current-base relative, and supported by strong predecessor-identical target execution. Exact current-head ordinary gates, full preflight, and independent complete-diff acceptance remain absent. Target policy and active public issue make issue-first direction the correct promotion route.  
Clearing condition: execute the exact current head through focused/adjacent tests, core build/typecheck, formatter, and `npm run preflight`; refresh public overlap; then obtain independent complete-diff review before seeking authorization for an issue #28392 comment.  
Reviewer eligibility: `self-review only`

## Current contribution disposition

`ISSUE FIRST`

This contribution should remain private to owned repositories until the execution and review clearing condition passes and the user authorizes one exact public issue interaction.

## Human deep-dive guide

The final human reviewer should focus on:

1. whether synchronous accepted-claim callbacks are the smallest durable ownership contract;
2. whether rejected claim rollback fully preserves unrelated history/log state and immediate retry;
3. whether actual-exit cleanup is exact-once across both child and PTY adapters;
4. whether the target would prefer one six-file atomic patch or a staged narrower repair after issue discussion;
5. whether current-head preflight and platform evidence support public preparation.

Suggested response:

`Unit 05 looks ready for issue-first upstream preparation after the named execution gate`  
—or—  
`Unit 05 concern: <specific source, test, compatibility, overlap, or framing issue>`
