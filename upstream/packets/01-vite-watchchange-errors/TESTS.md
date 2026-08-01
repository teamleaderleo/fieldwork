# Tests — Vite `watchChange` error isolation

## In simple words

The failure, predecessor repair, and current source have all run inside Vite. At the current source head, the new three-case Unit 01 regression passes on Windows, the full Linux Node 20/22/24/26 and macOS Node 24 jobs pass, and the repository lint/build/type/format/docs workflow passes. Two Windows full-job attempts failed later in the pre-existing HMR/SSR integration playground; those failures are classified separately from Unit 01.

## Evidence classes

- **Source-read:** inspected exact public and owned source without execution.
- **Model-executed:** disposable reproduction outside the ordinary target suite.
- **Target-executed:** Vite-native test or build ran against a named source revision.
- **Full-gate:** repository-declared ordinary job ran with its material limits named.

## Exact revisions

| Purpose | Revision |
| --- | --- |
| Inspected public Vite base | `e6b6b167afa0a80548829d1f24a0712f9194389a` |
| Research reproduction head | `882e62169e2cc4a8ac91d63aca2337fda4f69e1e` |
| Reviewed predecessor source | `8b5d1ae237bf61031a7436ed8fb0fc1e436b6d78` |
| Current-base replay commit | `5f513983f155a1bb59671b5eb9bc78b76f4ad889` |
| Current canonical source head | `a2ab7ca6183ad74d64066d6706e57a546e355224` |

## Source-read result

At public base `e6b6b167afa0a80548829d1f24a0712f9194389a`:

- `server/index.ts` awaits environment `watchChange` calls with fail-fast `Promise.all` before later change/add/unlink work;
- listener catches log the escaped rejection only after the inner worker has exited;
- `moduleGraph.ts` owns cache invalidation and deletion relations;
- `hmr.ts` owns event-typed HMR work after the watcher transaction reaches it;
- `EnvironmentPluginContainer.watchChange` is asynchronous and exposes synchronous hook throws and asynchronous rejections as rejected environment promises.

Result: the failure path remains present at the inspected public base, and server-level settle-all covers both throw and rejection forms.

## Runtime reproduction

Record: [`teamleaderleo/vite#1`](https://github.com/teamleaderleo/vite/pull/1)

Exact research head: `882e62169e2cc4a8ac91d63aca2337fda4f69e1e`

The retained reproduction uses a virtual module backed by a plugin-added watch file.

Control:

- backing file changes from `alpha` to `beta`;
- module cache invalidates;
- next transform contains `beta`.

Rejecting hook:

- exact hook error is logged;
- cache remains populated;
- HMR is skipped;
- next transform still contains `alpha`.

It passed on Ubuntu Node 20/22/24/26, macOS Node 24, and Windows Node 24. One broad Windows production-build HMR/SSR timeout was classified as unrelated. The original browser-encoded direct-transform request was corrected to the plugin-facing virtual ID before accepting the result.

Evidence class: target-executed reproduction with a stated broad-matrix limit.

## Reviewed predecessor execution

Exact source: `8b5d1ae237bf61031a7436ed8fb0fc1e436b6d78`

Recorded commands:

```sh
pnpm install --frozen-lockfile
pnpm exec oxfmt packages/vite/src/node/server/index.ts packages/vite/src/node/__tests__/server/watchChange-error-isolation.spec.js
pnpm run build
pnpm exec vitest run packages/vite/src/node/__tests__/server/watchChange-error-isolation.spec.js
pnpm exec eslint packages/vite/src/node/server/index.ts packages/vite/src/node/__tests__/server/watchChange-error-isolation.spec.js
```

Result: passed for the change-path regression, build, formatting, and lint. Temporary workflow files were removed by the later canonical head. Exact-head review [`4822979298`](https://github.com/teamleaderleo/vite/pull/4#pullrequestreview-4822979298) accepted semantic identity of the executed predecessor files.

Evidence class: focused target execution at the predecessor head; no predecessor full-gate claim.

## Current target-native test

Exact file: [`watchChange-error-isolation.spec.js`](https://github.com/teamleaderleo/vite/blob/a2ab7ca6183ad74d64066d6706e57a546e355224/packages/vite/src/node/__tests__/server/watchChange-error-isolation.spec.js)

### Change

- initial virtual transform contains `alpha`;
- exact rejecting-hook error reaches the logger;
- `hotUpdate` runs;
- transform cache clears;
- refreshed transform contains `beta`.

### Add

- watcher add maps to Rollup event `create`;
- exact rejection reaches the logger;
- HMR continues to `hotUpdate` with type `create`.

### Unlink

- watcher unlink maps to Rollup event `delete`;
- exact rejection reaches the logger;
- HMR continues to `hotUpdate` with type `delete`.

Current-head result: `packages/vite/src/node/__tests__/server/watchChange-error-isolation.spec.js (3 tests)` passed in the Windows unit job. The complete Windows unit suite passed: 68 files, 913 tests passed, 3 skipped.

Evidence class: target-executed at the current source head contained in the pull-request workflow merge; the exact source head is named separately from the synthetic merge commit.

## Current-head workflows

Exact source head: `a2ab7ca6183ad74d64066d6706e57a546e355224`

### Zizmor

- Run [`30674314445`](https://github.com/teamleaderleo/vite/actions/runs/30674314445): success.

### CI

- Run [`30674314447`](https://github.com/teamleaderleo/vite/actions/runs/30674314447).
- Changed-files: success.
- Lint pipeline: success, including dependency installation, repository build, lint, formatting check, typecheck, documentation tests, and workflow-file checks.
- Linux Build&Test: success on Node 20, 22, 24, and 26.
- macOS Build&Test: success on Node 24.

The successful Build&Test jobs ran unit, serve, bundled-development, and build-mode steps assigned by the Vite workflow.

### Windows attempt 1

Job [`91298369805`](https://github.com/teamleaderleo/vite/actions/runs/30674314447/job/91298369805):

- repository build: passed;
- unit suite: passed;
- Unit 01 focused test: 3/3 passed;
- later ordinary serve failed in existing `playground/hmr-ssr/__tests__/hmr-ssr.spec.ts`, timing out while waiting for the expected HMR console update.

Classification: unrelated existing Windows HMR/SSR integration flake. The failing path is outside the two-file Unit 01 diff and occurred after the focused regression passed.

### Windows attempt 2

Job [`91344104649`](https://github.com/teamleaderleo/vite/actions/runs/30674314447/job/91344104649):

- repository build: passed;
- unit suite: passed;
- Unit 01 focused test: 3/3 passed;
- ordinary serve: passed — 91 files passed, 17 skipped; 1128 tests passed, 165 skipped;
- bundled-development then failed three existing HMR/SSR timing/state assertions in the same playground family;
- build-mode did not run because the prior bundled-development step stopped the Windows job.

Classification: unrelated Windows HMR/SSR integration flake. The failure moved from ordinary serve to bundled-development while Unit 01 remained green and every Linux/macOS full job passed.

### Windows attempt 3

Job [`91344668365`](https://github.com/teamleaderleo/vite/actions/runs/30674314447/job/91344668365) was requested as supplementary full-job evidence and was queued when this receipt was reconciled. Its result can strengthen the ordinary Windows record but is not a reason to alter Unit 01 source without a Unit 01-linked failure.

### Preview

- Run [`30674314449`](https://github.com/teamleaderleo/vite/actions/runs/30674314449): skipped as expected for the internal source PR; no product claim.

## Synthetic merge caveat

GitHub Actions checked out a pull-request merge ref containing source head `a2ab7ca6183ad74d64066d6706e57a546e355224` merged into the owned repository's current default-branch head. The canonical source relation and complete-diff review remain the explicit base-to-head fence `e6b6b167...a2ab7ca6`.

The workflow evidence is therefore current compatibility execution containing the exact source head, not a claim that the synthetic merge commit is the canonical source revision.

## Current classification summary

| Claim | Result | Evidence class | Limit |
| --- | --- | --- | --- |
| Failure exists at inspected public base | confirmed | source-read + target reproduction | inspected base, virtual-module path |
| Change invalidation continues after rejection | passed | target-executed | focused test |
| Add/unlink reach event-typed HMR after rejection | passed | target-executed | hook reachability, not every downstream mutation |
| Build/lint/format/type/docs/workflow checks | passed | full-gate for named lint job | named CI steps only |
| Linux supported Node Build&Test | passed | full-gate | workflow-assigned paths |
| macOS Node 24 Build&Test | passed | full-gate | workflow-assigned paths |
| Windows build/unit/focused test | passed | target/full-gate portions | later HMR/SSR integration flaked |
| Windows ordinary serve | passed on rerun | integration-executed | bundled-development later flaked |
| Windows full job | incomplete | classified harness/integration result | existing HMR/SSR family stopped later steps |

## Additional controls not required by the current claim

- stronger add public-file bookkeeping assertion;
- stronger unlink graph-relation assertion;
- explicit multiple-environment/multiple-rejection logging control.

These may be maintainer-requested follow-ups. Their absence does not negate the current change/add/unlink ownership claim.

## Evidence limits

- Add/unlink hook reachability proves continuation into HMR, not every downstream state mutation.
- The reproduction establishes stale virtual transform output; it does not measure ecosystem prevalence or production impact.
- The Windows HMR/SSR failures are real ordinary-gate observations and remain recorded; classification does not relabel them as passes.
- A new source head, material base move, or new Unit 01-linked failure expires this receipt and requires reconciliation.
