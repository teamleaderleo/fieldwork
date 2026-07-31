# Gemini background shell temporary-resource ownership

Finding ID: `F319-gemini-background-temp-ownership`  
Finding state: `research-active`  
Owning issue: #319  
Programme: #14  
Target hub: #5  
Exact target source: `google-gemini/gemini-cli@d55e366f6ab393e024c613d940fead3696d56eac`  
Strongest evidence class: `source-read`  
Current disposition: `REPAIR`  
Non-delegable human decision: `none`  
Upstream contact authorized: `no`

## In simple words

The shell tool makes a temporary `gemini-shell-*` directory so an exit trap can record child process IDs. Foreground commands delete it. A request marked background deliberately skips that deletion because the file is still needed until the real shell exits.

The component that later sees the real exit never receives the directory or a cleanup operation. The temporary resource therefore has no owner after the shell tool returns its initial background receipt.

The selected repair transfers one idempotent cleanup operation to the execution service after process start. The shell tool keeps cleanup authority whenever that transfer never succeeds.

## Why this matters

Repeated background commands can accumulate directories and inode usage in the system temporary area. The same missing ownership also makes cancellation, short-lived background requests, and spawn failure harder to reason about because the request flag—not the actual lifecycle transition—currently decides cleanup.

This is a resource-lifecycle finding. It is separate from:

- whether kill requests wait for confirmed termination;
- background log retention;
- child-process termination and escalation;
- PID discovery correctness.

## Governing invariant

Every temporary execution resource has exactly one cleanup owner after each lifecycle transition.

- The creator owns cleanup before process start.
- A resource needed until actual exit transfers to the component that observes actual exit.
- Transfer failure leaves cleanup with the creator.
- Cleanup failure never replaces the primary execution outcome.
- Repeated terminal callbacks do not repeat destructive cleanup.

## Current source map

### Resource creation

`packages/core/src/tools/shell.ts` creates a directory with:

```ts
fs.mkdtempSync(path.join(os.tmpdir(), 'gemini-shell-'))
```

It stores `bgpids.tmp` inside that directory and wraps POSIX commands with an exit trap that writes `jobs -p` to the file.

### Foreground ownership

The invocation `finally` block removes the file and directory only when `is_background` is false.

### Background transition

For a background request, `ShellExecutionService.background(pid, sessionId, command)` receives process identity, session identity, and display command. It receives no temporary path or cleanup callback.

The initial execution result is settled when the process moves to background. It is not an actual-exit receipt, so attaching cleanup to that promise would delete the PID file too early.

### Actual exit owner

PTY and child-process finalizers already own actual-exit work:

- output settlement;
- background history updates;
- terminal/process map cleanup;
- background log stream cleanup;
- lifecycle completion.

Those finalizers have no shell-tool temporary-resource input.

### Short background requests

A command requested with `is_background: true` can finish during the delay and avoid the early background return. Its invocation `finally` still skips cleanup based on the request flag. This means the problem is broader than long-running process backgrounding.

### Windows boundary

The PID wrapper returns the command unchanged on Windows, yet the directory and file path are still created. The selected implementation should avoid creating the unused resource on Windows when that can be done without widening the repair. Otherwise, Windows avoidance remains a named follow-up.

## Evidence table

| Claim | Evidence class | Exact support | Limit |
| --- | --- | --- | --- |
| shell invocation creates the temporary directory and PID path | `source-read` | `packages/core/src/tools/shell.ts` at `d55e366...` | no target execution yet |
| background requests skip invocation cleanup | `source-read` | invocation `finally` guard | retained directory not yet measured in target test |
| background transition receives no cleanup owner | `source-read` | `ShellExecutionService.background()` signature and body | another hidden owner could still exist; search found none |
| actual exit finalizers clean other execution resources | `source-read` | PTY and child-process finalization paths | cleanup ordering still needs execution |
| short background requests share the gap | `inferred from source ordering` | request-flag cleanup guard plus completion-during-delay path | target-native control required |

## Alternatives compared

### A — transfer one process-exit cleanup operation

**Selected.** Pass a narrow sync-or-async cleanup callback or equivalent owned resource through `ShellExecutionConfig` into the process finalizer.

Advantages:

- matches the component that observes actual exit;
- supports PTY and child-process paths;
- handles long and short background requests;
- keeps foreground behavior stable;
- makes transfer success testable;
- avoids global deletion policy.

Cost:

- every terminal path must invoke best-effort cleanup exactly once;
- the invocation needs an explicit transfer flag for pre-start failures.

### B — attach cleanup to the initial execution result

**Rejected.** `ExecutionLifecycleService.background()` resolves that promise before actual exit. The PID file may still be needed by the shell exit trap.

### C — let the shell invocation poll the process and clean later

**Rejected.** The invocation has already returned and would duplicate process lifecycle ownership, error handling, and cancellation races.

### D — periodic global sweeper or age-based deletion

**Rejected as the first repair.** It delays cleanup, hides ownership defects, introduces age and safety policy, and cannot distinguish a live PID file from an abandoned one without recreating lifecycle knowledge.

### E — delete immediately after the background transition

**Rejected.** The shell may not have exited and written child PIDs yet.

## Selected implementation contract

1. Create one idempotent cleanup closure for the file and directory.
2. Keep creator ownership initially.
3. For background requests, provide the closure to the execution service before or during successful process registration.
4. Mark transfer only when a process lifecycle owner exists.
5. Invoke transferred cleanup after actual PTY or child-process exit processing.
6. Invoke it on terminal setup/finalization failures after transfer.
7. Creator cleanup covers validation, spawn, or registration failure before transfer.
8. Catch and log cleanup failures without changing execution results.
9. Preserve background log storage under its separate owner.
10. Avoid allocating the PID directory on Windows when the complete diff proves that boundary is independent and compatible.

## Discriminating controls

### Current-behavior characterization

- a background request returns its initial receipt;
- simulated or real later exit occurs;
- the created `gemini-shell-*` directory remains on the pinned base.

### Candidate controls

1. foreground success removes the directory exactly once;
2. long-running background execution retains the directory until actual exit, then removes it;
3. a short command requested as background removes it after its real exit;
4. cancellation removes it after termination settlement;
5. validation or spawn failure before transfer remains creator-cleaned;
6. repeated or racing finalization invokes cleanup once;
7. cleanup rejection leaves the original execution result unchanged and emits bounded diagnostics;
8. PTY and child-process fallback both satisfy the contract;
9. background log files remain readable after temporary PID-resource cleanup;
10. Windows creates no unused PID directory, or the retained boundary is documented and tested.

## Historical and architectural precedent

The current process service already centralizes actual-exit cleanup for terminal buffers, process maps, background logs, and execution completion. Temporary PID-resource cleanup follows the same ownership rule while remaining a separate resource.

The important difference is that the temporary directory originates in the shell tool because command wrapping needs its path before process creation. The repair therefore requires explicit ownership transfer rather than moving creation wholesale without preserving command construction.

## Edge cases outside the first repair

- crash recovery across abrupt CLI process death;
- sweeping directories left by older versions;
- shared or externally supplied temp roots;
- malicious replacement of the temporary path after creation;
- PID file parsing and child-process completeness;
- retention policy for background output logs;
- remote-agent executions that do not use this shell wrapper.

These may reopen or split the finding when evidence shows a distinct consequence.

## Exact next transition

1. prepare a target-native base characterization for long and short background requests;
2. materialize Alternative A on a clean owned branch;
3. execute focused shell/background tests and core typecheck;
4. run at least one real short-lived background process control;
5. obtain complete-diff review;
6. move to `delivery-gate-ready` only after a workflow-free source head and retained exact receipt exist.

## Reopening and stop conditions

Reopen the selected architecture if:

- a current source revision already owns the directory elsewhere;
- process-exit cleanup cannot run reliably on one supported adapter;
- the PID file is needed after process exit by a documented consumer;
- cleanup transfer materially changes background log or cancellation behavior.

Stop or retain a negative result if target execution shows the directory is removed by an unobserved owner on the pinned base.

## Current disposition

- Finding state: `research-active`
- Review disposition: `REPAIR`
- Selected direction: process-exit cleanup ownership transfer
- Exact next gate: target-native characterization and clean source candidate
- Clearing condition: exact PTY and child-process controls, workflow-free source, complete-diff review
- Non-delegable human decision: `none`
- Upstream contact authorized: `no`

## References

- Fieldwork #14, #22, #254, and #319.
- Gemini target source `d55e366f6ab393e024c613d940fead3696d56eac`.
- `packages/core/src/tools/shell.ts`.
- `packages/core/src/services/shellExecutionService.ts`.
- `packages/core/src/services/executionLifecycleService.ts`.
- Quiet external lead: https://github.com/google-gemini/gemini-cli/issues/28392.
