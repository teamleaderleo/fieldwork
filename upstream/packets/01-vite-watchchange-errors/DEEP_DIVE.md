# Deep dive — Vite `watchChange` errors and file-event continuation

## In simple words

Vite's dev server owns cache invalidation and HMR after filesystem events. Plugins receive an earlier `watchChange` notification. Today, one plugin rejection aborts the whole event handler, so Vite logs the plugin error yet skips its own later work. The selected fix keeps the error visible and lets Vite finish the work it owns.

## Governing invariant

After Vite accepts a filesystem change, add, or unlink event:

- every relevant plugin environment should receive its `watchChange` notification;
- each notification failure should be observable;
- one plugin failure should not prevent other environments from settling;
- Vite-owned cache, public-file, deletion, and HMR work should proceed under Vite's existing rules.

A plugin hook failure can affect plugin-produced state. It should not silently preserve a stale Vite transform cache merely because the hook ran before invalidation.

## Exact source map

Public base: [`e6b6b167afa0a80548829d1f24a0712f9194389a`](https://github.com/vitejs/vite/commit/e6b6b167afa0a80548829d1f24a0712f9194389a)

Current source: [`a2ab7ca6183ad74d64066d6706e57a546e355224`](https://github.com/teamleaderleo/vite/commit/a2ab7ca6183ad74d64066d6706e57a546e355224)

Primary implementation:

- [`packages/vite/src/node/server/index.ts`](https://github.com/teamleaderleo/vite/blob/a2ab7ca6183ad74d64066d6706e57a546e355224/packages/vite/src/node/server/index.ts)
  - watcher entrypoints: `change`, `add`, `unlink`
  - event workers: `onFileChange`, `onFileAddUnlink`
  - selected helper: `notifyWatchChange`
  - later Vite-owned work: module-graph callbacks and `onHMRUpdate`

Related state owner:

- [`packages/vite/src/node/server/moduleGraph.ts`](https://github.com/vitejs/vite/blob/e6b6b167afa0a80548829d1f24a0712f9194389a/packages/vite/src/node/server/moduleGraph.ts)
  - `onFileChange()` invalidates modules associated with a file
  - `onFileDelete()` removes importer relations for deleted modules
  - `invalidateModule()` clears transform results and propagates invalidation

HMR owner:

- [`packages/vite/src/node/server/hmr.ts`](https://github.com/vitejs/vite/blob/e6b6b167afa0a80548829d1f24a0712f9194389a/packages/vite/src/node/server/hmr.ts)
  - creates event-typed update contexts
  - invokes `hotUpdate` for create, delete, and update
  - invokes legacy `handleHotUpdate` only for update
  - contains its own plugin error handling after the watcher transaction reaches it

Target-native regression:

- [`packages/vite/src/node/__tests__/server/watchChange-error-isolation.spec.js`](https://github.com/teamleaderleo/vite/blob/a2ab7ca6183ad74d64066d6706e57a546e355224/packages/vite/src/node/__tests__/server/watchChange-error-isolation.spec.js)

## Current behavior on public main

The public-base change path performs these operations in order:

1. normalize the file path;
2. check whether tsconfig changes require restart behavior;
3. await `Promise.all` of each environment's `pluginContainer.watchChange` call;
4. call each environment module graph's `onFileChange`;
5. run HMR update processing.

The add/unlink path has the same fail-fast plugin notification before public-file bookkeeping, deletion graph work, and HMR.

The watcher listener attaches `.catch((e) => server.config.logger.error(e))`. This makes a rejection visible after the inner event worker has already exited. Logging occurs; later steps do not.

## Deterministic reproduction

The retained reproduction creates a disposable Vite project with:

- a virtual module;
- a text file read by the virtual module's `load` hook;
- `this.addWatchFile(textFile)` to bind the external file to the module;
- initial file content `alpha`;
- replacement content `beta`;
- a `watchChange` hook that either succeeds or rejects.

Observed control:

- file event reaches Vite;
- module transform cache clears;
- next transform reads `beta`.

Observed rejection case on the pinned research revision:

- exact plugin error reaches the configured logger;
- module transform cache remains populated;
- plugin HMR work is skipped;
- next transform still returns `alpha`.

Runtime evidence lives in [`teamleaderleo/vite#1`](https://github.com/teamleaderleo/vite/pull/1) and the Fieldwork #25 execution updates.

## Consequence and claim boundary

The proved consequence is stale transformed module output in development after a real watched-file change. The reproduction uses a virtual module backed by a plugin-added watch file, which directly exercises the plugin API and Vite module graph.

The packet does not claim:

- a measured prevalence across the Vite ecosystem;
- a production-build defect;
- browser-visible stale state for every plugin;
- recovery from arbitrary partial side effects performed inside a failing plugin hook;
- identical behavior under experimental bundled development, where HMR hook support has separate limits.

## Selected implementation

The helper accepts the normalized file and Rollup event name:

- `create` for add;
- `update` for change;
- `delete` for unlink.

It maps the environment snapshot to each `watchChange` promise, awaits `Promise.allSettled`, and logs every rejected result through `server.config.logger.error`.

Returning normally transfers control back to the existing event worker. No later Vite-owned code is duplicated or moved. This keeps the patch local to the ownership boundary that currently combines plugin notification with Vite's event transaction.

## Why this boundary owns the failure

The failure arises from orchestration in `server/index.ts`, not from generic plugin-hook ordering:

- environment plugin containers already own execution within one environment;
- the server owns fanout across environments;
- the server owns module-graph and HMR continuation after fanout;
- the listener catch can report only after the event worker has aborted.

The server-level helper can preserve per-environment semantics while changing only cross-environment failure aggregation and continuation.

## Multiple environments

`Promise.all` rejects on the first observed rejection. Other promises continue running, but the server stops waiting for their complete result set and reports only the rejection propagated out of the event worker.

`Promise.allSettled` gives the server one stable result per environment. The candidate logs every rejected result and waits for every notification to settle before invalidation/HMR. This preserves the existing ordering boundary: Vite-owned work still begins after all environment notifications finish.

## Add and unlink

The selected helper is shared by all event kinds. The current target-native controls distinguish the new behavior:

- add: `watchChange` receives `create`, its rejection is logged, and `hotUpdate` receives `create`;
- unlink: `watchChange` receives `delete`, its rejection is logged, and `hotUpdate` receives `delete`.

These controls establish continuation through the event-typed HMR boundary. The change control additionally establishes cache invalidation and refreshed content.

## Compatibility

### Plugin API

No signature, option, hook order, or success-path behavior changes.

### Failure behavior

A rejecting plugin can no longer abort Vite's later file-event work. The rejection remains visible. Multiple environment rejections may now produce multiple log calls.

### Timing

The server waits for all environment notifications to settle, as it already intended on the successful path. A first rejection no longer ends the await early.

### Performance

The steady successful path still performs parallel environment notifications followed by the same Vite-owned work. `Promise.allSettled` adds small result allocation only at the environment fanout boundary.

### Rollback

Reverting the helper and restoring the two `Promise.all` calls returns public-base behavior. No persisted format, generated artifact, lockfile, or migration is involved.

## Prior art

[`vitejs/vite#22188`](https://github.com/vitejs/vite/pull/22188) repaired dropped/unhandled watcher promises by attaching listener catches and added error-logging controls for all event kinds. Its review explicitly traced `watchChange` as the escaping hook in these handlers.

Unit 01 keeps that result and closes the later continuation gap. It does not reopen the listener-level error handling design.

## Remaining uncertainty

- Current-head focused and ordinary execution can expose typing, formatting, timing, or platform defects in the expanded test.
- A maintainer may prefer a different location or name for the helper while retaining the same ownership rule.
- Maintainers may ask for stronger add/unlink state assertions beyond reaching event-typed HMR.
- Independent review must confirm that logging every environment rejection matches Vite's logger expectations and that no server-restart path changes the intended transaction.

Evidence that would reverse the selected conclusion would need to show that a rejected `watchChange` hook is contractually intended to veto Vite-owned invalidation/HMR, or that continuing creates a larger correctness failure under a supported plugin contract. No inspected source, test, issue, or prior-art record states that veto contract.
