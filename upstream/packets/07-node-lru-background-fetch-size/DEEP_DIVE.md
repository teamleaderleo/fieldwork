# Deep dive — unit 07 backgroundFetchSize snapshot

## In simple words

A missing-key `fetch()` inserts an internal promise into the cache before the fetched value resolves. With size tracking enabled, that promise receives a provisional size. `backgroundFetchSize` supplies that number.

The released implementation read the public mutable field while inserting the promise. JavaScript callers can supply invalid values, and `fetchMethod` itself runs synchronously inside the Promise executor. That callback can mutate the field after an early check and before insertion accounting reads it. The selected repair captures one valid number before dispatch and carries it with the pending operation.

## Governing invariant

> Every missing-key background fetch under active size tracking is charged one primitive finite nonnegative integer captured before user code runs, and that charge remains stable until settlement.

## Current behavior

- entrypoint: `LRUCache#fetch()` → `#fetch()` → `#backgroundFetch()`
- state owner: the cache owns the provisional internal `BackgroundFetch` promise and size arrays
- caller-visible result: same-key callers coalesce on one provider execution; pending and settled size accounting remains coherent
- side effects: provisional insertion may evict entries to stay within `maxSize`
- cleanup owner: normal background-fetch resolution, abort, deletion, replacement, or eviction paths
- persistence or publication boundary: in-memory cache state only
- relevant ordering: Promise construction invokes `fetchMethod` synchronously before `#set()` inserts the internal promise

## Source map

| Area | Exact path and symbol | Responsibility | Relevant tests |
| --- | --- | --- | --- |
| numeric validation | [`src/index.ts#L45-L50`](https://github.com/teamleaderleo/node-lru-cache/blob/0f4a357a9bc0b09ad413e99fa566317bf4ce283c/src/index.ts#L45-L50) | accept zero and positive integers while rejecting coercive values | constructor matrix in [`test/background-fetch-size.ts`](https://github.com/teamleaderleo/node-lru-cache/blob/0f4a357a9bc0b09ad413e99fa566317bf4ce283c/test/background-fetch-size.ts) |
| public/internal type | [`BackgroundFetch`](https://github.com/teamleaderleo/node-lru-cache/blob/0f4a357a9bc0b09ad413e99fa566317bf4ce283c/src/index.ts#L114-L122) | optional receipt preserves source compatibility for exported mocks | build/declaration gate |
| constructor boundary | [`LRUCache` constructor](https://github.com/teamleaderleo/node-lru-cache/blob/0f4a357a9bc0b09ad413e99fa566317bf4ce283c/src/index.ts#L1410-L1470) | validate declared configuration before assignment | invalid constructor controls |
| consumption boundary | [`#requireSize`](https://github.com/teamleaderleo/node-lru-cache/blob/0f4a357a9bc0b09ad413e99fa566317bf4ce283c/src/index.ts#L1730-L1775) | consume and defensively validate the operation receipt | corrupted internal receipt control |
| dispatch boundary | [`#backgroundFetch`](https://github.com/teamleaderleo/node-lru-cache/blob/0f4a357a9bc0b09ad413e99fa566317bf4ce283c/src/index.ts#L2490-L2670) | snapshot before synchronous callback invocation and attach receipt | callback mutation and next-fetch controls |

## Reproduction or characterization

### Setup

- exact upstream revision: `16b3a916662ab449d496b7b4b4f04132565d1d28` (`lru-cache@11.5.2`)
- environment: Node 22, 24, and 26 in Fieldwork workflow `30491292307`
- fixture or input: synthetic missing-key background fetches using `NaN`, negative, fractional, infinity, and string values
- command: `npm run probe` from the retained package probe on Fieldwork PR #135

### Baseline result

- `NaN` permanently poisoned `calculatedSize`.
- Negative and fractional values entered live accounting.
- Positive infinity prevented provisional insertion and caused two same-key provider calls.
- Runtime string `'2'` changed addition into concatenation, removed entries, drove the public count negative, and rejected both waiters with `Invalid array length`.
- Zero preserved a cached, coalesced pending fetch with zero provisional size.

### Candidate result

Earlier exact candidate executions established constructor rejection, pre-dispatch rejection with zero provider calls, immutable pending size during synchronous callback mutation, same-key coalescing, and normal settlement. Current clean head `0f4a357a...` contains the reviewed final source and native controls; its repository CI and benchmark receipts are tracked in `TESTS.md`.

## Failure model

1. A caller constructs or mutates `backgroundFetchSize` to an invalid runtime value.
2. A missing-key fetch begins while size tracking is active.
3. The released implementation inserts the internal background promise and reads the mutable field for provisional accounting.
4. Invalid arithmetic enters calculated size, eviction, or index behavior.

A separate time-of-check/time-of-use path exists:

1. Code validates the public field before Promise construction.
2. Promise construction synchronously invokes user `fetchMethod`.
3. User code mutates `cache.backgroundFetchSize`.
4. Insertion re-reads the mutated field.

All ordering steps are source-confirmed. Production prevalence remains unknown.

## Consequence and claim boundary

### Established

- Invalid values can corrupt live accounting and caller-visible fetch behavior on released `11.5.2`.
- A snapshot taken before dispatch closes the demonstrated synchronous mutation window.
- Zero is a coherent supported value and requires preservation.

### Inferred

- Any integration that sources this option from untyped or dynamically parsed configuration can reach the defect family.
- Stable per-operation accounting reduces re-entry sensitivity without freezing the public field for later calls.

### Unknown or unmeasured

- Real-world frequency and affected production deployments.
- Performance impact beyond ordinary repository benchmarks.
- Maintainer preference for constructor-wide validation versus validation only when size tracking consumes the option.

## Selected implementation

The cache validates declared configuration at construction. During a missing-key fetch under active size tracking, `#backgroundFetch()` reads and validates `this.backgroundFetchSize` before creating the Promise that calls user code. The resulting number is assigned to `BackgroundFetch.__size`. `#requireSize()` consumes that receipt and rejects an absent or corrupt receipt.

The exported property is optional in the TypeScript type. Internal construction assigns it on every background-fetch object. This preserves compatibility for external typed mocks while retaining the runtime invariant where provisional accounting applies.

Stale refreshes bypass missing-key provisional insertion and continue using the existing entry’s size. Caches without size tracking skip the snapshot and remain insensitive to later irrelevant field mutation. Settlement replaces the provisional charge with the resolved value’s calculated size.

## Compatibility analysis

- public API: same option and public mutable field; invalid constructor values now throw `TypeError`
- source compatibility: optional `BackgroundFetch.__size` avoids forcing external typed mocks to add a new field
- binary or wire compatibility: not applicable
- persistence or format compatibility: not applicable
- platform behavior: ordinary JavaScript number semantics; native matrix spans Linux, macOS, and Windows
- performance and allocation: one validation and one promise property per missing-key size-tracked fetch; benchmark gate required
- cancellation, retry, and recovery: existing abort, replacement, eviction, rejection, and settlement paths remain unchanged
- generated output: declarations are produced by the existing build; no generated files are committed
- migration or rollback: revert the single candidate commit

## Adversarial and edge controls

- re-entry: synchronous `fetchMethod` mutation to string, `NaN`, and negative values
- concurrency: two same-key callers remain coalesced
- cancellation or interruption: existing native suite retains eviction and replacement behavior
- failure before ownership transfer: invalid mutation rejects before provider dispatch and leaves cache state unchanged
- failure after partial effect: corrupted internal receipt is rejected on reinsertion
- cleanup failure: not applicable to this in-memory accounting change
- same-key collision: zero and positive provisional sizes preserve one provider call
- unrelated-resource isolation: no-size caches ignore the field; stale refresh preserves existing size
- platform boundary: CI workflow covers Node 24/25 on Linux, macOS, Windows bash, and Windows PowerShell; benchmarks cover Node 22/24/25 on Linux, macOS, and Windows

## Review risks

1. **Constructor validation may reject a previously ignored invalid option in a no-size cache.** The selected contract treats an explicitly supplied option as configuration and mirrors validation conventions for other numeric options.
2. **The internal receipt leaks through an exported type.** Making it optional preserves typed adapters while the accounting boundary enforces presence.
3. **The autopurge control is adjacent to the product change.** It covers an existing line required by the repository’s complete-coverage gate and changes test behavior only.
4. **The candidate may widen beyond the bug.** The exact diff contains one source file and the existing focused test file; no dependencies, workflows, snapshots, or lockfiles remain.

## Reversing evidence

Reopen the conclusion if:

- current upstream `main` changes the background-fetch construction or provisional accounting owner;
- maintainers document coercive or negative/fractional `backgroundFetchSize` values as supported;
- exact-head native tests demonstrate a compatibility regression in stale refresh, no-size mode, zero coalescing, or settlement;
- a current public issue or PR supplies an equivalent or conflicting repair.

## Adjacent work excluded

- general validation of every mutable cache option
- broader background-fetch cancellation semantics
- changes to stale-while-refresh ownership
- redesign of size-array or eviction bookkeeping
- production telemetry or severity claims
