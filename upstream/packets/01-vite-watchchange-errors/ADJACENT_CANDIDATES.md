# Adjacent candidates discovered during Unit 01

## Scope rule

These findings came from reviewing the generic scheduler and lifecycle boundaries around Unit 01. They are not part of the canonical Unit 01 source diff and must not be folded into it without a separate assignment, reproduction, and review fence.

Public upstream interaction remains unauthorized and zero.

## Candidate A — preserve `closeBundle` after dev `buildEnd` failure

### Source mechanism

Vite dev environment close currently performs:

```text
wait tracked plugin promises
await hookParallel('buildEnd')
await hookParallel('closeBundle')
```

A rejected or synchronously throwing `buildEnd` therefore prevents `closeBundle` from running.

`DevEnvironment.close()` awaits `pluginContainer.close()` inside `Promise.allSettled`. The rejected plugin-container close does not necessarily reject the overall environment close, so skipped `closeBundle` cleanup can be silent to the caller.

### Rollup contrast

Rollup explicitly wraps `buildEnd`:

- if the build fails, it calls `buildEnd(error)`;
- if `buildEnd` also fails, it creates a compound error;
- in either case, it still calls `closeBundle`;
- if a successful build's `buildEnd` fails, it calls `closeBundle(buildEndError)` before rethrowing.

This is direct lifecycle evidence that `closeBundle` is intended to run after `buildEnd` failure.

### Risk

A plugin may acquire process, file, socket, worker, or temporary-resource ownership before close. If another plugin's `buildEnd` fails, later `closeBundle` cleanup may be skipped while server close otherwise appears settled.

### Proposed reproduction

Create a dev server with:

1. plugin A whose `buildEnd` throws;
2. plugin B whose `closeBundle` records execution;
3. optional plugin C whose `closeBundle` releases a real bounded resource;
4. explicit `await server.close()`.

Assert:

- plugin B/C `closeBundle` hooks run;
- the primary `buildEnd` error remains observable under the chosen close contract;
- cleanup runs once;
- server close does not leave the resource live.

### Candidate repair directions

- mirror Rollup's `try/catch` around `buildEnd` and always invoke `closeBundle`;
- preserve primary and secondary errors without silently replacing either;
- decide whether `DevEnvironment.close()` should expose, log, or retain lifecycle errors rather than only settling them.

### Current status

No matching current Vite issue or pull request was found by targeted search. No numbered Fieldwork unit currently owns this candidate.

## Candidate B — generic parallel-hook synchronous-throw parity

### Source mechanism

Vite's private generic `hookParallel()` invokes each handler directly while constructing the parallel promise list:

```text
handler.apply(...)
```

A synchronous throw escapes before the next plugin is visited. Later ordinary hooks and any later sequential barrier can be skipped.

Rollup's `PluginDriver.runHook()` starts from `Promise.resolve().then(...)`. A synchronous throw becomes a rejected promise returned to `hookParallel()`. The scheduler can still invoke later ordinary hooks before awaiting the group.

### Affected Vite dev hooks

Current generic callers include:

- `buildStart`;
- public/direct `watchChange` compatibility path;
- `buildEnd`;
- `closeBundle`.

Unit 01 intentionally fixes only watcher-driven server notifications through a specialized scheduler. It does not alter generic semantics.

### Questions requiring contract decisions

- Should all ordinary hooks in a parallel group be invoked even when one throws synchronously?
- Is fail-fast at the group await boundary enough, or should some notification/cleanup hooks settle all errors?
- Which hooks are transaction veto points versus advisory notifications or cleanup?
- Should sequential barriers after a failed group run for cleanup hooks but not build-start hooks?

### Proposed characterization matrix

For each hook class:

1. first ordinary hook throws synchronously;
2. second ordinary hook records whether it ran;
3. optional sequential hook records whether it ran;
4. final ordinary hook records whether it ran;
5. capture caller-visible error and lifecycle state.

Run for:

- `buildStart`;
- direct `watchChange`;
- `buildEnd`;
- `closeBundle`.

Compare Vite dev with Rollup's plugin driver and document intentional deviations.

### Repair caution

Changing generic `hookParallel()` would affect multiple hook contracts and public compatibility behavior. A global patch is inappropriate until the matrix establishes which semantics are shared.

## Candidate C — cleanup-hook settle-all policy

Even after ensuring `closeBundle` is reached, one rejection can fail the parallel group. Ordinary async hooks may already have started, but later sequential hooks can still be skipped.

Potential policy for cleanup hooks:

- invoke every applicable cleanup hook;
- preserve sequential barriers;
- collect all cleanup failures;
- report or aggregate them without hiding the primary lifecycle failure;
- complete as much cleanup as possible.

This policy may be appropriate for `buildEnd`/`closeBundle` while remaining inappropriate for `buildStart`.

## Candidate D — unresolved plugin hook shutdown behavior

Vite tracks asynchronous hook promises and waits them during plugin-container close. This prevents abandonment but means a never-settling hook can make shutdown wait indefinitely.

Questions:

- should server close have a bounded diagnostic timeout for plugin hooks?
- should pending hook diagnostics include plugin name, hook name, and environment?
- should forced shutdown exist, and under whose authority?
- how should this interact with restart rather than terminal close?

Rollup tracks unfinished hook actions and emits diagnostics when unresolved promises would otherwise cause confusing termination. Vite's dev server is long-running and may need a different policy, but the ownership problem is analogous.

## Candidate E — watcher error attribution

Unit 01 preserves each original thrown value and passes it to the configured logger. It does not attach plugin or environment identity.

Potential improvement:

- retain original error identity;
- add structured metadata or contextual text naming the plugin and environment;
- avoid double-wrapping errors already formatted by plugin context helpers;
- keep simultaneous-error ordering explicitly unspecified.

This is diagnostic quality, not continuation correctness, and should remain separate.

## Candidate F — overlapping file-event transactions

Separate add/change/unlink listener workers can overlap. Unit 01 waits every notification within one event but does not serialize events.

Characterization targets:

- two rapid changes to one path;
- atomic-save unlink/add sequences;
- one slow notification followed by a later event;
- restart-sensitive config changes overlapping ordinary source changes;
- event ordering across client and server environments.

Potential policies—per-path queues, global queues, debounce, coalescing, or unchanged concurrency—have different latency and plugin-contract costs. No policy should be selected without an executable matrix.

## Recommended research order

1. Reproduce `buildEnd` failure skipping `closeBundle` in Vite dev.
2. Add a synchronous-throw parity matrix for generic parallel hooks.
3. Decide cleanup-hook settle-all and error-composition policy.
4. Characterize unresolved-hook shutdown diagnostics.
5. Characterize overlapping same-path file events.
6. Consider error attribution after lifecycle semantics are stable.

## Admission criteria for a future numbered unit

A candidate should receive its own unit only after it has:

- a deterministic target-native reproduction;
- exact current source ownership;
- current duplicate/prior-art search;
- a bounded repair direction;
- compatibility and rollback analysis;
- a clean source candidate or a clear issue-first rationale;
- explicit separation from Unit 01.
