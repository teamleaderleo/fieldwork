# Approaches — Miniflare runtime-first disposal

## In simple words

The selected repair starts the workerd owner’s existing termination action before independent teardown awaits, without turning the patch into a broad cleanup rewrite. Review confirmed the browser helper owns its own process handle and endpoint, and repaired the rejected-proxy test so it always completes the rest of Miniflare teardown.

## Decision

Select the narrow early-start approach:

1. remove the exit hook;
2. invoke `Runtime.dispose()` immediately and retain its promise;
3. attach a rejection observer to that promise;
4. await browser cleanup;
5. await proxy-client cleanup;
6. await the retained runtime-exit promise;
7. continue the existing later cleanup sequence.

This changes when runtime ownership discharge begins while preserving the surrounding completion order.

## Selected approach — early-start runtime disposal

```ts
let runtimeDisposePromise: Promise<void>;
try {
	runtimeDisposePromise = Promise.resolve(this.#runtime?.dispose());
} catch (error) {
	runtimeDisposePromise = Promise.reject(error);
}
void runtimeDisposePromise.catch(() => {});

await this.#closeBrowserProcesses();
await this.#proxyClient?.dispose();
await runtimeDisposePromise;
```

Advantages:

- repairs both rejected and pending pre-runtime hooks;
- uses current `Runtime.dispose()` semantics, where termination is requested synchronously;
- preserves public API, normal cleanup order, and dispatcher-after-runtime ordering;
- keeps production scope to one source location;
- supports direct real-runtime controls;
- leaves broad cleanup policy separate.

Limits:

- simultaneous failures are observed but not fully aggregated;
- early runtime start precedes browser completion;
- exact-head target execution is still pending.

## Browser Rendering decision

Source review supports the selected ordering. Browser cleanup uses a retained browser-process handle plus a CDP WebSocket endpoint, sends `Browser.close`, and independently kills/waits for that browser process when needed. No direct workerd dependency was found.

This clears the known design question at source level. Target execution can still reveal an undocumented interaction and should be classified when available.

## Test-cleanup decision

The rejected-proxy test must always perform a second `mf.dispose()` after restoring the mock. Awaiting the killed workerd child is insufficient because the first disposal exited before later Miniflare cleanup. The repaired test now completes both the observed ownership action and the remaining lifecycle.

## Rejected alternatives

### Await runtime exit before all other cleanup

Rejected because a slow or failed runtime exit would newly skip/delay browser and proxy cleanup and would change completion order more aggressively than necessary.

### Phase-wide `Promise.allSettled()` and aggregation

Rejected for this unit because it requires a broader phase model, multi-error contract, and compatibility review.

### Deadlines around pre-runtime hooks

Rejected as the primary repair because a quick rejection would still skip runtime disposal and timeout policy is broader than the ownership invariant.

### Catch-and-continue around each hook

Rejected because an unresolved hook would still block runtime termination.

### Pool-level fallback kill

Rejected because it duplicates private ownership knowledge outside Miniflare and leaves other callers exposed.

## Exact current state

- base: `95d9b12f2c707f254b66b446e0bd9fd6b8b7d96d`;
- branch: `upstream/miniflare-runtime-first-disposal`;
- clean head: `d668e318f5e6b0c1e2cbd66ac4b46d8cddbca642`;
- source relation: ahead 1, behind 0;
- boundary: one production file, one target-native test file, one patch changeset;
- source/test repair: complete;
- exact-head workflows: pending;
- final advancement authority: repository owner;
- public upstream contact: unauthorized and not performed.
