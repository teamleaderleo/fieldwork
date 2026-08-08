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

Bun's Node-compatible `child_process.execFile()` appears to schedule the same timeout action twice. It passes `timeout` and `killSignal` into Bun's internal `spawn()`, which creates one timer, and then creates another timer inside `execFile()`.

Current Node keeps `execFile()`'s timeout at the `execFile()` layer, so this operation has one timeout timer there.

The source difference is established. A small POSIX probe can tell us whether a child that handles `SIGUSR1` and stays alive receives one signal under Node and two under Bun. The corrected probe records exactly one signal under Node 22.16.0. Bun execution remains the missing cell, so this is still a source-level compatibility lead.

## Assignment contract

Question: when `execFile()` uses a timeout with a handled non-terminating custom signal, can one timeout deliver the signal twice in Bun?

Expected deliverable: source/test map, overlap check, runnable discriminator, sampled adjacent surfaces, ranked continuation.

Owned output path: `programmes/open-source-ecosystems/scouts/bun-runtime-compatibility/`.

Dependencies: none for source reading; Bun execution is required to promote the lead.

Stop condition: one executable discriminator plus enough source, test, and overlap evidence to decide whether to execute, park, or promote.

External target access: read-only. Automated upstream contact remains prohibited.

## Source map

### Bun `src/js/node/child_process.ts`

At the pinned Bun revision:

1. `spawn()` validates `options.timeout` and `options.killSignal`.
2. When `timeout > 0`, `spawn()` creates a timer that calls `child.kill(killSignal)`.
3. `execFile()` calls `spawn()` and forwards both `timeout: options.timeout` and `killSignal: options.killSignal`.
4. `execFile()` then creates its own timeout timer whose `kill()` helper destroys stdout/stderr and calls `child.kill(options.killSignal)`.
5. `ChildProcess.kill()` checks the native handle's `killed` state. A first handled signal that leaves the process alive does not inherently settle the child before a second timer gets a chance to signal it.

The two timers are scheduled for the same timeout duration and have distinct callbacks.

### Node `lib/child_process.js`

At comparison revision `aed4eaf89dd8d47b9e399bccecc9a9fc588e0284`, Node's `execFile()` calls `spawn()` without forwarding `timeout` or `killSignal`. It then owns one `execFile()` timeout timer and sends the selected kill signal from that timer.

This comparison supplies the expected control behavior for the prepared probe.

## Test map

Bun's relevant local test surfaces include:

- `test/js/node/child_process/child_process.test.ts` for Bun-specific `spawn`, `kill`, timeout, stdio, and compatibility cases;
- ported Node child-process cases under `test/js/node/test/parallel/`;
- `test/js/web/workers/worker-terminate-lifetime.test.ts` for dedicated worker lifetime and teardown regressions.

The current child-process suite tests ordinary timeout termination and several kill-state properties. The inspected coverage does not exercise `execFile()` timeout with a custom signal handler that deliberately keeps the child alive long enough to observe repeated delivery.

## Prepared discriminator

Artifact: `artifacts/execfile-timeout-signal-count.mjs`

The probe:

1. creates a temporary receipt path;
2. launches a child through `execFile(process.execPath, ...)`;
3. gives `execFile()` `timeout: 1000` and `killSignal: "SIGUSR1"`;
4. has the child append one byte per `SIGUSR1` while continuing to run;
5. sends `SIGKILL` later only to guarantee cleanup;
6. reports the observed signal count as JSON;
7. optionally asserts a count through `EXPECT_SIGNALS`.

Suggested control:

```sh
EXPECT_SIGNALS=1 node programmes/open-source-ecosystems/scouts/bun-runtime-compatibility/artifacts/execfile-timeout-signal-count.mjs
```

Candidate execution:

```sh
EXPECT_SIGNALS=1 bun programmes/open-source-ecosystems/scouts/bun-runtime-compatibility/artifacts/execfile-timeout-signal-count.mjs
```

### Comparison control executed

The corrected probe ran in the available Linux analysis environment with Node `22.16.0`:

```json
{
  "runtime": "node 22.16.0",
  "signalCount": 1,
  "receiptBytes": "x",
  "callbackError": {
    "name": "Error",
    "code": null,
    "signal": "SIGKILL",
    "killed": true
  },
  "callbackStdout": "",
  "callbackStderr": ""
}
```

The terminal `SIGKILL` is the probe's explicit cleanup after the observation window. The timeout itself delivered one handled `SIGUSR1`.

An initial harness draft used an escaped textual delimiter whose parsing could collapse several signal deliveries into one logical row. The Node control exposed that ambiguity before handoff. The retained artifact now writes exactly one byte per signal and counts bytes directly.

Interpretation:

- Node 1 / Bun 1: the double timer is observationally coalesced for this discriminator; retain the source difference as a negative result unless another direct consequence appears.
- Node 1 / Bun 2: compatibility defect; promote with the execution receipt and a target-native regression test.
- Any other count: inspect signal order, process state, and timer settlement before drawing a conclusion.

## Overlap and recent-work check

Fieldwork already owns Bun global executable replacement atomicity in #345. That package-manager publication question stays in its existing lane.

Fieldwork intake #457 also records `findPackageJSON`, `threadCpuUsage`, and async-generator inspection as occupied by active Bun work.

Current Bun pull request [#35805](https://redirect.github.com/oven-sh/bun/pull/35805) covers timeout-timer event-loop liveness. Its proposal keeps the existing timer referenced so `spawn({ timeout })` can still deliver a deadline signal after the caller unrefs the child. Its stated scope leaves the `execFile()` double-timer question open.

Searches for an open Bun issue describing duplicate `execFile` timeout signal delivery returned no matching result during this pass. That is an overlap observation, not proof of novelty across all history.

## Adjacent sampling and negative results

### Worker teardown

Current Bun main has a dedicated `worker-terminate-lifetime.test.ts` suite covering constructor `ref: false`, late `terminate/ref/unref` after natural exit, nested-worker lifetime, ASAN DNS teardown, and worker termination while server streams are active. That is strong, recently maintained lifecycle coverage. This scout found no specific unoccupied worker hypothesis strong enough to outrank the child-process discriminator.

Disposition: sampled and parked.

### Package-manager replacement

Global executable replacement already has Fieldwork #345 with a concrete source boundary and failure-injection plan.

Disposition: occupied; no duplicate work.

### Child-process timer liveness

The `.unref()` behavior of Bun's timeout timers already has active upstream work in [Bun PR #35805](https://redirect.github.com/oven-sh/bun/pull/35805).

Disposition: occupied upstream; use only as context for the distinct double-delivery probe.

## Competing explanations

### H1 — duplicate delivery is observable

Both same-deadline timers call `child.kill(SIGUSR1)` before the child exits, producing two handler executions.

Discriminator: receipt count `2` under Bun while Node records `1`.

### H2 — native process state coalesces the second send

The first signal changes native handle state quickly enough that `ChildProcess.kill()` rejects the second send.

Discriminator: both runtimes record `1`.

### H3 — timer ordering or stream teardown changes the outcome

`execFile()`'s own `kill()` destroys stdio before signalling, while the `spawn()` timer only signals. Their order could affect callback timing or process state even when the receipt count remains one.

Discriminator: record count plus callback error, exit code, and terminating signal; extend the probe only if the basic count differs from the predicted outcomes.

## Ranked branch candidates

1. **Execute the `execFile()` double-timeout signal-count probe.** Strongest candidate because the source divergence is narrow, the control is explicit, the public compatibility boundary is clear, and the test can falsify the hypothesis quickly.
2. **Continue #345 separately.** Package-manager executable replacement already has a bounded Fieldwork lane and deserves its own failure-injection evidence.
3. **Return to workers only after a source-specific gap appears.** Current lifetime tests already cover several high-risk teardown races.

## Evidence classification

- Bun timer ownership and call flow: `source-read`.
- Node comparison behavior from implementation: `source-read`.
- Node 22.16.0 signal-count control: `model-executed` comparison evidence.
- Worker teardown coverage: `source-read`.
- Duplicate signal consequence in Bun: `target-test-prepared`; execution receipt absent.
- Broader operational impact: `Unknown` until the Bun discriminator runs and a realistic caller consequence is identified.

## Recommendation

Run the retained discriminator against the pinned Bun revision or record the exact newer Bun revision used. If Bun records two signals while Node records one, open a narrow finding or campaign for target-native regression coverage and the smallest repair that leaves `execFile()` with one timeout owner. If both record one signal, retain the negative result and stop this branch unless execution reveals another concrete difference.

No Bun repository mutation or maintainer-facing interaction occurred during this scout.