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
- preserve ordinary timestamp-invalidation semantics for analyzable static and dynamic imports while excluding plugin watch-file edges;
- emit no prune for unchanged final state;
- emit exactly the real prune set once for removal or replacement;
- preserve the previous committed accepted dependency, self-accept, accepted-export, and imported-binding view while the next user post hook runs;
- preserve prior committed graph state on parse, resolution, cancellation, or stale-request failure;
- preserve partial accept, normalization, diagnostics, and source-map behavior;
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

Carrier: Vite #9 at `38547370decd7328c50244596a580fe207fb3655`.

### Wins

- ordinary source rewriting stays in place;
- final pass can parse late imports and HMR state;
- focused repaired head demonstrated add, retain, and remove behavior.

### Executed losses

1. At old head `7132850…`, CI `30587631101`, macOS job `91022769607`, unchanged second-transform state emitted a false prune.
2. At current head `3854737…`, CI `30588826788` failed the same accepted-state visibility assertion across Node 20, 22, 24, 26, Windows 24.15, and macOS 24.
3. Inspected Ubuntu Node 24 job `91026466344` had 895 passing tests, 3 skipped, and one failure: the second user post hook did not see the previously committed late accepted dependency.
4. Formatting failed independently in job `91026379219`; two line-wrap changes do not alter the product disposition.
5. Zizmor `30588826793` passed.

### Consequence

Preserving previous late file imports alone does not preserve a coherent previous final graph view. A complete overlay must carry all HMR/binding metadata or graph mutation must be staged.

Disposition: `HOLD / RETAIN AS EXECUTED NEGATIVE COMPARISON`.

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

Vite #14 at `eb6ea755b1fea3f5260ec6cd926bf0dafdb530ab`:

- snapshots ordinary `_addedImports`;
- reconciles later graph-only watch facts on equal source;
- keeps analyzable dynamic imports aligned with ordinary timestamp-invalidation semantics;
- runs original focused tests plus one negative and three compatibility controls;
- publisher `30593631027` is queued.

### Remaining loss

Ordinary analysis still commits before final reconciliation. The complete previous HMR/binding view, one-transition prune publication, rollback, and stale-request fencing remain unresolved.

Disposition: preferred source basis, `REPAIR + EXECUTE`.

## B3 — distributed staged restoration

Source: Vite #12 at `2eb0500310fee42327000e8e97c5ed658d6ba506`.

### Mechanism

1. carry prior late import IDs through ordinary analysis;
2. restore prior committed imported and accepted dependency graph view before user post transforms;
3. reconcile final source after user post transforms.

### Executed win at prior head

CI `30589150453` passed every unit job on Linux, macOS, and Windows. The focused contract proved:

- previous accepted dependency visible during the next user post hook;
- no false prune on unchanged final state;
- one real prune on removal;
- raw dynamic-import compatibility and HMR update behavior.

The overall run was red only because `oxfmt` wanted one line collapse and the Windows serve worker exited after 1,046 passing tests and 165 skipped without a product assertion failure. Zizmor `30589150450` passed.

### Current discriminators

Current head `2eb0500…` fixes formatting and adds controls for:

- prior self-acceptance visible during the next user post hook;
- final accepted exports introduced late;
- imported bindings for a late named import.

Complete-diff review predicts these controls fail because `LateImportState` stores only imported IDs/URLs, accepted dependency URLs, and timestamp-invalidation URLs.

### Risks

- correctness depends on three jointly ordered hooks;
- restoration performs an additional graph update;
- state ownership is distributed;
- stale request, rollback, and cleanup reasoning is harder;
- test-only placement does not prove a safe internal insertion point.

Disposition: `EXECUTE / PARTIAL MECHANISM EVIDENCE`, not default winner.

## B4 — complete ordinary-analysis overlay

### Mechanism

Persist the previous committed final state per module/environment. Ordinary analysis includes that complete state in its graph update. Final reconciliation atomically replaces it.

### Required contents

- imported module identities and timestamp URLs;
- accepted dependency identities;
- accepted exports;
- self-accept/partial-accept flags;
- imported bindings;
- graph-only watch facts;
- generation and cleanup metadata.

### Wins

- prevents ordinary analysis from temporarily dropping previous final state;
- keeps previous committed graph/HMR facts visible to user post hooks;
- smaller than a general transaction if the state boundary remains coherent.

### Risks

- the B1 execution proves a file-only overlay is insufficient;
- partial overlay creates mixed old/new state;
- generation fencing and cleanup are mandatory;
- ordinary analysis becomes aware of final-reconciliation state.

Disposition: preferred next implementation direction only as a complete state overlay, after #14 passes.

## B5 — transform-scoped graph transaction

### Mechanism

Stage ordinary and final graph/HMR calculations during one transform request. Commit module graph state and dispatch prunes once after final reconciliation succeeds.

### Wins

- clearest one-transition model;
- prior committed graph remains visible until commit;
- rollback is natural before commit;
- stale request can be rejected before publication;
- ordinary and final responsibilities remain distinguishable inside one transaction.

### Risks

- broader plugin-container and module-graph change;
- current consumers may depend on graph mutation during the transform chain;
- requires composed controls across import analysis, HMR, CSS/watch facts, and transform request caching.

Disposition: preferred architectural fallback when complete overlay becomes distributed or incomplete.

## Edge controls

PR #13 at `3e588a2292a3c7fc2c32c5726c4bcdfcefe2ba9a` contains:

1. negative: source-preserving late watch file;
2. compatibility: import-like string versus a real late bare import;
3. compatibility: env-like string versus real late `import.meta.env`;
4. compatibility: analyzable late dynamic import remains in ordinary timestamp-invalidation state.

An earlier #13/#14 revision incorrectly asserted that analyzable dynamic imports should be excluded from `staticImportedUrls`. Ordinary `importAnalysis.ts` includes analyzable static and dynamic imports and excludes plugin watch-file edges. The false assertion and source hunk were removed.

PR #9 retains executed lifecycle criticism:

- false prune on unchanged repeat;
- previous accepted dependency missing during the next user post hook.

PR #12 now distinguishes accepted dependency restoration from complete HMR/binding state restoration.

## Selection rule

Use the smallest model that satisfies the complete graph-publication invariant without changing supported source-rewrite behavior.

Current ranking:

1. B2 source basis plus a complete B4 state overlay;
2. B5 transaction if complete overlay becomes distributed or incomplete;
3. B3 staged restoration as executable partial-state comparison;
4. B1 retained solely for mechanism and executed failure evidence;
5. A retained as compatibility-negative proof.

Reopen Option A only if the first-party post-analysis raw-import contract is removed or an explicit migration accepts the break.

## Next transition

1. inspect #14 publisher `30593631027`;
2. inspect #12 current CI `30593863720` and classify each metadata control;
3. transfer passing watch repair to clean source;
4. use #9/#12 controls as mandatory tests for complete overlay or transaction models;
5. execute rollback and stale-request controls;
6. complete independent exact-head review and retire temporary carriers.
