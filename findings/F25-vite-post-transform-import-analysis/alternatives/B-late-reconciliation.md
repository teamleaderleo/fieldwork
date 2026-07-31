# Alternative record: Option B late reconciliation ownership

Finding: [`../finding.md`](../finding.md)  
State: `comparative-evaluation-active`  
Human design decision pending: `no`

## Question

How should Vite preserve ordinary import rewriting and current user post-hook behavior while publishing final graph and HMR facts exactly once?

This record keeps technically distinguishable ownership models concrete. It does not grant merge or public-upstream authority.

## Shared requirements

Every surviving model must:

- preserve ordinary analyzed source as the current input to user post transforms;
- preserve first-party raw dynamic-import behavior;
- include final relative/browser-valid imports and HMR boundaries in graph state;
- include graph-only late `addWatchFile()` facts even when source text is unchanged;
- keep dynamic imports outside `staticImportedUrls`;
- emit no prune for unchanged final state;
- emit exactly the real prune set once for removal or replacement;
- preserve prior committed graph state on parse, resolution, cancellation, or stale-request failure;
- define the graph view visible to user post hooks on a later transform;
- preserve partial accept, bindings, self accept, exports, normalization, and diagnostics;
- keep temporary execution machinery outside any promoted source diff.

## A — full analysis moved to the post bucket

Carrier: Vite #5 at `1a5b6b5327efa43fc4a33ed5ad51553b6d9c37ba`.

### Wins

- one complete pass owns rewriting and graph publication;
- smallest implementation;
- reproduced graph/HMR case passes;
- named CI and workflow analysis passed.

### Loses

- changes user post-hook input;
- exposes first-party React RSC raw import to rewriting;
- can add `?import` contrary to the integration's stated purpose.

Disposition: retained executed negative comparison.

## B1 — simple retained overlay around a final reconciler

Carrier: Vite #9, current head `38547370decd7328c50244596a580fe207fb3655`.

### Wins

- ordinary source rewriting stays in place;
- final pass can parse late imports and HMR state;
- focused repaired head demonstrated add, retain, and remove behavior.

### Loses and criticism

- the first implementation emitted a false prune on unchanged repeat state;
- previous accepted-HMR state may disappear before a later user post hook reads the graph;
- current head ordinary CI failed formatting and unit jobs and needs exact failure classification;
- retained state needs lifecycle, rollback, and stale-request fences.

Disposition: mechanism and negative evidence retained; current branch is not the preferred source.

## B2 — current-public-base snapshot plus final reconciler

Source: Vite #11 at `ff92d9b4d933d23edfaefa908cb0e1d143bce546`.

### Wins

- current public revision;
- ordinary snapshot before user post hooks;
- parsed import and environment identity;
- explicit late rewrite rejection;
- browser/graph URL compatibility checks;
- broad final import/HMR source implementation.

### Current bounded repair

Vite #14 at `4de42376d3bd34e2b559e68e721f698a62b62a96`:

- snapshots ordinary `_addedImports`;
- reconciles late graph-only watch facts on equal source;
- records only non-dynamic imports as static;
- runs original focused tests plus four adversarial controls;
- publisher `30592816438` is queued.

### Remaining loss

Ordinary analysis still commits and may dispatch prune before the final pass. Post-only code cannot retract an already sent prune.

Disposition: preferred source basis, `REPAIR + EXECUTE`.

## B3 — distributed staged restoration

Source: Vite #12 at `63a26854bfcd44de66286ffdd3cf04ff0066fe9f`.

### Mechanism

1. carry prior late imports through ordinary analysis;
2. restore prior committed graph view before user post transforms;
3. reconcile final source after user post transforms.

### Wins

- makes prior graph visibility an explicit stage;
- is executable rather than paper-only;
- Zizmor passed; ordinary CI is in progress.

### Risks

- correctness depends on three jointly ordered hooks;
- state ownership is distributed;
- stale request, rollback, and cleanup reasoning is harder;
- accepted state, bindings, and static/dynamic facts must move together.

Disposition: active comparison, not default winner.

## B4 — direct ordinary-analysis overlay

### Mechanism

Persist the previous committed final-source overlay per module/environment. Ordinary analysis unions that prior overlay into its graph update. The final reconciler atomically replaces the overlay from final source.

### Wins

- prevents ordinary analysis from temporarily pruning prior late edges;
- preserves prior graph view for user post hooks;
- smaller change than a general graph transaction.

### Risks

- overlay must include imports, accepted deps, static URLs, bindings, exports, self-accept state, and relevant graph-only facts;
- partial overlay creates mixed old/new state;
- generation fencing and cleanup are mandatory;
- ordinary analysis becomes aware of final-reconciliation state.

Disposition: preferred next implementation direction if #14 passes.

## B5 — transform-scoped graph transaction

### Mechanism

Stage ordinary and final graph/HMR calculations during one transform request. Commit module graph state and dispatch prunes once after final reconciliation succeeds.

### Wins

- clearest one-transition model;
- rollback is natural before commit;
- stale request can be rejected before publication;
- ordinary and final responsibilities remain distinguishable inside one transaction.

### Risks

- broader plugin-container and module-graph change;
- current consumers may depend on graph mutation during the transform chain;
- requires composed controls across import analysis, HMR, CSS/watch facts, and transform request caching.

Disposition: preferred architectural fallback when direct overlay becomes distributed or incomplete.

## Adversarial controls

PR #13 at `b139c1be0965158970bd4353ac05eee5d51793bb` retains four criticisms:

1. source-preserving late watch file;
2. import-like string versus a real late bare import;
3. env-like string versus real late `import.meta.env`;
4. late dynamic edge absent from static invalidation state.

PR #9 retains lifecycle criticism:

- no false prune on unchanged repeat;
- one real prune on removal/replacement;
- prior accepted-state visibility.

Future controls must add rollback, stale-request publication, bindings/partial accepts, workers, aliases, virtual IDs, and cleanup.

## Selection rule

Use the smallest model that satisfies the complete graph-publication invariant without changing supported source-rewrite behavior.

Current ranking:

1. B2 source basis plus B4 direct overlay;
2. B5 transaction if overlay state becomes incomplete or distributed;
3. B3 staged restoration as executable comparison;
4. B1 retained for mechanism and failure evidence;
5. A retained as compatibility-negative proof.

Reopen Option A only if the first-party post-analysis raw-import contract is removed or an explicit migration accepts the break.

## Next transition

1. inspect #14 publisher `30592816438`;
2. transfer passing current-fact repairs to clean source;
3. instantiate no-false-prune ownership on that source family;
4. execute unchanged, removal, accepted-state visibility, rollback, and stale-request controls;
5. complete independent exact-head review and retire temporary carriers.
