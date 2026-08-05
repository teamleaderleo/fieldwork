# Delayed lifecycle reentry promise graph

Status: dependency-free model executed  
Fieldwork lane: #216  
Target: #4  
Scout: #19  
Signals worker: #194  
Upstream contact authorized: `false`

## Question

Can a lifecycle child cross an asynchronous boundary and then return its owner provider or reader's still-pending shutdown promise without creating a permanent self-dependency? Can an implementation identify that same-owner callback while preserving the ordinary rule that unrelated concurrent callers join one shared shutdown result?

## Model

The dependency-free model mirrors the current owned-fork trial shape:

- the first caller creates one shared shutdown promise;
- lifecycle children are invoked synchronously;
- a narrow invocation flag contains direct synchronous reentry;
- later callers receive the existing shared promise;
- `forceFlush()` after shutdown starts also returns that shared promise.

Files:

- `lifecycle-reentry-promise-graph.mjs`
- `lifecycle-reentry-promise-graph.result.json`

Execution runtime:

```text
Node v22.16.0
```

The script contains assertions for every expected outcome and exits successfully only when the result table matches.

## Result table

| Case | Result | Interpretation |
| --- | --- | --- |
| direct synchronous self-reentry | fulfilled | the narrow invocation guard contains the direct callback |
| delayed self-reentry through `shutdown()` | watchdog timeout | the child promise adopts the owner promise while the owner waits for the child |
| delayed self-reentry through `forceFlush()` | watchdog timeout | post-shutdown force flush returns the same owner promise and creates the same cycle |
| healthy unrelated concurrent caller | both fulfilled; same promise | ordinary callers must continue joining the shared one-shot result |
| unrelated caller during a self-cycle | both watchdog timeout; same promise | once the child creates the cycle, every legitimate joiner is trapped in it |
| delayed cross-owner nested shutdown | fulfilled | nesting into a distinct provider does not form the same self-dependency |

## Strongest supported conclusion

Shared promise identity is necessary for ordinary concurrent lifecycle callers, but it is insufficient for detecting delayed same-owner callback reentry.

After the child crosses an async boundary, these two calls are externally identical to the provider:

1. an unrelated caller asking to join the existing shutdown;
2. the provider's own child callback returning that shutdown to the aggregate that is waiting for the child.

A longer boolean invocation guard would suppress legitimate concurrency. Comparing returned promise identity happens too late because an async function adopts the returned promise rather than exposing the inner return value as a separate inspectable object.

## Contract-family review

### 1. Explicitly forbid delayed same-owner reentry

A useful public rule can state that a lifecycle callback must not await and then return its owner provider or reader's lifecycle operation. A diagnostic rule alone prevents undocumented assumptions but does not mechanically settle a callback that violates it.

A mechanical typed failure needs callback ancestry or an explicit lifecycle context that survives the asynchronous boundary.

### 2. Propagate callback ownership through async context

Node's async-context facilities could identify callback ancestry, but OpenTelemetry JS supports browser-facing packages. Making Node-only context tracking part of the provider contract would create a portability split and triggers the lane stop condition unless an equivalent repository-owned abstraction already spans every supported runtime.

### 3. Redesign fanout dependency ownership

A fanout could avoid waiting on a child result that depends on the aggregate it contributes to, but general Promise-cycle detection is unavailable. Racing every child against a timeout changes error and completion semantics; detaching child completion weakens shutdown truth; wrapping the shared promise does not change the dependency graph.

A viable redesign therefore needs an explicit child-operation token, context, or API rule rather than generic Promise inspection.

## Current disposition

**ACCEPT the promise-cycle characterization. HOLD production implementation.**

The next target evidence should remain characterization-only:

1. trace provider delayed shutdown and force-flush reentry;
2. `LoggerProvider` delayed shutdown and force-flush reentry;
3. `MeterProvider` delayed reader callback reentry;
4. `MetricReader` delayed `onShutdown()` reentry;
5. unrelated concurrent caller controls for every signal;
6. cross-provider nesting controls;
7. bounded watchdogs that prevent a hanging repository suite.

The tests should record current settlement behavior without adding a production workaround.

## Stop conditions retained

Hold implementation if the only mechanism requires:

- global Promise instrumentation;
- Node-only async context for a browser-facing SDK contract;
- suppressing all concurrent callers during child shutdown;
- arbitrary timeouts that redefine successful teardown;
- detaching child completion from the provider's reported result.

No upstream issue, pull request, comment, review, reaction, or direct backlink is authorized.
