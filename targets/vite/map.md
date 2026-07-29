# Target Map: Vite

Repository: https://redirect.github.com/vitejs/vite

## In simple words

A development and build toolchain whose plugin graph, module resolution, invalidation, filesystem watching, and production build paths affect many JavaScript applications.

## Areas worth understanding

- plugin ordering and lifecycle;
- module resolution and virtual modules;
- dependency optimization;
- HMR and invalidation;
- filesystem watching and path normalization;
- dev versus build divergence;
- SSR and environment boundaries;
- performance on realistic project graphs.

## Evidence we can produce

- minimal plugins and virtual modules;
- deterministic HMR and invalidation traces;
- path and filesystem fixtures;
- dev/build comparison cases;
- integration trials in Elatura, Scrapbook, Renderprove, or Proofwake;
- performance baselines.

## Entry standard

Map the plugin and module graph responsible for the behavior. A change should preserve correctness, reduce invalidation or build cost, improve compatibility, or make a demonstrated integration safer.

## Stop conditions

- the behavior is application configuration rather than toolchain behavior;
- the result is only cosmetic warning text;
- the experiment lacks a stable project graph or revision;
- a broad plugin API redesign is required before a bounded failure is established.
