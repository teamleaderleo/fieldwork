# lru-cache background fetch size accounting

State: `probe-prepared`

Fieldwork lane: #132

Programme: data-durable-workflows

Target package: `lru-cache@11.5.2`

Source pin: `isaacs/node-lru-cache@16b3a916662ab449d496b7b4b4f04132565d1d28`

Feature commit: `4708153206daf822a3ad440ce47248b9cfbdb973`

Upstream contact authorized: `false`

## In simple words

`lru-cache` can assign a temporary size to an entry while an asynchronous cache fill is still running. Version 11.5 added the `backgroundFetchSize` option for that value.

The constructor stores the runtime value directly. The later accounting code assumes it is a positive finite integer, but does not validate it before adding it to `calculatedSize` and using it in eviction arithmetic.

Source review indicates that JavaScript callers can pass values such as `NaN`, negative numbers, fractions, or strings and corrupt the public size total while a fetch is pending. `Infinity` follows a different path: it is treated as larger than `maxEntrySize`, so the provisional entry is not cached and concurrent requests are no longer coalesced.

## Source map

### Option introduction

Feature commit `4708153206daf822a3ad440ce47248b9cfbdb973` added:

- `backgroundFetchSize?: number`;
- a public `backgroundFetchSize` field;
- constructor default `1`;
- provisional use when a background fetch does not shadow a stale entry.

### Constructor boundary

The constructor assigns:

```ts
this.backgroundFetchSize = backgroundFetchSize
```

It validates `max`, `sizeCalculation`, and `fetchMethod`, but does not validate this new size input.

### Size invariant

The internal `isPosInt()` helper requires a non-zero, finite, positive integer. Explicit entry sizes and `sizeCalculation` results are checked against that invariant.

For a background fetch, `#requireSize()` instead returns `this.backgroundFetchSize` directly.

### Accounting consequence

`#addItemSize()` stores that value and performs:

```ts
const maxSize = this.#maxSize - sizes[index]
while (this.#calculatedSize > maxSize) {
  this.#evict(true)
}
this.#calculatedSize += sizes[index]
```

Consequences supported by JavaScript coercion and the inspected source:

- `NaN` makes `calculatedSize` become and remain `NaN`, disabling meaningful comparisons;
- a negative value undercounts in-flight usage and can temporarily admit excess entries;
- a fraction violates the integer size contract;
- a numeric string changes `calculatedSize` into a string and can later produce incorrect subtraction or eviction;
- `Infinity` exceeds `maxEntrySize`, prevents provisional insertion, and causes duplicate concurrent fetches instead of one shared in-flight fetch.

## Probe

The released-package probe uses exact dependency `lru-cache@11.5.2` and runs on Node 22, 24, and 26.

Cases:

- valid control: `1`;
- zero;
- negative `-1`;
- fraction `1.5`;
- `NaN`;
- positive infinity;
- runtime numeric string `'2'`.

For each case it records:

- constructor acceptance;
- number of `fetchMethod` calls after two same-key fetches;
- cache entry count;
- `calculatedSize` value and runtime type;
- behavior after inserting a normal entry;
- behavior after resolving the pending fetches;
- final cleanup.

The probe contains assertions for the source-predicted distinctions and fails if the released package behaves differently.

## Prior-art status

Searches for `backgroundFetchSize` with validation, `NaN`, and `Infinity` found no matching current issue or pull request.

Historical issue #264 documents the project's established expectation that size inputs are positive integers and should produce clear runtime errors when required size information is invalid. It does not cover provisional background-fetch sizing.

## Candidate repair

Validate `backgroundFetchSize` during construction using the same positive finite integer invariant used by entry sizes and `sizeCalculation` results.

Candidate error shape:

```ts
if (!isPosInt(backgroundFetchSize)) {
  throw new TypeError(
    'backgroundFetchSize must be a positive integer',
  )
}
```

The validation should occur regardless of whether `maxSize`, `sizeCalculation`, or `fetchMethod` is currently configured, matching the constructor's treatment of other supplied option values and preventing delayed configuration-dependent failures.

## Acceptance requirements

- valid positive integers retain current behavior;
- invalid runtime values fail at construction with a stable `TypeError`;
- two concurrent same-key fetches remain coalesced for valid provisional sizes;
- `calculatedSize` remains a finite non-negative integer;
- later insertion and eviction remain consistent;
- stale-entry background fetches retain the stale entry's size;
- no behavior change occurs when background fetch support is unused.

## Contact boundary

No upstream issue, pull request, comment, review, reaction, or message has been created. Any packet remains held for explicit human authorization.
