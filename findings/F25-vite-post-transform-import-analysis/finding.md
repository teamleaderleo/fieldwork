# F25: Reconcile final Vite dev source with import analysis

Finding state: `comparative-evaluation-active`

Workstream: `B — Browser, web tooling, and runtime boundaries`  
Canonical Fieldwork issue: `#25`  
Current public source boundary: `vitejs/vite@843a47da6b93dbd3ce28c4ffae33a8ef338c6f05`  
First-party compatibility boundary: `vitejs/vite-plugin-react@9db4976a9f30e89205d327b9e951a0a1d4912fe5`  
Upstream contact authorized: `no`

## Current exact identities

- full analysis moved later: `teamleaderleo/vite#5@1a5b6b5327efa43fc4a33ed5ad51553b6d9c37ba`;
- simple retained overlay: `#9@38547370decd7328c50244596a580fe207fb3655`;
- preferred current-public-base reconciler: `#11@1f3d972cbdb7a0774b23876ef2b3ea845dab9c00`;
- staged restoration comparison: `#12@2eb0500310fee42327000e8e97c5ed658d6ba506`;
- publication and edge carrier: `#13@4945dd57c31864319b0fdee35a68ec82a9d713e1` against source `#11@ff92d9b4d933d23edfaefa908cb0e1d143bce546`;
- bounded late-watch repair: `#14@eb6ea755b1fea3f5260ec6cd926bf0dafdb530ab`.

Strongest evidence class: `target-executed` cross-platform comparison evidence; Candidate A also has `full-gate` evidence.  
Current disposition: `REPAIR + EXECUTE #11; retain #12 and #9 as executed losers; compare complete overlay with transform-scoped transaction`.  
Non-delegable human decision: `none`.

## In simple words

Vite performs development import rewriting and graph/HMR publication before user transforms with hook-level `order: 'post'`. A later transform can therefore change the source that reaches the browser after Vite has committed earlier graph facts.

Moving all import analysis later repairs final graph truth but changes current post-hook input and breaks first-party raw dynamic-import behavior. The selected family keeps ordinary rewriting in place and reconciles final graph/HMR state later.

Execution has narrowed the ownership problem. Restoring selected edge sets is insufficient. The surviving implementation must preserve complete committed metadata until one fresh transform request publishes one rollback-safe replacement.

## Governing invariant

**Final development graph and HMR metadata describe final transformed source and graph-only plugin facts while ordinary rewriting and current post-hook compatibility remain intact. Previous committed state remains coherent until one successful fresh request replaces it. Unchanged state emits no prune; real removal emits the exact prune set once.**

## Current technical conclusion

PR #11 remains the preferred source basis. It preserves normal rewriting, snapshots analyzed source, uses parsed import and `import.meta.env` identity, rejects late facts that still require browser-source rewriting, and performs final graph/HMR reconciliation.

The source family still requires four repairs:

1. preserve source-independent late `addWatchFile()` facts;
2. preserve the complete previous committed import/HMR view during later user post hooks;
3. fence graph publication by transform-request freshness;
4. retain prior committed state when final parse or resolution fails.

A fifth control is executing at current #11 head: distinguish count-preserving changes between nonliteral dynamic-import expressions after ordinary analysis rewrites them to `__vite__injectQuery(...)`.

## Executed comparisons

### Option A — full analysis moved later

PR #5 passed named gates and repairs the original mismatch. It changes user post-hook input and exposes first-party React RSC raw imports to incompatible rewriting. Retained as an executed compatibility-negative comparison.

### B1 — simple retained overlay

PR #9 produced two executed losses:

- unchanged repeat emitted a false prune;
- the next user post hook could not see the previously committed late accepted dependency.

A file-import-only overlay cannot represent coherent committed state.

### B3 — staged restoration

PR #12 at `2eb0500…` is now an executed loser.

CI `30593863720` reproduced the same result across Linux Node 20/22/24/26, macOS Node 24, and Windows Node 24.15. The inspected Linux Node 24 job `91041941210` ran 902 tests: 896 passed, 3 skipped, and exactly three discriminating controls failed:

1. previous late self-acceptance was absent during the next user post transform;
2. a late accepted export was absent from `acceptedHmrExports`;
3. a late named import was absent from `importedBindings`.

Previous accepted-dependency visibility still passed. Selected-field staging repairs one slice but does not reconstruct complete committed state. Review `4827592392` records `REJECT as winner / ACCEPT as executed comparison evidence`.

### B2 publication boundaries

PR #13 at `4945dd5…` target-executed three source failures across Linux, macOS, and Windows in CI `30594195534`:

1. source-preserving late `addWatchFile()` was absent from graph state;
2. a superseded older request overwrote the newer committed graph;
3. final parse failure removed the prior committed edge instead of retaining it without prune.

Parsed import identity, parsed `import.meta.env` identity, and analyzable dynamic-import timestamp-invalidation compatibility passed. Review `4827654817` accepts those results.

The inherited nonliteral dynamic-expression control was ineffective because it tried to replace pre-analysis text after ordinary analysis had already rewritten the expression. Current #11 head `1f3d972c…` mutates the actual analyzed expression and records that the hook changed it. Its exact product result remains held because the focused run stopped on accumulated branch formatting before tests.

## Self-review correction retained

An earlier revision incorrectly claimed analyzable dynamic imports should be absent from Vite's timestamp-invalidation set. Ordinary import analysis includes analyzable static and dynamic imports; plugin watch-file edges are the excluded class. The false criticism and source hunk were removed.

## Surviving ownership models

### Complete previous-state overlay

Persist and integrate the complete prior final state during ordinary analysis:

- imported modules and timestamp URLs;
- accepted dependencies;
- self/partial acceptance;
- accepted exports;
- imported bindings;
- graph-only watch facts;
- request generation and cleanup identity.

This can remain bounded only when the state is complete and publication still has one freshness gate.

### Transform-scoped graph transaction

Stage ordinary and final calculations during one transform request. Keep prior committed state visible, reject stale requests before publication, then commit graph/HMR state and emit prunes once.

This is the preferred fallback when a complete overlay becomes distributed across hooks or fields.

## Claim table

| Claim | Evidence class | Exact support | Limit |
| --- | --- | --- | --- |
| post transforms can change imports/HMR after ordinary analysis | `target-executed` | original reproduction and #5 | focused client-dev path |
| moving full analysis later repairs the mismatch | `full-gate` | #5, CI `30487475188` | compatibility loss remains |
| simple overlay emits false prune and hides prior accepted state | `target-executed` | #9 runs `30587631101`, `30588826788` | incomplete overlay only |
| staged restoration recovers accepted deps but omits complete metadata | `target-executed` | #12 CI `30593863720`, job `91041941210` | test placement remains comparison-only |
| late watch facts are lost | `target-executed` | #13 CI `30594195534` | exact executed source `ff92d9b…` |
| superseded requests can publish stale graph state | `target-executed` | #13 CI `30594195534` | exact executed source `ff92d9b…` |
| final parse failure does not preserve prior graph | `target-executed` | #13 CI `30594195534` | exact executed source `ff92d9b…` |
| parsed import/env identity and analyzable dynamic compatibility pass | `target-executed` | #13 CI `30594195534` | corrected expression-change control pending |
| count-preserving nonliteral expression change is distinguished | `target-test-prepared` | #11 `1f3d972c…` | formatting blocked focused execution |

## Required next controls

1. finish #14 exact execution and transfer the watch repair only if it passes;
2. format and execute current #11 expression-change control;
3. instantiate complete overlay and transaction sketches against the #9/#12/#13 controls;
4. preserve no-prune repeat and one-prune removal behavior;
5. cover parse/resolve failure and stale request before publication;
6. cover partial accept, normalization, aliases, virtual IDs, optimized dependencies, workers, and query imports;
7. measure final parse and source-map cost after correctness ownership settles.

CSS late watch files remain a sibling finding. Shared graph-publication machinery may emerge, while CSS analysis and JavaScript source rewriting retain separate conclusions.

## Current disposition

- Finding state: `comparative-evaluation-active`;
- preferred source: PR #11;
- active bounded repair: PR #14;
- executed losing alternatives: PR #9 and PR #12;
- surviving ownership comparison: complete overlay versus transform-scoped transaction;
- clearing condition: complete metadata, graph-only facts, freshness fencing, rollback, and one publication pass the retained controls;
- exact next transition: execute #14 and corrected #11, then instantiate the two surviving ownership models;
- non-delegable human decision: `none`.

## Changes to the canonical conclusion

| Date | Record | Change |
| --- | --- | --- |
| 2026-07-29 | #2/#5 | mismatch reproduced; Option A passed named gates |
| 2026-07-31 | React RSC source and #6/#7 | Option A lost preferred status |
| 2026-07-31 | #9 | simple overlay shown non-atomic and incomplete |
| 2026-07-31 | self-review | false dynamic-import exclusion claim removed |
| 2026-07-31 | #12 | staged restoration rejected as complete ownership after three metadata failures |
| 2026-07-31 | #13 | late-watch, stale-request, and rollback defects target-executed |
| 2026-07-31 | #11 `1f3d972c…` | ineffective expression-change control repaired; execution pending |

No public upstream interaction occurred.
