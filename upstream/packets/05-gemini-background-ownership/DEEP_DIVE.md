# Deep dive — Unit 05 background shell cleanup ownership

## In simple words

The shell tool creates a temporary directory before launching a command. The directory carries a PID file used by the shell wrapper while descendants start. Foreground execution has a simple owner: the invocation removes the directory when it finishes. Background execution crosses an ownership boundary because the invocation returns while the process keeps running.

The defect came from using request intent (`is_background`) as a cleanup decision. A command can finish before the delayed background claim, a foreground command can be moved into the background later, and the claim itself can fail or re-enter. Cleanup therefore needs an accepted lifecycle transition, not a request flag.

The selected implementation keeps creator ownership until `ExecutionLifecycleService.background()` reserves and accepts one pending execution. A synchronous `onBackgroundClaim` callback transfers the temporary resource before the foreground result continuation. Actual child or PTY exit invokes one best-effort cleanup callback. Rejected transfer leaves the creator responsible. The evidence covers the Linux child-process slice and the lifecycle state transitions; current-head ordinary execution, broader adapter/platform paths, and independent review remain open.

## Governing invariant

> Every temporary shell-execution resource has exactly one cleanup owner after each lifecycle transition. Ownership transfers only after one accepted background claim, and cleanup failure never replaces the execution result.

## Current behavior

Baseline behavior at public revision `d55e366f6ab393e024c613d940fead3696d56eac`:

- entrypoint: `ShellToolInvocation.execute()` in `packages/core/src/tools/shell.ts`
- state owner before launch: the shell invocation
- caller-visible result: a foreground result after exit, or an early background result after `ShellExecutionService.background()`
- side effects: create `gemini-shell-*`, create `bgpids.tmp`, wrap the command so descendant PIDs can be written, optionally publish background history and log output
- cleanup owner: invocation `finally` for foreground requests; no actual-exit owner for background requests
- persistence or publication boundary: background history/log publication occurs in `ShellExecutionService.background()`
- relevant ordering:
  - `is_background` schedules a delayed claim while the process can finish first;
  - live UI backgrounding can claim a command originally launched as foreground;
  - child `error` can precede `close`;
  - claim callbacks and start listeners can throw or re-enter;
  - rejected publication can be immediately retried.

The baseline `finally` skipped cleanup whenever the request carried `is_background: true`, even when lifecycle ownership never transferred. Conversely, a manual background transition occurred outside the shell invocation’s request flag, so creator cleanup could run after the foreground result settled despite an accepted live background claim.

## Source map

| Area | Exact path and symbol | Responsibility | Relevant tests |
| --- | --- | --- | --- |
| lifecycle claim | [`ExecutionLifecycleService.background()` and `canBackground()`](https://github.com/teamleaderleo/gemini-cli/blob/f754eafde164420b43df5a58861d874cfb73acde/packages/core/src/services/executionLifecycleService.ts) | reserve one claim, call ownership transfer synchronously, revalidate identity, settle result, emit start | [`executionLifecycleService.backgroundClaim.test.ts`](https://github.com/teamleaderleo/gemini-cli/blob/f754eafde164420b43df5a58861d874cfb73acde/packages/core/src/services/executionLifecycleService.backgroundClaim.test.ts) |
| shell adapter lifecycle | [`ShellExecutionService.execute()`, `runProcessExitCleanup()`, and `background()`](https://github.com/teamleaderleo/gemini-cli/blob/f754eafde164420b43df5a58861d874cfb73acde/packages/core/src/services/shellExecutionService.ts) | pass claim/exit callbacks to child and PTY registrations, finalize child exit once, stage/rollback history, start logs after acceptance | [`shell-execution-process-exit-cleanup.test.ts`](https://github.com/teamleaderleo/gemini-cli/blob/f754eafde164420b43df5a58861d874cfb73acde/packages/core/src/services/shell-execution-process-exit-cleanup.test.ts), [`executionLifecycleService.backgroundClaim.test.ts`](https://github.com/teamleaderleo/gemini-cli/blob/f754eafde164420b43df5a58861d874cfb73acde/packages/core/src/services/executionLifecycleService.backgroundClaim.test.ts) |
| temporary-resource owner | [`ShellToolInvocation.execute()`](https://github.com/teamleaderleo/gemini-cli/blob/f754eafde164420b43df5a58861d874cfb73acde/packages/core/src/tools/shell.ts) | create PID resources, retain creator ownership, transfer on accepted claim, clean after actual exit, creator-clean all untransferred paths | [`shell-background-temp-ownership-repair.test.ts`](https://github.com/teamleaderleo/gemini-cli/blob/f754eafde164420b43df5a58861d874cfb73acde/packages/core/src/tools/shell-background-temp-ownership-repair.test.ts) |
| baseline characterization | [`Gemini #9`](https://github.com/teamleaderleo/gemini-cli/pull/9) | short requested-background command finishes before claim and leaves directory on baseline | run [`30596117032`](https://github.com/teamleaderleo/gemini-cli/actions/runs/30596117032) |
| canonical finding | [`F319 finding`](https://github.com/teamleaderleo/fieldwork/blob/c2f138d00521077f94126b4e8c8ae763e55b95f9/findings/F319-gemini-background-temp-ownership/finding.md) | original ownership model, alternatives, receipts, limits | [`Fieldwork #319`](https://github.com/teamleaderleo/fieldwork/issues/319) and [`#320`](https://github.com/teamleaderleo/fieldwork/pull/320) |

## Reproduction or characterization

### Setup

- exact upstream revision: `d55e366f6ab393e024c613d940fead3696d56eac`
- environment: owned fork GitHub Actions, Node 22 for the characterization carrier; Linux runner
- fixture: existing `ShellTool` harness with a mocked execution that completes before the background delay settles
- characterization branch: `fieldwork/background-temp-ownership-d55-characterization`
- exact head: `c0f5202d6179979c7abc69d3f3659a3418b97323`
- workflow: [`30596117032`](https://github.com/teamleaderleo/gemini-cli/actions/runs/30596117032)

Representative invocation:

```text
ShellTool.build({ command: 'true', is_background: true, delay_ms: 0 })
```

### Baseline result

The execution completes before the delayed background transition. The normal tool result returns, while the extracted `gemini-shell-*` directory still exists. Teardown removes the retained directory so the test carrier remains clean.

This establishes the request-intent leak mechanism under the target harness. It does not measure production frequency or prove every OS adapter behaves identically.

### Candidate result

The candidate tests preserve two independent events:

1. actual process exit can be observed before ownership transfer;
2. ownership transfer can be accepted before actual exit.

Cleanup runs only when both events have occurred. If transfer never succeeds, invocation `finally` performs creator cleanup. The target-executed candidate receipts are detailed in `TESTS.md`.

## Failure model

### Requested background command finishes before claim

1. Confirmed: the invocation creates `tempDir` and `bgpids.tmp`.
2. Confirmed: `is_background` schedules backgrounding after a delay.
3. Confirmed: the command can settle before that delay.
4. Confirmed baseline: `finally` sees the request flag and skips deletion.
5. Confirmed: lifecycle ownership was never accepted, so no actual-exit cleanup owner exists.
6. Result: the temporary directory remains.

### Requested background command remains running

1. The invocation creates temporary resources and remains their owner.
2. `ShellExecutionService.background()` checks that the lifecycle execution is pending.
3. It stages history, then calls `ExecutionLifecycleService.background()`.
4. The lifecycle reserves the claim and synchronously invokes `onBackgroundClaim`.
5. The invocation records transfer before the background result is resolved.
6. The lifecycle revalidates the same resolver and execution object, settles the background result, and emits one start event.
7. The shell service creates background logging before the foreground promise continuation.
8. Actual exit invokes `onProcessExit`; the invocation cleans once.

### Manual foreground-to-background transition

1. The command starts without `is_background` and creator cleanup remains armed.
2. A live UI action invokes `ShellExecutionService.background(pid, ...)`.
3. The lifecycle claim synchronously calls `onBackgroundClaim` before resolving the foreground result as backgrounded.
4. Invocation `finally` sees transferred ownership and keeps the PID resources.
5. Actual exit performs cleanup.

### Rejected or hostile claim

1. `canBackground()` confirms the resolver/execution exist and no claim is already active.
2. The shell service snapshots existing background history and provisionally adds the running record.
3. The lifecycle places the execution ID in `backgroundClaims`.
4. Re-entry sees the claim reservation and returns `false`.
5. A callback throw is caught; the reservation is released; ownership stays foreground and retryable.
6. Callback-driven completion changes resolver/execution identity; revalidation rejects the claim.
7. On rejection, the shell service restores the exact history snapshot and creates no log stream or file.
8. An immediate retry starts from clean state.

## Consequence and claim boundary

### Established

- The baseline request-flag cleanup rule can leave a temporary directory after a short requested-background command completes under the target harness.
- The candidate gives the creator and actual-exit path one explicit transfer boundary.
- Foreground, exit-before-claim, claim-before-exit, declined claim, callback throw, callback-driven settlement, manual backgrounding, cleanup rejection, and child `error` followed by `close` have target-native controls.
- Rejected claim attempts restore history and avoid log creation, allowing an immediate clean retry.
- The current public delta from `d55e366…` to `f47d6c6…` changes no unit file; the current source compare remains exactly six files.

### Inferred

- Long-lived sessions that repeatedly use successful background shell execution can accumulate temporary directories under the baseline. Public issue #28392 reports this operational consequence, while Fieldwork execution proves the local mechanism rather than prevalence.
- Giving actual-exit finalization the cleanup callback is a stronger owner match than registration from request intent because it covers manual transitions and failed transfer.

### Unknown or unmeasured

- Production frequency, accumulated disk/inode impact, and A2A usage prevalence.
- Windows behavior around temporary directory allocation and child process tracking.
- PTY duplicate callback and terminal ordering under real terminal implementations.
- Cancellation, termination escalation, and abrupt CLI death.
- Whether maintainers prefer the six-file atomic ownership change or a smaller repair after current architectural review.
- Current-head test behavior until `f754eafd…` receives retained target execution.

## Selected implementation

### Ownership boundary

The shell invocation owns the resource because it creates the directory and knows whether transfer occurred. `ExecutionLifecycleService` owns acceptance because it knows whether the execution is still pending and can settle as backgrounded. `ShellExecutionService` owns actual adapter exit and therefore calls the transferred cleanup operation.

This division avoids a global path map and avoids making log/history state the resource owner.

### New states and transitions

At the invocation:

- `tempCleanupTransferred = false` initially;
- `processExitObserved = false` initially;
- accepted claim sets `tempCleanupTransferred = true`;
- adapter exit sets `processExitObserved = true`;
- when both become true, one memoized cleanup promise removes the file and directory;
- invocation `finally` cleans whenever transfer stayed false.

At lifecycle scope:

- `backgroundClaims` contains execution IDs whose synchronous claim callback is active;
- `canBackground()` requires active resolver, active execution, and no active claim;
- callback throw or identity change returns `false` without settlement;
- accepted claim resolves once and emits start listeners independently.

At shell-service scope:

- history is staged before the synchronous claim so observers see the record during settlement;
- the exact prior history snapshot is restored when the claim rejects;
- log file/stream creation occurs only after lifecycle acceptance and before the promise continuation;
- child finalization checks `exited` before cleanup, publication, lifecycle completion, and transferred cleanup.

### Error and cleanup precedence

- claim callback failure rejects only the background transition and leaves the foreground execution live;
- process-exit cleanup rejection is logged and cannot replace the process result;
- listener failure is isolated after accepted ownership;
- repeated cleanup calls share one promise;
- destructive cleanup remains best-effort, matching existing shell cleanup behavior.

### Unchanged behavior

- foreground result data and normal foreground cleanup;
- shell command wrapping and PID parsing;
- background output/history contract after an accepted claim;
- no public API or wire contract changes outside internal TypeScript service signatures;
- no dependency, generated, lockfile, CLI flag, or documentation change.

## Compatibility analysis

- public API: internal service API changes; no documented end-user API change
- source compatibility: internal callers of `ExecutionLifecycleService.background()` and `ShellExecutionService.background()` now receive a boolean; ignoring the return remains valid TypeScript/JavaScript behavior, while internal tests and relevant call sites were updated
- binary or wire compatibility: `not applicable`
- persistence or format compatibility: background history/log formats remain unchanged
- platform behavior: candidate code uses existing `fsPromises.unlink/rm`; target execution is Linux-focused; Windows evidence remains open
- performance and allocation: one closure and memoized promise per shell invocation; one temporary set membership during claim; history snapshot copies at most the service’s bounded 100 records during manual/background publication
- cancellation, retry, and recovery: callback throw leaves the execution retryable; immediate retry control passes; cancellation/escalation interaction remains unexecuted
- generated output: `not applicable`
- migration or rollback: revert the three logical commits or the six-file diff; existing temporary directories from earlier runs require separate cleanup policy and are outside this candidate

## Adversarial and edge controls

- re-entry: nested lifecycle claim returns `false`; one start event
- concurrency: one claim reservation per execution; distinct executions remain independent
- cancellation or interruption: outside retained execution for this unit
- failure before ownership transfer: creator `finally` cleans
- failure after partial effect: history snapshot restores exactly; log setup happens after acceptance
- cleanup failure: caught after process result; result stays authoritative
- same-key or same-resource collision: immediate retry uses the same PID and verifies no stale history/log state
- unrelated-resource isolation: history rollback restores the pre-existing session map rather than clearing unrelated records
- platform or runtime boundary: Linux child process executed; PTY and Windows require separate receipts

## Review risks

1. **The callback runs inside the lifecycle claim and can perform irreversible work.** Current registrations only flip invocation-local state. The lifecycle catches throws, yet it cannot undo arbitrary future callback effects. Review should enforce the documented requirement that claim callbacks stay synchronous, bounded, and claim-local.
2. **History staging precedes acceptance.** The exact map snapshot is restored on rejection, and log creation follows acceptance. Review should check nested calls and unrelated session entries.
3. **Cleanup runs after lifecycle completion for child exit.** The callback is best-effort and result-independent. Review should decide whether observability of deletion failure belongs in the same contribution.
4. **PTY and child adapters share the callback contract but received unequal real execution.** The PTY source path calls cleanup from its terminal finalizer; a real PTY duplicate/failure control remains valuable.
5. **The candidate is larger than closed PR #28394.** The larger scope addresses request-intent registration, manual backgrounding, failed claims, exact-once finalization, and retry atomicity. Maintainer direction should decide whether this full contract fits one PR.
6. **Current source history contains an internal merge commit.** The six-file diff is clean; a public branch should replay the three logical commits or squash onto the then-current upstream head.

## Reversing evidence

The conclusion should be reopened if:

- current upstream source already transfers the PID directory through another owner;
- maintainers define request intent as sufficient ownership and accept cleanup before actual lifecycle acknowledgement;
- a supported adapter needs `bgpids.tmp` after actual process exit;
- target-native current-head tests expose ordering, log, history, or listener regressions;
- a real PTY or Windows control shows the callback cannot run safely at terminal exit;
- an equivalent active public PR supersedes this implementation;
- project maintainers request a narrower `onExit` registration after accepting its failure boundaries.

## Adjacent work excluded

- old-version orphan-directory sweeper or age policy
- PID parsing completeness and malicious path replacement
- background log retention and history eviction policy
- remote-agent executions that bypass this shell wrapper
- asynchronous termination ownership and cancellation escalation
- general lifecycle callback transaction semantics beyond current bounded registrations
- cleanup of resources created by already-released Gemini CLI versions
