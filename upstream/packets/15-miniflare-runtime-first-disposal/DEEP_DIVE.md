# Deep dive — Miniflare runtime-first disposal

## In simple words

Miniflare could fail to request termination of its owned workerd child because browser and proxy cleanup were awaited first. The repaired candidate starts runtime disposal before those independent awaits, while preserving their completion order. Source review also found that Browser Rendering cleanup owns its own process handle and CDP endpoint, so no direct dependency on a live workerd process was found.

Date: `2026-08-03`

## Question

Can an awaited teardown hook prevent Miniflare from requesting termination of the workerd child it owns?

## Answer

Yes. At pinned base `95d9b12f2c707f254b66b446e0bd9fd6b8b7d96d`, control flow reaches `Runtime.dispose()` only after awaiting browser cleanup and proxy-client disposal. A rejection exits the cleanup block. An unresolved promise suspends it. Both paths leave runtime termination unstarted.

The clean candidate at `d668e318f5e6b0c1e2cbd66ac4b46d8cddbca642` starts `Runtime.dispose()` first, retains and immediately observes its promise, then awaits browser cleanup, proxy cleanup, and runtime exit in that order.

This establishes and repairs a lifecycle ownership defect. It does not establish trigger frequency or causal identity with a public hang report.

## Runtime ownership boundary

`Runtime.dispose()` performs its ownership actions before returning:

1. reads and clears the child-process reference;
2. destroys stdin, stdout, stderr, and the control pipe;
3. sends `SIGKILL` to workerd;
4. returns the recorded process-exit promise.

That permits a narrow repair: initiate the existing ownership action before independent awaits, retain its completion promise, and preserve the surrounding cleanup order.

## Selected candidate behavior

1. remove the exit hook;
2. call `Runtime.dispose()` and normalize a synchronous throw into a rejected promise;
3. attach an immediate rejection observer;
4. await browser-process cleanup;
5. await proxy-client cleanup;
6. await the retained runtime-exit promise;
7. close dispatchers and continue later teardown.

Properties retained:

- browser cleanup remains before proxy cleanup;
- runtime exit remains before dispatcher closure;
- an earlier browser/proxy failure remains the outward error when it fails first;
- later cleanup order remains unchanged after successful preceding phases;
- repeated runtime disposal remains safe after the child reference is cleared.

## Browser Rendering interaction

`#closeBrowserProcesses()` snapshots and clears Miniflare’s retained browser-process records, then calls `closeBrowserProcess(browserProcess, wsEndpoint)` for each one.

`closeBrowserProcess()`:

- connects directly to the browser’s CDP WebSocket endpoint;
- sends `Browser.close`;
- observes the browser process’s own `hasClosed()` promise;
- falls back to `browserProcess.kill()` and waits for that process to exit.

No call in this helper requires the workerd runtime to remain alive. This source evidence supports early runtime termination. It does not replace exact target execution or prove every undocumented integration expectation.

## Regression controls

### Rejected proxy cleanup

The first disposal must request workerd termination despite the injected proxy rejection. After restoring the mock, the repaired test always calls `mf.dispose()` again to complete remaining teardown, then waits for the killed child’s exit.

The unconditional second disposal is important: child exit alone does not complete dispatchers, loopback resources, registries, and other Miniflare-owned cleanup skipped by the earlier rejection.

### Pending proxy cleanup

The termination request must be visible while proxy cleanup remains pending. The hook is then released and full disposal completes.

### Later cleanup rejection

A later registry rejection must occur after the workerd termination request, proving the observer is specific to the pre-runtime ordering boundary.

## Error boundary

If runtime disposal and an earlier hook both fail, the earlier hook can remain the outward rejection while the runtime rejection is observed by the attached handler. Complete multi-error retention is intentionally excluded. The selected patch repairs ownership discharge without inventing a broad teardown error contract.

## Exact source fence

- base: `95d9b12f2c707f254b66b446e0bd9fd6b8b7d96d`;
- branch: `upstream/miniflare-runtime-first-disposal`;
- head: `d668e318f5e6b0c1e2cbd66ac4b46d8cddbca642`;
- relation: ahead 1, behind 0;
- files: changeset, one production file, one test file;
- no temporary workflow or research artifacts.

## Evidence classification

- base disposal ordering: `source-read`;
- synchronous runtime termination request: `source-read`;
- JavaScript rejection/pending control flow: `model-executed`;
- corrected three-file candidate: `source-read`;
- three target-native controls: `target-test-prepared`;
- browser-process independence: `source-read`;
- clean-head repository validation: pending.

## Limits

No claim is made about frequency, a specific public incident, multi-error aggregation, generic cleanup deadlines, initialization-error precedence, Vite ownership, or Durable Object behavior.
