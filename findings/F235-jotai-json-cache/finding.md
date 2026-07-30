# F235-jotai-json-cache: isolate parsed JSON by key and retain cache for adapter lifetime

Finding state: `delivery-gate-ready`

Workstream: `D`  
Canonical Fieldwork issue: `#235`  
Canonical finding path: `findings/F235-jotai-json-cache/finding.md`  
Canonical implementation: `teamleaderleo/fieldwork#252` patch carrier; direct owned Jotai source branch absent  
Exact implementation head: `d9dd61c4a0d1f9073c300519990e6ba9ec2855d9`  
Exact target source revision: `56a9cc51de8a5dd762b95a145820f12589cc47c9`  
Strongest evidence class: `target-executed`  
Reviewed input generation: issue #235 body before retention selection, PR #252 head `d9dd61c4a0d1f9073c300519990e6ba9ec2855d9`, and review `reviews/20260731-workstream-d-retention-selection.md`  
Current review disposition: `ACCEPT option A; EXECUTE direct source transfer and ordinary repository gates`  
Desk routing: `Delivery Desk #160 D2`  
Upstream contact authorized: `no`

## In simple words

Jotai converts stored JSON strings into JavaScript values. It remembers parsed values so reading unchanged storage can return the same object again. The released adapter keeps one remembered value for the whole adapter, so two different keys containing identical JSON can receive the same mutable object.

The candidate gives each key its own remembered value and clears stale identity after removal, missing storage, or malformed JSON. Adapter-lifetime per-key retention is selected because it preserves the historical same-key identity behavior without adding a public lifecycle API or making identity depend on unrelated-key eviction.

The next transition is a clean direct owned source branch, ordinary Jotai gates, and independent complete-diff review.

## Why we care

Different storage keys represent different values and update histories. Sharing one mutable parsed object across those keys makes in-memory state depend on read order and byte-for-byte JSON equality. A caller can observe key B change after mutating key A even though storage and subscriptions report no key-B update.

The selected repair removes that aliasing while preserving unchanged same-key identity across unrelated-key activity. Its per-key map can retain one serialized string and parsed value for every observed key until invalidation or adapter collection. Dynamic-key retention remains a documented reopening condition rather than a reason to weaken a confirmed compatibility property without usage evidence.

## What happens if we leave it alone

Observed released behavior:

- equal JSON under different keys produces the same object identity;
- mutating one returned object changes the other key's previously returned object;
- no storage write or notification explains that change.

Observed candidate behavior removes cross-key aliasing and stale identity resurrection. Frequency in applications and memory cost under dynamic key churn remain unmeasured.

## Governing goals and invariant

Governing invariant: **unchanged serialized data for one key preserves parsed identity across unrelated-key activity, while different keys never share mutable parsed identity merely because their serialized bytes match.**

| Goal or contract | Primary source | Consequence for the design |
| --- | --- | --- |
| Preserve same-key identity during mount and subscription setup. | Jotai commit `9e336c6bd2bebf257ffca957b0af18f97444323c` and its regression. | Unrelated-key activity must not evict or replace a valid same-key cache entry. |
| Keep fixes focused and covered by failing tests. | Jotai `CONTRIBUTING.md` at source revision `56a9cc51...`. | The narrow repair should avoid a new public lifecycle contract. |
| Keep different storage keys independent. | Released cross-key alias reproduction and candidate tests. | Cache ownership must be per key. |
| Preserve initiating errors and deterministic invalidation. | Removal, missing-read, malformed-read, and commit-then-reject controls. | Cleanup must not replace errors or leave obsolete identity authoritative. |

## Current finding

The candidate correctly scopes parsed identity by storage key and conservatively invalidates an affected key after every terminal removal outcome because a rejection cannot prove the durable delete was absent. It also invalidates after a read observes missing or malformed storage so identical JSON restored later cannot resurrect an obsolete object.

Adapter-lifetime per-key retention is the selected policy. It is the smallest compatible repair: it keeps the historical identity behavior, introduces no new public authority, and avoids an arbitrary capacity rule. Production promotion remains held for direct source transfer, ordinary repository gates, and independent complete-diff review.

### Claim table

| Claim | Evidence class | Exact support | Limit |
| --- | --- | --- | --- |
| Released Jotai shares parsed object identity across different keys containing equal JSON. | `target-executed` | Released-package run `30548784323` on Node 22/24/26 and retained experiment result. | Does not measure how often applications share adapters or mutate returned values. |
| The candidate isolates identity by key while preserving same-key identity. | `target-executed` | Exact-source run `30579399493`; native key-isolation tests. | Patch carrier over pinned source, not a direct source branch. |
| Removal invalidation must account for commit-then-reject ambiguity. | `target-executed` | Native synchronous, pending, rejection, fulfillment, and commit-then-reject controls. | Does not create a general storage transaction protocol. |
| Missing or malformed reads must invalidate the affected key's cached identity. | `target-executed` | `atomWithStorageReadInvalidation.test.ts` at head `d9dd61c4...`. | Covers synchronous read controls; broader async completion ordering remains separate. |
| Adapter-lifetime retention best preserves the established identity contract in the narrow repair. | `source-read` plus comparative review | Historical identity repair, candidate matrix, and `reviews/20260731-workstream-d-retention-selection.md`. | Practical dynamic-key retention remains unmeasured. |

## System and ownership map

- Entry point: `createJSONStorage()` wraps a string storage backend.
- State owner: one adapter-local map from storage key to serialized string and parsed value.
- Read flow: fetch a string by key, reuse a same-key cached value when the string matches, otherwise parse and replace that key's entry.
- Write flow: serialize and delegate to the underlying storage; candidate does not change write ordering.
- Removal flow: delegate removal, preserve identity while an async removal is pending, invalidate the affected key on every terminal outcome, and preserve the initiating error.
- Recovery: a missing or malformed read deletes that key's cache and returns the supplied initial value.
- Public contract: stable same-key identity without cross-key aliasing.
- Test boundary: candidate regressions plus the existing `atomWithStorage.test.tsx` suite.

## Historical precedent

### Original same-key identity repair

- Source: Jotai issue #1079 and PR #1080, recorded in the retained Fieldwork report.
- Revision: implementing commit `9e336c6bd2bebf257ffca957b0af18f97444323c`.
- Principle supported: repeated reads of unchanged JSON for one key need stable object identity during mount and subscription setup.
- Important difference: the retained regression used one key. It did not require one adapter-wide identity cache or cover equal JSON under different keys.

### Removal acknowledgement ambiguity

- Source: candidate fault-injection controls retained in PR #252.
- Revision: exact target-tested source/test generation `a2c836fcd6eba43cf03e0e8a94c9cc374dcbdb1e` and report head `d9dd61c4...`.
- Principle supported: a rejected async removal may have committed before its acknowledgement was lost, so rejection cannot prove the old cache remains authoritative.
- Important difference: the control establishes a conservative cache rule, not a durable storage transaction guarantee.

## Decision criteria

| Priority | Criterion | How it was measured or falsified |
| --- | --- | --- |
| 1 | Preserve established same-key identity across unrelated-key activity. | Interleaved native identity controls and historical regression. |
| 2 | Eliminate cross-key mutable aliases. | Equal-JSON and mutation-isolation tests. |
| 3 | Avoid widening the public lifecycle API for a narrow bug fix. | Complete source/API diff review. |
| 4 | Keep invalidation deterministic on observed terminal outcomes. | Removal, missing, malformed, and restoration controls. |
| 5 | Avoid trading a confirmed compatibility property for an unmeasured memory concern. | Evidence inventory and absence of representative dynamic-key measurements. |
| 6 | Preserve a clear reopening path. | Explicit churn and lifecycle triggers below. |

## Alternatives instantiated or analyzed

### Option A — adapter-lifetime per-key retention

- Artifact or branch: PR #252 candidate patch at `d9dd61c4a0d1f9073c300519990e6ba9ec2855d9`.
- Invariant implemented: per-key identity continuity until named invalidation or adapter collection.
- Expected benefit: strongest compatibility with the historical same-key behavior and the smallest source change.
- Expected cost or failure: dynamic key churn may retain values for the adapter lifetime.
- Discriminating control: identity remains stable after arbitrary unrelated-key reads.
- Rollback boundary: remove the candidate map and return to the released adapter-wide cache.

### Option B — bounded or LRU eviction

- Artifact or branch: paper-only; implementation would prove the already-known consequence that finite eviction breaks identity after enough unrelated-key activity.
- Invariant implemented: bounded retained entry count.
- Expected benefit: explicit memory bound.
- Expected cost or failure: same-key identity becomes dependent on unrelated-key access order and an arbitrary capacity.
- Discriminating control: read one key, churn beyond capacity, then read unchanged data for the first key.
- Rollback boundary: restore adapter-lifetime retention.

### Option C — explicit dispose or key-release authority

- Artifact or branch: paper-only; a useful prototype requires a separate public lifecycle contract and caller-ownership study.
- Invariant implemented: deterministic cleanup under explicit caller authority.
- Expected benefit: preserves identity until release while allowing deterministic reclamation.
- Expected cost or failure: widened API, shared-adapter ambiguity, subscriber ordering, and backward-compatibility work.
- Discriminating control: shared adapter with several atoms, subscriptions, releases, and later reuse.
- Rollback boundary: keep lifecycle authority outside the narrow repair.

### Declined — one adapter-wide cache

This is the released defect. Equal serialized bytes under unrelated keys create shared mutable identity.

### Declined — weak references as the sole policy

Garbage-collection timing cannot provide a deterministic identity contract, and primitive parsed values cannot be weakly referenced.

## Comparative results

| Criterion | Baseline | Option A | Option B | Option C | Winner |
| --- | --- | --- | --- | --- | --- |
| Cross-key isolation | fails | passes | can pass | can pass | A/B/C |
| Same-key identity across unrelated activity | accidental and cross-key unsafe | passes | fails after eviction | can pass | A/C |
| Public API compatibility | unchanged | unchanged | unchanged but behavior weakened | widened | A |
| Deterministic invalidation | incomplete | passes named controls | can pass | requires new lifecycle controls | A/B |
| Implementation and review cost | defective | smallest bounded repair | policy and capacity work | API and ownership campaign | A |
| Evidence proportionality | confirmed defect | directly executed | memory concern unmeasured | caller need unmeasured | A |

## Independent criticism

| Reviewer or evidence source | Counterexample or criticism | Response or new control | Effect on recommendation |
| --- | --- | --- | --- |
| Source review | The map can grow with every observed key. | Record bounded-key expectation and reopen on representative material churn evidence. | Keeps A selected; preserves a measurable reopening trigger. |
| Alternative analysis | Weak references might reclaim values automatically. | GC timing is nondeterministic and primitives cannot be weakly referenced. | Weak-reference policy rejected. |
| Source review | Async same-key reads may settle out of order. | Split into a separate generation-order finding; retention does not own completion ordering. | No change to A; creates a new bounded research lead. |
| API review | Explicit release could provide deterministic cleanup. | Requires a public ownership contract and shared-adapter controls beyond the narrow fix. | C deferred to a separate investigation. |

## Selected direction and losing reasons

Selected direction: **Option A — adapter-lifetime per-key retention.**

Why it wins: it alone satisfies the established identity behavior, key isolation, narrow API boundary, deterministic invalidation controls, and proportional implementation cost without inventing an eviction capacity or a public lifecycle authority.

| Losing or deferred option | Reason it lost or moved elsewhere | Reopening trigger |
| --- | --- | --- |
| B — bounded/LRU | Necessarily weakens same-key identity after unrelated-key churn; no measured hard memory bound justifies that compatibility change. | Representative evidence that retained dynamic keys cause material memory cost and identity continuity can be explicitly weakened. |
| C — explicit lifecycle | Adds public authority, shared-adapter ownership, and compatibility work beyond this repair. | Concrete caller need for deterministic release and a separate lifecycle design packet. |
| Adapter-wide cache | Confirmed cross-key mutable alias defect. | None within this finding. |

## Edge cases covered

| Edge case or control | Evidence | Result |
| --- | --- | --- |
| Same key, unchanged JSON, interleaved reads | native candidate test | Identity preserved. |
| Different keys, equal JSON | native candidate test | Distinct objects. |
| Mutating key A result | native candidate test | Key B remains unchanged. |
| Async string storage | native candidate test | Key isolation preserved. |
| Custom reviver | native candidate test | Runs once per key; same-key identity preserved. |
| Sync removal success or throw | native candidate test | Affected key invalidated; original error preserved. |
| Async removal pending | native candidate test | Identity preserved until settlement. |
| Async fulfillment or rejection | native candidate test | Affected key invalidated on terminal outcome. |
| Commit-then-reject | native candidate test | Restored identical JSON receives a fresh object. |
| Out-of-band removal | `atomWithStorageReadInvalidation.test.ts` | Restored identical JSON receives a fresh object. |
| Malformed JSON then restoration | same | Restored identical JSON receives a fresh object. |
| Unrelated key through affected-key transitions | native controls | Identity remains stable. |
| Existing mount/subscription regression | existing Jotai suite | Passed. |

## Edge cases deferred or outside scope

| Edge case | Why deferred | Owning next record or reopening trigger |
| --- | --- | --- |
| Dynamic-key retention frequency and size | No representative workload measurement exists. | Reopen retention when a real adapter profile shows material unbounded churn. |
| Out-of-order async same-key reads | Separate pre-existing completion-order problem. | New generation-order finding and discriminating deferred-read control. |
| Concurrent `setItem`/`removeItem` generations | Candidate owns parsed identity, not full storage-operation authority. | Separate storage settlement finding. |
| Browser, React Native, and unusual storage backends | Exact-source Node matrix only. | Direct source branch compatibility gate. |
| Ecosystem impact | Released mechanism confirmed; usage frequency unmeasured. | Integration-context research before wider claims. |

## Exact execution and receipts

| Repository/head | Command or workflow | Platform/environment | Result | Evidence class |
| --- | --- | --- | --- | --- |
| released `jotai@2.20.2` | Fieldwork run `30548784323` | Node 22/24/26 | cross-key alias reproduced | `target-executed` |
| exact target source `56a9cc51...` with candidate generation `a2c836fc...` | run `30579399493` | Node 22/24/26 | native candidate, existing storage suite, ESLint, Prettier, and `tsc --noEmit` passed | `target-executed` |
| Fieldwork report head `d9dd61c4...` | Fieldwork integrity `30579399390` | GitHub Actions | success | `full-gate` for Fieldwork records |
| PR #252 head `d9dd61c4...` | reruns `30579753383` and `30579753019` | GitHub Actions | success | `target-executed` and Fieldwork gate |
| finding review commit `bf9203ef...` | complete source, precedent, alternatives, and compatibility review | repository review | Option A selected | `source-read` comparative review |

## Complete-diff and compatibility review

- Complete changed-file fence: read-only exact-source workflow, generated candidate patch, two native candidate test files, durable report, and canonical comparison review.
- Current-base relationship: PR #252 is open and mergeable against Fieldwork main; it is an evidence/patch carrier rather than the production source destination.
- Temporary carrier status: PRs #236 and #242 are superseded; PR #252 is canonical for the current evidence.
- Compatibility surfaces examined: same-key identity, cross-key isolation, sync/async storage, reviver, removal settlement, missing/malformed reads, existing mount/subscription behavior, lint, formatting, and TypeScript.
- Known routine repair remaining: direct source extraction and ordinary repository validation.
- Reviewer eligibility: the retention choice received an independent workstream comparison; consequential source acceptance still requires independent review of the direct source diff.

## Current disposition and desk routing

- Finding state: `delivery-gate-ready`
- Review disposition: `ACCEPT option A; EXECUTE direct source transfer`
- Review Queue entry: none until a direct source diff is ready for independent examination.
- Delivery lane: `D2`
- Exact next transition: create a clean direct owned Jotai source branch implementing the selected per-key adapter-lifetime map and its native controls.
- Clearing condition: direct source diff passes Jotai's declared format, build, test, type, and focused compatibility gates and receives independent complete-diff review.
- Required subgates: `pnpm run fix:format` verification, `pnpm run build`, `pnpm run test`, focused storage matrix, TypeScript/lint checks, current-base review, and carrier receipt transfer.
- Autonomous work remaining: direct source materialization, execution, carrier cleanup, and review preparation.
- Non-delegable human decision: none.

## Changes to the canonical conclusion

| Date | Pull request or commit | Change in conclusion |
| --- | --- | --- |
| 2026-07-30 | released-package evidence #228 | Confirmed adapter-wide cross-key aliasing. |
| 2026-07-30 | early PRs #236/#242 | Prepared key-scoped cache and repaired removal settlement; carriers superseded. |
| 2026-07-30 | PR #252 head `8cd0109f...` | Earlier queue entry recorded R1 before later read-invalidation work. |
| 2026-07-30 | PR #252 head `d9dd61c4...` | Added missing/malformed read invalidation, exact-source execution, and explicit alternatives; prior exact-head review expired. |
| 2026-07-31 | review `reviews/20260731-workstream-d-retention-selection.md` | Applied `DECISIONS.md`, selected adapter-lifetime retention, removed the human-choice hold, and routed the result to D2. |

## References

- `https://github.com/teamleaderleo/fieldwork/issues/235`
- `https://github.com/teamleaderleo/fieldwork/pull/252`
- `https://github.com/teamleaderleo/fieldwork/actions/runs/30548784323`
- `https://github.com/teamleaderleo/fieldwork/actions/runs/30579399493`
- `https://github.com/teamleaderleo/fieldwork/actions/runs/30579399390`
- `https://github.com/teamleaderleo/fieldwork/actions/runs/30579753383`
- `https://github.com/teamleaderleo/fieldwork/actions/runs/30579753019`
- `programmes/data-durable-workflows/scouts/jotai-json-storage-key-isolation/report.md`
- `programmes/data-durable-workflows/scouts/jotai-json-storage-key-isolation/candidate.patch`
- `programmes/data-durable-workflows/scouts/jotai-json-storage-key-isolation/atomWithStorageKeyIsolation.test.ts`
- `programmes/data-durable-workflows/scouts/jotai-json-storage-key-isolation/atomWithStorageReadInvalidation.test.ts`
- `findings/F235-jotai-json-cache/reviews/20260731-workstream-d-retention-selection.md`
