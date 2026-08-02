# Unit 07 exact-head execution classification — 2026-08-02

## Exact identity

- Public `isaacs/node-lru-cache` main and inspected base: `16b3a916662ab449d496b7b4b4f04132565d1d28`.
- Canonical owned source head: `47fef8068ab3e4a36b939e6d4c05b2ea085f6314`.
- Source PR: `teamleaderleo/node-lru-cache#2`.
- Source fence: exactly `src/index.ts` and `test/background-fetch-size.ts`.
- Current public main has not moved beyond the inspected base.
- Canonical source contains no workflow, dependency, lockfile, generated-output, or Fieldwork-only file.

## Native repository execution retained

### Benchmarks

Run `30674842990` on product-identical predecessor `70a9e62...`: passed.

### CI

Run `30674843003` on product-identical predecessor `70a9e62...` completed with an overall failure, but the job-level classification matters:

- Ubuntu Node 24 and Node 25: passed;
- macOS Node 24 and Node 25: passed;
- Windows Node 24/25, PowerShell and Bash: failed before test execution because Tap could not load the repository-configured `@tapjs/clock` plugin.

The Windows diagnostic is:

```text
'@tapjs/clock' does not appear to be a tap plugin.
Cannot find module '@tapjs/clock'
```

The public base's `.taprc` references the plugin, while the package does not install it. This is a baseline repository dependency/configuration failure. It does not execute or reject the `backgroundFetchSize` candidate assertions.

## Pre-format exact-source carrier

Fieldwork run `30674901995` checked out exact predecessor `70a9e62...` on Node 22, 24, and 26.

Every version passed:

- exact checkout verification;
- dependency installation;
- source and declaration build;
- the focused `test/background-fetch-size.ts` gate with coverage disabled;
- OXLint with zero warnings and zero errors.

The focused test reported 95 passing assertions on the inspected Node 22 job. All three jobs then failed only because Prettier reported `test/background-fetch-size.ts` as unformatted.

## Formatting repair

Execution-only PR #5 ran the repository's installed Prettier and published the exact formatted file. The output was copied byte-for-byte to the canonical two-file source at commit `47fef8068ab3e4a36b939e6d4c05b2ea085f6314`.

PR #5 was closed without merge. No workflow or carrier file entered the canonical source.

## Exact formatted-head gate

Execution-only PR #6, workflow `30754588900`, job `91514469959`, Ubuntu 24.04 ARM, Node 24.18.0:

- dependency installation and repository build: passed;
- focused `test/background-fetch-size.ts`: 95/95 assertions passed;
- OXLint on both changed files: 0 warnings, 0 errors;
- Prettier check on both changed files: passed;
- `git diff --check`: passed;
- tracked worktree hygiene: passed.

PR #6 was closed without merge after receipt transfer.

## Product classification

Supported:

- exact formatted candidate builds and passes its 95-assertion focused gate;
- both changed files pass OXLint and repository Prettier;
- predecessor behavior also passed on Node 22/24/26;
- Linux and macOS native CI passed on Node 24/25;
- benchmarks passed;
- Windows native jobs are blocked before tests by an upstream baseline Tap-plugin dependency failure.

Current-head native CI `30754536472` and Benchmarks `30754536526` are queued. They are not represented as passes or failures.

Remaining work:

1. classify the current-head native matrix when it executes;
2. obtain a Windows product-test receipt through an execution-only harness that installs the baseline-declared Tap plugin, or retain the baseline blocker explicitly;
3. perform current-head complete-diff review.

Do not add `@tapjs/clock`, package-lock churn, or workflow files to the canonical two-file source merely to repair the upstream baseline harness.

## Current disposition

`EXECUTE — exact formatted focused gate passed; current-head native matrix pending`.

Public upstream interaction remains unauthorized and none occurred.
