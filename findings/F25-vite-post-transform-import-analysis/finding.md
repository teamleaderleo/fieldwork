# F25: Run Vite dev import analysis after user post transforms

Finding state: `design-decision-ready`

Workstream: `B — Browser, web tooling, and runtime boundaries`  
Canonical Fieldwork issue: `#25`  
Canonical implementation: `teamleaderleo/vite#5`  
Exact implementation head: `1a5b6b5327efa43fc4a33ed5ad51553b6d9c37ba`  
Exact base revision: `8a245726944ed29225920d49be77c33c6e03afc8`  
Strongest evidence class: `full-gate` for the fork repository's named CI matrix; browser-visible mechanism established by target execution  
Current review disposition: `ACCEPT as design-decision-ready; HOLD public upstream action`  
Desk routing: `Review Queue #213 and Delivery Desk #160 D3`  
Upstream contact authorized: `no`

## In simple words

Vite reads transformed JavaScript to learn which files a page imports and which files can update through hot reload. A plugin can ask to run its transform at the very end. Today that plugin can add an import after Vite already finished reading the file.

The browser receives the import, but Vite's development graph never records it. The candidate makes Vite's internal import analysis run at the end of the same post-transform group so it sees the final source.

## Why we care

A missing graph edge creates two different truths:

- the browser executes code that imports the dependency;
- Vite's dev server believes the dependency and HMR boundary do not exist.

That can produce full-page reloads instead of hot updates, stale graph state, missing hot-context injection, and development behavior that diverges from production build output.

## What happens if we leave it alone

Plugins using hook-level `transform: { order: 'post' }` can inject imports or `import.meta.hot.accept()` calls that are visible in served code yet absent from Vite's module graph. Dependency edits then fall back to a full reload. Production build still sees the final transformed source, so the discrepancy appears only in development.

The affected plugin population and real-world frequency remain unmeasured.

## Current finding

Vite's internal `vite:import-analysis` transform should carry `order: 'post'`. Vite already appends this internal server-only plugin after user plugins, so it remains last inside the post-transform bucket and analyzes final user-transformed source without adding a second parse or graph pass.

### Claim table

| Claim | Evidence class | Exact support | Limit |
| --- | --- | --- | --- |
| A user post transform can inject an import after current dev import analysis. | `target-executed` | Vite PR #2 reproduction | Focused scenario |
| The missing import also removes the accepted HMR dependency and hot-context injection. | `target-executed` | PR #2 and PR #5 regression | One plugin pattern |
| Marking the internal hook `order: 'post'` repairs the graph and HMR update. | `full-gate` plus focused assertion | PR #5 at exact head; CI `30487475188`; Zizmor `30487475253` | Compatibility outside repository tests remains a design question |
| Plugin list order keeps import analysis last within the post bucket. | `source-read` | `packages/vite/src/node/plugins/index.ts` and hook sorting | Depends on current plugin ordering contract |

## System and ownership map

- User plugins can define hook-level transform order.
- `getSortedPluginsByHook()` groups `pre`, normal, and `post` hooks while preserving plugin-list order inside each group.
- `resolvePlugins()` appends internal server-only plugins after user plugins.
- `vite:import-analysis` parses final dev code to update module imports, HMR acceptance, and hot-context injection.
- Production build uses the bundler's final parse and therefore already observes the injected import.

## Historical precedent

### Import analysis must observe plugin-injected imports

- Source: https://github.com/vitejs/vite/pull/23029
- Revision or date: merged before the pinned July 2026 base
- Principle supported: imports injected by plugins must be visible to import-analysis behavior.
- Important difference: that precedent concerns optimized dependency files and interop imports. This finding concerns hook ordering in the dev transform pipeline.

### Internal server-only plugins are appended after user plugins

- Source: `packages/vite/src/node/plugins/index.ts` at the pinned base
- Principle supported: Vite already intends internal analysis to run after user behavior.
- Important difference: list order alone loses to hook-level `order: 'post'`, so the current intent is incomplete without hook metadata.

## Approaches considered

### Retained approach: mark the existing internal hook `order: 'post'`

This keeps one analysis pass, preserves the existing handler, and uses Vite's established hook-order mechanism.

### Declined: run a second import-analysis pass

A second parse adds cost, duplicate mutation risk, and a harder result-merging model. The existing ordering machinery can establish one final pass.

### Declined: prohibit or ignore imports from user post transforms

That would narrow plugin capability and leave served code inconsistent with the graph.

### Deferred: move `cssAnalysisPlugin` into the same explicit order

The confirmed reproduction is JavaScript import/HMR analysis. CSS analysis may have a similar ordering question, but it needs a distinct source and compatibility investigation.

## Edge cases covered

| Edge case or control | Evidence | Result |
| --- | --- | --- |
| Injected static import | PR #5 regression | Dependency appears in served code and graph |
| Injected HMR accept boundary | PR #5 regression | Accepted dependency recorded |
| Hot-context injection | PR #5 regression | `__vite__createHotContext` present |
| Dependency update | PR #5 regression | HMR `update`, not `full-reload` |
| Cross-platform path identity | PR #2 correction | URL-facing graph lookup passes Linux, macOS, Windows |
| Repository CI across Node 20/22/24/26 and major platforms | CI `30487475188` | Passed |
| Workflow static analysis | Zizmor `30487475253` | Passed |

## Edge cases deferred or outside scope

| Edge case | Why deferred | Owning next record or reopening trigger |
| --- | --- | --- |
| Plugins that intentionally expect to transform after import analysis | Compatibility decision | Human design decision before upstream packet |
| CSS post transforms and CSS analysis ordering | Separate pipeline | New finding if reproduced |
| Source-map quality after ordering change | No regression observed, no targeted measurement | Add compatibility probe before land-ready |
| Bundled-development plugin behavior | Different HMR engine and existing experimental gap | Separate Vite bundled-dev finding |
| Performance impact of later analysis | Same parse count; no benchmark retained | Benchmark if reviewers identify risk |

## Exact execution and receipts

| Repository/head | Command or workflow | Platform/environment | Result | Evidence class |
| --- | --- | --- | --- | --- |
| `teamleaderleo/vite@1a5b6b5327efa43fc4a33ed5ad51553b6d9c37ba` | CI `30487475188` | Node 20/22/24/26 Ubuntu; Node 24 macOS and Windows | Lint, formatting, typecheck, docs, unit, serve, bundled dev, and build jobs passed | `full-gate` for named CI |
| Same head | Zizmor `30487475253` | GitHub workflow analysis | Passed | `target-executed` |

## Alternatives and consequences for the decision maker

| Option | What it does | Benefit | Cost or risk | Evidence needed after selection |
| --- | --- | --- | --- | --- |
| A — retain explicit post order | Makes import analysis observe final user transforms | Repairs demonstrated graph/HMR mismatch with a tiny diff | A plugin may rely on running after current analysis | Focused ecosystem compatibility review and current-main refresh |
| B — keep current order and document the limit | Preserves exact current compatibility | No ordering change | Served code and dev graph remain inconsistent for supported hook metadata | Clear contract decision and warning design |
| C — add a second final analysis pass | Observes late imports without moving the first pass | May preserve intermediate behavior | More parsing, duplicate side effects, complex merging | Performance and idempotency design |

Recommendation: **Option A**. It matches the existing internal-plugin ordering intent and has the smallest execution model.

## Current disposition and desk routing

- Finding state: `design-decision-ready`
- Review disposition: `ACCEPT the candidate as the preferred repair direction`
- Review Queue entry: #213
- Delivery lane: `D3`
- Exact next transition: user selects whether Vite's internal analysis contract should always observe final user post transforms
- Clearing condition: selected contract plus current-main compatibility refresh
- User decision requested: approve Option A for promotion toward an upstream-ready packet, or explicitly retain/document the current limitation

## Changes to the canonical conclusion

| Date | Pull request or commit | Change in conclusion |
| --- | --- | --- |
| 2026-07-29 | Vite PR #2 | Reproduced browser/dev-graph mismatch and corrected cross-platform probe identity |
| 2026-07-29 | Vite PR #5 | Added narrow explicit-order repair and complete repository CI evidence |
| 2026-07-30 | Exact-head cross-review | No source defect found; remaining question classified as compatibility/design judgment |

## References

- https://github.com/teamleaderleo/fieldwork/issues/25
- https://github.com/teamleaderleo/vite/pull/2
- https://github.com/teamleaderleo/vite/pull/5
- https://github.com/vitejs/vite/pull/23029
- CI run `30487475188`
- Zizmor run `30487475253`
