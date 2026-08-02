# Unit 07 exact-head execution classification — 2026-08-02

## Exact identity

- Public `isaacs/node-lru-cache` main and inspected base: `16b3a916662ab449d496b7b4b4f04132565d1d28`.
- Canonical owned source head: `70a9e62b0555e6bb68763fb9d32458fa82fd2a70`.
- Source PR: `teamleaderleo/node-lru-cache#2`.
- Source fence: exactly `src/index.ts` and `test/background-fetch-size.ts`.
- Current public main has not moved beyond the inspected base.

## Native repository execution

### Benchmarks

Run `30674842990`: passed.

### CI

Run `30674843003` completed with an overall failure, but the job-level classification matters:

- Ubuntu Node 24 and Node 25: passed;
- macOS Node 24 and Node 25: passed;
- Windows Node 24/25, PowerShell and Bash: failed before test execution because Tap could not load the repository-configured `@tapjs/clock` plugin.

The Windows diagnostic is:

```text
'@tapjs/clock' does not appear to be a tap plugin.
Cannot find module '@tapjs/clock'
```

The public base's `.taprc` references the plugin, while the package does not install it. This is a baseline repository dependency/configuration failure. It does not execute or reject the `backgroundFetchSize` candidate assertions.

## Exact-source focused carrier

Fieldwork run `30674901995` checked out exact source `70a9e62...` on Node 22, 24, and 26.

Every version passed:

- exact checkout verification;
- dependency installation;
- source and declaration build;
- the focused `test/background-fetch-size.ts` gate with coverage disabled;
- OXLint with zero warnings and zero errors.

The focused test reported 95 passing assertions on the inspected Node 22 job. All three jobs then failed only because Prettier reported `test/background-fetch-size.ts` as unformatted.

## Product classification

Supported:

- exact candidate builds on Node 22/24/26;
- focused behavior passes on Node 22/24/26;
- Linux and macOS native CI pass on Node 24/25;
- benchmarks pass;
- Windows native jobs are blocked before tests by an upstream baseline Tap-plugin dependency failure.

Remaining candidate repair:

1. format `test/background-fetch-size.ts` with repository Prettier 3.8.3 and `.prettierrc.json`;
2. rerun focused build/OXLint/Prettier on the new exact head;
3. obtain a Windows product-test receipt through a harness that installs the baseline-declared Tap plugin, or explicitly retain the baseline blocker without modifying the two-file product fence;
4. perform current-head complete-diff review.

Do not add `@tapjs/clock`, package-lock churn, or workflow files to the canonical two-file source merely to repair the upstream baseline harness. Any execution-only dependency workaround belongs in a carrier and must be classified separately.

## Current disposition

`REPAIR — product behavior passes; one formatting repair and Windows baseline-harness classification remain`.

Public upstream interaction remains unauthorized and none occurred.
