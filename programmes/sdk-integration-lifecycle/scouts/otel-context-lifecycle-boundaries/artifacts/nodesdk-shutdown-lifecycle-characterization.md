# NodeSDK registration lifecycle characterization

## Status

- First recorded: 2026-07-29
- Extended: 2026-07-30
- OpenTelemetry JS revision: `7b06368b7362a30ca69c178f43bd94dfbb36f85d`
- User-owned fork: `teamleaderleo/opentelemetry-js`
- Fork branch: `fieldwork/nodesdk-shutdown-lifecycle-characterization`
- Draft fork PR: https://redirect.github.com/teamleaderleo/opentelemetry-js/pull/1
- Upstream contact authorized: `false`
- Upstream contact performed: `false`

This artifact promotes the report's highest-ranked branch candidate into executable characterization tests. It does not propose an upstream patch and does not create an upstream backlink.

## Questions

1. What remains registered after `NodeSDK.shutdown()`?
2. What happens when a second `NodeSDK` instance starts in the same process?
3. What happens when `start()` is called twice on the same `NodeSDK` instance?

## Source-level result

At the pinned revision:

1. `NodeSDK.start()` calls `registerInstrumentations(...)` but does not retain the returned unload function.
2. `NodeSDK.start()` enables and globally registers a context manager and propagator.
3. Configured tracer, meter, and logger providers are registered globally.
4. `NodeSDK.shutdown()` shuts down only the providers currently stored in `_tracerProvider`, `_meterProvider`, and `_loggerProvider`.
5. API global registration rejects duplicate registration and leaves the existing global in place.
6. `NodeSDK.start()` has no started-state guard. A repeated call constructs new providers and overwrites the SDK's private provider fields even when duplicate global registration leaves the first provider globally active.
7. The existing NodeSDK test suite manually disables context, tracing, propagation, metrics, and logs before each test, so ordinary suite isolation does not prove `NodeSDK.shutdown()` cleanup or repeated-start ownership.

Pinned source references:

- NodeSDK start and shutdown: https://redirect.github.com/open-telemetry/opentelemetry-js/blob/7b06368b7362a30ca69c178f43bd94dfbb36f85d/experimental/packages/opentelemetry-sdk-node/src/sdk.ts
- Context and propagator setup: https://redirect.github.com/open-telemetry/opentelemetry-js/blob/7b06368b7362a30ca69c178f43bd94dfbb36f85d/experimental/packages/opentelemetry-sdk-node/src/utils.ts
- Instrumentation registration disposer: https://redirect.github.com/open-telemetry/opentelemetry-js/blob/7b06368b7362a30ca69c178f43bd94dfbb36f85d/experimental/packages/opentelemetry-instrumentation/src/autoLoader.ts
- Duplicate-global rejection: https://redirect.github.com/open-telemetry/opentelemetry-js/blob/7b06368b7362a30ca69c178f43bd94dfbb36f85d/api/src/internal/global-utils.ts
- Trace proxy delegate behavior: https://redirect.github.com/open-telemetry/opentelemetry-js/blob/7b06368b7362a30ca69c178f43bd94dfbb36f85d/api/src/api/trace.ts and https://redirect.github.com/open-telemetry/opentelemetry-js/blob/7b06368b7362a30ca69c178f43bd94dfbb36f85d/api/src/trace/ProxyTracerProvider.ts
- NodeSDK test isolation: https://redirect.github.com/open-telemetry/opentelemetry-js/blob/7b06368b7362a30ca69c178f43bd94dfbb36f85d/experimental/packages/opentelemetry-sdk-node/test/sdk.test.ts

## Executable characterization

The fork branch adds two test files:

- `experimental/packages/opentelemetry-sdk-node/test/lifecycle-characterization.test.ts`
- `experimental/packages/opentelemetry-sdk-node/test/lifecycle-double-start-characterization.test.ts`

### 1. Instrumentation remains enabled

A tracking instrumentation is supplied to `NodeSDK`. After `start()` and awaited `shutdown()`, its `disable()` call count remains zero and its configuration remains enabled.

This directly characterizes the consequence of discarding the unloader returned by `registerInstrumentations()`.

### 2. First context manager remains global

SDK A starts with context manager A, then shuts down. SDK B starts with context manager B. The global context manager remains A after both A's shutdown and B's start.

This directly characterizes duplicate registration: B is enabled as an object, but cannot become the process-global manager while A remains registered.

### 3. Second tracer provider does not receive spans

SDK A starts with exporter A and exports one span. SDK A shuts down. SDK B starts with exporter B. A span created through the global tracing API after B starts reaches neither B's exporter nor a live replacement provider; exporter B remains empty because the shutdown provider from A remains global.

This is the concrete functional consequence. It is stronger than a diagnostic-log-only duplicate registration report.

### 4. Repeated start splits global and owned provider identity

One `NodeSDK` instance starts twice. The first start installs tracer provider A as the delegate behind the global trace proxy. The second start constructs provider B and overwrites the SDK's `_tracerProvider` field, but duplicate global registration leaves provider A as the global delegate.

When `sdk.shutdown()` is called, provider B receives shutdown while provider A remains globally active and is no longer owned by the SDK object. The characterization test explicitly shuts provider A down afterward only to isolate the test.

This is a distinct ownership failure from `start A -> shutdown A -> start B`. It can occur without creating a second SDK object.

## Classification

The behaviors above are source-confirmed. Their final classification depends on the intended `NodeSDK` contract.

The cross-language signal specifications require each provider's shutdown to flush and clean up its processors or exporters. They do not clearly require a language-specific combined helper to unregister process globals or unpatch instrumentation. The JavaScript NodeSDK documentation describes shutdown as a way to export telemetry before process exit, which is consistent with a process-singleton interpretation.

Repeated startup is normally an application integration mistake. However, accepting the second call, constructing replacement providers, overwriting private ownership, and then shutting down a provider that is not globally active creates a library-level contract gap even when the initiating call is mistaken.

The decision space is:

1. **Restart and repeated installation are supported.** `NodeSDK` needs owned teardown and start-state transitions.
2. **One start per process is the contract.** `NodeSDK.start()` should reject or safely no-op repeated calls, and documentation and tests should state this clearly.
3. **Provider shutdown and installation disposal are separate.** The package needs a distinct owned `dispose()` or `stop()` operation with explicit instrumentation and global-registration semantics.

## Local execution requirements

No additional repository needs to be forked. To run the branch locally, use the existing JavaScript fork with Node.js 20 and npm:

```bash
git clone https://github.com/teamleaderleo/opentelemetry-js.git
cd opentelemetry-js
git checkout fieldwork/nodesdk-shutdown-lifecycle-characterization
npm ci
npm run compile
npm test --workspace=@opentelemetry/sdk-node
```

The repository's contribution guide uses `npm ci`, `npm run compile`, and `npm run test`. Node 20 is the conservative choice because some root tooling explicitly requires Node.js 20 even though the SDK package supports selected Node 18 releases.

## Validation status

- Source and type-shape review: complete for both test files.
- Fork branch and draft PR: created and extended.
- GitHub Actions jobs visible for the fork commits: none at the recorded checks.
- Full monorepo package execution: unavailable in the work container because repository dependencies are not installed and outbound package retrieval is unavailable.

The package-level falsification command is:

```bash
npm test --workspace=@opentelemetry/sdk-node
```

If the branch compiles and the characterization tests pass, promote the result to a reproduced lifecycle defect or contract gap. If a test fails, retain the exact output and revise the ownership model rather than forcing the hypothesis.

## Related prior report

A prior duplicate-registration report was attributed to application double startup rather than shutdown or restart:

https://redirect.github.com/open-telemetry/opentelemetry-js/issues/4804

That negative result remains valid for its reported setup. The new tests deliberately isolate two different cases:

- `start A -> shutdown A -> start B`
- `start A -> start A again -> shutdown A`

No upstream issue, pull request, comment, review, reaction, or direct backlink was created.
