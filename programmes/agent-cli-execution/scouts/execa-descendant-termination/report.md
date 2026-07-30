# Execa descendant termination and signal safety

State: `validated-candidate`

Fieldwork lane: #106

Programme: #14

Target release: `execa@10.0.0`

Release pin: `sindresorhus/execa@e389369f3cd82ae59a8635781ecb9fb20f7cb201`

Current-main inspection pin: `sindresorhus/execa@499fe800361e6b383b0085f635a69fd27e6cf447`

Feature introduction: `84fa0ecb3f7ca5f73f2dcbd4d4ec0c65fb6b1146`

Owned implementation: `teamleaderleo/execa#1`

Owned head: `dc73ffcd1765666f77fb39775af73abec08c5bb5`

Cross-platform workflow: `30491600304`

Upstream contact authorized: `false`

## In simple words

Execa is a Node.js library for launching and controlling other programs. Execa 10 added `killDescendants` so one termination request can close a subprocess and the processes it started.

Node treats signal `0` specially: it checks whether a process exists and must not terminate it. Execa explicitly accepts `subprocess.kill(0)`. The Windows descendant adapter routes signals through forced `taskkill /T /F`, so signal `0` can become process-tree termination instead of a liveness check.

The owned correction handles signal `0` before selecting any platform-specific descendant adapter. Non-zero signals keep the existing tree-termination behavior.

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

That change confirms the intended ownership boundary: the Windows adapter owns descendant termination. It did not separate non-terminating signal `0` from actual termination signals.

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

### Local source execution

Node `22.16.0`, Linux x86-64:

- exact Windows adapter branch: signal `0` called native `subprocess.kill(0)`, launched no `taskkill`, and a later `SIGTERM` produced the expected `/T /F` command;
- real Unix process group: signal `0` preserved a live parent and grandchild, then a later non-zero signal terminated the group.

Both passed.

### Real Windows and Ubuntu execution

Fieldwork workflow `30491600304` checked out the exact owned Execa branch and ran:

```text
npx ava test/terminate/kill-descendants.js test/terminate/kill-descendants-signal-zero.js
```

Matrix result:

- Node 22 on Ubuntu: pass;
- Node 24 on Ubuntu: pass;
- Node 26 on Ubuntu: pass;
- Node 22 on Windows: pass;
- Node 24 on Windows: pass;
- Node 26 on Windows: pass.

The Windows jobs used the real Windows runner and real `taskkill.exe` path. They prove that signal `0` preserves the live process tree, does not trigger delayed force-kill escalation, and that a later ordinary kill still closes the tree.

Fieldwork integrity and external-reference policy passed on the workflow-bearing head.

## Acceptance result

- no `taskkill` process is started for signal `0`: pass;
- direct child and descendant remain alive: pass;
- boolean return follows Node's native liveness check: pass;
- no delayed force-kill terminates the tree: pass;
- ordinary descendant termination remains unchanged: pass;
- focused tests pass on actual Windows runners: pass.

## Adjacent questions retained but not folded into this finding

- whether asynchronous `taskkill` launch errors should be observable;
- whether returning `true` before `taskkill` starts is the best `ChildProcess.kill()` compatibility contract;
- process-tree escape through new sessions or process groups;
- terminal detachment and lost CTRL-C forwarding on Unix;
- PID reuse between liveness checks and later termination;
- job-object ownership as a stronger Windows process-tree primitive.

## Current decision

The defect and narrow repair are cross-platform validated. No additional source or test work is needed for the current scope.

The owned PR remains draft because it is a Fieldwork research branch, not an authorized upstream submission. The issue-first packet remains held.

## Contact boundary

No upstream issue, pull request, comment, review, reaction, or message has been created. Any upstream packet remains held for explicit human authorization.
