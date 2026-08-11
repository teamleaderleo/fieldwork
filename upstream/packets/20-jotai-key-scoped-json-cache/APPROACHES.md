# Approaches — unit 20 Jotai key-scoped JSON cache

## In simple words

The selected direction is one adapter-lifetime cache entry per storage key. It preserves the historical same-key identity behavior and removes the confirmed cross-key mutable alias without changing the public API. Finite eviction and explicit release authority remain viable designs for different priorities, yet each widens or weakens the narrow fix. Async completion generations belong to unit 21 and should stack on this base.

## Decision criteria

1. Different storage keys never share mutable parsed identity solely because their bytes match.
2. Unchanged same-key reads preserve identity across unrelated-key activity.
3. Public storage interfaces and JSON formats remain unchanged.
4. Missing, malformed, and removal outcomes have explicit cache behavior.
5. The source diff stays focused and reviewable.
6. Retention and asynchronous ordering limits remain visible.

## Selected approach

### Adapter-lifetime per-key map

- Design: `Map<string, { str, value }>` owned by each `createJSONStorage()` adapter.
- Owning boundary: JSON parsing and identity memoization inside `createJSONStorage()`.
- Evidence: target-executed candidate at Fieldwork PR #252 head `d9dd61c4...`; retention-selection review at `fbfdeb...`.
- Advantages: removes cross-key aliases, preserves same-key identity, keeps API and storage format unchanged, isolates invalidation by key.
- Costs and risks: retained entry count follows observed key count; stale async completion publication needs unit 21.
- Remaining controls: direct source materialization, ordinary target gates, unit 21 sequencing, independent complete-diff review.

## Viable alternatives

### Bounded or LRU cache

- Design: cap the number of remembered keys and evict older entries.
- Why it remains plausible: creates an explicit retained-memory bound.
- What it would improve: dynamic-key cache growth.
- What it would widen or complicate: identity continuity becomes dependent on unrelated-key access order and an arbitrary capacity.
- Exact discriminator: read key A, churn beyond capacity through other keys, then read unchanged A and test identity.
- Reopening trigger: representative workloads demonstrate materially large adapter key sets and identity continuity ranks below a hard bound.

### Explicit key release or adapter disposal

- Design: expose deterministic caller authority to release one key or the whole cache.
- Why it remains plausible: preserves identity until deliberate release and permits deterministic reclamation.
- What it would improve: lifecycle clarity for shared long-lived adapters.
- What it would widen or complicate: public API, shared-adapter ownership, subscription lifetime, backward compatibility, and caller misuse.
- Exact discriminator: realistic shared-adapter scenarios with multiple atoms, subscriptions, release, reuse, and failures.
- Reopening trigger: a concrete caller need for deterministic release authority.

## Executed losing approaches

### Adapter-wide single-entry cache

- Exact revision: released `jotai@2.20.2`; source `56a9cc51...`.
- What ran: released-package workflow `30548784323` on Node 22/24/26.
- Result: equal JSON under two different keys returned one object; mutation crossed the key boundary.
- Why it lost: key independence fails.
- Useful evidence retained: same-key reuse and separate-adapter/different-JSON negative controls.

### Early key-scoped patch with immediate removal invalidation

- Exact branch/PR: Fieldwork PR #236, closed unmerged.
- What ran: workflow `30553976771` stopped at corrupt patch syntax before target setup.
- Result: no target evidence transferred.
- Why it lost: malformed patch and invalidation-before-settlement semantics.
- Useful evidence retained: the need to distinguish removal initiation from settlement.

### Success-only post-settlement invalidation

- Exact branch/PR: Fieldwork PR #242 head `3c573a6...`, closed unmerged.
- What ran: local patch/type preparation only; no transferable target matrix.
- Result: improved pending-removal behavior, while rejection/commit ambiguity remained contested.
- Why it lost: superseded by current-main restack and conservative terminal-outcome controls in PR #252.
- Useful evidence retained: pending-removal identity and affected-key-only invalidation cases.

## Rejected easy answers

### Remove memoization

- Temptation: parsing every read eliminates shared cache state.
- Why incomplete: breaks the historical same-key identity behavior introduced for mount/subscription consistency.
- Source fact: Jotai issue #1079 and PR #1080 deliberately added unchanged-string identity reuse.

### Cache only the most recently read key

- Temptation: pair the remembered value with a key while retaining one entry.
- Why incomplete: an unrelated-key read evicts same-key identity and violates the interleaved same-key control.
- Negative control: `preserves same-key identity across interleaved reads`.

### Weak references

- Temptation: allow garbage collection to bound retention automatically.
- Why incomplete: GC timing gives no deterministic identity contract and parsed primitives cannot be weakly referenced.

### Treat unit 20 as complete without generation fencing

- Temptation: focused tests are green and the cross-key defect is repaired.
- Why incomplete: a late pre-removal async read can repopulate cache authority after invalidation.
- Negative control: independent review `4823648945` and the 2026-08-01 model.

## Prior upstream approaches

| Link | Approach | Status | Relationship to this unit |
| --- | --- | --- | --- |
| Jotai issue #1079 | describe pre-mount storage inconsistency | closed | establishes same-key identity requirement |
| Jotai PR #1080 / `9e336c6...` | adapter-wide last-string/value memoization | merged | direct prior art; this unit corrects its multi-key boundary |
| Jotai issue #1815 | propagate RESET/removal through subscriptions | closed | related storage lifecycle, distinct cache-identity question |

## Deferred adjacent work

- Async read/removal publication generations — unit 21.
- Read completion versus later `setItem` — separate operation-authority investigation.
- Representative dynamic-key retention measurement — reopen only with a real workload.
- Public lifecycle API — separate design proposal.

## Decision history

| Date | Exact inputs | Decision | Reason | Reopening trigger |
| --- | --- | --- | --- | --- |
| 2026-07-30 | release `2.20.2`, run `30548784323` | retain finding; preserve memoization | released alias reproduced and historical identity intent confirmed | equivalent upstream correction |
| 2026-07-30 | PRs #236/#242 | supersede early carriers | patch/setup failures and removal-settlement gaps | none; evidence incorporated in #252 |
| 2026-07-30 | PR #252 `d9dd61c4...`, runs `30579399493`/`30579753383` | accept key-scoped mechanism | focused target matrix passed | direct-source incompatibility |
| 2026-07-31 | selection `fbfdeb...` | choose adapter-lifetime retention | strongest compatibility with established same-key identity | measured dynamic-key pressure or release need |
| 2026-08-01 | issue #282 / PR #317 plus fresh model | hold standalone upstream preparation pending sequencing | stale async publication repair belongs to unit 21 | one clean combined or stacked direct-source head |
