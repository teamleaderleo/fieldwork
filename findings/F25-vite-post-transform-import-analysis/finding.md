# F25: Reconcile final Vite dev source with import analysis

Finding state: `comparative-evaluation-active`

Workstream: `B — Browser, web tooling, and runtime boundaries`  
Canonical Fieldwork issue: `#25`  
Canonical finding path: `findings/F25-vite-post-transform-import-analysis/finding.md`  
Current public source boundary: `vitejs/vite@843a47da6b93dbd3ce28c4ffae33a8ef338c6f05`  
First-party compatibility boundary: `vitejs/vite-plugin-react@9db4976a9f30e89205d327b9e951a0a1d4912fe5`  
Upstream contact authorized: `no`

## Current exact identities

### Source alternatives

- Option A, full analysis moved later: `teamleaderleo/vite#5@1a5b6b5327efa43fc4a33ed5ad51553b6d9c37ba`
- Option B1, simple retained-state prototype: `#9@38547370decd7328c50244596a580fe207fb3655`
- Option B2, current-public-base reconciler: `#11@ff92d9b4d933d23edfaefa908cb0e1d143bce546`
- Option B3, staged restoration comparison: `#12@2eb0500310fee42327000e8e97c5ed658d6ba506`
- Option B2 bounded watch-fact repair: `#14@eb6ea755b1fea3f5260ec6cd926bf0dafdb530ab`

### Execution and criticism surfaces

- baseline stage probe: `#6@7229602a44df963d0395bc9c0160ea062a014d5c`
- Option A stage/raw-import probe: `#7@e169bafdcfc0c25b3f77cadb41aebf762458586b`
- desired combined contract: `#8@5d9a0ca545cd7763a7d8bfffd3a646ecb6c4a076`
- CSS sibling watch-file probe: `#10@81719c925a53040135e6bb8bfcbabd24365bcd51`
- current-public-base edge controls: `#13@3e588a2292a3c7fc2c32c5726c4bcdfcefe2ba9a`

Strongest evidence class: Candidate A `full-gate`; B1 lifecycle and accepted-state losses `target-executed`; B3 accepted-dependency restoration `target-executed`; current B2 watch-fact repair queued.  
Current review disposition: `REPAIR + EXECUTE Option B2; compare complete state overlay against a transform-scoped graph transaction; HOLD Option A promotion`.  
Non-delegable human decision: `none`.  
Desk routing: `not-entered`.

## In simple words

Vite rewrites development imports, records module dependencies, and stores hot-update boundaries. A plugin can run after ordinary import analysis and add behavior that reaches the browser after Vite has already committed its graph state.

Moving the whole analysis pass later fixes final graph truth, but it changes what user post transforms observe. Current first-party React RSC code deliberately inserts a raw dynamic import after normal rewriting so Vite does not add `?import`.

The selected repair family keeps ordinary rewriting where it is and performs bounded final reconciliation for graph and HMR facts. The unresolved ownership question is how one transform request publishes one coherent final state while the previous committed state remains visible until replacement succeeds.

## Why we care

Without a repair, served code and the development graph can disagree. That can produce stale edges, full reloads, missing accepted HMR dependencies, and dev/build divergence.

A careless repair can:

- rewrite a deliberately raw first-party import;
- emit a false client prune on every unchanged repeat transform;
- miss a late `addWatchFile()` because source text did not change;
- hide previous accepted dependency, self-accept, accepted-export, or binding state while a later plugin reads the graph;
- publish partial state after parse, resolution, cancellation, or stale-request failure.

## Governing invariant

**Final development graph and HMR metadata must describe the final transform result and graph-only plugin facts while ordinary source rewriting and current post-hook compatibility remain intact. The previous committed final state remains coherent until one successful replacement commit; unchanged final state emits no prune, and a real removal emits the exact prune set once.**

## Governing contracts

| Contract | Primary evidence | Consequence |
| --- | --- | --- |
| final graph and HMR truth | original reproduction and Candidate A regression | late imports and accepts must enter final state |
| current post-hook source | hook ordering, #6/#7, current first-party source | ordinary rewrite output remains visible to user post hooks |
| raw-import escape | React RSC `rsc:vite-client-raw-import` | final graph work must not rerun incompatible URL rewriting |
| atomic transition | #9 false-prune execution | ordinary and final analysis cannot dispatch contradictory transitions |
| graph-only facts | transform-context `_addedImports` | source equality cannot imply graph equality |
| timestamp invalidation set | ordinary `importAnalysis.ts` | analyzable static and dynamic imports are included; plugin watch-file edges are excluded |
| complete previous HMR view | #9 loss and #12 controls | accepted deps, self accept, exports, bindings, and related metadata move together |
| parsed identity | current #11 snapshot parser and collision controls | matching text is not proof that an import or env access was analyzed |
| exact-head review | Fieldwork protocol | every source or reviewed-input movement expires disposition |

## Current technical conclusion

Option B — ordinary analysis plus bounded final reconciliation — remains the selected family.

PR #11 is the strongest current source basis. At `ff92d9b…` it now:

- snapshots ordinary analyzed source before user post transforms;
- compares parsed import identities with multiplicity;
- compares parsed `import.meta.env` presence;
- preserves current post-hook input;
- rejects late bare/static-asset imports that still require source rewriting;
- rejects changed nonliteral dynamic expressions and browser/graph URL disagreement;
- parses final HMR state and injects hot context when required.

The earlier snapshot-order and raw-substring objections are repaired on the current head. Three disposition-bearing boundaries remain:

1. equal-source early return skips a source-preserving late `addWatchFile()`;
2. the previous committed full HMR/binding state is not yet proven coherent during a later user post hook;
3. ordinary and final analysis do not yet publish through one rollback-safe, stale-request-fenced commit.

PR #14 instantiates the bounded repair for the first boundary. It snapshots the ordinary-analysis watch set and reconciles later graph-only additions even when source text is unchanged. Publisher `30593631027` is queued at exact carrier head `eb6ea75…`.

The second and third boundaries require ownership before or around ordinary graph mutation. The leading models are:

- integrate a complete previous-final overlay into ordinary analysis; or
- stage ordinary and final graph changes in a transform-scoped transaction and commit once.

PR #12 is the executable distributed restoration comparison. At prior head `63a2685…`, all platform unit jobs passed the accepted-dependency visibility, unchanged no-prune, and real-removal contract. Current head `2eb0500…` adds self-acceptance, accepted-export, and imported-binding controls because complete-diff review shows its stored state currently contains only imported IDs/URLs, accepted dependency URLs, and timestamp-invalidation URLs.

## Self-review correction

An earlier review and finding revision claimed that analyzable dynamic imports should be absent from `staticImportedUrls`. That was wrong.

Ordinary Vite import analysis intentionally places analyzable static and dynamic imports in that timestamp-invalidation set; plugin watch-file edges are the excluded class. The incorrect #13 assertion and #14 source hunk were removed. PR #11 correction review `4824349528` records the narrowed disposition.

This correction does not change the selected repair family. It removes one false defect and narrows #14 to the real graph-only watch-fact boundary.

## Claim table

| Claim | Evidence class | Exact support | Limit |
| --- | --- | --- | --- |
| post transforms can add imports/HMR facts after ordinary analysis | `target-executed` | original reproduction and #5 regression | focused client-dev path |
| moving full analysis later repairs the reproduced mismatch | `full-gate` | #5; CI `30487475188`; Zizmor `30487475253` | compatibility loss remains |
| first-party RSC intentionally inserts a raw dynamic import after analysis | `source-read` | `vite-plugin-react@9db4976…` | broader frequency unmeasured |
| naïve post-only reconciliation emits a false prune on unchanged repeat | `target-executed` | #9 old head `7132850…`; CI `30587631101`; macOS job `91022769607` | one discriminating platform receipt |
| file-import-only overlay loses previous accepted dependency before the next post hook | `target-executed` | #9 current CI `30588826788`; Ubuntu job `91026466344`; same failure across unit matrix | complete metadata not exercised there |
| staged restoration repairs previous accepted dependency visibility | `target-executed` | #12 prior CI `30589150453`; unit success on Linux/macOS/Windows | three-hook test-only placement |
| staged state currently omits self-accept, accepted exports, and imported bindings | `source-read`; `target-test-prepared` | #12 current diff and head `2eb0500…` | current CI `30593863720` queued |
| current #11 repairs snapshot timing and parsed identity | `source-read` | #11 current diff at `ff92d9b…` | current focused/full runs queued |
| equal source can still contain new graph-only watch facts | `source-read`; `target-test-prepared` | #13/#14 watch control | execution queued |
| analyzable dynamic imports remain in ordinary timestamp-invalidation state | `source-read`; `target-test-prepared` | ordinary `importAnalysis.ts`; corrected #13/#14 control | current corrected runs queued |

## Alternatives

### Baseline — current ordering without reconciliation

Preserves current hook behavior and raw imports. Loses final graph/HMR truth. Retained as a negative control.

### Option A — move full import analysis to the post bucket

Smallest one-pass source change and full named gate passed. Loses current post-hook input and first-party raw-import compatibility. Retained as an executed negative comparison.

### Option B1 — simple retained overlay

PR #9 proved the combined mechanism, then exposed false-prune and accepted-state losses. Current head `3854737…` is `HOLD / RETAIN AS EXECUTED NEGATIVE COMPARISON`; formatting alone must not revive it.

### Option B2 — current-public-base final reconciler

PR #11 is the preferred source basis. PR #14 repairs only late graph-only watch facts. Complete prior HMR state, atomic publication, rollback, and stale-request fencing remain required.

### Option B3 — staged restoration

PR #12 restored prior accepted dependency visibility and passed the focused lifecycle across the unit matrix at `63a2685…`. The current head tests whether the staged state can carry self accept, accepted exports, and bindings. Three jointly ordered hooks remain higher-cost ownership than one commit boundary.

### Option B4 — complete direct overlay

A complete previous-final overlay integrates prior imports, accepted deps, self accept, accepted exports, imported bindings, timestamp URLs, and graph-only facts into ordinary analysis. The B1 execution proves a file-only overlay is insufficient.

### Option B5 — transform-scoped graph transaction

A transaction preserves previous committed state while ordinary/final calculations are staged, then commits graph/HMR state and dispatches prunes once. It is the preferred fallback when complete overlay becomes distributed or incomplete.

## Current execution

| Surface/head | Receipt | Current state | Meaning |
| --- | --- | --- | --- |
| `#11@ff92d9b…` | focused `30590723703`; CI `30590723653`; Zizmor `30590723690` | queued/pending | preferred source basis awaiting execution |
| `#12@2eb0500…` | CI `30593863720`; Zizmor `30593863689` | queued/pending | complete staged-metadata controls |
| `#12@63a2685…` | CI `30589150453`; Zizmor `30589150450` | unit matrix passed; overall red from one format delta and Windows worker exit; Zizmor success | accepted-dependency restoration target-executed |
| `#13@3e588a2…` | focused `30593583611`; CI `30593583624`; Zizmor `30593583604` | queued | watch negative plus three compatibility controls |
| `#14@eb6ea75…` | publisher `30593631027`; CI `30593631043`; Zizmor `30593631035` | queued/pending | bounded watch-fact repair |
| `#9@3854737…` | CI `30588826788`; Zizmor `30588826793` | product control failed across unit matrix; Zizmor success | executed negative overlay comparison |

## Required next controls

Priority order:

1. execute #14 and inspect the first material failure;
2. execute #12 complete-metadata controls and classify each state component;
3. retain no false prune on unchanged repeat and one exact prune on removal/replacement;
4. preserve prior committed state on final parse/resolve failure;
5. fence stale or superseded transform publication;
6. cover partial-accept, self-accept, accepted exports, imported bindings, and normalization on the preferred source family;
7. cover classic workers, aliases, virtual IDs, optimized dependencies, and query imports;
8. measure final parse cost and source-map behavior after correctness ownership settles.

CSS post-transform watch files remain a sibling ownership question under PR #10. They may share graph-publication machinery, but CSS analysis and JavaScript import rewriting retain separate canonical conclusions.

## Current disposition

- Finding state: `comparative-evaluation-active`
- Review disposition: `REPAIR + EXECUTE Option B2; HOLD Option A promotion`
- Preferred source: PR #11 current-public-base reconciler
- Active bounded repair carrier: PR #14
- Active ownership comparison: PR #12
- Clearing condition: graph-only watch facts pass and one ownership model preserves complete prior HMR state with one rollback-safe publication
- Exact next transition: inspect #14 and #12 current-head executions, then integrate the surviving ownership model into the preferred source family
- Autonomous work remaining: execution, rollback/stale-request controls, comparison, carrier cleanup, independent exact-head review
- Non-delegable human decision: none

## Changes to the canonical conclusion

| Date | Record | Change |
| --- | --- | --- |
| 2026-07-29 | #2/#5 | reproduced mismatch; Option A passed named gates |
| 2026-07-31 | first-party RSC source and #6/#7 | Option A lost preferred status |
| 2026-07-31 | #9 repeat and accepted-state controls | simple overlay shown non-atomic and incomplete |
| 2026-07-31 | #12 prior CI | staged restoration proved previous accepted-dependency visibility can be restored |
| 2026-07-31 | #11 current head | snapshot order and parsed identity repaired on current public base |
| 2026-07-31 | self-review correction | analyzable dynamic imports confirmed inside ordinary timestamp-invalidation state; false criticism removed |
| 2026-07-31 | #13/#14 corrected | graph-only watch fact isolated as bounded current repair |

## References

- Fieldwork issue #25.
- Vite owned PRs #5–#14 as classified above.
- `evidence/20260731-workstream-b-transform-order-comparison.md`.
- `alternatives/B-late-reconciliation.md`.
- No public upstream interaction occurred.