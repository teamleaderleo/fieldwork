# Review — Unit 07 `backgroundFetchSize` snapshot

## Review subject

- source PR: `teamleaderleo/node-lru-cache#2`;
- base: `16b3a916662ab449d496b7b4b4f04132565d1d28`;
- head: `47fef8068ab3e4a36b939e6d4c05b2ea085f6314`;
- fence: `src/index.ts`, `test/background-fetch-size.ts`.

## Source findings

No blocking source defect remains.

- `isNonNegativeInt()` checks primitive number type before the existing positive-integer helper, so symbols, objects, and hostile conversion hooks are never coerced.
- constructor default `1`, explicit zero, and positive integers remain valid; explicit `undefined` keeps omission/default behavior.
- the missing-key receipt is captured before the Promise executor invokes user `fetchMethod` synchronously.
- stale refresh continues to use the existing entry size and does not consume the provisional receipt.
- caches without size tracking remain insensitive to later irrelevant field mutation.
- `BackgroundFetch.__size` is optional in the exported type, while the internal accounting boundary rejects an absent or corrupt receipt.
- the two-file diff contains no workflow, dependency, lockfile, generated output, or unrelated formatting.

## Execution reviewed

- focused exact head: run `30754588900`, job `91514469959`, 95/95 assertions, build, OXLint, Prettier, diff hygiene — success;
- benchmarks `30754536526` — success;
- native CI `30754536472`:
  - Ubuntu Node 24/25 — success;
  - macOS Node 24/25 — success;
  - Windows Node 24/25 Bash/PowerShell — stopped before tests because the unchanged repository configuration requests missing `@tapjs/clock`.

The Windows logs under both shells are identical at the ownership boundary: package installation/build succeeds, then Tap fails to load the plugin before collecting candidate assertions. A separate base/candidate harness comparison classifies this as unchanged-base coverage behavior.

## Evidence limits

- no green native Windows coverage suite is claimed;
- production prevalence remains unknown;
- constructor-wide eager validation remains a public-contract choice, though it is internally coherent and covered;
- public overlap, policy, and maintainer preference can change before filing.

## Disposition

`ACCEPT / TECHNICALLY READY`

The source can advance to owner review and authorized upstream preparation. Repeat current-main, duplicate, contribution-policy, and disclosure checks immediately before filing. Public upstream interaction remains unauthorized.
