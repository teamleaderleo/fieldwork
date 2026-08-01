# Upstream pull-request draft — fix(utils): isolate JSON storage cache identity by key

Draft status: `not ready — direct source head and unit 21 sequencing required`  
Proposed head: `teamleaderleo/jotai:fix/utils-key-scoped-json-cache`  
Proposed base: `pmndrs/jotai:main` from `56a9cc51de8a5dd762b95a145820f12589cc47c9`  
Public interaction authorized: `no`

---

## Summary

- Scope `createJSONStorage()`'s parsed-value cache by storage key.
- Preserve unchanged same-key identity while preventing equal JSON under different keys from sharing one mutable object.
- Invalidate only the affected key for missing, malformed, and removal outcomes, with asynchronous publication ordering fenced in the final composed source candidate.

## Problem

`createJSONStorage()` currently keeps one `lastStr` and `lastValue` pair for the entire adapter. When one adapter serves different keys containing identical JSON, the second key reuses the first key's parsed value. Both callers receive the same mutable object.

The cache exists to preserve same-key identity during mount/subscription rereads, so removing memoization would regress historical behavior. Cache ownership needs to include the storage key.

## Change

Replace the adapter-wide cache pair with an adapter-local map keyed by storage key. Reads reuse a cached value only when both the key and serialized string match. Missing or malformed data removes only that key's entry. Removal invalidates the affected key while preserving the original storage result or error.

The final direct-source candidate should compose the accepted per-key read-generation fence so an older asynchronous completion cannot publish cache state after a newer read or completed removal. That mechanism is prepared separately and must appear in the exact submitted source head or be explicitly split with maintainer agreement.

## Tests

Focused source-candidate commands prepared from the retained receipts:

```text
pnpm vitest run \
  tests/react/vanilla-utils/atomWithStorageKeyIsolation.test.ts \
  tests/react/vanilla-utils/atomWithStorageReadInvalidation.test.ts \
  tests/react/vanilla-utils/atomWithStorageAsyncReadGenerationRepair.test.ts \
  tests/react/vanilla-utils/atomWithStorage.test.tsx
```

Required ordinary gates on the final direct source head:

```text
pnpm run fix:format
pnpm run build
pnpm run test
```

Retained focused evidence before direct materialization:

- unit 20 source and storage suites: 37 tests passed on Node 22, 24, and 26;
- changed-file ESLint and Prettier passed;
- `tsc --noEmit` passed;
- unit 21 generation repair has its own accepted target-executed receipt and must be revalidated on the composed direct source head.

## Compatibility

- public API: unchanged
- existing behavior retained: unchanged same-key JSON preserves parsed identity; original mount/subscription suite remains green
- platform or runtime notes: Node 22/24/26 focused matrix passed; browser and React Native final checks remain
- performance or allocation notes: one map entry per observed key until invalidation or adapter collection
- migration or rollback: no migration; revert restores adapter-wide cache behavior

## Alternatives considered

- Removing memoization breaks the historical same-key identity contract.
- A one-entry key-aware cache loses identity after unrelated-key reads.
- LRU eviction bounds memory but makes identity depend on unrelated-key activity and an arbitrary capacity.
- Explicit release/dispose authority widens the public lifecycle contract.
- Weak references provide no deterministic identity guarantee and cannot retain primitives.

## Limits

- Production frequency and practical retained-memory cost remain unmeasured.
- Read completion versus a later `setItem` remains a separate operation-ordering question.
- The current Fieldwork patch carrier is evidence, not the proposed upstream branch.

## Related work

- #1079 and PR #1080 established the same-key identity requirement.
- #1815 covers reset subscription propagation and is adjacent rather than equivalent.

---

## Submission checklist

- [ ] Writable owned fork and direct source branch exist.
- [ ] Branch is a clean child or rebase of a current upstream head.
- [ ] Unit 20 and the required unit 21 generation mechanism share one exact reviewed source head or have explicit maintainer-approved sequencing.
- [ ] Diff contains only product source and target-native tests.
- [ ] Fieldwork workflows, reports, receipts, and patch files are absent.
- [ ] Every changed file was reviewed at the exact proposed head.
- [ ] Focused baseline/candidate regressions ran.
- [ ] `pnpm run fix:format`, `pnpm run build`, and `pnpm run test` passed.
- [ ] Current duplicate and overlap search is complete.
- [x] Proposed title follows conventional commit style.
- [ ] Current contribution and AI-disclosure policies checked at filing time.
- [ ] Exact user authorization to open the public pull request recorded.
