# Unit 01 exact-head continuation — closed 2026-08-03

## Exact identity

- Public Vite base and current public main: `e6b6b167afa0a80548829d1f24a0712f9194389a`.
- Canonical source branch: `fix/fieldwork-25-watchchange-error-isolation`.
- Canonical source head: `ba8ac979ee91c77fdd91304ccde38942e9752133`.
- Source PR: `teamleaderleo/vite#4`.
- Changed-file fence: exactly:
  1. `packages/vite/src/node/server/index.ts`;
  2. `packages/vite/src/node/server/pluginContainer.ts`;
  3. `packages/vite/src/node/__tests__/server/watchChange-error-isolation.spec.js`.
- No workflow, trigger, dependency, lockfile, generated output, or Fieldwork-only file remains on the canonical source branch.

## Repairs completed

The source PR was restored from a temporary five-file carrier head to the clean three-file product fence.

Ordinary type checking then exposed and caused repair of:

1. an optional hook passed to `getHookHandler` without narrowing;
2. an optional plugin flag leaking from a helper declared to return `boolean`.

Final head `ba8ac979...` fixes both without changing lifecycle policy or public API.

## Final exact-head execution

- Zizmor `30753769710`: **success**.
- CI `30753769684`: **success**.
- Preview `30753769692`: skipped as expected.

CI passed:

- changed-file discovery;
- build, lint, formatting, typecheck, docs, and workflow checks;
- complete Build&Test on Ubuntu Node 20/22/24/26;
- complete Build&Test on macOS Node 24;
- complete Build&Test on Windows Node 24.15.0;
- final `Build & Test Passed or Skipped` aggregate.

The failure aggregate skipped. Every Build&Test job completed build, unit, ordinary serve, bundled-development serve, and build tests.

## Final complete-diff pre-review

`ACCEPT`

The exact three-file comparison was re-read after the final typing repair. No blocking lifecycle, ordering, error-reporting, API, or test defect was found.

The direct public `pluginContainer.watchChange()` path remains fail-fast. The watcher-specific internal path settles and reports each applicable plugin hook, preserves sequential barriers, waits all environments, and allows later Vite-owned invalidation/HMR work to proceed.

The authoritative final records are now `README.md`, `TESTS.md`, `REVIEW.md`, and `receipts/current-head-2026-08-01.md`. This continuation note is closed and no longer carries a pending gate.

## Disposition

`ACCEPT — technically ready for human review`.

Public upstream interaction remains unauthorized and none occurred.
