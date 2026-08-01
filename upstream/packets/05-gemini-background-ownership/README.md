# Unit 05 — fix(core): transfer background shell cleanup ownership atomically

## In simple words

Gemini CLI creates a temporary `gemini-shell-*` directory and `bgpids.tmp` file before shell execution so the shell wrapper can record descendant process IDs. Foreground commands clean those resources when the tool invocation ends. Background commands need them until the real process exits, yet the original code returned a background result without giving any later component cleanup ownership.

This unit transfers one idempotent cleanup operation to the execution lifecycle only after that lifecycle accepts a still-pending background claim. The shell invocation remains the owner when the command finishes early, validation or spawn fails, backgrounding is declined, or a claim callback fails. The same transfer covers a foreground command moved into the background through the live UI. Re-entry, callback failure, stale execution identity, duplicate child terminal events, and immediate retry are covered by target-native tests.

The current source is clean and based on the public upstream head inspected on 2026-08-01. The identical six product/test file blobs passed focused target execution on the immediately preceding public base. The new current-head draft triggered only a skipped E2E launcher, so current-head ordinary gates remain open. Gemini CLI contribution policy also requires discussion through an existing issue before a pull request. Public issue #28392 remains open and has closed overlapping PRs. The useful next public action, once explicitly authorized, is an issue-first clarification on ownership semantics and overlap.

## Current disposition

`ISSUE FIRST`

Last verified: `2026-08-01`  
Worker: `GPT-5.6 Thinking`  
Priority-zero parent: [`teamleaderleo/fieldwork#435`](https://github.com/teamleaderleo/fieldwork/issues/435)  
Upstream contact authorized: `no`

## Contribution

- Target project: `google-gemini/gemini-cli`
- Proposed upstream destination: `google-gemini/gemini-cli:main`
- Proposed title: `fix(core): transfer background shell cleanup ownership atomically`
- Contribution synopsis: transfer temporary shell resource cleanup from the invocation to actual process-exit finalization only after an accepted background claim, while preserving creator cleanup for all failed, declined, foreground, and already-completed paths.
- Work class: `issue-first design` with a clean owned-fork source candidate

## Exact identities

- Public upstream base inspected: [`f47d6c6f7a1308d81f9f57acf7d279f0928c5249`](https://github.com/google-gemini/gemini-cli/commit/f47d6c6f7a1308d81f9f57acf7d279f0928c5249)
- Earlier executed public base: [`d55e366f6ab393e024c613d940fead3696d56eac`](https://github.com/google-gemini/gemini-cli/commit/d55e366f6ab393e024c613d940fead3696d56eac)
- Owned target fork: `teamleaderleo/gemini-cli`
- Canonical source branch: `fieldwork/unit-05-background-ownership-current-source`
- Canonical source head: [`f754eafde164420b43df5a58861d874cfb73acde`](https://github.com/teamleaderleo/gemini-cli/commit/f754eafde164420b43df5a58861d874cfb73acde)
- Canonical owned-fork draft: [`teamleaderleo/gemini-cli#19`](https://github.com/teamleaderleo/gemini-cli/pull/19)
- Fieldwork packet branch: `p0/435-unit-05-gemini-background-ownership`
- Fieldwork packet head: the current branch head; the exact final head is recorded in the latest unit 05 handoff on [`teamleaderleo/fieldwork#435`](https://github.com/teamleaderleo/fieldwork/issues/435) because a file cannot contain the SHA of the commit that contains itself.
- Current-base refresh carrier: [`teamleaderleo/gemini-cli#18`](https://github.com/teamleaderleo/gemini-cli/pull/18), merged internally to create `f754eafd…`
- Retained source generations: [`#11@c9a0ec7f`](https://github.com/teamleaderleo/gemini-cli/pull/11), [`#13@1c8a1982`](https://github.com/teamleaderleo/gemini-cli/pull/13), [`#17@417ce25a`](https://github.com/teamleaderleo/gemini-cli/pull/17)
- Retained characterization: [`#9@c0f5202d`](https://github.com/teamleaderleo/gemini-cli/pull/9), [`#14@1522d0ae`](https://github.com/teamleaderleo/gemini-cli/pull/14)
- Superseded execution or publisher carriers: [`Gemini #10`](https://github.com/teamleaderleo/gemini-cli/pull/10), [`#12`](https://github.com/teamleaderleo/gemini-cli/pull/12), [`#15`](https://github.com/teamleaderleo/gemini-cli/pull/15), [`#16`](https://github.com/teamleaderleo/gemini-cli/pull/16), [`Fieldwork #321`](https://github.com/teamleaderleo/fieldwork/pull/321), and [`Fieldwork #334`](https://github.com/teamleaderleo/fieldwork/pull/334)
- Canonical finding: [`Fieldwork #319`](https://github.com/teamleaderleo/fieldwork/issues/319), [`finding.md@c2f138d0`](https://github.com/teamleaderleo/fieldwork/blob/c2f138d00521077f94126b4e8c8ae763e55b95f9/findings/F319-gemini-background-temp-ownership/finding.md), and [`Fieldwork #320`](https://github.com/teamleaderleo/fieldwork/pull/320)

## Current code and tests

### Product code

- [`executionLifecycleService.ts@f754eafd`](https://github.com/teamleaderleo/gemini-cli/blob/f754eafde164420b43df5a58861d874cfb73acde/packages/core/src/services/executionLifecycleService.ts) — reserves one synchronous background claim, rejects re-entry, invokes the ownership callback, revalidates active identity, settles the result, and isolates start-listener failures.
- [`shellExecutionService.ts@f754eafd`](https://github.com/teamleaderleo/gemini-cli/blob/f754eafde164420b43df5a58861d874cfb73acde/packages/core/src/services/shellExecutionService.ts) — passes ownership callbacks through child and PTY registrations, finalizes process-exit cleanup best-effort, guards duplicate child exit, rolls back rejected history, and creates logs after accepted lifecycle ownership.
- [`shell.ts@f754eafd`](https://github.com/teamleaderleo/gemini-cli/blob/f754eafde164420b43df5a58861d874cfb73acde/packages/core/src/tools/shell.ts) — holds creator ownership, records accepted transfer and actual exit independently, cleans once after both have occurred, and creator-cleans every path without transfer.

### Target-native tests

- [`executionLifecycleService.backgroundClaim.test.ts@f754eafd`](https://github.com/teamleaderleo/gemini-cli/blob/f754eafde164420b43df5a58861d874cfb73acde/packages/core/src/services/executionLifecycleService.backgroundClaim.test.ts) — re-entry, throwing callback with immediate clean retry, callback-driven settlement, and start-listener isolation.
- [`shell-execution-process-exit-cleanup.test.ts@f754eafd`](https://github.com/teamleaderleo/gemini-cli/blob/f754eafde164420b43df5a58861d874cfb73acde/packages/core/src/services/shell-execution-process-exit-cleanup.test.ts) — exact-once claim, manual background ordering, real child exit cleanup, cleanup rejection, and child `error` followed by `close` exactly once.
- [`shell-background-temp-ownership-repair.test.ts@f754eafd`](https://github.com/teamleaderleo/gemini-cli/blob/f754eafde164420b43df5a58861d874cfb73acde/packages/core/src/tools/shell-background-temp-ownership-repair.test.ts) — exit-before-claim, accepted transfer, manual foreground-to-background transfer, and foreground creator ownership.

### Required generated or dependency files

- `not applicable`

## Changed-file fence

| Path | Role | Keep upstream? |
| --- | --- | --- |
| `packages/core/src/services/executionLifecycleService.ts` | production lifecycle claim semantics | yes |
| `packages/core/src/services/shellExecutionService.ts` | production shell adapter ownership and exit cleanup | yes |
| `packages/core/src/tools/shell.ts` | production temporary-resource owner | yes |
| `packages/core/src/services/executionLifecycleService.backgroundClaim.test.ts` | regression and adversarial lifecycle tests | yes |
| `packages/core/src/services/shell-execution-process-exit-cleanup.test.ts` | process-exit and ordering tests | yes |
| `packages/core/src/tools/shell-background-temp-ownership-repair.test.ts` | shell invocation ownership tests | yes |

The compare from public base `f47d6c6…` to source head `f754eafd…` contains exactly these six files. It contains no `.github` workflow, publisher, Fieldwork report, generated file, lockfile, or unrelated formatting change.

## Evidence summary

| Claim | Evidence class | Exact receipt | Limit |
| --- | --- | --- | --- |
| a short command requested as background retains `gemini-shell-*` on the base | `target-executed` | [`Gemini #9`](https://github.com/teamleaderleo/gemini-cli/pull/9), run [`30596117032`](https://github.com/teamleaderleo/gemini-cli/actions/runs/30596117032) | mocked execution; Linux-oriented path |
| accepted ownership transfer covers exit-before-claim, claim-before-exit, foreground fallback, child exit, cleanup rejection, and child error/close duplication | `target-executed` | [`Gemini #10` run `30624706086`](https://github.com/teamleaderleo/gemini-cli/actions/runs/30624706086), job `91137148865`; 121 passed, one existing skip | executed on public base `d55e366…`; focused/adjacent package slice |
| manual foreground-to-background transfer occurs before foreground result continuation | `target-executed` | [`Gemini #12` run `30629626006`](https://github.com/teamleaderleo/gemini-cli/actions/runs/30629626006), job `91152716494`; 123 passed, one existing skip | pinned Linux child-process path |
| claim re-entry, callback throw, stale identity, rejected publication, listener failure, and immediate retry are handled | `target-executed` | characterization [`30649820502`](https://github.com/teamleaderleo/gemini-cli/actions/runs/30649820502), job `91220038173`; repaired publisher [`30651009451`](https://github.com/teamleaderleo/gemini-cli/actions/runs/30651009451), job `91224012827`; 39/39 | no full target preflight; future callback side effects must stay bounded |
| current public delta has no overlap with the six unit files | `source-read` | compare `d55e366…f47d6c6…` and compare [`f47d6c6…f754eafd`](https://github.com/teamleaderleo/gemini-cli/compare/fieldwork/upstream-f47-background-ownership-base...fieldwork/unit-05-background-ownership-current-source) | current upstream may move after 2026-08-01 |
| current-head ordinary checks passed | `target-test-prepared` | [`Gemini #19`](https://github.com/teamleaderleo/gemini-cli/pull/19) triggered run `30674218875`, which skipped | current-head target execution remains open |

## Packet navigation

- [Deep dive](./DEEP_DIVE.md)
- [Approaches](./APPROACHES.md)
- [Tests and receipts](./TESTS.md)
- [Upstream issue draft](./UPSTREAM_ISSUE.md)
- [Upstream pull-request draft](./UPSTREAM_PR.md)
- [Review and human inspection guide](./REVIEW.md)

## Duplicate and prior-art result

- Search date: `2026-08-01`
- Current upstream issue checked: [`google-gemini/gemini-cli#28392`](https://github.com/google-gemini/gemini-cli/issues/28392), open
- Prior upstream PRs checked:
  - [`#28394`](https://github.com/google-gemini/gemini-cli/pull/28394), closed without merge; two-file `onExit` registration from request intent; automated review identified cleanup exposure before registration or spawn success
  - [`#28496`](https://github.com/google-gemini/gemini-cli/pull/28496), closed without merge and contained zero changed files
- Related source history checked: [`#25537`](https://github.com/google-gemini/gemini-cli/pull/25537), which introduced unique temporary directories as part of shell wrapping work
- Equivalent implementation found: `no`
- Relationship to prior work: `complementary refinement of the same open defect`; unit 05 adds accepted-transfer semantics, creator fallback, manual backgrounding, atomic claim handling, and exact-once exit behavior absent from the closed implementation.

## Remaining work

Complete in this order:

1. Repeat the duplicate and ownership search against the public head current at the time of action; verify issue #28392’s assignee/claim state and any replacement PR.
2. Run current-head target execution on `f754eafd…`: formatter, the three focused files plus adjacent shell/lifecycle suites, core build/typecheck, and preferably the target-declared `npm run preflight` on Node `~20.19.0`.
3. Obtain an eligible independent complete-diff review of the six-file source and this packet.
4. With explicit user authorization, comment on or update issue #28392 first, describing the ownership race and asking whether maintainers want the larger atomic transfer candidate.
5. Open a public PR only after maintainer direction, current checks, CLA readiness, and a fresh direct branch/rebase from the then-current upstream head.

## Blockers and limits

- Public contact authority remains absent.
- Current-head `f754eafd…` has no retained passing ordinary-check receipt; run `30674218875` skipped.
- Target `npm run preflight` has never been retained for this exact candidate generation.
- Independent final review remains absent; existing acceptances are builder/same-account or earlier-slice reviews.
- Public issue #28392 is open and another contributor stated they were working on it; both known public PR attempts are closed.
- PTY-specific duplicate terminal callbacks, cancellation/escalation ordering, Windows PID-directory allocation, and real deletion diagnostics remain bounded gaps.
- The source branch contains a merge commit used for internal current-base materialization. A future public branch should replay or rebase the three logical commits cleanly on the current upstream head.
- The target requires a linked issue, CLA compliance, and current contribution/AI-assistance policy review.

## Latest handoff

State: `ISSUE FIRST`  
Exact source head: `f754eafde164420b43df5a58861d874cfb73acde`  
Exact packet head: see the latest unit 05 comment on `teamleaderleo/fieldwork#435`  
Tests: predecessor-identical blobs passed 121 + 123 + 39 focused/adjacent controls with build/typecheck/format receipts; current-head E2E launcher skipped and no ordinary status was emitted  
Temporary machinery remaining: historical closed carrier branches and open superseded source PRs #11/#13/#17; none appear in canonical source diff  
Next worker action: run current-head gates, refresh public overlap, and seek independent review before requesting issue-contact authorization  
Public upstream interaction: `none`
