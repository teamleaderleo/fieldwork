# Upstream pull-request draft — fix(utils): scope JSON cache by storage key

Draft status: `not ready — unit 20 source is clean and executed; final source sequencing with unit 21 remains`  
Proposed head: `teamleaderleo/jotai:fix/key-scoped-json-cache`  
Current unit 20 source head: `9fb2e455ed844d0fb248823009714ab5084d06fc`  
Proposed base: `pmndrs/jotai:main` from `56a9cc51de8a5dd762b95a145820f12589cc47c9`  
Public interaction authorized: `no`

---

## Summary

- Scope `createJSONStorage()`'s parsed-value cache by storage key.
- Preserve unchanged same-key identity while preventing equal JSON under different keys from sharing one mutable value.
- Invalidate only the affected key after removal terminal outcomes or unreadable storage observations.

## Problem

`createJSONStorage()` keeps one `lastStr` and `lastValue` pair for the whole adapter. When one adapter serves different keys containing identical JSON, the second key reuses the first key's parsed value. Both callers receive the same mutable object, so mutating one key's returned value can change another key's previously returned value without a storage write or subscription event.

The cache exists to preserve same-key identity during mount and subscription rereads. Removing memoization would regress that historical behavior. Cache ownership needs to include the storage key.

## Change

Replace the adapter-wide cache pair with an adapter-local map keyed by storage key.

- Reads reuse a value only when both the key and serialized string match.
- Equal JSON under another key parses independently.
- Missing or malformed data deletes only the affected key's entry.
- Removal preserves identity while an asynchronous removal is pending, then invalidates the affected key on every terminal outcome while preserving the original result or error.
- Public types and caller APIs remain unchanged.

This unit intentionally leaves asynchronous completion publication ordering to the separately reviewed generation-fence successor. The final upstream delivery should either compose that successor on one exact source head or use an explicitly reviewed stack.

## Tests

Executed on owned-fork carrier head `ac5dd98da6c3083f31560b71d84ad3bf850aaafc`:

```text
pnpm install --frozen-lockfile
pnpm vitest run \
  tests/react/vanilla-utils/atomWithStorageKeyIsolation.test.ts \
  tests/react/vanilla-utils/atomWithStorageReadInvalidation.test.ts \
  tests/react/vanilla-utils/atomWithStorage.test.tsx
pnpm eslint \
  src/vanilla/utils/atomWithStorage.ts \
  tests/react/vanilla-utils/atomWithStorageKeyIsolation.test.ts \
  tests/react/vanilla-utils/atomWithStorageReadInvalidation.test.ts
pnpm prettier --check \
  src/vanilla/utils/atomWithStorage.ts \
  tests/react/vanilla-utils/atomWithStorageKeyIsolation.test.ts \
  tests/react/vanilla-utils/atomWithStorageReadInvalidation.test.ts
pnpm tsc --noEmit
pnpm run build
```

Results:

- Node 22: 37 tests, ESLint, Prettier, TypeScript, and complete build passed;
- Node 24: 37 tests, ESLint, Prettier, TypeScript, and complete build passed;
- Node 26: 37 tests, ESLint, Prettier, TypeScript, and complete build passed.

The current clean head removes the one-off workflow and every execution note. Its diff contains only the production source and two target-native test files. Native clean-head workflows were queued at the latest packet update.

## Compatibility

- public API: unchanged;
- existing behavior retained: unchanged same-key JSON preserves parsed identity and the historical mount/subscription suite remains green;
- synchronous and asynchronous string storage: covered in focused tests;
- custom reviver: covered;
- platform/runtime: Node 22/24/26 direct-source matrix passed;
- browser and React Native: unexecuted;
- allocation: one cache entry per observed key until affected-key invalidation or adapter collection;
- migration: none;
- rollback: revert the source and two tests.

## Alternatives considered

- Removing memoization breaks historical same-key identity behavior.
- A one-entry key-aware cache loses identity after unrelated-key reads.
- LRU eviction makes identity depend on unrelated-key activity and an arbitrary capacity.
- Explicit release or disposal widens caller lifecycle authority.
- Weak references provide no deterministic identity contract and cannot retain primitive parsed values.

## Limits

- A stale asynchronous read completion can publish after a newer read or completed removal; the accepted generation-fence successor owns that correction.
- Read completion versus a later `setItem` remains a separate operation-ordering question.
- Production frequency and practical retained-memory cost remain unmeasured.
- Public upstream acceptance has not been tested or requested.

## Related work

- Jotai issue #1079 and PR #1080 established same-key identity reuse during mount/subscription setup.
- Jotai issue #1815 covers reset subscription propagation and is adjacent rather than equivalent.

---

## Submission checklist

- [x] Writable owned fork and direct source branch exist.
- [x] Branch is a clean child of the exact selected upstream base.
- [x] Unit 20 diff contains only product source and target-native tests.
- [x] Temporary workflows, reports, receipts, and execution notes are absent from the current source head.
- [x] Focused baseline/candidate regressions ran.
- [x] Changed-file ESLint and Prettier passed.
- [x] Repository TypeScript checking passed.
- [x] Complete build passed on Node 22/24/26.
- [ ] Clean-head native workflow generation settled and classified.
- [ ] Independent complete-diff review recorded at `9fb2e455...`.
- [ ] Unit 20 and unit 21 share one exact reviewed final source head or an explicit reviewed stack.
- [ ] Current duplicate and overlap search repeated immediately before filing.
- [x] Proposed title follows conventional commit style.
- [ ] Current contribution and AI-disclosure policies checked at filing time.
- [ ] Exact user authorization to open the public pull request recorded.
