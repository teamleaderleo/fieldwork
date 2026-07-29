# Review audit — 2026-07-30

Target revision: `vitejs/vite@8a245726944ed29225920d49be77c33c6e03afc8`

Upstream contact: none.

## Research and implementation split

The three owned Vite research pull requests remain draft evidence records:

- `teamleaderleo/vite#1` — rejected `watchChange` preserves stale transform state;
- `teamleaderleo/vite#2` — a user post transform can escape dev import/HMR analysis;
- `teamleaderleo/vite#3` — experimental bundled development can observe a file event while skipping plugin `hotUpdate`, leaving browser-visible state stale.

Implementation review moved to separate branches:

- `teamleaderleo/vite#4` — settle environment `watchChange` notifications, report failures, then continue Vite-owned invalidation and HMR;
- `teamleaderleo/vite#5` — keep the existing import-analysis handler unchanged but mark the internal hook `order: 'post'` so it remains last after user post transforms.

Candidate 3 has no fix branch. Bundled development uses a distinct HMR engine and the source contains an explicit TODO for plugin hot-update hooks. Forwarding classic hook results without a defined bundled-patch contract would be premature.

## Precedent correction

[Vite PR 22188 — handle errors in the watchChange hook](https://redirect.github.com/vitejs/vite/pull/22188) merged watcher-listener catches and tests requiring rejected `watchChange` hooks to reach the configured logger. Candidate 1 is a follow-up transactional gap: the listener logs only after the file-event handler has exited, so invalidation and HMR are still skipped.

The portable issue draft on research PR #1 now states this relationship directly.

## Probe corrections

### Post-transform graph lookup

The original candidate-2 test looked modules up by a temporary absolute path. That was not portable:

- macOS canonicalizes `/var` through `/private/var`;
- Windows uses different path identity rules.

The corrected research and fix tests use `EnvironmentModuleGraph.getModuleByUrl()` and match transformed source IDs by normalized suffix. Both corrected branches now pass the full Vite CI matrix.

### Bundled browser formatting

The candidate-3 browser fixture passed its focused classic/bundled comparison but failed the repository formatting check on one multiline callback. The current head contains the formatter's exact single-line form. Its focused browser workflow passes; the corrected broad CI rerun remains active.

## Fix review notes

### PR #4 — watchChange isolation

The final diff is two files. A self-removing owned-branch workflow formatted, built Vite, ran the focused regression, and linted the changed files before committing source.

The new regression proves the `change` path:

- plugin error is reported;
- module cache is invalidated;
- `hotUpdate` remains reachable;
- the next transform reads the new value.

`add` and `unlink` share the same helper and retain the existing error-logging controls from PR 22188, but separate stale-state correctness tests would strengthen an upstream submission.

### PR #5 — final post import analysis

An initial implementation wrapped and reformatted the 500-line handler, creating a review-hostile diff. It was replaced with a shallow metadata wrapper around the unchanged handler. The current diff is two files, 86 additions and one deletion.

The final head passes the full Vite CI matrix and Zizmor. Compatibility review remains necessary before promotion.

Open compatibility questions:

- whether any supported plugin relies on a user post transform running after Vite import analysis;
- whether CSS analysis needs the same explicit-order treatment;
- whether moving import analysis within the post bucket changes source maps or measurable transform cost.

## Portfolio audit findings

The wider owned-repository review found two concrete defects and one coordination failure:

- Fieldwork PR #105 was marked ready while its Codex and Workers SDK cards were already stale; it was returned to draft with a live-state refresh gate.
- Codex PR #17 retains settled read-only receipts in the same permanent 1,024-entry safety budget as potentially mutating operations; a read-heavy session can set irreversible coverage loss without unresolved mutation.
- Workers SDK PR #3 can replace the primary deployment error if its diagnostic reporter throws, contradicting its exact-error-preservation contract.

Fieldwork issue #87 now records repository classes, evidence classes, staleness fields, anti-patterns, and good precedent for the generated coordination board.

## General precedent

Good patterns to preserve:

- exact pinned revisions and exact-head receipts;
- negative controls and rejected hypotheses;
- explicit separation of observation, policy, and mutation authority;
- blocked security PRs remaining blocked despite green CI;
- no-upstream-contact markers;
- closed disposable execution carriers and named canonical replacements.

Patterns to reject:

- stale indexes presented as current;
- model execution described near package execution without distinction;
- one test stack requiring multiple unrelated fixes;
- reporting code that can replace the primary error;
- giant formatting diffs hiding a one-hook change;
- green CI presented as proof of an untested security property;
- PR bodies retaining old dependency or running-job language after the head changes.
