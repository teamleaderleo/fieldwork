# Unit 07 native matrix — historical receipt from 2026-08-03

## In simple words

This receipt records native CI and benchmark results on an earlier product-identical source generation. Ubuntu and macOS passed on Node 24 and 25, and benchmarks passed. Every Windows job stopped before collecting candidate tests because TAP could not load the unchanged-base `@tapjs/clock` plugin.

The final submitted head is `364a8c1c07c9f6281fbe19943eacd261bd410fc4`, and the owner submitted it as [isaacs/node-lru-cache#410](https://redirect.github.com/isaacs/node-lru-cache/pull/410).

The production source blob is unchanged from the generation covered here, while the final test tree was later narrowed. Therefore this receipt supports the production logic and platform classification but is not an exact submitted-test-tree green claim.

## Historical exact identities

- repository: `teamleaderleo/node-lru-cache`;
- historical canonical branch: `repair/background-fetch-size-source`;
- historical head: `47fef8068ab3e4a36b939e6d4c05b2ea085f6314`;
- public base: `16b3a916662ab449d496b7b4b4f04132565d1d28`;
- changed files: `src/index.ts`, `test/background-fetch-size.ts`;
- native CI: `30754536472`;
- benchmarks: `30754536526`;
- focused exact-source repair: `30754588900`, job `91514469959`.

## Historical results

Native CI `30754536472`:

- Ubuntu Node 24: passed;
- Ubuntu Node 25: passed;
- macOS Node 24: passed;
- macOS Node 25: passed;
- Windows Node 24, Bash: harness failure before tests;
- Windows Node 24, PowerShell: harness failure before tests;
- Windows Node 25, Bash: harness failure before tests;
- Windows Node 25, PowerShell: harness failure before tests.

Windows signature:

```text
'@tapjs/clock' does not appear to be a tap plugin.
Cannot find module '@tapjs/clock'
```

Benchmarks `30754536526`: passed.

Focused job `91514469959`:

- repository install/build passed;
- 95/95 focused assertions passed on the historical broader test tree;
- OXLint passed with zero warnings/errors;
- repository formatter check passed;
- diff hygiene and clean-tree checks passed.

## Submitted-head boundary

Submitted source identity:

- head: `364a8c1c07c9f6281fbe19943eacd261bd410fc4`;
- production source blob: `c3549a638b84ce096b13ebd7e3f71496dbe5afd5`;
- final test blob: `a83968f5110bfe42cfe32aae55cb6018aba6aebd`.

Fresh fork runs for that final tree remained queued at the submission record update:

- CI `31231433021`;
- Benchmarks `31231433009`.

Do not describe those queued runs as green. The unchanged-source historical receipts remain useful support, and the Windows pre-test failure remains a baseline harness classification.

## Disposition effect

Unit 07 is `SUBMITTED`. No dependency, lockfile, or workflow change should be added to the source merely to alter the baseline Windows harness. No additional upstream interaction is authorized without explicit owner direction.
