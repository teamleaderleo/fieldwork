# Upstream issue draft

Proposed title: `Lifecycle fanout can skip processors present at operation start`  
Draft status: `review-ready — issue-first recommended`  
Public interaction authorized: `no`  
Technical details: [`DEEP_DIVE.md`](./DEEP_DIVE.md)

The text between the dividers is the proposed public issue body.

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

This proposal doesn't turn a failed operation into success. It prevents one processor's failure from suppressing unrelated processors' final export or cleanup opportunity. If several operations are deliberately dependent, that dependency can be owned inside one composite processor rather than arising accidentally from a synchronous throw.

Specification references:

- [Trace SDK — Shutdown and ForceFlush](https://opentelemetry.io/docs/specs/otel/trace/sdk/#shutdown)
- [Logs SDK — Shutdown and ForceFlush](https://opentelemetry.io/docs/specs/otel/logs/sdk/#shutdown)

## Steps to reproduce

### A synchronous shutdown throw skips a later trace processor

```ts
import type { SpanProcessor } from '@opentelemetry/sdk-trace';
import { TracerProvider } from '@opentelemetry/sdk-trace';

let secondCalls = 0;

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
    secondCalls += 1;
  },
};

const provider = new TracerProvider({ spanProcessors: [first, second] });

try {
  await provider.shutdown();
} catch {}

console.log(secondCalls); // current: 0, expected: 1
```

`TracerProvider.shutdown()` delegates to `MultiSpanProcessor.shutdown()`. The first direct throw exits the loop before the second processor is invoked.

The same direct-throw behavior exists in `MultiSpanProcessor.forceFlush()` and in log processor shutdown and force-flush fanout.

### A synchronous provider force-flush failure can leave its timeout armed

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

### Removing a processor during fanout changes the current operation

The providers retain the supplied processor array. If the first processor synchronously runs `processors.splice(1, 1)` during shutdown or force flush, live iteration can skip the removed processor even though it belonged to the opening set.

## Expected result

Every processor present when a lifecycle operation begins should be invoked once for that operation.

A processor-array mutation may affect later operations, but it shouldn't rewrite the operation already in progress. A direct synchronous implementation error should enter the entrypoint's existing asynchronous failure path, and a processor's timeout should be cleared once that processor has already failed.

The overall operation may still fail. This issue concerns which processors are attempted, not whether failure is reported.

## Actual result

Depending on the entrypoint, a direct synchronous throw or live-array mutation can prevent a later opening processor from being invoked. `TracerProvider.forceFlush()` can also retain a referenced timeout after it has already reported the corresponding synchronous failure.

## Additional details

This mainly affects custom or third-party processors. It's a lifecycle-correctness and shutdown-reliability issue; it isn't evidence that built-in processors routinely lose telemetry.

A skipped processor may miss its final export or cleanup opportunity. In Node.js, the stale provider timer may also delay natural process termination by the configured force-flush timeout.

A candidate implementation and tests are prepared in a fork.

```text
operation starts
    -> snapshot the processor list
    -> invoke every processor in that snapshot
    -> convert direct synchronous throws into rejected promises
    -> preserve the existing error and timeout policy
```

Affected implementation points:

- `MultiSpanProcessor.shutdown()` and `forceFlush()`
- `TracerProvider.forceFlush()`
- `MultiLogRecordProcessor.shutdown()` and `forceFlush()`

Metrics isn't included. `MeterProvider` constructs its collector list internally, the earlier mutation control required private-state access, and metric collector lifecycle methods are already `async`.

## OpenTelemetry setup code

The reproduction above is the complete setup and uses only public OpenTelemetry interfaces.

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

Current `main` was also checked at:

`f278e3b8427c406c271b8cba2c0f1a9c47c2f15e`

## Relevant log output

```text
secondCalls: 0
forceFlush rejected
process exit delayed until the forceFlush timeout expires
```

## Operating System and Version

I reproduced this in a Node.js process; it doesn't depend on a specific operating system.

## Runtime and Version

Node.js v22.16.0.

---

Before filing: refresh `main`, package versions, specification links, duplicate search, CI, and review status.