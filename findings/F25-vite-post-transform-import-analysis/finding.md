# F25: Run Vite dev import analysis after user post transforms

Finding state: `comparative-evaluation-active`

Workstream: `B — Browser, web tooling, and runtime boundaries`  
Canonical Fieldwork issue: `#25`  
Canonical finding path: `findings/F25-vite-post-transform-import-analysis/finding.md`  
Canonical implementation: `teamleaderleo/vite#5`  
Exact implementation head: `1a5b6b5327efa43fc4a33ed5ad51553b6d9c37ba`  
Exact base revision: `8a245726944ed29225920d49be77c33c6e03afc8`  
Strongest evidence class: `full-gate` for the fork repository's named CI matrix; browser-visible mechanism established by target execution  
Current review disposition: `EXECUTE compatibility comparison; preferred source direction remains ACCEPT`  
Desk routing: `not-entered`  
Upstream contact authorized: `no`

## In simple words

Vite reads transformed JavaScript to learn which files a page imports and which files can update through hot reload. A plugin can ask to run its transform at the very end. Today that plugin can add an import after Vite already finished reading the file.

The browser receives the import, but Vite's development graph never records it. The candidate makes Vite's internal import analysis run at the end of the same post-transform group so it sees final user-transformed source.

## Why we care

A missing graph edge creates two truths:

- the browser executes code that imports the dependency;
- Vite's dev server believes the dependency and HMR boundary do not exist.

That can produce full-page reloads instead of hot updates, stale graph state, missing hot-context injection, and development behavior that diverges from production build output.

## What happens if we leave it alone

Plugins using hook-level `transform: { order: 'post' }` can inject imports or `import.meta.hot.accept()` calls that are visible in served code yet absent from Vite's module graph. Dependency edits then fall back to full reload. Production build sees final transformed source, so the discrepancy is development-specific.

The affected plugin population and compatibility dependence remain unmeasured.

## Current finding

The strongest current direction is to give the internal `vite:import-analysis` transform `order: 'post'`. Vite already appends this internal server-only plugin after user plugins, so it remains last inside the post-transform bucket and analyzes final user-transformed source without adding a second parse or graph pass.

The source and repository gate are strong. One technical comparison remains before routing the candidate toward delivery: determine whether any supported plugin behavior intentionally depends on transforming after current import analysis and whether a focused ecosystem fixture can distinguish that from accidental ordering.

### Claim table

| Claim | Evidence class | Exact support | Limit |
| --- | --- | --- | --- |
| A user post transform can inject an import after current dev import analysis. | `target-executed` | Vite PR #2 reproduction | Focused scenario |
| The missing import also removes the accepted HMR dependency and hot-context injection. | `target-executed` | PR #2 and PR #5 regression | One plugin pattern |
| Marking the internal hook `order: 'post'` repairs the graph and HMR update. | `full-gate` plus focused assertion | PR #5 at exact head; CI `30487475188`; Zizmor `30487475253` | Ecosystem compatibility outside repository tests remains unmeasured |
| Plugin list order keeps import analysis last within the post bucket. | `source-read` | `packages/vite/src/node/plugins/index.ts` and hook sorting | Depends on current plugin ordering contract |

## System and ownership map

- User plugins can define hook-level transform order.
- `getSortedPluginsByHook()` groups `pre`, normal, and `post` hooks while preserving plugin-list order inside each group.
- `resolvePlugins()` appends internal server-only plugins after user plugins.
- `vite:import-analysis` parses dev code to update module imports, HMR acceptance, and hot-context injection.
- Production build uses the bundler's final parse and already observes the injected import.

## Historical precedent

### Import analysis must observe plugin-injected imports

- Source: https://github.com/vitejs/vite/pull/23029
- Revision or date: merged before the pinned July 2026 base
- Principle supported: imports injected by plugins must be visible to import-analysis behavior.
- Important difference: that precedent concerns optimized dependency files and interop imports. This finding concerns hook ordering in the dev transform pipeline.

### Internal server-only plugins are appended after user plugins

- Source: `packages/vite/src/node/plugins/index.ts` at the pinned base
- Principle supported: Vite already intends internal analysis to run after user behavior.
- Important difference: list order loses to hook-level `order: 'post'`, so current intent is incomplete without hook metadata.

## Approaches considered

### Option A — mark the existing internal hook `order: 'post'`

Why it leads: one analysis pass, existing handler, established hook-order mechanism, focused behavior repaired, full named CI passed.

How it can lose: a representative supported plugin or documented contract demonstrates that post transforms intentionally run after import analysis and require that order.

### Option B — retain current order and document the limit

Attraction: exact current compatibility remains.

Why it currently loses: served code and development graph remain inconsistent for supported post-hook metadata, and the focused HMR failure remains.

How it can win: ecosystem compatibility evidence shows moving analysis breaks a stronger contract than the reproduced graph mismatch.

### Option C — add a second final analysis pass

Attraction: late imports are observed without moving the first pass.

Why it currently loses: extra parsing, duplicate mutation risk, harder merge/idempotency model.

How it can win: a focused prototype preserves both intermediate compatibility and final graph correctness with acceptable cost and no duplicate side effects.

### Deferred — CSS analysis ordering

The confirmed reproduction is JavaScript import/HMR analysis. CSS has a different pipeline and needs a separate finding if reproduced.

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
| Representative plugins that intentionally transform after current analysis | Technical compatibility evidence absent | Run source search and focused ecosystem fixtures before review-ready |
| CSS post transforms and CSS analysis ordering | Separate pipeline | New finding if reproduced |
| Source-map quality after ordering change | No regression observed, no targeted measurement | Add focused compatibility probe |
| Bundled-development plugin behavior | Different HMR engine and existing experimental gap | Separate Vite bundled-dev finding |
| Performance impact of later analysis | Same parse count; no benchmark retained | Benchmark if source review identifies a plausible hot-path cost |

## Exact execution and receipts

| Repository/head | Command or workflow | Platform/environment | Result | Evidence class |
| --- | --- | --- | --- | --- |
| `teamleaderleo/vite@1a5b6b5327efa43fc4a33ed5ad51553b6d9c37ba` | CI `30487475188` | Node 20/22/24/26 Ubuntu; Node 24 macOS and Windows | Lint, formatting, typecheck, docs, unit, serve, bundled dev, and build jobs passed | `full-gate` for named CI |
| Same head | Zizmor `30487475253` | GitHub workflow analysis | Passed | `target-executed` |

## Complete-diff and compatibility review

The exact source candidate is small and the named repository gate passed. The remaining comparison is not a user preference question. It is a technical compatibility question:

1. search current Vite source, docs, tests, and plugin ecosystem for code that depends on post transforms running after import analysis;
2. instantiate the strongest plausible counterexample;
3. compare Option A with a bounded second-pass prototype only if that counterexample survives;
4. refresh the candidate on current main before review-ready.

No public upstream action is authorized.

## Current disposition and desk routing

- Finding state: `comparative-evaluation-active`
- Review disposition: `EXECUTE compatibility comparison; Option A remains preferred`
- Review Queue entry: none until the comparison is complete
- Delivery lane: `not-entered`
- Exact next transition: run current-source overlap and representative plugin compatibility controls
- Clearing condition: Option A survives the strongest supported counterexample, or another option wins through execution
- Required subgates: current-main refresh, complete diff, focused compatibility controls
- Autonomous work remaining: ecosystem/source search, counterexample fixture, current-main refresh
- Non-delegable human decision: none

## Changes to the canonical conclusion

| Date | Pull request or commit | Change in conclusion |
| --- | --- | --- |
| 2026-07-29 | Vite PR #2 | Reproduced browser/dev-graph mismatch and corrected cross-platform probe identity |
| 2026-07-29 | Vite PR #5 | Added narrow explicit-order repair and complete repository CI evidence |
| 2026-07-30 | Exact-head cross-review | Preferred repair survived source and repository review; ecosystem compatibility remained unmeasured |
| 2026-07-31 | Canonical protocol composition | Reclassified from human decision to autonomous comparative evaluation because technical controls can still distinguish options |

## References

- https://github.com/teamleaderleo/fieldwork/issues/25
- https://github.com/teamleaderleo/vite/pull/2
- https://github.com/teamleaderleo/vite/pull/5
- https://github.com/vitejs/vite/pull/23029
- CI run `30487475188`
- Zizmor run `30487475253`
