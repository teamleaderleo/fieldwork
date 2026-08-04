# Upstream issue draft

## In simple words

This issue-first draft describes the source-proven ownership defect without claiming a specific public incident has the same cause. A clean candidate now exists and the browser cleanup path has been inspected. The draft must not be posted until the repository owner authorizes public upstream contact.

Status: **DRAFT — DO NOT POST**

Public upstream contact authorized: `false`

## Proposed title

`Miniflare disposal can skip workerd termination when an earlier cleanup hook rejects`

## Proposed body

### Summary

At pinned revision `95d9b12f2c707f254b66b446e0bd9fd6b8b7d96d`, `Miniflare.dispose()` awaits Browser Rendering cleanup and proxy-client disposal before calling `Runtime.dispose()`.

That ordering allows either earlier hook to prevent the workerd termination request:

- a rejection exits cleanup before `Runtime.dispose()` is reached;
- an unresolved promise leaves disposal suspended before `Runtime.dispose()` begins.

`Runtime.dispose()` requests workerd termination synchronously before returning its child-exit promise. Starting it before awaiting independent cleanup hooks preserves runtime ownership when another teardown step fails or remains pending.

### Proposed invariant

Once `Miniflare.dispose()` begins its cleanup phase, it should initiate termination of its owned workerd process before awaiting independent teardown hooks.

### Prepared implementation

A clean owned-fork candidate exists at `d668e318f5e6b0c1e2cbd66ac4b46d8cddbca642`:

- invoke `Runtime.dispose()` before browser and proxy awaits;
- retain and immediately observe its promise;
- preserve completion order by awaiting browser cleanup, proxy cleanup, then runtime exit;
- retain later dispatcher and resource cleanup order;
- add a patch changeset and three real-runtime controls.

The rejected-proxy test restores its mock and always performs a second disposal so the test completes the remaining Miniflare teardown after the injected failure.

### Browser Rendering boundary

The browser cleanup helper uses its own browser-process handle and CDP WebSocket endpoint, attempts `Browser.close`, and independently kills/waits for the browser process if needed. No direct dependency on a live workerd process was found in that helper.

### Minimal target-native controls

1. Make `ProxyClient.prototype.dispose()` reject once and confirm the first disposal still requests workerd termination; then restore the mock and finish cleanup.
2. Leave proxy cleanup pending and confirm termination is requested before releasing it.
3. Inject a later `DevRegistry.dispose()` rejection and confirm workerd termination already occurred.

### Scope

This proposal covers runtime termination initiation only. It excludes simultaneous-error aggregation, initialization-error precedence, generic cleanup deadlines, Vite owner handoff, Durable Object runtime behavior, and causal claims about public hang reports.

### Questions

1. Should runtime termination initiation be treated as the first ownership action in the cleanup phase?
2. Does any undocumented integration require workerd to remain live while independently owned browser cleanup runs?
3. Do maintainers prefer this narrow ordering fix or a broader phase-wide cleanup/error-aggregation design?

## Posting checklist

- [ ] Explicit owner authorization for public upstream contact.
- [ ] Current upstream head and duplicate/overlap refreshed.
- [ ] Exact-head focused and ordinary results recorded.
- [ ] Public links and contribution-policy requirements refreshed.
- [ ] No causal claim about a public incident without a runnable reproduction.
- [ ] Internal Fieldwork references and private operational details removed.
