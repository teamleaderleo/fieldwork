# OpenTelemetry JS delayed lifecycle reentry

State: `model-executed — target characterization pending`

Fieldwork lane: #216  
Parent scout: #19  
Signals worker: #194  
Target hub: #4  
Upstream contact authorized: `false`

## In simple words

The current owned OpenTelemetry lifecycle candidates correctly stop a processor or reader from calling its owner provider's shutdown method immediately inside the same synchronous callback.

That protection ends when the callback returns its promise. A custom child can wait for one microtask and then call the same owner shutdown method. The owner returns the shared shutdown promise, while that shared promise is already waiting for the child's promise. Each promise then waits for the other and the operation can remain pending forever.

The difficult part is preserving an unrelated concurrent caller. That caller should receive and await the same shared shutdown result. At the public method boundary, the unrelated caller and the delayed self-reentrant child make the same call after the same synchronous guard has cleared. A correct runtime repair needs provenance, an operation-owned timeout policy, or an interface change; suppressing every in-flight call would silently break legitimate joiners.

## Exact source identities

- core `BindOnceFuture` source base: `teamleaderleo/opentelemetry-js@7b06368b7362a30ca69c178f43bd94dfbb36f85d`
- trace one-shot candidate: `teamleaderleo/opentelemetry-js#4` at `50cd262e326c2a24419bad53c932a688b42224a4`
- logs direct-reentry candidate: `teamleaderleo/opentelemetry-js#8` at `7d49735173c8467a88afab426a4bf02910a3dd62`
- metrics composed lifecycle candidate: `teamleaderleo/opentelemetry-js#9` at `5bb520f141759ce003dc002196c43cda4fe96551`

No claim in this record applies automatically to a later target head.

## Source mechanism

### Shared owner promise

`BindOnceFuture` owns one deferred promise. On the first call it marks the operation called, invokes the callback, and resolves or rejects the deferred only after the callback's returned value settles:

```text
owner promise P
  waits for callback result Q
```

Later calls return P.

### Synchronous guard lifetime

The owned trace, logs, `MeterProvider`, and `MetricReader` candidates use the same narrow pattern:

```text
set invocation-active
invoke child shutdown and return its promise
clear invocation-active in finally
```

The `finally` executes after the child function returns Q, not after Q settles. This correctly detects a child that calls the owner synchronously during invocation. It cannot identify the same child after an `await`.

### Delayed cycle

For a delayed custom child:

```ts
async shutdown() {
  await Promise.resolve();
  return owner.shutdown();
}
```

execution becomes:

```text
P = owner shared shutdown promise
Q = async child shutdown promise

owner invokes child and starts waiting for Q
synchronous invocation flag clears
child resumes after await
child calls owner.shutdown()
owner returns P
Q adopts P

P waits for Q
Q waits for P
```

Neither side can settle without another terminal mechanism.

### Fanout does not remove the cycle

Trace and logs aggregate child shutdown promises with `Promise.all`. Metrics aggregates collectors and each collector awaits its reader. These layers preserve the dependency; they do not add independent completion authority.

### Metric timeout exception

`MetricReader.shutdown({ timeoutMillis })` wraps its `onShutdown()` promise with an operation-owned timeout before returning through `BindOnceFuture`. If that timeout fires, the shared reader promise rejects, which can unwind a delayed self-cycle.

This is materially different from a caller placing its own `Promise.race` around `shutdown()`: a caller-local deadline stops one waiter while the owner operation remains pending. `LoggerProvider.shutdown()` and `TracerProvider.shutdown()` expose no equivalent shutdown timeout option in the inspected candidates.

The metric timeout path still leaves a policy question: the underlying `onShutdown()` work may continue after the shared result rejects, and the SDK must state what ownership, export, resource, and retry behavior survives that timeout.

## Executed promise graph

Run:

```sh
node programmes/sdk-integration-lifecycle/scouts/otel-context-lifecycle-boundaries/delayed-reentry/promise-graph.mjs
```

Retained result: `results/latest.json`.

The model establishes:

1. direct synchronous recursion settles through the current invocation guard;
2. delayed same-owner recursion leaves both owner and child pending;
3. an unrelated external caller correctly joins the same owner promise;
4. cross-owner nesting settles when its dependency graph is acyclic;
5. comparing the returned child promise with the owner promise misses an async adopting wrapper;
6. a caller-local deadline leaves the owner cycle pending;
7. an operation-owned watchdog rejects the one shared result for every joined caller;
8. explicit owner provenance distinguishes self-reentry while preserving external joining;
9. suppressing every in-flight call makes the external caller return early with a different result.

Evidence class: `model-executed`.

## Why the obvious repairs fail

### Keep the active flag set until all children settle

This prevents delayed recursion only by classifying every call during shutdown as recursive. An unrelated external caller during the same interval would stop joining the shared result and could miss the actual shutdown failure.

### Compare promise identity

A directly returned P can be detected. An `async` child returns a distinct Q that adopts P. Q and P are different objects even though they form a cycle.

### Add a timeout around one caller

The caller returns, while P and Q remain pending and can retain processors, readers, exporters, timers, sockets, or other owned resources.

### Use Node async context

`AsyncLocalStorage` could carry provenance across an `await`, but OpenTelemetry JS lifecycle packages also support browser environments. A Node-only hidden dependency is not an acceptable cross-signal contract.

### Stop awaiting children

That avoids the cycle by abandoning the meaning of shutdown completion and child failure propagation.

## Contract choices

The full comparison is retained in `contract-matrix.md`.

Two directions remain credible:

### Explicit lifecycle provenance

The owner invokes each child with an internal operation token or capability. A same-owner call carrying that token fails with a typed reentry error, while a public external call still receives P.

This is portable and preserves the distinction. Current arbitrary processor and reader interfaces do not carry such provenance, so adopting it requires an internal adapter or interface contract change.

### Operation-owned timeout

The shared owner operation has a named timeout and terminal unfinished-cleanup policy. Every caller receives the same timeout result, and the child promise unwinds when P rejects.

This is portable. It introduces compatibility and resource-ownership decisions for valid slow cleanup. Metrics has part of this mechanism; trace and logs do not expose it in the inspected candidates.

## Minimum compatible rule

Until a runtime mechanism is selected:

> A lifecycle child must not await the shutdown or force-flush promise of the same owner whose lifecycle callback is currently awaiting that child.

This should be stated as a lifecycle contract, not as proof that the runtime is protected from violations.

## Required target characterizations

Add direct tests on exact owned candidate heads for:

1. delayed same-owner shutdown from a trace processor;
2. delayed same-owner force flush during trace shutdown;
3. delayed same-owner shutdown and force flush from a log processor;
4. delayed `MeterProvider.shutdown()` from a custom reader path;
5. delayed `MetricReader.shutdown()` from `onShutdown()` without a timeout;
6. the same reader case with a short operation-owned timeout;
7. unrelated external callers joining during each delayed child;
8. cross-provider nesting as a passing control;
9. cleanup failure after a timeout, with no unhandled rejection;
10. no duplicate child shutdown, export, or final collection.

Each hanging case must use a bounded test watchdog and assert the inner ownership state rather than leaving the suite process pending.

## Current disposition

**ACCEPT the mechanism and model. HOLD a production repair. EXECUTE target characterization.**

The source and model establish a real promise dependency class in the owned one-shot candidates. They do not yet establish a released-package failure or choose a compatible cross-signal repair.

Target execution should decide whether the first durable output is:

- a documented prohibition plus regression characterizations;
- a deliberate provider-wide timeout contract;
- an explicit lifecycle provenance design;
- or a held limitation with no safe narrow implementation.

## Adjacent inquiries

This result exposes several useful follow-ons without merging them into #216:

1. **Timeout aftermath ownership** — what work may continue after `MetricReader.shutdown()` rejects from its operation timeout, and how is later exporter failure observed?
2. **Cross-signal lifecycle cycles** — a log processor, span processor, or metric exporter may call another provider whose child calls back into the first owner.
3. **Global installation disposal** — provider shutdown and global API unregistration remain different owners; delayed reentry can cross that boundary.
4. **Context-manager teardown** — disabling the context manager while processor/exporter callbacks still depend on active context can create a separate ordering problem.
5. **Resource async attributes during shutdown** — final export may wait on async resource attributes that call instrumented services owning the same teardown path.
6. **Error aggregation after timeout** — an operation timeout can become primary while later child cleanup failures still need observation without changing the public result.

These should enter the growing queue when each has a bounded question and evidence owner.

## Evidence boundary

- exact source mechanism: `source-read`;
- promise dependency outcomes and candidate comparison: `model-executed`;
- target-native delayed reentry: pending;
- released package behavior: unexecuted;
- production compatibility and implementation: undecided;
- external impact or frequency: unmeasured;
- upstream contact: unauthorized and not performed.
