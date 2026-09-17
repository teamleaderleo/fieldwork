# F235-jotai-json-cache: isolate parsed JSON by key and choose its retention contract

Finding state: `design-decision-ready`

Workstream: `D`  
Canonical Fieldwork issue: `#235`  
Canonical finding path: `findings/F235-jotai-json-cache/finding.md`  
Canonical implementation: `teamleaderleo/fieldwork#252` patch carrier; direct owned Jotai source branch absent  
Exact implementation head: `d9dd61c4a0d1f9073c300519990e6ba9ec2855d9`  
Exact target source revision: `56a9cc51de8a5dd762b95a145820f12589cc47c9`  
Strongest evidence class: `target-executed`  
Reviewed input generation: issue #235 body before decision sync plus PR #252 head `d9dd61c4a0d1f9073c300519990e6ba9ec2855d9`  
Current review disposition: `HOLD production promotion; choose retention policy`  
Desk routing: `Review Queue #213 and Delivery Desk #160 D3`  
Upstream contact authorized: `no`

## In simple words

Jotai converts stored JSON strings into JavaScript values. It remembers parsed values so reading unchanged storage can return the same object again. The released adapter keeps one remembered value for the whole adapter, so two different keys containing identical JSON can receive the same object. Mutating the object from key A can then change the object already handed out for key B without any key-B write or notification.

The candidate gives each key its own remembered value. It also clears stale identity when removal settles, storage disappears outside the adapter, or malformed JSON is observed. Exact-source tests pass on Node 22, 24, and 26.

One design choice remains: how long should values for old keys stay retained? Research should pause until that contract is selected.

## Why we care

Different storage keys ordinarily represent different values and update histories. Sharing one mutable parsed object across those keys makes in-memory state depend on read order and byte-for-byte JSON equality. A caller can observe key B change after mutating key A even though storage and subscriptions report no key-B update.

The key-scoped repair removes that aliasing. Its per-key map can retain one serialized string and parsed value for every observed key, so applications with unbounded dynamic keys could retain values for the adapter lifetime.

## What happens if we leave it alone

Observed released behavior:

- equal JSON under different keys produces the same object identity;
- mutating one returned object changes the other key's previously returned object;
- no storage write or notification explains that change.

Observed candidate behavior removes cross-key aliasing and stale identity resurrection. Frequency in real applications and memory cost under dynamic key churn remain unmeasured.

## Current finding

The candidate correctly scopes parsed identity by storage key and conservatively invalidates an affected key after every terminal removal outcome because a rejection cannot prove the durable delete was absent. It also invalidates after a read observes missing or malformed storage so identical JSON restored later cannot resurrect an obsolete object.

The candidate is target-executed and design-decision-ready. Production promotion remains held until one retention policy is selected and the chosen implementation is transferred to a direct owned Jotai source branch with ordinary repository gates.

### Claim table

| Claim | Evidence class | Exact support | Limit |
| --- | --- | --- | --- |
| Released Jotai shares parsed object identity across different keys containing equal JSON. | `target-executed` | Released-package run `30548784323` on Node 22/24/26 and retained experiment result. | Does not measure how often applications share adapters or mutate returned values. |
| The candidate isolates identity by key while preserving same-key identity. | `target-executed` | Exact-source run `30579399493`; native key-isolation tests. | Patch carrier over pinned source, not a direct source branch. |
| Removal invalidation must account for commit-then-reject ambiguity. | `target-executed` | Native synchronous, pending, rejection, fulfillment, and commit-then-reject controls. | Does not create a general storage transaction protocol. |
| Missing or malformed reads must invalidate the affected key's cached identity. | `target-executed` | `atomWithStorageReadInvalidation.test.ts` at head `d9dd61c4...`. | Covers synchronous read controls; broader async completion ordering remains separate. |
| Adapter-lifetime per-key retention can grow with dynamic key churn. | `source-read` | Candidate uses `Map<string, { str, value }>` and deletes entries only on named invalidation events or adapter collection. | Practical frequency and retained size are unmeasured. |

## System and ownership map

- Entry point: `createJSONStorage()` wraps a string storage backend.
- State owner: one adapter-local parsed-value cache.
- Read flow: fetch a string by key, reuse a same-key cached value when the string matches, otherwise parse and replace that key's entry.
- Write flow: serialize and delegate to the underlying storage; candidate does not change write ordering.
- Removal flow: delegate removal, preserve identity while an async removal is pending, invalidate the affected key on every terminal outcome, and preserve the initiating error.
- Recovery: a missing or malformed read deletes that key's cache and returns the supplied initial value.
- Public contract under study: stable same-key identity without cross-key aliasing.
- Test boundary: candidate regressions plus the existing `atomWithStorage.test.tsx` suite.

## Historical precedent

### Original same-key identity repair

- Source: Jotai issue #1079 and PR #1080, recorded in the retained Fieldwork report.
- Revision: implementing commit `9e336c6bd2bebf257ffca957b0af18f97444323c`.
- Principle supported: repeated reads of unchanged JSON for one key may need stable object identity during mount and subscription setup.
- Important difference: the retained regression used one key. It did not require one adapter-wide identity cache or cover equal JSON under different keys.

### Removal acknowledgement ambiguity

- Source: candidate fault-injection controls retained in PR #252.
- Revision: exact target-tested source/test generation `a2c836fcd6eba43cf03e0e8a94c9cc374dcbdb1e` and report head `d9dd61c4...`.
- Principle supported: a rejected async removal may have committed before its acknowledgement was lost, so rejection cannot prove the old cache remains authoritative.
- Important difference: the control establishes a conservative cache rule, not a durable storage transaction guarantee.

## Approaches considered

### Option A: adapter-lifetime per-key retention

Keep the current map. This preserves same-key identity across arbitrary interleaving and is simple for adapters with a bounded key set. Dynamic key churn may retain values until the adapter becomes unreachable.

### Option B: bounded eviction

Use a fixed-capacity or LRU cache. This bounds retention. Eviction intentionally breaks same-key identity after enough unrelated key activity, weakening the historical compatibility behavior.

### Option C: explicit lifecycle authority

Add disposal or key-release authority. This preserves identity while allowing deterministic cleanup. It widens the adapter contract and requires subscriber, shared-adapter, and backward-compatibility design.

### Declined: one adapter-wide cache

This is the released defect. Equal serialized bytes under unrelated keys create shared mutable identity.

### Declined: weak references as the sole policy

Garbage-collection timing cannot provide a deterministic identity contract, and primitive parsed values cannot be weakly referenced.

### Deferred: general async read-generation ordering

A late older async read can replace a newer cache entry. That behavior predates this candidate and needs a separate generation/ordering finding.

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
| Dynamic-key retention frequency and size | No representative workload measurement exists. | Measure after selecting A, B, or C when application profile warrants it. |
| Out-of-order async same-key reads | Separate pre-existing ordering problem. | New finding when a direct source design is proposed. |
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

## Complete-diff and compatibility review

- Complete changed-file fence: read-only exact-source workflow, generated candidate patch, two native candidate test files, and durable report.
- Current-base relationship: PR #252 is open and mergeable against current Fieldwork main; it is an evidence/patch carrier rather than the production source destination.
- Temporary carrier status: PRs #236 and #242 are superseded; PR #252 is canonical for the current finding.
- Compatibility surfaces examined: same-key identity, cross-key isolation, sync/async storage, reviver, removal settlement, missing/malformed reads, existing mount/subscription behavior, lint, formatting, and TypeScript.
- Known routine repair remaining: none in the bounded candidate behavior at `d9dd61c4...`.
- Decision remaining: retention policy A, B, or C.
- Production gates after selection: direct owned source branch, ordinary repository-wide tests/build, complete-diff independent review.

## Alternatives and consequences for the decision maker

| Option | What it does | Benefit | Cost or risk | Evidence needed after selection |
| --- | --- | --- | --- | --- |
| A | Keep one map entry per observed key until invalidation or adapter collection. | Strongest continuity with historical same-key identity; smallest change. | Dynamic key churn can retain values for adapter lifetime. | Direct source extraction, ordinary repository gates, bounded-key use assumption documented. |
| B | Add bounded/LRU eviction. | Explicit memory bound. | Same-key identity can disappear after unrelated key activity; needs compatibility decision and eviction tests. | Capacity policy, interleaving matrix, mount/subscription compatibility, ordinary gates. |
| C | Add explicit dispose/release authority. | Deterministic cleanup while preserving identity until release. | Wider API and ownership contract; shared adapters and subscribers need design. | API review, lifecycle tests, backward compatibility, ordinary gates. |

Recommendation: choose **A** for the narrow repair when adapters are expected to serve bounded key sets, document that contract, and open a separate lifecycle proposal only when measured dynamic-key use justifies C. Choose B only when a hard memory bound outranks identity continuity.

## Current disposition and desk routing

- Finding state: `design-decision-ready`
- Review disposition: `HOLD production promotion; evidence supports policy selection`
- Review Queue entry: `#213`
- Delivery lane: `D3`
- Exact next transition: select retention option A, B, or C.
- Clearing condition: one explicit policy choice and its compatibility consequence recorded.
- Required subgates after choice: direct owned Jotai source branch, ordinary format/type/lint/spec/build gates, complete-diff independent review.
- User decision requested: choose A, B, or C; recommendation is A under a bounded-key adapter contract.

## Changes to the canonical conclusion

| Date | Pull request or commit | Change in conclusion |
| --- | --- | --- |
| 2026-07-30 | released-package evidence #228 | Confirmed adapter-wide cross-key aliasing. |
| 2026-07-30 | early PRs #236/#242 | Prepared key-scoped cache and repaired removal settlement; carriers superseded. |
| 2026-07-30 | PR #252 head `8cd0109f...` | Earlier queue entry recorded R1 before later read-invalidation work. |
| 2026-07-30 | PR #252 head `d9dd61c4...` | Added missing/malformed read invalidation, exact-source execution, and explicit A/B/C retention decision; prior exact-head review expired. |

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
