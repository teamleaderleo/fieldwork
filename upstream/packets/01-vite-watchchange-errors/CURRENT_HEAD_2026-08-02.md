# Unit 01 exact-head continuation — 2026-08-02

## Why this note exists

The canonical Vite source moved after the previous packet snapshot. This note controls until the packet's larger narrative files are reconciled after the final ordinary-CI aggregate settles.

## Exact identity

- Public base and current public `vitejs/vite` main: `e6b6b167afa0a80548829d1f24a0712f9194389a`.
- Canonical owned branch: `fix/fieldwork-25-watchchange-error-isolation`.
- Superseded clean source: `79fa097750158790ec9bf03d74e6f83d702dd4c2`.
- Current clean source: `ba8ac979ee91c77fdd91304ccde38942e9752133`.
- Source PR: `teamleaderleo/vite#4`.
- Changed-file fence: exactly three files:
  1. `packages/vite/src/node/server/index.ts`;
  2. `packages/vite/src/node/server/pluginContainer.ts`;
  3. `packages/vite/src/node/__tests__/server/watchChange-error-isolation.spec.js`.
- No workflow, trigger, dependency, lockfile, generated output, or Fieldwork-only file remains on the canonical source branch.

## Repair found during P0 continuation

The live PR head had drifted from the documented three-file product head to `acd7160d3297521aadf377411b7f2321a5c3553b`, adding only `.github/workflows/ci.yml` and `.fieldwork-unit-01-restart-trigger`. The canonical branch was restored to the clean product source before making the source correction below.

Ordinary type checking on clean head `79fa097...` exposed two product-source errors:

1. the specialized lifecycle runner read `plugin[hookName]` as optional before passing it to `getHookHandler`;
2. `shouldRunWatchChange()` could return `undefined` through `plugin.perEnvironmentWatchChangeDuringDev` despite declaring `boolean`.

Commit `ba8ac979ee91c77fdd91304ccde38942e9752133` repairs both narrowly:

- assert the hook is present inside the loop produced by `getSortedPlugins(hookName)`;
- compare `plugin.perEnvironmentWatchChangeDuringDev === true` so the helper is strictly boolean.

No lifecycle behavior, ordering, error-reporting, or public API policy changed.

## Exact current-head execution

### Security and metadata

- Zizmor run `30753769710`: **success**.
- Preview release `30753769692`: skipped as expected for this internal PR.

### Ordinary CI `30753769684`

Completed successfully:

- changed-file discovery;
- lint, formatting, typecheck, documentation tests, and workflow-file checks on Ubuntu / Node 24;
- complete Build&Test on Ubuntu / Node 20;
- complete Build&Test on Ubuntu / Node 22;
- complete Build&Test on Ubuntu / Node 24;
- complete Build&Test on Ubuntu / Node 26;
- complete Build&Test on macOS / Node 24;
- complete Build&Test on Windows / Node 24.15.0.

Each Build&Test job passed dependency installation, Vite build, unit tests, ordinary serve tests, bundled-development serve tests, and build tests.

The failure aggregate job completed as skipped. The only non-terminal job at the latest snapshot is the administrative `Build & Test Passed or Skipped` aggregate job `91527020001`, which remains queued after every substantive dependency job succeeded.

## Current disposition

`EXECUTE — exact source and every substantive ordinary gate are green; final administrative aggregate pending`.

A terminal-success aggregate advances the unit to exact-diff review and packet reconciliation without further source work. A failure or cancellation must be classified from that aggregate's own logic; it does not retroactively erase the successful product jobs.

After the aggregate settles, update `README.md`, `TESTS.md`, `REVIEW.md`, the compact receipt, source PR #4, packet PR #438, issue #25, and parent #435 together.

Public upstream interaction remains unauthorized and none occurred.
