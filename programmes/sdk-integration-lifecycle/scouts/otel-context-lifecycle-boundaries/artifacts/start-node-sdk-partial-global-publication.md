# startNodeSDK partial process-global publication

## In simple words

`startNodeSDK()` publishes context, logs, metrics, traces, and propagation one at a time and ignores every registration result. The process can therefore accept some of the helper's components while retaining older components for other signals.

The helper still returns one shutdown handle for its privately created providers. That handle can shut down a tracer provider that was never global while leaving the actual global tracer provider active. Meanwhile, the helper-created context manager may have become global successfully.

This is not simply “the second SDK failed.” It is a mixed installation assembled from different owners.

## Pinned scope

- repository: `open-telemetry/opentelemetry-js`
- revision: `7b06368b7362a30ca69c178f43bd94dfbb36f85d`
- package: `@opentelemetry/sdk-node`
- helper: `startNodeSDK()`
- characterization branch: `fieldwork/nodesdk-shutdown-lifecycle-characterization`
- characterization head: `f1b401e49904f9523cd4a8a204451d33cb4ba5ff`
- evidence class: `target-test-prepared`

## Source sequence

The function publishes globals sequentially and does not inspect return values:

1. context manager;
2. logger provider;
3. meter provider;
4. tracer provider;
5. propagator.

Source:

https://redirect.github.com/open-telemetry/opentelemetry-js/blob/7b06368b7362a30ca69c178f43bd94dfbb36f85d/experimental/packages/opentelemetry-sdk-node/src/start.ts#L94-L108

The API setters reject duplicate first-registration attempts by returning `false` rather than rolling back earlier successful registrations.

## Prepared characterization

File:

`experimental/packages/opentelemetry-sdk-node/test/lifecycle-start-function-characterization.test.ts`

The new case:

1. registers an existing SDK `TracerProvider` globally;
2. configures `startNodeSDK()` to create a separate trace provider;
3. calls the helper;
4. observes context registration return `true`;
5. observes trace-provider registration return `false`;
6. creates a span through the global trace API and sees it reach the pre-existing provider;
7. calls the returned shutdown handle and observes shutdown of the helper-created private provider, not the global provider;
8. creates another global span and sees the pre-existing provider remain active.

The process now contains:

- helper-owned global context;
- pre-existing global tracing;
- helper-owned private tracing reachable only through its shutdown closure.

## Why this matters

A single startup helper implies one installation boundary, but the actual process state can be signal-by-signal partial.

Consequences include:

- instrumentation may have been configured against helper-created providers that did not become global;
- shutdown can target private providers while applications keep using older global providers;
- diagnostics warn about duplicate registration but the returned handle does not report degraded installation;
- later cleanup cannot safely remove globals because ownership differs by signal;
- application code cannot tell whether startup fully succeeded, partially succeeded, or merely created private components.

## Relationship to existing findings

This extends earlier findings:

- repeated `NodeSDK.start()` can split private and global provider ownership;
- repeated `startNodeSDK()` enables rejected context managers;
- failed setup can leave side effects unless cleanup occurs before publication.

The new case proves that even one helper call can create a mixed installation when the process already owns one signal global.

## Contract choices

### A. Preflight all required global slots

Check whether every intended registration can be owned before publishing any component.

Problem: current API setters do not expose reservation or ownership-token primitives, and some APIs may already use proxy globals.

### B. Treat registration as a transaction

Publish every signal only if all can commit; otherwise roll back only registrations still owned by this attempt.

Problem: safe rollback requires exact ownership tokens or compare-and-remove operations that current APIs do not expose.

### C. Fail before side effects when any duplicate exists

Define the helper as process-singleton startup and reject a second or conflicting installation before context enablement, instrumentation registration, or provider creation.

Problem: cross-package detection still needs a reliable process-level installation marker and compatibility agreement.

### D. Return an explicit installation result

Return per-signal registration outcomes and distinguish provider shutdown from installation disposal.

Problem: changes the experimental helper surface and still leaves partial installation unless callers can request all-or-nothing behavior.

## Current direction

Do not attempt blind rollback with the current public APIs.

The safest design discussion should cover:

- whether the helper promises all-or-nothing installation;
- process-singleton enforcement before side effects;
- per-signal ownership tokens;
- compare-and-remove global disposal;
- separate provider shutdown and installation disposal;
- explicit degraded or partial startup results if partial installation remains supported.

This belongs under the process-global registration ownership and disposal design candidate rather than the narrow failed-creation cleanup patch.

## Validation boundary

The test is committed in the user-owned fork but has not run in the current environment. No passing test or executed failure is claimed.

## Contact boundary

No upstream issue, pull request, comment, review, reaction, or direct backlink was created.
