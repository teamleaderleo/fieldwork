# Approaches — Unit 05 background shell cleanup ownership

## In simple words

The selected direction treats cleanup as an ownership transfer tied to one accepted lifecycle transition. The shell invocation creates the temporary resource and keeps cleanup responsibility until the lifecycle service accepts background ownership. The component that observes actual process exit then runs the transferred cleanup operation.

Several smaller answers were explored or appeared in public prior work. Registering an exit callback as soon as the request says “background” misses early failures and manual backgrounding. Cleaning on the first background receipt can remove the PID file while descendants still need it. Polling or sweeping adds a second owner instead of repairing the missing handoff. The selected direction leads because it covers both execution orderings, rejected claims, live manual transitions, and duplicate terminal events with one explicit rule.

## Decision criteria

1. Every temporary resource has exactly one cleanup owner after each lifecycle transition.
2. Foreground, already-completed, failed, declined, and manual-background paths preserve their existing result semantics.
3. Cleanup occurs after actual process exit and cannot replace the primary execution result.
4. The candidate stays inside the shell invocation, shell adapter, and lifecycle claim boundary with a reviewable file fence.
5. Claim rejection and immediate retry leave no history, log, listener, or cleanup residue.
6. The direction can work for child and PTY adapters without a new global path registry.

## Selected approach

### Accepted lifecycle claim transfers one idempotent cleanup operation

- Design: the invocation provides `onBackgroundClaim` and `onProcessExit` callbacks. The lifecycle service reserves and accepts one background claim synchronously. The invocation records transfer only inside that accepted claim. The adapter invokes process-exit cleanup. Invocation `finally` handles every untransferred path.
- Owning boundary: creator = `ShellToolInvocation`; claim authority = `ExecutionLifecycleService`; actual-exit observer = `ShellExecutionService`.
- Evidence: source heads [`c9a0ec7f`](https://github.com/teamleaderleo/gemini-cli/commit/c9a0ec7f452ee9a3252661b78c230a1c7b5f9fcc), [`1c8a1982`](https://github.com/teamleaderleo/gemini-cli/commit/1c8a198295ecbd01971bb79f0ed6afed16e66dbf), [`417ce25a`](https://github.com/teamleaderleo/gemini-cli/commit/417ce25afdfd28cc4f6d0f1dcd5ad2686ec5e255), materialized on current base at [`f754eafd`](https://github.com/teamleaderleo/gemini-cli/commit/f754eafde164420b43df5a58861d874cfb73acde); target receipts in `TESTS.md`.
- Advantages:
  - separates request intent from accepted ownership;
  - covers model-requested and manual foreground-to-background transitions;
  - preserves creator fallback after early completion or failed claim;
  - allows actual exit to occur before or after transfer;
  - contains cleanup failure;
  - avoids a global temporary-path map;
  - makes re-entry and retry testable.
- Costs and risks:
  - adds an internal synchronous callback contract;
  - widens three service/invocation files and adds three focused test files;
  - future claim callbacks must remain bounded and reversible in local state;
  - PTY and Windows evidence remains thinner than child-process evidence.
- Remaining controls: current-head gate, target preflight, real PTY/cancellation/Windows disposition, independent complete-diff review, maintainer direction through the open issue.

## Viable alternatives

### ShellExecutionService owns a temporary-directory field directly

- Design: pass `tempDir` into background process metadata and delete it from adapter finalization.
- Why it remains plausible: it closely matches public issue #28392’s suggested solution and keeps deletion in the process manager.
- What it would improve: fewer callbacks and a concrete resource field.
- What it would widen or complicate: the service would need creator/transfer state for short completion, failed claim, foreground launch later moved to background, and PID-file/file-plus-directory cleanup. A path field alone still needs accepted transfer semantics.
- Exact discriminator: implement the field while requiring exit-before-claim, manual backgrounding, rejected callback, and immediate retry controls. The design must show who deletes resources when transfer never succeeds.
- Reopening trigger: maintainer preference for typed resource ownership records or a broader execution-resource registry.

### One lifecycle-level resource bag per execution

- Design: register cleanup resources with `ExecutionLifecycleService` and transfer/settle them transactionally with execution state.
- Why it remains plausible: generalizes ownership beyond shell temp files.
- What it would improve: reusable cleanup semantics for future execution resources.
- What it would widen or complicate: new generic API, ordering and failure policy for arbitrary resources, greater review cost, and speculative scope.
- Exact discriminator: another concrete execution resource needs the same semantics and can share a tested contract without weakening result precedence.
- Reopening trigger: maintainer request for a general lifecycle resource API.

### Narrow request-time `onExit` registration plus creator fallback

- Design: register an adapter exit callback for `is_background`, then ensure `finally` still cleans if registration or spawn fails.
- Why it remains plausible: close to closed upstream PR #28394 and smaller in file count.
- What it would improve: fixes successful model-requested background runs with modest code.
- What it would widen or complicate: manual backgrounding needs a second path; request-time registration can still transfer before lifecycle acceptance; callback cleanup and creator cleanup need exact race coordination.
- Exact discriminator: run the unit’s exit-before-claim, declined claim, manual transition, re-entry, and immediate retry controls against the smaller design.
- Reopening trigger: maintainers explicitly scope the issue to successful model-requested background execution and defer manual/atomic transitions.

## Executed losing approaches

### Public PR #28394: register cleanup from request intent

- Exact branch, patch, or commit: [`google-gemini/gemini-cli#28394@4b9f89ed`](https://github.com/google-gemini/gemini-cli/commit/4b9f89ed4cd283d6ae1f18dc1b4f87f372ab85cc)
- What ran: contributor reported core workspace tests; public automated review inspected the two-file patch.
- Result: closed without merge. The patch registered `ShellExecutionService.onExit(pid, callback)` before the delayed background result path and changed only `shell.ts` plus a mock.
- Why it lost: registration followed request intent rather than accepted lifecycle ownership; automated review identified cleanup exposure when spawn or pre-registration paths fail; the patch had no manual-background, exact-once, claim-rejection, or immediate-retry controls.
- Useful evidence retained: confirms maintainers’ existing `onExit` surface was considered, and demonstrates the appeal and boundary of a two-file repair.

### First atomicity repair generation

- Exact branch, patch, or commit: `c3e07b42d535ae6b3ad8e8faabb6a95e78193bec`
- What ran: focused and adjacent atomicity/lifecycle/process-exit/temp-ownership gates.
- Result: tests passed, but review `4830760086` returned `REPAIR`.
- Why it lost: rejected attempts opened asynchronous log deletion before lifecycle acceptance, allowing an immediate retry to race stale cleanup against its new log.
- Useful evidence retained: moved log creation after accepted lifecycle ownership and added the immediate clean retry control in final head `417ce25a…`.

### Characterization-only re-entry and callback-failure stack

- Exact branch, patch, or commit: [`Gemini #14@1522d0ae`](https://github.com/teamleaderleo/gemini-cli/commit/1522d0ae74acdb3ee71243829b8b1031565e3d54)
- What ran: 37/37 focused and adjacent tests in run [`30649820502`](https://github.com/teamleaderleo/gemini-cli/actions/runs/30649820502).
- Result: confirmed nested acceptance/start duplication and retained history/log publication after a throwing claim callback.
- Why it lost: test-only evidence; no production repair.
- Useful evidence retained: exact negative controls that distinguish the final atomic claim implementation.

## Rejected easy answers

### Cleanup on initial background receipt

- Temptation: delete when the tool returns “Command moved to background.”
- Why it is incomplete or unsafe: the real process and shell trap may still need the PID file; the receipt is earlier than actual exit.
- Negative control or source fact: actual-exit finalizers exist in child and PTY adapters; the resource exists to support process tracking through launch/exit.

### Keep using `is_background` in `finally`

- Temptation: add more request-flag branches.
- Why it is incomplete or unsafe: a short requested-background command can finish before claim, and a foreground request can become backgrounded later.
- Negative control or source fact: Gemini #9 baseline characterization and the manual transition test.

### Global sweeper or age-based deletion

- Temptation: periodically remove old `gemini-shell-*` directories.
- Why it is incomplete or unsafe: introduces unrelated age, liveness, path, and cross-process policy while leaving active ownership ambiguous.
- Negative control or source fact: one accepted transition and actual-exit observer already provide a bounded owner for new executions.

### Invocation polling after return

- Temptation: have the original invocation poll the process manager until exit.
- Why it is incomplete or unsafe: duplicates process lifecycle ownership and keeps invocation work alive after its public result.
- Negative control or source fact: `ShellExecutionService` already observes actual exit and publishes lifecycle completion.

### Delete immediately after requesting background

- Temptation: assume the PID file is finished once backgrounding is requested.
- Why it is incomplete or unsafe: request intent can be declined or race process/PID-file completion.
- Negative control or source fact: exit-before-claim and rejected-claim controls.

### Swallow callback throws and accept the claim anyway

- Temptation: keep backgrounding despite ownership callback failure.
- Why it is incomplete or unsafe: lifecycle would report background ownership while the creator still believes it owns cleanup, creating dual or missing ownership.
- Negative control or source fact: throwing callback leaves foreground state retryable and produces no start event.

## Prior upstream approaches

| Link | Approach | Status | Relationship to this unit |
| --- | --- | --- | --- |
| [`issue #28392`](https://github.com/google-gemini/gemini-cli/issues/28392) | transfer temp directory to the background process manager and remove on exit | open | same defect and desired outcome; issue-first coordination surface |
| [`PR #28394`](https://github.com/google-gemini/gemini-cli/pull/28394) | register `onExit` cleanup when request flag is background | closed, unmerged | narrower predecessor; unit adds accepted transfer and failure/transition controls |
| [`PR #28496`](https://github.com/google-gemini/gemini-cli/pull/28496) | intended fix for #28392 | closed, zero changed files | no implementation to reuse |
| [`PR #25537`](https://github.com/google-gemini/gemini-cli/pull/25537) | introduced unique temp directories and shell wrapping improvements | historical related work | source origin/context; cleanup lifetime remained open |

## Deferred adjacent work

- PTY real-terminal duplicate finalization — separate adapter execution gate
- cancellation and escalation cleanup ordering — overlaps execution termination ownership
- Windows PID-directory behavior — platform-specific source/execution gate
- orphan sweeper for directories created by older releases — separate policy and safety problem
- deletion failure telemetry — observability decision independent of ownership correctness
- background log retention and history limits — separate resource family

## Decision history

| Date | Exact inputs | Decision | Reason | Reopening trigger |
| --- | --- | --- | --- | --- |
| 2026-07-31 | finding #319, base `d55e366…`, characterization #9 | select explicit process-exit transfer | request flag lacks an actual-exit owner | supported adapter cannot invoke cleanup reliably |
| 2026-07-31 | source `c9a0ec7f…`, 121-test receipt | retain initial child-process transfer | both exit/claim orderings and creator fallback passed | manual background transition breaks ownership |
| 2026-07-31 | source `1c8a1982…`, 123-test receipt | add synchronous manual claim callback | transfer must precede foreground result continuation | target rejects callback API or ordering |
| 2026-07-31 | characterization `1522d0ae…` | require atomic claim repair | nested claim and throw could split lifecycle/publication state | lifecycle claim becomes intrinsically transactional elsewhere |
| 2026-07-31 | first atomicity head `c3e07b42…`, review `4830760086` | reject first generation | asynchronous rejected-log cleanup raced immediate retry | no same-PID retry or logs move to unique generation identity |
| 2026-07-31 | final stack `417ce25a…`, 39/39 receipt | accept content for peer review | log creation after acceptance and exact rollback close the race | independent review or current-head execution finds defect |
| 2026-08-01 | public `f47d6c6…`, source `f754eafd…`, issue/PR overlap search | disposition `ISSUE FIRST` | current source is clean; target policy and active open issue require direction; current-head gates remain open | issue closes with accepted equivalent repair or maintainers authorize direct PR |
