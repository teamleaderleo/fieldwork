# Vite scout execution update — 2026-07-29

State: `ready-for-synthesis`

- Fieldwork lane: #25
- Fieldwork research PR: #48
- Vite fork research PR: `teamleaderleo/vite#1`
- Vite target revision: `8a245726944ed29225920d49be77c33c6e03afc8`
- Upstream contact authorized: `false`
- Upstream contact performed: `none`

## Candidate 1 result: reproduced

The `watchChange` error-isolation candidate is now runtime-reproduced in the pinned Vite fork.

A disposable virtual module reads a watched `state.txt` file. The control changes the file from `alpha` to `beta`; Vite invalidates the module and the next transform returns `beta`.

In the rejecting case, the plugin throws from `watchChange`. Vite logs the error, exits the watcher handler before `moduleGraph.onFileChange` and HMR, retains the previous transform result, and the next transform still returns `alpha`.

Evidence lives in draft PR `teamleaderleo/vite#1` on branch `research/fieldwork-25-watchchange-isolation`:

- disposable reproduction under `research/fieldwork-25/watchchange-error/`;
- in-tree Vitest reproduction at `packages/vite/src/node/__tests__/server/watchChange-stale-cache.spec.js`;
- issue draft and fix design in the research directory.

The corrected reproduction passed Vite unit tests on Node 20, 22, 24, and 26 on Ubuntu and Node 24 on macOS and Windows. Lint, formatting, type checking, docs, serve tests, and bundled-dev tests passed. The overall matrix was red only because an unrelated Windows production-build HMR/SSR test timed out.

Evidence labels:

- **Observed:** control refreshes to `beta`.
- **Observed:** rejecting `watchChange` logs the plugin error.
- **Observed:** rejecting case keeps the previous transform cached and returns `alpha`.
- **Documented/source-confirmed:** watcher handlers await plugin `watchChange` before core invalidation and HMR.
- **Inferred fix direction:** report plugin failures while continuing Vite-owned cache invalidation and safe HMR processing.

## Probe correction

The first Fieldwork probe revision called `server.transformRequest()` with the browser-encoded `/@id/__x00__...` URL. Direct server API use must pass the plugin-facing virtual ID. The fork reproduction corrected this to `virtual:fieldwork-state` before the result was accepted.

The all-in-one Fieldwork probe should carry the same correction before it is used as an authoritative runner.

## Next bounded work

Candidate 2, post-transform import graph disagreement, is next. The acceptance bar is:

1. a normal transform injects an import and Vite records the dependency;
2. a hook-level `order: 'post'` transform serves the injected import after import analysis;
3. the dev module graph omits the injected dependency or HMR accept edge;
4. production build includes the dependency;
5. a changed dependency demonstrates an incorrect HMR boundary, reload decision, or stale browser result.

Candidate 3 remains behind the Renderprove integration gate because bundled development is experimental and the missing plugin hot-update delivery is already described as a compatibility limit.
