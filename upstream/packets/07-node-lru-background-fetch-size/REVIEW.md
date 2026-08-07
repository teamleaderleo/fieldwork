# Review — Unit 07 `backgroundFetchSize` snapshot

## Review subject

- source PR: `teamleaderleo/node-lru-cache#2`;
- base: `16b3a916662ab449d496b7b4b4f04132565d1d28`;
- canonical head: `1191f6607d4df62bf302ce86cdc3287f9e2c57e0`;
- reviewed identical-tree head: `5dce70a1765b6985244cd46325e011c19920dd80`;
- fence: `src/index.ts`, `test/background-fetch-size.ts`;
- canonical relation: ahead 1, behind 0.

The canonical one-commit head is a history-only collapse. Both changed-file blob SHAs are identical to the reviewed head, so no source or test bytes changed.

## Source findings

No blocking source defect remains.

- `isNonNegativeInt()` checks primitive number type before the existing positive-integer helper, so symbols, objects, and hostile conversion hooks are never coerced.
- constructor default `1`, explicit zero, and positive integers remain valid; explicit `undefined` keeps omission/default behavior.
- the missing-key receipt is captured before the Promise executor invokes user `fetchMethod` synchronously.
- stale refresh continues to use the existing entry size and does not consume the provisional receipt.
- caches without size tracking remain insensitive to later irrelevant field mutation.
- `BackgroundFetch.__size` is optional in the exported type, while the internal accounting boundary rejects an absent or corrupt receipt.
- the two-file diff contains no workflow, dependency, lockfile, generated output, or unrelated source change.

## Execution reviewed

For the identical reviewed tree:

- focused run `30754588900`, job `91514469959`: 95/95 assertions, build, OXLint, Prettier, diff hygiene — success; the final tree removed only the unrelated TTL-autopurge control from that file;
- exact reviewed-tree benchmarks `31010354657` — success;
- exact reviewed-tree native CI `31010353969`:
  - Ubuntu Node 24/25 — success;
  - macOS Node 24/25 — success;
  - Windows Node 24/25 Bash/PowerShell — stopped before product tests because the unchanged repository configuration requests missing `@tapjs/clock`.

The Windows logs under both shells are identical at the ownership boundary: package installation/build succeeds, then Tap fails to load the plugin before collecting candidate assertions. A separate base/candidate harness comparison classifies this as unchanged-base coverage behavior.

The canonical head carries these receipts by exact blob identity rather than by claiming that its new commit SHA executed them.

## Fresh public-state check

- public `isaacs/node-lru-cache` latest commit remains the candidate base `16b3a916662ab449d496b7b4b4f04132565d1d28`;
- GitHub searches found no issue or pull request overlap for `backgroundFetchSize`;
- current `CONTRIBUTING.md` contains only the neveragain.tech pledge request.

## Evidence limits

- no green native Windows coverage suite is claimed;
- production prevalence remains unknown;
- constructor-wide eager validation remains a public-contract choice, though it is internally coherent and covered;
- maintainer preference can still differ from the selected API contract.

## Disposition

`ACCEPT / TECHNICALLY READY`

The source can advance to owner review and authorized upstream preparation. Public interaction still requires explicit user authorization and a final interaction-text/disclosure check. No public upstream interaction has occurred.
