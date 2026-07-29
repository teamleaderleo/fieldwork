# NodeSDK shutdown registration lifecycle characterization

## Status

- Date: 2026-07-29
- OpenTelemetry JS revision: `7b06368b7362a30ca69c178f43bd94dfbb36f85d`
- User-owned fork: `teamleaderleo/opentelemetry-js`
- Fork branch: `fieldwork/nodesdk-shutdown-lifecycle-characterization`
- Draft fork PR: https://redirect.github.com/teamleaderleo/opentelemetry-js/pull/1
- Upstream contact authorized: `false`
- Upstream contact performed: `false`

This artifact promotes the report's highest-ranked branch candidate into executable characterization tests. It does not propose an upstream patch and does not create an upstream backlink.

## Question

What remains registered after `NodeSDK.shutdown()`, and what happens when a second `NodeSDK` instance starts in the same process?

## Source-level result

At the pinned revision:

1. `NodeSDK.start()` calls `registerInstrumentations(...)` but does not retain the returned unload function.
2. `NodeSDK.start()` enables and globally registers a context manager and propagator.
3. Configured tracer, meter, and logger providers are registered globally.
4. `NodeSDK.shutdown()` shuts down only the providers owned in `_tracerProvider`, `_meterProvider`, and `_loggerProvider`.
5. API global registration rejects duplicate registration and leaves the existing global in place.
6. The existing NodeSDK test suite manually disables context, tracing, propagation, metrics, and logs before each test, so ordinary suite isolation does not prove `NodeSDK.shutdown()` cleanup.

Pinned source references:

- NodeSDK start and shutdown: https://redirect.github.com/open-telemetry/opentelemetry-js/blob/7b06368b7362a30ca69c178f43bd94dfbb36f85d/experimental/packages/opentelemetry-sdk-node/src/sdk.ts
- Context and propagator setup: https://redirect.github.com/open-telemetry/opentelemetry-js/blob/7b06368b7362a30ca69c178f43bd94dfbb36f85d/experimental/packages/opentelemetry-sdk-node/src/utils.ts
- Instrumentation registration disposer: https://redirect.github.com/open-telemetry/opentelemetry-js/blob/7b06368b7362a30ca69c178f43bd94dfbb36f85d/experimental/packages/opentelemetry-instrumentation/src/autoLoader.ts
- Duplicate-global rejection: https://redirect.github.com/open-telemetry/opentelemetry-js/blob/7b06368b7362a30ca69c178f43bd94dfbb36f85d/api/src/internal/global-utils.ts
- NodeSDK test isolation: https://redirect.github.com/open-telemetry/opentelemetry-js/blob/7b06368b7362a30ca69c178f43bd94dfbb36f85d/experimental/packages/opentelemetry-sdk-node/test/sdk.test.ts

## Executable characterization

The fork branch adds:

`experimental/packages/opentelemetry-sdk-node/test/lifecycle-characterization.test.ts`

It contains three tests.

### 1. Instrumentation remains enabled

A tracking instrumentation is supplied to `NodeSDK`. After `start()` and awaited `shutdown()`, its `disable()` call count remains zero and its configuration remains enabled.

This directly characterizes the consequence of discarding the unloader returned by `registerInstrumentations()`.

### 2. First context manager remains global

SDK A starts with context manager A, then shuts down. SDK B starts with context manager B. The global context manager remains A after both A's shutdown and B's start.

This directly characterizes duplicate registration: B is enabled as an object, but cannot become the process-global manager while A remains registered.

### 3. Second tracer provider does not receive spans

SDK A starts with exporter A and exports one span. SDK A shuts down. SDK B starts with exporter B. A span created through the global tracing API after B starts reaches neither B's exporter nor a live replacement provider; exporter B remains empty because the shutdown provider from A remains global.

This is the concrete functional consequence. It is stronger than a diagnostic-log-only duplicate registration report.

## Contract interpretation

This is a confirmed behavior and a confirmed restart failure under the tested lifecycle. Its classification as a library bug still depends on the intended `NodeSDK` contract.

The cross-language signal specifications require each provider's shutdown to flush and clean up its processors/exporters. They do not clearly require a language-specific combined helper to unregister process globals or unpatch instrumentation. The JavaScript NodeSDK documentation describes shutdown as a way to export telemetry before process exit, which is consistent with a process-singleton interpretation.

Therefore the decision is one of:

1. **Restart is supported.** Then `NodeSDK` needs owned teardown for instrumentation and globals, plus start-shutdown-start tests.
2. **Restart is unsupported.** Then `NodeSDK` should state the process-singleton contract and reject or diagnose second start deterministically rather than silently leaving the second provider unreachable.
3. **Provider shutdown and installation disposal are separate.** Then the package needs a distinct owned `dispose()` or `stop()` operation with explicit semantics.

## Validation status

- Source and type-shape review: complete.
- Fork branch and draft PR: created.
- GitHub Actions jobs visible for the fork commit: none at the time of recording.
- Full monorepo package test execution: not yet available in the work container because the repository dependencies are not installed and outbound package retrieval is unavailable.

The exact package command to falsify the characterization is:

```bash
npm test --workspace=@opentelemetry/sdk-node -- --grep "NodeSDK shutdown lifecycle characterization"
```

If the branch compiles and all three tests pass, promote this from source-backed candidate to reproduced lifecycle defect/contract gap. If any test fails, retain the actual output and revise the ownership model rather than forcing the hypothesis.

## Related prior report

A prior duplicate-registration report was attributed to application double startup rather than shutdown/restart:

https://redirect.github.com/open-telemetry/opentelemetry-js/issues/4804

That negative result remains valid. The new characterization is different: it intentionally performs `start A -> shutdown A -> start B` and tests the post-shutdown global owner.
