# Upstream pull-request draft — fix: snapshot backgroundFetchSize before invoking user code

Draft status: `not ready — exact-head gates and independent review pending`  
Proposed head: `teamleaderleo/node-lru-cache:repair/background-fetch-size-source`  
Proposed base: `isaacs/node-lru-cache:main` at `16b3a916662ab449d496b7b4b4f04132565d1d28`  
Public interaction authorized: `no`

---

## Summary

- validate `backgroundFetchSize` as a primitive nonnegative integer;
- snapshot the missing-key provisional size before invoking user `fetchMethod`;
- preserve zero-size coalescing, stale refresh sizing, and no-size cache behavior.

## Problem

A missing-key background fetch is inserted as an internal promise and receives a provisional calculated size. Released `11.5.2` accepts invalid runtime `backgroundFetchSize` values into that accounting. Values such as `NaN`, infinity, negative or fractional numbers, and runtime strings can corrupt calculated size, break same-key coalescing, or damage cache bookkeeping.

The field is public and mutable. `fetchMethod` runs synchronously while the internal Promise is constructed, before the provisional promise is inserted. Validation followed by a later read of the public field leaves a callback re-entry window.

## Change

- add a primitive nonnegative-integer guard that accepts zero and positive finite integers;
- validate constructor configuration;
- before a missing-key fetch dispatch under active size tracking, validate and capture the current field value;
- store the captured value on the internal `BackgroundFetch` promise;
- charge provisional accounting from that receipt and reject an absent or corrupt receipt;
- declare the receipt optional on the exported `BackgroundFetch` type to preserve source compatibility for typed mocks and adapters.

The public field remains mutable. Mutation inside one provider callback applies to later operations, while the already-dispatched operation retains its captured charge.

## Tests

- `npm test -- -c -t0`
- `npm run benchmark`
- native `test/background-fetch-size.ts` controls:
  - invalid constructor values;
  - invalid public mutation before dispatch with zero provider calls and unchanged state;
  - synchronous callback mutation after validation;
  - valid mutation applying to the next fetch only;
  - zero-size same-key coalescing;
  - stale and no-size compatibility;
  - pending-to-settled size transition;
  - corrupted internal receipt rejection;
  - autopurge reschedule branch coverage.

## Compatibility

- public API: existing option and mutable field remain; invalid runtime values now throw `TypeError`;
- existing behavior retained: zero, positive integers, same-key coalescing, stale refresh size, no-size caches, settlement, abort and eviction paths;
- platform or runtime notes: ordinary repository CI spans Node 24/25 on Linux, macOS, and Windows; benchmark matrix spans Node 22/24/25;
- performance or allocation notes: one validation and one internal property per missing-key size-tracked fetch;
- migration or rollback: callers supplying invalid runtime values must provide zero or a positive finite integer; rollback is one commit.

## Alternatives considered

- constructor-only validation leaves the synchronous callback mutation window;
- re-reading the public field during insertion leaves current-operation accounting mutable;
- making the field immutable widens public API compatibility;
- coercing dynamic values would admit strings, booleans, objects, or hostile conversion hooks;
- adding a clock test dependency widens the patch without product value.

## Limits

- production prevalence remains unmeasured;
- the change addresses this option’s provisional accounting only;
- benchmark results are used as a regression gate, without a performance claim.

## Related work

- `backgroundFetchSize` introduction: commit `4708153206daf822a3ad440ce47248b9cfbdb973`
- autopurge reschedule behavior covered by the native suite: commit `0b0a77e99245e12c53ec0cf05e200c66e6749ba9`
- current duplicate search on 2026-08-01 found no matching upstream issue or pull request.

---

## Submission checklist

- [x] Branch is a direct child of public commit `16b3a916662ab449d496b7b4b4f04132565d1d28`.
- [x] Diff contains only `src/index.ts` and `test/background-fetch-size.ts`.
- [x] Fieldwork wording, temporary workflows, publishers, receipts, and evidence-only files are absent.
- [x] Every changed file was reviewed at exact proposed head `0f4a357a9bc0b09ad413e99fa566317bf4ce283c`.
- [x] Baseline negative controls and candidate compatibility controls are retained.
- [ ] Exact-head ordinary CI passes.
- [ ] Exact-head benchmarks pass.
- [x] Current duplicate and overlap search is complete as of 2026-08-01.
- [x] Commit title follows the target’s imperative style.
- [ ] Target contribution and AI-disclosure policies checked again at filing time.
- [ ] Exact user authorization to open a public pull request recorded.
