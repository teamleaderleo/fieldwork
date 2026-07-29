# Execa descendant termination and signal safety

State: `investigating`

Fieldwork lane: #106

Programme: #14

Target release: `execa@10.0.0`

Source pin: `sindresorhus/execa@e389369f3cd82ae59a8635781ecb9fb20f7cb201`

Feature introduction: `84fa0ecb3f7ca5f73f2dcbd4d4ec0c65fb6b1146`

Upstream contact authorized: `false`

## In simple words

Execa 10 added `killDescendants` so one termination request can close a subprocess tree. The Unix path preserves the requested signal and targets a process group. The Windows path ignores the signal and always launches `taskkill /T /F`.

Node treats signal `0` specially: it checks whether a process exists and must not terminate it. Execa also explicitly accepts `subprocess.kill(0)`. The current Windows adapter therefore appears to turn a standard non-destructive existence check into forced process-tree termination when `killDescendants: true`.

This report records the source finding and a released-package probe. The defect is not marked confirmed until the Windows workflow executes.

## Why this is worth checking

- `killDescendants` is new in Execa 10.0.0.
- The public API retains the `ChildProcess.kill(signal)` shape and accepts integer signal `0`.
- Process supervisors commonly use signal `0` for liveness checks before cleanup, reconciliation, or ownership transfer.
- A destructive liveness check could stop a valid command tree while the caller believes it only inspected state.
- Smolrunner and Starsector Preflight are plausible future contexts, but neither is an active testbed for this lane.

## Source map

### Signal acceptance

`lib/terminate/kill.js` parses `subprocess.kill()` arguments and accepts any integer before calling `normalizeSignalArgument()`.

`lib/terminate/signal.js` deliberately returns signal `0` unchanged. It rejects `0` only for the default `killSignal` option, not for an explicit `subprocess.kill(0)` call.

### Descendant dispatch

`lib/terminate/kill-descendants.js` selects a platform adapter whenever `killDescendants` is enabled.

On Unix:

```js
process.kill(-subprocess.pid, signal)
```

This preserves signal `0`, so the process-group check remains non-destructive.

On Windows:

```js
execFile('taskkill', ['/pid', `${subprocess.pid}`, '/T', '/F'], () => {})
return true
```

The signal argument is discarded. Every call becomes forced process-tree termination.

### Escalation interaction

`subprocessKill()` schedules `forceKillAfterDelay` only when the requested signal equals the configured termination signal. Signal `0` does not normally schedule escalation. The destructive action is therefore inside the Windows adapter itself, before escalation logic.

## Probe contract

The released-package probe runs on Ubuntu and Windows with Node 22, 24, and 26.

For each job it:

1. starts a long-lived Node subprocess with `killDescendants: true`;
2. confirms the PID is alive using Node's own `process.kill(pid, 0)`;
3. calls Execa's `subprocess.kill(0)`;
4. waits for the adapter outcome;
5. records whether the process remained alive;
6. performs deterministic cleanup.

Expected current result:

- Ubuntu: child remains alive;
- Windows: child is forcefully terminated by `taskkill`.

A mismatch is treated as a changed implementation or probe error and should be diagnosed before any claim is promoted.

## Narrow repair seam

Handle signal `0` before platform-specific descendant termination.

Candidate behavior:

```js
if (signal === 0) {
  return subprocess.kill(0)
}
```

Acceptance requirements:

- no `taskkill` process is started;
- the direct child and descendants remain alive;
- the boolean return matches Node's liveness-check behavior;
- no force-kill timer is scheduled;
- Execa does not mark the operation canceled, timed out, or forcefully terminated;
- ordinary descendant termination remains unchanged.

A focused Windows regression should pair `kill(0)` with a normal termination control to prove the adapter still closes the full tree for actual kill signals.

## Adjacent questions retained but not folded into this finding

- whether asynchronous `taskkill` launch errors should be observable;
- whether returning `true` before `taskkill` starts is the best `ChildProcess.kill()` compatibility contract;
- process-tree escape through new sessions or process groups;
- terminal detachment and lost CTRL-C forwarding on Unix;
- PID reuse between liveness checks and later termination;
- job-object ownership as a stronger Windows process-tree primitive.

## Stop conditions

Stop or narrow the lane if:

- released Execa 10.0.0 keeps the process alive on Windows;
- current main already contains an equivalent signal-zero guard and regression;
- Node or Execa rejects the call before descendant dispatch;
- the behavior is documented as an intentional incompatibility and a non-destructive public check exists.

## Contact boundary

No upstream issue, pull request, comment, review, reaction, or message has been created. Any upstream packet remains held for explicit human authorization.