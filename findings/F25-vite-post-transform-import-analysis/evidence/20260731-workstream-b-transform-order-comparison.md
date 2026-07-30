# Vite post-transform and import-analysis ordering comparison

Date: `2026-07-31`  
Workstream: `B`  
Canonical finding: `findings/F25-vite-post-transform-import-analysis/finding.md`  
Upstream contact authorized: `no`

## In simple words

The original repair makes Vite read imports after every user transform. That fixes the demonstrated missing graph edge. It also moves import analysis after user post transforms.

A current first-party Vite React RSC plugin deliberately uses a post transform to insert a dynamic import *after* import analysis so Vite will not append `?import`. Candidate A reverses that ordering and would let Vite rewrite the injected import. This is a concrete compatibility dependency, not a hypothetical preference.

Paired owned-fork probes now compare the baseline and candidate stage contracts, including a minimal version of the RSC raw-import pattern.

## Governing sources

### Current Vite plugin ordering

At upstream revision `843a47da6b93dbd3ce28c4ffae33a8ef338c6f05`:

- `packages/vite/src/node/plugins/index.ts` places user `postPlugins` before the internal server-only plugins and comments that internal plugins apply after everything else.
- `getSortedPluginsByHook()` separately groups hook-level `pre`, normal, and `post` hooks while preserving plugin-list order inside each bucket.
- `vite:import-analysis` is currently a normal transform hook.

Current behavior is therefore:

1. normal transform hooks, including import analysis;
2. user hooks carrying `transform.order = 'post'`.

Candidate A changes import analysis into a post hook. Because the internal plugin is listed after user plugins, candidate behavior is:

1. user post transforms;
2. internal import analysis last inside the post bucket.

Sources:

- https://github.com/vitejs/vite/blob/843a47da6b93dbd3ce28c4ffae33a8ef338c6f05/packages/vite/src/node/plugins/index.ts
- https://github.com/vitejs/vite/blob/843a47da6b93dbd3ce28c4ffae33a8ef338c6f05/packages/vite/src/node/plugins/importAnalysis.ts

### Official hook contract

Current Vite documentation says plugin-level `enforce` order and hook-level `order` are separate. Rolldown documentation defines sequential hooks as passing prior results to later hooks in the specified order.

Sources:

- https://vite.dev/guide/api-plugin.html#plugin-ordering
- https://rolldown.rs/apis/plugin-api

### First-party compatibility dependency: React RSC raw imports

At `vitejs/vite-plugin-react@9db4976a9f30e89205d327b9e951a0a1d4912fe5`, `packages/plugin-rsc/src/plugin.ts` defines `rsc:vite-client-raw-import`:

```ts
transform: {
  order: 'post',
  filter: { code: '__vite_rsc_raw_import__' },
  handler(code) {
    if (code.includes('__vite_rsc_raw_import__')) {
      // inject dynamic import last to avoid Vite adding `?import` query
      // to client references (and browser mode server references)
      return code.replace('__vite_rsc_raw_import__', 'import')
    }
  },
}
```

`packages/plugin-rsc/src/browser.ts` emits the placeholder call during development. The post transform changes it into a real dynamic import only after current import analysis has already run.

Sources:

- https://github.com/vitejs/vite-plugin-react/blob/9db4976a9f30e89205d327b9e951a0a1d4912fe5/packages/plugin-rsc/src/plugin.ts
- https://github.com/vitejs/vite-plugin-react/blob/9db4976a9f30e89205d327b9e951a0a1d4912fe5/packages/plugin-rsc/src/browser.ts

Candidate A moves import analysis after that replacement. The import then becomes visible to Vite's non-JavaScript import rewriting, defeating the first-party plugin's explicit intent.

A separate first-party post transform, `validateImportPlugin()`, also uses dev module-graph state. It remains a secondary timing control:

- https://github.com/vitejs/vite-plugin-react/blob/9db4976a9f30e89205d327b9e951a0a1d4912fe5/packages/plugin-rsc/src/plugins/validate-import.ts

## Executable comparison

### Baseline carrier

PR: `teamleaderleo/vite#6`  
Current head: `7229602a44df963d0395bc9c0160ea062a014d5c`

Controls:

1. a user post transform receives code after hot-context injection;
2. a post transform replaces `__raw_import__` with `import` after analysis;
3. the final dynamic import remains `import('./dep.txt')` without `?import`.

Current receipts:

- CI `30586609039` — queued
- Zizmor `30586609010` — pending

### Candidate A carrier

PR: `teamleaderleo/vite#7`  
Current head: `e169bafdcfc0c25b3f77cadb41aebf762458586b`

Controls:

1. a user post transform receives source before hot-context injection;
2. the same post transform replaces `__raw_import__` with `import` before candidate import analysis;
3. candidate import analysis rewrites the dynamic import with `?import`.

Current receipts:

- CI `30586630958` — pending
- Zizmor `30586630986` — queued

## Comparative conclusion

Candidate A remains the smallest repair for final graph truth, but it no longer qualifies as the default winner. It conflicts with an explicit current first-party use of post-transform ordering.

This changes the option ranking:

1. **Option B — compatibility-preserving late reconciliation** becomes the next implementation candidate.
2. **Option C — explicit internal finalization outside user hooks** remains the fallback if bounded reconciliation cannot own graph state safely.
3. **Option A — move full import analysis to the post bucket** is retained as a useful negative comparison and may survive only with a deliberate compatibility break plus migration strategy.
4. **Baseline** remains incorrect for post transforms that add real imports or HMR boundaries.

No user decision is required. The codebase and first-party integration now provide enough evidence to continue autonomously.

## Option B requirements

A viable late-reconciliation prototype must:

- preserve the current normal import-analysis pass so user post hooks continue to receive analyzed code;
- inspect final post-transform source for imports and HMR boundaries added afterward;
- update module-graph and HMR metadata for late additions;
- avoid rewriting intentional raw imports introduced after normal analysis;
- avoid duplicate hot-context and env injection;
- preserve pruning when late imports disappear;
- preserve parse and resolution errors without replacing the primary transform failure;
- define whether late imports receive URL rewriting, graph-only tracking, or an explicit supported subset;
- record the extra parse and runtime cost.

The RSC pattern demonstrates that “analyze final source” and “rewrite every final import” are separate responsibilities. The next prototype should separate them rather than moving the entire existing handler unchanged.

## Decision criteria

1. The development module graph describes final served imports and HMR boundaries.
2. Current first-party raw-import behavior remains intact.
3. User post transforms retain their current observable input unless a separately justified migration changes it.
4. URL rewriting, helper injection, graph update, pruning, and errors each have one clear owner.
5. Source maps and diagnostics remain coherent.
6. Runtime and parse cost remains proportional.
7. The implementation is narrow enough to test and maintain.

## Next actions

1. Finish exact execution of PRs #6 and #7.
2. Prototype Option B on a separate owned branch.
3. Add controls for late static imports, late HMR accept boundaries, raw dynamic imports, removal/pruning, and parse errors.
4. Cross-review Option B against the current import-analysis state model.
5. Select Option B or fall back to an explicit finalization design.

## Stop condition

Stop the lane only after one implementation preserves both final graph truth and the supported first-party post-transform contract, or after retained execution proves those requirements cannot coexist without a broader contract change.