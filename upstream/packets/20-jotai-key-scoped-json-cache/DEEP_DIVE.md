# Deep dive — unit 20 Jotai key-scoped JSON cache

## In simple words

`createJSONStorage()` converts a string storage backend into Jotai's value storage interface. It memoizes parsed JSON so unchanged reads can return the same value identity. At exact source `56a9cc51...`, that memory is one adapter-wide pair. Storage key identity is absent from the cache key, so equal bytes under unrelated keys share one parsed object.

The unit 20 candidate makes the cache key-aware. The selected retention contract keeps entries for the adapter lifetime, with deletion after named invalidation events. This preserves the 2022 same-key identity behavior while removing the confirmed cross-key mutable alias.

A distinct ordering defect appears when asynchronous reads finish after a newer removal or read outcome. Unit 21 owns the generation fence. Unit 20 should remain the source base and avoid claiming complete asynchronous publication ordering on its own.

## Governing invariant

> Unchanged serialized data for one storage key preserves parsed identity across unrelated-key activity, while different keys never share mutable parsed identity merely because their serialized bytes match.

## Current behavior

- entrypoint: `createJSONStorage<Value>()`
- state owner: adapter closure
- released state: `lastStr` and `lastValue`, shared by every key
- caller-visible result: parsed value, initial value on missing or malformed JSON
- side effects: reads underlying string storage; candidate updates or deletes adapter-local cache entries
- cleanup owner: adapter lifetime plus key-specific invalidation
- persistence boundary: underlying storage owns bytes; the adapter owns parsed in-memory identity
- ordering boundary: synchronous reads are immediate; asynchronous reads publish cache state when their promise completes

## Source map

| Area | Exact path and symbol | Responsibility | Relevant tests |
| --- | --- | --- | --- |
| value adapter | [`src/vanilla/utils/atomWithStorage.ts#createJSONStorage`](https://github.com/pmndrs/jotai/blob/56a9cc51de8a5dd762b95a145820f12589cc47c9/src/vanilla/utils/atomWithStorage.ts) | parse, memoize, delegate writes/removals, build subscription adapter | existing `atomWithStorage.test.tsx` |
| unit 20 source candidate | [`candidate.patch`](https://github.com/teamleaderleo/fieldwork/blob/d9dd61c4a0d1f9073c300519990e6ba9ec2855d9/programmes/data-durable-workflows/scouts/jotai-json-storage-key-isolation/candidate.patch) | per-key map and affected-key invalidation | two retained native regression files |
| key isolation tests | [`atomWithStorageKeyIsolation.test.ts`](https://github.com/teamleaderleo/fieldwork/blob/d9dd61c4a0d1f9073c300519990e6ba9ec2855d9/programmes/data-durable-workflows/scouts/jotai-json-storage-key-isolation/atomWithStorageKeyIsolation.test.ts) | identity, mutation, async, reviver, removal outcomes | 10 tests |
| unreadable-state tests | [`atomWithStorageReadInvalidation.test.ts`](https://github.com/teamleaderleo/fieldwork/blob/d9dd61c4a0d1f9073c300519990e6ba9ec2855d9/programmes/data-durable-workflows/scouts/jotai-json-storage-key-isolation/atomWithStorageReadInvalidation.test.ts) | missing/malformed observation and restoration | 2 tests |
| historical intent | [Jotai PR #1080](https://github.com/pmndrs/jotai/pull/1080), merge commit `9e336c6...` | same-key identity during mount/subscription reread | original issue #1079 regression |

## Reproduction and characterization

### Setup

- exact released package: `jotai@2.20.2`
- release commit: `5c4ca26b0db5571114be58393e17854a771f7790`
- exact current source inspected: `56a9cc51de8a5dd762b95a145820f12589cc47c9`
- baseline workflow: Fieldwork run `30548784323`
- candidate workflow: Fieldwork run `30579753383`
- platform matrix: Ubuntu 24.04, Node 22, 24, and 26

### Baseline result

One adapter reading keys `alpha` and `beta`, each containing the same object JSON, returns the same object reference for both keys. Mutating `alpha`'s returned object changes `beta`'s previously returned object in memory. Separate adapters and different JSON act as negative controls.

### Candidate result

The candidate returns distinct objects for equal JSON under different keys, preserves repeated same-key identity across other-key reads, isolates mutation, preserves reviver semantics, and invalidates only the affected key for the tested removal and unreadable-state transitions.

## Confirmed failure model: cross-key alias

1. `createJSONStorage()` owns one `lastStr` and `lastValue` pair.
2. Key `alpha` reads serialized string `S`; the adapter parses `S` into object `A` and remembers both.
3. Key `beta` reads the same serialized string `S`.
4. The adapter sees `lastStr === S` and returns object `A` without considering the key.
5. Callers for `alpha` and `beta` now hold one mutable object.
6. A mutation through either reference changes the value observed through the other reference, without a storage operation for the other key.

Steps 1–6 are target-executed against the released package.

## Known candidate ordering limit

1. An async read for key `alpha` captures pre-removal serialized string `S`.
2. `removeItem(alpha)` settles and deletes the current cache entry.
3. The older read resolves afterward and stores a parsed object for `S`.
4. Storage later recreates `alpha` with identical `S`.
5. A current read reuses the late read's object identity.

Independent review `4823648945` and the 2026-08-01 dependency-free model reproduce this sequence. The generation-counter repair is retained in unit 21. Unit 20's key-scoping mechanism remains valid, while its standalone invalidation claim stays bounded to the executed orderings.

## Consequence and claim boundary

### Established

- Adapter-wide cache identity crosses storage-key boundaries in released Jotai.
- Equal JSON under different keys can create a shared mutable object.
- A per-key map removes that alias and preserves unchanged same-key identity in the executed matrix.
- Adapter-lifetime retention is the selected narrow compatibility policy.
- A late async completion can regain cache publication authority after a newer invalidation.

### Inferred

- Applications that reuse one JSON adapter across independent keys and mutate returned objects can observe unexplained cross-key in-memory changes.
- The practical risk grows with adapter reuse and mutable values.

### Unknown or unmeasured

- Production frequency and user impact.
- Typical number of dynamic keys per adapter and retained heap size.
- Browser `localStorage`, React Native AsyncStorage, and custom thenable behavior on the final direct source branch.
- Maintainer preference for one combined unit 20+21 submission versus a stacked sequence.

## Selected implementation

Unit 20 changes adapter-local cache ownership from one pair to:

```ts
const cachedValues = new Map<string, { str: string; value: Value }>()
```

For each key:

- equal unchanged JSON returns that key's cached value;
- equal JSON under another key parses independently;
- malformed or missing data deletes only the observed key's cache entry;
- removal preserves the underlying error and invalidates the affected key on the terminal outcome in the retained candidate;
- unrelated-key entries survive affected-key transitions.

Retention lasts until named invalidation or adapter collection. Finite eviction was declined because it makes same-key identity depend on unrelated-key activity. A public release/dispose API was deferred because it widens caller ownership.

## Compatibility analysis

- public API: unchanged
- source compatibility: unchanged public types and call signatures
- binary or wire compatibility: not applicable
- persistence or format compatibility: unchanged JSON encoding and storage keys
- platform behavior: sync and promise-like backends executed on Node; browser and React Native final checks remain
- performance and allocation: map lookup replaces scalar comparison; one entry retained per observed key until invalidation or adapter collection
- cancellation, retry, and recovery: no cancellation API; stale async completion ordering requires unit 21
- generated output: no generated file expected; build output must be checked on direct source head
- migration or rollback: source-only revert restores adapter-wide cache behavior

## Adversarial and edge controls

- repeated same-key reads around unrelated-key activity
- two keys with identical serialized JSON
- mutation through one key's returned object
- synchronous and asynchronous string storage
- custom reviver invocation
- synchronous removal success and throw
- asynchronous removal pending, fulfillment, rejection, and commit-then-reject
- out-of-band removal and later identical recreation
- malformed JSON and later identical restoration
- unrelated-key preservation
- late pre-removal async completion, reproduced as the unit 21 dependency

## Review risks

1. **The map retains entries for dynamic keys.** The selected policy preserves established same-key identity; representative churn measurements would reopen the decision.
2. **Removal invalidation semantics are wider than cross-key isolation.** The retained tests support the named paths, while async publication ordering requires the unit 21 generation fence.
3. **Two new test files may be broader than target style prefers.** A direct branch reviewer may fold cases into the existing storage suite while preserving every assertion.
4. **Focused execution can hide repository-wide build or test failures.** Ordinary gates remain a clearing condition.

## Reversing evidence

Reopen the conclusion if:

- current Jotai source replaces the adapter-wide cache or adds equivalent key isolation;
- maintainers define adapter-wide identity sharing as intentional;
- the original same-key identity requirement has been removed or superseded;
- representative dynamic-key evidence shows unacceptable retained growth;
- direct-source ordinary gates expose a compatibility failure.

## Adjacent work excluded

- async read generation authority — unit 21 / Fieldwork issue #282
- read versus `setItem` generation ordering
- general storage transaction semantics
- subscription reset propagation from Jotai issue #1815
- ecosystem prevalence and production severity
