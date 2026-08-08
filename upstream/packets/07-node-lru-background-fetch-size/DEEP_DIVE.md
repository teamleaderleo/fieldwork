# Deep dive — unit 07 backgroundFetchSize snapshot

## In simple words

A missing-key `fetch()` inserts an internal promise into the cache before the fetched value resolves. With size tracking enabled, that promise receives a provisional size. `backgroundFetchSize` supplies that number.

The released implementation read the public mutable field while inserting the promise. JavaScript callers can supply invalid runtime values, and `fetchMethod` itself begins synchronously inside the Promise executor. That callback can mutate the field before insertion accounting reads it. The submitted repair captures one valid number before dispatch and carries it with the pending operation.

Owner submission: [isaacs/node-lru-cache#410](https://redirect.github.com/isaacs/node-lru-cache/pull/410).

## Governing invariant

> Every missing-key background fetch under active size tracking is charged one primitive finite nonnegative integer captured before user code runs, and that charge remains stable for that in-flight operation.

## Exact submitted source

- public base: `16b3a916662ab449d496b7b4b4f04132565d1d28`;
- submitted head: `364a8c1c07c9f6281fbe19943eacd261bd410fc4`;
- source PR: `teamleaderleo/node-lru-cache#2`;
- changed files: `src/index.ts`, `test/background-fetch-size.ts`;
- total diff: +193 / -1;
- source blob: `c3549a638b84ce096b13ebd7e3f71496dbe5afd5`;
- test blob: `a83968f5110bfe42cfe32aae55cb6018aba6aebd`.

## Current behavior

- entrypoint: `LRUCache#fetch()` → `#fetch()` → `#backgroundFetch()`;
- state owner: the cache owns the provisional internal `BackgroundFetch` promise and size arrays;
- caller-visible result: same-key callers coalesce on one provider execution;
- side effect: provisional insertion can contribute to size-based eviction before the fetched value exists;
- stale refresh: uses the existing entry size instead of `backgroundFetchSize`;
- no-size cache: does not consume `backgroundFetchSize` for accounting;
- relevant ordering: Promise construction invokes `fetchMethod` synchronously before the internal promise is inserted.

## Source map

| Area | Exact path and symbol | Responsibility |
| --- | --- | --- |
| numeric validation | [`isNonNegativeInt`](https://redirect.github.com/teamleaderleo/node-lru-cache/blob/364a8c1c07c9f6281fbe19943eacd261bd410fc4/src/index.ts) | accept primitive zero or positive finite integers without coercion |
| public/internal type | [`BackgroundFetch`](https://redirect.github.com/teamleaderleo/node-lru-cache/blob/364a8c1c07c9f6281fbe19943eacd261bd410fc4/src/index.ts) | carry an optional internal provisional-size receipt without making it required for external typed mocks |
| constructor boundary | [`LRUCache` constructor](https://redirect.github.com/teamleaderleo/node-lru-cache/blob/364a8c1c07c9f6281fbe19943eacd261bd410fc4/src/index.ts) | fail fast on explicitly invalid configuration |
| consumption boundary | [`#requireSize`](https://redirect.github.com/teamleaderleo/node-lru-cache/blob/364a8c1c07c9f6281fbe19943eacd261bd410fc4/src/index.ts) | consume the stored receipt during provisional accounting |
| dispatch boundary | [`#backgroundFetch`](https://redirect.github.com/teamleaderleo/node-lru-cache/blob/364a8c1c07c9f6281fbe19943eacd261bd410fc4/src/index.ts) | validate and snapshot before synchronous provider code runs |
| regression coverage | [`test/background-fetch-size.ts`](https://redirect.github.com/teamleaderleo/node-lru-cache/blob/364a8c1c07c9f6281fbe19943eacd261bd410fc4/test/background-fetch-size.ts) | public-option validation, mutation race, zero/coalescing, stale/no-size compatibility |

## Baseline characterization

Released `lru-cache@11.5.2` on base `16b3a916...` accepted invalid runtime values into provisional accounting:

- `NaN` could poison `calculatedSize`;
- negative and fractional values entered live accounting;
- positive infinity could prevent the pending entry from being cached and break same-key coalescing;
- runtime string values could reach coercive arithmetic;
- zero remained coherent and coalesced.

The defect is narrow: it requires `fetchMethod`, missing-key `fetch()`, and active size tracking. Ordinary `get()`/`set()` caches and stale refresh accounting do not use this provisional value in the same way.

## Failure model

### Invalid runtime value

1. A caller constructs or later mutates `backgroundFetchSize` to an invalid runtime value.
2. A missing-key fetch begins while size tracking is active.
3. The released implementation inserts the internal background promise and reads the mutable field for provisional accounting.
4. Invalid arithmetic can enter calculated size, eviction, or coalescing behavior.

### Synchronous mutation race

1. The cache begins a missing-key fetch with `backgroundFetchSize = 2`.
2. Promise construction synchronously invokes user `fetchMethod`.
3. User code changes `cache.backgroundFetchSize = 4`.
4. If insertion re-reads the public property, the already-started fetch is charged `4` instead of `2`.

The submitted repair validates/captures `2` before step 2, so the current fetch keeps `2` and a later fetch can observe `4`.

## Selected implementation

The constructor validates the configured value as a primitive finite nonnegative integer. During a missing-key fetch under active size tracking, `#backgroundFetch()` reads and validates the current property before constructing the Promise that invokes user code. The captured number is attached to the internal background-fetch object as `__size`. Provisional accounting reads that operation-local receipt instead of re-reading the mutable public property.

`__size` remains optional in the exported TypeScript `BackgroundFetch` type to avoid requiring external typed mocks or adapters to add an internal field. The accounting path retains a small defensive validity check, but the regression suite does not manufacture corrupted private state to exercise it.

Stale refreshes keep the existing entry's size. Caches without size tracking skip the snapshot. Settlement replaces the provisional charge with the resolved value's ordinary calculated size.

## Submitted regression coverage

The final test suite intentionally covers distinct supported behavior rather than every constructible JavaScript value or private-state mutation:

- representative negative, fractional, `NaN`, and infinity rejection;
- representative runtime non-number rejection;
- hostile conversion object rejected without invoking conversion hooks;
- zero and positive integer acceptance;
- invalid post-construction mutation rejected before provider dispatch;
- synchronous callback mutation cannot change the current operation's charge;
- later operations observe later valid mutation;
- same-key callers remain coalesced;
- no-size caches ignore irrelevant mutation;
- stale refresh keeps the existing entry size;
- zero provisional size remains coalesced.

A prior test that changed `BackgroundFetch.__size` through `unsafeExposeInternals()` and reinserted the promise was removed before submission because upstream documents mutation through that API as unsupported and potentially breakage-inducing.

## Compatibility analysis

- public API: same option and mutable property;
- runtime behavior change: invalid constructor values now throw `TypeError`;
- zero: remains supported;
- later mutation: remains supported for later applicable operations;
- source compatibility: `BackgroundFetch.__size` is optional;
- wire/persistence compatibility: not applicable;
- generated output: no generated files are committed;
- source surface: exactly one production file and the existing feature test file;
- rollback: revert the single submitted commit.

## Execution evidence and limits

Historical receipts on the unchanged production source established:

- focused build/behavior/OXLint/Prettier/diff-hygiene success;
- Ubuntu Node 24/25 success;
- macOS Node 24/25 success;
- benchmark success;
- Windows jobs stopping before product test discovery because the unchanged repository TAP configuration cannot load `@tapjs/clock`.

The final test tree changed during regression-scope cleanup, so those historical receipts are not described as exact submitted-head green. Fresh fork CI `31231433021` and Benchmarks `31231433009` remain queued at this record update.

Production prevalence and real-world affected deployment count remain unknown.

## Review risks

1. **Constructor validation is eager.** A maintainer could prefer validating only when a size-tracked missing-key fetch consumes the option.
2. **The internal receipt appears in an exported type.** Keeping it optional limits source-compatibility impact.
3. **The accounting path validates a value that normal construction has already validated.** This is defensive rather than a separately promised public behavior.
4. **The bug surface is narrow.** The contribution should be judged as a bounded correctness repair, not a broad cache failure.

## Reversing evidence

Reopen the conclusion if upstream changes the background-fetch representation/accounting owner, documents coercive or non-integer values as supported, or identifies a compatibility regression in stale refresh, no-size mode, zero coalescing, or settlement.

## Adjacent work excluded

- redesign of the internal `BackgroundFetch` representation;
- general validation policy for every mutable cache option;
- broader background-fetch cancellation semantics;
- changes to stale-while-refresh ownership;
- general hardening against deliberately corrupted private internals;
- production telemetry or severity claims.

## Disposition

`SUBMITTED` by the owner as upstream PR #410. No additional upstream interaction is authorized from Fieldwork without explicit owner direction.
