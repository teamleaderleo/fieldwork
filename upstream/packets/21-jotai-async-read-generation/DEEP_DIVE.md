# Deep dive — unit 21 Jotai async read generation

## In simple words

`createJSONStorage()` memoizes parsed JSON so repeated reads of unchanged bytes can return the same value identity. Unit 20 changes that cache from one adapter-wide entry to one entry per storage key. On that base, asynchronous reads can still settle out of order and let an older read publish or delete shared cache identity after a newer read or completed removal.

Unit 21 assigns each key a monotonically increasing read generation. Every read captures its generation at initiation. Valid and malformed completions may update shared cache state only while that generation remains current. Completed removal advances the same generation before invalidation.

The clean source now exists in the owned fork. Unit 21 head `dfe607d7637fbcf61ae41c39f4f470f61fa7c531` is an exact two-commit child of unit 20 head `b2f84273b53bbed9df073354dac503e520be7101`, with only one production file and one eleven-case target-native test file. Historical focused target execution is green; current fork workflows are queued.

## Governing invariant

> For each storage key, cache publication authority follows read initiation order and completed removal invalidation: only the current generation may publish or delete shared parsed identity, while each caller still receives the result or rejection of its own backend operation under the existing same-string identity behavior.

## Source and state map

| Area | Exact path or identity | Responsibility |
| --- | --- | --- |
| Public baseline | `pmndrs/jotai` at `56a9cc51de8a5dd762b95a145820f12589cc47c9` | adapter-wide `lastStr`/`lastValue` cache |
| Unit 20 clean base | `teamleaderleo/jotai:fix/utils-key-scoped-json-cache` at `b2f84273b53bbed9df073354dac503e520be7101` | per-key cache entries and terminal removal invalidation |
| Unit 21 clean source | `teamleaderleo/jotai:fix/utils-async-read-generation` at `dfe607d7637fbcf61ae41c39f4f470f61fa7c531` | per-key generations and guarded publication/deletion |
| Production entrypoint | `src/vanilla/utils/atomWithStorage.ts`, `createJSONStorage()` | backend reads, parsing, memoized identity, writes, removals, subscriptions |
| Clean unit-21 regression | `tests/react/vanilla-utils/atomWithStorageAsyncReadGenerationRepair.test.ts` | eleven deterministic read/read, read/removal, malformed, rejection, same-string, and unrelated-key controls |
| Historical characterization | head `2fb60bd0497d5557afb54d11c3d6d1a31020b312` | proves completion-order publication on the selected unit-20 behavior |
| Historical accepted repair | head `e99c7d2e9e3b16c04b1738397ad6109758ad481e` | six-case target execution of the selected mechanism |

The unit-21 target compare is `b2f84273b53bbed9df073354dac503e520be7101...dfe607d7637fbcf61ae41c39f4f470f61fa7c531`: ahead by two commits, behind by zero, and exactly two changed files.

## Current behavior and failure model

After unit 20, the adapter owns one `Map<string, { str, value }>` for parsed identity. Each `getItem()` creates a parse closure. For asynchronous storage, that closure runs whenever its backend promise settles.

Without unit 21:

1. an older read starts for key `alpha`;
2. a newer read starts or removal completes for `alpha`;
3. the newer operation establishes the intended current cache state;
4. the older backend promise settles later;
5. its parse closure publishes valid identity or deletes identity after malformed data;
6. later reads can reuse cache state selected by the obsolete completion.

The caller's return value and shared cache publication are separate boundaries. A stale caller still receives its own backend outcome. When stale and current reads contain the same serialized bytes, the cache lookup can return the newer cached object identity to the stale caller before publication guards run. The repair preserves that compatibility behavior.

## Characterization and repair evidence

### Characterization

At exact head `2fb60bd0497d5557afb54d11c3d6d1a31020b312`, workflow `30588753020` passed on Node 22, 24, and 26 while establishing the selected baseline behavior. The inspected Node 24 job ran four files and 42 tests, then ESLint, Prettier, and TypeScript.

The characterization demonstrated:

1. an older same-key read can replace identity published by a newer read;
2. a pre-removal read can repopulate identity after removal settlement;
3. an older valid result can restore authority after a newer missing result;
4. an older valid result can restore authority after a newer malformed result;
5. unrelated keys remain isolated.

### Accepted focused repair

At exact head `e99c7d2e9e3b16c04b1738397ad6109758ad481e`, workflow `30623229098` passed on Node 22, 24, and 26. Adjacent unit-20 workflow `30623229114` also passed. The inspected Node 24 job `91132389642` ran four files and 43 tests, then ESLint, Prettier, and `tsc --noEmit`.

Six native controls cover reverse same-key completion, completed removal, newer missing storage, newer malformed JSON, stale malformed completion, and unrelated-key stability.

### Expanded controls and clean materialization

A dependency-free model passed 11/11 on Node `v22.16.0`, adding rejected-read and same-string controls. The byte-equivalent eleven-case native test is now present at the clean target head `dfe607d7637fbcf61ae41c39f4f470f61fa7c531`.

Fork-local draft PR `teamleaderleo/jotai#3` triggered the repository's existing Test, multiple-version, old-TypeScript, multiple-build, compressed-size, and preview-release workflows. Their exact conclusions remain queued and must be recorded before promotion.

## Selected implementation

The JSON adapter owns the invariant because it owns parsed cache identity.

- `readGenerations` maps each key to its latest initiated read or completed-removal generation.
- `advanceReadGeneration(key)` increments and returns the current generation.
- `getItem()` captures a generation before backend access.
- A successful parse writes `cachedValues` only if the captured generation is still current.
- A malformed result deletes `cachedValues` only if the captured generation is still current.
- Removal settlement advances the generation inside unit 20's terminal `invalidate()` path before deleting cached identity.
- Backend promise rejection propagates unchanged.
- `setItem()` and subscription callbacks remain unchanged.

This is 15 additions and 2 deletions in the production file. The retained unit-only patch is [`patches/0001-fix-utils-fence-stale-async-json-reads.patch`](./patches/0001-fix-utils-fence-stale-async-json-reads.patch).

## Rejection semantics

A read advances authority when it starts, even if the backend later rejects. This means:

- the rejection remains visible to that caller;
- an older read cannot become shared publication authority afterward;
- a valid cache entry from before the rejected read remains available;
- without prior cache, the older result remains caller-visible but cannot establish shared identity;
- a later successful read can establish new shared identity.

This rule follows initiation order rather than successful-completion order. It is explicitly represented in the model and clean target-native test and remains an important independent-review point.

## Consequence and claim boundary

### Established

- completion order can override intended shared cache authority on the selected unit-20 base;
- a pre-removal read can repopulate cache identity after removal settlement;
- per-key generations prevent stale valid and malformed completions from changing shared cache state;
- unrelated keys remain independent;
- backend rejection remains caller-visible;
- unit 21 depends mechanically and semantically on unit 20;
- the clean owned-fork source stack and exact two-file unit-21 diff now exist.

### Inferred

- initiation-ordered authority is the conservative rule for a rejected newer read because it prevents authority from moving backward while retaining prior cache identity;
- map lookup and integer advancement add constant-time work per operation;
- adapter-lifetime generation retention is consistent with unit 20's selected cache lifetime.

### Unknown or pending

- final conclusions and command coverage of the exact-head fork workflows;
- independent complete-diff acceptance;
- frequency and consequence in real applications;
- memory retained under dynamic key churn;
- browser, React Native, Windows, macOS, and unusual thenable/backend behavior beyond available execution;
- practical numeric counter exhaustion after extreme same-key operation counts.

## Compatibility analysis

- public API: unchanged;
- exported types: unchanged;
- stored JSON bytes and format: unchanged;
- caller-visible backend values and errors: unchanged;
- same-key same-string identity reuse: preserved;
- unrelated-key isolation: preserved from unit 20;
- runtime mechanisms: plain `Map` and numeric counters;
- migration: none;
- rollback: revert the unit-21 two-commit delta while retaining unit 20, restoring completion-order publication.

## Exact changed-file and commit fence

Files relative to unit 20:

1. `src/vanilla/utils/atomWithStorage.ts` — production generation fence;
2. `tests/react/vanilla-utils/atomWithStorageAsyncReadGenerationRepair.test.ts` — eleven regressions.

Commits:

1. `fix(utils): fence stale async JSON reads by per-key generation`;
2. `test(utils): cover stale async JSON read fencing`.

Excluded and absent: workflows, Fieldwork files, receipts, publishers, dependency changes, lockfiles, generated output, snapshots, and unrelated formatting.

## Adversarial controls

- reverse same-key completion;
- completion crossing removal settlement;
- newer missing storage versus older valid data;
- newer malformed storage versus older valid data;
- stale malformed completion versus newer valid identity;
- backend rejection with and without prior cache identity;
- recovery after rejection;
- unrelated-key stability through races and rejection;
- same-string stale-caller reuse of newer cached identity.

## Risks and review questions

1. Should rejected read initiation retain publication authority despite publishing no value?
2. Is same-string identity reuse for a stale caller the intended compatibility behavior?
3. Is advancing generation only after removal settlement correct for pending-removal identity semantics?
4. Is adapter-lifetime generation retention acceptable under dynamic-key workloads?
5. Should eventual public delivery remain stacked or be combined after unit 20 review?
6. Do the exact-head workflows cover the required focused tests, formatting, build, and aggregate test gates?

## Reversing evidence

Reopen the conclusion if:

- current Jotai source implements equivalent initiation-ordered publication authority;
- exact-head target execution contradicts the model or historical repair results;
- maintainers define completion-order cache publication as intentional;
- unit 20 changes its cache owner or lifecycle;
- representative performance evidence shows material regression.

## Adjacent work excluded

- read versus `setItem()` ordering;
- read versus subscription-event ordering;
- a generation covering all storage operations;
- unit 20's cross-key isolation and retention decision;
- public discussion, issue filing, or public pull-request submission.
