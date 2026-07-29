# Target Map: Playwright

Repository: https://redirect.github.com/microsoft/playwright

## In simple words

A browser automation and testing system that owns browser processes, contexts, pages, retries, traces, artifacts, and teardown. Reliability depends on what survives or disappears across failures and retries.

## Areas worth understanding

- browser and context lifecycle;
- retry isolation and state leakage;
- timeout and cancellation ownership;
- tracing, screenshots, video, and artifact finalization;
- process teardown and orphan cleanup;
- protocol and browser-version compatibility;
- parallel execution and resource pressure;
- fixtures and test-runner semantics.

## Evidence we can produce

- deterministic flaky and retry fixtures;
- teardown and orphan-process checks;
- artifact completeness matrices;
- browser-version comparisons;
- controlled trials in Elatura or Renderprove;
- timing and resource measurements.

## Entry standard

Preserve exact browser, runner, and operating-system versions. A meaningful change should improve correctness, isolation, cleanup, diagnosability, performance, or compatibility under a demonstrated scenario.

## Stop conditions

- the failure depends only on an unstable external website;
- the result is a test-authoring mistake rather than runner behavior;
- browser-version differences cannot be isolated;
- the proposal is only wording or documentation cleanup.
