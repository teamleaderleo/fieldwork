# Unit 07 current-head native matrix — 2026-08-03

## In simple words

The exact formatted node-lru-cache source head completed its native CI and benchmark runs. Ubuntu and macOS passed on Node 24 and 25, and benchmarks passed. Every Windows job stopped before collecting candidate tests because TAP could not load the public-base `@tapjs/clock` plugin. The same missing-plugin signature had already occurred on the product-identical predecessor head.

This is a dependency/harness failure, not a failed background-fetch assertion. The canonical source remains exactly two files and must not absorb unrelated package or lockfile changes merely to alter that baseline harness.

## Exact identities

- Repository: `teamleaderleo/node-lru-cache`
- Canonical branch: `repair/background-fetch-size-source`
- Exact head: `47fef8068ab3e4a36b939e6d4c05b2ea085f6314`
- Public base: `16b3a916662ab449d496b7b4b4f04132565d1d28`
- Changed files: `src/index.ts`, `test/background-fetch-size.ts`
- Native CI: `30754536472`
- Benchmarks: `30754536526`
- Exact focused repair: `30754588900`, job `91514469959`

## Current-head results

Native CI `30754536472`:

- Ubuntu Node 24: passed
- Ubuntu Node 25: passed
- macOS Node 24: passed
- macOS Node 25: passed
- Windows Node 24, bash: harness failure before tests
- Windows Node 24, PowerShell: harness failure before tests
- Windows Node 25, bash: harness failure before tests
- Windows Node 25, PowerShell: harness failure before tests

Windows signature:

```text
'@tapjs/clock' does not appear to be a tap plugin.
Cannot find module '@tapjs/clock'
```

Benchmarks `30754536526`: passed.

Focused exact-head job `91514469959`:

- repository install/build passed;
- 95/95 focused assertions passed;
- OXLint passed with zero warnings/errors;
- repository formatter check passed;
- diff hygiene and clean-tree checks passed.

## Disposition effect

The source repair is no longer waiting on queued exact-head execution. Candidate-owned behavior, build, lint, formatting, Unix/macOS native matrices, and benchmarks passed. Windows remains an explicit baseline harness limit because no candidate assertion was collected.

No public upstream interaction occurred or is authorized.
