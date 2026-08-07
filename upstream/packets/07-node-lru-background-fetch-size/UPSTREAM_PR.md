# Upstream pull-request draft — `backgroundFetchSize` snapshot

Draft status: `ready for owner copy/paste review — no upstream post performed`  
Proposed title: `fix: snapshot backgroundFetchSize before invoking user code`  
Proposed head: `teamleaderleo/node-lru-cache:repair/background-fetch-size-source` at `1191f6607d4df62bf302ce86cdc3287f9e2c57e0`  
Proposed base: `isaacs/node-lru-cache:main` at `16b3a916662ab449d496b7b4b4f04132565d1d28`  
Compare / create-PR page: https://redirect.github.com/isaacs/node-lru-cache/compare/main...teamleaderleo:repair/background-fetch-size-source?expand=1

---

## Copy/paste PR body

### Summary

`backgroundFetchSize` is used as the provisional size of a missing-key background fetch while that fetch is still pending.

Today the value can be read after `fetchMethod` has already started running synchronously. Because `backgroundFetchSize` is public and mutable, callback code can change the value between dispatch and provisional accounting. Invalid runtime values such as `NaN`, infinities, negative/fractional numbers, or non-number values can also reach that accounting path.

This change:

- validates `backgroundFetchSize` as a primitive nonnegative integer;
- captures the missing-key provisional size before invoking `fetchMethod`;
- stores that operation-local value on the internal background fetch;
- uses the captured value for provisional accounting instead of rereading the mutable public field.

### Behavior

A mutation performed by one `fetchMethod` call can still affect later fetches, but it cannot change the provisional charge of the fetch that is already in progress.

The existing behavior is preserved for:

- `backgroundFetchSize: 0` and same-key in-flight coalescing;
- stale refreshes, which continue using the existing entry size;
- caches without size tracking, where later `backgroundFetchSize` mutation is irrelevant;
- normal settlement, replacement, abort, and eviction paths.

One intentional validation change is that an explicitly invalid `backgroundFetchSize` now throws `TypeError` at construction, even if that cache is not currently using size tracking. This treats an invalid supplied option as a configuration error rather than deferring validation until the value is consumed.

### Tests

The added coverage checks:

- invalid numeric and non-number values, including hostile objects that must not be coerced;
- invalid post-construction mutation rejecting before provider dispatch;
- synchronous `fetchMethod` mutation not changing the current operation's captured size;
- valid mutation applying to the next operation;
- zero-size coalescing;
- stale-refresh and no-size-cache behavior;
- defensive rejection of a missing/corrupt internal provisional-size receipt.

Fork CI passes on Ubuntu and macOS for Node 24 and 25. The Windows lanes stop before product test discovery because the repository TAP configuration references unavailable `@tapjs/clock`; the same harness failure is reproducible on the unchanged base.

---

## Internal submission notes — do not paste upstream

### Procedure

- Direct PR is the idiomatic route for this repository; no issue-first step is needed for this bounded bug fix.
- Current `CONTRIBUTING.md` states only the neveragain.tech pledge request.
- No repository-specific CLA, DCO, `Signed-off-by`, cryptographic commit-signing, changeset/changelog, or AI-assistance trailer requirement was found.
- Maintainer guidance on PR #392 explicitly welcomed a bug report submitted as a test plus fixing patch.
- No extra source comments are recommended. The existing ordering comment explains the non-obvious invariant; the JSDoc sentence documents the newly enforced public option contract.

### Exact source state

- canonical head: `1191f6607d4df62bf302ce86cdc3287f9e2c57e0`;
- relation to public base: ahead 1 / behind 0;
- changed files: `src/index.ts`, `test/background-fetch-size.ts` only;
- no dependency, lockfile, workflow, generated-output, or Fieldwork file in the source diff;
- changed-file blobs are byte-identical to reviewed tree `5dce70a1765b6985244cd46325e011c19920dd80`:
  - `src/index.ts`: `c3549a638b84ce096b13ebd7e3f71496dbe5afd5`;
  - `test/background-fetch-size.ts`: `ce5f70eac6ed995361fe55ddc9b445f85fcbd07a`.

### Evidence boundary

- focused identical-tree gate: build, 95/95 assertions, OXLint, Prettier, and diff hygiene passed;
- current exact-head CI: Ubuntu Node 24/25 passed; macOS Node 24/25 passed; Windows Node 24/25 Bash/PowerShell stopped in the same pre-test `@tapjs/clock` harness failure;
- current exact-head benchmark run `31201645066` is queued at this edit and is not claimed as passed;
- prior benchmark run on the byte-identical reviewed tree passed;
- current public `main` remains at the exact base and the latest overlap search found no `backgroundFetchSize` issue or PR.

### Owner posting boundary

The repository owner will perform any public submission manually. Fieldwork/assistant work must not create the upstream PR, issue, comment, review, reaction, or other public interaction.
