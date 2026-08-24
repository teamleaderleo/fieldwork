# Deep dive — Vite `watchChange` settlement and file-event continuation

## Current disposition

`REPAIR`

The original reproduction remains valid: a rejected plugin notification can preserve stale transformed output by aborting Vite-owned invalidation and HMR. A second adversarial pass found that the first repair stopped one layer too early.

## Governing invariant

After Vite accepts a filesystem change, add, or unlink event:

- every applicable plugin hook should be invoked under existing filtering rules;
- every asynchronous hook should settle before Vite-owned invalidation/HMR begins;
- synchronous throws and asynchronous rejections should remain observable;
- one plugin failure should not skip sibling hooks, sequential barriers, other environments, or later Vite-owned work;
- environment close should wait still-running notification hooks;
- successful parallelism and Rollup-compatible ordering should remain intact.

A plugin may leave its own state incomplete. It should not gain an undocumented veto over Vite's cache coherence merely by rejecting an earlier notification.

## Exact source map

- Inspected public base: `e6b6b167afa0a80548829d1f24a0712f9194389a`
- Last clean but incomplete source: `a2ab7ca6183ad74d64066d6706e57a546e355224`
- Source branch: `fix/fieldwork-25-watchchange-error-isolation`
- Source PR: `teamleaderleo/vite#4`

Primary owners:

### `server/index.ts`

Owns:

- watcher entrypoints for change, add, and unlink;
- fanout across current environments;
- later module-graph, public-file, deletion, restart, and HMR work.

### `server/pluginContainer.ts`

Owns:

- plugin selection within one environment;
- parallel hook groups;
- `sequential: true` barriers;
- promise tracking through `handleHookPromise`;
- waiting tracked work during environment close;
- the backward-compatible direct plugin-container wrapper.

### `server/moduleGraph.ts`

Owns change invalidation and delete graph maintenance.

### `server/hmr.ts`

Owns event-typed hot-update execution after watcher notification and graph work reach it.

## Public-base failure

For change, the inspected server flow is:

1. normalize path;
2. process restart-sensitive files;
3. await every environment's `pluginContainer.watchChange()` through fail-fast `Promise.all`;
4. invalidate each module graph;
5. run HMR.

Add/unlink has the same notification boundary before public-file bookkeeping, delete handling, and HMR.

A listener catch logs the escaped rejection only after the inner worker exits. Visibility is preserved, continuation is not.

## Original deterministic reproduction

A disposable project contains:

- a virtual module;
- a text backing file registered with `this.addWatchFile()`;
- initial `alpha` and replacement `beta` content;
- a `watchChange` hook that either succeeds or rejects.

On the public-base behavior with rejection:

- the error reaches the configured logger;
- the cached transform remains;
- HMR plugin work is skipped;
- the next transform still returns `alpha`.

The corrected target-native reproduction ran across Ubuntu Node 20/22/24/26, macOS Node 24, and Windows Node 24.

## First repair layer: environment settlement

The old clean candidate introduced a server-local helper that used `Promise.allSettled` across environments and logged rejected environment results before returning to existing Vite work.

This fixed:

- cross-environment fail-fast behavior;
- stale-cache continuation with one failing plugin;
- add/change/unlink continuation with one failure.

It passed full ordinary gates after a final Windows rerun.

## Second failure layer: plugin settlement inside an environment

`EnvironmentPluginContainer.watchChange()` still delegated to generic `hookParallel()`. Ordinary parallel batches end with fail-fast `Promise.all`.

With fast and slow failing sibling hooks:

```text
fast:start
slow:start
fast:reject
logged:fast
vite:continues
slow:reject
```

The outer environment-level `allSettled` sees one rejected environment promise and resumes. It does not know that a sibling plugin hook is still running.

### Consequences

- HMR can overtake a slower notification hook.
- Only the first rejection per environment is available to the server result set.
- A synchronous throw can stop later plugin invocation.
- A failed ordinary group can skip a later sequential hook and all following hooks.
- environment close may need to wait a hook that server orchestration already treated as finished.

The original and prior-art controls used one failing plugin, so they did not distinguish this case.

## Rollup-compatible barrier model

`watchChange` is an asynchronous parallel hook. Hook objects can request `sequential: true`.

The compatible model is:

1. start the current ordinary group in parallel;
2. wait the whole group;
3. run the sequential hook alone;
4. start the next ordinary group;
5. wait the final group.

Failure isolation must treat each failed hook as settled without removing these barriers.

## Selected implementation boundary

The specialized path is activated only when watcher-driven server orchestration supplies an internal error callback to `EnvironmentPluginContainer.watchChange()`.

When supplied, the plugin container:

- applies the existing per-environment filter;
- invokes every eligible hook;
- wraps asynchronous results with `handleHookPromise`;
- catches each synchronous throw or rejection;
- reports each failure through the callback;
- preserves sequential barriers;
- waits all groups before returning.

Without the callback, the existing generic fail-fast path remains. This preserves direct `server.pluginContainer.watchChange()` compatibility.

The server still uses environment-level settlement as a final guard for failures outside ordinary hook rejection.

## Lifecycle integration

`EnvironmentPluginContainer.close()` sets the container closed and waits `Promise.allSettled(Array.from(_processesing))` before build-end and close-bundle work.

Using `handleHookPromise` in the specialized watcher path means close and restart participate in the same existing lifecycle tracker. No second registry is introduced.

## Expanded target-native controls

The focused suite now has five cases under the repair carrier.

### Change stale-cache case

Proves exact error visibility, HMR reachability, cache invalidation, and refreshed `beta` output.

### Add and unlink cases

Prove create/delete mapping, exact error visibility, and event-typed HMR continuation.

### Multi-plugin and sequential-barrier case

Proves:

- fast and slow hooks both start;
- fast failure is reported while slow remains blocked;
- HMR has not run;
- slow failure is reported after release;
- sequential and later ordinary hooks run in order;
- HMR runs last.

### Synchronous-throw case

Proves a later hook still runs, the error is reported, and HMR continues.

The repair execution passed formatting, full Vite build, all 5 focused tests, and ESLint. The first clean-packaging attempt then failed because a depth-one checkout did not contain the exact public-base tree used to restore the original CI workflow. A full-history packaging run is correcting only that execution detail.

## Compatibility analysis

### Successful hooks

Parallel groups, arguments, environment filtering, and sequential barriers remain unchanged.

### Failing hooks

Watcher-driven server events now continue to later hooks and Vite-owned work after reporting failures. This is the intended behavior change.

### Direct compatibility wrapper

Calls without the internal callback retain existing fail-fast behavior. The callback is not a new public option.

### Error shape

Errors are reported individually. No aggregate error is introduced, so original error identity is retained. Relative ordering between nearly simultaneous failures is not promised.

### Logger failure

A configured logger that throws can still interrupt reporting. Existing Vite listener catches also assume logger calls return. Changing this would be a broader logging contract and remains outside Unit 01.

### Performance

Successful ordinary hooks remain parallel. The specialized path adds per-hook error handling and small promise bookkeeping only for watcher notifications.

### Rollback

Reverting the specialized helper/callback and server callback restores the prior environment-only candidate. Reverting both repair layers restores public-base behavior. No persisted format, migration, dependency, or generated artifact is involved.

## Adjacent concurrency question

Vite launches separate filesystem event workers independently. Two events can overlap even after every event waits its own hooks.

Unit 01 does not serialize, debounce, or coalesce separate events. Those policies may affect latency, ordering, and plugin expectations and require their own reproduction and contract decision.

## Prior art

Vite PR `#22188` added listener-level catches and error-logging controls for add/change/unlink. It solved dropped watcher rejections but left the event worker fail-fast.

Unit 01 retains that listener behavior and closes two deeper continuation layers:

1. environment-level settlement;
2. plugin-level settlement within each environment.

## Evidence limits

The packet does not claim:

- prevalence across the ecosystem;
- recovery of arbitrary partial state inside a failing plugin;
- global serialization of file events;
- a production-build defect;
- deterministic ordering of simultaneous errors;
- safety when a custom logger throws;
- exhaustive public-file and delete-graph side-effect coverage.

## Reversal evidence

The selected conclusion should reverse only if supported evidence shows one of these:

- rejecting `watchChange` is contractually intended to veto sibling hooks or Vite invalidation/HMR;
- preserving sequential barriers while continuing after failure violates a supported plugin contract;
- tracked notification promises create a supported close/restart regression;
- direct compatibility calls accidentally switch to settle-and-continue behavior;
- the exact target-native controls fail on a clean committed head for a Unit 01-linked reason.

No inspected source, documentation, prior art, or current duplicate record establishes such a veto contract.

See [`ADVERSARIAL_AUDIT.md`](./ADVERSARIAL_AUDIT.md) and [`APPROACHES.md`](./APPROACHES.md) for the retained mechanism and decision history.
