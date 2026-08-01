# Tests — Vite `watchChange` error isolation

## In simple words

The failure and predecessor repair have run inside Vite. The current source head is rebased onto public main and adds dedicated add/unlink controls. Zizmor has passed at the current head; the ordinary CI matrix remains queued at this packet revision.

## Evidence classes

- **Source-read:** inspected exact public and owned source without execution.
- **Model-executed:** disposable reproduction outside the ordinary target suite.
- **Target-executed:** Vite-native test or build ran against an exact source revision.
- **Full-gate:** repository-declared ordinary jobs completed at the exact source revision.
- **Prepared:** test exists in source but has no accepted execution receipt at that exact revision.

## Exact revisions

| Purpose | Revision |
| --- | --- |
| Current public Vite base | `e6b6b167afa0a80548829d1f24a0712f9194389a` |
| Research reproduction head | `882e62169e2cc4a8ac91d63aca2337fda4f69e1e` |
| Reviewed predecessor source | `8b5d1ae237bf61031a7436ed8fb0fc1e436b6d78` |
| Current-base replay commit | `5f513983f155a1bb59671b5eb9bc78b76f4ad889` |
| Current canonical source head | `a2ab7ca6183ad74d64066d6706e57a546e355224` |

## Source-read checks at current public base

Inspected at `e6b6b167afa0a80548829d1f24a0712f9194389a`:

- [`server/index.ts`](https://github.com/vitejs/vite/blob/e6b6b167afa0a80548829d1f24a0712f9194389a/packages/vite/src/node/server/index.ts): change/add/unlink await environment `watchChange` through `Promise.all` before later Vite work; listener catches log the escaped rejection.
- [`server/moduleGraph.ts`](https://github.com/vitejs/vite/blob/e6b6b167afa0a80548829d1f24a0712f9194389a/packages/vite/src/node/server/moduleGraph.ts): change invalidation clears cached transform results; delete processing removes importer relations.
- [`server/hmr.ts`](https://github.com/vitejs/vite/blob/e6b6b167afa0a80548829d1f24a0712f9194389a/packages/vite/src/node/server/hmr.ts): `hotUpdate` receives create/delete/update types after the watcher worker reaches HMR.
- [`CONTRIBUTING.md`](https://github.com/vitejs/vite/blob/e6b6b167afa0a80548829d1f24a0712f9194389a/CONTRIBUTING.md): pnpm setup, build, unit, serve, build-mode, and bundled-development commands.

Result: source confirms the failure path remains present on current public main.

## Runtime reproduction

Record: [`teamleaderleo/vite#1`](https://github.com/teamleaderleo/vite/pull/1)

Pinned target: `8a245726944ed29225920d49be77c33c6e03afc8`

Control assertions:

- watched backing file changes from `alpha` to `beta`;
- virtual-module cache is invalidated;
- next transform contains `beta`.

Rejecting-hook assertions:

- exact hook error is logged;
- cache remains populated;
- HMR is skipped;
- next transform still contains `alpha`.

Execution result recorded in Fieldwork #25:

- target-native reproduction passed on Ubuntu with Node 20, 22, 24, and 26;
- passed on macOS with Node 24;
- passed on Windows with Node 24;
- lint, formatting, typecheck, docs, unit, serve, and bundled-development checks passed for the research change;
- one broad Windows production-build HMR/SSR timeout was classified as unrelated to the focused result.

Evidence class: target-executed reproduction with a stated broad-matrix limit.

## Reviewed predecessor source execution

Exact source: `8b5d1ae237bf61031a7436ed8fb0fc1e436b6d78`

Commands recorded by the self-removing workflow:

```sh
pnpm install --frozen-lockfile
pnpm exec oxfmt packages/vite/src/node/server/index.ts packages/vite/src/node/__tests__/server/watchChange-error-isolation.spec.js
pnpm run build
pnpm exec vitest run packages/vite/src/node/__tests__/server/watchChange-error-isolation.spec.js
pnpm exec eslint packages/vite/src/node/server/index.ts packages/vite/src/node/__tests__/server/watchChange-error-isolation.spec.js
```

Assertions at that revision:

- rejecting update notification reaches the configured logger;
- `hotUpdate` is reached;
- virtual-module transform cache clears;
- next transform reads `beta`.

Result: passed. The workflow committed the formatted source/test content and removed its temporary workflow files. Exact-head review [`4822979298`](https://github.com/teamleaderleo/vite/pull/4#pullrequestreview-4822979298) accepted semantic identity between the executed files and predecessor source.

Old ordinary workflow runs:

- CI `30486590733` — `action_required`
- Zizmor `30486590708` — `action_required`
- Preview `30486590736` — `action_required`

Those old runs provide no ordinary-gate pass.

Evidence class: focused target execution at the predecessor exact head; no predecessor full-gate claim.

## Current target-native test inventory

Exact file: [`watchChange-error-isolation.spec.js`](https://github.com/teamleaderleo/vite/blob/a2ab7ca6183ad74d64066d6706e57a546e355224/packages/vite/src/node/__tests__/server/watchChange-error-isolation.spec.js)

### Change case

Prepared assertions:

- initial virtual transform contains `alpha`;
- rejecting `watchChange` error reaches the configured logger;
- `hotUpdate` runs;
- transform cache clears;
- refreshed transform contains `beta`.

This case is semantically retained from the executed predecessor test after current-base replay.

### Add case

Prepared assertions:

- watcher add maps to `watchChange` event `create`;
- exact rejection reaches the logger;
- HMR processing continues to plugin `hotUpdate`;
- `hotUpdate` type is `create`.

### Unlink case

Prepared assertions:

- watcher unlink maps to `watchChange` event `delete`;
- exact rejection reaches the logger;
- HMR processing continues to plugin `hotUpdate`;
- `hotUpdate` type is `delete`.

The add/unlink cases were added in commit [`a2ab7ca6183ad74d64066d6706e57a546e355224`](https://github.com/teamleaderleo/vite/commit/a2ab7ca6183ad74d64066d6706e57a546e355224).

Evidence class at packet creation: prepared on the current exact head, pending CI execution.

## Current-head workflows

Exact source: `a2ab7ca6183ad74d64066d6706e57a546e355224`

| Workflow | Run | Status at this packet revision | Claim |
| --- | --- | --- | --- |
| Zizmor | [`30674314445`](https://github.com/teamleaderleo/vite/actions/runs/30674314445) | success | current-head workflow-security check passed |
| CI | [`30674314447`](https://github.com/teamleaderleo/vite/actions/runs/30674314447) | queued | no current-head CI result yet |
| Preview release | [`30674314449`](https://github.com/teamleaderleo/vite/actions/runs/30674314449) | skipped | expected for this internal source PR; no product claim |

## Commands required for direct focused renewal

Run from the Vite repository root at the final exact source head:

```sh
corepack enable
pnpm install --frozen-lockfile
pnpm run build
pnpm exec vitest run packages/vite/src/node/__tests__/server/watchChange-error-isolation.spec.js
pnpm exec oxfmt --check packages/vite/src/node/server/index.ts packages/vite/src/node/__tests__/server/watchChange-error-isolation.spec.js
pnpm exec eslint packages/vite/src/node/server/index.ts packages/vite/src/node/__tests__/server/watchChange-error-isolation.spec.js
```

Use the exact package-manager version declared by Vite's `packageManager` field.

## Ordinary gates to inspect

The current CI workflow should establish the exact jobs it runs. At minimum, inspect:

- supported Node unit-test matrix;
- macOS and Windows unit coverage;
- lint;
- formatting;
- typecheck;
- documentation checks;
- serve-mode integration tests;
- build-mode integration tests;
- bundled-development tests;
- package build.

A job failure must be classified as product, test, fixture, setup, runner, unrelated baseline, or packaging before changing source.

## Checks prepared but unexecuted at this packet revision

- current-head direct focused Vitest command;
- current-head direct formatter and ESLint commands;
- stronger add public-file bookkeeping assertion;
- stronger unlink graph-relation assertion;
- explicit multiple-environment/multiple-rejection logging control;
- independent exact-head review.

## Evidence limits

- The predecessor test executed only the change case; add/unlink source controls are current-head additions.
- Workflow success should be reported only for jobs that actually complete at the exact final head.
- Add/unlink hook reachability proves continuation into HMR, not every downstream state mutation.
- The reproduction establishes a stale virtual transform; it does not measure prevalence or production impact.
- Any source-head movement expires the current workflow and review fence.
