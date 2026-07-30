# Vite post-transform and import-analysis ordering comparison

Date: `2026-07-31`  
Workstream: `B`  
Canonical finding: `findings/F25-vite-post-transform-import-analysis/finding.md`  
Upstream contact authorized: `no`

## In simple words

The original repair makes Vite read imports after every user transform. That fixes the demonstrated missing graph edge. It also changes what a user transform marked `order: 'post'` receives: today the user hook receives code after Vite has rewritten imports and injected HMR helpers; under the candidate it receives source before those changes.

This note turns that compatibility question into two exact target-native probes instead of leaving it as a hypothetical reason for a person to choose.

## Governing sources

### Current Vite plugin ordering

At upstream revision `843a47da6b93dbd3ce28c4ffae33a8ef338c6f05`:

- `packages/vite/src/node/plugins/index.ts` places user `postPlugins` before the internal server-only plugins and comments that the internal plugins apply after everything else.
- `getSortedPluginsByHook()` separately groups hook-level `pre`, normal, and `post` hooks while preserving plugin-list order inside each hook-order bucket.
- `vite:import-analysis` is currently a normal transform hook.

Therefore current behavior is:

1. all normal transform hooks, including import analysis;
2. user hooks carrying `transform.order = 'post'`.

The candidate changes import analysis into a post hook. Because the internal plugin is listed after user plugins, candidate behavior is:

1. user post transforms;
2. internal import analysis last inside the post bucket.

Sources:

- https://github.com/vitejs/vite/blob/843a47da6b93dbd3ce28c4ffae33a8ef338c6f05/packages/vite/src/node/plugins/index.ts
- https://github.com/vitejs/vite/blob/843a47da6b93dbd3ce28c4ffae33a8ef338c6f05/packages/vite/src/node/plugins/importAnalysis.ts

### Official plugin contract

Current Vite documentation says plugin-level `enforce` order and hook-level `order` are separate. Rolldown documentation defines sequential hooks as running in specified plugin order, with hook metadata changing hook order.

Sources:

- https://vite.dev/guide/api-plugin.html#plugin-ordering
- https://rolldown.rs/apis/plugin-api

### First-party post-transform use

The current first-party React RSC plugin uses a post transform to inspect the development module graph for invalid import chains:

- https://github.com/vitejs/vite-plugin-react/blob/9db4976a9f30e89205d327b9e951a0a1d4912fe5/packages/plugin-rsc/src/plugins/validate-import.ts

That implementation does not by itself prove dependence on import-analysis-mutated source. It establishes that post transforms are an active first-party mechanism and that compatibility review should test concrete observations rather than assume the hook is unused.

## Options under comparison

### Baseline — current normal import analysis

Carrier: `teamleaderleo/vite#6`  
Head: `a8cd287f45d74940af4d9ec63246643aa0c275e2`

The probe starts from owned `main` and requires a user post transform to observe:

- `__vite__createHotContext` already injected;
- the original `if (import.meta.hot)` form already replaced.

Queued receipts:

- CI `30586292234`
- Zizmor `30586292172`

### Candidate A — import analysis last in the post bucket

Carrier: `teamleaderleo/vite#7`  
Head: `9914696ab349c183bd4ef14ea43ff097ee9be56b`

The probe starts from the accepted candidate head and requires a user post transform to observe:

- the original `if (import.meta.hot)` source;
- no `__vite__createHotContext` yet.

Queued receipts:

- CI `30586307192`
- Zizmor `30586307115`

## Preliminary compatibility conclusion

Candidate A repairs one demonstrated contract: the module graph must describe the final code sent to the browser.

Candidate A also changes another observable stage contract: user post transforms no longer receive import-analysis output. The current repository documentation does not explicitly promise that internal import analysis runs before user post hooks, but current implementation and hook semantics make it observable.

This means the earlier `design-decision-ready` classification was premature. The remaining work is autonomous comparative evaluation:

1. execute both visibility probes;
2. inspect first-party and representative post transforms for reliance on analyzed source, graph timing, or injected helpers;
3. prototype a compatibility-preserving alternative if real reliance exists;
4. use explicit criteria to select a winner.

## Candidate alternatives to instantiate next

### Option A — move the existing analysis hook to `order: 'post'`

Benefit: one parse and one graph update; demonstrated final-source correctness.

Risk: changes post-hook input from analyzed code to pre-analysis code.

### Option B — retain current analysis and add bounded late-source reconciliation

Goal: preserve current post-hook input while detecting imports and HMR boundaries added afterward.

Questions requiring a prototype:

- can late reconciliation update graph and HMR metadata without duplicate URL rewriting or helper injection;
- can it distinguish additions from already processed imports;
- does it preserve pruning and failure behavior;
- what second-parse cost appears.

### Option C — move final graph ownership outside the user transform hook sequence

Goal: make final graph reconciliation an explicit internal finalization phase rather than another user-visible transform hook.

Questions requiring source design:

- whether the plugin container exposes a safe finalization boundary;
- how source maps and transform results reach that boundary;
- whether this is disproportionate to the demonstrated failure.

### Option D — retain current behavior and diagnose unsupported late imports

Benefit: preserves exact transform-stage compatibility.

Cost: accepts a dev graph that can disagree with served code or rejects currently expressible plugin behavior.

## Decision criteria

1. The development module graph describes the final served import and HMR boundary set.
2. Existing post transforms lose no supported observation without evidence and migration treatment.
3. Import rewriting, helper injection, graph update, pruning, and error behavior run exactly once where possible.
4. Source-map behavior remains coherent.
5. The implementation has a bounded, testable ownership model.
6. Runtime and parsing cost remains proportional.
7. Dev and build semantics diverge only where Vite intentionally documents the difference.

## Reopening and stop conditions

Select Option A if target execution passes and precedent plus source search finds no meaningful supported reliance on analyzed post-hook input, or if that reliance is explicitly outside contract and migration cost is accepted by repository evidence.

Prototype Option B or C if concrete first-party or representative behavior relies on the current stage contract.

Stop and retain current behavior only if every final-source repair introduces a larger demonstrated compatibility or ownership failure.
