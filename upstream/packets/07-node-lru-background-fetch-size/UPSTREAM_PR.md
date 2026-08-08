# Upstream pull-request draft — `backgroundFetchSize` snapshot

Draft status: `ready for owner copy/paste review — no upstream post performed`  
Proposed title: `fix: snapshot backgroundFetchSize before invoking user code`  
Proposed head: `teamleaderleo/node-lru-cache:repair/background-fetch-size-source` at `364a8c1c07c9f6281fbe19943eacd261bd410fc4`  
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
- stale refreshes and caches without size tracking.

The existing `test/background-fetch-size.ts` test file and TAP clock setup are preserved.

Linux and macOS CI passed for the same production change. The Windows jobs stop before test discovery because the repository's TAP configuration references an unavailable `@tapjs/clock` plugin.

---

## Internal submission notes — do not paste upstream

### Regression scope

The final test suite is intentionally limited to supported behavior and realistic regression boundaries.

A previous test imported the exported `BackgroundFetch` type, reached through `unsafeExposeInternals()`, changed the hidden `__size` receipt to `NaN`, and reinserted that internal Promise through `set()`. That test was removed. The repository's own documentation warns that mutating values returned by `unsafeExposeInternals()` may cause strange breakage, so malformed private state isn't part of the supported contract this PR needs to promise.

The accounting boundary still validates the stored receipt defensively. That guard is cheap protection against an impossible/malformed internal state, but it doesn't need a dedicated public-behavior regression test.

The remaining added tests each protect a distinct contract:

- constructor validation of the option's numeric domain and representative non-number values;
- non-coercion of hostile runtime input;
- validation of post-construction mutation before provider dispatch;
- snapshotting before synchronous `fetchMethod` mutation, including later-operation behavior and same-key coalescing;
- no-size caches ignoring an irrelevant mutated option;
- stale refreshes continuing to use the existing entry size;
- zero-size background fetches remaining coalesced.

### Test placement / style check

Repository convention has two relevant patterns:

- broad constructor-option validation appears in `test/basic.ts`;
- feature-specific behavior lives in dedicated files, and upstream itself introduced `test/background-fetch-size.ts` with this option.

Keeping the closely related constructor and runtime regressions together in the existing feature file avoids adding a third changed file and keeps review focused.

### Why this hole existed

`backgroundFetchSize` was added in 11.5 by commit `4708153206daf822a3ad440ce47248b9cfbdb973`.

Before that change, background-fetch placeholders were a special case in `#requireSize()` and simply returned provisional size `0`. Version 11.5 changed that special-case return to `this.backgroundFetchSize` without adding the normal size guard around the new option.

### Why not use only `isPosInt()`

The repository already has `isPosInt()` for ordinary positive size/count contracts. `backgroundFetchSize` is different because `0` is useful and supported.

The new nonnegative wrapper first requires a primitive number, then accepts zero or delegates positive values to `isPosInt()`. That type-first check also avoids invoking caller conversion hooks merely to reject an invalid runtime value.

### Final source state

- canonical head: `364a8c1c07c9f6281fbe19943eacd261bd410fc4`;
- one commit over the exact public base;
- exactly two files;
- `src/index.ts`: +33 / -1;
- `test/background-fetch-size.ts`: +160 / -0;
- total: +193 / -1;
- source blob: `c3549a638b84ce096b13ebd7e3f71496dbe5afd5`;
- test blob: `a83968f5110bfe42cfe32aae55cb6018aba6aebd`;
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
- final exact-head CI `31231433021`: queued at this edit;
- final exact-head Benchmarks `31231433009`: queued at this edit;
- no exact-head success is claimed until those execute;
- Windows `@tapjs/clock` failure remains an unchanged-base repository harness limit, not repaired in this contribution.

### Owner posting boundary

The repository owner will perform any public submission manually. Fieldwork/assistant work must not create the upstream PR, issue, comment, review, reaction, or other public interaction.
