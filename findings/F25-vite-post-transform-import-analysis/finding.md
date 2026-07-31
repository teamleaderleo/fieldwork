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
- Option B1, retained-state prototype: `#9@38547370decd7328c50244596a580fe207fb3655`
- Option B2, current-public-base reconciler: `#11@ff92d9b4d933d23edfaefa908cb0e1d143bce546`
- Option B3, staged restoration comparison: `#12@63a26854bfcd44de66286ffdd3cf04ff0066fe9f`
- Option B2 bounded current-facts repair: `#14@4de42376d3bd34e2b559e68e721f698a62b62a96`

### Execution and criticism surfaces

- baseline stage probe: `#6@7229602a44df963d0395bc9c0160ea062a014d5c`
- Option A stage/raw-import probe: `#7@e169bafdcfc0c25b3f77cadb41aebf762458586b`
- desired combined contract: `#8@5d9a0ca545cd7763a7d8bfffd3a646ecb6c4a076`
- CSS sibling watch-file probe: `#10@81719c925a53040135e6bb8bfcbabd24365bcd51`
- adversarial current-public-base controls: `#13@b139c1be0965158970bd4353ac05eee5d51793bb`

Strongest evidence class: Candidate A `full-gate`; Option B lifecycle `target-executed` negative and repaired targeted controls; current-public-base repairs remain queued.  
Current review disposition: `REPAIR + EXECUTE Option B2; retain direct overlay or graph transaction as the publication model; HOLD Option A promotion`.  
Non-delegable human decision: `none`.  
Desk routing: `not-entered`.

## In simple words

Vite rewrites development imports, records module dependencies, and stores hot-update boundaries. A plugin can run after ordinary import analysis and add behavior that reaches the browser after Vite has already committed its graph state.

Moving the whole analysis pass later fixes final graph truth, but it changes what user post transforms observe. Current first-party React RSC code deliberately inserts a raw dynamic import after normal rewriting so Vite does not add `?import`.

The selected repair family therefore keeps ordinary rewriting where it is and performs bounded final reconciliation for graph and HMR facts. The unresolved ownership question is how one transform request publishes one coherent graph transition without a temporary prune or temporary loss of prior accepted state.

## Why we care

Without a repair, served code and the development graph can disagree. That can produce stale edges, full reloads, missing accepted HMR dependencies, and dev/build divergence.

A careless repair can create a different set of defects:

- rewrite a deliberately raw first-party import;
- emit a false client prune on every unchanged repeat transform;
- mark a dynamic import as static and permit the wrong soft-invalidation path;
- miss a late `addWatchFile()` because source text did not change;
- hide the previous accepted HMR boundary while a later plugin reads the graph;
- publish partial state after parse, resolution, or stale-request failure.

## Governing invariant

**Final development graph and HMR metadata must describe the final transform result and graph-only plugin facts while ordinary source rewriting and current post-hook compatibility remain intact. One request publishes one coherent transition: unchanged final state emits no prune, and a real removal emits the exact prune set once.**

## Governing contracts

| Contract | Primary evidence | Consequence |
| --- | --- | --- |
| final graph and HMR truth | original reproduction and Candidate A regression | late imports and accepts must enter final state |
| current post-hook source | hook ordering, #6/#7, current first-party source | ordinary rewrite output remains visible to user post hooks |
| raw-import escape | React RSC `rsc:vite-client-raw-import` | final graph work must not rerun incompatible URL rewriting |
| atomic transition | #9 false-prune execution | ordinary and final analysis cannot dispatch two contradictory transitions |
| graph-only facts | transform-context `_addedImports` | source equality cannot imply graph equality |
| static/dynamic distinction | `EnvironmentModuleGraph.staticImportedUrls` contract | only static source imports may enable ordinary soft invalidation |
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

The earlier snapshot-order and raw-substring objections are repaired on the current head. Three disposition-bearing defects remain:

1. equal-source early return skips a source-preserving late `addWatchFile()`;
2. every resolved final import currently enters `staticImportedUrls`, including dynamic imports;
3. ordinary analysis can dispatch a transient prune before final reconciliation re-adds an unchanged late edge.

PR #14 instantiates bounded repairs for the first two current defects. It snapshots the ordinary-analysis watch set, reconciles later graph-only additions, and adds only non-dynamic imports to static state. Publisher `30592816438` is queued at exact carrier head `4de4237…`.

The third defect requires ownership before prune dispatch. The leading models are:

- integrate a retained previous-final overlay into ordinary analysis; or
- stage ordinary and final graph changes in a transform-scoped transaction and commit once.

PR #12 remains an executable distributed restoration comparison. Even if it passes, three jointly ordered hooks are a higher reasoning and integration cost than one graph commit boundary.

## Claim table

| Claim | Evidence class | Exact support | Limit |
| --- | --- | --- | --- |
| post transforms can add imports/HMR facts after ordinary analysis | `target-executed` | original reproduction and #5 regression | focused client-dev path |
| moving full analysis later repairs the reproduced graph mismatch | `full-gate` | #5; CI `30487475188`; Zizmor `30487475253` | compatibility loss remains |
| first-party RSC intentionally inserts a raw dynamic import after analysis | `source-read` | `vite-plugin-react@9db4976…` | broader frequency unmeasured |
| naïve post-only reconciliation emits a false prune on unchanged repeat | `target-executed` | #9 old head `7132850…`; CI `30587631101`; macOS job `91022769607` | one discriminating platform receipt |
| repaired #9 add/retain/remove targeted unit passed Windows and macOS | `target-executed` | #9 head `bf18a77…`; CI `30588034626` | later unrelated suites failed; head moved |
| current #11 repairs snapshot timing and parsed identity | `source-read` | #11 current diff at `ff92d9b…` | current focused/full runs queued |
| equal source can still contain new graph-only watch facts | `source-read`; `target-test-prepared` | #13/#14 watch control | execution queued |
| a dynamic late import must remain outside static invalidation state | `source-read`; `target-test-prepared` | moduleGraph contract and #13/#14 control | execution queued |
| staged restoration is executable | `target-test-prepared` | #12 at `63a2685…` | CI still running |

## Alternatives

### Baseline — current ordering without reconciliation

Preserves current hook behavior and raw imports. Loses final graph/HMR truth. Retained as a negative control.

### Option A — move full import analysis to the post bucket

Smallest one-pass source change and full named gate passed. Loses current post-hook input and first-party raw-import compatibility. Retained as an executed negative comparison.

### Option B1 — retained overlay prototype

PR #9 proved the combined mechanism, then exposed the false-prune lifecycle. A later head passed focused add, retain, and remove transitions. Current head `3854737…` adds prior accepted-state visibility but ordinary CI `30588826788` failed formatting and unit jobs across the matrix; that head needs exact failure classification before reuse.

### Option B2 — current-public-base final reconciler

PR #11 is the preferred source basis. PR #14 repairs late watch facts and static/dynamic classification on top of it. Atomic publication remains required.

### Option B3 — staged restoration

PR #12 restores previous graph view before the user post hook and reconciles final source after it. Zizmor `30589150450` passed; CI `30589150453` is in progress. Retained as a concrete comparison, not the default winner.

### Option B4 — direct overlay or transform-scoped graph transaction

Direct overlay integrates prior final state into ordinary analysis. A transaction stages both views and calls graph update/prune once. This is the preferred ownership family if bounded #14 repairs pass.

## Current execution

| Surface/head | Receipt | Current state | Meaning |
| --- | --- | --- | --- |
| `#11@ff92d9b…` | focused `30590723703`; CI `30590723653`; Zizmor `30590723690` | queued/pending | current source basis awaiting execution |
| `#12@63a2685…` | CI `30589150453`; Zizmor `30589150450` | CI in progress; Zizmor success | staged comparison active |
| `#13@b139c1b…` | focused `30592606208`; CI `30592606321`; Zizmor `30592606239` | queued/pending | four adversarial controls |
| `#14@4de4237…` | publisher `30592816438`; CI `30592816370`; Zizmor `30592816378` | queued | bounded current-facts repair |
| `#9@3854737…` | CI `30588826788`; Zizmor `30588826793` | CI failed; Zizmor success | accepted-state comparison requires failure classification |

## Required next controls

Priority order:

1. execute #14 and inspect the first material failure;
2. retain no false prune on unchanged repeat and one exact prune on removal/replacement;
3. define prior accepted-HMR graph state visible to the next user post hook;
4. preserve prior committed state on final parse/resolve failure;
5. fence stale or superseded transform publication;
6. cover binding, partial-accept, self-accept, and `acceptExports` transitions;
7. cover classic workers, aliases, virtual IDs, optimized dependencies, and query imports;
8. measure final parse cost and source-map behavior after correctness ownership settles.

CSS post-transform watch files remain a sibling ownership question under PR #10. They may share graph-publication machinery, but CSS analysis and JavaScript import rewriting retain separate canonical conclusions.

## Current disposition

- Finding state: `comparative-evaluation-active`
- Review disposition: `REPAIR + EXECUTE Option B2; HOLD Option A promotion`
- Preferred source: PR #11 current-public-base reconciler
- Active bounded repair carrier: PR #14
- Clearing condition: current-fact controls pass and one ownership model prevents transient prune publication
- Exact next transition: inspect #14 publisher, then integrate no-false-prune lifecycle into the preferred source family
- Autonomous work remaining: source review, execution, rollback/stale-request controls, comparison, carrier cleanup, independent exact-head review
- Non-delegable human decision: none

## Changes to the canonical conclusion

| Date | Record | Change |
| --- | --- | --- |
| 2026-07-29 | #2/#5 | reproduced mismatch; Option A passed named gates |
| 2026-07-31 | first-party RSC source and #6/#7 | Option A lost preferred status |
| 2026-07-31 | #9 executed repeat control | post-only two-pass publication shown non-atomic |
| 2026-07-31 | #11 current head | snapshot order and parsed identity repaired on current public base |
| 2026-07-31 | #13/#14 | graph-only watch and dynamic/static facts made executable |

## References

- Fieldwork issue #25.
- Vite owned PRs #5–#14 as classified above.
- `evidence/20260731-workstream-b-transform-order-comparison.md`.
- `alternatives/B-late-reconciliation.md`.
- No public upstream interaction occurred.