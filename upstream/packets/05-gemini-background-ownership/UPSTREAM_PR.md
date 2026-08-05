# Upstream pull-request draft — fix(core): transfer background shell cleanup ownership atomically

Draft status: `issue first`  
Proposed head: `teamleaderleo/gemini-cli:fieldwork/unit-05-background-ownership-current-source` at `f754eafde164420b43df5a58861d874cfb73acde` for review only; create a freshly rebased/replayed public head after maintainer direction  
Proposed base: `google-gemini/gemini-cli:main`; inspected base `f47d6c6f7a1308d81f9f57acf7d279f0928c5249`  
Public interaction authorized: `no`

The text between the separators is the proposed public pull-request body. Replace bracketed current-gate lines with exact results from the final public candidate before filing.

---

## Summary

- Transfer temporary shell PID-resource cleanup only after one accepted background lifecycle claim.
- Keep creator cleanup for foreground, already-completed, failed, declined, or rejected claims, including an immediate retry after callback failure.
- Run transferred cleanup once from actual child/PTY exit without replacing the execution result.

Fixes #28392.

## Problem

`ShellToolInvocation` creates a temporary `gemini-shell-*` directory and `bgpids.tmp` file before shell execution. The PID file must remain available while a background process starts and runs, so foreground-style cleanup cannot happen when the invocation returns an early background result.

The old cleanup decision followed the original `is_background` request flag. That leaves two ownership gaps:

1. a short requested-background command can finish before the delayed background claim, leaving the creator cleanup suppressed even though lifecycle ownership never transferred;
2. a foreground command can be moved into the background later, allowing the original invocation to clean the PID resources when its result settles while the process remains active.

The invariant is one cleanup owner after each transition: the invocation owns the resource until one still-pending execution is accepted as backgrounded, then actual process-exit finalization owns cleanup.

## Change

### Lifecycle claim

`ExecutionLifecycleService.background()` now returns whether one background claim was accepted. It reserves the execution ID while a synchronous `onBackgroundClaim` callback runs, rejects re-entry, catches callback failure, and revalidates the same resolver and execution object before settling the background result.

A callback that throws rejects backgrounding and leaves the still-pending foreground execution retryable. Callback activity that settles or replaces the execution also rejects the background claim while preserving that resulting execution state. Background-start listeners run independently after acceptance so one failing listener cannot undo ownership.

### Shell adapter

`ShellExecutionService` passes `onBackgroundClaim` and `onProcessExit` callbacks through child and PTY lifecycle registrations. Child finalization guards `error` followed by `close` before command cleanup, terminal publication, lifecycle completion, and transferred resource cleanup.

`ShellExecutionService.background()` preflights lifecycle eligibility, snapshots and stages background history, and invokes the lifecycle claim. Rejection restores the exact prior history. Background log streams/files are created only after lifecycle acceptance and before the original promise continuation, avoiding rejected-attempt residue and immediate-retry races.

### Temporary resource owner

`ShellToolInvocation` creates one memoized cleanup operation. It records two independent events:

- accepted background ownership transfer;
- actual process exit.

Cleanup runs once when both events have occurred. Invocation `finally` runs cleanup whenever transfer never succeeds, preserving foreground and early-completion behavior.

## Tests

Focused target-native tests cover:

- short requested-background execution completing before claim;
- exit-before-claim and claim-before-exit orderings;
- manual foreground-to-background transfer before result continuation;
- foreground creator cleanup;
- exact-once lifecycle claim;
- nested claim rejection;
- throwing claim with clean immediate retry;
- callback-driven execution settlement;
- failing background-start listener isolation;
- rejected history/log rollback;
- child actual-exit cleanup;
- cleanup rejection preserving the execution result;
- child `error` followed by awaited real `close` finalizing once.

Retained focused execution on the predecessor public base produced:

- initial ownership generation: 121 passed, one existing skip, package build, core typecheck, and formatting;
- manual-background generation: 123 passed, one existing skip, package build, core typecheck, and formatting;
- final atomicity generation: 39/39 focused and adjacent tests, package build, core typecheck, and formatting.

The current public-base delta touched none of the changed files. Before submission, record the exact final candidate results here:

- `[current-head focused tests: pending]`
- `[npm run preflight: pending]`
- `[platform/PTY disposition: pending]`

## Compatibility

- public API: no documented user-facing API change; internal service methods gain callback fields and boolean claim results
- existing behavior retained: foreground execution, output, background history/log format, and successful background result content
- platform or runtime notes: existing filesystem APIs are used; Linux child-process execution is covered; PTY and Windows need explicit final disposition
- performance or allocation notes: one closure and memoized promise per invocation, one temporary claim-set entry, and a snapshot of a background history map bounded to 100 records during publication
- migration or rollback: revert the six-file change; stale directories created by older releases remain a separate cleanup-policy question

## Alternatives considered

- Register cleanup from `is_background` request intent: smaller, but misses manual backgrounding and can transfer before lifecycle acceptance.
- Pass only `tempDir` into background metadata: still needs creator fallback and accepted-transfer semantics for early completion and rejected claims.
- Delete on the first background receipt: can remove the PID file before actual process exit.
- Poll from the invocation: duplicates process lifecycle ownership after the invocation returns.
- Sweep old temporary directories: introduces unrelated age/liveness policy and leaves new execution ownership ambiguous.

## Limits

- Real PTY duplicate/error/abort ordering is outside the retained child-process execution.
- Cancellation and termination escalation interaction remains separate.
- Windows temporary directory and process tracking behavior needs explicit review or execution.
- Cleanup deletion remains best-effort; this change does not add user-visible deletion diagnostics.
- Claim callbacks must stay synchronous, bounded, and limited to local ownership state.

## Related work

- #28392
- #28394
- #28496

---

## Submission checklist

- [ ] Maintainer direction received on issue #28392.
- [ ] Branch is replayed or rebased directly onto the public head current at submission time; internal merge commit removed from public history.
- [x] Current owned source diff contains only three product files and three target-native test files.
- [x] Fieldwork wording, temporary workflows, publishers, receipts, and evidence-only files are absent from the target source diff.
- [x] Every changed file received a fresh-instance complete-diff review at exact source head `f754eafde164420b43df5a58861d874cfb73acde`; retained review `teamleaderleo/gemini-cli#19` review `4834163401`.
- [x] Focused baseline/candidate relationship is retained for the request-intent leak and adversarial claim paths.
- [ ] Formatter, focused tests, adjacent suites, core build/typecheck, and `npm run preflight` pass at the exact public candidate head.
- [ ] Current PTY/cancellation/Windows gaps are executed or accepted as bounded follow-up by maintainers.
- [ ] Current duplicate and overlap search repeated; contributor claim on issue #28392 reconciled.
- [ ] Commit history and title checked against current target conventions.
- [ ] CLA status and current contribution/AI-disclosure policies checked.
- [ ] Exact user authorization to open the pull request recorded.
