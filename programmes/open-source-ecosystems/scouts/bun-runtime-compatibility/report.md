# Bun runtime compatibility scout

Issue: #705  
Programme: #207  
Parent scout: #209  
Target: `oven-sh/bun` / `target:bun`  
Worker: `chatgpt:gpt-5.6-sol`  
Retrieval date: 2026-08-08  
Exact Bun source inspected: `f972c287f9b7a71754b0b0b1cd18722aa3c75280`  
Comparison Node source: `aed4eaf89dd8d47b9e399bccecc9a9fc588e0284`  
Claim scope: `interface`  
Automated upstream contact authorized: `false`

## Outcome

Confirmed Node-compatibility defect and locally validated repair.

Bun's `child_process.execFile()` gave one timeout two owners: it forwarded `timeout` and `killSignal` into internal `spawn()`, which armed one timeout kill, while `execFile()` armed another timeout kill itself. Current Node keeps the timeout at the `execFile()` layer and does not forward those two options to `spawn()`.

The divergence was first predicted from source, then reproduced on a user-run Mac with Bun `1.3.14+0d9b296af`, and then reproduced again against a debug build from the exact inspected Bun revision.

The user manually opened Bun pull request [#37186](https://redirect.github.com/oven-sh/bun/pull/37186), `node:child_process: avoid duplicate execFile timeout kill`.

Fieldwork automation made no upstream mutation. The upstream pull request and subsequent branch updates were human-performed.

## Source map

At Bun `f972c287f9b7a71754b0b0b1cd18722aa3c75280`:

1. `spawn()` validates and owns its own optional timeout.
2. `spawn({ timeout, killSignal })` arms a timer that calls `child.kill(killSignal)`.
3. `execFile()` passed its `timeout` and `killSignal` into that internal `spawn()` call.
4. `execFile()` also armed its own timeout timer, whose local kill helper tears down buffered stdout/stderr and calls `child.kill(options.killSignal)`.

At Node `aed4eaf89dd8d47b9e399bccecc9a9fc588e0284`, `execFile()` calls `spawn()` without `timeout` or `killSignal`; the `execFile()` layer owns the deadline.

## Runtime confirmation

### Installed Bun receipt

User-run macOS probe under Bun `1.3.14+0d9b296af`:

```json
{
  "runtime": "bun 1.3.14",
  "killCallCount": 2,
  "killCalls": [19, 19],
  "exitCode": null,
  "signalCode": null
}
```

A single `execFile()` timeout therefore reached `ChildProcess.kill()` twice while the child remained alive.

Node 22.16.0 control for the same mechanism recorded one timeout-driven kill call.

### Exact-source fail-before

The user built Bun from `f972c287f9b7a71754b0b0b1cd18722aa3c75280` on macOS and added the focused regression before changing production code.

```text
bun test v1.4.0 (f972c287f)
Expected length: 1
Received length: 2
✗ execFile timeout invokes ChildProcess.kill once
0 pass
1 fail
```

This established the defect on the exact inspected source rather than only on an installed release build.

## Repair

The production repair is intentionally small: remove these fields from `execFile()`'s internal `spawn()` options:

```diff
-    timeout: options.timeout,
-    killSignal: options.killSignal,
```

`execFile()` keeps its existing timeout logic. `spawn()` still supports its own timeout when callers use `spawn()` directly.

This matches Node's ownership boundary.

## Regression test

The submitted regression lives in `test/js/node/child_process/child_process.test.ts` and is POSIX-only.

It launches `sleep 10` with `timeout: 300` and non-terminating `SIGCONT`, wraps the returned `ChildProcess.kill()` method, and checks the timeout behavior while the child remains alive.

The final submitted form was refined after automated review:

- wait for the first observable timeout kill rather than sleeping for the whole timeout window;
- allow a bounded 100 ms polling window for a second timeout owner to reveal itself;
- assert the exact platform-correct signal using `node:os` `constants.signals.SIGCONT`, because Bun sanitizes signal names to numeric values before this call path;
- clean up with the original unwrapped `kill("SIGKILL")`, keeping cleanup outside the measured call list.

Current upstream PR head observed read-only: `1e71275eb909099c22c193126527a3b078a02fd2`.

CodeRabbit's latest review of the refined test reported no actionable comments.

## Pass-after and controls

After removing only the two forwarded fields, the identical focused regression passed:

```text
bun test v1.4.0 (f972c287f)
✓ execFile timeout invokes ChildProcess.kill once
1 pass
0 fail
```

Additional local validation:

- full `test/js/node/child_process/child_process.test.ts`: passed with expected skips;
- `test-child-process-exec-timeout-expire.js`: exit `0` under Bun's intended Node-test configuration;
- `test-child-process-exec-timeout-kill.js`: exit `0` under Bun's intended Node-test configuration.

Running those vendored Node files through the repository's full local runner also surfaced small LeakSanitizer teardown reports. Direct execution with the same Node-test config and event-loop-drain behavior passed, so those LSAN reports were not treated as timeout-assertion regressions from this two-line JS repair.

## Retained discriminator artifact

`artifacts/execfile-timeout-signal-count.mjs` remains the source-independent discriminator used during the scout.

It counts parent-side calls to `ChildProcess.kill()` separately from child-side signal receipts. That distinction is important because ordinary POSIX signals can coalesce while pending, so one child handler execution can hide multiple signal-send attempts.

## Upstream submission

Human-created Bun PR: [#37186](https://redirect.github.com/oven-sh/bun/pull/37186).

The PR is open for maintainer review. Fieldwork automation continues to treat `oven-sh/bun` as read-only and will not comment, react, edit, merge, close, or otherwise mutate the upstream repository or PR.

Human-performed upstream interaction recorded:

- fork created by user;
- repair branch pushed by user;
- PR #37186 opened by user;
- test refinements pushed by user after review feedback.

## Overlap and surrounding code

Fieldwork #345 owns Bun global executable replacement atomicity and remains separate.

Fieldwork #457 records `findPackageJSON`, `threadCpuUsage`, and async-generator inspection as occupied Bun work.

Bun [PR #35805](https://redirect.github.com/oven-sh/bun/pull/35805) addresses timeout-timer event-loop liveness. It is related to timeout implementation but distinct from duplicate `execFile()` timeout ownership.

Adjacent child-process IPC backpressure, advanced serialization, stdio stream passing, spawn-failure normalization, piped-stdio Socket parity, and diagnostics-channel gaps already had public ownership and were excluded from this lane.

Worker teardown was sampled and parked because current Bun main already had focused lifetime regression coverage.

## Evidence classification

- Bun timeout ownership and call flow: `source-read`.
- Node comparison implementation: `source-read`.
- Node 22.16.0 comparison control: `model-executed`.
- Installed Bun duplicate kill behavior: `target-executed`.
- Exact Bun source fail-before: `target-executed`.
- Two-line repair focused pass-after: `target-executed`.
- Full Bun child-process test file: `target-executed`.
- Two relevant vendored Node timeout controls: `target-executed`.
- Upstream submission state: human-performed, open for review.

## Recommendation

Scout work is complete for this candidate. The actionable result is now upstream as human-submitted PR [#37186](https://redirect.github.com/oven-sh/bun/pull/37186).

No further automated upstream action is authorized. Any future Fieldwork work should be limited to read-only observation or durable recording of a user-provided/observed upstream outcome.
