# Potential PR draft: guard NodeSDK against repeated start

## Title

`fix(sdk-node): make NodeSDK start idempotent`

## Summary

Prevent one `NodeSDK` instance from running its initialization sequence more than once.

Today, a repeated `start()` call can leave the SDK object and the global APIs owning different providers:

- tracing and logs keep the first global provider while the SDK stores a newly constructed provider;
- metrics can throw while rebinding the configured reader, after earlier startup work has already begun;
- instrumentation, context, propagation, and resource setup are attempted again.

This change adds an instance start-state guard before any registration side effects. Later calls emit a diagnostic warning and return without rebuilding providers or repeating registration.

## Proposed behavior

- The first `start()` behaves as before.
- Later `start()` calls on the same instance are safe no-ops.
- The SDK continues to own the providers established by the first call.
- `shutdown()` therefore targets the providers used by the global APIs.
- Starting a different SDK instance after shutdown remains outside this narrow change.

## Proposed source change

```diff
diff --git a/experimental/packages/opentelemetry-sdk-node/src/sdk.ts b/experimental/packages/opentelemetry-sdk-node/src/sdk.ts
@@
   private _disabled?: boolean;
+  private _started = false;
@@
   public start(): void {
     if (this._disabled) {
       return;
     }
+
+    if (this._started) {
+      diag.warn('NodeSDK.start() called more than once. Ignoring.');
+      return;
+    }
+    this._started = true;
 
     registerInstrumentations({
```

The flag is set before registration begins. If initialization throws after partial side effects, the same object cannot repeat the sequence and compound the mixed state. The failure-recovery contract should be documented explicitly if maintainers prefer a different policy.

## Tests

Add focused SDK-node tests covering:

1. trace-only repeated start retains one provider and one shutdown owner;
2. log-only repeated start retains one provider and one shutdown owner;
3. metric-only repeated start does not attempt to bind the reader again;
4. instrumentation registration is invoked once;
5. context and propagation setup occur once;
6. a diagnostic warning is emitted on the repeated call;
7. `shutdown()` after a repeated call shuts down the first provider exactly once.

## Compatibility

This changes only unsupported or ambiguous repeated initialization. Normal one-start process-lifetime usage is unchanged.

A warning plus no-op is less disruptive than introducing a new synchronous exception from `start()`. If the desired contract is fail-fast, the same guard can throw before side effects instead.

## Validation

```bash
npm ci
npm run compile
npm test --workspace=@opentelemetry/sdk-node
```

Characterization branch: `fieldwork/nodesdk-shutdown-lifecycle-characterization`

Draft characterization PR: https://redirect.github.com/teamleaderleo/opentelemetry-js/pull/1

## Out of scope

- unregistering globals during `shutdown()`;
- unpatching all instrumentations during provider shutdown;
- supporting start → shutdown → start with the same instance;
- replacing a global SDK installed by another `NodeSDK` instance;
- changing provider-level shutdown semantics.

## Contact boundary

This is a Fieldwork draft only. No upstream issue or PR has been opened.