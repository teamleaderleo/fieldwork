# Upstream issue draft

Status: **DRAFT — DO NOT POST**

Public upstream contact authorized: `false`

## Proposed title

`Miniflare disposal can skip workerd termination when an earlier cleanup hook rejects`

## Proposed body

### Summary

`Miniflare.dispose()` currently awaits Browser Rendering cleanup and proxy-client disposal before calling `Runtime.dispose()`.

That ordering allows either earlier hook to prevent the workerd termination request:

- a rejection exits the cleanup `finally` block before `Runtime.dispose()` is reached;
- an unresolved promise leaves disposal suspended before `Runtime.dispose()` begins.

`Runtime.dispose()` already requests workerd termination synchronously before returning its child-exit promise. Starting it before awaiting independent cleanup hooks would preserve runtime ownership even when another teardown step fails or remains pending.

### Current source

At current `main` revision `95d9b12f2c707f254b66b446e0bd9fd6b8b7d96d`, the relevant sequence in `packages/miniflare/src/index.ts` is:

```ts
await this.#closeBrowserProcesses();
this.#removeExitHook?.();
await this.#proxyClient?.dispose();
await this.#runtime?.dispose();
```

`Runtime.dispose()` clears the child reference, destroys the child streams, sends `SIGKILL`, and returns the process-exit promise.

### Minimal target-native controls

A focused regression test can use a real Miniflare instance and exported prototypes:

1. make `ProxyClient.prototype.dispose()` reject once;
2. call `Miniflare.dispose()`;
3. observe `ChildProcess.prototype.kill()` for the workerd child.

Current behavior preserves the proxy rejection but does not request workerd termination during the first disposal.

A second control leaves proxy cleanup pending. Current behavior does not request workerd termination until that promise is released.

A negative control injects a later `DevRegistry.dispose()` rejection and confirms workerd termination already occurred.

### Proposed invariant

Once `Miniflare.dispose()` begins its cleanup phase, it should initiate termination of its owned workerd process before awaiting independent teardown hooks.

### Proposed implementation direction

Invoke `Runtime.dispose()` before the browser/proxy awaits, retain its returned promise, attach a rejection observer, then preserve the existing completion order by awaiting browser cleanup, proxy cleanup, and finally the retained runtime-exit promise.

This keeps the change local to Miniflare disposal and leaves broader cleanup aggregation and timeout policy for separate discussion.

### Questions

1. Is any Browser Rendering or proxy-client cleanup expected to require a live workerd process after `Miniflare.dispose()` has begun?
2. Should runtime termination initiation be treated as the first ownership action in the cleanup phase?
3. Would maintainers prefer this narrow ordering fix or a broader phase-wide cleanup/error-aggregation design?

### Related public work

- `#14903` reports a live workerd child after parallel Vitest files complete. That report is a symptom match; this issue does not claim the same cause without a runnable reproduction.
- `#12025` established immediate stream destruction and `SIGKILL` inside `Runtime.dispose()`.
- `#13078` isolated best-effort temporary cleanup after runtime disposal.
- `#14727` bounded Browser Rendering process shutdown.

### Scope

This proposal covers runtime termination initiation only. It excludes:

- aggregation of simultaneous teardown errors;
- initialization-error precedence;
- generic cleanup deadlines;
- Vite owner handoff;
- Durable Object runtime behavior.

## Posting checklist

- [ ] Explicit authorization to contact public upstream is recorded.
- [ ] Current upstream head is refreshed.
- [ ] The focused baseline controls have executed and receipts are linked.
- [ ] Public links use the current source revision.
- [ ] The issue avoids claiming that `#14903` has this cause.
- [ ] Internal Fieldwork links and private operational details are absent.
