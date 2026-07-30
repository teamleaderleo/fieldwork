# F25: Reconcile final Vite dev source with import analysis

Finding state: `comparative-evaluation-active`

Workstream: `B — Browser, web tooling, and runtime boundaries`  
Canonical Fieldwork issue: `#25`  
Canonical finding path: `findings/F25-vite-post-transform-import-analysis/finding.md`  
Canonical implementation or alternatives: candidate A `teamleaderleo/vite#5`; execution carriers `#6` and `#7`; Option B prototype pending  
Exact heads: A `1a5b6b5327efa43fc4a33ed5ad51553b6d9c37ba`; baseline carrier `7229602a44df963d0395bc9c0160ea062a014d5c`; A carrier `e169bafdcfc0c25b3f77cadb41aebf762458586b`  
Exact base or source revision: owned base `8a245726944ed29225920d49be77c33c6e03afc8`; current upstream research `843a47da6b93dbd3ce28c4ffae33a8ef338c6f05`  
Strongest evidence class: `full-gate` for candidate A; paired compatibility execution queued  
Current review disposition: `REPAIR direction; EXECUTE comparison; prototype Option B`  
Desk routing: `not-entered`  
Upstream contact authorized: `no`

## In simple words

Vite reads transformed JavaScript to build its development import graph and hot-reload boundaries. A plugin can run a transform at the end. Today that plugin can add an import after Vite already read the file, so the browser receives code that the graph never records.

Candidate A fixes that by moving all import analysis after user post transforms. Further research found a current first-party React RSC plugin that deliberately adds a dynamic import after import analysis so Vite will leave it raw instead of adding `?import`. Candidate A reverses that behavior.

The preferred next direction is now a compatibility-preserving late reconciliation phase: keep current import analysis and post-hook visibility, then update graph/HMR truth for safe late additions without rerunning every rewriting side effect.

## Why we care

Without a repair, final browser code and Vite's graph disagree. That can cause full reloads, stale HMR boundaries, missing hot-context setup, and dev/build divergence.

With candidate A unchanged, Vite repairs graph truth by changing an active first-party post-transform contract. The RSC plugin's source explicitly relies on injecting a dynamic import last to avoid Vite's `?import` rewrite. A viable repair needs to preserve both behaviors or document and execute a broader contract migration.

## What happens if we leave it alone

A post transform can inject imports or `import.meta.hot.accept()` calls that appear in served code but remain absent from the module graph. Dependency changes may then full-reload or propagate incorrectly.

The affected ecosystem frequency remains unmeasured. The mechanism and focused consequence are executed.

## Governing invariant

**Vite's development graph and HMR metadata must describe final served source, while supported post transforms retain their current observable input and intentional late-import behavior unless a separately evidenced contract change is chosen.**

| Contract or goal | Primary source | Design consequence |
| --- | --- | --- |
| Internal plugins are intended to run after user plugins. | Vite `plugins/index.ts` at `843a47d…` | Final graph ownership must account for user transforms. |
| Hook-level `order` is separate from plugin-level `enforce`. | Vite Plugin API and `getSortedPluginsByHook()` | Moving one hook changes the stage visible to later hooks. |
| Sequential transforms expose prior results to later hooks. | Rolldown Plugin API | Current post-transform input is observable behavior. |
| RSC raw imports are deliberately injected after analysis. | `vite-plugin-react` `plugin.ts` at `9db4976…` | Full late rewriting breaks a first-party intent. |

## Current finding

Candidate A is source-coherent and passed the named repository gate for the originally tested graph/HMR invariant. It is no longer the preferred complete repair because current first-party source establishes a concrete compatibility dependency on the existing ordering.

Option B — preserve normal import analysis and add bounded late graph/HMR reconciliation — is the next prototype direction. It must separate final graph tracking from URL rewriting and helper injection.

### Claim table

| Claim | Evidence class | Exact support | Limit |
| --- | --- | --- | --- |
| Current post transforms can add imports after graph analysis. | `target-executed` | Vite PR #2 | Focused plugin pattern. |
| The late import and HMR boundary are absent from graph state. | `target-executed` | PRs #2 and #5 regression | One dev path. |
| Candidate A restores graph/HMR truth. | `full-gate` | PR #5 at `1a5b6b5…`; CI `30487475188`; Zizmor `30487475253` | Does not preserve current post-hook stage behavior. |
| Current first-party RSC source injects a dynamic import in a post transform to avoid `?import`. | `source-read` | `vite-plugin-react` `packages/plugin-rsc/src/plugin.ts` at `9db4976…` | Paired minimal target test is queued. |
| Candidate A would analyze and rewrite that late dynamic import. | `source-read` plus prepared target control | Hook order plus carrier #7 at `e169baf…` | Exact workflow result pending. |

## Historical precedent

### Plugin-injected imports must reach import analysis

- Source: https://github.com/vitejs/vite/pull/23029
- Principle: plugin-added imports must participate in Vite's analysis behavior.
- Difference: the precedent does not settle when rewriting versus graph reconciliation should occur.

### Plugin order and hook order are distinct

- Source: https://vite.dev/guide/api-plugin.html#plugin-ordering
- Retrieved: `2026-07-31`
- Principle: plugin-level and hook-level order are separate.
- Difference: the docs do not define a dedicated final graph phase.

### Sequential hook results are visible

- Source: https://rolldown.rs/apis/plugin-api
- Retrieved: `2026-07-31`
- Principle: later sequential hooks receive earlier transform results.
- Difference: Vite also owns graph and HMR state outside generic transformation.

### First-party raw dynamic import escape

- Source: https://github.com/vitejs/vite-plugin-react/blob/9db4976a9f30e89205d327b9e951a0a1d4912fe5/packages/plugin-rsc/src/plugin.ts
- Related caller: https://github.com/vitejs/vite-plugin-react/blob/9db4976a9f30e89205d327b9e951a0a1d4912fe5/packages/plugin-rsc/src/browser.ts
- Principle: a post transform intentionally bypasses Vite import rewriting.
- Difference: the pattern still needs graph/HMR semantics appropriate to its dynamic runtime target.

## Decision criteria

| Priority | Criterion | Discriminating evidence |
| --- | --- | --- |
| 1 | Final graph and HMR truth | Late static import and late accept-boundary regression. |
| 2 | First-party compatibility | Raw dynamic import stays free of `?import`. |
| 3 | Current post-hook visibility | Baseline/candidate stage probes. |
| 4 | Single state ownership | No duplicate rewriting, helper injection, pruning, or error replacement. |
| 5 | Removal correctness | Late imports disappearing prune graph edges. |
| 6 | Diagnostics and maps | Parse, resolve, and source-map controls. |
| 7 | Proportional cost | Parse-count/source accounting and targeted benchmark if needed. |

## Alternatives

### Baseline — current ordering

- Carrier: `teamleaderleo/vite#6` at `7229602…`
- Wins: preserves current post-hook input and first-party raw-import pattern.
- Loses: reproduced final graph/HMR mismatch.

### Option A — move full import analysis to `order: 'post'`

- Candidate: `teamleaderleo/vite#5` at `1a5b6b5…`
- Carrier: `teamleaderleo/vite#7` at `e169baf…`
- Wins: smallest one-pass final-source repair; full-gate evidence.
- Loses: changes post-hook input and conflicts with explicit first-party raw-import intent.
- Current status: retained negative comparison, no longer preferred.

### Option B — normal analysis plus bounded late reconciliation

- Candidate: pending separate owned branch.
- Goal: preserve current rewriting stage, then reconcile graph/HMR additions from final source.
- Required boundary: late reconciliation must not rewrite intentional raw imports or duplicate hot-context/env injection.
- Current status: preferred prototype direction.

### Option C — internal finalization outside user transform hooks

- Candidate: paper design until Option B proves unsafe.
- Goal: establish an explicit final graph phase with its own result contract.
- Cost: broader plugin-container and source-map plumbing.
- Current status: fallback.

### Option D — diagnose or forbid late imports

- Wins: preserves exact current execution.
- Loses: leaves or rejects an expressible behavior instead of repairing graph truth.
- Current status: rejected unless all repair directions fail.

## Comparative results

| Criterion | Baseline | Option A | Option B | Option C | Current result |
| --- | --- | --- | --- | --- | --- |
| Final graph truth | Fails | Passes focused/full gate | Target requirement | Target requirement | A proven; B/C pending. |
| Raw late import | Preserves | First-party conflict | Must preserve | Must define | B preferred. |
| Post-hook input | Preserves | Changes | Preserves | Could preserve | B preferred. |
| Mutation ownership | One incomplete early pass | One complete late pass | Split but bounded | Explicit final owner | Needs prototype. |
| Breadth | None | Narrow | Medium | Broad | B before C. |

## Edge cases covered

| Case | Evidence | Result |
| --- | --- | --- |
| Late static import | PR #5 regression | Candidate A records graph edge. |
| Late HMR accept boundary | PR #5 regression | Candidate A records accepted dependency. |
| Hot-context injection | PR #5 regression | Final output receives helper. |
| Dependency update | PR #5 regression | HMR update replaces full reload. |
| Cross-platform graph lookup | PR #2 and full matrix | Passed Linux, macOS, Windows. |
| Current post-hook input | Carrier #6 | Exact head queued. |
| Candidate A post-hook input | Carrier #7 | Exact head queued. |
| First-party raw-import analogue | Carriers #6/#7 | Exact heads queued. |

## Deferred or next controls

| Case | Reason | Next record or trigger |
| --- | --- | --- |
| Option B late static import and HMR tracking | Prototype pending | Same finding, new owned branch. |
| Late import removal/pruning | Requires Option B | Same prototype. |
| Late parse/resolve failure | Requires result contract | Same prototype. |
| Actual RSC integration | Minimal analogue may settle mechanism first | Run first-party integration if ambiguity remains. |
| CSS analysis ordering | Separate CSS graph pipeline | Sibling finding after bounded reproduction. |
| Bundled development | Different engine | Separate finding. |

## Exact execution and receipts

| Repository/head | Workflow | Result | Evidence class |
| --- | --- | --- | --- |
| `teamleaderleo/vite@1a5b6b5…` | CI `30487475188` | Passed full named matrix | `full-gate` |
| Same head | Zizmor `30487475253` | Passed | `target-executed` |
| `teamleaderleo/vite@7229602…` | CI `30586609039`; Zizmor `30586609010` | queued/pending | pending |
| `teamleaderleo/vite@e169baf…` | CI `30586630958`; Zizmor `30586630986` | pending/queued | pending |

## Complete-diff and compatibility review

- Candidate A complete diff remains two product/test files.
- Carriers #6 and #7 each contain one execution-only test file and are non-canonical.
- Current upstream source research revision is newer than the owned candidate base; selected implementation requires a refresh.
- Earlier ACCEPT proves candidate A's exact tested behavior, not the expanded compatibility claim.
- Carriers must close after receipts transfer.

## Current disposition and routing

- Finding state: `comparative-evaluation-active`
- Review disposition: `REPAIR direction; EXECUTE paired controls; prototype Option B`
- Review Queue entry: no user decision request
- Delivery lane: `not-entered`
- Exact next transition: implement bounded late reconciliation on a separate owned branch
- Clearing condition: one exact-head candidate preserves final graph truth and first-party raw-import/post-hook compatibility
- Required subgates: paired receipts; Option B focused execution; current-source refresh; complete-diff review; carrier retirement
- Autonomous work remaining: prototype, execution, source review, adversarial cross-review
- Non-delegable human decision: `none`

## Changes to the conclusion

| Date | Record | Change |
| --- | --- | --- |
| 2026-07-29 | Vite PR #2 | Reproduced final-source graph mismatch. |
| 2026-07-29 | Vite PR #5 | Implemented and fully gated one-pass late analysis. |
| 2026-07-30 | Exact-head review | Accepted A as coherent and treated compatibility as a design judgment. |
| 2026-07-31 | Fieldwork PR #264 and Vite #6/#7 | Reopened as autonomous comparison. |
| 2026-07-31 | First-party RSC source review | Found explicit current reliance on post-analysis dynamic-import injection; Option B became preferred prototype. |

## References

- https://github.com/teamleaderleo/fieldwork/issues/25
- https://github.com/teamleaderleo/vite/pull/2
- https://github.com/teamleaderleo/vite/pull/5
- https://github.com/teamleaderleo/vite/pull/6
- https://github.com/teamleaderleo/vite/pull/7
- https://github.com/vitejs/vite/pull/23029
- https://github.com/vitejs/vite/blob/843a47da6b93dbd3ce28c4ffae33a8ef338c6f05/packages/vite/src/node/plugins/index.ts
- https://github.com/vitejs/vite/blob/843a47da6b93dbd3ce28c4ffae33a8ef338c6f05/packages/vite/src/node/plugins/importAnalysis.ts
- https://vite.dev/guide/api-plugin.html#plugin-ordering
- https://rolldown.rs/apis/plugin-api
- https://github.com/vitejs/vite-plugin-react/blob/9db4976a9f30e89205d327b9e951a0a1d4912fe5/packages/plugin-rsc/src/plugin.ts
- https://github.com/vitejs/vite-plugin-react/blob/9db4976a9f30e89205d327b9e951a0a1d4912fe5/packages/plugin-rsc/src/browser.ts
- `findings/F25-vite-post-transform-import-analysis/evidence/20260731-workstream-b-transform-order-comparison.md`
