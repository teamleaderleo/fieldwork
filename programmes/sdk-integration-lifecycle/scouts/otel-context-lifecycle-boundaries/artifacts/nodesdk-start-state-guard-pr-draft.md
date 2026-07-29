# Fix PR draft and fork trial: guard NodeSDK start attempts

## Status

- Draft implemented in user-owned fork: https://redirect.github.com/teamleaderleo/opentelemetry-js/pull/2
- Branch: `fieldwork/nodesdk-start-state-guard`
- Base: `7b06368b7362a30ca69c178f43bd94dfbb36f85d`
- Source commit: `91fd86e3e727522dc3dfd62a134657fdfa921436`
- Test commit: `14b524ff0c0d8e39321c31be218b0c9ee0ca0b78`
- Upstream issue or PR opened: `false`

## Title

`fix(sdk-node): guard repeated start attempts`

## Summary

Prevent one `NodeSDK` object from running its initialization sequence more than once.

Today, a repeated `start()` can leave the SDK object and process-global APIs owning different providers:

- tracing and logs keep provider A global while the SDK stores provider B;
- metrics can throw while rebinding configured readers after preceding startup side effects;
- instrumentation, context, propagation, and resource setup are attempted again;
- a start after shutdown constructs private providers while globals remain attached to the first shutdown providers.

The fork trial adds a one-attempt guard before any registration side effect. Later calls emit a diagnostic warning and return.

## Implemented source change

```diff
diff --git a/experimental/packages/opentelemetry-sdk-node/src/sdk.ts b/experimental/packages/opentelemetry-sdk-node/src/sdk.ts
@@
   private _disabled?: boolean;
+  private _startAttempted = false;
@@
   public start(): void {
     if (this._disabled) {
       return;
     }
+
+    if (this._startAttempted) {
+      diag.warn('NodeSDK.start() may only be called once.');
+      return;
+    }
+    this._startAttempted = true;
 
     registerInstrumentations({
```

The property is named `_startAttempted`, not `_started`, because it is set before initialization can succeed or fail.

## Behavior

- The first start attempt behaves as before.
- Reentrant calls are blocked before registration repeats.
- Later direct calls are warning no-ops.
- A call after shutdown is a warning no-op.
- A second call after the first attempt throws is a warning no-op.
- Recovery after partial startup failure requires a new object and explicit process cleanup; the partially mutated object is not treated as safely retryable.

## Why set the guard before side effects

Setting the flag after successful startup would leave two holes:

1. A context manager or instrumentation callback could call `start()` reentrantly while the first call is still running.
2. A first call could register instrumentation or context and then throw during provider construction. Retrying the same object would compound partial state.

The one-attempt guard closes both.

## Why warning plus no-op instead of throw

Repeated startup is unsupported or ambiguous behavior, but changing it to a synchronous exception could break applications that currently initialize twice accidentally.

A warning plus no-op:

- prevents ownership corruption;
- preserves normal one-start behavior;
- avoids introducing a new crash path;
- still provides diagnostics.

A future major version could choose a thrown lifecycle error if maintainers want stricter behavior.

## Tests implemented

File:

`experimental/packages/opentelemetry-sdk-node/test/start-state-guard.test.ts`

Cases:

1. repeated start retains the first private tracer provider and performs one global registration;
2. start after shutdown does not create another provider;
3. reentrant start from context-manager enablement is blocked before provider registration repeats;
4. a second call after a startup exception does not repeat the failing side effect.

## Compatibility

This changes only repeated initialization on one object. Normal process-lifetime usage is unchanged.

The change does not claim to support restart. The guard intentionally remains set after shutdown because shutdown does not currently unregister globals or dispose instrumentation installation.

## Validation

```bash
npm ci
npm run compile
npm test --workspace=@opentelemetry/sdk-node -- --grep "NodeSDK start-state guard"
```

Source and type-shape review is complete. The work container cannot install repository dependencies, and no GitHub Actions run is visible for the fork commit, so the package suite is not claimed as passing.

## Out of scope

- replacing or rejecting a different `NodeSDK` object;
- repeated calls to the newer `startNodeSDK()` function;
- unregistering globals during shutdown;
- disabling instrumentations during provider shutdown;
- metric-reader constructor rollback;
- trace-provider shutdown state and idempotence;
- full start → shutdown → start support.

These are covered in `nodesdk-lifecycle-decision-record.md` and `nodesdk-followup-lifecycle-findings.md`.

## Contact boundary

The implementation exists only in the user-owned fork. No upstream issue, pull request, comment, review, reaction, or direct backlink was created.
