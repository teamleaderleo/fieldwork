# F25: Reconcile final Vite dev source with import analysis

Finding state: `comparative-evaluation-active`

Workstream: `B — Browser, web tooling, and runtime boundaries`  
Canonical Fieldwork issue: `#25`  
Canonical finding path: `findings/F25-vite-post-transform-import-analysis/finding.md`  
Canonical alternatives: `teamleaderleo/vite#5`, `#6`, `#7`, `#8`, and `#9`  
Exact heads: A `1a5b6b5327efa43fc4a33ed5ad51553b6d9c37ba`; baseline `7229602a44df963d0395bc9c0160ea062a014d5c`; A comparison `e169bafdcfc0c25b3f77cadb41aebf762458586b`; desired contract `5d9a0ca545cd7763a7d8bfffd3a646ecb6c4a076`; Option B prototype `bf18a77bc97d63dc01aa7b3fab5ad10340f8e89a`  
Exact base or source revision: owned base `8a245726944ed29225920d49be77c33c6e03afc8`; current upstream research `843a47da6b93dbd3ce28c4ffae33a8ef338c6f05`  
Strongest evidence class: Candidate A `full-gate`; Option B `target-executed failure` plus repaired exact head queued  
Current review disposition: `REPAIR and EXECUTE Option B; HOLD Candidate A promotion`  
Desk routing: `not-entered`  
Upstream contact authorized: `no`

## In simple words

Vite reads JavaScript after plugins transform it. That reading step rewrites imports, builds the development dependency graph, and records hot-reload boundaries.

A plugin can ask to run its transform last. Today that plugin can add an import after Vite already read the file. The browser receives the import, but Vite's graph never records it.

Candidate A moves all import analysis to the end. It fixes the graph, but a current first-party React RSC plugin deliberately adds a dynamic import after analysis so Vite will leave it raw instead of adding `?import`. Candidate A breaks that escape.

Option B keeps ordinary import analysis where it is, then performs a smaller final reconciliation for graph and HMR state. The first prototype proved the combined one-shot behavior, then failed a repeat-transform control by emitting a false prune. A retained late-state overlay now targets add, retain, and remove transitions explicitly.

## Why we care

Without a repair, served browser code and Vite's graph can disagree. That can cause full reloads, stale HMR boundaries, missing hot-context setup, and development behavior that differs from production build behavior.

Moving the entire analysis pass later repairs that mismatch by changing an active first-party ordering contract. A sound repair must preserve final graph truth and intentional post-analysis imports, or explicitly demonstrate why one contract must change.

## What happens if we leave it alone

A post transform can add static imports or `import.meta.hot.accept()` calls that never enter the module graph. Changes to those dependencies can propagate incorrectly or trigger a full reload.

The mechanism and focused consequence are executed. Ecosystem frequency remains unmeasured.

## Governing invariant

**Vite's development graph and HMR metadata must describe final served source, while supported post transforms retain their current observable input and intentional late-import behavior unless a separately evidenced migration changes that contract.**

| Goal or contract | Primary evidence | Design consequence |
| --- | --- | --- |
| Internal server plugins are intended to complete Vite-owned dev processing. | Vite `plugins/index.ts` at `843a47d…` | Final graph ownership must account for user transforms. |
| Hook-level `order` and plugin-level `enforce` are separate. | Current Vite Plugin API and hook sorter | Moving a hook changes user-visible stage ordering. |
| Sequential transforms expose prior results to later hooks. | Current Rolldown Plugin API | Current post-transform input is observable behavior. |
| React RSC inserts a dynamic import last to avoid `?import`. | `vite-plugin-react` `plugin.ts` at `9db4976…` | Full late rewriting conflicts with first-party intent. |

## Current finding

Candidate A remains the smallest one-pass proof that final-source analysis repairs the graph and HMR problem. Its exact head passed the named Vite CI matrix.

Candidate A is no longer the preferred complete direction because first-party React RSC source provides a concrete counterexample to moving every rewriting side effect after post transforms.

Option B is the preferred family. Its first implementation separated normal rewriting from final graph/HMR reconciliation. Target execution showed that a naïve two-pass union emits a transient prune when the same late dependency is present on a second transform. The revised prototype retains a per-environment late import overlay through ordinary analysis, then replaces it from final source.

### Claim table

| Claim | Evidence class | Exact support | Limit |
| --- | --- | --- | --- |
| A post transform can add imports after current dev analysis. | `target-executed` | Vite PR #2 | Focused plugin pattern. |
| Missing late graph/HMR state changes update behavior. | `target-executed` | PRs #2 and #5 regression | One dev pipeline. |
| Candidate A repairs final graph and HMR truth. | `full-gate` | PR #5 at `1a5b6b5…`; CI `30487475188`; Zizmor `30487475253` | Does not preserve current post-hook stage behavior. |
| First-party RSC intentionally inserts a late raw dynamic import. | `source-read` | `vite-plugin-react` `plugin.ts` and `browser.ts` at `9db4976…` | Minimal analogue execution still queued. |
| The naïve Option B prototype passes the first mechanism and emits a false prune on repeat transform. | `target-executed` | PR #9 run `30587631101`, macOS job `91022769607` | One platform job completed before repair; other jobs were still queued. |
| The retained-overlay repair now defines add, unchanged-retain, and removal transitions. | `target-test-prepared` | PR #9 at `bf18a77…` | Exact execution pending. |

## Historical precedent

### Plugin-added imports must participate in analysis

- Source: https://github.com/vitejs/vite/pull/23029
- Principle supported: imports introduced by plugins must enter Vite's analysis behavior.
- Important difference: the precedent does not decide which late side effects should rewrite source and which should update graph state only.

### Plugin and hook ordering are distinct contracts

- Source: https://vite.dev/guide/api-plugin.html#plugin-ordering
- Retrieved: `2026-07-31`
- Principle supported: plugin order and hook order are independently meaningful.
- Important difference: the documentation does not define a final graph-commit phase.

### Sequential hooks expose intermediate results

- Source: https://rolldown.rs/apis/plugin-api
- Retrieved: `2026-07-31`
- Principle supported: later sequential hooks receive earlier results.
- Important difference: Vite owns module-graph and HMR state in addition to source transformation.

### First-party raw-import escape

- Source: https://github.com/vitejs/vite-plugin-react/blob/9db4976a9f30e89205d327b9e951a0a1d4912fe5/packages/plugin-rsc/src/plugin.ts
- Caller: https://github.com/vitejs/vite-plugin-react/blob/9db4976a9f30e89205d327b9e951a0a1d4912fe5/packages/plugin-rsc/src/browser.ts
- Principle supported: a post transform intentionally inserts a dynamic import after normal analysis to avoid `?import`.
- Important difference: the pattern still needs final graph semantics appropriate to its runtime behavior.

## Decision criteria

| Priority | Criterion | Discriminating evidence |
| --- | --- | --- |
| 1 | Final graph and HMR truth | Late static import and accept-boundary controls. |
| 2 | First-party raw-import compatibility | Dynamic non-JavaScript late import remains free of `?import`. |
| 3 | Current post-hook stage | Baseline and Candidate A visibility carriers. |
| 4 | Atomic graph ownership | No transient prune for unchanged state; one prune for removal. |
| 5 | Complete HMR semantics | accepted deps, self accept, partial accept, bindings, and normalization. |
| 6 | Recovery | Parse, resolution, invalidation, and stale-transform controls. |
| 7 | Compatibility breadth | aliases, virtual IDs, optimized deps, CSS, SSR, workers, and query-bearing imports. |
| 8 | Cost and maps | second-pass cost and source-map accuracy. |

## Alternatives instantiated

### Baseline — current ordering

- Carrier: `teamleaderleo/vite#6`
- Head: `7229602a44df963d0395bc9c0160ea062a014d5c`
- Preserves current post-hook input and raw-import behavior.
- Loses the reproduced final graph/HMR case.

### Option A — move full import analysis to the post bucket

- Candidate: `teamleaderleo/vite#5`
- Head: `1a5b6b5327efa43fc4a33ed5ad51553b6d9c37ba`
- Comparison carrier: `teamleaderleo/vite#7` at `e169baf…`
- Wins the smallest one-pass implementation and full-gate evidence.
- Loses first-party raw-import compatibility and changes post-hook input.
- Retained as a negative comparison.

### Desired combined contract

- Carrier: `teamleaderleo/vite#8`
- Head: `5d9a0ca545cd7763a7d8bfffd3a646ecb6c4a076`
- Requires raw-import preservation, late graph dependency, late accepted dependency, hot-context injection, and HMR update together.
- Expected to fail on both baseline and Candidate A for different reasons.

### Option B — normal analysis plus bounded late reconciliation

- Prototype: `teamleaderleo/vite#9`
- Current head: `bf18a77bc97d63dc01aa7b3fab5ad10340f8e89a`
- Changed files:
  - `packages/vite/src/node/plugins/lateImportAnalysis.ts`
  - `packages/vite/src/node/__tests__/server/post-transform-late-reconciliation-contract.spec.js`
- The prototype remains test-config-only and is not globally wired.
- Current mechanism:
  - normal analysis keeps source-rewrite ownership;
  - a preserve plugin carries prior late file imports through ordinary analysis;
  - a final post plugin parses final source, reconciles imports and HMR state, normalizes accepted URLs, injects hot context, and replaces retained overlay state;
  - dynamic imports requiring explicit import treatment are left raw.

### Option C — explicit transform-scoped graph transaction

- Paper design.
- Would stage ordinary and final graph changes and commit/prune once.
- Better single-commit semantics, but broader plugin-container and module-graph change.
- Becomes preferred if the retained overlay requires several hidden hooks or cannot protect concurrent/stale transforms.

## Comparative results

| Criterion | Baseline | Option A | Option B current | Option C | Current result |
| --- | --- | --- | --- | --- | --- |
| Final graph truth | Fails | Passes | One-shot passed before repeat control; repaired run pending | Target requirement | A proven; B active. |
| Raw late import | Preserves | Conflicts | Preserves in mechanism test | Must define | B leads. |
| Post-hook source input | Preserves | Changes | Preserves | Can preserve | B leads. |
| Unchanged repeat transform | Existing graph never had edge | Consistent one-pass | First prototype emitted false prune; overlay repair queued | Should commit once | B must prove repair. |
| Actual removal | No late state | One-pass final | Explicit one-prune control queued | Should commit once | Pending. |
| Implementation breadth | None | Narrow | Medium, test-only | Broad | B before C. |

## Exact execution and receipts

| Repository/head | Workflow or job | Result | Evidence class |
| --- | --- | --- | --- |
| `teamleaderleo/vite@1a5b6b5…` | CI `30487475188` | Passed named Node/platform matrix | `full-gate` |
| Same | Zizmor `30487475253` | Passed | `target-executed` |
| `teamleaderleo/vite@7132850…` | CI `30587631101`, macOS job `91022769607` | Build passed; unit failed only at false-prune negative control | `target-executed` |
| `teamleaderleo/vite@bf18a77…` | New PR #9 workflows | pending | pending |
| PRs #6, #7, #8 | exact-head CI/Zizmor | queued at latest observation | pending |

The macOS failure was the intended discriminating control: received one `prune` payload where the unchanged repeat transform required none.

## Edge cases covered

| Case | Evidence | Result |
| --- | --- | --- |
| Late static import | PR #5 and PR #9 desired contract | A passes; B repaired run pending. |
| Late accepted dependency | Same | A passes; B repaired run pending. |
| Hot-context injection | Same | A passes; B first mechanism reached repeat control. |
| HMR update | Same | B first mechanism reached repeat control after update assertion. |
| First-party-style raw dynamic import | PRs #6/#7/#9 | B first mechanism preserved it; comparison runs queued. |
| Unchanged repeat | PR #9 old head | Naïve B failed with false prune. |
| Retained overlay repair | PR #9 current head | exact execution pending. |
| Late removal | PR #9 current test | exactly-one-prune control prepared. |
| Cross-platform graph lookup | PR #2 and Candidate A matrix | Passed Linux, macOS, and Windows for A. |

## Edge cases deferred

| Case | Why deferred | Reopening or next record |
| --- | --- | --- |
| Post-hook graph visibility for prior accepted deps | Overlay currently preserves file imports before normal analysis but restores accepted state only at final reconciliation. | Add control before global wiring. |
| Imported bindings and `acceptExports` | Prototype preserves ordinary values but does not derive late additions. | Extend Option B or move to transaction design. |
| Bare, aliased, virtual, optimized, CSS, query-bearing imports | Current desired contract uses relative JS plus raw non-JS dynamic import. | Add compatibility matrix after base lifecycle survives. |
| SSR and workers | Different consumers and helper rules. | Targeted environment controls. |
| Parse and resolution rollback | Current final pass reports parse errors but stale graph publication is unproved. | Add failure transaction controls. |
| Concurrent or superseded transforms | WeakMap overlay has no generation fence. | Add stale-request control; may force Option C. |
| Cleanup and retained-state lifetime | WeakMap scopes by environment, but module removal/close behavior is unproved. | Add invalidation and teardown controls. |
| Source maps | Late HMR string rewrite and helper prepend generate maps through `MagicString`. | Assert mapping before promotion. |
| Cost | Final pass adds a lexer parse. | Measure after correctness model stabilizes. |

## Independent criticism

| Criticism | Concrete response | Effect |
| --- | --- | --- |
| Candidate A changes user post-hook input. | Created baseline/candidate visibility carriers #6/#7. | Reopened the lane. |
| Candidate A conflicts with first-party RSC raw imports. | Added raw-import controls and selected Option B. | A held as negative comparison. |
| A two-pass union may falsely prune unchanged late state. | Added repeat-transform negative control. | Old Option B head failed exactly there. |
| Retaining prior state could make removed imports sticky. | Added removal transition requiring one real prune and absent graph relationships. | Current head queued. |

## Current disposition and routing

- Finding state: `comparative-evaluation-active`
- Review disposition: `REPAIR and EXECUTE Option B; HOLD Candidate A promotion`
- Review Queue: no user design question; reviewers should attack concrete alternatives
- Delivery lane: `not-entered`
- Preferred family: Option B
- Current preferred mechanism: retained late-state overlay, subject to exact execution and state-visibility review
- Exact next transition: inspect current PR #9 workflows, repair concrete failures, then add accepted-state visibility, error rollback, and generation controls
- Clearing condition: one exact-head implementation preserves final graph truth, raw-import compatibility, repeat/remove correctness, and defined post-hook graph visibility
- Non-delegable human decision: `none`

## Changes to the conclusion

| Date | Record | Change |
| --- | --- | --- |
| 2026-07-29 | Vite PR #2 | Reproduced final-source graph mismatch. |
| 2026-07-29 | Vite PR #5 | Implemented and fully gated Candidate A. |
| 2026-07-31 | First-party RSC source review | Found explicit reliance on late raw-import insertion; A ceased to be preferred. |
| 2026-07-31 | PRs #6–#8 | Instantiated baseline, A, and combined desired contract. |
| 2026-07-31 | PR #9 at `7132850…` | One-shot mechanism passed earlier assertions; repeat transform exposed false prune. |
| 2026-07-31 | PR #9 at `bf18a77…` | Added retained overlay plus unchanged-retain and real-removal controls. |

## Durable supporting records

- `findings/F25-vite-post-transform-import-analysis/evidence/20260731-workstream-b-transform-order-comparison.md`
- `findings/F25-vite-post-transform-import-analysis/alternatives/B-late-reconciliation.md`

## References

- https://github.com/teamleaderleo/fieldwork/issues/25
- https://github.com/teamleaderleo/vite/pull/2
- https://github.com/teamleaderleo/vite/pull/5
- https://github.com/teamleaderleo/vite/pull/6
- https://github.com/teamleaderleo/vite/pull/7
- https://github.com/teamleaderleo/vite/pull/8
- https://github.com/teamleaderleo/vite/pull/9
- https://github.com/vitejs/vite/pull/23029
- https://github.com/vitejs/vite/blob/843a47da6b93dbd3ce28c4ffae33a8ef338c6f05/packages/vite/src/node/plugins/index.ts
- https://github.com/vitejs/vite/blob/843a47da6b93dbd3ce28c4ffae33a8ef338c6f05/packages/vite/src/node/plugins/importAnalysis.ts
- https://vite.dev/guide/api-plugin.html#plugin-ordering
- https://rolldown.rs/apis/plugin-api
- https://github.com/vitejs/vite-plugin-react/blob/9db4976a9f30e89205d327b9e951a0a1d4912fe5/packages/plugin-rsc/src/plugin.ts
- https://github.com/vitejs/vite-plugin-react/blob/9db4976a9f30e89205d327b9e951a0a1d4912fe5/packages/plugin-rsc/src/browser.ts
- CI `30487475188`
- Zizmor `30487475253`
- PR #9 CI `30587631101`, job `91022769607`
