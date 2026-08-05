# NodeSDK lifecycle decision record

## Status

- Date: 2026-07-30
- OpenTelemetry JS base: `7b06368b7362a30ca69c178f43bd94dfbb36f85d`
- Characterization branch: `fieldwork/nodesdk-shutdown-lifecycle-characterization`
- Characterization draft PR: https://redirect.github.com/teamleaderleo/opentelemetry-js/pull/1
- Fix trial branch: `fieldwork/nodesdk-start-state-guard`
- Fix trial draft PR: https://redirect.github.com/teamleaderleo/opentelemetry-js/pull/2
- Upstream contact authorized: `false`
- Upstream contact performed: `false`

## Decision summary

The lifecycle problem is real, but it is not one bug with one safe all-purpose cleanup call.

The work now separates three layers:

1. **One object can start more than once.** This is narrow, directly reproducible, and safely preventable with an instance-level one-attempt guard.
2. **The package installs process-global components without ownership handles.** This affects multiple `NodeSDK` objects and the newer `startNodeSDK()` function. It cannot be safely solved by blindly calling every global `disable()` method during provider shutdown.
3. **The trace provider does not enforce its own shutdown boundary.** Repeated provider shutdown can reach custom processors repeatedly, and custom processors can still receive spans after shutdown.

The recommended first patch is the implemented one-attempt guard. Broader cleanup and trace-provider shutdown behavior should remain separate changes.

## Implemented first patch

Draft fork PR #2 adds:

```ts
private _startAttempted = false;

public start(): void {
  if (this._disabled) {
    return;
  }

  if (this._startAttempted) {
    diag.warn('NodeSDK.start() may only be called once.');
    return;
  }
  this._startAttempted = true;

  // existing initialization
}
```

The flag is set before instrumentation registration, context-manager enablement, propagation setup, resource detection, or provider construction.

This timing is deliberate. Setting the flag only after successful startup would not prevent:

- reentrant `start()` calls from instrumentation or context-manager callbacks;
- a second attempt after a first attempt partially mutated process state and then threw;
- repeated resource and registration side effects during recovery attempts.

The guard therefore means **one start attempt per `NodeSDK` object**, not one successful start.

## Why warning plus no-op

A synchronous exception would be defensible, but warning plus no-op is the lower-risk compatibility change:

- normal one-start applications are unchanged;
- accidental repeated initialization no longer corrupts ownership;
- applications that currently reach initialization twice do not begin crashing solely because the SDK became stricter;
- the diagnostic still exposes the mistake.

A future major version could choose a thrown lifecycle error, but that is not required to stop the current mixed state.

## Why the guard must not reset on shutdown

Resetting `_startAttempted` during `shutdown()` would re-enable the exact broken path:

- shutdown closes providers but leaves global registrations installed;
- a later start constructs new providers;
- duplicate global registration leaves the old shutdown providers active;
- the SDK object stores and later shuts the new providers instead.

Restart cannot be supported by clearing one boolean. It requires owned removal or replacement of every installed global component and a defined instrumentation policy.

## Why shutdown must not blindly disable globals

The API exposes broad process-global operations such as `context.disable()`, `trace.disable()`, `metrics.disable()`, `logs.disable()`, and `propagation.disable()`.

Calling these from `NodeSDK.shutdown()` is unsafe without ownership checks:

- the component might have been registered before NodeSDK started;
- another SDK or library may own the current global;
- registration may have failed, leaving a different component global;
- a callback during startup may have changed a global;
- multiple package copies can bypass package-local ownership state.

A shutdown helper should never remove a component merely because it attempted registration. It needs proof that the current global is the exact component it installed.

The present APIs do not consistently provide conditional unregister handles.

## Why the instrumentation disposer is not yet safe for NodeSDK shutdown

`registerInstrumentations()` returns a function that disables every supplied instrumentation.

That disposer does not record whether an instrumentation was already enabled before registration. Registration normally leaves already-enabled instrumentation enabled, but the disposer later disables it unconditionally.

Therefore retaining the current disposer and calling it from `NodeSDK.shutdown()` would let NodeSDK disable instrumentation it did not enable or exclusively own.

A safe installation disposer would need to restore prior state, including:

- whether each instrumentation was enabled;
- which tracer, meter, and logger providers it previously referenced;
- whether NodeSDK patched or merely adopted the instrumentation.

The current `Instrumentation` interface exposes provider setters but not provider getters or a general state snapshot, so complete restoration is not currently possible.

## `startNodeSDK()` duplicates the ownership problem

The newer function-based startup path has separate lifecycle code rather than sharing the `NodeSDK` implementation.

Current behavior:

1. register instrumentations;
2. create and enable a context manager and construct providers;
3. return `NOOP_SDK` if component creation throws;
4. register global components without checking registration success;
5. return a shutdown closure that closes providers only.

Consequences now characterized in the fork:

- component creation can fail after instrumentation was enabled;
- the newly enabled context manager is not disabled on creation failure;
- invoking `startNodeSDK()` twice enables a second context manager even though global registration rejects it;
- the returned shutdown closures do not disable either context manager;
- multiple function calls can construct providers that never become global but are still owned by the returned shutdown handle.

A class-only guard is therefore necessary but not sufficient for the whole package.

## Construction is not transactional

`MeterProvider` binds readers one-by-one in its constructor. If a later reader throws because it is already bound, earlier readers remain bound to the partially constructed provider.

In NodeSDK, the local `MeterProvider` is assigned to `_meterProvider` only after construction completes. When construction throws:

- `_meterProvider` remains undefined;
- `NodeSDK.shutdown()` cannot reach the partially constructed provider;
- earlier readers remain permanently bound and cannot be attached elsewhere;
- context and instrumentation work performed before meter construction also remains.

This cannot be completely repaired only inside NodeSDK because the metric reader API has no validation or unbind transaction.

## Trace-provider shutdown is a lower-level contract issue

The trace SDK provider delegates `shutdown()` directly to `MultiSpanProcessor` and does not record provider shutdown state.

Characterization now shows:

- calling `NodeSDK.shutdown()` twice calls a custom span processor's `shutdown()` twice;
- after shutdown, the globally installed trace provider can still create normal spans;
- those spans continue reaching a custom span processor after its shutdown method ran.

Standard processors often hide this because they have their own one-shot guards, but custom processors are allowed and expose the provider-level gap.

The trace SDK specification says provider shutdown must be called only once and that post-shutdown tracer acquisition should return no-op behavior when possible. This points to a fix in `TracerProvider`, not merely a NodeSDK wrapper workaround.

## Lifecycle model recommended for the package

For each helper instance:

```text
new -> start-attempted -> running | failed -> shutdown
```

Rules:

- `start()` may transition out of `new` only once.
- Reentrant or later starts warn and return before side effects.
- A failed start remains failed; recovery uses a new object after process cleanup, not the partially mutated object.
- `shutdown()` is idempotent and returns the same completion result to concurrent or repeated callers.
- `shutdown()` closes providers owned by the helper.
- `shutdown()` does not imply process-global uninstallation unless an explicit ownership/disposal contract is added.
- Restart is unsupported until installation disposal exists.

For the package as a whole, documentation should state that initialization is intended once near process startup and shutdown near process exit.

## Longer-term architecture

The clean long-term design is an installation handle distinct from provider shutdown.

Conceptually:

```ts
interface SDKInstallation {
  shutdown(): Promise<void>; // flush and close providers
  dispose(): Promise<void>;  // remove only globals and patches owned by this installation
}
```

A safe `dispose()` requires registration APIs to return ownership-aware handles, for example:

```ts
const registration = context.register(contextManager);
registration.dispose(); // succeeds only for the component installed by this handle
```

Instrumentation registration similarly needs a state-aware disposer that restores prior state rather than disabling everything passed to it.

Until those primitives exist, documenting process-lifetime installation and preventing repeated starts is safer than simulating restart support.

## Recommended change sequence

1. **Land the instance one-attempt guard.** Small, compatible, and directly evidence-backed.
2. **Add trace-provider shutdown state.** Make shutdown one-shot and return no-op tracers or suppress processor callbacks after shutdown.
3. **Harden `startNodeSDK()` failure cleanup.** At minimum disable the context manager it enabled and avoid claiming `NOOP_SDK` when side effects remain.
4. **Define package-level duplicate initialization behavior.** Decide whether a second helper should throw, return a no-op handle, or adopt the existing installation.
5. **Design ownership-aware registration/disposal primitives.** Do not use broad global disable calls as a substitute.
6. **Address metric-construction transactionality in the metrics SDK.** Add validation or rollback support for reader binding.

## Validation boundary

The fork changes have been reviewed against current source and type shapes. No package dependencies are installed in the work container and the fork has no visible GitHub Actions runs, so full test execution is not claimed.

Local commands:

```bash
npm ci
npm run compile
npm test --workspace=@opentelemetry/sdk-node
```

No upstream issue, pull request, comment, review, reaction, or direct backlink was created.
