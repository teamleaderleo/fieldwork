# Gemini background shell temporary-resource ownership

Finding ID: `F319-gemini-background-temp-ownership`  
Finding state: `research-active`  
Owning issue: #319  
Programme: #14  
Target hub: #5  
Exact target source: `google-gemini/gemini-cli@d55e366f6ab393e024c613d940fead3696d56eac`  
Strongest evidence class: `target-executed`  
Current disposition: `ACCEPT child-process slice / continue bounded execution`  
Non-delegable human decision: `none`  
Upstream contact authorized: `no`

## In simple words

Gemini CLI creates a temporary `gemini-shell-*` directory so a shell exit trap can record child process IDs. Foreground commands delete it. Background requests used to skip cleanup because the file may still be needed after the shell tool returns its first background receipt.

The process service that observes the real exit did not receive the directory or a cleanup operation. The selected repair transfers one idempotent cleanup operation only after the lifecycle service accepts ownership of a still-running background execution. The shell invocation keeps cleanup authority when that transfer never succeeds.

The current Linux child-process candidate has executed successfully. It also prevents the child `error` and later `close` events from finalizing or cleaning the same execution twice.

## Why this matters

Repeated background commands can accumulate temporary directories and inode usage. More importantly, request intent must not decide lifecycle ownership. Cleanup must follow the actual transition:

- creator-owned before transfer;
- process-owned after accepted background transfer;
- exactly once after actual exit;
- best-effort without replacing the execution result.

This finding is separate from termination receipts, background-log retention, child-process escalation policy, and PID-discovery completeness.

## Governing invariant

Every temporary execution resource has exactly one cleanup owner after each lifecycle transition.

1. The creator owns cleanup before process registration.
2. A resource needed until actual exit transfers only to the component that observes actual exit.
3. Failed or declined transfer leaves cleanup with the creator.
4. Cleanup failure never replaces the primary execution outcome.
5. Repeated terminal callbacks never repeat destructive cleanup or terminal publication.

## Source and ownership map

### Current base defect

At `d55e366f...`:

- `packages/core/src/tools/shell.ts` creates `gemini-shell-*` and `bgpids.tmp` before shell execution;
- its cleanup follows the `is_background` request flag;
- `ShellExecutionService.background()` receives process, session, and display identity without a temporary-resource owner;
- PTY and child-process finalizers own actual-exit settlement for output, history, maps, logs, and lifecycle completion;
- short commands requested as background can finish during the delay while the request flag still suppresses creator cleanup.

Owned Gemini PR #9 retains the exact short-command base characterization.

### Selected candidate

The executed candidate changes five Gemini files:

- `packages/core/src/services/executionLifecycleService.ts`;
- `packages/core/src/services/shellExecutionService.ts`;
- `packages/core/src/tools/shell.ts`;
- one lifecycle/child-process regression file;
- one shell ownership-ordering regression file.

The contract is:

- `ExecutionLifecycleService.background()` acknowledges whether it claimed the still-pending execution;
- the shell invocation transfers cleanup only after that acknowledgement;
- exit observed before transfer does not delete the PID file before parsing finishes;
- transfer observed before exit keeps the directory until actual exit;
- foreground and failed-transfer paths remain creator-cleaned;
- child finalization is guarded before command cleanup, terminal publication, and transferred cleanup;
- cleanup rejection is logged and does not alter the execution result.

The `canBackground()` preflight and final claim execute synchronously in one JavaScript turn, so a process-exit callback cannot interleave between them. Failed preflight creates no background history or log side effects.

## Evidence table

| Claim | Evidence class | Exact support | Limit |
| --- | --- | --- | --- |
| base creates the PID directory and lacks an exit owner | `source-read` | Gemini `d55e366f...` source map | no cross-version claim |
| short background request retains the directory on the base | `target-executed` | Gemini PR #9, run `30596117032` | mocked execution, Linux path |
| ownership transfer handles exit-before-claim and claim-before-exit | `target-executed` | Fieldwork PR #334, run `30623523324` | pinned Linux source |
| foreground cleanup remains creator-owned | `target-executed` | shell ownership-transfer controls | one target runtime |
| child actual exit invokes cleanup and cleanup rejection preserves result | `target-executed` | process-exit controls | child-process adapter |
| child `error` followed by actual `close` finalizes exactly once | `target-executed` | deterministic close-barrier regression | PTY callback duplication remains separate |
| package compatibility for the focused slice | `target-executed` | 121 tests, package build, explicit typecheck, Prettier | not the full repository preflight |

## Exact execution receipt

Canonical execution carrier: Fieldwork PR #334.  
Exact Fieldwork head: `0c398748c8e961e9c09c7df4ec78fdd61a025a32`.  
Exact target source: `d55e366f6ab393e024c613d940fead3696d56eac`.

- Fieldwork integrity `30623523226`: success;
- target run `30623523324`, job `91133338900`: success;
- inherited candidate patch: `12/12` hunks applied;
- target formatter: five files formatted and checked;
- `executionLifecycleService.test.ts`: 26 passed;
- process-exit cleanup controls: 4 passed;
- shell ownership controls: 3 passed;
- adjacent `shell.test.ts`: 89 passed, one existing skip;
- total: 121 passed, one skipped;
- package posttest build: passed;
- explicit core typecheck: passed;
- exact five-file fence and diff hygiene: passed;
- artifact: `8790481698`;
- artifact digest: `sha256:02a2251db89ab172861d2a88945602d2ada6a34dd8eec43c654a58dd361dcfa7`;
- complete review `4827751443`: `ACCEPT` for the next execution-carrier transition.

## Alternatives compared

### A — explicit process-exit cleanup transfer

**Selected.** It matches actual-exit ownership, preserves foreground behavior, supports both completion orderings, and makes transfer success observable.

### B — cleanup on the initial background receipt

**Rejected.** The receipt precedes actual exit, while the shell trap may still need the PID file.

### C — shell-invocation polling

**Rejected.** It duplicates process ownership after the invocation has returned.

### D — global sweeper or age-based deletion

**Rejected as the first repair.** It hides the ownership defect and introduces unrelated age and deletion policy.

### E — immediate deletion after requesting background

**Rejected.** Request intent is not accepted lifecycle ownership and may precede PID-file completion.

## Executed and remaining controls

### Executed

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
- package build, typecheck, formatting, and five-file fence.

### Remaining before promotion

1. materialize the formatted artifact as one clean workflow-free Gemini source branch;
2. execute or explicitly bound PTY finalization and duplicate-callback behavior;
3. execute cancellation/escalation cleanup ordering;
4. decide Windows PID-directory avoidance through source and platform evidence;
5. compare the clean source against the current public Gemini head;
6. obtain complete-diff review of the clean source branch;
7. transfer receipts and prove temporary workflows absent before carrier retirement.

## Edge cases outside the first source slice

- abrupt CLI process death and old-version directory sweeping;
- shared or externally supplied temporary roots;
- malicious path replacement;
- PID parsing completeness;
- remote-agent executions that do not use the shell wrapper;
- background-output log retention policy.

These remain separate unless new evidence shows they share the same owner.

## Exact next transition

Publish the executed five-file artifact as a clean owned Gemini source branch directly parented by `d55e366f...`. Re-run the exact target controls on that source generation, then add the smallest PTY, cancellation, and Windows discriminators needed to decide promotion. Retire PRs #321 and #334 only after the clean source owns the receipt and a later exact head proves temporary workflow absence.

## Reopening and stop conditions

Reopen the selected architecture if:

- a newer source revision already owns the directory elsewhere;
- one supported adapter cannot invoke cleanup reliably after transfer;
- a documented consumer needs the PID file after actual exit;
- cleanup transfer changes background-log or cancellation semantics;
- current-upstream comparison conflicts materially with the pinned candidate.

Stop or narrow remaining platform work when target-native evidence shows a boundary is impossible, already handled, or lower consequence than its compatibility cost.

## Current disposition

- Finding state: `research-active`
- Review disposition: `ACCEPT child-process slice / continue bounded execution`
- Selected direction: explicit process-exit cleanup ownership transfer
- Exact next gate: clean workflow-free source materialization and remaining adapter controls
- Clearing condition: current-source relation, PTY/child/cancellation/Windows disposition, exact receipt transfer, complete source review
- Non-delegable human decision: `none`
- Upstream contact authorized: `no`

## References

- Fieldwork #14, #22, #254, #319, PR #320, PR #321, and PR #334.
- Gemini PR #9.
- Gemini target source `d55e366f6ab393e024c613d940fead3696d56eac`.
- Quiet external lead: `https://github.com/google-gemini/gemini-cli/issues/28392`.
