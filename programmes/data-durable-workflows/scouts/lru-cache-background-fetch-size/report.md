# lru-cache background fetch size accounting

State: `implementing`

Fieldwork lane: #132

Programme: data-durable-workflows

Target package: `lru-cache@11.5.2`

Source pin: `isaacs/node-lru-cache@16b3a916662ab449d496b7b4b4f04132565d1d28`

Feature commit: `4708153206daf822a3ad440ce47248b9cfbdb973`

Released-package workflow: `30491292307`

Owned implementation: `teamleaderleo/node-lru-cache#1`

Owned branch: `fieldwork/background-fetch-size-validation`

Owned head: `f50193f7d92809eb1941469af3708d4d2406fce1`

Candidate workflow: `30495807465`

Upstream contact authorized: `false`

## In simple words

`lru-cache` can assign a temporary size to an entry while an asynchronous cache fill is still running. Version 11.5 added the `backgroundFetchSize` option for that value.

The constructor stores the runtime value directly. Later accounting expects a nonnegative finite integer, but the option is not validated before it enters calculated-size, eviction, and index bookkeeping.

Released `lru-cache@11.5.2` reproduced several consequences on Node 22, 24, and 26:

- `NaN` made `calculatedSize` permanently `NaN`;
- negative and fractional values entered live accounting;
- positive infinity prevented the provisional entry from being stored, so two same-key requests started two independent fetches;
- runtime string `'2'` changed arithmetic into string concatenation, then drove the public cache entry count negative and rejected both waiting fetches with `Invalid array length`.

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

It validates `max`, `maxSize`, `maxEntrySize`, `sizeCalculation`, and `fetchMethod`, but does not validate this new size input.

### Size invariant

The internal `isPosInt()` helper requires a non-zero, finite, positive integer. Explicit entry sizes and `sizeCalculation` results are checked against that invariant.

For a background fetch, `#requireSize()` instead returns `this.backgroundFetchSize` directly.

The released behavior for `0` remains coherent and matches the pre-11.5 effective accounting behavior: a pending fetch has zero provisional size but remains cached and coalesced. The conservative correction preserves it while rejecting every other value that is not a positive integer.

### Accounting consequence

`#addItemSize()` stores the provisional value and performs:

```ts
const maxSize = this.#maxSize - sizes[index]
while (this.#calculatedSize > maxSize) {
  this.#evict(true)
}
this.#calculatedSize += sizes[index]
```

That arithmetic assumes numeric, finite, integer input. Runtime coercion can affect calculated size, eviction, free-index handling, and fetch settlement.

## Executed released-package probe

The released-package probe pins `lru-cache@11.5.2` and ran on Node 22, 24, and 26.

Workflow `30491292307` passed all three jobs after the probe was strengthened to assert the observed consequences rather than merely print them. Fieldwork integrity and external-reference policy also passed for the tested head.

### Control: `1`

- constructor accepted;
- first pending fetch contributed size `1`;
- second same-key call shared the same fetch;
- settlement produced normal size accounting.

### Zero

- constructor accepted;
- pending fetch contributed size `0`;
- same-key fetch remained coalesced;
- later normal entry and settlement returned to valid integer accounting.

This is retained as a compatibility control, not promoted as a defect.

### Negative and fractional values

- `-1` made the pending total `-1` and undercounted the cache after another entry was inserted;
- `1.5` made the public total fractional while pending;
- both eventually returned to valid totals after settlement in this bounded case, but violated the accounting invariant during the operation.

### `NaN`

- the first pending fetch made `calculatedSize` `NaN`;
- a later normal insertion left it `NaN`;
- fetch settlement left it `NaN`;
- size comparisons were no longer meaningful.

### Positive infinity

- the provisional fetch was treated as larger than `maxEntrySize` and was not stored;
- a second same-key request started a second `fetchMethod` call;
- the callers received different results (`A1` and `A2`) rather than sharing one in-flight fetch.

### Runtime numeric string

TypeScript rejects the value statically, but ordinary JavaScript or untyped configuration can supply it.

Observed on Node 22 and 24:

- the first pending fetch changed `calculatedSize` to string `'02'`;
- inserting a normal size-5 entry changed it to `'025'`;
- settlement entered repeated eviction/index mutation;
- the public cache entry count became a large negative number;
- both waiting fetches rejected with `Invalid array length`;
- all entries disappeared.

The exact negative count varied by Node version, consistent with corrupted internal index bookkeeping rather than a stable user-facing state.

## Prior art

Searches for `backgroundFetchSize` with validation, `NaN`, `Infinity`, and runtime size corruption found no matching current issue or pull request.

Historical issue #264 records the project's expectation that invalid required size information should produce a clear runtime error. Existing `sizeCalculation` tests also assert `TypeError` for non-positive or non-numeric calculated sizes. Neither covers provisional background-fetch sizing introduced in 11.5.

## Owned candidate

Draft PR: `teamleaderleo/node-lru-cache#1`

The connected GitHub editor only supports complete file replacement, while `src/index.ts` is roughly 3,200 lines. Replacing that entire file mechanically would create unnecessary review and corruption risk. The branch therefore contains:

- the complete focused test update in `test/background-fetch-size.ts`;
- an exact source hunk in `.fieldwork/background-fetch-size-validation.patch`;
- a Fieldwork workflow that applies the hunk to a clean checkout before building and testing.

The candidate guard is:

```ts
if (
  typeof backgroundFetchSize !== 'number' ||
  (backgroundFetchSize !== 0 && !isPosInt(backgroundFetchSize))
) {
  throw new TypeError(
    'backgroundFetchSize must be a nonnegative integer',
  )
}

this.backgroundFetchSize = backgroundFetchSize
```

The explicit runtime type check is required before `isPosInt()`. It guarantees that strings, booleans, bigint, symbols, null, arrays, and objects receive the package's stable `TypeError` instead of incidental JavaScript coercion errors.

## Candidate tests

The owned branch covers:

- constructor acceptance for `0`, `1`, and another positive integer;
- rejection of `-1`, `1.5`, `NaN`, positive/negative infinity;
- rejection of runtime string, boolean, bigint, symbol, null, object, and array inputs;
- stable error name and message;
- zero-size pending fetch coalescing;
- a custom positive provisional size transitioning to the resolved entry size;
- the existing stale-value and eviction behavior.

Candidate workflow `30495807465` checks out the exact owned branch, applies the source hunk with `git apply --check`, builds the repository, and runs the focused test on Node 22, 24, and 26. The jobs were queued at the latest recorded check; no candidate execution result is claimed yet.

## Decision

This is a confirmed released-package defect with a narrow owned-fork candidate. The candidate is source-reviewed and ready for execution. Keep the implementation draft until the clean-checkout matrix passes and the source hunk can be committed directly through an approved write path.

## Contact boundary

No upstream issue, pull request, comment, review, reaction, or message has been created. Any packet remains held for explicit human authorization.