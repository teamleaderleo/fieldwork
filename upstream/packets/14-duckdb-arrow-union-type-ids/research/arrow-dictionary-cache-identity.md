# Arrow dictionary cache identity audit

Date: 2026-08-06

Status: `AUDITED — NO DEFECT ESTABLISHED FOR A CONFORMING PRODUCER`

Public upstream contact remains unauthorized. This note records a investigated avenue that should not currently be promoted as a bug.

## Source pin

DuckDB source inspected at `58c019320e250a7b369efd756f84c6dfd68bedcb`.

Relevant code:

- `src/include/duckdb/function/table/arrow.hpp`
- `src/function/table/arrow/arrow_array_scan_state.cpp`
- `src/function/table/arrow_conversion.cpp`

## Initial concern

`ArrowArrayScanState::Reset()` intentionally retains the decoded dictionary across batches. Cache freshness is determined by pointer identity:

```cpp
if (dictionary == arrow_dictionary.get()) {
    return false;
}
```

At first glance, a producer that reuses an `ArrowArray` dictionary struct address with different buffers could cause DuckDB to reuse stale decoded values.

## Lifetime analysis

When DuckDB caches a dictionary, it adds `ArrowAuxiliaryData(owned_data)` to the cached dictionary vector. This retains the owning root `ArrowArrayWrapper`.

Under the Arrow C Data and C Stream lifetime contract, a producer may not mutate or recycle the array object or its buffers while the consumer still owns that returned array. Because DuckDB retains the prior root owner with the dictionary cache, a conforming producer cannot legally reuse the same live dictionary struct address for different contents.

Therefore, while the prior owner remains retained:

- same pointer means the same still-live dictionary object;
- a changed dictionary must arrive through a different object/pointer;
- allocator address reuse cannot occur until the prior object is released.

Pointer identity is consequently adequate for a conforming producer in this ownership model.

## Cases still worth testing

These are regression controls, not evidence of a current bug:

1. same immutable dictionary pointer across several batches;
2. different dictionary pointers with identical values;
3. replacement dictionary with different values and a different pointer;
4. nested dictionary inside list/struct across chunk boundaries;
5. dictionary cache destruction releases the owning root exactly once;
6. failed later batch does not release the cached prior dictionary prematurely.

## Nonconforming producer behavior

A producer that mutates a retained dictionary object or reuses its address before release violates Arrow ownership. DuckDB does not need to make that behavior work. A strict/debug validator could detect some mutations through a fingerprint, but adding production hashing solely to support invalid producers is not justified.

## Design caution

Any future refactor that removes the cached dictionary vector's root-owner auxiliary data would invalidate this conclusion. Pointer identity is safe here because identity and lifetime retention are coupled.

## Disposition

Do not route this as a defect. Preserve it as a reviewed losing avenue and use the test matrix if dictionary ownership is refactored.
