# NodeSDK shutdown and start interleaving

## In simple words

`NodeSDK.shutdown()` can currently say “finished” before `NodeSDK.start()` has created any providers. Startup may then continue and install live providers after the shutdown promise has resolved. This can happen when shutdown is called before start or reentered synchronously from user-controlled instrumentation during start.

This is a new lifecycle lead. It is not yet promoted to an additional upstream proposal because the new characterization tests have not been executed in this environment.

## Pinned scope

- repository: `open-telemetry/opentelemetry-js`
- revision: `7b06368b7362a30ca69c178f43bd94dfbb36f85d`
- package: `@opentelemetry/sdk-node`
- characterization branch: `fieldwork/nodesdk-shutdown-lifecycle-characterization`
- characterization commit: `1cd6c44f6ab66efc2ae2e86b73c83c9fae4a4357`

## Source sequence

`registerInstrumentations()` obtains the current global providers and synchronously calls `enableInstrumentations()`:

https://redirect.github.com/open-telemetry/opentelemetry-js/blob/7b06368b7362a30ca69c178f43bd94dfbb36f85d/experimental/packages/opentelemetry-instrumentation/src/autoLoader.ts#L22-L39

`enableInstrumentations()` synchronously calls user instrumentation `enable()` when the instrumentation is configured as disabled:

https://redirect.github.com/open-telemetry/opentelemetry-js/blob/7b06368b7362a30ca69c178f43bd94dfbb36f85d/experimental/packages/opentelemetry-instrumentation/src/autoLoaderUtils.ts#L18-L42

`NodeSDK.start()` performs that registration before context, resource, metric, trace, and log provider construction. Provider fields are assigned later:

https://redirect.github.com/open-telemetry/opentelemetry-js/blob/7b06368b7362a30ca69c178f43bd94dfbb36f85d/experimental/packages/opentelemetry-sdk-node/src/sdk.ts#L248-L363

`NodeSDK.shutdown()` only collects shutdown promises from provider fields that exist at the instant it is called. With no fields set, `Promise.all([])` resolves successfully:

https://redirect.github.com/open-telemetry/opentelemetry-js/blob/7b06368b7362a30ca69c178f43bd94dfbb36f85d/experimental/packages/opentelemetry-sdk-node/src/sdk.ts#L365-L381

## Characterization cases

New test file:

`experimental/packages/opentelemetry-sdk-node/test/lifecycle-shutdown-start-interleaving-characterization.test.ts`

### Case 1 — shutdown before start

1. Construct a trace-enabled `NodeSDK`.
2. Await `sdk.shutdown()` before calling `start()`.
3. Call `sdk.start()`.
4. Create a span through the global trace API.

Source-predicted result:

- the first shutdown resolves without shutting a provider;
- start still creates and registers a provider;
- the post-shutdown span reaches the exporter;
- a second shutdown is required to shut that provider.

### Case 2 — shutdown reentered during instrumentation enable

1. Supply an instrumentation configured as disabled.
2. Its synchronous `enable()` callback calls `sdk.shutdown()`.
3. At that instant no provider field exists, so shutdown captures an empty set.
4. `start()` continues and creates the provider.
5. Await the earlier shutdown promise and create a span.

Source-predicted result:

- the reentrant shutdown promise resolves;
- the later-created provider was not included;
- telemetry remains active after the resolved shutdown;
- a later shutdown is required.

## Why this matters

A resolved shutdown normally communicates a lifecycle boundary: work owned by the object has stopped or will not subsequently start. Here, startup can cross that boundary afterward.

The issue is not ordinary thread-level concurrency. `start()` is synchronous, but it invokes user-controlled synchronous callbacks. Those callbacks can reenter the SDK.

The narrow `_startAttempted` guard in fork PR #2 does not address this. It prevents another start call; it does not coordinate start with shutdown.

## Possible contracts

### A. Shutdown is terminal even before start

- `shutdown()` moves the object to a terminal state.
- a later `start()` warns and returns or throws before side effects.
- simple, but changes current shutdown-before-start behavior.

### B. Shutdown requested during start is deferred

- startup records a `starting` state;
- reentrant shutdown returns a promise tied to startup completion and provider shutdown;
- startup either completes and immediately shuts down or aborts with owned cleanup;
- strongest lifecycle semantics, but requires a real state machine and failure handling.

### C. Invalid ordering fails explicitly

- shutdown during start returns a rejected promise;
- start after shutdown throws or no-ops;
- clear, but potentially disruptive and still requires the start path to detect terminal state.

### D. Document the ordering as unsupported

- smallest implementation burden;
- weak protection because the SDK itself invokes user callbacks during startup and currently exposes no state query or guard.

## Current recommendation

Do not expand the narrow start-guard PR yet. Retain this as a separate state-machine lead under the process-global lifecycle design work until the characterization test runs and compatibility expectations are checked.

A future design should make these transitions explicit:

```text
new -> starting -> running | failed
new -> shutdown
starting + shutdown request -> terminal outcome with one shared promise
running -> shutting-down -> shutdown
```

The key invariant should be: after a shutdown promise resolves, that helper object cannot subsequently install or expose newly running providers.

## Negative result: logger startup ordering

A separate lead considered whether instrumentations retain a no-op logger because registration occurs before NodeSDK installs the logger provider.

That concern is not supported. The logs API returns a `ProxyLoggerProvider` before global registration, and first registration installs the real provider as its delegate. Existing proxy loggers can resolve through that delegate:

https://redirect.github.com/open-telemetry/opentelemetry-js/blob/7b06368b7362a30ca69c178f43bd94dfbb36f85d/experimental/packages/api-logs/src/api/logs.ts#L20-L59

https://redirect.github.com/open-telemetry/opentelemetry-js/blob/7b06368b7362a30ca69c178f43bd94dfbb36f85d/experimental/packages/api-logs/src/ProxyLoggerProvider.ts#L14-L54

The explicit provider reassignment in NodeSDK remains metrics-specific; the logger ordering is not promoted as a defect.

## Validation boundary

The test source has been added to the fork, but dependencies are unavailable in the current work environment and no passing CI run is claimed.

Local command:

```bash
npm ci
npm run compile
npm test --workspace=@opentelemetry/sdk-node -- --grep "NodeSDK shutdown/start interleaving characterization"
```

## Contact boundary

No upstream issue, pull request, comment, review, reaction, or direct backlink was created.