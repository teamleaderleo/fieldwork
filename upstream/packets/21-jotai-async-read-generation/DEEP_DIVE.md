# Deep dive — unit 21 Jotai async read generation

## In simple words

`createJSONStorage()` memoizes parsed JSON so repeated reads of unchanged bytes can return the same value identity. Unit 20 changes that cache from one adapter-wide entry to one entry per storage key. On that selected base, asynchronous reads still receive parse closures that can publish into the shared per-key cache whenever their backend promises settle.

A read started earlier can therefore settle after a newer read or a completed removal and replace the cache identity chosen by the newer operation. The selected repair assigns each key a monotonically increasing read generation. Every read captures its generation at initiation. Valid and malformed completions may update shared cache state only while their generation remains current, and completed removal advances the same generation before invalidation.

The repair has focused target execution on Node 22, 24, and 26. A clean direct Jotai branch still depends on unit 20's clean source head and an owned fork.

## Governing invariant

> For each storage key, cache publication authority follows read initiation order and completed removal invalidation: only the current generation may publish or delete shared parsed identity, while each caller still receives the result of its own backend operation under the existing same-string identity behavior.

## Current behavior

The relevant behavior is the stacked unit-20 candidate, because public Jotai main still uses one adapter-wide `lastStr`/`lastValue` cache.

- entrypoint: `createJSONStorage()` in `src/vanilla/utils/atomWithStorage.ts`
- state owner after unit 20: one adapter-local `Map<string, { str, value }>`
- caller-visible result: each `getItem()` resolves from its own backend read; equal serialized bytes may reuse the currently cached object identity
- side effect: the parse closure may publish or delete that key's shared cached identity
- cleanup owner: unit 20 invalidates the affected key when removal settles; unit 21 adds generation advancement at that point
- publication boundary: successful JSON parse publishes identity; malformed or missing input deletes identity
- ordering: without unit 21, promise completion order controls publication even when read initiation order or completed removal says otherwise

Exact current public source: [`atomWithStorage.ts` at `56a9cc51...`](https://github.com/pmndrs/jotai/blob/56a9cc51de8a5dd762b95a145820f12589cc47c9/src/vanilla/utils/atomWithStorage.ts).

## Source map

| Area | Exact path and symbol | Responsibility | Relevant tests |
| --- | --- | --- | --- |
| JSON adapter | [`createJSONStorage()`](https://github.com/pmndrs/jotai/blob/56a9cc51de8a5dd762b95a145820f12589cc47c9/src/vanilla/utils/atomWithStorage.ts#L88-L202) | obtains serialized values, parses them, memoizes parsed identity, delegates writes/removals, and adapts subscriptions | [`atomWithStorage.test.tsx`](https://github.com/pmndrs/jotai/blob/56a9cc51de8a5dd762b95a145820f12589cc47c9/tests/react/vanilla-utils/atomWithStorage.test.tsx) |
| Unit 20 prerequisite | [`candidate.patch` at `d9dd61c4...`](https://github.com/teamleaderleo/fieldwork/blob/d9dd61c4a0d1f9073c300519990e6ba9ec2855d9/programmes/data-durable-workflows/scouts/jotai-json-storage-key-isolation/candidate.patch) | establishes per-key cache identity and terminal removal invalidation | [`atomWithStorageKeyIsolation.test.ts`](https://github.com/teamleaderleo/fieldwork/blob/d9dd61c4a0d1f9073c300519990e6ba9ec2855d9/programmes/data-durable-workflows/scouts/jotai-json-storage-key-isolation/atomWithStorageKeyIsolation.test.ts), [`atomWithStorageReadInvalidation.test.ts`](https://github.com/teamleaderleo/fieldwork/blob/d9dd61c4a0d1f9073c300519990e6ba9ec2855d9/programmes/data-durable-workflows/scouts/jotai-json-storage-key-isolation/atomWithStorageReadInvalidation.test.ts) |
| Characterization | [`atomWithStorageAsyncReadGeneration.test.ts` at `2fb60bd...`](https://github.com/teamleaderleo/fieldwork/blob/2fb60bd0497d5557afb54d11c3d6d1a31020b312/programmes/data-durable-workflows/scouts/jotai-json-storage-key-isolation/atomWithStorageAsyncReadGeneration.test.ts) | proves completion-order publication and removal-crossing repopulation | Fieldwork PR #284, run `30588753020` |
| Selected repair | [`async-read-generation-candidate.patch` at `34670f7...`](https://github.com/teamleaderleo/fieldwork/blob/34670f709753668827043bbc76c4159a8b36ade2/programmes/data-durable-workflows/scouts/jotai-json-storage-key-isolation/async-read-generation-candidate.patch) | adds per-key generations and publication guards | [`repair test` at `34670f7...`](https://github.com/teamleaderleo/fieldwork/blob/34670f709753668827043bbc76c4159a8b36ade2/programmes/data-durable-workflows/scouts/jotai-json-storage-key-isolation/atomWithStorageAsyncReadGenerationRepair.test.ts) |
| Expanded controls | [`packet native test draft`](./fixtures/atomWithStorageAsyncReadGenerationRepair.test.ts) | adds rejected-read semantics and same-string identity precision | [`local model`](./fixtures/async-read-generation-model.mjs), [`receipt`](./receipts/20260801-local-reconciliation.md) |

## Reproduction or characterization

### Setup

- exact upstream revision: `56a9cc51de8a5dd762b95a145820f12589cc47c9`
- selected prerequisite: unit 20 patch at `d9dd61c4a0d1f9073c300519990e6ba9ec2855d9`
- characterization head: `2fb60bd0497d5557afb54d11c3d6d1a31020b312`
- environment: GitHub Actions Ubuntu 24.04, Node 22/24/26
- command: focused Vitest matrix plus changed-file ESLint, Prettier, and `tsc --noEmit`

### Baseline result

The characterization established five material transitions:

1. a newer same-key read settles first, then an older read replaces shared cache identity;
2. a read started before removal settles later and repopulates identity;
3. an older valid completion restores authority after a newer missing read;
4. an older valid completion restores authority after a newer malformed read;
5. unrelated keys remain isolated.

The Node 24 characterization job ran four files and 42 tests. Node 22 and 26 also passed the characterization matrix, proving the tests described the selected unit-20 behavior consistently.

### Candidate result

At exact executed repair head `e99c7d2e9e3b16c04b1738397ad6109758ad481e`, the generation repair workflow passed on Node 22, 24, and 26. The inspected Node 24 job ran four files and 43 tests, then ESLint, Prettier, and TypeScript.

Six native controls prove the selected repair across reverse same-key completion, completed removal, newer missing storage, newer malformed JSON, stale malformed completion, and unrelated-key stability.

A local 11-case model on Node `v22.16.0` added four rejected-read cases and the same-string stale-caller behavior. These additions remain `target-test-prepared` until the clean direct source branch executes them.

## Failure model

Confirmed sequence:

1. `getItem('alpha')` starts read generation N and captures a parse closure.
2. a later read or removal becomes authoritative for `alpha`.
3. the older backend promise settles after that later operation.
4. without a generation guard, its parse closure publishes or deletes `alpha`'s shared cache entry.
5. a subsequent read can reuse identity selected by the obsolete operation.

The caller's own returned value and shared cache publication are separate boundaries. A stale caller may still receive its parsed result. When stale and current reads contain the same serialized bytes, the existing cache lookup can return the newer cached object identity to the stale caller before publication logic runs; the repair intentionally preserves this same-string behavior.

## Consequence and claim boundary

### Established

- completion order can override initiation order for shared cache publication on the selected unit-20 base;
- a pre-removal read can repopulate cache identity after removal settlement;
- per-key generations prevent stale valid and malformed completions from mutating shared cache state;
- unrelated keys remain independent;
- rejected reads remain caller-visible and advance authority at initiation in the model;
- current public main still lacks the prerequisite per-key cache, so unit 21 is a stacked contribution.

### Inferred

- initiation-ordered authority is the conservative rule for a rejected newer read: it suppresses older publication while preserving whatever cache identity existed before the rejected read;
- the added map and integer increment have constant-time cost per operation and adapter-lifetime retention consistent with unit 20's selected cache lifetime.

### Unknown or unmeasured

- frequency in real applications;
- memory retained by dynamic key churn;
- browser, React Native, and custom backend behavior beyond the focused Node matrix;
- repository-wide build and test compatibility on a direct source head;
- practical counter exhaustion after more than `Number.MAX_SAFE_INTEGER` initiations for one key.

## Selected implementation

The JSON adapter owns the publication invariant because it owns parsed cache identity.

- `readGenerations` maps each key to its latest initiated read/removal generation;
- `advanceReadGeneration(key)` returns the newly current generation;
- `getItem()` captures a generation before backend access;
- successful parse publishes only when the captured generation remains current;
- malformed input deletes only when the captured generation remains current;
- removal settlement advances the generation before deleting cached identity;
- backend rejections propagate unchanged through the promise chain;
- writes and subscription callbacks remain unchanged.

The unit-only patch is retained at [`patches/0001-fix-utils-fence-stale-async-json-reads.patch`](./patches/0001-fix-utils-fence-stale-async-json-reads.patch).

## Compatibility analysis

- public API: unchanged
- source compatibility: one internal map and helper added; no exported types change
- binary or wire compatibility: not applicable
- persistence or format compatibility: stored JSON bytes remain unchanged
- platform behavior: plain `Map` and number operations; focused Linux/Node matrix passed
- performance and allocation: one adapter-local map entry per observed key plus one increment per read and terminal removal
- cancellation, retry, and recovery: backend promise rejection remains visible; later reads can establish authority; no cancellation API exists at this boundary
- generated output: none required in the source diff
- migration or rollback: revert the unit-21 commit while retaining unit 20; cache publication returns to completion order

## Adversarial and edge controls

- reverse same-key completion;
- completion crossing removal settlement;
- newer missing storage versus older valid data;
- newer malformed storage versus older valid data;
- stale malformed completion versus newer valid identity;
- backend read rejection with and without prior cache identity;
- recovery after rejection;
- unrelated-key identity through same-key races and rejection;
- same-string stale caller reuse of newer cached identity.

## Review risks

1. **Stack dependency hidden in a direct-main diff.** The unit-21 patch references `cachedValues`, which exists only after unit 20. The local patch-order check fails directly on main and passes after unit 20.
2. **Rejected-read semantics underspecified.** The original six tests omit promise rejection. The packet adds four native controls and a passing model; direct target execution remains required.
3. **Claim that every caller receives a freshly parsed result.** Equal serialized bytes may reuse current cache identity. Draft wording says each caller receives its operation result under existing same-string identity semantics.
4. **Accidental expansion into all storage operations.** `setItem()` and subscription callbacks do not advance the generation. They remain excluded.
5. **Adapter-lifetime memory growth.** Unit 20 selected adapter-lifetime per-key retention; unit 21 follows that policy and records dynamic-key churn as a reopening trigger.

## Reversing evidence

Reopen the conclusion if:

- current Jotai main replaces the cache with equivalent initiation-ordered publication authority;
- target-native rejection controls contradict the model;
- maintainers define completion-order cache publication as intentional;
- unit 20 selects a different cache owner or lifecycle;
- representative performance evidence shows the generation map creates material regression.

## Adjacent work excluded

- read versus `setItem()` ordering;
- read versus subscription-event ordering;
- a general generation covering every storage operation;
- unit 20's cross-key isolation, removal semantics, and retention decision;
- public discussion, issue filing, or pull-request submission.
