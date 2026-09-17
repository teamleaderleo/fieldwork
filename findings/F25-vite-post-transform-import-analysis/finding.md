# F25: Reconcile Vite imports added by user post transforms

Finding state: `comparative-evaluation-active`

Workstream: `B — Browser, web tooling, and runtime boundaries`  
Canonical Fieldwork issue: `#25`  
Canonical finding path: `findings/F25-vite-post-transform-import-analysis/finding.md`  
Current source alternatives: `teamleaderleo/vite#5`, baseline probe #6, candidate-order probe #7, late-reconciliation prototype pending`  
Exact source identities: `#5@1a5b6b5327efa43fc4a33ed5ad51553b6d9c37ba`; `#6@7229602a44df963d0395bc9c0160ea062a014d5c`; `#7@e169bafdcfc0c25b3f77cadb41aebf762458586b`  
Original base revision: `8a245726944ed29225920d49be77c33c6e03afc8`  
Current source-read boundary: `vitejs/vite@843a47da6b93dbd3ce28c4ffae33a8ef338c6f05`; `vitejs/vite-plugin-react@9db4976a9f30e89205d327b9e951a0a1d4912fe5`  
Strongest evidence class: `full-gate` for original repair plus current first-party compatibility source and paired target-test-prepared probes  
Current review disposition: `EXECUTE Option B late-reconciliation prototype; Option A retained as negative comparison`  
Desk routing: `not-entered`  
Upstream contact authorized: `no`

## In simple words

Vite reads JavaScript during development to learn which files a page imports and which files can hot update. A plugin can run a transform after Vite's normal import analysis.

The original bug is real: a late plugin can add an import or HMR boundary that reaches the browser but never enters Vite's module graph.

The first repair moved the entire import-analysis pass after user post transforms. That fixes final graph truth, but current first-party React RSC code intentionally inserts a raw dynamic import after normal analysis so Vite will not rewrite it with `?import`.

The next direction is narrower: preserve normal import analysis and current post-hook observations, then reconcile only graph and HMR facts added by late transforms without reapplying every import rewrite.

## Why we care

The baseline can produce two truths:

- served code imports a dependency or declares an HMR boundary;
- Vite's development graph does not know it exists.

That can cause full reloads, stale graph state, missing accepted dependencies, and development/build divergence.

Moving full analysis later introduces a different incompatibility: supported first-party post transforms can rely on inserting imports after rewriting has finished. Reprocessing those imports changes their URL and observable hook stage.

The repair must preserve both graph truth and supported late-transform contracts.

## What happens if we leave it alone

Baseline consequence:

- post transforms can add real imports or HMR accepts that the graph misses.

Original Option A consequence:

- user post transforms receive pre-analysis source rather than currently analyzed source;
- React RSC's deliberate raw dynamic import becomes visible to import rewriting and can gain `?import`, defeating the plugin's stated intent.

Frequency outside the executed fixtures remains unmeasured.

## Governing goals and invariant

Governing invariant: Vite's development graph and HMR metadata must describe final served behavior without rerunning incompatible source-rewrite responsibilities after plugins that intentionally execute post-analysis.

| Goal or contract | Primary source | Consequence for the design |
| --- | --- | --- |
| Final graph truth | original #25 reproduction and PR #5 | late static imports and HMR accepts need reconciliation |
| Current hook-stage compatibility | Vite ordering source and probes #6/#7 | user post transforms should continue receiving normal import-analysis output unless an explicit contract changes |
| First-party raw-import behavior | `vite-plugin-react` RSC `rsc:vite-client-raw-import` | late reconciliation must not rewrite intentional raw imports with `?import` |
| Single ownership per effect | current import-analysis implementation | graph update, URL rewriting, helper injection, pruning, and diagnostics must not run twice ambiguously |
| Bounded cost | development transform hot path | extra parsing or scanning needs measured and narrow scope |

## Current finding

The original `order: 'post'` source change is no longer the preferred production direction. It remains valuable as a negative comparison because it proves one way to recover graph truth and makes the compatibility change executable.

The next implementation candidate is **Option B — compatibility-preserving late reconciliation**:

1. keep the existing normal import-analysis pass;
2. preserve the source currently observed by user post transforms;
3. inspect final post-transform source for graph and HMR facts added after normal analysis;
4. reconcile late imports, accepted dependencies, pruning, and HMR boundaries without blindly repeating URL rewriting or helper injection;
5. retain explicit ownership and diagnostics for unsupported late-import forms.

If bounded reconciliation cannot safely own these facts, the fallback is an explicit internal finalization stage outside user hooks rather than moving the existing full handler unchanged.

### Claim table

| Claim | Evidence class | Exact support | Limit |
| --- | --- | --- | --- |
| Current baseline misses imports and HMR boundaries added by post transforms. | `target-executed` | Vite PR #2 and original PR #5 regression | Focused plugin pattern |
| Moving full import analysis to the post bucket repairs the reproduced graph and HMR mismatch. | `full-gate` | PR #5, CI `30487475188`, Zizmor `30487475253` | Does not establish compatibility |
| Current baseline lets a user post transform observe import-analysis output. | `target-test-prepared` | baseline PR #6 at `7229602...` | CI `30586609039` and Zizmor `30586609010` pending at current record |
| Option A makes the same hook observe pre-analysis source. | `target-test-prepared` | candidate PR #7 at `e169baf...` | CI `30586630958` and Zizmor `30586630986` queued |
| First-party React RSC deliberately inserts a raw dynamic import after analysis to avoid `?import`. | `source-read` | `vite-plugin-react@9db4976...`, `packages/plugin-rsc/src/plugin.ts` and `browser.ts` | Exact paired execution still pending |
| Option A would expose that final import to non-JavaScript import rewriting. | `source-read` plus prepared paired probe | ordering model and PR #7 raw-import control | Full target receipts pending |

## System and ownership map

- Plugin list order places user post plugins before internal server-only plugins.
- Hook-level `order` independently groups `pre`, normal, and `post` transforms.
- Current `vite:import-analysis` is a normal transform hook.
- User post transforms therefore observe analyzed source.
- React RSC uses that stage to replace a placeholder with a real dynamic import after rewriting.
- Import analysis owns more than graph discovery: URL rewriting, HMR parsing, helper injection, environment replacement, pruning, diagnostics, and metadata updates.
- A final reconciliation stage should own only the late facts it can update without duplicating incompatible responsibilities.

## Historical and current precedent

### Plugin-injected imports must enter analysis where compatible

- Source: `vitejs/vite#23029`
- Principle supported: plugin-injected imports can require import-analysis visibility.
- Important difference: the precedent concerns optimized dependency and interop behavior, not post-hook stage compatibility.

### Current internal plugins run after user plugins by list order

- Source: `packages/vite/src/node/plugins/index.ts` at `843a47d...`
- Principle supported: internal server behavior is placed after user plugin lists.
- Important difference: hook-level order creates a second ordering dimension; normal internal analysis still runs before user post hooks.

### First-party RSC raw-import post transform

- Source: `vite-plugin-react@9db4976...`, `packages/plugin-rsc/src/plugin.ts`
- Principle supported: current first-party integration intentionally uses post-analysis insertion to avoid Vite URL rewriting.
- Important difference: it does not justify missing all graph and HMR facts added late.

Detailed evidence: `evidence/20260731-workstream-b-transform-order-comparison.md`.

## Alternatives instantiated or analyzed

### Baseline — no late reconciliation

Benefit: preserves every current hook observation and raw-import behavior.

Failure: final graph and HMR truth can be wrong.

Disposition: retained negative control.

### Option A — move full import analysis into the post bucket

Benefit: final source receives one complete analysis pass; original reproduction passes; tiny source diff.

Failure: changes post-hook observable input and conflicts with first-party RSC raw-import intent.

Disposition: retained negative comparison; no longer preferred.

Reopening trigger: evidence proves the first-party pattern is obsolete or a migration explicitly accepts the compatibility break.

### Option B — preserve normal analysis and reconcile late facts

Benefit: aims to preserve current stage compatibility and final graph truth.

Risks:

- duplicate parse and performance cost;
- unclear subset of late imports that can remain unrewritten yet enter the graph;
- pruning and HMR metadata can diverge if responsibilities split poorly;
- diagnostics can report the wrong transform owner.

Disposition: next implementation candidate.

It loses if a bounded prototype cannot update graph/HMR truth without duplicating rewriting, helper injection, or inconsistent pruning.

### Option C — explicit internal finalization stage

Benefit: gives final-source reconciliation an explicit lifecycle outside user hook ordering.

Risks: broader plugin-container design, new contract, more compatibility and maintenance surface.

Disposition: fallback if Option B cannot establish clear ownership.

### Option D — document the baseline limit

Benefit: no implementation compatibility change.

Failure: accepts demonstrated development graph divergence for supported hook metadata.

Disposition: declined unless every repair direction fails stronger compatibility controls.

## Option B required controls

A viable prototype must cover:

1. late static import added after normal analysis;
2. late HMR accept boundary and hot dependency;
3. intentional raw dynamic import that must remain without `?import`;
4. late import removal and module-graph pruning;
5. duplicate existing import versus newly late import;
6. helper and hot-context injection exactly once;
7. source maps and diagnostic ownership;
8. parse and resolution failure after a post transform;
9. post transform receiving the current analyzed-stage input;
10. measured parse/runtime cost;
11. current first-party React RSC fixture or a minimized equivalent;
12. current-main complete diff and named repository gates.

## Edge cases already covered

| Edge case or control | Evidence | Result |
| --- | --- | --- |
| Late static import under Option A | PR #5 regression | graph records dependency |
| Late HMR accept under Option A | PR #5 regression | accepted dependency recorded |
| Hot-context injection under Option A | PR #5 regression | present |
| Dependency update under Option A | PR #5 regression | HMR update rather than full reload |
| Cross-platform path identity | PR #2 correction | Linux, macOS, Windows identity control passed |
| Original repository gate | CI `30487475188` | passed named Node/platform matrix |
| Workflow analysis | Zizmor `30487475253` | passed |
| Baseline post-hook stage | PR #6 | exact target carrier pending |
| Option A post-hook stage and raw import | PR #7 | exact target carrier pending |

## Edge cases deferred or outside scope

| Edge case | Why deferred | Owning next record or reopening trigger |
| --- | --- | --- |
| CSS post-transform analysis | Different pipeline | Separate finding after reproduction |
| Bundled-development HMR engine | Separate experimental implementation | Existing bundled-dev lane |
| General plugin API contract change | Option B attempts to avoid one | Only if bounded reconciliation fails |
| Public migration or release note | No public authority and no selected final source | Delivery stage after acceptance |

## Exact execution and receipts

| Repository/head | Workflow | Result at this record | Evidence class |
| --- | --- | --- | --- |
| `teamleaderleo/vite@1a5b6b5327efa43fc4a33ed5ad51553b6d9c37ba` | CI `30487475188` | success | full named gate for Option A source |
| same | Zizmor `30487475253` | success | workflow analysis |
| `teamleaderleo/vite@7229602a44df963d0395bc9c0160ea062a014d5c` | CI `30586609039`; Zizmor `30586609010` | queued / pending | target-test-prepared baseline compatibility |
| `teamleaderleo/vite@e169bafdcfc0c25b3f77cadb41aebf762458586b` | CI `30586630958`; Zizmor `30586630986` | queued | target-test-prepared Option A compatibility |

Refresh exact live states before any promotion claim.

## Complete-diff and compatibility review

- PR #5 remains a valid executed negative comparison and a useful source prototype.
- PRs #6/#7 are execution carriers, not product candidates.
- The first-party RSC dependency defeats the prior default ranking of Option A.
- The next source branch must be separate and own only Option B reconciliation.
- Temporary workflows and test-only carriers require receipt transfer and retirement mapping.
- No source candidate is review-ready until Option B or Option C survives the paired compatibility matrix.

## Current disposition and desk routing

- Finding state: `comparative-evaluation-active`
- Review disposition: `EXECUTE Option B; HOLD delivery of Option A`
- Review Queue entry: none
- Delivery lane: `not-entered`
- Exact next transition: settle PRs #6/#7 and build a separate Option B late-reconciliation prototype
- Clearing condition: one implementation preserves final graph/HMR truth and the supported first-party post-transform contract at a current exact head
- Required subgates: paired stage/raw-import controls, pruning, errors, performance, complete diff, current-main repository gate
- Autonomous work remaining: Option B design/source, fixtures, execution, cross-review, carrier cleanup
- Non-delegable human decision: none

## Changes to the canonical conclusion

| Date | Record | Change in conclusion |
| --- | --- | --- |
| 2026-07-29 | Vite PR #2 | Reproduced served-source and development-graph mismatch |
| 2026-07-29 | Vite PR #5 | Demonstrated tiny Option A and passed named repository gates |
| 2026-07-31 | canonical protocol audit | Reclassified compatibility question from human decision to technical comparison |
| 2026-07-31 | first-party RSC source and PRs #6/#7 | Option A lost default-winner status; Option B became next candidate |

## References

- Fieldwork issue #25.
- Vite owned PRs #2, #5, #6, and #7.
- `findings/F25-vite-post-transform-import-analysis/evidence/20260731-workstream-b-transform-order-comparison.md`.
- `vitejs/vite@843a47da6b93dbd3ce28c4ffae33a8ef338c6f05`.
- `vitejs/vite-plugin-react@9db4976a9f30e89205d327b9e951a0a1d4912fe5`.
- Vite upstream PR #23029.
- No public upstream interaction occurred.
