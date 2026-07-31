# Alternative record: Option B late reconciliation ownership

Finding: [`../finding.md`](../finding.md)  
State: `comparative-evaluation-active`  
Human design decision pending: `no`

## Question

How should Vite preserve ordinary import rewriting and current user post-hook behavior while publishing final graph and HMR facts exactly once?

## Shared requirements

Every surviving model must:

- preserve ordinary analyzed source as user post-transform input;
- preserve first-party raw dynamic-import behavior;
- publish final imports and HMR facts;
- include source-independent late `addWatchFile()` facts;
- preserve complete previous imports, accepted dependencies, self/partial acceptance, accepted exports, imported bindings, and timestamp state during the next post hook;
- distinguish parsed identities rather than raw string collisions;
- preserve prior committed state on parse, resolution, cancellation, or stale-request failure;
- emit no prune for unchanged state and one exact prune set for removal;
- reject stale requests before graph publication;
- keep execution machinery outside promoted source.

## A — full analysis moved later

Carrier: Vite #5 at `1a5b6b5327efa43fc4a33ed5ad51553b6d9c37ba`.

### Result

The implementation repairs the original mismatch and passed named gates. It changes user post-hook input and exposes first-party React RSC raw imports to incompatible rewriting.

Disposition: `REJECT as preferred direction / RETAIN as full-gate compatibility-negative evidence`.

## B1 — simple retained overlay

Carrier: Vite #9 at `38547370decd7328c50244596a580fe207fb3655`.

### Executed losses

- unchanged repeat emitted a false prune;
- the next user post hook lost the previously committed late accepted dependency.

A file-import-only overlay cannot preserve coherent committed state.

Disposition: `REJECT as winner / RETAIN as executed negative evidence`.

## B2 — current-public-base reconciler

Source: Vite #11 at `1f3d972cbdb7a0774b23876ef2b3ea845dab9c00`.

### Retained strengths

- normal rewriting remains in place;
- ordinary analyzed source remains visible to user post hooks;
- import and `import.meta.env` identities are parsed;
- late facts requiring browser-source rewriting fail closed;
- final relative imports and HMR state can be reconciled.

### Target-executed losses on predecessor source

PR #13 at `4945dd57c31864319b0fdee35a68ec82a9d713e1`, against #11 `ff92d9b…`, proved across Linux, macOS, and Windows:

1. source-preserving late `addWatchFile()` is omitted;
2. a superseded old request can overwrite newer graph state;
3. final parse failure removes prior committed state instead of rolling back.

Parsed import identity, parsed env identity, and analyzable dynamic-import compatibility passed.

### Current expression control

The prior nonliteral dynamic-expression control changed no code because ordinary analysis had already rewritten the expression. Current head `1f3d972c…` mutates the actual `__vite__injectQuery(target, 'import')` expression and records the mutation. Exact product execution remains pending after a formatting-first focused failure.

Disposition: `PREFERRED SOURCE BASIS / REPAIR + EXECUTE`.

## B3 — distributed staged restoration

Source: Vite #12 at `2eb0500310fee42327000e8e97c5ed658d6ba506`.

### Executed result

CI `30593863720` reproduced the same result across Linux Node 20/22/24/26, macOS Node 24, and Windows Node 24.15.

The mechanism restored previous accepted-dependency visibility. It failed to restore:

- previous self-acceptance;
- accepted exports;
- imported bindings.

The inspected Linux Node 24 job ran 902 tests: 896 passed, 3 skipped, and only those three discriminating controls failed.

### Consequence

Selected-field staging creates continuing omission risk and distributes ownership across three ordered hooks. Expanding the state one property at a time is rejected.

Disposition: `REJECT as winner / ACCEPT as target-executed partial-mechanism evidence`; review `4827592392`.

## B4 — complete previous-state overlay

### Mechanism

Persist one complete previous final state per module/environment. Ordinary analysis consumes that whole state so later post hooks see a coherent committed graph. Final reconciliation replaces it only after success and request-freshness validation.

### Required state

- imported module identities and timestamp URLs;
- accepted dependencies;
- self and partial acceptance;
- accepted exports;
- imported bindings;
- graph-only watch facts;
- request generation and cleanup identity.

### Wins

- bounded extension of current import analysis;
- prior committed state remains visible during later hooks;
- smaller change than a general transaction when the state boundary remains complete.

### Risks

- any omitted field recreates B1/B3 losses;
- ordinary analysis becomes aware of final-reconciliation state;
- publication, cleanup, and stale-request fencing still need one owner.

Disposition: `ACTIVE IMPLEMENTATION CANDIDATE`.

## B5 — transform-scoped graph transaction

### Mechanism

Stage ordinary and final graph/HMR calculations during one transform request. Keep previous committed state visible until final reconciliation succeeds. Reject stale requests, then commit graph state and emit prune once.

### Wins

- clearest one-transition model;
- rollback is natural before commit;
- stale requests can be discarded before publication;
- avoids maintaining a manually complete overlay across hooks.

### Risks

- broader module-graph and plugin-container change;
- consumers may currently observe graph mutation during the transform chain;
- requires composed controls across JavaScript analysis and sibling watch-file producers.

Disposition: `ACTIVE IMPLEMENTATION CANDIDATE`; preferred when B4 becomes distributed or incomplete.

## Executed criticism set

The surviving candidates must pass all of these:

1. #9 unchanged-repeat false prune;
2. #9 previous accepted-dependency visibility;
3. #12 previous self-acceptance;
4. #12 accepted exports;
5. #12 imported bindings;
6. #13 late graph-only watch fact;
7. #13 stale-request publication;
8. #13 rollback after final parse failure;
9. parsed import and env identity;
10. analyzable dynamic-import compatibility;
11. current #11 count-preserving nonliteral expression change.

## Current ranking

1. B4 complete overlay, only while completeness and one publication owner remain demonstrable;
2. B5 transaction when overlay ownership becomes distributed;
3. B3 retained as partial positive/negative comparison;
4. B1 retained as simple-overlay failure evidence;
5. A retained as compatibility-negative evidence.

## Next transition

1. finish #14 late-watch execution;
2. format and execute current #11 expression control;
3. instantiate minimal B4 and B5 sketches;
4. run the complete criticism set against both;
5. retain the provisional winner, losing reasons, and reopening triggers;
6. publish clean source and complete independent exact-head review.

No merge or public upstream interaction is authorized.
