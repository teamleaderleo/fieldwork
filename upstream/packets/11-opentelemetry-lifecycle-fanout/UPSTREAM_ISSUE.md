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

- Invoke every processor present when the lifecycle operation begins.
- Preserve the existing failure result.
- Clear a processor timeout after that processor has already failed.

## Actual result

- A direct synchronous throw or live-array mutation can skip a later processor.
- `TracerProvider.forceFlush()` can retain a timeout after reporting the corresponding synchronous failure.

## Additional details

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

Metrics is not included because its collector list is internally constructed and its lifecycle methods already cross an async boundary.

No public API, configuration, dependency, or normal telemetry hot-path change is proposed.

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

Reproduced in a Node.js process; no operating-system-specific behavior is required.

## Runtime and Version

Node.js v22.16.0.

---

## Internal filing checklist

- [x] Matches the current bug-report form
- [x] Uses a pure OpenTelemetry reproduction
- [x] Separates processor invocation from operation failure
- [x] Notes the prepared implementation without linking internal staging records
- [ ] Refresh public `main`, package versions, specification links, and duplicate search before filing
- [ ] Confirm the rebased exact-head workflows and renewed review
- [ ] Record explicit authority for the public issue creation
