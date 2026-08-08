# Upstream pull-request draft — `backgroundFetchSize` snapshot

Draft status: `ready for owner copy/paste review — no upstream post performed`  
Proposed title: `fix: snapshot backgroundFetchSize before invoking user code`  
Proposed head: `teamleaderleo/node-lru-cache:repair/background-fetch-size-source` at `4a80ff2cec44d259907e474336a64ec984a465a5`  
Proposed base: `isaacs/node-lru-cache:main` at `16b3a916662ab449d496b7b4b4f04132565d1d28`  
Compare / create-PR page: https://redirect.github.com/isaacs/node-lru-cache/compare/main...teamleaderleo:repair/background-fetch-size-source?expand=1

---

## Copy/paste PR body

### Summary

`backgroundFetchSize` is used to account for a background fetch while its value is still pending.

Unlike normal cache sizes, it currently bypasses the usual size validation. Invalid values such as negative numbers, fractions, `NaN`, or `Infinity` can therefore reach the cache's size accounting.

There's also a timing issue when `fetchMethod` changes `backgroundFetchSize` synchronously. The current fetch can end up using the new value even though it started with the old one.

This change validates `backgroundFetchSize` and snapshots it before calling `fetchMethod`, so each in-flight fetch keeps the size it started with. `0` remains valid, and changes to `backgroundFetchSize` still apply to later fetches.

### Tests

Added coverage for:

- invalid `backgroundFetchSize` values;
- rejecting invalid runtime values without coercing them;
- mutation from inside `fetchMethod`;
- mutations applying to later, but not already-running, fetches;
- `backgroundFetchSize: 0`;
- stale refreshes and caches without size tracking;
- invalid internal provisional-size state.

The existing `test/background-fetch-size.ts` test file and TAP clock setup are preserved.

Linux and macOS CI passed for the same production change. The Windows jobs stop before test discovery because the repository's TAP configuration references an unavailable `@tapjs/clock` plugin.

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
