# Upstream issue draft — backgroundFetchSize accepts invalid runtime values that corrupt cache accounting

Draft status: `ready — optional issue-first route`  
Public interaction authorized: `no`

---

## Summary

`backgroundFetchSize` is used as the provisional calculated size of a missing-key background fetch. Runtime values outside the intended nonnegative-integer domain currently enter size and eviction arithmetic without validation.

JavaScript callers can supply values that TypeScript would reject, and the field is public and mutable. Invalid values can corrupt `calculatedSize`, prevent same-key fetch coalescing, evict unrelated entries, or damage index bookkeeping.

## Reproduction

1. Create a size-tracked cache with `backgroundFetchSize: '2'` at runtime.
2. Start two concurrent fetches for the same missing key.
3. Insert another sized value while the fetch is pending, then settle the provider.

Minimal code:

```js
import { LRUCache } from 'lru-cache'

let resolveFetch
const cache = new LRUCache({
  maxSize: 10,
  sizeCalculation: () => 5,
  backgroundFetchSize: '2',
  fetchMethod: () =>
    new Promise(resolve => {
      resolveFetch = resolve
    }),
})

const first = cache.fetch('a')
const second = cache.fetch('a')

console.log(cache.calculatedSize) // '02'
cache.set('b', 'B')
console.log(cache.calculatedSize) // '025'

resolveFetch('A')
console.log(await Promise.allSettled([first, second]))
console.log(cache.size)
```

## Observed behavior

Against `lru-cache@11.5.2` on Node 22, 24, and 26:

- both waiting fetches reject with `Invalid array length`;
- entries are removed;
- the public cache entry count becomes negative;
- exact negative counts can vary by runtime.

Additional runtime values produce other failures:

- `NaN` leaves `calculatedSize` as `NaN` after later insertion and settlement;
- positive infinity prevents the provisional entry from being cached, so concurrent same-key calls invoke `fetchMethod` twice;
- negative and fractional values enter live pending accounting.

`0` behaves coherently and preserves same-key coalescing.

## Expected behavior

An explicitly supplied `backgroundFetchSize` should be a primitive finite nonnegative integer. Invalid values should fail before provider dispatch or provisional accounting changes cache state. Zero should remain supported.

For an already-dispatched missing-key fetch, accounting should use the value validated before invoking user `fetchMethod`, so synchronous callback mutation affects later operations only.

## Current source observation

The constructor assigns `backgroundFetchSize` directly. During missing-key background insertion, provisional size accounting reads the public field.

Promise construction invokes `fetchMethod` synchronously before the internal background-fetch promise is inserted. A check performed before Promise construction can therefore be bypassed if insertion later re-reads the public mutable field.

## Candidate direction

A narrow repair can:

1. validate the constructor value as a primitive finite nonnegative integer;
2. for a missing-key fetch under active size tracking, validate and capture the current value before invoking `fetchMethod`;
3. attach that value to the internal pending fetch;
4. consume the captured value during provisional accounting.

Stale refreshes can continue using the existing entry size, and caches without size tracking can continue ignoring later irrelevant mutation.

## Compatibility and risks

- constructor calls that currently pass invalid runtime values would begin throwing `TypeError`;
- zero must remain valid;
- any internal receipt exposed through an exported TypeScript type should stay optional for source compatibility with external mocks or adapters;
- the repair adds one validation and one internal promise property per missing-key size-tracked fetch.

## Evidence limits

- production frequency and affected deployment count are unknown;
- tests use synthetic in-memory values;
- the benchmark gate checks regressions without claiming a measurable performance improvement.

## Versions and environment

- project version or commit: `lru-cache@11.5.2`, commit `16b3a916662ab449d496b7b4b4f04132565d1d28`
- platform: Ubuntu in the minimal released-package probe
- runtime/compiler: Node 22, 24, and 26
- relevant configuration: `maxSize`, `sizeCalculation`, `fetchMethod`, and runtime `backgroundFetchSize`

## Additional context

The option was introduced in commit `4708153206daf822a3ad440ce47248b9cfbdb973`. A current issue and pull-request search for `backgroundFetchSize` and `background fetch size` found no equivalent report or repair on 2026-08-01.

---

## Filing checklist

- [ ] Current upstream issue and PR search repeated immediately before filing.
- [ ] Reproduction works on the current public revision.
- [x] Severity and prevalence wording stays within evidence.
- [x] Private, internal, and evidence-only links are absent from the public draft.
- [ ] Target issue template and contribution policy checked again.
- [ ] AI disclosure handled according to the project policy current at filing time.
- [ ] Exact user authorization to file this issue recorded.
