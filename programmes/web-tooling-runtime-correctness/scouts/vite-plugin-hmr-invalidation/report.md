# Vite plugin, HMR, and invalidation scout

State: `ready-for-synthesis`

- Fieldwork lane: #25
- Programme: #15
- Target hub: #9
- Fieldwork base revision: `09fe47ac92ec9c0c333b4979011f6321795deff2`
- Vite target revision: [`8a245726944ed29225920d49be77c33c6e03afc8`](https://redirect.github.com/vitejs/vite/commit/8a245726944ed29225920d49be77c33c6e03afc8)
- Vite package version at that revision: `8.2.0-beta.0`
- Retrieval date: 2026-07-29
- Upstream contact authorized: `false`
- Claim scope reached: mechanism and interface

## In simple words

Vite's ordinary development path has a clear sequence: plugins receive a filesystem event, each environment's module graph is invalidated, then HMR propagation chooses update boundaries or a full reload. Plugin ordering has two layers: plugin-level `enforce` placement and per-hook `order`. The second layer can place a user transform after Vite's own import analysis.

Three bounded campaign candidates emerged:

1. a rejecting `watchChange` hook exits the filesystem-change handler before Vite invalidates its own caches or runs HMR;
2. a hook-level post transform can inject imports after dev import analysis, leaving the served code and module graph in disagreement while production build analysis still sees the import;
3. experimental bundled development exits before `hotUpdate` and `handleHotUpdate`, so plugin-defined HMR handling is skipped.

The first two can preserve stale code or omit dependency edges. The third is source-confirmed and documented as an experimental compatibility limit; it needs an owned integration trial before promotion.

## Execution boundary

A runnable zero-project-state probe lives at `artifacts/probe/`. It creates disposable Vite projects and checks all three candidates against the pinned source build.

Local validation completed:

```text
node --check artifacts/probe/probe.mjs
Node v22.16.0
result: pass
```

The current execution environment contained no Vite package, no pnpm installation, and no network package installation. The Vite-backed assertions remain `probe-ready`; this report distinguishes source-confirmed behaviour from executed reproduction.

## Plugin ordering map

### Configuration order

`sortUserPlugins` partitions user plugins by `enforce` while preserving order inside each group:

```text
user pre -> user normal -> user post
```

Vite then interleaves those groups with internal plugins. The important high-level order is:

```text
optimized dependencies
package-data watch
pre-alias and alias
user pre
internal resolve / HTML proxy / CSS / transforms / assets
user normal
define / CSS post / HTML / worker / build-pre / glob
user post
build-post / devtools
client injection / CSS analysis / import analysis
```

Sources:

- [`sortUserPlugins`](https://github.com/vitejs/vite/blob/8a245726944ed29225920d49be77c33c6e03afc8/packages/vite/src/node/config.ts#L2357-L2373)
- [`resolvePlugins`](https://github.com/vitejs/vite/blob/8a245726944ed29225920d49be77c33c6e03afc8/packages/vite/src/node/plugins/index.ts#L45-L158)

### Per-hook order

For every hook, Vite sorts participating plugins again by hook-object `order`:

```text
hook order pre -> hook normal -> hook order post
```

This sort uses the full resolved plugin list. A normal user plugin with `transform: { order: 'post' }` therefore runs after normal internal transform hooks, including `vite:import-analysis`, even though the plugin itself appeared earlier in the resolved list.

Hook execution forms:

- `resolveId`: first non-null result wins;
- `load`: first non-null result wins;
- `transform`: waterfall; each result becomes the next hook's input;
- parallel hooks: concurrent by default, with `sequential: true` acting as a barrier.

Sources:

- [per-hook sorting](https://github.com/vitejs/vite/blob/8a245726944ed29225920d49be77c33c6e03afc8/packages/vite/src/node/plugins/index.ts#L178-L233)
- [`resolveId`, `load`, and `transform`](https://github.com/vitejs/vite/blob/8a245726944ed29225920d49be77c33c6e03afc8/packages/vite/src/node/server/pluginContainer.ts#L354-L620)
- [parallel and sequential hook execution](https://github.com/vitejs/vite/blob/8a245726944ed29225920d49be77c33c6e03afc8/packages/vite/src/node/server/pluginContainer.ts#L305-L352)

## Module graph map

Each environment owns a separate `EnvironmentModuleGraph`. A module node records:

- served URL, resolved ID, and clean file path;
- importers and imported modules;
- accepted HMR dependencies and exports;
- imported bindings and self-acceptance;
- transform result, ETag, SSR module, and SSR error caches;
- last HMR and ordinary invalidation timestamps;
- hard or soft invalidation state;
- the subset of imports that were static source imports.

The graph indexes nodes by URL, resolved ID, ETag, and file. Several URLs or queries can map to one resolved module, and one file can map to several module nodes.

Source: [`EnvironmentModuleNode` and `EnvironmentModuleGraph`](https://github.com/vitejs/vite/blob/8a245726944ed29225920d49be77c33c6e03afc8/packages/vite/src/node/server/moduleGraph.ts#L16-L123).

### Graph construction

Dev import analysis resolves imports, creates dependency nodes, records importer edges, HMR accept relationships, imported bindings, and static import URLs. Plugin calls to `this.addWatchFile()` during `load` or `transform` are also inserted as imported graph edges. They stay outside `staticImportedUrls`, so changes to those watched files hard-invalidate the importer.

Sources:

- [`addWatchFile`](https://github.com/vitejs/vite/blob/8a245726944ed29225920d49be77c33c6e03afc8/packages/vite/src/node/server/pluginContainer.ts#L864-L876)
- [load/transform watch-file capture](https://github.com/vitejs/vite/blob/8a245726944ed29225920d49be77c33c6e03afc8/packages/vite/src/node/server/pluginContainer.ts#L1050-L1067)
- [plugin watch files folded into import analysis](https://github.com/vitejs/vite/blob/8a245726944ed29225920d49be77c33c6e03afc8/packages/vite/src/node/plugins/importAnalysis.ts#L839-L878)

Virtual modules use resolved IDs such as `\0virtual:name`; browser-facing URLs are encoded separately, while the graph keeps the resolved ID. File-only entries represent dependencies such as inlined CSS imports that still need to trigger importer updates.

Source: [entry creation and file-only entries](https://github.com/vitejs/vite/blob/8a245726944ed29225920d49be77c33c6e03afc8/packages/vite/src/node/server/moduleGraph.ts#L345-L417).

## Filesystem watch flow

The ordinary dev server creates a chokidar watcher over the project root, config dependencies, environment files, and public directory. On a change event:

```text
normalize path
-> reload tsconfig data when relevant
-> await pluginContainer.watchChange for every environment
-> moduleGraph.onFileChange for every environment
-> handleHMRUpdate
```

Create and delete events follow the same plugin-first model. Delete also detaches importer relationships through `onFileDelete` before HMR.

Sources:

- [watcher creation](https://github.com/vitejs/vite/blob/8a245726944ed29225920d49be77c33c6e03afc8/packages/vite/src/node/server/index.ts#L520-L574)
- [change/add/delete handlers](https://github.com/vitejs/vite/blob/8a245726944ed29225920d49be77c33c6e03afc8/packages/vite/src/node/server/index.ts#L857-L930)

`watchChange` runs only for the client environment by default. A global server option or plugin flag enables per-environment delivery. The same default applies to `buildStart` and `buildEnd` during dev.

Source: [per-environment plugin state and lifecycle flags](https://github.com/vitejs/vite/blob/8a245726944ed29225920d49be77c33c6e03afc8/docs/guide/api-environment-plugins.md#per-environment-state-in-plugins).

## Invalidation behaviour

`onFileChange` finds every module node mapped to the changed file and calls `invalidateModule` with one shared seen set.

Hard invalidation:

- marks the module `HARD_INVALIDATED`;
- removes its transform ETag;
- clears transform, SSR module, and SSR error caches;
- recurses through importers until an accepted HMR dependency blocks traversal.

Soft invalidation retains the previous transform result so the next request can rewrite import timestamps without a full transform. It applies to JavaScript importers whose source contains a static import edge. Watched-file and glob edges generally force hard invalidation.

Source: [`onFileChange` and `invalidateModule`](https://github.com/vitejs/vite/blob/8a245726944ed29225920d49be77c33c6e03afc8/packages/vite/src/node/server/moduleGraph.ts#L147-L236).

## HMR propagation

`handleHMRUpdate` first handles broad cases:

- config, config dependency, or environment-file changes restart the server;
- changes inside Vite's own client trigger full reload;
- experimental bundled development returns before plugin hot-update hooks.

For ordinary dev, Vite builds a changed-module set for each environment from the file index. The client environment runs first to support legacy mixed client/SSR compatibility. Each `hotUpdate` hook may narrow or replace the affected modules. The legacy `handleHotUpdate` hook runs only for update events and operates on a mixed client/SSR view.

After hooks, every environment runs HMR propagation. `propagateUpdate` walks importers until it finds:

- a self-accepting module;
- an importer that accepts the changed dependency;
- accepted exports covering the imported bindings;
- a dead end that requires full reload.

Circular acceptance is tagged because execution order may require reload. The resulting payload is either an update list, a prune list, or a full reload.

Sources:

- [`handleHMRUpdate`](https://github.com/vitejs/vite/blob/8a245726944ed29225920d49be77c33c6e03afc8/packages/vite/src/node/server/hmr.ts#L413-L681)
- [`updateModules` and `propagateUpdate`](https://github.com/vitejs/vite/blob/8a245726944ed29225920d49be77c33c6e03afc8/packages/vite/src/node/server/hmr.ts#L685-L898)
- [pruned modules](https://github.com/vitejs/vite/blob/8a245726944ed29225920d49be77c33c6e03afc8/packages/vite/src/node/server/hmr.ts#L979-L996)

## SSR and environment boundaries

Client, SSR, and custom environments have separate module graphs and plugin containers while sharing the resolved plugin pipeline. The same plugin instance may run across environments, so mutable plugin state must be keyed by environment.

Client import analysis injects the HMR runtime and records accept calls. SSR import analysis treats HMR transforms as no-ops while preserving existing self-accepting state. The compatibility `server.moduleGraph` combines client and SSR views for legacy APIs.

Sources:

- [environment creation and mixed compatibility graph](https://github.com/vitejs/vite/blob/8a245726944ed29225920d49be77c33c6e03afc8/packages/vite/src/node/server/index.ts#L577-L605)
- [environment-aware plugin hooks](https://github.com/vitejs/vite/blob/8a245726944ed29225920d49be77c33c6e03afc8/docs/guide/api-environment-plugins.md#per-environment-hooks-and-global-hooks)
- [SSR HMR handling in import analysis](https://github.com/vitejs/vite/blob/8a245726944ed29225920d49be77c33c6e03afc8/packages/vite/src/node/plugins/importAnalysis.ts#L849-L878)

## Development and build differences

| Boundary | Ordinary dev | Production build | Build watch |
| --- | --- | --- | --- |
| module processing | on-demand requests through Vite plugin container | full Rolldown graph | Rolldown watch graph |
| `resolveId` / `load` / `transform` | yes | yes | yes |
| `moduleParsed` | omitted | yes | yes |
| output hooks | omitted except close lifecycle | yes | yes |
| `configureServer` | yes | absent | absent |
| module graph | Vite environment graph with HMR metadata | Rolldown graph | Rolldown watch graph |
| invalidation | Vite watcher + environment graphs | one build invocation | bundler watch invalidation |
| HMR | Vite server propagation | absent | absent |
| dependency optimization | enabled when configured | absent | absent |
| hook context `watchMode` | true | false | true |

Vite injects the environment into build hooks and passes the resolved plugin list to Rolldown. Build-specific plugins appear before and after user plugins. The build graph reparses final transformed code, which is a key difference for the post-transform candidate below.

Sources:

- [dev hook coverage](https://github.com/vitejs/vite/blob/8a245726944ed29225920d49be77c33c6e03afc8/docs/guide/api-plugin.md#rolldown-hooks)
- [build plugin composition and Rolldown options](https://github.com/vitejs/vite/blob/8a245726944ed29225920d49be77c33c6e03afc8/packages/vite/src/node/build.ts#L524-L743)
- [`watchMode` resolution](https://github.com/vitejs/vite/blob/8a245726944ed29225920d49be77c33c6e03afc8/packages/vite/src/node/config.ts#L1877-L1889)

## Dependency optimization

`vite:optimized-deps` is the first resolved plugin for ordinary unbundled dev and is disabled for bundled environments. Optimized dependency requests carry browser hashes. A hash mismatch, superseded metadata, or missing old optimized file throws an outdated-request signal so the page can request the current prebundle.

Source: [`optimizedDepsPlugin`](https://github.com/vitejs/vite/blob/8a245726944ed29225920d49be77c33c6e03afc8/packages/vite/src/node/plugins/optimizedDeps.ts#L22-L116).

No branch candidate was retained here: the mapped paths already defend the stale-prebundle boundary with explicit versions and outdated-request handling.

## Test map and visible gaps

Current focused tests cover:

- plugin hook contexts in dev, build, preview, `handleHotUpdate`, and `hotUpdate`;
- logging for rejected `watchChange` hooks on add, change, and unlink;
- basic module-graph invalidation of SSR errors, resolved-ID coalescing, and legacy mixed graphs;
- a bundled-dev HMR playground.

Visible gaps relevant to this scout:

- continuation of core invalidation after a rejected `watchChange` hook;
- import-graph accuracy when a user transform runs after `vite:import-analysis`;
- plugin hot-update hook delivery in bundled development.

Sources:

- [plugin hook tests](https://github.com/vitejs/vite/blob/8a245726944ed29225920d49be77c33c6e03afc8/packages/vite/src/node/__tests__/plugins/hooks.spec.ts)
- [module graph tests](https://github.com/vitejs/vite/blob/8a245726944ed29225920d49be77c33c6e03afc8/packages/vite/src/node/server/__tests__/moduleGraph.spec.ts)
- [bundled-dev HMR playground](https://github.com/vitejs/vite/tree/8a245726944ed29225920d49be77c33c6e03afc8/playground/hmr-full-bundle-mode)

## Ranked branch candidates

### 1. Isolate `watchChange` failures from core invalidation

Proposed campaign branch: `campaign/vite-watchchange-error-isolation`

Status: **source-confirmed, probe-ready**

Minimal scenario:

1. A virtual module reads `state.txt` and registers it with `this.addWatchFile()`.
2. The module is requested once, caching transformed output containing `alpha`.
3. A plugin `watchChange` hook throws when `state.txt` changes to `beta`.
4. The watcher listener catches and logs the rejection.
5. `moduleGraph.onFileChange` and `handleHMRUpdate` were never reached.
6. A later request can reuse the previous transform result containing `alpha`.

Code path:

```text
watcher change
-> await Promise.all(environment.pluginContainer.watchChange)
-> rejection
-> listener catch/logger
-> graph invalidation skipped
-> HMR skipped
```

Consequence: stale transformed code and stale SSR cache can survive a plugin lifecycle failure.

Candidate direction after reproduction:

- preserve core invalidation and HMR even when one plugin's `watchChange` rejects;
- collect and report plugin errors without letting them veto cache invalidation;
- add a regression test that inspects transform cache state and the next transformed result.

Competing concern: some plugins may expect a failed `watchChange` to abort their own update logic. Core invalidation can still proceed while plugin-specific follow-up remains failed.

### 2. Reconcile post-transform imports with the dev graph

Proposed campaign branch: `campaign/vite-post-transform-import-graph`

Status: **source-confirmed ordering, probe-ready consequence**

Minimal scenario:

1. A user plugin uses `transform: { order: 'post' }`.
2. Its transform injects `import './dep.js'` and an HMR accept call into `main.js`.
3. `vite:import-analysis` already ran as a normal transform hook.
4. The dev response contains the new import, while `main.js` lacks the dependency and accept edge in its environment module graph.
5. Production build reparses the completed transform output and includes `dep.js`.

Consequence: dev/build graph disagreement. A later edit to `dep.js` can miss the intended HMR boundary or reload path because the dev graph never recorded the injected edge.

Candidate direction after reproduction:

- define and enforce the latest safe position for transforms that introduce imports;
- run a final graph analysis pass when post transforms mutate import syntax;
- reject or diagnose unsupported post-analysis import injection with a code-level assertion;
- add a regression fixture comparing served code, graph edges, HMR payload, and build output.

A warning-only change would miss the lane's entry standard. Promotion requires a demonstrated stale update, wrong reload, or graph disagreement in the probe.

### 3. Deliver plugin hot-update handling in bundled development

Proposed campaign branch: `campaign/vite-bundled-dev-hotupdate`

Status: **source-confirmed, documented experimental limit, integration evidence needed**

Minimal scenario:

1. A plugin watches external data and implements `hotUpdate` to filter affected virtual modules or send a custom event.
2. Classic dev delivers `watchChange`, then `hotUpdate`.
3. Bundled dev delivers `watchChange`, enters `handleHMRUpdate`, and returns before `hotUpdate` or legacy `handleHotUpdate`.

Consequence: plugin-defined invalidation and custom HMR behaviour disappear in bundled development. A framework or virtual-module plugin can retain stale application state or fall back to an unrelated bundle update path.

The Vite 8.1 release note labels bundled development experimental and says third-party plugins may fail in this mode. The source also carries a TODO for hot-update hook support. Treat this as a compatibility campaign only after an owned trial demonstrates a concrete stale-state or incorrect-update result.

Sources:

- [bundled-dev early return](https://github.com/vitejs/vite/blob/8a245726944ed29225920d49be77c33c6e03afc8/packages/vite/src/node/server/hmr.ts#L469-L473)
- [Vite 8.1 bundled-dev release note](https://vite.dev/blog/announcing-vite8-1#experimental-bundled-dev-mode)

## Negative results and stopped leads

- **Per-environment `watchChange` default:** documented compatibility behaviour. It stays client-only unless the global or plugin flag opts into per-environment delivery. No branch without a concrete plugin failure.
- **Watched-file invalidation:** plugin `addWatchFile` dependencies are represented in the dev graph and deliberately hard-invalidate importers. No missing edge in the ordinary pre-analysis path.
- **Optimized dependency staleness:** version hashes and explicit outdated-request errors already guard the mapped stale-file paths.
- **Config and environment changes:** server restart is intentional and source-explicit.
- **HMR traversal order:** update sending can run across environments concurrently after client-first hook compatibility handling. No demonstrated race consequence was found.
- **Project-specific configuration mistakes:** excluded by lane scope.

## Proposed owned integration trial

Recommended testbed: Renderprove.

Why: Renderprove already owns browser interaction and evidence capture. Elatura currently uses TypeScript builds without Vite, Scrapbook uses Next/Turbopack, and Proofwake is a Node CLI. Adding Vite solely for this scout would manufacture a weak scenario in those repositories.

Trial outline:

1. Create a dedicated Renderprove branch, separate from this Fieldwork branch.
2. Add a disposable Vite fixture with a virtual module backed by an external text or JSON file.
3. Capture initial DOM state, module request, and HMR payload.
4. Edit the watched file under four modes:
   - ordinary dev control;
   - ordinary dev with rejecting `watchChange`;
   - ordinary dev with post-order import injection;
   - bundled development with plugin `hotUpdate`.
5. Capture whether the DOM updates in place, reloads, or remains stale.
6. Run a production build and compare emitted dependency inclusion.
7. Roll back the fixture after retaining a compact reproduction if it proves useful.

The trial has been defined and has not begun. No `testbed:renderprove` label was added.

## Disposition

Promote candidates 1 and 2 into separate campaigns after the pinned probe executes and confirms the expected stale-cache and missing-edge consequences. Keep candidate 3 behind an integration gate because bundled development is experimental and its compatibility limits are already documented.

No upstream issue, discussion, message, pull request, or comment was created or modified.
