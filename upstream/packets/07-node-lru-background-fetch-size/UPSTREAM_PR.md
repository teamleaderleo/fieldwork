# Upstream pull-request draft — `backgroundFetchSize` snapshot

Draft status: `ready for owner copy/paste review — no upstream post performed`  
Proposed title: `fix: snapshot backgroundFetchSize before invoking user code`  
Proposed head: `teamleaderleo/node-lru-cache:repair/background-fetch-size-source` at `4a80ff2cec44d259907e474336a64ec984a465a5`  
Proposed base: `isaacs/node-lru-cache:main` at `16b3a916662ab449d496b7b4b4f04132565d1d28`  
Compare / create-PR page: https://redirect.github.com/isaacs/node-lru-cache/compare/main...teamleaderleo:repair/background-fetch-size-source?expand=1

---

## Copy/paste PR body

### Summary

`backgroundFetchSize` is the provisional size used for a missing-key background fetch while the real value is still pending.

The option was added as a special case inside the normal size-validation path. Ordinary item sizes are checked as positive integers, but a background-fetch placeholder can return `backgroundFetchSize` directly from that exception. As a result, invalid runtime values can reach cache accounting without the normal size check.

There is also a re-entry window: `fetchMethod` starts running synchronously before the placeholder is inserted. Because `backgroundFetchSize` is public and mutable, callback code can change it before provisional accounting reads it.

This change:

- accepts `0` and positive finite integers for `backgroundFetchSize`;
- rejects negative, fractional, non-finite, and representative non-number values without coercing caller objects;
- captures the missing-key provisional size before invoking `fetchMethod`;
- stores that operation-local value on the internal background fetch;
- uses the captured value for provisional accounting instead of rereading the mutable public field.

### Behavior

`0` remains supported: an in-flight fetch can occupy a cache slot while contributing zero provisional calculated size, and same-key callers still coalesce onto the same fetch.

A mutation performed by one `fetchMethod` call can still affect later fetches, but it cannot change the provisional charge of the fetch already in progress.

Existing behavior is preserved for stale refreshes, caches without size tracking, normal settlement, replacement, abort, and eviction paths.

One intentional validation choice is visible for review: an explicitly invalid `backgroundFetchSize` now throws `TypeError` at construction even when that particular cache is not currently using size tracking. The essential correctness fix is the validation/snapshot at the missing-key size-tracked fetch boundary; constructor fail-fast behavior can be narrowed if preferred.

### Tests

Coverage stays in the existing `test/background-fetch-size.ts` feature test and preserves its TAP clock setup.

The added cases cover:

- negative, fractional, `NaN`, and infinite values;
- runtime string/symbol values and a hostile object that must not be coerced;
- invalid post-construction mutation rejecting before provider dispatch;
- synchronous `fetchMethod` mutation not changing the current operation's captured size;
- valid mutation applying to later operations;
- zero-size coalescing;
- stale-refresh and no-size-cache behavior;
- defensive rejection of a corrupt internal provisional-size receipt.

Fresh CI and benchmarks for the final exact head are currently queued. The production logic is unchanged from the previously reviewed tree, which passed the focused behavioral gate, Ubuntu/macOS native CI, and benchmarks. The known Windows native lanes stop before product test discovery because the unchanged repository TAP configuration references unavailable `@tapjs/clock`.

---

## Internal submission notes — do not paste upstream

### Test placement / style check

Repository convention has two relevant patterns:

- broad constructor-option validation appears in `test/basic.ts` (for example TTL/maxSize validation);
- feature-specific behavior lives in dedicated files such as `test/size-calculation.ts`, and upstream itself introduced `test/background-fetch-size.ts` with this option.

Keeping the `backgroundFetchSize` constructor and behavior regressions together in the dedicated feature file avoids expanding the contribution to a third file for one closely related check. This is the better ownership/scope tradeoff here.

The earlier test matrix enumerated many redundant JavaScript types. It has been reduced to representative cases that each prove a distinct invariant. The final test delta is +190 / -1 instead of +269 / -1.

### Why this hole existed

`backgroundFetchSize` was added in 11.5 by commit `4708153206daf822a3ad440ce47248b9cfbdb973`.

Before that change, background-fetch placeholders were a special case in `#requireSize()` and simply returned provisional size `0`. Version 11.5 moved the special case inside the invalid-explicit-size branch and changed the returned provisional value from `0` to `this.backgroundFetchSize`.

That direct return never passes through the normal positive-integer validator used for explicit sizes and `sizeCalculation()` results. The option therefore inherited the background-fetch exception but not the surrounding size invariant.

### Why not use only `isPosInt()`

The repository already has `isPosInt()` for ordinary positive size/count contracts. `backgroundFetchSize` is intentionally different because `0` is useful and supported.

The new nonnegative wrapper first requires `typeof value === "number"`, then accepts zero or delegates positive values to `isPosInt()`. The type-first check matters because the property is public and mutable at runtime: JavaScript callers can assign symbols or objects even though TypeScript declares `number`. This avoids invoking conversion hooks merely to reject an invalid value.

### Final source state

- canonical head: `4a80ff2cec44d259907e474336a64ec984a465a5`;
- one commit over the exact public base;
- exactly two files;
- `src/index.ts`: +33 / -1;
- `test/background-fetch-size.ts`: +190 / -1;
- total: +223 / -2;
- no dependency, lockfile, workflow, snapshot, generated-output, or Fieldwork file.

The repository's original `t.clock` setup remains unchanged.

### Procedure

- Direct PR is the idiomatic route; no issue-first step is needed for this bounded bug fix.
- Current `CONTRIBUTING.md` states only the neveragain.tech pledge request.
- No repository-specific CLA, DCO, `Signed-off-by`, cryptographic commit-signing, changeset/changelog, or AI-assistance trailer requirement was found.
- Maintainer guidance on PR #392 explicitly welcomed a bug report submitted as a test plus fixing patch.

### Evidence boundary

- production source is unchanged from the previously reviewed candidate;
- prior focused production-tree gate, Ubuntu/macOS native CI, and benchmarks passed;
- final exact-head CI `31227785209`: queued at this edit;
- final exact-head Benchmarks `31227785205`: queued at this edit;
- no exact-head success is claimed until those execute;
- Windows `@tapjs/clock` failure remains an unchanged-base repository harness limit, not repaired in this contribution.

### Owner posting boundary

The repository owner will perform any public submission manually. Fieldwork/assistant work must not create the upstream PR, issue, comment, review, reaction, or other public interaction.
