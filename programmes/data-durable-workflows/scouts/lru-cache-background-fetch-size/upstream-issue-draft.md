# Held upstream issue draft

Title: `backgroundFetchSize accepts invalid runtime values that corrupt cache accounting`

## Summary

`lru-cache@11.5.2` accepts invalid runtime values for the new `backgroundFetchSize` option. The value is stored without validation and later enters calculated-size, eviction, and index bookkeeping for an in-flight background fetch.

The option is typed as `number`, so TypeScript catches some inputs, but ordinary JavaScript and untyped configuration can still provide `NaN`, infinity, negative or fractional numbers, strings, and other values.

## Reproduction

```js
import { LRUCache } from 'lru-cache'

let resolveFetch
const cache = new LRUCache({
  maxSize: 10,
  sizeCalculation: () => 5,
  backgroundFetchSize: '2',
  fetchMethod: () => new Promise(resolve => {
    resolveFetch = resolve
  }),
})

const first = cache.fetch('a')
const second = cache.fetch('a')

console.log(cache.calculatedSize) // '02'
cache.set('b', 'B')
console.log(cache.calculatedSize) // '025'

resolveFetch('A')
await Promise.allSettled([first, second])

console.log(cache.size) // negative value on tested Node versions
```

On Node 22, 24, and 26, the full probe observed both waiting fetches reject with `Invalid array length`, all entries disappear, and the public cache entry count become negative. The exact negative count varies by Node version.

Additional cases:

- `NaN` makes `calculatedSize` remain `NaN` after later insertion and fetch settlement.
- `Infinity` prevents the provisional entry from being cached, so two concurrent same-key fetches execute `fetchMethod` twice and return distinct results.
- negative and fractional values enter live accounting while the fetch is pending.

`0` behaves coherently: it preserves same-key coalescing and matches the previous effective zero-size accounting for provisional fetches.

## Cause

The constructor assigns `backgroundFetchSize` directly. `#requireSize()` returns it for a background fetch without applying the positive-integer checks used for explicit entry sizes and `sizeCalculation` results.

## Suggested behavior

Preserve `0`, but reject every non-zero value that is not a positive finite integer during construction:

```ts
if (backgroundFetchSize !== 0 && !isPosInt(backgroundFetchSize)) {
  throw new TypeError(
    'backgroundFetchSize must be a nonnegative integer',
  )
}
```

## Validation

The released-package probe passed on Node 22, 24, and 26 and asserts the consequences above. No matching current issue or pull request was found.

This draft is retained in Fieldwork. It has not been posted upstream.
