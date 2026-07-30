# F25: Reconcile final Vite dev source with import analysis

Finding state: `comparative-evaluation-active`

Workstream: `B — Browser, web tooling, and runtime boundaries`  
Canonical Fieldwork issue: `#25`  
Canonical finding path: `findings/F25-vite-post-transform-import-analysis/finding.md`  
Canonical implementation or alternatives: `teamleaderleo/vite#5`, execution carriers `#6` and `#7`  
Exact implementation heads: candidate `1a5b6b5327efa43fc4a33ed5ad51553b6d9c37ba`; baseline probe `a8cd287f45d74940af4d9ec63246643aa0c275e2`; candidate probe `9914696ab349c183bd4ef14ea43ff097ee9be56b`  
Exact base revision: owned base `8a245726944ed29225920d49be77c33c6e03afc8`; current upstream research revision `843a47da6b93dbd3ce28c4ffae33a8ef338c6f05`  
Strongest evidence class: `full-gate` for candidate A repository CI; paired compatibility probes queued  
Current review disposition: `HOLD promotion; EXECUTE comparison`  
Desk routing: `not-entered`  
Upstream contact authorized: `no`

## In simple words

Vite reads transformed JavaScript to learn which files a page imports and which files can update through hot reload. A plugin can ask to run its transform at the end. Today that plugin can add an import after Vite already finished reading the file.

The browser receives the import, but Vite's development graph never records it. Candidate A makes Vite's internal import analysis run after user post transforms, which repairs that mismatch.

The candidate also changes what user post transforms receive. Today they receive code after Vite has rewritten imports and injected HMR helpers. Candidate A gives them source before import analysis. That compatibility change now has paired executable probes. The lane remains active until the alternatives are compared and one direction wins.

## Why we care

A missing graph edge creates two different truths:

- the browser executes code that imports the dependency;
- Vite's dev server believes the dependency and HMR boundary do not exist.

That can produce full-page reloads instead of hot updates, stale graph state, missing hot-context injection, and development behavior that diverges from production build output.

Moving analysis later may repair those failures while changing an observable plugin-stage contract. A correct repair must preserve final graph truth without casually breaking supported post-transform behavior.

## What happens if we leave it alone

Plugins using hook-level `transform: { order: 'post' }` can inject imports or `import.meta.hot.accept()` calls that are visible in served code yet absent from Vite's module graph. Dependency edits then fall back to a full reload. Production build still sees the final transformed source, so the discrepancy appears only in unbundled development.

The affected plugin population and real-world frequency remain unmeasured.

## Governing goals and invariant

Governing invariant: **Vite's development graph and HMR metadata must describe the final source delivered to the browser, while transform ordering remains compatible with documented hook semantics unless evidence justifies a contract change.**

| Goal or contract | Primary source | Consequence for the design |
| --- | --- | --- |
| Internal server-only plugins are intended to run after user plugins. | `packages/vite/src/node/plugins/index.ts` at upstream `843a47d…` | Final internal analysis should observe user behavior. |
| Hook-level `order` is separate from plugin-level `enforce`. | Current Vite Plugin API and `getSortedPluginsByHook()` | Plugin list position alone does not guarantee final execution. |
| Sequential transform hooks expose intermediate code to later hooks. | Rolldown Plugin API and current implementation | Moving analysis changes user post-hook input. |
| Dev and build should share plugin behavior where practical. | Current Vite Plugin API | An intentional dev-only divergence needs a clear reason and tests. |

## Current finding

Candidate A establishes the smallest one-pass repair for the demonstrated graph/HMR mismatch. Its complete repository gate passed.

Further source research establishes a compatibility delta that the earlier review packet did not execute: candidate A moves user post transforms from after import-analysis mutation to before it. That delta is now under paired baseline/candidate execution. No user decision is required; the next step is autonomous comparison under `DECISIONS.md`.

### Claim table

| Claim | Evidence class | Exact support | Limit |
| --- | --- | --- | --- |
| A user post transform can inject an import after current dev import analysis. | `target-executed` | Vite PR #2 reproduction | Focused scenario. |
| The missing import also removes the accepted HMR dependency and hot-context injection. | `target-executed` | PR #2 and PR #5 regression | One plugin pattern. |
| Marking the internal hook `order: 'post'` repairs the graph and HMR update. | `full-gate` plus focused assertion | PR #5 at `1a5b6b5…`; CI `30487475188`; Zizmor `30487475253` | Does not settle compatibility with post hooks that observe analyzed code. |
| Current hook sorting runs normal import analysis before user post transforms. | `source-read` | upstream `packages/vite/src/node/plugins/index.ts` and `importAnalysis.ts` at `843a47d…` | Source ordering, pending paired runtime receipt. |
| Candidate A runs user post transforms before internal import analysis. | `source-read` | PR #5 diff plus current hook sorting | Pending paired runtime receipt. |
| First-party code actively uses post transforms. | `source-read` | `vite-plugin-react` RSC `validate-import.ts` at `9db4976…` | No demonstrated dependence on analyzed source yet. |

## System and ownership map

- User plugins can define plugin-level `enforce` and hook-level `order` independently.
- `getSortedPluginsByHook()` groups `pre`, normal, and `post` hooks while preserving plugin-list order inside each group.
- `resolvePlugins()` appends user `postPlugins` before internal server-only plugins.
- `vite:import-analysis` parses dev code, rewrites import URLs, updates module imports, records HMR acceptance, and injects hot context.
- A later user post transform can currently observe those mutations and can also add new source afterward.
- Production build uses the bundler's final parse and therefore observes late imports.

## Historical precedent

### Import analysis must observe plugin-injected imports

- Source: https://github.com/vitejs/vite/pull/23029
- Revision or date: merged before the pinned July 2026 owned base
- Principle supported: imports injected by plugins must be visible to import-analysis behavior.
- Important difference: that precedent concerns optimized dependency files and interop imports. This finding concerns hook ordering and the user-visible transform stage in the dev pipeline.

### Vite separates plugin order from hook order

- Source: https://vite.dev/guide/api-plugin.html#plugin-ordering
- Revision or date: retrieved `2026-07-31`
- Principle supported: `enforce` ordering and hook-level `order` are independent contracts.
- Important difference: documentation describes the mechanisms but does not specify whether internal import analysis should precede or follow user post transforms.

### Sequential hooks expose intermediate transform results

- Source: https://rolldown.rs/apis/plugin-api
- Revision or date: retrieved `2026-07-31`
- Principle supported: sequential hooks run in order and later hooks receive prior results.
- Important difference: Vite's internal graph finalization has requirements beyond a generic transform chain.

### First-party React RSC post-transform validation

- Source: https://github.com/vitejs/vite-plugin-react/blob/9db4976a9f30e89205d327b9e951a0a1d4912fe5/packages/plugin-rsc/src/plugins/validate-import.ts
- Revision or date: `9db4976a9f30e89205d327b9e951a0a1d4912fe5`
- Principle supported: post transforms are a live first-party extension point used for dev graph-related behavior.
- Important difference: current source does not show that this plugin relies on import-analysis-mutated code.

## Decision criteria

| Priority | Criterion | How it will be measured or falsified |
| --- | --- | --- |
| 1 | Final graph truth | Late imports and HMR boundaries appear in module graph and update propagation. |
| 2 | Post-hook compatibility | Baseline and candidates record the exact code and graph state visible to representative post hooks. |
| 3 | Single ownership of mutation | URL rewriting, helper injection, pruning, error reporting, and graph updates do not duplicate or conflict. |
| 4 | Source-map and diagnostic coherence | Targeted source-map/error controls plus existing gates. |
| 5 | Runtime cost | Parse count and targeted benchmark or source accounting. |
| 6 | Architectural fit | Complete-diff review against Vite plugin-container and environment ownership. |

## Alternatives instantiated or analyzed

### Option A — move existing import analysis to the post bucket

- Artifact or branch: `teamleaderleo/vite#5`, head `1a5b6b5…`
- Invariant implemented: final user-transformed source is analyzed once.
- Expected benefit: smallest one-pass repair; full-gate evidence exists.
- Expected cost or failure: user post hooks no longer receive analyzed code.
- Discriminating control: candidate visibility carrier `teamleaderleo/vite#7`.
- Rollback boundary: one source hook wrapper plus regression.

### Baseline control — retain current ordering

- Artifact or branch: `teamleaderleo/vite#6`, head `a8cd287…`
- Invariant implemented: current post-hook stage visibility.
- Expected benefit: exact compatibility baseline.
- Expected cost or failure: final-source graph mismatch remains.
- Discriminating control: post hook must observe hot-context injection.
- Rollback boundary: execution-only test commit.

### Option B — retain current analysis and add bounded late-source reconciliation

- Artifact or branch: paper design pending probe results
- Invariant implemented: preserve current post-hook input while reconciling late graph/HMR additions.
- Expected benefit: may preserve both contracts.
- Expected cost or failure: second parse, duplicate state transitions, pruning complexity, and split ownership.
- Discriminating control: prototype must add late imports without duplicate rewriting or helper injection.
- Rollback boundary: separate owned branch if instantiated.

### Option C — explicit internal finalization phase outside user transform hooks

- Artifact or branch: source design pending evidence that Option A breaks supported behavior
- Invariant implemented: final graph ownership is separate from user-visible transform stages.
- Expected benefit: explicit semantic boundary.
- Expected cost or failure: broader plugin-container change and source-map/result plumbing.
- Discriminating control: minimal finalization prototype and complete pipeline tests.
- Rollback boundary: separate owned branch.

### Option D — retain current behavior and diagnose late imports

- Artifact or branch: paper alternative
- Invariant implemented: current transform-stage compatibility.
- Expected benefit: no ordering change.
- Expected cost or failure: rejects or documents a currently expressible plugin behavior while graph and served code can diverge.
- Discriminating control: contract and warning design cannot repair the demonstrated HMR behavior.
- Rollback boundary: documentation/diagnostic only.

## Comparative results

| Criterion | Baseline | Option A | Option B | Option C | Current result |
| --- | --- | --- | --- | --- | --- |
| Final graph truth | Fails reproduced late-import case | Passes focused regression and full gate | Unknown | Unknown | Option A leads. |
| Post-hook stage compatibility | Current contract | Changed; exact probe queued | Intended to preserve | Could define a new explicit boundary | Unresolved. |
| Mutation ownership | One early pass, incomplete final truth | One final pass | Likely two phases | One final internal phase | Option A simplest. |
| Implementation breadth | None | Two-file narrow diff | Medium/high | High | Option A leads. |
| Performance | Current | Same parse count | Extra parse likely | Depends on design | Option A leads. |

## Independent criticism

| Reviewer or evidence source | Counterexample or criticism | Response or new control | Effect on recommendation |
| --- | --- | --- | --- |
| Workstream B source cross-review | Candidate changes code visible to user post transforms. | Created paired target-native carriers #6 and #7 and reopened comparison. | Removed D3/user-decision routing; promotion held. |
| First-party RSC post-transform source | Post hooks participate in dev graph behavior. | Added first-party compatibility source review; targeted runtime integration remains available if needed. | Raises compatibility search priority without disproving Option A. |

## Selected direction and losing reasons

Selected direction: **comparison still active; Option A remains provisional leader**.

Why it leads: it is the only instantiated repair that restores final graph/HMR truth, retains one analysis pass, and has a complete repository gate.

It has not yet won because the post-hook input change needs exact execution and representative compatibility review.

| Losing or deferred option | Reason it has not won | Reopening or instantiation trigger |
| --- | --- | --- |
| Baseline | Demonstrated graph/HMR mismatch. | Only retained if every final-source repair creates a larger supported break. |
| Option B | Split mutation ownership and extra parse are unproven. | Instantiate if real supported reliance on analyzed post-hook input appears. |
| Option C | Broader than current evidence warrants. | Instantiate if Option A and bounded reconciliation both fail. |
| Option D | Does not repair graph truth. | Reconsider only if late imports are explicitly outside contract and compatibility cost dominates. |

## Edge cases covered

| Edge case or control | Evidence | Result |
| --- | --- | --- |
| Injected static import | PR #5 regression | Dependency appears in served code and graph. |
| Injected HMR accept boundary | PR #5 regression | Accepted dependency recorded. |
| Hot-context injection | PR #5 regression | `__vite__createHotContext` present in final output. |
| Dependency update | PR #5 regression | HMR `update`, not `full-reload`. |
| Cross-platform path identity | PR #2 correction | URL-facing graph lookup passes Linux, macOS, Windows. |
| Repository CI across Node 20/22/24/26 and major platforms | CI `30487475188` | Passed. |
| Workflow static analysis | Zizmor `30487475253` | Passed. |
| Baseline post-hook visibility | PR #6 | Exact CI queued. |
| Candidate post-hook visibility | PR #7 | Exact CI queued. |

## Edge cases deferred or outside scope

| Edge case | Why deferred | Owning next record or reopening trigger |
| --- | --- | --- |
| Representative plugins that inspect rewritten URLs or injected helpers | Requires source search and targeted integration | Continue in this finding after paired probes. |
| React RSC invalid-import graph timing | First-party post hook uses module graph but no failure established | Add targeted integration if source reasoning cannot settle timing. |
| CSS post transforms and `cssAnalysisPlugin` ordering | Separate content and graph pipeline | Open a sibling finding after bounded reproduction. |
| Source-map quality after ordering change | Existing gates passed; no targeted measurement | Add before delivery-gate-ready if candidate remains selected. |
| Bundled-development plugin behavior | Different HMR engine | Separate Vite bundled-dev finding. |
| Performance impact | Same parse count for Option A; alternatives may differ | Benchmark if Option B/C is instantiated or source review identifies risk. |

## Exact execution and receipts

| Repository/head | Command or workflow | Platform/environment | Result | Evidence class |
| --- | --- | --- | --- | --- |
| `teamleaderleo/vite@1a5b6b5327efa43fc4a33ed5ad51553b6d9c37ba` | CI `30487475188` | Node 20/22/24/26 Ubuntu; Node 24 macOS and Windows | Named CI matrix passed | `full-gate` |
| Same head | Zizmor `30487475253` | GitHub workflow analysis | Passed | `target-executed` |
| `teamleaderleo/vite@a8cd287f45d74940af4d9ec63246643aa0c275e2` | CI `30586292234`; Zizmor `30586292172` | GitHub Actions | Queued | pending |
| `teamleaderleo/vite@9914696ab349c183bd4ef14ea43ff097ee9be56b` | CI `30586307192`; Zizmor `30586307115` | GitHub Actions | Queued | pending |

## Complete-diff and compatibility review

- Candidate A complete changed-file fence: import-analysis source and focused regression.
- Baseline carrier #6: one execution-only test file.
- Candidate carrier #7: one execution-only test file based on candidate A.
- Owned candidate base relationship: candidate based on `8a245726…`; current upstream research moved to `843a47da…`, so a later refresh is required.
- Temporary carriers #6 and #7 remain non-canonical and must close after receipts transfer.
- Known routine work remaining: paired execution, representative post-hook search, current-main refresh, and targeted source-map control if Option A remains selected.
- Earlier ACCEPT remains evidence for candidate A's source coherence at its exact head; it no longer resolves the broadened compatibility claim.

## Current disposition and desk routing

- Finding state: `comparative-evaluation-active`
- Review disposition: `HOLD promotion; EXECUTE paired visibility and compatibility comparison`
- Review Queue entry: remove active decision request; independent reviews may continue against concrete options
- Delivery lane: `not-entered`
- Exact next transition: complete paired probes, search representative post-hook dependencies, then select Option A or instantiate bounded Option B
- Clearing condition: one selected exact-head direction satisfies final graph truth and the supported post-hook compatibility boundary
- Required subgates: paired CI receipts; current upstream refresh; exact-head review; carrier retirement
- Autonomous work remaining: execution, ecosystem source review, possible alternative prototype, adversarial cross-review
- Non-delegable human decision: `none`
- Why further autonomous work cannot settle it: `not applicable`

## Changes to the canonical conclusion

| Date | Pull request or commit | Change in conclusion |
| --- | --- | --- |
| 2026-07-29 | Vite PR #2 | Reproduced browser/dev-graph mismatch and corrected cross-platform probe identity. |
| 2026-07-29 | Vite PR #5 | Added narrow explicit-order repair and complete repository CI evidence. |
| 2026-07-30 | Exact-head cross-review | Found no source defect and classified the remaining question as design judgment. |
| 2026-07-31 | PRs #6/#7 and Fieldwork PR #264 | Reclassified the question as autonomous comparative evaluation after identifying the post-hook input compatibility delta. |

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
- https://github.com/vitejs/vite-plugin-react/blob/9db4976a9f30e89205d327b9e951a0a1d4912fe5/packages/plugin-rsc/src/plugins/validate-import.ts
- `findings/F25-vite-post-transform-import-analysis/evidence/20260731-workstream-b-transform-order-comparison.md`
- CI `30487475188`
- Zizmor `30487475253`
