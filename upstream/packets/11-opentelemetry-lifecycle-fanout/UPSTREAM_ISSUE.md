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

The trace SDK specification requires provider shutdown to invoke shutdown on all internal processors and force flush to invoke force flush on all registered span processors. The logs SDK specification requires the same for all registered log record processors. Both specifications also say the operation should tell the caller whether it succeeded, failed, or timed out.

```text
processor A fails
processor B succeeds

call A
call B
report the operation as failed through the existing result policy
```

Processor failures stay visible while every processor present at operation start gets its lifecycle call.

Specification references:

- [Trace SDK — Shutdown and ForceFlush](https://opentelemetry.io/docs/specs/otel/trace/sdk/#shutdown)
- [Logs SDK — Shutdown and ForceFlush](https://opentelemetry.io/docs/specs/otel/logs/sdk/#shutdown)

## Steps to reproduce

### A synchronous shutdown throw skips a later trace processor

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

### A synchronous force-flush throw leaves the provider timeout armed

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

```text
processors = [A, B]
A runs processors.splice(1, 1)
live iteration skips B
```

Array mutations should apply to later operations. The operation already in progress should keep its opening processor set.

## Expected result

```text
opening processors = snapshot(current processors)

for each processor in opening processors:
    invoke lifecycle method
    route a direct throw into the existing promise failure path

report the operation through the existing result policy
clear any timer owned by a processor that has already finished or failed
```

## Actual result

A direct synchronous throw or live-array mutation can skip a later opening processor. `TracerProvider.forceFlush()` can also retain a referenced timeout after reporting the corresponding synchronous failure.

## Additional details

This mainly affects custom or third-party processors. A skipped processor may miss its final export or cleanup opportunity. In Node.js, the stale provider timer can delay natural process termination by the configured timeout.

A candidate implementation and tests are prepared in a fork.

```text
operation starts
    -> snapshot processor list
    -> call each processor in the snapshot
    -> convert direct throws to rejected promises
    -> use the existing error and timeout policy
```

Affected paths:

- `MultiSpanProcessor.shutdown()` and `forceFlush()`
- `TracerProvider.forceFlush()`
- `MultiLogRecordProcessor.shutdown()` and `forceFlush()`

Metrics stays out of scope because its collector list is internally constructed and its lifecycle methods already cross an async boundary.

Public APIs, configuration, dependencies, and normal telemetry processing stay unchanged. Each repaired lifecycle entrypoint adds one shallow array copy.

## OpenTelemetry setup code

The reproduction above is the complete setup and uses public OpenTelemetry interfaces.

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
secondShutdownCalls: 0
forceFlush rejected
process exit delayed until the forceFlush timeout expires
```

## Operating System and Version

The behavior follows JavaScript control flow and reproduces independently of the operating system.

## Runtime and Version

Node.js v22.16.0.

---

Before filing: refresh `main`, package versions, specification links, duplicate search, CI, and review status.