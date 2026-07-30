# Option B — bounded late import and HMR reconciliation

Date: `2026-07-31`  
Finding: `findings/F25-vite-post-transform-import-analysis/finding.md`  
State: `prototype-executing`  
Upstream contact authorized: `no`

## In simple words

Vite's existing import analysis should keep doing the things user post transforms already expect: rewrite ordinary imports, inject established helpers, and populate the graph before post hooks run.

After those post hooks finish, a smaller final pass should compare the final source with the graph and reconcile only the state added late. It should not rerun every rewrite. This is intended to preserve the first-party React RSC raw-import escape while fixing missing late static imports and HMR boundaries.

## Concrete artifacts

### Desired contract

Owned carrier: `teamleaderleo/vite#8`  
Head: `5d9a0ca545cd7763a7d8bfffd3a646ecb6c4a076`

The test requires all of the following together:

1. a dynamic non-JavaScript import deliberately introduced by a post transform stays raw and does not gain `?import`;
2. a static JavaScript import introduced by the same transform becomes a module-graph dependency;
3. a late `import.meta.hot.accept()` becomes an accepted HMR dependency;
4. hot context is injected;
5. a dependency update produces an HMR update rather than a full reload.

The current baseline should fail graph/HMR assertions. Candidate A should fail the raw-import assertion.

Workflow receipts:

- CI `30587056193` — queued at the last recorded observation;
- Zizmor `30587056061` — queued at the last recorded observation.

### First source prototype

Owned prototype: `teamleaderleo/vite#9`  
Current head: `71328504581b6af0b4084bddee8f40efc9e0dc75`

Changed files:

- `packages/vite/src/node/plugins/lateImportAnalysis.ts`
- `packages/vite/src/node/__tests__/server/post-transform-late-reconciliation-contract.spec.js`

The prototype is activated only in the test configuration. It is not wired into the global internal plugin list.

Current source behavior:

- keeps normal import analysis unchanged;
- runs an experimental final post hook;
- parses final source with `es-module-lexer`;
- resolves trackable final imports and unions them into graph state;
- skips dynamic imports requiring explicit import handling, preserving the first-party raw-import pattern;
- lexes late HMR accept dependencies;
- rewrites accepted HMR dependency strings to normalized HMR URLs;
- injects hot context when late source introduced HMR;
- updates module graph and dispatches returned prunes.

Workflow receipts:

- CI `30587631101` — queued at the last recorded observation;
- Zizmor `30587630916` — queued at the last recorded observation.

## Why the prototype is separate from a candidate

A one-shot passing test would establish only that late graph state can be added without rewriting the raw dynamic import in that scenario. General integration has harder ownership requirements.

The existing normal import-analysis pass updates and prunes graph state before the final pass runs. On a later transform of the same module, it can temporarily remove a previously late dependency and emit a prune before the prototype re-adds it. The latest test explicitly rejects that transient prune.

This is a design defect in a naïve two-pass implementation, not a reason to return the decision to the user.

## Required repaired ownership model

A viable version must preserve previous final-source state through the normal pass and commit changes once the final source is known.

Candidate mechanisms to compare:

### B1 — retained late-state overlay

Keep per-module late import, accepted-dependency, self-acceptance, and static-import state. Before ordinary analysis commits its graph update, preserve the previous overlay. After post transforms, atomically replace the overlay and emit prunes only for dependencies absent from the new final state.

Advantages:

- smallest conceptual change to current analysis;
- current post-hook source and graph timing can remain available;
- actual removals can be distinguished from transient normal-pass removal.

Risks:

- ordinary analysis needs a narrow integration point;
- imported bindings and partial accept state need precise overlay semantics;
- cache invalidation must clear stale overlays.

### B2 — transform-scoped graph transaction

Let ordinary and late analysis stage graph updates in one transform transaction. User post hooks can read an explicitly defined intermediate or previous committed graph; final commit and prune occur once after all hooks.

Advantages:

- single commit and prune point;
- explicit ownership and easier negative controls;
- extensible to CSS or other final-state analyzers.

Risks:

- wider plugin-container and module-graph change;
- current post hooks that expect the freshly analyzed graph need a compatibility model;
- error rollback and concurrent requests become central.

### B3 — preserve imports early, restore HMR state before post hooks, reconcile finally

Use retained late state to keep late imports present during ordinary analysis, restore previous accepted HMR state before user post hooks, then replace it after final source analysis.

Advantages:

- may avoid a full transaction layer;
- preserves current post-hook graph observations.

Risks:

- several ordered internal hooks share one invariant;
- easy to create transient inconsistencies or duplicate side effects;
- more difficult to explain and test than B1 or B2.

## Discriminating controls

The next repair must include:

1. first transform adds a late static dependency and accepted HMR dependency;
2. second transform retains the same late state and emits no prune;
3. third transform removes the late dependency and emits one real prune;
4. ordinary imports remain unchanged across the overlay lifecycle;
5. raw dynamic non-JavaScript imports remain unrevised;
6. late accepted dependency strings are normalized for the client;
7. late self-accept and partial-accept behavior is correct;
8. parse or resolution failure preserves the primary error and leaves the prior committed graph coherent;
9. concurrent or superseded transforms cannot publish stale overlays;
10. invalidation, close, and environment teardown clear retained state;
11. source maps include only actual late source mutations;
12. focused parse-count or timing evidence measures the second lexer pass.

## Current criticism

The prototype currently unions final parsed nodes with graph state already committed by ordinary analysis. It does not yet:

- prevent transient pruning on repeat transforms;
- own late-state removal atomically;
- record imported bindings for late imports;
- handle `acceptExports` or partial-accept additions;
- prove virtual, optimized, aliased, CSS, SSR, worker, or query-bearing behavior;
- prove parse and resolution error rollback;
- guard against stale concurrent publication;
- demonstrate source-map accuracy or acceptable cost.

The new repeat-transform negative control is expected to expose the transient-prune problem if compilation and the first mechanism control succeed.

## Provisional selection

Option B remains the preferred family because it is the only current direction aimed at preserving both final graph truth and the first-party raw-import contract.

Within Option B, B1 is the narrowest next repair to instantiate. B2 becomes preferred if B1 requires several hidden integration hooks or cannot provide atomic pruning and stale-request safety. B3 is retained as a mechanism sketch but currently ranks behind B1 and B2 due to distributed ownership.

## Reopening trigger

Reconsider Candidate A only if primary project evidence explicitly removes or replaces the first-party late raw-import contract, or if every compatibility-preserving implementation proves materially more unsafe or complex under target execution.

## Exact next transition

Inspect PR #9 execution. Repair compile or mechanism failures first. Then instantiate B1 with retained per-module late state and add retain/remove/error controls before any global plugin wiring or delivery routing.