# Upstream issue draft

Proposed title: `Lifecycle fanout can skip processors present at operation start`  
Draft status: `review-ready — issue-first recommended`  
Public interaction authorized: `no`  
Internal technical record: [`DEEP_DIVE.md`](./DEEP_DIVE.md)

The text between the dividers is the proposed public issue body. The deep dive keeps the source map, rejected alternatives, exact evidence, and compatibility analysis so the report doesn't repeat them.

---

## What happened?

OpenTelemetry trace and log providers can skip a processor that was registered when `shutdown()` or `forceFlush()` began.

The lifecycle fanout currently invokes processors while walking a retained array. Two JavaScript behaviors can change the current operation:

```text
processor A throws synchronously
    -> promise-list construction stops
    -> processor B is never called

processor A removes processor B from the retained array
    -> live iteration no longer sees B
    -> processor B is never called
```

`TracerProvider.forceFlush()` has a related cleanup problem. It creates a timeout before invoking each processor. A direct synchronous throw is caught by the surrounding `Promise` constructor, so later `.map()` callbacks still run, but the throw bypasses the returned-promise rejection handler that clears that processor's timeout. The operation reports failure while the obsolete timer remains armed until expiry.

## Intended lifecycle behavior

The trace SDK specification requires provider shutdown to invoke shutdown on all internal processors and force flush to invoke force flush on all registered span processors. The logs SDK specification requires the same for all registered log record processors. Both specifications separately say the operation should tell the caller whether it succeeded, failed, or timed out.

Those are separate requirements:

```text
processor A fails
processor B succeeds

expected:
    call A
    call B
    report the operation as failed under the existing result policy
```

This proposal does not turn a failed operation into success. It prevents one processor's failure from suppressing unrelated processors' final export or cleanup opportunity. If several operations are deliberately dependent, that dependency can be owned inside one composite processor rather than arising accidentally from a synchronous throw.

Specification references:

- [Trace SDK — Shutdown and ForceFlush](https://opentelemetry.io/docs/specs/otel/trace/sdk/#shutdown)
- [Logs SDK — Shutdown and ForceFlush](https://opentelemetry.io/docs/specs/otel/logs/sdk/#shutdown)

### Steps to reproduce

#### 1. A synchronous shutdown throw skips a later trace processor

```ts
import type { SpanProcessor } from '@opentelemetry/sdk-trace';
import { TracerProvider } from '@opentelemetry/sdk-trace';

let secondShutdownCalls = 0;

const first: SpanProcessor = {
  onStart() {},
  onEnd() {},
  forceFlush: async () => {},
  shutdown() {
    throw new Error('first processor failed');
  },
};

const second: SpanProcessor = {
  onStart() {},
  onEnd() {},
  forceFlush: async () => {},
  shutdown: async () => {
    secondShutdownCalls += 1;
  },
};

const provider = new TracerProvider({ spanProcessors: [first, second] });

try {
  await provider.shutdown();
} catch {}

console.log(secondShutdownCalls); // current: 0, expected: 1
```

`TracerProvider.shutdown()` delegates to `MultiSpanProcessor.shutdown()`. The first direct throw exits the loop before the second processor is invoked.

The same direct-throw behavior is present in `MultiSpanProcessor.forceFlush()` and in log processor shutdown/force-flush fanout.

#### 2. A synchronous force-flush throw leaves the provider timeout armed

Current `main` supports a per-call timeout:

```ts
import type { SpanProcessor } from '@opentelemetry/sdk-trace';
import { TracerProvider } from '@opentelemetry/sdk-trace';

const throwing: SpanProcessor = {
  onStart() {},
  onEnd() {},
  shutdown: async () => {},
  forceFlush() {
    throw new Error('processor failed immediately');
  },
};

const provider = new TracerProvider({ spanProcessors: [throwing] });

try {
  await provider.forceFlush({ timeoutMillis: 1000 });
} catch {
  console.log('forceFlush rejected');
}

console.log('the process should now be able to exit immediately');
```

The rejection is observed immediately, but the timeout for the throwing processor remains referenced until it expires. Running the script with a shell timing command keeps the process alive for roughly the configured timeout.

For released `@opentelemetry/sdk-trace` 2.10.0, configure the same timeout with the deprecated `TracerProvider` constructor option instead; the per-call option was added afterward on `main`.

#### 3. Removing a processor during fanout changes the current operation

The providers retain the supplied processor array. If the first processor synchronously runs `processors.splice(1, 1)` during shutdown or force flush, live iteration can skip the removed processor even though it belonged to the opening set.

## Expected result

Every processor present when a lifecycle operation begins should be invoked once for that operation.

A processor-array mutation may affect later operations, but should not rewrite the operation already in progress. A direct synchronous implementation error should enter the surface's existing asynchronous failure path, and an operation-owned timeout should be cleared after its processor has already failed.

The overall operation may still fail. This issue concerns which processors are attempted, not whether failure is reported.

## Actual result

Depending on the entrypoint, a direct synchronous throw or live-array mutation can prevent a later opening processor from being invoked. Public `TracerProvider.forceFlush()` can also retain a referenced timeout after it has already reported the corresponding synchronous failure.

## Additional details

This mainly affects custom or third-party processors. It is a bounded lifecycle-correctness and shutdown-reliability issue, not evidence that built-in processors commonly lose telemetry.

A skipped processor may miss its final export or cleanup opportunity. In Node.js, the stale provider timer may also delay natural process termination by the configured force-flush timeout.

A candidate implementation and regression tests are prepared in a fork. I can open a pull request after maintainers confirm whether the trace and logs changes should remain one contribution.

A proposed repair would:

```text
operation starts
    -> snapshot the current processor list
    -> invoke every processor in that snapshot, in order
    -> convert only direct synchronous throws into rejected promises
    -> keep each entrypoint's existing outward error policy
```

Affected implementation points:

- `MultiSpanProcessor.shutdown()` and `forceFlush()`;
- `TracerProvider.forceFlush()`;
- `MultiLogRecordProcessor.shutdown()` and `forceFlush()`.

Metrics is intentionally excluded. `MeterProvider` constructs an internal collector list instead of retaining the caller's reader array, prior mutation controls required private-state access, and metric collector lifecycle methods are already `async`.

## OpenTelemetry setup code

The reproduction snippets use only public OpenTelemetry provider and processor interfaces.

## package.json

For the released-package form of the reproduction:

```json
{
  "type": "module",
  "dependencies": {
    "@opentelemetry/sdk-logs": "0.221.0",
    "@opentelemetry/sdk-trace": "2.10.0"
  }
}
```

The current-main form was also reproduced against:

`f278e3b8427c406c271b8cba2c0f1a9c47c2f15e`

## Relevant log output

```text
secondShutdownCalls: 0
forceFlush rejected
process exit delayed until forceFlush timeout expires
```

## Runtime and version

- Node.js v22.16.0 for the isolated process-lifetime reproduction;
- current repository test matrix for the target-native regression coverage.

## Proposed compatibility boundary

- no new public API, type, configuration, dependency, or normal telemetry hot-path change;
- the current per-call trace timeout API remains unchanged;
- one shallow array copy per affected lifecycle operation;
- processors remain eagerly invoked in their existing order;
- mutations remain visible to later operations;
- existing trace aggregate, provider, and logs settlement policies remain;
- genuinely pending processors still time out;
- no `Promise.allSettled`, retry, cancellation, idempotence, malformed-return validation, or multi-error redesign.

## Prior-art check

A refreshed issue and pull-request search found no equivalent repair. The recently merged per-call trace timeout work is complementary: it changes how the timeout is selected, not opening-set membership or synchronous-failure timeout cleanup.

---

## Internal filing checklist

- [x] issue-first route restored;
- [x] pure OpenTelemetry reproductions included;
- [x] aggregate throw behavior distinguished from provider Promise-constructor behavior;
- [x] failure reporting distinguished from invoking all processors;
- [x] prepared implementation noted without linking internal staging records;
- [x] released-package and current-main timeout forms distinguished;
- [x] current-main and overlap refreshed on `2026-08-05`;
- [x] metrics private-state-only behavior excluded;
- [x] severity and prevalence limited to supported claims;
- [ ] refresh public `main`, versions, specification links, and duplicate search immediately before filing;
- [ ] confirm the rebased exact-head workflow matrix and renewed review;
- [ ] record explicit authority for the exact public issue creation.
