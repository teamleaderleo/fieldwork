# Upstream pull-request draft — fix: snapshot backgroundFetchSize before invoking user code

Draft status: `not ready — exact-head gates and independent review pending`  
Proposed head: `teamleaderleo/node-lru-cache:repair/background-fetch-size-source`  
Proposed base: `isaacs/node-lru-cache:main` at `16b3a916662ab449d496b7b4b4f04132565d1d28`  
Public interaction authorized: `no`

---

## Summary

- validate `backgroundFetchSize` as a primitive nonnegative integer without coercion;
- snapshot the missing-key provisional size before invoking user `fetchMethod`;
- preserve zero-size coalescing, constructor/default `undefined`, stale refresh sizing, and no-size cache behavior.

## Problem

A missing-key background fetch is inserted as an internal promise and receives a provisional calculated size. Released `11.5.2` accepts invalid runtime `backgroundFetchSize` values into that accounting. Values such as `NaN`, infinity, negative or fractional numbers, and runtime strings can corrupt calculated size, break same-key coalescing, or damage cache bookkeeping.

The field is public and mutable. `fetchMethod` runs synchronously while the internal Promise is constructed, before the provisional promise is inserted. Validation followed by a later read of the public field leaves a callback re-entry window.

## Change

- add a primitive nonnegative-integer guard that accepts zero and positive finite integers and short-circuits every non-number value;
- validate constructor configuration after option defaults, so explicit `undefined` retains omission semantics;
- before a missing-key fetch dispatch under active size tracking, validate and capture the current field value;
- store the captured value on the internal `BackgroundFetch` promise;
- charge provisional accounting from that receipt and reject an absent or corrupt receipt;
- declare the receipt optional on the exported `BackgroundFetch` type to preserve source compatibility for external mocks and adapters.

The public field remains mutable. Mutation inside one provider callback applies to later operations, while the already-dispatched operation retains its captured charge. Stale refresh and no-size paths continue ignoring the field because they do not consume missing-key provisional size.

## Tests

- `npm test -- -c -t0`
- `npm run benchmark`
- `npm run prepare`
- `npx tap --disable-coverage test/background-fetch-size.ts`
- `npx oxlint src/index.ts test/background-fetch-size.ts`
- `npx prettier --check src/index.ts test/background-fetch-size.ts`
- native controls:
  - labeled invalid constructor values;
  - hostile object with throwing conversion hooks;
  - constructor/default `undefined` and post-construction invalid `undefined`;
  - invalid public mutation before dispatch with zero provider calls and unchanged state;
  - synchronous callback mutation after validation;
  - valid mutation applying to the next fetch only;
  - invalid field ignored for stale refresh and no-size cache;
  - zero-size same-key coalescing;
  - pending-to-settled size transition;
  - corrupted internal receipt rejection;
  - autopurge reschedule branch coverage.

Current exact-head runs:

- native CI `30674843003`;
- native Benchmarks `30674842990`;
- focused build/OXLint/Prettier carrier `30674901995`.

## Compatibility

- public API: existing option and mutable field remain; invalid runtime values now throw `TypeError`;
- existing behavior retained: zero, positive integers, explicit constructor `undefined`, same-key coalescing, stale refresh size, no-size caches, settlement, abort, replacement, and eviction paths;
- source compatibility: `BackgroundFetch.__size` is optional on the exported type;
- platform or runtime notes: ordinary repository CI spans Node 24/25 on Linux, macOS, and Windows; benchmark matrix spans Node 22/24/25; focused carrier spans Node 22/24/26 on Ubuntu;
- performance or allocation notes: one validation and one internal property per missing-key size-tracked fetch;
- migration or rollback: callers supplying invalid runtime values must provide zero or a positive finite integer; rollback is one commit.

## Alternatives considered

- constructor-only validation leaves the synchronous callback mutation window;
- re-reading the public field during insertion leaves current-operation accounting mutable;
- making the field immutable widens public API compatibility;
- validating every fetch path would reject values that stale/no-size paths never consume;
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
- [x] Exact proposed head is `70a9e62b0555e6bb68763fb9d32458fa82fd2a70`.
- [x] Diff contains only `src/index.ts` and `test/background-fetch-size.ts`.
- [x] Fieldwork wording, temporary workflows, publishers, receipts, and evidence-only files are absent from the target diff.
- [x] Every changed file was self-reviewed at the exact proposed head.
- [x] Baseline negative controls and candidate compatibility controls are retained.
- [ ] Exact-head ordinary CI passes.
- [ ] Exact-head benchmarks pass.
- [ ] Exact-head build/focused/OXLint/Prettier carrier passes.
- [x] Current duplicate and overlap search is complete as of 2026-08-01.
- [x] Commit title follows the target’s imperative style.
- [ ] Independent complete-diff review accepts the source and test reachability.
- [ ] Target contribution and AI-disclosure policies checked again at filing time.
- [ ] Exact user authorization to open a public pull request recorded.
