# Upstream issue draft

Proposed title: `Processor lifecycle fanout can skip registered processors`  
Draft status: `review-ready — issue-first filing recommended`  
Public interaction authorized: `no`

## What happened?

Some trace and log lifecycle fanout paths iterate a retained processor array while invoking each processor.

Two related problems can result:

1. a custom processor can throw synchronously before returning its declared promise, preventing a later processor from being invoked on aggregate fanout paths;
2. a processor can synchronously mutate the retained array, causing live iteration to skip a processor that was registered when the operation began.

Public `TracerProvider.forceFlush()` has an additional failure-cleanup problem. A synchronous throw is caught by its Promise constructor, so later `.map()` callbacks still run, but the throw bypasses the existing handler that clears the per-processor timeout. The timeout remains armed until it expires.

### Steps to reproduce

#### 1. Public trace shutdown skips a later processor after a synchronous throw

```ts
import type { SpanProcessor } from '@opentelemetry/sdk-trace';
import { TracerProvider } from '@opentelemetry/sdk-trace';

let secondShutdownCalls = 0;

const first: SpanProcessor = {
  onStart() {},
  onEnd() {},
  forceFlush: async () => {},
  shutdown() {
    throw new Error('synchronous shutdown failure');
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

console.log(secondShutdownCalls); // 0 today; expected 1
```

`TracerProvider.shutdown()` delegates to `MultiSpanProcessor.shutdown()`. The first direct throw exits promise-list construction before the second processor is invoked.

The same direct-throw behavior is reachable through `LoggerProvider.shutdown()` and `LoggerProvider.forceFlush()` with custom `LogRecordProcessor` implementations.

#### 2. Public trace force flush leaves its timeout armed after synchronous failure

```ts
import type { SpanProcessor } from '@opentelemetry/sdk-trace';
import { TracerProvider } from '@opentelemetry/sdk-trace';

const first: SpanProcessor = {
  onStart() {},
  onEnd() {},
  shutdown: async () => {},
  forceFlush() {
    throw new Error('synchronous forceFlush failure');
  },
};

const second: SpanProcessor = {
  onStart() {},
  onEnd() {},
  shutdown: async () => {},
  forceFlush: async () => {},
};

const provider = new TracerProvider({
  spanProcessors: [first, second],
  forceFlushTimeoutMillis: 1000,
});

const started = Date.now();
try {
  await provider.forceFlush();
} catch {
  console.log('forceFlush rejected after', Date.now() - started, 'ms');
}

console.log('the process should now be able to exit immediately');
```

The rejection is observed immediately, but the timeout created for the first processor remains referenced until the configured timeout expires. Running the script with a shell timing command shows the process staying alive for roughly the timeout duration.

#### 3. Opening-set mutation can skip a later processor

The same paths retain the caller-provided array. If the first processor synchronously removes the second processor from that array during `shutdown()` or `forceFlush()`, live iteration can omit the second processor from the current operation.

## Expected result

Every processor registered when `shutdown()` or `forceFlush()` begins should be invoked once for that operation.

A direct synchronous implementation error should enter the surface's existing asynchronous failure path. Operation-owned timeouts should be cleared after the corresponding processor has already failed.

## Actual result

Depending on the entrypoint, a direct synchronous throw or live-array mutation can prevent a later opening processor from being invoked. Public `TracerProvider.forceFlush()` can also retain a timeout after it has already reported the corresponding synchronous failure.

## Additional details

The trace and logs SDK specifications require provider shutdown and force flush to invoke the operation on all registered processors.

The affected boundary is mainly custom or third-party processors and caller code that retains and mutates the configured processor array. This is a bounded correctness and shutdown-reliability issue; it is not evidence that ordinary built-in processors commonly lose telemetry.

A skipped processor may miss its final export or cleanup opportunity. In Node.js, the stale provider timer can also delay natural process termination by the configured force-flush timeout.

A proposed repair would:

- take a shallow snapshot of the processor array when each lifecycle operation begins;
- invoke each processor eagerly in the existing order;
- convert only a direct synchronous throw into a rejected promise;
- route public trace-provider synchronous failure through its existing timeout cleanup and error-array handling;
- preserve each surface's existing settlement policy and genuine timeout behavior.

Affected implementation points:

- `MultiSpanProcessor.shutdown()` and `forceFlush()`;
- `MultiLogRecordProcessor.shutdown()` and `forceFlush()`;
- `TracerProvider.forceFlush()`.

Metrics is intentionally excluded. Metric collector lifecycle methods are already `async`, the provider owns its collector list internally, and no supported post-construction mutation route was established.

## OpenTelemetry setup code

The reproduction snippets above use only the public SDK processor interfaces and providers.

## package.json

```json
{
  "type": "module",
  "dependencies": {
    "@opentelemetry/sdk-logs": "0.221.0",
    "@opentelemetry/sdk-trace": "2.10.0"
  }
}
```

The candidate was also reproduced and tested directly against repository revision `2c931bf4eec18a234a28706567c6977f08139abd`.

## Relevant log output

```text
secondShutdownCalls: 0
forceFlush rejected immediately
process exit delayed until forceFlush timeout expires
```

## Runtime and version

- Node.js v22.16.0 for the isolated control-flow and process-lifetime model;
- repository GitHub Actions matrix for the target-native regression tests.

## Compatibility and limits

- no public API, type, configuration, or telemetry hot-path change is proposed;
- one shallow array copy per repaired lifecycle call;
- processors remain eagerly invoked in their existing order;
- mutations remain visible to later operations, but not to the operation already in progress;
- aggregate trace shutdown would still reject;
- aggregate trace force flush would still report through the global error handler and resolve;
- logs would still reject;
- public trace-provider force flush would still reject with an error array;
- genuinely pending operations would still time out;
- no `Promise.allSettled`, retries, cancellation, idempotence, malformed-return validation, or multi-error redesign is proposed.

## Duplicate check

Issue, pull-request, and commit searches found no equivalent current repair at the time this draft was refreshed. Older force-flush work changes propagation or provider structure but does not repair this opening-set and synchronous-failure behavior.

## Filing checklist

- [ ] repeat current-main and duplicate searches immediately before filing;
- [ ] confirm the reproduction against the then-current public revision;
- [x] follow the repository bug-report fields;
- [x] provide pure OpenTelemetry reproduction code;
- [x] distinguish aggregate skipping from provider timeout cleanup;
- [x] exclude unsupported metrics-private-state claims;
- [x] avoid unsupported prevalence or severity claims;
- [ ] record explicit authority before public interaction.
