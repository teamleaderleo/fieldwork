# Upstream issue draft — clarify cleanup ownership for background shell temporary resources

Draft status: `not ready — current-head execution and fresh overlap check required`  
Public interaction authorized: `no`

Preferred destination: comment on the existing open issue [`google-gemini/gemini-cli#28392`](https://github.com/google-gemini/gemini-cli/issues/28392). Create a new issue only when maintainers request a separate report.

The text between the separators is the proposed public comment. It intentionally omits Fieldwork process links, owned-fork execution machinery, review IDs, and internal disposition language.

---

Thanks for reporting this. I reproduced the ownership gap and explored a candidate against a current `main` revision.

## Summary

The temporary `gemini-shell-*` directory needs to survive until actual process exit, but request intent alone does not identify the cleanup owner. There are two background transitions to cover:

1. a command launched with `is_background: true` after the delay is accepted; and
2. an active foreground command moved to the background later through the execution lifecycle UI.

A short command can also finish before the delayed background claim. In that case the invocation should keep creator cleanup responsibility because background ownership was never accepted.

## Reproduction

1. Start a short shell command with `is_background: true` and `delay_ms: 0`.
2. Let the execution finish before the delayed background claim settles.
3. Await the normal shell tool result.
4. Inspect the extracted `gemini-shell-*` directory.

Representative target-native setup:

```ts
const invocation = shellTool.build({
  command: 'true',
  is_background: true,
  delay_ms: 0,
});

const result = await invocation.execute({
  abortSignal: new AbortController().signal,
});
```

## Observed behavior

On the baseline behavior, the invocation’s `finally` skips cleanup because the request carried `is_background: true`, even though the process completed before lifecycle background ownership was accepted. The temporary directory remains.

The same ownership problem appears in the opposite direction when a command starts as foreground and is moved to the background later: cleanup must transfer before the original foreground result continuation runs.

## Expected behavior

Each temporary shell resource should have one cleanup owner after every transition:

- the invocation owns cleanup before an accepted background claim;
- successful background ownership transfers cleanup synchronously before result settlement;
- the component that observes actual process exit invokes cleanup;
- failed, declined, already-completed, or throwing claims leave cleanup with the invocation;
- duplicate terminal callbacks and cleanup failure cannot alter the primary execution result.

## Current source observation

`ShellToolInvocation.execute()` creates the temporary directory and PID file. `ShellExecutionService` observes child/PTY exit and owns background history/log publication. `ExecutionLifecycleService` knows whether an execution is still pending and can be accepted as backgrounded.

A candidate direction is to let lifecycle acceptance synchronously notify the invocation of ownership transfer, while the shell adapter invokes one idempotent process-exit cleanup callback. This keeps request intent separate from accepted ownership and covers both model-requested and manual foreground-to-background transitions.

## Candidate direction

The candidate I explored uses:

- a boolean-returning lifecycle background claim;
- a synchronous, bounded `onBackgroundClaim` callback after claim reservation and before result settlement;
- re-entry rejection and resolver/execution revalidation;
- one best-effort `onProcessExit` callback from child and PTY finalizers;
- creator fallback when transfer never succeeds;
- history rollback and no log creation on rejected claims;
- log publication after accepted lifecycle ownership and before the foreground promise continuation.

Focused controls cover:

- exit before claim;
- claim before exit;
- manual foreground-to-background transition;
- foreground cleanup;
- nested claim re-entry;
- throwing claim followed by immediate retry;
- claim callback completing the execution;
- one failing background-start listener;
- child `error` followed by real `close` exactly once;
- cleanup rejection preserving the process result.

Would maintainers prefer this accepted-transfer contract in one focused change, or a smaller initial fix limited to successful model-requested background execution?

## Compatibility and risks

- This changes internal lifecycle/service signatures and adds no user-facing option or output format.
- Claim callbacks need to remain synchronous, bounded, and limited to local ownership state; catching an exception cannot undo arbitrary external side effects.
- Linux child-process focused tests exist. PTY-specific terminal ordering, cancellation/escalation, and Windows behavior deserve explicit review or follow-up coverage.
- Existing temporary directories from prior releases require a separate cleanup policy.

## Evidence limits

- The local mechanism and candidate controls are exercised; production frequency and disk/inode impact were not measured.
- Current-head full repository preflight and broader platform execution must complete before a pull request.

## Versions and environment

- project commit inspected: `f47d6c6f7a1308d81f9f57acf7d279f0928c5249`
- executed predecessor base: `d55e366f6ab393e024c613d940fead3696d56eac`
- platform: Linux GitHub runner for retained focused tests
- runtime: retained carriers used Node 22; a submission candidate should rerun with the repository-supported Node version and `npm run preflight`
- relevant configuration: shell tool with interactive shell disabled in focused invocation tests; child-process adapter exercised for actual exit controls

## Additional context

- Existing issue: https://github.com/google-gemini/gemini-cli/issues/28392
- Closed earlier implementation: https://github.com/google-gemini/gemini-cli/pull/28394
- Closed zero-file attempt: https://github.com/google-gemini/gemini-cli/pull/28496

---

## Filing checklist

- [ ] Current upstream issue and PR search repeated immediately before posting.
- [ ] Existing issue #28392 remains open and has no active replacement implementation or current contributor coordination conflict.
- [ ] Reproduction and focused candidate tests rerun on a current public revision.
- [x] Severity and prevalence wording stays within evidence.
- [x] Private, internal, or evidence-only links removed from the public draft.
- [ ] Target issue/comment format and contribution policy rechecked.
- [ ] AI disclosure handled according to the project policy current at posting time.
- [ ] Exact user authorization to post this comment recorded.

## Internal posting note

The target contribution guide says contributors should locate or create an issue, receive maintainer direction, and link a pull request to that issue. Issue #28392 already supplies the public defect report. A future authorized action should comment there with the accepted-transfer distinction and ask whether the six-file atomic candidate is desired. Avoid opening a second issue unless maintainers request one.
