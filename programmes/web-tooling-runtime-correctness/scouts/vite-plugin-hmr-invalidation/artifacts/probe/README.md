# Vite plugin, HMR, and invalidation probe

This probe targets Vite commit `8a245726944ed29225920d49be77c33c6e03afc8` (`8.2.0-beta.0` in `packages/vite/package.json`). It creates disposable projects and checks three source-derived branch candidates:

1. a rejecting `watchChange` hook prevents core module invalidation and preserves stale transformed code;
2. a user `transform` hook with hook-level `order: 'post'` runs after Vite import analysis, so imports injected by that hook are present in the dev response but absent from the dev module graph while the production build includes them;
3. experimental bundled development delivers `watchChange` but exits before `hotUpdate` and `handleHotUpdate` hooks.

## Exact-source run

Build the pinned Vite checkout, then point the probe at its Node entry:

```sh
git clone https://github.com/vitejs/vite.git
cd vite
git checkout 8a245726944ed29225920d49be77c33c6e03afc8
corepack pnpm install
corepack pnpm build
cd /path/to/fieldwork/programmes/web-tooling-runtime-correctness/scouts/vite-plugin-hmr-invalidation/artifacts/probe
VITE_ENTRY="file:///absolute/path/to/vite/packages/vite/dist/node/index.js" npm run probe
```

The probe prints JSON and exits non-zero when a source-derived expectation fails.

## Published-package convenience run

The package version at the pinned revision is `8.2.0-beta.0`. A convenience run can install that exact release, though the commit-pinned checkout remains the authoritative reproduction:

```sh
npm install --no-save vite@8.2.0-beta.0
npm run probe
```

## Local validation performed in Fieldwork

`node --check probe.mjs` passed under Node `v22.16.0`. The execution environment had no Vite package and no network package installation, so the Vite-backed assertions remain ready for execution on a machine with the pinned checkout.
