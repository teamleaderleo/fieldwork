# Adversarial audit — plugin-level `watchChange` settlement

## Status

Disposition: `REPAIR`

This audit invalidates the earlier environment-only acceptance fence. It records a deeper failure boundary inside each Vite environment and the narrow repair now under execution.

Public upstream interaction remains unauthorized and zero.

## Finding

The earlier source candidate changed the server watcher transaction from fail-fast `Promise.all` across environments to `Promise.allSettled` across environments. That prevents one environment rejection from skipping Vite-owned invalidation and HMR.

Each environment still delegates `watchChange` to generic plugin-container `hookParallel()`. That helper runs ordinary parallel hook groups with fail-fast `Promise.all`.

Environment settlement is therefore not plugin settlement.

## Reproduced control flow

With two failing plugin hooks in one environment, one fast and one slow, the relevant shape is:

```text
fast:start
slow:start
fast:reject
logged:fast
vite:continues
slow:reject
```

The environment promise rejects when the fast hook rejects. The outer server-level `allSettled` considers that environment settled and resumes later Vite work. The slow hook remains live.

Consequences:

1. invalidation or HMR can overtake a slower sibling `watchChange` hook;
2. only the first plugin rejection per environment reaches the server-level result;
3. a later rejection is consumed by an already-rejected `Promise.all` and is not reported by the server logger;
4. a synchronous throw can prevent later hooks in the same parallel group from being invoked;
5. a failed parallel group can prevent a later `sequential: true` barrier and all hooks after it from running.

## Why prior evidence did not catch it

The Unit 01 change/add/unlink controls each used one failing plugin. The merged prior-art Vite repair also tested one rejecting plugin per event kind. Those tests distinguish listener-level visibility and environment-level continuation, but not sibling-plugin settlement.

The old focused suite could remain green while HMR overtook a pending plugin hook.

## Rollup compatibility model

`watchChange` is an asynchronous parallel hook. Rollup-compatible hook objects may set `sequential: true`.

The required barrier behavior is:

1. start the current ordinary parallel group;
2. wait for that group to settle;
3. run the sequential hook alone;
4. resume the next ordinary parallel group;
5. wait for the final group.

The Unit 01 repair must preserve these barriers while changing failure aggregation only for watcher-driven Vite server events.

Changing generic `hookParallel()` globally would broaden the patch across unrelated hooks and consumers. That option remains rejected.

## Selected repair boundary

Add a specialized plugin-container execution path used only when Vite's filesystem watcher supplies an internal error callback.

The specialized path:

- invokes every applicable `watchChange` hook;
- wraps asynchronous hooks with the existing `handleHookPromise` tracker;
- catches synchronous throws and asynchronous rejections per plugin;
- reports each failure through the supplied callback;
- treats a failure as settled for barrier purposes;
- preserves `sequential: true` ordering;
- waits all applicable hooks before returning to invalidation and HMR.

Calls to `server.pluginContainer.watchChange()` without the internal callback retain the prior fail-fast compatibility path.

## Lifecycle finding

`EnvironmentPluginContainer.close()` waits the `_processesing` promise set before build-end and close-bundle hooks. The specialized path should use `handleHookPromise` for every asynchronous `watchChange` result so environment close and restart cannot silently abandon a still-running hook.

This closes a lifecycle gap without adding a second tracking mechanism.

## Adversarial controls

The expanded target-native suite adds:

### Two asynchronous failures and a sequential barrier

- fast and slow hooks start in one parallel group;
- fast rejects and is logged while slow remains blocked;
- HMR must not run yet;
- slow is released, rejects, and is logged;
- a `sequential: true` hook runs only after both prior hooks settle;
- the later ordinary hook runs after the sequential barrier;
- HMR runs last.

### Synchronous throw

- the first hook throws synchronously;
- the error is reported;
- a later plugin's `watchChange` still runs;
- HMR still runs.

The repair carrier executed formatting, full Vite build, the expanded focused suite, and ESLint successfully. The focused suite passed 5/5 tests. The first packaging attempt failed only because a shallow checkout lacked the exact public-base tree needed to restore the original CI workflow; source and test gates had already passed. A corrected full-history packaging run is in progress.

## Adjacent questions classified outside the patch

### Overlapping filesystem events

Vite's watcher listeners launch change/add/unlink transactions independently. Separate events can overlap today. Serializing or coalescing all events could affect latency and semantics and is not justified by the plugin-rejection reproduction. Keep this as a separate characterization candidate.

### Throwing custom logger

The repair assumes the configured logger's `error` method returns normally, matching Vite's ordinary logger contract. A custom logger that throws can still interrupt error reporting. Changing logger-failure policy would be a broader reliability decision and remains an explicit compatibility limit.

### Cross-environment ordering

Environments remain concurrent. Unit 01 requires each environment to settle all applicable plugin notifications before the shared watcher transaction resumes; it does not impose ordering between environments.

### Error aggregation object

No aggregate error is introduced. Every rejection is sent individually through the existing logger interface. This preserves error identity and avoids inventing a new public error shape.

## Losing and rejected options

- **Environment-only `Promise.allSettled`:** fixes one failure level but leaves sibling-plugin races and hidden errors. Losing approach.
- **Global `hookParallel` change:** affects unrelated hooks and direct plugin-container consumers. Rejected as too broad.
- **Sequentially await every plugin:** eliminates parallelism and changes the contract for successful hooks. Rejected.
- **Fire-and-forget failed siblings:** preserves throughput but allows invalidation/HMR and close to overtake hooks. Rejected.
- **Aggregate all errors and throw later:** would again suppress Vite-owned continuation unless caught separately and would alter error shape. Rejected.
- **Serialize every filesystem event:** adjacent concurrency policy, not required by this defect. Deferred.

## Promotion conditions

A new source head can leave `REPAIR` only after:

1. temporary execution workflows are absent from the canonical diff;
2. the exact diff contains only bounded product source and tests;
3. expanded focused tests pass on the committed head;
4. build, formatting, lint, and type checks pass;
5. ordinary cross-platform gates are reconciled;
6. the packet, drafts, receipt, and review fence name the same exact source head;
7. independent review confirms the plugin-level settlement and compatibility boundary.
