# Cross-language comparison: OpenTelemetry initialization and shutdown lifecycle

## Scope and caution

This is a source comparison, not a claim that every OpenTelemetry language SDK has the same bug.

The JavaScript findings concern a particular combination:

1. process-global registration may reject replacement;
2. the convenience helper ignores that result;
3. the helper still stores newly created providers privately;
4. shutdown later targets the private providers rather than necessarily the active globals.

Other languages make different choices. Those choices provide design precedent and test ideas, but they do not automatically transfer implementation details to JavaScript.

## JavaScript

### Global installation

The API global registration functions return success or failure. NodeSDK currently ignores these results while storing newly constructed providers in private fields.

Pinned implementation:

https://redirect.github.com/open-telemetry/opentelemetry-js/blob/7b06368b7362a30ca69c178f43bd94dfbb36f85d/experimental/packages/opentelemetry-sdk-node/src/sdk.ts#L248-L363

### Shutdown

NodeSDK shuts down the provider objects in its private fields. It does not verify that they are the providers used by the global APIs.

https://redirect.github.com/open-telemetry/opentelemetry-js/blob/7b06368b7362a30ca69c178f43bd94dfbb36f85d/experimental/packages/opentelemetry-sdk-node/src/sdk.ts#L365-L381

The base trace provider delegates shutdown directly to its processor collection and has no provider-level shutdown state.

https://redirect.github.com/open-telemetry/opentelemetry-js/blob/7b06368b7362a30ca69c178f43bd94dfbb36f85d/packages/sdk-trace/src/TracerProvider.ts#L148-L150

### Characterized result

- repeated same-object start can split global and private ownership;
- different SDK objects can create rejected but privately retained providers;
- custom trace processors can receive repeated shutdown and post-shutdown spans;
- the metrics constructor can partially bind readers before throwing.

## Java

### Global installation

Java documents the global as a set-once operation and throws on a second call. It also recommends passing `OpenTelemetry` instances explicitly rather than relying on the global where practical.

https://redirect.github.com/open-telemetry/opentelemetry-java/blob/6ffe557f36f6d1150556c9e95bfea9fc20e3a49e/api/all/src/main/java/io/opentelemetry/api/GlobalOpenTelemetry.java#L30-L62

https://redirect.github.com/open-telemetry/opentelemetry-java/blob/6ffe557f36f6d1150556c9e95bfea9fc20e3a49e/api/all/src/main/java/io/opentelemetry/api/GlobalOpenTelemetry.java#L162-L185

A reset exists explicitly for tests, not as an ordinary application lifecycle operation:

https://redirect.github.com/open-telemetry/opentelemetry-java/blob/6ffe557f36f6d1150556c9e95bfea9fc20e3a49e/api/all/src/main/java/io/opentelemetry/api/GlobalOpenTelemetry.java#L289-L295

### Shutdown

The aggregate Java SDK uses an `AtomicBoolean` to make shutdown one-shot and returns success on later calls.

https://redirect.github.com/open-telemetry/opentelemetry-java/blob/6ffe557f36f6d1150556c9e95bfea9fc20e3a49e/sdk/all/src/main/java/io/opentelemetry/sdk/OpenTelemetrySdk.java#L101-L117

### Design lesson for JavaScript

Java demonstrates a coherent strict-singleton model:

- duplicate global setup fails explicitly;
- test reset is clearly exceptional;
- aggregate shutdown is one-shot.

The JavaScript start-attempt guard follows the same broad direction without requiring JavaScript globals to throw.

## Go

### Global installation

Go allows the global tracer and meter providers to be replaced. The first replacement also updates previously returned default delegating providers; subsequent calls update the current global value.

https://redirect.github.com/open-telemetry/opentelemetry-go/blob/2776cee15126f0841bd65ad205f576b240883a24/internal/global/state.go#L66-L93

https://redirect.github.com/open-telemetry/opentelemetry-go/blob/2776cee15126f0841bd65ad205f576b240883a24/internal/global/state.go#L127-L153

### Shutdown

Go's trace provider uses atomic state and a lock to make shutdown safe under repeated, recursive, and concurrent calls. It shuts each processor once, clears the processor set, and documents that all provider methods become no-ops after shutdown.

https://redirect.github.com/open-telemetry/opentelemetry-go/blob/2776cee15126f0841bd65ad205f576b240883a24/sdk/trace/provider.go#L297-L328

### Design lesson for JavaScript

Global replacement can be supported, but only when it is an explicit API contract. It does not emerge safely from ignoring registration failure. Go also provides strong precedent for provider-level one-shot shutdown.

## Python

### Global installation

Python uses set-once global providers and emits warnings such as `Overriding of current TracerProvider is not allowed` when initialization repeats.

A real Streamlit report shows the same process being rerun and attempting provider and instrumentation setup multiple times:

https://redirect.github.com/open-telemetry/opentelemetry-python/issues/3743

A maintainer response describes global provider and instrumentor setup as work intended to happen once per Python process:

https://redirect.github.com/open-telemetry/opentelemetry-python/issues/3743#issuecomment-2045465437

A second maintainer response notes that providers and other components are not meant to be instantiated repeatedly and warns about duplicate telemetry and growing thread creation:

https://redirect.github.com/open-telemetry/opentelemetry-python/issues/3743#issuecomment-2048110009

### Shutdown

The Python tracer provider directly calls its active span processor's shutdown and unregisters its exit hook. The provider itself does not visibly guard repeated shutdown in this method.

https://redirect.github.com/open-telemetry/opentelemetry-python/blob/3381a88ec5a2480a60edbeb4f4441599c97dab1b/opentelemetry-sdk/src/opentelemetry/sdk/trace/__init__.py#L1477-L1484

A 2026 test-flakiness issue includes repeated global-provider warnings and `cannot schedule new futures after shutdown` during repeated shutdown paths:

https://redirect.github.com/open-telemetry/opentelemetry-python/issues/5113

### Design lesson for JavaScript

Python shows that hot-reload and persistent-process rerun environments create real lifecycle pressure across languages. It also shows that warning-only singleton enforcement can still leave users confused when setup helpers are not explicitly idempotent.

This does not prove that Python has the exact JavaScript ownership bug.

## .NET

### Ownership model

The .NET trace provider records owned instrumentation instances and disposes them, its processor, listener, sampler, and optionally its owned service provider. Disposal is guarded by a provider-level `Disposed` flag.

https://redirect.github.com/open-telemetry/opentelemetry-dotnet/blob/53af1101f36261b85c903ce6f0488ea1bf0efedc/src/OpenTelemetry/Trace/TracerProviderSdk.cs#L18-L27

https://redirect.github.com/open-telemetry/opentelemetry-dotnet/blob/53af1101f36261b85c903ce6f0488ea1bf0efedc/src/OpenTelemetry/Trace/TracerProviderSdk.cs#L341-L390

### Design lesson for JavaScript

Instrumentation disposal is much safer when ownership is explicit and objects participate in a standard disposal interface. JavaScript's current instrumentation registration disposer lacks equivalent per-item ownership information, so copying .NET's cleanup behavior without redesign would be unsafe.

## Rust

### Global installation

Rust allows replacement of the global tracer provider under a write lock.

https://redirect.github.com/open-telemetry/opentelemetry-rust/blob/0e78170d712e5046b8ed93b6f99b2b003af15cd7/opentelemetry/src/global/trace.rs#L426-L443

Its documentation also recommends retaining a provider clone when the application will later need to shut it down, separating global access from lifecycle ownership.

https://redirect.github.com/open-telemetry/opentelemetry-rust/blob/0e78170d712e5046b8ed93b6f99b2b003af15cd7/opentelemetry/src/global/mod.rs#L114-L129

### Shutdown

Rust uses atomic shutdown state. A repeated shutdown returns `AlreadyShutdown`, and requesting a tracer after shutdown produces a no-op tracer.

https://redirect.github.com/open-telemetry/opentelemetry-rust/blob/0e78170d712e5046b8ed93b6f99b2b003af15cd7/opentelemetry-sdk/src/trace/provider.rs#L245-L298

### Design lesson for JavaScript

Rust provides strong precedent for putting shutdown state in the provider itself rather than relying on every processor or calling helper to guard repeated and post-shutdown behavior.

## Comparison matrix

| Language | Global policy | Duplicate setup response | Provider shutdown | Post-shutdown tracer behavior | Relevant lesson |
| --- | --- | --- | --- | --- | --- |
| JavaScript | First registration retained by API globals | Helper often ignores rejection | Trace provider not one-shot | Can remain functional with custom processor | Fix helper bookkeeping and provider shutdown separately |
| Java | Set once | Throws | Aggregate SDK one-shot | Provider-specific | Strict singleton is an established option |
| Go | Replacement supported | Explicit replacement | One-shot; all methods no-op | No-op | Replacement requires deliberate global design |
| Python | Set once | Warning | Direct processor shutdown | Not clearly provider-guarded | Persistent-process reruns are a real user scenario |
| .NET | DI/provider ownership | Provider construction through service graph | Guarded disposal | Listener disposed | Cleanup is safer with explicit ownership |
| Rust | Replacement supported | Explicit replacement | Atomic; repeated call errors | New tracer is no-op | Strong provider-level shutdown precedent |

## Conclusion

The JavaScript finding is not merely that globals are singletons. Singletons are common across OpenTelemetry implementations.

The specific defect is that the JavaScript helper can lose agreement with the global APIs after registration rejection and then use its private disagreement to decide shutdown ownership.

The cross-language evidence supports three separate directions:

1. make convenience-helper initialization deterministic and one-shot unless replacement is explicitly supported;
2. enforce provider shutdown state at the provider layer;
3. require explicit ownership before uninstalling globals or instrumentation.

## Contact boundary

All references use redirect links. No upstream project was contacted.