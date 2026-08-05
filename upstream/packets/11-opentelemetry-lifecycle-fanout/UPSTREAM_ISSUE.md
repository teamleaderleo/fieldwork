# Upstream issue draft

Proposed title: `Lifecycle fanout can skip processors present at operation start`  
Draft status: `review-ready — issue-first recommended`  
Public interaction authorized: `no`  
Technical details: [`DEEP_DIVE.md`](./DEEP_DIVE.md)

The text between the dividers is the proposed public issue body.

---

## What happened?

`shutdown()` and `forceFlush()` can skip processors that were registered when the operation began.

```text
Current
[A, B] -> call A -> A throws or removes B -> B is skipped

Expected
snapshot [A, B] -> call A -> call B -> report A's failure
```

The overall operation may still fail. The issue is that one processor's failure or array mutation can prevent another processor from receiving its lifecycle call.

The trace and logs SDK specifications require lifecycle calls to reach all registered processors:

- [Trace SDK — Shutdown and ForceFlush](https://opentelemetry.io/docs/specs/otel/trace/sdk/#shutdown)
- [Logs SDK — Shutdown and ForceFlush](https://opentelemetry.io/docs/specs/otel/logs/sdk/#shutdown)

## Steps to reproduce

### A synchronous shutdown throw skips a later processor

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

The same direct-throw behavior exists in trace force flush and log shutdown/force flush.

### Array mutation can change the current operation

```text
processors = [A, B]
A runs processors.splice(1, 1)
live iteration no longer reaches B
```

Mutation may affect later operations, but it should not change the set already being processed.

### A synchronous provider force-flush failure can leave its timeout armed

```text
create timeout
    -> processor.forceFlush() throws immediately
    -> operation reports failure
    -> timeout remains referenced until expiry
```

## Expected result

```text
snapshot opening processors
call each processor
report failure through the existing policy
clear completed processor timers
```

## Actual result

A direct throw or live-array mutation can skip a processor. A synchronous provider throw can leave its timeout armed.

## Additional details

A candidate implementation and tests are prepared in a fork.

## OpenTelemetry setup code

The reproduction above is the complete setup.

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

## Relevant log output

```text
secondCalls: 0
forceFlush rejected
process exit delayed until timeout expiry
```

## Operating System and Version

Not operating-system-specific.

## Runtime and Version

Node.js v22.16.0.

---

Before filing: refresh `main`, versions, duplicate search, CI, and review status.