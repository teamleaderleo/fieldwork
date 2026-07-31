# Gemini background shell temporary-resource ownership

Finding ID: `F319-gemini-background-temp-ownership`  
Finding state: `research-active`  
Owning issue: #319  
Programme: #14  
Target hub: #5  
Exact target base: `google-gemini/gemini-cli@d55e366f6ab393e024c613d940fead3696d56eac`  
Canonical owned source: `teamleaderleo/gemini-cli#11@c9a0ec7f452ee9a3252661b78c230a1c7b5f9fcc`  
Evidence classes present: `source-read`, `target-executed`  
Current disposition: `ACCEPT clean Linux child-process source / continue bounded adapter execution`  
Non-delegable human decision: `none`  
Upstream contact authorized: `no`

## In simple words

Gemini CLI creates a temporary `gemini-shell-*` directory so a shell exit trap can record child process IDs. Foreground commands delete it. Background requests used to return before actual process exit while no later owner received that directory.

The selected repair transfers one idempotent cleanup operation only after the lifecycle service accepts a still-pending background execution. The shell invocation keeps cleanup authority when transfer never succeeds. Child `error` followed by `close` finalizes and cleans once.

The clean five-file source branch is now published, target-executed, workflow-free, and independently reviewed for the pinned Linux child-process slice.

## Governing invariant

Every temporary execution resource has exactly one cleanup owner after each lifecycle transition.

1. The creator owns cleanup before accepted background transfer.
2. A resource needed until actual exit transfers only to the component that observes actual exit.
3. Failed or declined transfer leaves cleanup with the creator.
4. Cleanup failure never replaces the primary execution outcome.
5. Repeated terminal callbacks never repeat destructive cleanup or terminal publication.

## Base defect

At `d55e366f...`:

- `packages/core/src/tools/shell.ts` creates `gemini-shell-*` and `bgpids.tmp`;
- cleanup follows the `is_background` request flag;
- `ShellExecutionService.background()` receives process, session, and command identity without temporary-resource ownership;
- PTY and child-process finalizers observe actual exit;
- a short command requested as background can finish during the delay while creator cleanup remains suppressed.

Gemini PR #9 retains the exact short-command base characterization.

## Selected source

Canonical owned source: Gemini PR #11.  
Exact head: `c9a0ec7f452ee9a3252661b78c230a1c7b5f9fcc`.  
Exact parent: `d55e366f6ab393e024c613d940fead3696d56eac`.  
Changed-file fence: five files, with no `.github` change.

- `packages/core/src/services/executionLifecycleService.ts`;
- `packages/core/src/services/shell-execution-process-exit-cleanup.test.ts`;
- `packages/core/src/services/shellExecutionService.ts`;
- `packages/core/src/tools/shell-background-temp-ownership-repair.test.ts`;
- `packages/core/src/tools/shell.ts`.

The source contract is:

- `ExecutionLifecycleService.background()` acknowledges exactly one still-pending execution;
- the shell invocation transfers cleanup only after that acknowledgement;
- exit observed before transfer records the fact without deleting the PID file before parsing;
- transfer observed before exit retains the directory until actual exit;
- foreground, short-completed, validation-failure, and declined-transfer paths remain creator-cleaned;
- child finalization is guarded before command cleanup, terminal publication, lifecycle completion, and transferred cleanup;
- service-level cleanup rejection is caught and cannot replace the execution result.

The `canBackground()` preflight and final claim execute synchronously in one JavaScript turn, so process exit cannot interleave between them.

## Claim-scoped evidence

| Claim | Evidence class | Exact support | Limit |
| --- | --- | --- | --- |
| base creates the PID directory and lacks an exit owner | `source-read` | Gemini `d55e366f...` | no cross-version claim |
| short background request retains the directory on the base | `target-executed` | Gemini PR #9, run `30596117032` | mocked execution, Linux path |
| exit-before-claim and claim-before-exit preserve one owner | `target-executed` | PR #11 publication run `30624706086` | pinned Linux source |
| foreground and declined transfer remain creator-cleaned | `target-executed` | shell ownership controls | one target runtime |
| child actual exit invokes cleanup | `target-executed` | process-exit controls | child-process adapter |
| child `error` followed by real `close` finalizes once | `target-executed` | deterministic close-barrier regression | PTY remains separate |
| cleanup callback rejection preserves the process result | `target-executed` | service-level rejection control | real filesystem deletion errors remain silently best-effort |
| focused package compatibility | `target-executed` | 121 tests, build, typecheck, Prettier | not full repository preflight |

## Clean-source receipt

Publisher: Gemini PR #10 at `b7ea64681711c71160a3be6b045c577f7c3de838`.  
Run `30624706086`, job `91137148865`: success.

- exact Fieldwork input `0c398748c8e961e9c09c7df4ec78fdd61a025a32`;
- exact target checkout `d55e366f...`;
- target Prettier on five files;
- 121 tests passed, one existing skip;
- package posttest build and explicit core typecheck passed;
- exact parent and five-file fence passed;
- clean worktree and workflow-free source push passed;
- source artifact `8791620099`;
- artifact digest `sha256:ab74a490fb2e6de882e66f13fdafe783b7149025f6938c3bdb1c25fa9df73f36`;
- source review `4828059167`: `ACCEPT` for the pinned Linux child-process transition.

## Alternatives compared

### A — explicit process-exit cleanup transfer

**Selected.** It matches actual-exit ownership, preserves foreground behavior, supports both completion orderings, and makes transfer success observable.

### B — cleanup on the initial background receipt

**Rejected.** The receipt precedes actual exit, while the shell trap may still need the PID file.

### C — shell-invocation polling

**Rejected.** It duplicates process ownership after the invocation returns.

### D — global sweeper or age-based deletion

**Rejected as the first repair.** It hides the ownership defect and introduces unrelated deletion policy.

### E — immediate deletion after requesting background

**Rejected.** Request intent is not accepted lifecycle ownership and may precede PID-file completion.

## Executed controls

- base short-command retained-directory characterization;
- foreground cleanup;
- exit-before-claim;
- claim-before-exit;
- exact-once background claim;
- failed-preflight side-effect avoidance;
- child actual-exit cleanup;
- cleanup rejection with result preservation;
- child `error` followed by real `close` exactly once;
- adjacent shell and lifecycle suites;
- package build, typecheck, formatting, exact parent, and five-file source fence.

## Remaining before promotion

1. execute or explicitly bound PTY finalization and duplicate-callback behavior;
2. execute cancellation/escalation cleanup ordering;
3. decide Windows PID-directory allocation through source and platform evidence;
4. decide whether actual filesystem deletion diagnostics are required for the promoted claim;
5. compare the clean source against the current public Gemini head;
6. obtain a current-upstream compatibility receipt if the source path moved;
7. retire temporary carriers after their front pages transfer this exact source and receipt.

## Edge cases outside the first source slice

- abrupt CLI process death and old-version directory sweeping;
- shared or externally supplied temporary roots;
- malicious path replacement;
- PID parsing completeness;
- remote-agent executions that do not use the shell wrapper;
- background-output log retention policy.

## Exact next transition

Retire publisher PR #10 and superseded Fieldwork carriers #321/#334 after front-page transfer. Then execute the smallest PTY, cancellation, and Windows discriminators against PR #11, refresh the public-source comparison, and decide whether the clean source can advance beyond `research-active`.

## Reopening and stop conditions

Reopen the selected architecture if:

- a newer source revision already owns the directory elsewhere;
- one supported adapter cannot invoke cleanup reliably after transfer;
- a documented consumer needs the PID file after actual exit;
- cleanup transfer changes background-log or cancellation semantics;
- current-upstream comparison conflicts materially with the pinned source.

Stop or narrow remaining platform work when target-native evidence shows a boundary is already handled, impossible to exercise safely, or lower consequence than its compatibility cost.

## Current disposition

- Finding state: `research-active`
- Review disposition: `ACCEPT clean Linux child-process source / continue bounded adapter execution`
- Selected direction: explicit process-exit cleanup ownership transfer
- Exact next gate: PTY, cancellation, Windows, deletion-diagnostic, and current-source disposition
- Clearing condition: current-source relation plus complete supported-adapter evidence or bounded stop records
- Non-delegable human decision: `none`
- Upstream contact authorized: `no`

## References

- Fieldwork #14, #22, #254, #319, PR #320, PR #321, and PR #334.
- Gemini PR #9, PR #10, and PR #11.
- Gemini target base `d55e366f6ab393e024c613d940fead3696d56eac`.
- Quiet external lead: `https://github.com/google-gemini/gemini-cli/issues/28392`.
