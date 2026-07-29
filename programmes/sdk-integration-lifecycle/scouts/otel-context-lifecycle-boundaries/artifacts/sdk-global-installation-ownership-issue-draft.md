# Potential design issue draft: define SDK global installation ownership

## Title

Define process-global ownership, duplicate initialization, and disposal semantics for Node SDK helpers

## Scope

- Packages: `@opentelemetry/sdk-node`, `@opentelemetry/api`, `@opentelemetry/instrumentation`
- Helpers: `NodeSDK` and experimental `startNodeSDK()`
- Draft only; not submitted

## Summary

The Node SDK convenience helpers create process-wide components, register API globals, enable context management, configure instrumentation, and retain provider objects for later shutdown.

The current APIs do not define one complete ownership model for those operations.

Questions that appear simple—such as “can I start twice?”, “can a second SDK replace the first?”, or “should shutdown unpatch instrumentation?”—have different answers depending on which component is considered and whether registration succeeded.

This issue would define the lifecycle contract before attempting broad cleanup or restart support.

## Concrete findings motivating the design discussion

### Same-object repeated start

A repeated `NodeSDK.start()` can leave global provider A active while the SDK object stores provider B and later shuts down B.

Narrow fix trial:

https://redirect.github.com/teamleaderleo/opentelemetry-js/pull/2

### Function creation failure

`startNodeSDK()` can return `NOOP_SDK` after setup side effects. A separate narrow trial delays instrumentation and cleans the newly created context manager on failure:

https://redirect.github.com/teamleaderleo/opentelemetry-js/pull/3

### Rejected registration ownership

Context, propagation, trace, metrics, and logs do not all expose or behave with the same registration result. A helper can create and retain components that did not become the active global components.

### Instrumentation disposal ownership

`registerInstrumentations()` returns a disposer that disables every supplied instrumentation. Registration itself only enables instrumentation that was disabled. Therefore the disposer can disable an instrumentation that was already enabled and owned outside the SDK helper.

https://redirect.github.com/open-telemetry/opentelemetry-js/blob/7b06368b7362a30ca69c178f43bd94dfbb36f85d/experimental/packages/opentelemetry-instrumentation/src/autoLoader.ts#L16-L40

https://redirect.github.com/open-telemetry/opentelemetry-js/blob/7b06368b7362a30ca69c178f43bd94dfbb36f85d/experimental/packages/opentelemetry-instrumentation/src/autoLoaderUtils.ts#L18-L53

## Historical user reports

### JavaScript: auto plus manual initialization

Issue #4804 reported duplicate registration errors. The root cause was initializing through `--require @opentelemetry/auto-instrumentations-node/register` and also calling `NodeSDK.start()` manually.

https://redirect.github.com/open-telemetry/opentelemetry-js/issues/4804

The discussion explicitly asked whether the SDK was being registered twice, and the reporter confirmed the auto-plus-manual setup was the cause:

https://redirect.github.com/open-telemetry/opentelemetry-js/issues/4804#issuecomment-2178006532

https://redirect.github.com/open-telemetry/opentelemetry-js/issues/4804#issuecomment-2178704154

This prior report established duplicate initialization as an application configuration problem. The new Fieldwork finding adds that the helper's internal response to duplicate or rejected registration can itself become inconsistent.

### Python: persistent-process reruns

A Streamlit user reported repeated provider and instrumentation setup because the framework reruns code in the same process:

https://redirect.github.com/open-telemetry/opentelemetry-python/issues/3743

Maintainers described provider and instrumentor setup as process-once operations and warned that repeated component construction can cause duplicate telemetry and growing threads:

https://redirect.github.com/open-telemetry/opentelemetry-python/issues/3743#issuecomment-2045465437

https://redirect.github.com/open-telemetry/opentelemetry-python/issues/3743#issuecomment-2048110009

This is strong evidence that notebooks, hot reloaders, and rerun frameworks are recurring lifecycle environments rather than purely hypothetical misuse.

### Java: explicit set-once global behavior

Java documents global setup as a one-time operation and throws on a second set. It also recommends checking whether the global is already set or passing instances explicitly.

https://redirect.github.com/open-telemetry/opentelemetry-java/blob/6ffe557f36f6d1150556c9e95bfea9fc20e3a49e/api/all/src/main/java/io/opentelemetry/api/GlobalOpenTelemetry.java#L30-L62

https://redirect.github.com/open-telemetry/opentelemetry-java/blob/6ffe557f36f6d1150556c9e95bfea9fc20e3a49e/api/all/src/main/java/io/opentelemetry/api/GlobalOpenTelemetry.java#L162-L185

User reports show the cost of strict set-once semantics when agents, shims, autoconfiguration, and application setup race or overlap:

https://redirect.github.com/open-telemetry/opentelemetry-java/issues/5343

https://redirect.github.com/open-telemetry/opentelemetry-java/issues/7354

The Java model is coherent, but its historical reports show that error messages and initialization ordering still need careful design.

## Questions requiring an explicit decision

### 1. What is the unit of singleton ownership?

Possible answers:

- one `NodeSDK` object may start once;
- one Node SDK helper of any kind may install globally once per process;
- multiple helpers may coexist if only one installs globals;
- globals may be replaced intentionally.

### 2. What should duplicate initialization do?

Options:

- warn and no-op before side effects;
- throw before side effects;
- return the existing installation handle;
- replace the current installation after disposing it;
- allow construction but reject global installation explicitly.

### 3. Is shutdown the same operation as disposal?

Provider shutdown normally means flush and release provider-owned resources.

Installation disposal may additionally mean:

- unregister globals;
- disable context management;
- remove propagators;
- unpatch instrumentations;
- release process listeners.

Combining these operations is convenient but unsafe without ownership proof.

### 4. How is ownership represented?

Potential approaches:

- registration tokens returned by global APIs;
- compare-and-unregister using an exact registered object identity;
- a process-global installation coordinator;
- an explicit `SDKInstallation` handle containing only successfully installed components;
- per-instrumentation enablement ownership or reference counting.

### 5. Is restart supported?

Restart should not be documented until all of the following are addressed:

- globals can be removed or replaced safely;
- context managers can be stopped safely;
- instrumentation patch ownership is tracked;
- cached tracers/meters/loggers transition coherently;
- metric readers and exporters have a reuse or recreation contract;
- concurrent start and shutdown are specified.

## Cross-language models

### Strict singleton

Java sets the global once and throws on repetition. Test reset is a separate, explicitly test-only API.

### Replaceable global

Go and Rust allow explicit global provider replacement:

https://redirect.github.com/open-telemetry/opentelemetry-go/blob/2776cee15126f0841bd65ad205f576b240883a24/internal/global/state.go#L66-L93

https://redirect.github.com/open-telemetry/opentelemetry-rust/blob/0e78170d712e5046b8ed93b6f99b2b003af15cd7/opentelemetry/src/global/trace.rs#L426-L443

Replacement is a designed API behavior in those implementations. It is not equivalent to a helper ignoring failed first-writer-wins registration.

### Explicit disposal ownership

.NET retains instrumentation and service-provider objects under the provider and disposes them with provider-level guards:

https://redirect.github.com/open-telemetry/opentelemetry-dotnet/blob/53af1101f36261b85c903ce6f0488ea1bf0efedc/src/OpenTelemetry/Trace/TracerProviderSdk.cs#L341-L390

The JavaScript instrumentation API currently does not expose equivalent per-instrumentation ownership.

## Recommended initial contract

Until ownership-aware disposal exists:

```text
new -> start-attempted -> running | failed -> shutdown
```

- one start attempt per helper object;
- no same-object restart;
- duplicate same-object calls warn and no-op before side effects;
- provider shutdown is one-shot;
- provider shutdown does not blindly unregister process globals;
- provider shutdown does not blindly disable every supplied instrumentation;
- a second helper's behavior remains explicitly unsupported or separately guarded.

## Potential future API shape

Conceptually:

```ts
const installation = installNodeSDK(options);

await installation.shutdownProviders();
await installation.disposeInstallation();
```

The installation handle would retain only components it successfully installed and could conditionally remove them if they are still owned by that installation.

The exact API is open for design; the important point is separating provider lifecycle from process installation lifecycle.

## Proposed issue outcome

The design issue should produce:

1. a documented helper state machine;
2. duplicate-initialization behavior shared by `NodeSDK` and `startNodeSDK()`;
3. a decision on shutdown versus disposal;
4. ownership requirements for global and instrumentation cleanup;
5. a clear statement on restart support;
6. a sequence of implementation PRs rather than a single broad patch.

## Supplemental deep dive

After explicit authorization, link the Fieldwork synthesis once:

https://redirect.github.com/teamleaderleo/fieldwork/pull/32

Each concrete child issue should still contain its own reproduction and source references.

## Contact boundary

No upstream issue or PR has been created.