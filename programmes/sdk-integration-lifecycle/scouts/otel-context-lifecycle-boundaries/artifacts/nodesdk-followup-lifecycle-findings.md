# NodeSDK follow-up lifecycle findings

## Status

- Date: 2026-07-30
- Target revision: `open-telemetry/opentelemetry-js@7b06368b7362a30ca69c178f43bd94dfbb36f85d`
- Current upstream `sdk.ts` checked: same blob as target revision
- Characterization branch: `fieldwork/nodesdk-shutdown-lifecycle-characterization`
- Characterization draft PR: https://redirect.github.com/teamleaderleo/opentelemetry-js/pull/1
- Fix branch: `fieldwork/nodesdk-start-state-guard`
- Fix draft PR: https://redirect.github.com/teamleaderleo/opentelemetry-js/pull/2
- Upstream contact performed: `false`

## New executable characterizations

The characterization branch now adds the following tests beyond the original repeated-start cases.

### Function startup failure is not a no-op

File:

`experimental/packages/opentelemetry-sdk-node/test/lifecycle-start-function-characterization.test.ts`

The newer `startNodeSDK()` function calls `registerInstrumentations()` before component creation.

When declarative component creation fails:

- the function returns the shared `NOOP_SDK` object;
- a supplied initially disabled instrumentation has already been enabled;
- the instrumentation is not disabled;
- an `AsyncLocalStorageContextManager` has already been created and enabled;
- that context manager is not disabled because component creation throws before it is returned or globally registered.

A second test invokes `startNodeSDK()` twice with signals disabled. Both context managers are enabled, both registration calls occur, the second global registration returns false, and neither returned shutdown handle disables a context manager.

Pinned source:

- https://redirect.github.com/open-telemetry/opentelemetry-js/blob/7b06368b7362a30ca69c178f43bd94dfbb36f85d/experimental/packages/opentelemetry-sdk-node/src/start.ts

### Metric construction can strand a reader

File:

`experimental/packages/opentelemetry-sdk-node/test/lifecycle-metric-construction-characterization.test.ts`

A `MeterProvider` binds configured readers in order. The test passes:

1. a fresh reader;
2. a reader already bound to another provider.

The fresh reader is bound first. The second reader then throws. Because the `MeterProvider` constructor never returns, NodeSDK never assigns the provider to `_meterProvider`.

Observed consequence:

- `sdk.start()` throws;
- `_meterProvider` remains undefined;
- `sdk.shutdown()` does not call the fresh reader's shutdown;
- the fresh reader rejects attachment to another provider because it remains bound to the unreachable partial provider.

Pinned sources:

- https://redirect.github.com/open-telemetry/opentelemetry-js/blob/7b06368b7362a30ca69c178f43bd94dfbb36f85d/packages/sdk-metrics/src/MeterProvider.ts
- https://redirect.github.com/open-telemetry/opentelemetry-js/blob/7b06368b7362a30ca69c178f43bd94dfbb36f85d/packages/sdk-metrics/src/export/MetricReader.ts
- https://redirect.github.com/open-telemetry/opentelemetry-js/blob/7b06368b7362a30ca69c178f43bd94dfbb36f85d/experimental/packages/opentelemetry-sdk-node/src/sdk.ts

This is a lower-level metrics construction transaction problem. A NodeSDK-only catch block cannot unbind the stranded reader with the current interfaces.

### Repeated shutdown reaches a custom trace processor twice

File:

`experimental/packages/opentelemetry-sdk-node/test/lifecycle-shutdown-idempotence-characterization.test.ts`

The test configures a custom `SpanProcessor`, starts NodeSDK, and awaits `sdk.shutdown()` twice.

The processor's `shutdown()` method is called twice.

Tracing differs from logs and metrics here:

- `LoggerProvider` uses a one-shot future;
- `MeterProvider` marks itself shutdown before awaiting readers;
- `TracerProvider` delegates each shutdown call to `MultiSpanProcessor` without provider state.

Pinned sources:

- https://redirect.github.com/open-telemetry/opentelemetry-js/blob/7b06368b7362a30ca69c178f43bd94dfbb36f85d/packages/sdk-trace/src/TracerProvider.ts
- https://redirect.github.com/open-telemetry/opentelemetry-js/blob/7b06368b7362a30ca69c178f43bd94dfbb36f85d/packages/sdk-trace/src/MultiSpanProcessor.ts

### Custom trace processors still receive spans after shutdown

File:

`experimental/packages/opentelemetry-sdk-node/test/lifecycle-post-shutdown-tracing-characterization.test.ts`

The test configures a custom processor with counters for `onStart`, `onEnd`, and `shutdown`.

After `sdk.shutdown()` resolves, a span created through the still-global trace API increments both processing counters.

Standard span processors often hide this behavior because they implement their own shutdown guards. The provider itself, however, continues returning regular tracers and forwarding events to arbitrary custom processors.

The trace SDK specification requires one provider shutdown and recommends no-op tracer behavior after shutdown where possible. This finding therefore belongs below the NodeSDK helper as well as at the helper boundary.

## Fix trial

Draft fork PR #2 contains the actual narrow source patch:

- branch: `fieldwork/nodesdk-start-state-guard`
- source commit: `91fd86e3e727522dc3dfd62a134657fdfa921436`
- test commit: `14b524ff0c0d8e39321c31be218b0c9ee0ca0b78`

Production diff:

```diff
+  private _startAttempted = false;
@@
+    if (this._startAttempted) {
+      diag.warn('NodeSDK.start() may only be called once.');
+      return;
+    }
+    this._startAttempted = true;
```

The fork test file covers:

- direct repeated start;
- start after shutdown;
- reentrant start during context-manager enablement;
- a second attempt after startup throws.

The guard is deliberately set before the first side effect.

## Revised classification

The campaign now contains multiple confirmed behaviors:

1. **Same-object repeated initialization bug:** safely addressed by the one-attempt guard.
2. **Process-global installation ownership gap:** affects separate NodeSDK objects and `startNodeSDK()`; requires explicit ownership design.
3. **Failure-path cleanup gap:** `startNodeSDK()` can return `NOOP_SDK` after installation side effects.
4. **Metric construction transaction gap:** reader binding can partially commit before constructor failure.
5. **Trace provider shutdown contract gap:** repeated shutdown and post-shutdown custom processor callbacks remain possible.

These should not be combined into one large first patch.

## Validation status

- Source and type-shape review: complete.
- Characterization tests committed: complete.
- Narrow production fix committed: complete.
- Fork draft PRs: open.
- GitHub Actions visible for fork commits: none at recorded checks.
- Full monorepo test execution: not available in the work container because dependencies cannot be installed.

No upstream issue, pull request, comment, review, reaction, or direct backlink was created.
