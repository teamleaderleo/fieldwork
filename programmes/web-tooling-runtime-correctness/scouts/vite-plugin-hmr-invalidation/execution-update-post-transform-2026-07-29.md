# Vite scout execution update — post-transform import graph

State: `ready-for-synthesis`

- Fieldwork lane: #25
- Fieldwork research PR: #48
- Vite fork research PR: `teamleaderleo/vite#2`
- Vite target revision: `8a245726944ed29225920d49be77c33c6e03afc8`
- Upstream contact: none

## Candidate 2 result: reproduced

The post-transform import graph candidate is now runtime-reproduced in the pinned Vite fork.

The in-tree test runs the same plugin in normal transform order and with hook-level `transform: { order: 'post' }`. The plugin injects an import of `dep.js` and an HMR accept call into an otherwise import-free `main.js`.

### Normal transform order

Observed:

- served dev code contains the injected import;
- the dev module graph records `dep.js` as an imported module;
- the graph records `dep.js` as an accepted HMR dependency;
- Vite injects its HMR context setup;
- changing `dep.js` produces an HMR `update` payload;
- production build includes the dependency sentinel.

### Post transform order

Observed:

- served dev code still contains the injected import;
- the dev module graph omits the dependency;
- the graph omits the accepted HMR dependency;
- Vite's HMR context setup is absent because import analysis already ran;
- the same dependency change produces a `full-reload` payload;
- production build still includes the dependency sentinel because the bundler parses final transformed code.

## Consequence

This is a concrete dev/build disagreement and HMR behaviour difference. The plugin's intended accept boundary is invisible to Vite in dev when introduced after import analysis, so the same update that is accepted in normal order causes a page reload in post order.

More complex virtual-module or stateful plugin graphs could turn the missing edge into stale behaviour, but this reproduction establishes the bounded graph and HMR consequence without claiming every post transform is unsafe.

## Evidence

The reproduction lives in draft PR `teamleaderleo/vite#2`:

```text
packages/vite/src/node/__tests__/server/post-transform-import-graph.spec.js
research/fieldwork-25/post-transform-import/README.md
research/fieldwork-25/post-transform-import/draft-issue.md
```

The test passed active Vite unit-test jobs on Node 20, 22, 24, and 26 on Ubuntu. Remaining platform and integration jobs were still running when this update was written.

## Candidate fix directions

- perform a final graph and HMR metadata extraction pass after post transforms;
- detect imports or HMR syntax introduced after analysis and re-analyse only required metadata;
- constrain post transforms from introducing such syntax through an explicit plugin contract.

A warning-only change would preserve the runtime mismatch.

## Disposition

Candidate 2 now meets the scout's promotion bar for a campaign branch. Candidate 1 and candidate 2 should remain separate because their fixes affect different control-flow and plugin-order boundaries.
