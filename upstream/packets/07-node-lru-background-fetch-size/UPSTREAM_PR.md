# Upstream pull-request record — `backgroundFetchSize` snapshot

Submission status: `submitted manually by owner`  
Upstream pull request: [isaacs/node-lru-cache#410](https://redirect.github.com/isaacs/node-lru-cache/pull/410)  
Title: `fix: snapshot backgroundFetchSize before invoking user code`  
Submitted head: `teamleaderleo/node-lru-cache:repair/background-fetch-size-source` at `364a8c1c07c9f6281fbe19943eacd261bd410fc4`  
Base at submission: `isaacs/node-lru-cache:main` at `16b3a916662ab449d496b7b4b4f04132565d1d28`

---

## Submitted PR body

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
- stale refreshes and caches without size tracking.

---

## Internal submission notes

### Regression scope

The submitted test suite is intentionally limited to supported behavior and realistic regression boundaries.

A previous test imported the exported `BackgroundFetch` type, reached through `unsafeExposeInternals()`, changed the hidden `__size` receipt to `NaN`, and reinserted that internal Promise through `set()`. That test was removed. The repository's own documentation warns that mutating values returned by `unsafeExposeInternals()` may cause strange breakage, so malformed private state is not part of the supported contract this PR needs to promise.

The accounting boundary still validates the stored receipt defensively. That guard is cheap protection against an impossible or malformed internal state, but it does not need a dedicated public-behavior regression test.

The remaining added tests each protect a distinct contract:

- constructor validation of the option's numeric domain and representative non-number values;
- non-coercion of hostile runtime input;
- validation of post-construction mutation before provider dispatch;
- snapshotting before synchronous `fetchMethod` mutation, including later-operation behavior and same-key coalescing;
- no-size caches ignoring an irrelevant mutated option;
- stale refreshes continuing to use the existing entry size;
- zero-size background fetches remaining coalesced.

### Why this hole existed

`backgroundFetchSize` was added in 11.5 by commit `4708153206daf822a3ad440ce47248b9cfbdb973`.

Before that change, background-fetch placeholders were a special case in `#requireSize()` and simply returned provisional size `0`. Version 11.5 changed that special-case return to `this.backgroundFetchSize` without adding the normal size guard around the new option.

### Final source state

- canonical/submitted head: `364a8c1c07c9f6281fbe19943eacd261bd410fc4`;
- one commit over the exact public base;
- exactly two files;
- `src/index.ts`: +33 / -1;
- `test/background-fetch-size.ts`: +160 / -0;
- total: +193 / -1;
- source blob: `c3549a638b84ce096b13ebd7e3f71496dbe5afd5`;
- test blob: `a83968f5110bfe42cfe32aae55cb6018aba6aebd`;
- no dependency, lockfile, workflow, snapshot, generated-output, or Fieldwork file.

### Evidence boundary

- prior focused production-tree gate, Ubuntu/macOS native CI, and benchmarks passed for the unchanged production logic;
- submitted-head fork CI `31231433021` remains queued at this record update;
- submitted-head Benchmarks `31231433009` remains queued at this record update;
- no exact submitted-head green claim is made until those runs execute;
- Windows `@tapjs/clock` failure remains an unchanged-base repository harness limit, not repaired in this contribution.

### Public interaction boundary

The owner created upstream PR #410 manually. The assistant did not create it. No additional upstream issue, comment, review, reaction, merge, release, or other public interaction is authorized without explicit owner direction for that exact action.
