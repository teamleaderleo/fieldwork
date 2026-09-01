# Unit 07 execution classification — historical receipt from 2026-08-02

## Scope of this receipt

This file records execution performed on an earlier product-identical generation of the Unit 07 source. It is retained as historical evidence for the production logic, not as an exact submitted-head green receipt.

Final owner submission: [isaacs/node-lru-cache#410](https://redirect.github.com/isaacs/node-lru-cache/pull/410).

Submitted source:

- public base: `16b3a916662ab449d496b7b4b4f04132565d1d28`;
- submitted head: `364a8c1c07c9f6281fbe19943eacd261bd410fc4`;
- source PR: `teamleaderleo/node-lru-cache#2`;
- source fence: `src/index.ts`, `test/background-fetch-size.ts`;
- production source blob: `c3549a638b84ce096b13ebd7e3f71496dbe5afd5`.

The final regression-scope cleanup changed only the test blob, so the production-source observations below remain applicable while exact final-tree execution remains a separate receipt question.

## Native repository execution retained

### Benchmarks

Run `30674842990` on predecessor `70a9e62...`: passed.

### CI

Run `30674843003` on predecessor `70a9e62...` completed with an overall failure, with this job-level classification:

- Ubuntu Node 24 and Node 25: passed;
- macOS Node 24 and Node 25: passed;
- Windows Node 24/25, PowerShell and Bash: stopped before test execution because Tap could not load the repository-configured `@tapjs/clock` plugin.

Windows diagnostic:

```text
'@tapjs/clock' does not appear to be a tap plugin.
Cannot find module '@tapjs/clock'
```

The public base's `.taprc` references the plugin while the package does not install it. This is an unchanged-base repository dependency/configuration failure; it did not execute or reject the Unit 07 assertions.

## Focused source gate

Fieldwork run `30674901995` checked out predecessor `70a9e62...` on Node 22, 24, and 26. Every version passed dependency installation, source/declaration build, focused `test/background-fetch-size.ts` execution with coverage disabled, and OXLint. Those jobs then exposed formatting drift in the historical test tree.

Execution-only PR #5 used the repository's installed Prettier to generate the corrected test formatting. No workflow, dependency, or lockfile change entered the canonical source.

Execution-only PR #6, workflow `30754588900`, job `91514469959`, then established on the formatted production generation:

- dependency installation/build: passed;
- focused test: 95/95 assertions passed;
- OXLint: zero warnings/errors;
- Prettier: passed;
- `git diff --check`: passed;
- tracked worktree hygiene: passed.

## What this receipt supports

Supported for the unchanged production logic:

- source/declaration build;
- focused behavior on the historical broader regression tree;
- lint and formatting;
- Ubuntu/macOS native CI on Node 24/25;
- benchmarks;
- classification of the Windows result as a pre-test baseline harness failure.

It does **not** establish exact submitted-head green status because the final test file was later narrowed to supported regression boundaries.

Fresh submitted-head fork runs at the submission record update:

- CI `31231433021`: queued;
- Benchmarks `31231433009`: queued.

## Disposition

Historical execution receipt retained under a `SUBMITTED` unit. Do not add `@tapjs/clock`, package-lock churn, or workflow files to the submitted two-file source merely to repair the unchanged-base harness.

No additional upstream interaction is authorized from Fieldwork without explicit owner direction.
