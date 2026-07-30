# OpenTelemetry JS delayed lifecycle reentry

State: `model-executed — target characterization queued`

Fieldwork lane: #216  
Fieldwork packet: #221  
Parent scout: #19  
Signals worker: #194  
Target hub: #4  
Synthesis packet: #32  
Upstream contact authorized: `false`

## In simple words

The current owned OpenTelemetry lifecycle candidates contain a processor or reader that calls its owner provider's shutdown method immediately inside the same synchronous callback.

That protection ends when the callback returns its promise. A custom child can wait for one microtask and then call the same owner shutdown method. The owner returns the shared shutdown promise while that promise is already waiting for the child's promise. The child promise adopts the owner promise, so each can wait for the other indefinitely.

The hard compatibility requirement is preserving an unrelated concurrent caller. That caller should receive the same shared shutdown result. At the public method boundary, the legitimate caller and the delayed self-reentrant child make the same call after the synchronous guard has cleared.

## Exact source identities

- core `BindOnceFuture` source base: `teamleaderleo/opentelemetry-js@7b06368b7362a30ca69c178f43bd94dfbb36f85d`
- trace one-shot candidate: `teamleaderleo/opentelemetry-js#4` at `50cd262e326c2a24419bad53c932a688b42224a4`
- logs direct-reentry candidate: `teamleaderleo/opentelemetry-js#8` at `7d49735173c8467a88afab426a4bf02910a3dd62`
- metrics composed lifecycle candidate: `teamleaderleo/opentelemetry-js#9` at `f3740eb9bda8ec22ae81941adcdaf0de0aa3c764`

The earlier metrics head `5bb520f141759ce003dc002196c43cda4fe96551` is the first all-green repair ancestor. Complete-diff review later restored released unbound-reader diagnostic order at `f3740eb...`; this inquiry uses the final head.

## Source mechanism

`BindOnceFuture` owns one deferred promise. The first call invokes the lifecycle callback and settles the deferred only after the callback result settles. Later callers receive the same deferred promise.

The owned provider candidates use a narrow direct-reentry guard:

```text
set invocation-active
invoke child lifecycle method and receive its promise
clear invocation-active in finally
```

The `finally` runs after the child function returns its promise, not after that promise settles. A child that calls the owner synchronously is visible to the guard. A child that resumes after an `await` is not.

For a delayed child:

```ts
async shutdown() {
  await Promise.resolve();
  return owner.shutdown();
}
```

the dependency becomes:

```text
P = owner shared shutdown promise
Q = async child shutdown promise

P waits for Q
Q resumes and calls owner.shutdown()
owner returns P
Q adopts P

P waits for Q
Q waits for P
```

Trace and logs preserve the dependency through `Promise.all`. Metrics preserves it through provider, collector, and reader layers.

## Executed model

The dependency-free promise graph is retained at:

- `promise-graph.mjs`
- `results/latest.json`
- `contract-matrix.md`

Model head `140e8bfbe6a6cd7e0d287d3e654f251c6f9917e3` passed:

- OpenTelemetry delayed lifecycle reentry focused workflow;
- Fieldwork integrity;
- External reference policy.

Current PR #221 head `9d8ba210a25df84214ae42886ffe40f02cf97713` adds review-queue notes. No current-head repository receipt is claimed for that later head.

The model establishes:

1. direct synchronous same-owner recursion settles through the narrow guard;
2. delayed same-owner recursion leaves owner and child pending;
3. unrelated external callers correctly join the same owner promise;
4. cross-owner nesting settles when the dependency graph is acyclic;
5. promise identity misses an async adopting wrapper;
6. a caller-local deadline stops one waiter but leaves the owner cycle pending;
7. an operation-owned timeout rejects the shared result for every joiner and unwinds the adopting child;
8. explicit owner provenance can distinguish self-reentry while preserving external joining;
9. suppressing every in-flight call breaks the shared-result contract for legitimate callers.

Evidence class: `model-executed`.

## Timeout distinction

A caller-local deadline:

```text
caller stops waiting
owner promise remains pending
child/owner cycle remains
```

An operation-owned timeout:

```text
shared owner promise rejects
all joined callers receive the same rejection
the adopting child promise unwinds
```

`MetricReader.shutdown({ timeoutMillis })` already has an operation-owned timeout seam. The inspected trace and logs candidates do not expose an equivalent shutdown option.

The metric timeout still leaves an ownership question: underlying `onShutdown()` work may continue after the shared result rejects. Export, resource, retry, and late-error behavior require an explicit policy.

## Active target characterizations

### Logs — OTel PR #10

Exact head: `6bbd0f34b1e8579840033c7ded88ff8059afbb3f`

Prepared controls:

- delayed same-owner shutdown reentry;
- delayed post-shutdown force-flush reentry;
- unrelated external caller joins the canonical promise;
- bounded pending-state watchdog;
- one processor shutdown call and no processor force-flush call.

### Trace — OTel PR #11

Exact head: `ea6f27274c2a7e9cd154f86bded9b23b18bafbd6`

Prepared controls:

- delayed same-owner shutdown reentry;
- delayed post-shutdown force-flush reentry;
- unrelated external caller joins the canonical promise;
- bounded pending-state watchdog;
- one child shutdown call and no child force-flush call;
- delayed cross-provider shutdown nesting completes.

### Metrics — OTel PR #12

Exact head: `89563cf41d5da6b81d1016a7dedd89e206c290a3`

Prepared controls:

- delayed `MetricReader` same-owner cycle without timeout remains pending;
- reader operation-owned timeout rejects the shared result;
- delayed `MeterProvider` and reader cycle without timeout remains pending;
- provider timeout options reach the reader and reject every provider joiner;
- each case preserves one child shutdown invocation;
- unrelated callers join the canonical promise.

Unit, Lint, E2E, CodeQL, Bundler, W3C, API peer-dependency, and workflow-security runs are queued for all three exact heads. Evidence remains `target-test-prepared` until each matrix settles.

## Contract comparison

### Retain only the synchronous guard

Preserves legitimate concurrency but leaves delayed same-owner cycles. Insufficient alone.

### Suppress every call while shutdown is active

Breaks delayed cycles by returning early, but unrelated callers no longer receive the shared result or its failure. Rejected.

### Compare child and owner promise identity

An async child returns a distinct promise that adopts the owner promise. Identity misses the cycle. Rejected.

### Caller-local timeout

Leaves the owner operation and resources pending. Rejected as a lifecycle repair.

### Operation-owned timeout

Portable and preserves shared-result semantics, but changes valid slow-cleanup behavior and requires an unfinished-cleanup policy. Viable only as an explicit provider contract.

### Node async context

Could carry provenance in Node, but these SDK packages also target browsers. Rejected as the cross-signal contract.

### Explicit lifecycle provenance

An internal owner token or capability can distinguish same-owner callback ancestry from a public external caller. The current arbitrary processor and reader interfaces carry no such token. Correct model; requires an adapter or interface redesign.

### Stop awaiting children

Avoids the cycle by abandoning shutdown completion and child failure propagation. Rejected.

## Minimum compatible rule

Until a runtime mechanism is selected:

> A lifecycle child must not await the shutdown or force-flush promise of the same owner whose lifecycle callback is currently awaiting that child.

This is a contract statement, not runtime protection.

## Current disposition

**ACCEPT the mechanism and executed model. EXECUTE target characterization. HOLD production implementation.**

After OTel PRs #10–#12 settle, decide whether the first durable contract is:

- explicit prohibition plus characterization tests;
- a deliberate provider-wide operation timeout and unfinished-cleanup policy;
- explicit lifecycle provenance;
- or a held limitation with no safe narrow implementation.

## Adjacent bounded inquiries

Promote separately only when each has an owner and distinguishing test:

1. timeout aftermath and later child failure observation;
2. cross-signal provider dependency cycles;
3. provider shutdown versus global API unregistration;
4. context-manager teardown ordering;
5. async resource attributes during final export;
6. error aggregation after operation timeout.

## Evidence boundary

- exact source mechanism: `source-read`;
- promise dependency outcomes and candidate comparison: `model-executed`;
- target-native delayed reentry: `target-test-prepared` and queued;
- released package behavior: unexecuted;
- production compatibility and implementation: undecided;
- external impact or frequency: unmeasured;
- upstream contact: unauthorized and not performed.
