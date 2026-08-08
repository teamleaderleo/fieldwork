# Bun runtime compatibility scout

Issue: #705  
Programme: #207  
Parent scout: #209  
Target: `oven-sh/bun` / `target:bun`  
Worker: `chatgpt:gpt-5.6-sol`  
Retrieval date: 2026-08-08  
Exact Bun source: `f972c287f9b7a71754b0b0b1cd18722aa3c75280`  
Comparison Node source: `aed4eaf89dd8d47b9e399bccecc9a9fc588e0284`  
Claim scope: `interface`  
Upstream contact authorized: `false`

## In simple words

Bun's Node-compatible `child_process.execFile()` currently gives one timeout two owners. It passes `timeout` and `killSignal` into Bun's internal `spawn()`, which arms a kill timer, and then `execFile()` arms another kill timer of its own.

Current Node keeps `execFile()`'s timeout at the `execFile()` layer. One `execFile()` call therefore produces one timeout `ChildProcess.kill()` attempt in Node.

The retained discriminator now measures both the parent's actual `ChildProcess.kill()` calls and the child's received `SIGUSR1` count. Counting parent calls is important because ordinary POSIX signals can coalesce while pending, so one child handler invocation does not prove that only one signal-send attempt occurred.

Node 22.16.0 control: `killCallCount: 1`, `signalCount: 1`.

Exact Bun execution is the remaining promotion gate.

## Assignment contract

Question: when `execFile()` uses a timeout with a handled non-terminating custom signal, does Bun invoke `ChildProcess.kill()` twice for one timeout while Node invokes it once?

Expected deliverable: source/test map, overlap check, runnable discriminator, sampled adjacent surfaces, ranked continuation.

Owned output path: `programmes/open-source-ecosystems/scouts/bun-runtime-compatibility/`.

Stop condition: one executable discriminator plus enough source, test, overlap, and negative evidence to decide whether to promote or stop.

External target access is read-only. Automated upstream contact remains prohibited.

## Source map

### Bun `src/js/node/child_process.ts`

At `f972c287f9b7a71754b0b0b1cd18722aa3c75280`:

1. `spawn()` validates `options.timeout` and `options.killSignal`.
2. When `timeout > 0`, `spawn()` creates a timer that calls `child.kill(killSignal)`.
3. `execFile()` calls `spawn()` and forwards both `timeout: options.timeout` and `killSignal: options.killSignal`.
4. `execFile()` then creates another timeout timer whose `kill()` helper destroys stdout/stderr and calls `child.kill(options.killSignal)`.
5. Both timers use the public `ChildProcess.kill()` method and are created for the same timeout duration.
6. `ChildProcess.kill()` consults the native handle's terminated state. A handled signal that leaves the process alive does not inherently make the second attempt disappear.

The source therefore contains two independent timeout callbacks for one `execFile()` operation.

### Node `lib/child_process.js`

At comparison revision `aed4eaf89dd8d47b9e399bccecc9a9fc588e0284`, Node's `execFile()` calls `spawn()` without forwarding `timeout` or `killSignal`. `execFile()` owns one timeout timer and sends the configured signal from that one timer.

## Existing timeout tests and the blind spot

Bun vendors Node's ordinary `exec` timeout tests. The inspected cases use terminating signals such as `SIGTERM` and `SIGKILL` and assert the resulting exit/error state.

Those are healthy compatibility tests, but the first signal terminates the child, so they cannot distinguish one timeout owner from two same-deadline timeout owners.

The retained probe uses a handled non-terminating `SIGUSR1` to keep the process alive through the timeout boundary.

## Prepared discriminator

Artifact: `artifacts/execfile-timeout-signal-count.mjs`

The probe:

1. creates an isolated temporary receipt;
2. launches a child through `execFile(process.execPath, ...)`;
3. uses `timeout: 1000` and `killSignal: "SIGUSR1"`;
4. has the child append one byte for each delivered `SIGUSR1` while remaining alive;
5. wraps the returned child's public `kill()` method immediately after `execFile()` returns and records every timeout-driven call;
6. uses the original unwrapped kill method for a later `SIGKILL` cleanup, keeping cleanup out of `killCallCount`;
7. reports parent kill attempts, child signal receipts, callback result, and runtime identity as JSON.

### Why count kill attempts separately

Standard POSIX signals do not queue multiple pending instances. Two back-to-back `kill(SIGUSR1)` calls may therefore produce only one handler execution if the second arrives while the first signal is still pending.

That makes child-side signal count useful consequence evidence, but insufficient mechanism evidence on its own. The wrapped public method directly distinguishes one Node timeout attempt from two Bun timeout attempts.

### Control receipt

Executed locally under Node 22.16.0:

```json
{
  "runtime": "node 22.16.0",
  "killCallCount": 1,
  "killCalls": [{ "signal": 10, "atMs": 1010 }],
  "signalCount": 1,
  "callbackError": {
    "name": "Error",
    "code": null,
    "signal": "SIGKILL",
    "killed": true
  }
}
```

The final `SIGKILL` is explicit probe cleanup after the handled timeout signal.

Suggested Node control:

```sh
EXPECT_KILL_CALLS=1 EXPECT_SIGNALS=1 node programmes/open-source-ecosystems/scouts/bun-runtime-compatibility/artifacts/execfile-timeout-signal-count.mjs
```

Exact Bun discriminator:

```sh
EXPECT_KILL_CALLS=2 bun programmes/open-source-ecosystems/scouts/bun-runtime-compatibility/artifacts/execfile-timeout-signal-count.mjs
```

Interpretation:

- Bun `killCallCount: 2`: source divergence is target-executed. Record whether `signalCount` is 1 or 2 separately; either value is compatible with two send attempts because standard signals may coalesce.
- Bun `killCallCount: 1`: the apparent source double-owner path is suppressed at runtime; retain a negative result and stop this branch unless another direct consequence appears.
- another count or harness failure: inspect exact timer order and process state before promotion.

## Execution carrier

Fieldwork PR #707 is an execution-only carrier. It installs exact Bun revision `f972c287f9b7a71754b0b0b1cd18722aa3c75280` with `oven-sh/setup-bun`, reruns the Node 22.16.0 control, and runs the Bun discriminator.

The workflow file is temporary and must not enter the canonical scout. Transfer its receipt into this report and retire #707 after execution.

## Overlap and recent-work check

Fieldwork #345 already owns Bun global executable replacement atomicity. That package-manager publication question stays in its existing lane.

Fieldwork intake #457 records `findPackageJSON`, `threadCpuUsage`, and async-generator inspection as occupied Bun work.

Current Bun pull request [#35805](https://redirect.github.com/oven-sh/bun/pull/35805) addresses timeout-timer event-loop liveness: it proposes keeping the existing timeout timers referenced so an unref'd child still receives its deadline signal. Its stated scope leaves the separate `execFile()` double-owner question open.

Searches for an open Bun issue or pull request specifically describing duplicate `execFile()` timeout kill attempts returned no matching result during this pass. This is an overlap observation, not proof of novelty across all history.

## Surrounding code sampled

### Child-process IPC and serialization

`fork()` routes through the same `spawn()` implementation. `spawn()` validates `serialization: "json" | "advanced"` and forwards it into `Bun.spawn`, while IPC message and disconnect callbacks are wired through the native subprocess handle.

No specific unoccupied defect was established from this pass. The surface is deeper than the timeout lead and already has native/JS ownership boundaries, so it should get its own scout only when a concrete mismatch appears.

### Extra stdio descriptors

On POSIX, Bun maps extra `"pipe"` descriptors (`fd >= 3`) to a `socket-fd` ownership mode and wraps the parent side in `net.Socket`, with comments explicitly protecting against double-close. This is a recently intentional ownership boundary rather than an obvious loose end.

Disposition: sampled; no candidate promoted.

### Worker teardown

Current main has focused lifetime coverage for constructor `ref: false`, late `terminate/ref/unref`, nested-worker lifetime, DNS teardown under ASAN, and worker termination while server streams are active.

Disposition: sampled and parked.

### Package-manager replacement

Global executable replacement remains occupied by #345.

Disposition: no duplicate work.

## Competing explanations

### H1 — two timeout kill attempts execute

Both same-duration timers reach the public `child.kill(SIGUSR1)` method.

Discriminator: Bun `killCallCount: 2`, Node `killCallCount: 1`.

### H2 — one timer is suppressed before calling `ChildProcess.kill()`

Some runtime settlement path prevents one callback from reaching the public method.

Discriminator: Bun `killCallCount: 1`.

### H3 — two attempts occur while one signal is delivered

Both callbacks call `kill()`, but the OS coalesces two pending standard `SIGUSR1` instances.

Discriminator: Bun `killCallCount: 2`, `signalCount: 1`.

### H4 — two attempts and two deliveries occur

The child processes the first signal before the second send lands.

Discriminator: Bun `killCallCount: 2`, `signalCount: 2`.

## Ranked branch candidates

1. **Complete exact Bun execution for the `execFile()` double-timeout ownership probe.** Narrowest and strongest current candidate.
2. **If confirmed, prepare one target-native regression and smallest repair.** The Node-shaped repair candidate is to leave timeout ownership at `execFile()` and stop forwarding its timeout/killSignal into internal `spawn()`.
3. **Continue #345 separately.** Its package-publication question has different ownership, evidence, and failure injection.
4. **Return to IPC/worker/extra-stdio areas only with a concrete mismatch.** Current reading alone does not justify another lane.

## Evidence classification

- Bun timer ownership and call flow: `source-read`.
- Node comparison implementation: `source-read`.
- Node 22.16.0 discriminator control: `model-executed`.
- Bun kill-attempt consequence: `target-test-prepared` pending #707.
- Child-side duplicate delivery: `target-test-prepared`; may be coalesced by POSIX signal semantics.
- Broader operational consequence: `Unknown` until target execution and realistic caller interpretation.

## Recommendation

Finish #707. If exact Bun executes two timeout `ChildProcess.kill()` calls while Node executes one, promote a narrow Node-compatibility finding. Keep the repair tiny: one timeout owner for `execFile()`, a handled-signal regression, ordinary terminating-signal controls, and interaction with the pending timer-liveness work checked explicitly.

If exact Bun records one kill attempt, retain the source difference as a negative result and stop this branch.

No Bun repository mutation or maintainer-facing interaction occurred during this scout.
