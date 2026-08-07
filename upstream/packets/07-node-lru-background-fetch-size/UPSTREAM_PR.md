# Upstream pull-request draft — fix: snapshot `backgroundFetchSize` before invoking user code

Draft status: `technically ready — public contact unauthorized`  
Proposed head: `teamleaderleo/node-lru-cache:repair/background-fetch-size-source` at `1191f6607d4df62bf302ce86cdc3287f9e2c57e0`  
Proposed base: `isaacs/node-lru-cache:main` at `16b3a916662ab449d496b7b4b4f04132565d1d28`

---

## Summary

- validate `backgroundFetchSize` as a primitive nonnegative integer without coercion;
- snapshot the missing-key provisional size before invoking user `fetchMethod`;
- preserve zero-size coalescing, explicit constructor `undefined`, stale refresh sizing, and no-size cache behavior.

## Problem

A missing-key background fetch is inserted as an internal promise and receives a provisional calculated size. Released `11.5.2` accepts invalid runtime `backgroundFetchSize` values into that accounting. `NaN`, infinity, negative or fractional values, and runtime strings can corrupt calculated size, break same-key coalescing, evict unrelated entries, or damage bookkeeping.

The field is public and mutable. `fetchMethod` runs synchronously while the internal Promise is constructed, before provisional insertion. Validation followed by a later public-field read therefore leaves a callback re-entry window.

## Change

- add a primitive nonnegative-integer guard that accepts zero and positive finite integers and short-circuits non-number values;
- validate constructor configuration after defaults, so explicit `undefined` retains omission semantics;
- before a missing-key fetch under active size tracking, validate and capture the current field value;
- attach the value to the internal `BackgroundFetch` promise;
- charge provisional accounting from the receipt and reject an absent or corrupt receipt;
- keep the receipt optional on the exported type for source compatibility.

The public field remains mutable. Mutation inside one provider callback applies to later operations, while the dispatched operation retains its captured charge. Stale refresh and no-size paths continue ignoring the field because they do not consume missing-key provisional size.

## Tests

The canonical source is one commit over the unchanged public base and has byte-identical changed-file blobs to reviewed head `5dce70a1765b6985244cd46325e011c19920dd80`.

Identical-tree evidence:

- focused run `30754588900`, job `91514469959` — build, 95/95 assertions, OXLint, Prettier, and diff hygiene passed before the later removal of one unrelated TTL-autopurge control;
- exact reviewed-tree Benchmarks `31010354657` — passed;
- exact reviewed-tree native CI `31010353969`:
  - Ubuntu Node 24/25 passed;
  - macOS Node 24/25 passed;
  - Windows Node 24/25 under Bash and PowerShell stopped before product tests because the unchanged repository configuration could not load `@tapjs/clock`.

The Windows coverage failure is present independently of the two-file candidate and is not repaired by adding package or lockfile churn to this change.

## Compatibility

- existing option and mutable field remain;
- invalid runtime values now throw `TypeError`;
- zero, positive integers, explicit constructor `undefined`, same-key coalescing, stale refresh, no-size caches, settlement, abort, replacement, and eviction behavior remain covered;
- one validation and one internal promise property are added per missing-key size-tracked fetch.

## Current public state

- public `main` remains at the exact inspected base;
- current GitHub issue and pull-request searches found no `backgroundFetchSize` overlap;
- `CONTRIBUTING.md` currently states only the neveragain.tech pledge request.

## Limits

- no green native Windows coverage suite is claimed;
- production prevalence remains unmeasured;
- the change addresses provisional accounting for this option only.

---

## Submission checklist

- [x] Exact source is one commit over the inspected public base.
- [x] Diff contains only `src/index.ts` and `test/background-fetch-size.ts`.
- [x] No workflow, dependency, lockfile, generated output, or Fieldwork file is present.
- [x] Focused build/test/lint/format gate passed on the identical relevant tree.
- [x] Exact reviewed-tree benchmarks passed.
- [x] Linux and macOS native matrices passed on the exact reviewed tree.
- [x] Windows native red is classified as unchanged-base TAP/coverage setup before product tests.
- [x] Complete-diff technical review accepted the identical source tree.
- [x] Public main and overlap search refreshed.
- [x] Current repository-specific contribution file checked.
- [ ] Final interaction text / AI-disclosure wording checked.
- [ ] Exact user authorization to interact publicly recorded.
