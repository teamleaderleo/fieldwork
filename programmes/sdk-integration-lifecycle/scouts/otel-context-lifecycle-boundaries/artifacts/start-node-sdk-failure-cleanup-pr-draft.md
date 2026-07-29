# Fix PR draft and fork trial: clean up failed startNodeSDK creation

## Status

- Draft implemented in user-owned fork: https://redirect.github.com/teamleaderleo/opentelemetry-js/pull/3
- Branch: `fieldwork/start-node-sdk-failure-cleanup`
- Base: `7b06368b7362a30ca69c178f43bd94dfbb36f85d`
- Source commit: `2ed8f4b846fc4a62d0e724e43264e7036d7065e7`
- Test commit: `3f79d0d93155edd82174d161caafd650aefdcfd7`
- Upstream issue or PR opened: `false`

## Title

`fix(sdk-node): clean up failed startNodeSDK creation`

## Problem

The experimental `startNodeSDK()` function currently registers supplied instrumentations before it creates SDK components.

If component creation throws, the function logs an error and returns `NOOP_SDK`, but:

- an initially disabled instrumentation may already have been enabled;
- a context manager has already been constructed and enabled;
- the context manager is not globally registered and is not disabled;
- the returned no-op shutdown function cannot reach either side effect.

The return value therefore overstates the amount of rollback performed.

## Implemented change

The fork trial makes two small ordering and cleanup changes:

1. move `registerInstrumentations()` until after component creation and global setup succeed;
2. call `components.contextManager.disable()` in the component-creation catch path.

Source diff shape:

```diff
-  registerInstrumentations({
-    instrumentations: sdkOptions?.instrumentations?.flat() ?? [],
-  });
-
   let components: SDKComponents;
   try {
     components = create(config, sdkOptions);
@@
   if (components.propagator) {
     propagation.setGlobalPropagator(components.propagator);
   }
+
+  registerInstrumentations({
+    instrumentations: sdkOptions?.instrumentations?.flat() ?? [],
+  });
@@
   } catch (createErr) {
     // Clean up any SDK components that were created before the error.
+    if (components.contextManager) {
+      components.contextManager.disable();
+    }
```

## Why move registration instead of calling the disposer on failure

The current instrumentation disposer disables every supplied instrumentation.

An instrumentation may have been enabled before `startNodeSDK()` received it. Registration does not re-enable that instrumentation, but the disposer would still disable it. Calling the disposer in the catch path would therefore let failed SDK setup disable externally established instrumentation state.

Delaying registration avoids creating that ownership problem on component-creation failure.

## Successful-path effect

Instrumentation registration still occurs synchronously before `startNodeSDK()` returns.

Because global providers are installed first, `registerInstrumentations()` observes the provider configuration that the process will actually use. This is also preferable for metrics, whose API does not use the same delegate proxy model as tracing.

## Tests implemented

File:

`experimental/packages/opentelemetry-sdk-node/test/start-failure-cleanup.test.ts`

Cases:

1. a configuration that fails component creation returns `NOOP_SDK`, does not enable the supplied instrumentation, and disables the context manager created during the failed attempt;
2. successful component setup still registers and enables the supplied instrumentation.

## Scope

This patch does not solve:

- calling `startNodeSDK()` successfully more than once;
- global registration result handling;
- provider cleanup when global registration is rejected;
- instrumentation disposal during normal shutdown;
- a `MeterProvider` constructor that binds some readers before a later reader throws;
- trace-provider shutdown state.

## Validation

```bash
npm ci
npm run compile
npm test --workspace=@opentelemetry/sdk-node -- --grep "startNodeSDK failure cleanup"
```

Source and type-shape review is complete. The work container cannot install repository dependencies, and no GitHub Actions run is visible for the fork commit, so the package suite is not claimed as passing.

## Contact boundary

The implementation exists only in the user-owned fork. No upstream issue, pull request, comment, review, reaction, or direct backlink was created.
