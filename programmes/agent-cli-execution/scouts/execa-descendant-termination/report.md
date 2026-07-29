# Execa descendant termination and signal safety

State: `candidate-implemented`

Fieldwork lane: #106

Programme: #14

Target release: `execa@10.0.0`

Release pin: `sindresorhus/execa@e389369f3cd82ae59a8635781ecb9fb20f7cb201`

Current-main inspection pin: `sindresorhus/execa@499fe800361e6b383b0085f635a69fd27e6cf447`

Feature introduction: `84fa0ecb3f7ca5f73f2dcbd4d4ec0c65fb6b1146`

Owned implementation: `teamleaderleo/execa#1`

Owned head: `dc73ffcd1765666f77fb39775af73abec08c5bb5`

Upstream contact authorized: `false`

## In simple words

Execa is a Node.js library for launching and controlling other programs. Execa 10 added `killDescendants` so one termination request can close a subprocess and the processes it started.

Node treats signal `0` specially: it checks whether a process exists and must not terminate it. Execa explicitly accepts `subprocess.kill(0)`. The Windows descendant adapter routes signals through forced `taskkill /T /F`, so signal `0` can become process-tree termination instead of a liveness check.

The owned candidate now handles signal `0` before selecting any platform-specific descendant adapter. Non-zero signals keep the existing tree-termination behavior.

## Why this is worth checking

- `killDescendants` is new in Execa 10.0.0.
- The public API retains the `ChildProcess.kill(signal)` shape and accepts integer signal `0`.
- Supervisors use signal `0` for liveness checks before cleanup, reconciliation, or ownership transfer.
- A destructive liveness check can stop valid work while the caller believes it only inspected state.
- Smolrunner and Starsector Preflight are plausible future contexts, but neither is an active testbed for this lane.

## Source map

### Signal acceptance

`lib/terminate/kill.js` parses `subprocess.kill()` arguments and passes an explicit integer signal through `normalizeSignalArgument()`.

`lib/terminate/signal.js` deliberately returns signal `0` unchanged. It rejects `0` only for the default `killSignal` option, not for an explicit `subprocess.kill(0)` call.

### Descendant dispatch

`lib/terminate/kill-descendants.js` selects a platform adapter whenever `killDescendants` is enabled.

On Unix, non-zero signals target the subprocess process group:

```js
process.kill(-subprocess.pid, signal)
```

On Windows, non-zero signals use:

```js
execFile(taskkillFile, ['/pid', `${subprocess.pid}`, '/T', '/F'], callback)
```

`taskkill /F` does not preserve signal `0`; it terminates the tree.

### Escalation interaction

`subprocessKill()` schedules `forceKillAfterDelay` only when the requested signal equals the configured termination signal. Signal `0` does not normally schedule escalation. The original destructive action is inside the Windows descendant adapter itself.

## Historical precedent

Merged upstream PR #1258 improved `taskkill` discovery and fallback behavior. It intentionally kept `taskkill /T /F` as the primary Windows tree-termination path and forwarded the requested signal only when `taskkill` was unavailable or failed.

That change provides the closest implementation precedent and confirms the intended ownership boundary: the Windows adapter owns descendant termination. It did not separate non-terminating signal `0` from actual termination signals.

Searches for `killDescendants`, `signal 0`, `kill(0)`, and `taskkill` found no matching current issue or pull request for this exact case.

## Self-review correction

The first candidate placed the signal-zero guard only inside the Windows adapter. Review moved it into the shared dispatcher:

```js
return signal => signal === 0
  ? subprocess.kill(0)
  : killDescendantsFunction(subprocess, signal)
```

This is the clearer contract. `killDescendants` changes how termination is delivered; it should not redefine a liveness check on any platform or require every future platform adapter to remember signal-zero semantics.

## Owned candidate

Draft PR: `teamleaderleo/execa#1`

Branch: `fieldwork/kill-descendants-signal-zero`

Current changes:

- intercept signal `0` before Unix or Windows descendant dispatch;
- delegate the liveness check to the native child-process method;
- retain process-group and `taskkill` behavior for non-zero signals;
- add a deterministic Windows-adapter test proving no `taskkill` launch;
- add a live process-tree test proving the parent and descendant remain alive;
- add a delayed-escalation test with `forceKillAfterDelay: 100`;
- retain normal tree-termination controls.

## Validation receipt

Local runtime: Node `22.16.0`, Linux x86-64.

### Exact Windows adapter execution

The current candidate source was imported after setting `process.platform` to `win32` and replacing Node's `execFile` binding with a recorder.

Observed:

- `kill(0)` returned `true`;
- native `subprocess.kill(0)` received the call;
- zero `taskkill` calls occurred for signal `0`;
- a later `SIGTERM` produced `taskkill.exe /pid <pid> /T /F`.

Result: pass.

This executes the exact Windows adapter branch, but it is not an actual Windows-kernel or `taskkill.exe` run.

### Real Unix process-tree execution

A detached Node child spawned a live grandchild. The candidate source then performed signal `0` followed by `SIGTERM`.

Observed:

- signal `0` returned `true`;
- parent and grandchild remained alive after the check;
- the later non-zero signal terminated the process group;
- no descendant remained running after cleanup.

Result: pass.

### Fork CI boundary

The repository's existing CI matrix covers Node 22, 24, and 26 on Ubuntu, macOS, and Windows. GitHub Actions are disabled on the newly created fork, and no workflow run exists for the candidate head. An actual Windows OS receipt remains pending and is not implied by the adapter test.

## Acceptance requirements

- no `taskkill` process is started for signal `0`;
- the direct child and descendants remain alive;
- the boolean return matches Node's native liveness-check behavior;
- no force-kill timer later terminates the tree;
- Execa does not classify the operation as canceled, timed out, or forcefully terminated;
- ordinary descendant termination remains unchanged;
- the focused tests pass on an actual Windows runner.

## Adjacent questions retained but not folded into this finding

- whether asynchronous `taskkill` launch errors should be observable;
- whether returning `true` before `taskkill` starts is the best `ChildProcess.kill()` compatibility contract;
- process-tree escape through new sessions or process groups;
- terminal detachment and lost CTRL-C forwarding on Unix;
- PID reuse between liveness checks and later termination;
- job-object ownership as a stronger Windows process-tree primitive.

## Current decision

Retain the candidate as a credible narrow fix. Do not mark the defect target-confirmed or the repair complete until an actual Windows job executes the live regression.

No additional design work is needed before that run. The next action is execution, not expansion.

## Contact boundary

No upstream issue, pull request, comment, review, reaction, or message has been created. Any upstream packet remains held for explicit human authorization.
