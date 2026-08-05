# Approaches — Vite `watchChange` error isolation

## Current disposition

`REPAIR`

The earlier server-local environment-settlement helper was necessary but incomplete. It prevented one environment rejection from aborting Vite-owned invalidation and HMR, yet each environment still used fail-fast plugin-level `hookParallel()`.

The selected design now isolates failures at the plugin-notification boundary used by watcher-driven server events while preserving generic hook behavior for other callers.

## Selected approach

### Specialized plugin-level settlement for watcher events

Boundary:

- `EnvironmentPluginContainer.watchChange()` accepts an optional internal error callback;
- watcher-driven server orchestration supplies that callback;
- direct compatibility calls without the callback retain the existing fail-fast path.

Execution policy when the callback is present:

1. select applicable plugins using the existing environment filter;
2. start ordinary hooks in parallel;
3. wrap asynchronous hook results with the existing `handleHookPromise` lifecycle tracker;
4. catch synchronous throws and asynchronous rejections per plugin;
5. report each failure through the callback;
6. treat each failure as settled for barrier purposes;
7. preserve `sequential: true` barriers;
8. wait the final group before returning to invalidation and HMR.

Why it wins:

- it fixes the actual sibling-plugin race;
- HMR cannot overtake a slower `watchChange` hook;
- every plugin failure can be reported;
- synchronous throws do not skip later hooks;
- environment close waits tracked asynchronous hooks;
- successful parallelism and sequential barriers remain intact;
- generic hook callers and the backward-compatible public plugin-container wrapper remain unchanged;
- no aggregate error type or new public configuration is introduced.

Reopening triggers:

- exact-head tests show the internal callback broadens direct compatibility behavior;
- a supported contract says hook failure must veto all later hooks or Vite-owned invalidation;
- environment close does not wait the specialized hook promises;
- a target-native test shows barrier or filtering drift.

## Executed losing approach

### Environment-only `Promise.allSettled`

Old clean head: `a2ab7ca6183ad74d64066d6706e57a546e355224`

Implementation:

- fan out to every environment;
- await environment promises with `Promise.allSettled`;
- log each rejected environment result;
- continue existing Vite work.

What it fixed:

- one environment could no longer suppress invalidation/HMR for the entire watcher transaction;
- change/add/unlink continuation worked with one failing plugin;
- all ordinary gates eventually passed.

Why it loses as the final repair:

An environment promise can reject on the first plugin failure while slower sibling hooks remain pending. The outer helper then considers that environment settled, logs only the first reason, and resumes later Vite work.

This approach remains useful history and a valid first-layer repair, but it is not a complete plugin-notification settlement boundary.

## Retained compatibility path

### Generic fail-fast `hookParallel()` for direct calls

The backward-compatible `server.pluginContainer.watchChange()` wrapper delegates to the client environment without the internal error callback.

Why retained:

- it avoids silently changing direct programmatic callers;
- it confines settle-and-continue semantics to actual Vite watcher transactions;
- it keeps the contribution claim narrow and reviewable.

A structural review should confirm this path remains unchanged. A dedicated control may be added if review identifies a credible regression risk.

## Rejected alternatives

### Change generic `hookParallel()` globally

Rejected because it is shared by unrelated hooks and callers. A global change would alter rejection semantics far beyond file-event orchestration.

### Sequentially await every plugin

Rejected because `watchChange` is a parallel hook. Serializing successful hooks would change performance and contract behavior.

### Catch only the aggregate environment rejection

Rejected because it exposes only the first failure and permits slower siblings to remain live.

### Aggregate all plugin failures and throw after settlement

Rejected because throwing would again require a second catch to preserve Vite-owned work and would invent a new error shape. Individual logging preserves error identity.

### Fire and forget sibling hooks

Rejected because HMR, restart, or close could overtake them.

### Put all later event work in `finally`

Rejected because it would continue after unrelated failures in public-file handling, graph deletion, or HMR rather than isolating only plugin notification.

### Serialize all filesystem events

Deferred. Vite currently allows separate watcher transactions to overlap. Global serialization or coalescing could change latency and semantics and is not required by the reproduced sibling-plugin failure.

### Guard against a throwing custom logger

Deferred as a broader logging-policy question. The ordinary Vite logger contract returns normally, and existing listener catches also depend on that behavior.

## Test approaches

### Retained stale-cache change control

A virtual module reads a watched file. After a rejecting hook, the test proves invalidation occurred by transforming refreshed `beta` content rather than cached `alpha`.

### Retained add/unlink controls

Parameterized controls prove create/delete event mapping, error visibility, and event-typed `hotUpdate` continuation.

### New multi-plugin settlement control

Two failing hooks share one environment:

- fast and slow hooks begin in the same parallel group;
- the fast error is reported while the slow hook remains blocked;
- HMR must not run yet;
- after release, the slow error is reported;
- a sequential hook runs after the whole prior group settles;
- a later ordinary hook runs after that barrier;
- HMR runs last.

### New synchronous-throw control

The first hook throws before returning a promise. A later plugin still receives `watchChange`, the error is reported, and HMR continues.

### Deferred direct-compatibility control

Potential assertion: calling `server.pluginContainer.watchChange()` directly without the internal callback retains fail-fast rejection behavior.

Add only if exact diff review identifies a realistic accidental-path risk; the current implementation preserves it structurally.

## Packaging approach

Canonical work remains:

- packet branch: `p0/435-unit-01-vite-watchchange-errors`
- source branch: `fix/fieldwork-25-watchchange-error-isolation`
- exact public-base mirror: `upstream/unit-01-vite-main-e6b6b167`
- source PR: `teamleaderleo/vite#4`
- packet PR: `teamleaderleo/fieldwork#438`

Temporary execution workflows and trigger branches are non-canonical. They must be absent from the final source diff and closed after the clean candidate is published.

## Adjacent research retained outside the patch

- concurrency and coalescing across separate filesystem events;
- behavior when a custom logger throws;
- error ordering when multiple hooks reject at nearly the same instant;
- environment identity in error reporting;
- restart transactions during pending watcher hooks;
- stronger public-directory add and module-deletion state assertions;
- generic plugin-hook failure policy across other parallel hooks.

See [`ADVERSARIAL_AUDIT.md`](./ADVERSARIAL_AUDIT.md) for the mechanism and evidence model.
