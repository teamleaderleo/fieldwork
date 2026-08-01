# Upstream issue draft — lifecycle fanout can skip opening processors after synchronous failure or mutation

Draft status: `not applicable — direct PR preferred`  
Public interaction authorized: `no`

A direct pull request is preferred because the affected behavior, bounded correction, focused tests, and compatibility boundary are already concrete. Retain this issue draft only as a fallback if maintainers request design discussion before code review.

---

## Summary

The trace, logs, and metrics SDK lifecycle aggregators invoke child processors or readers while iterating mutable arrays. A synchronous child throw can stop later invocations before the aggregate promise is built. A child can also remove a later indexed child during iteration, causing the current shutdown or force-flush operation to skip a child that belonged to the opening set.

This can leave an opening processor or reader without its lifecycle call.

## Reproduction

1. Configure two child processors or readers.
2. Make the first child synchronously throw, or remove the second child from the backing collection during `shutdown()` or `forceFlush()`.
3. Invoke the aggregate lifecycle method and count calls to the second child.

Minimal pattern:

```ts
const children = [first, second];
first.shutdown = () => {
  children.splice(1, 1);
  return Promise.resolve();
};

await aggregate.shutdown();
assert.equal(secondShutdownCalls, 1);
```

Equivalent controls apply to synchronous throws and to force flush across trace, logs, and metrics.

## Observed behavior

At commit `2c931bf4eec18a234a28706567c6977f08139abd`, the affected entrypoints iterate live arrays and invoke child methods directly while constructing promise inputs. A synchronous throw stops later construction. Live indexed mutation can remove a later child before iteration reaches it.

## Expected behavior

A lifecycle aggregate should attempt every child present when the operation starts. Mutations during the operation should affect future operations while leaving current opening membership stable. Existing package-specific error behavior should remain unchanged.

## Current source observation

The relevant entrypoints are:

- `MultiSpanProcessor.shutdown()` and `forceFlush()`;
- `MultiLogRecordProcessor.shutdown()` and `forceFlush()`;
- `MeterProvider.shutdown()` and `forceFlush()`.

They use eager promise fanout but do not combine an opening snapshot with synchronous invocation protection.

## Candidate direction

Take a shallow copy of the child array before the first invocation, then invoke every snapshot entry through a helper that converts synchronous throws into rejected promises. Continue using `Promise.all` and preserve each package's current outward error policy.

## Compatibility and risks

- One shallow array allocation occurs per affected shutdown or force-flush call.
- Future operations continue to observe mutations to the original collections.
- The proposal keeps first-rejection behavior; it does not aggregate every asynchronous child error.
- Public APIs and method signatures remain unchanged.

## Evidence limits

- Production frequency and ecosystem prevalence are unmeasured.
- No extreme child-count performance benchmark has been run.
- Delayed lifecycle recursion, one-shot shutdown state, final metrics collection, and span delivery after shutdown starts are separate questions.

## Versions and environment

- project commit: `2c931bf4eec18a234a28706567c6977f08139abd`;
- platform: repository-supported GitHub Actions matrix;
- runtime/compiler: repository-declared versions;
- relevant configuration: two processors or readers with a synchronous throw or backing-array mutation in the first child.

## Additional context

Historical lifecycle work includes span-processor force-flush support in PR #802. Searches for an existing stable-opening lifecycle fanout repair found no equivalent current issue or pull request as of 2026-08-01.

---

## Filing checklist

- [ ] Current upstream issue and PR search repeated immediately before filing.
- [ ] Reproduction works on a current public revision.
- [x] Severity and prevalence wording stays within evidence.
- [x] Private, internal, or evidence-only links removed from the public draft.
- [ ] Target issue template and contribution policy rechecked at filing time.
- [ ] AI disclosure handled according to current project policy.
- [ ] Exact user authorization to file this issue recorded.
