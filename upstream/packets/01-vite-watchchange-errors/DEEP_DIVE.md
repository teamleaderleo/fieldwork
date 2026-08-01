# Deep dive — Vite `watchChange` errors and file-event continuation

## In simple words

Vite's dev server owns cache invalidation and HMR after filesystem events. Plugins receive an earlier `watchChange` notification. On the inspected public base, one plugin rejection exits the inner event handler, so Vite logs the plugin error yet skips its own later work. The selected fix keeps the error visible and lets Vite finish the work it owns.

## Governing invariant

After Vite accepts a filesystem change, add, or unlink event:

- every relevant plugin environment should receive its `watchChange` notification;
- each notification failure should remain observable;
- one plugin failure should not prevent other environments from settling;
- Vite-owned cache, public-file, deletion, and HMR work should proceed under Vite's existing rules.

A plugin hook failure can affect plugin-produced state. It should not silently preserve a stale Vite transform cache merely because the hook ran before invalidation.

## Exact source map

- Inspected public base: [`e6b6b167afa0a80548829d1f24a0712f9194389a`](https://github.com/vitejs/vite/commit/e6b6b167afa0a80548829d1f24a0712f9194389a)
- Current source: [`a2ab7ca6183ad74d64066d6706e57a546e355224`](https://github.com/teamleaderleo/vite/commit/a2ab7ca6183ad74d64066d6706e57a546e355224)
- Source PR: [`teamleaderleo/vite#4`](https://github.com/teamleaderleo/vite/pull/4)

Primary implementation:

- [`packages/vite/src/node/server/index.ts`](https://github.com/teamleaderleo/vite/blob/a2ab7ca6183ad74d64066d6706e57a546e355224/packages/vite/src/node/server/index.ts)
  - watcher entrypoints: `change`, `add`, `unlink`
  - event workers: `onFileChange`, `onFileAddUnlink`
  - selected helper: `notifyWatchChange`
  - later Vite-owned work: module-graph callbacks and `onHMRUpdate`

Related state owner:

- [`packages/vite/src/node/server/moduleGraph.ts`](https://github.com/vitejs/vite/blob/e6b6b167afa0a80548829d1f24a0712f9194389a/packages/vite/src/node/server/moduleGraph.ts)
  - change invalidation clears transform results and propagates invalidation;
  - delete processing removes importer relations.

HMR owner:

- [`packages/vite/src/node/server/hmr.ts`](https://github.com/vitejs/vite/blob/e6b6b167afa0a80548829d1f24a0712f9194389a/packages/vite/src/node/server/hmr.ts)
  - creates event-typed update contexts;
  - invokes `hotUpdate` for create, delete, and update;
  - invokes legacy `handleHotUpdate` only for update;
  - contains its own plugin error handling after the watcher transaction reaches it.

Plugin notification owner:

- [`packages/vite/src/node/server/pluginContainer.ts`](https://github.com/vitejs/vite/blob/e6b6b167afa0a80548829d1f24a0712f9194389a/packages/vite/src/node/server/pluginContainer.ts)
  - `watchChange` is asynchronous and awaits `hookParallel`;
  - synchronous hook throws and asynchronous rejections reach server orchestration as rejected environment promises.

Target-native regression:

- [`packages/vite/src/node/__tests__/server/watchChange-error-isolation.spec.js`](https://github.com/teamleaderleo/vite/blob/a2ab7ca6183ad74d64066d6706e57a546e355224/packages/vite/src/node/__tests__/server/watchChange-error-isolation.spec.js)

## Current behavior on the inspected public base

The change path performs these operations in order:

1. normalize the file path;
2. check whether tsconfig changes require restart behavior;
3. await `Promise.all` of each environment's `pluginContainer.watchChange` call;
4. call each environment module graph's `onFileChange`;
5. run HMR update processing.

The add/unlink path has the same fail-fast plugin notification before public-file bookkeeping, deletion graph work, and HMR.

The watcher listener attaches a catch that logs the escaped rejection. That catch executes after the inner event worker has already exited. Logging occurs; the later transaction steps do not.

## Deterministic reproduction

The retained reproduction creates a disposable Vite project with:

- a virtual module;
- a text file read by the virtual module's `load` hook;
- `this.addWatchFile(textFile)` to bind the external file to the module;
- initial content `alpha`;
- replacement content `beta`;
- a `watchChange` hook that either succeeds or rejects.

Control result:

- file event reaches Vite;
- module transform cache clears;
- next transform reads `beta`.

Rejecting-hook result on the pinned research revision:

- exact plugin error reaches the configured logger;
- module transform cache remains populated;
- plugin HMR work is skipped;
- next transform still returns `alpha`.

Runtime evidence lives in [`teamleaderleo/vite#1`](https://github.com/teamleaderleo/vite/pull/1), exact research head `882e62169e2cc4a8ac91d63aca2337fda4f69e1e`, and the Fieldwork #25 execution updates.

The reproduction passed on Ubuntu Node 20/22/24/26, macOS Node 24, and Windows Node 24. The original direct-transform probe was corrected to use the plugin-facing virtual ID rather than the browser-encoded URL before the result was accepted.

## Consequence and claim boundary

The proved consequence is stale transformed module output in development after a real watched-file change. The reproduction directly exercises the plugin API and Vite module graph through a virtual module backed by a plugin-added watch file.

The packet does not claim:

- measured prevalence across the Vite ecosystem;
- a production-build defect;
- browser-visible stale state for every plugin;
- recovery from arbitrary partial side effects inside a failing plugin hook;
- identical behavior under experimental bundled development;
- that every add public-file or unlink graph mutation is individually asserted.

## Selected implementation

The helper accepts the normalized file and Rollup event name:

- `create` for add;
- `update` for change;
- `delete` for unlink.

It maps the current environment snapshot to each `watchChange` promise, awaits `Promise.allSettled`, and logs every rejected result through `server.config.logger.error`.

Returning normally transfers control back to the existing event worker. No later Vite-owned code is duplicated or moved. This keeps the patch local to the ownership boundary that currently combines plugin notification with Vite's event transaction.

## Why this boundary owns the failure

The failure arises from orchestration in `server/index.ts`, not from generic plugin-hook ordering:

- environment plugin containers own execution within one environment;
- the server owns fanout across environments;
- the server owns module-graph and HMR continuation after fanout;
- the listener catch can report only after the event worker has aborted.

The server-level helper preserves per-environment semantics while changing only cross-environment failure aggregation and continuation.

## Multiple environments

`Promise.all` rejects on the first observed rejection. Other promises continue running, but the server stops waiting for their complete result set and reports only the rejection propagated out of the event worker.

`Promise.allSettled` gives the server one stable result per environment. The candidate logs every rejected result and waits for every notification to settle before invalidation/HMR. The successful-path ordering boundary remains unchanged: Vite-owned work begins after all environment notifications finish.

## Add and unlink

The helper is shared by all event kinds. The current target-native controls distinguish the behavior:

- add: `watchChange` receives `create`, its rejection is logged, and `hotUpdate` receives `create`;
- unlink: `watchChange` receives `delete`, its rejection is logged, and `hotUpdate` receives `delete`.

These controls establish continuation through the event-typed HMR boundary. The change control additionally establishes cache invalidation and refreshed content.

## Compatibility

### Plugin API

No signature, option, hook order, or success-path behavior changes.

### Failure behavior

A rejecting plugin can no longer abort Vite's later file-event work. The rejection remains visible. Multiple environment rejections may produce multiple logger calls.

### Timing

The server waits for all environment notifications to settle, as it already does on the successful path. A first rejection no longer ends the await early.

### Performance

The successful path still performs parallel environment notifications followed by the same Vite-owned work. `Promise.allSettled` adds a small result allocation at the environment fanout boundary.

### Rollback

Reverting the helper and restoring the two `Promise.all` calls returns inspected public-base behavior. No persisted format, generated artifact, lockfile, or migration is involved.

## Prior art

[`vitejs/vite#22188`](https://github.com/vitejs/vite/pull/22188) repaired dropped/unhandled watcher promises by attaching listener catches and added error-logging controls for all event kinds. Its review traced `watchChange` as the escaping hook in these handlers.

Unit 01 keeps that result and closes the later continuation gap. It does not reopen the listener-level error-handling design.

## Current execution interpretation

At source head `a2ab7ca6183ad74d64066d6706e57a546e355224`:

- workflow security passed;
- repository build/lint/format/type/docs/workflow checks passed;
- full Linux Node 20/22/24/26 Build&Test passed;
- full macOS Node 24 Build&Test passed;
- Windows build, unit, and the three-case Unit 01 regression passed;
- Windows ordinary serve passed on rerun.

Two Windows full-job attempts later failed in the pre-existing HMR/SSR integration playground. The first failure was an ordinary-serve timeout waiting for an HMR console update. The rerun passed ordinary serve and then failed three timing/state assertions in the same family during bundled-development. The moving failure location, unchanged green Unit 01 regression, two-file diff boundary, and green Linux/macOS full matrix support classification as unrelated Windows HMR/SSR integration flakiness.

GitHub's PR workflow used a synthetic merge containing the exact source head on the owned repository's current default branch. That is useful compatibility evidence but does not replace the canonical public-base-to-source comparison.

## Remaining uncertainty

- An independent reviewer must confirm the configured-logger behavior for multiple environment rejections and the compatibility boundary.
- A maintainer may prefer a different helper location or name while retaining the same ownership rule.
- Maintainers may request stronger add public-file or unlink graph-state assertions.
- Windows HMR/SSR integration timing remains noisy outside the changed files.
- The then-current Vite main, duplicate landscape, and contribution policy must be refreshed immediately before any authorized public submission.

Evidence that would reverse the selected conclusion would need to show that a rejected `watchChange` hook is contractually intended to veto Vite-owned invalidation/HMR, or that continuation creates a larger correctness failure under a supported plugin contract. No inspected source, test, issue, review, or prior-art record states that veto contract.
