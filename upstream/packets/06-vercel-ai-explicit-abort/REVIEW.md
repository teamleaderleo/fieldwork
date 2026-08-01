# Review guide — unit 06

## Current disposition

`REPAIR`

Canonical source: `teamleaderleo/ai` branch `upstream/06-explicit-abort-nonblocking` at `92079da650430d8376a7eeef2436910b44393411`.

## Review fence

Review exactly five files against public base `e84b8bc8154030cdb7469b0e0b8cd8b9354f19a0`:

1. `.changeset/slow-streams-abort.md`
2. `packages/ai/src/generate-text/stream-text.ts`
3. `packages/ai/src/generate-text/stream-text.test.ts`
4. `packages/ai/src/generate-text/stream-text-explicit-abort.test.ts`
5. `packages/ai/src/generate-text/stream-text-explicit-abort-races.test.ts`

## Blocking finding

The pre-registration path currently awaits:

```ts
await languageModelStream.cancel(getAbortReason());
```

A provider-controlled cancel promise can reject or remain pending. Repair this before promotion. The preferred narrow direction is a cancellation request with local rejection containment and immediate return.

## Claim-by-claim inspection

### Public results settle on explicit abort

Inspect the abort listener, `rejectResultPromises()`, and pre-aborted/setup catch paths. Confirm one abort operation rejects roots once.

### Outward settlement precedes observability

Confirm abort enqueue, controller close, listener cleanup, and reader cancellation request occur before detached `notify()`.

### Later provider outcomes lose

Inspect both the successful `reader.read()` path and catch path. Once abort owns the result, neither a value nor an ordinary provider error may enqueue/error a competing outward outcome.

### Registration-gap ownership

Confirm a provider stream created after abort is directly cancelled because it is absent from the stitchable owner's registered set. Confirm the direct request cannot block setup or create an unhandled rejection.

### Consumer cancellation remains separate

Inspect `cancel(reason)` on the outward stream and tests. It must not fire the operation signal, reject roots as abort, or invoke `onAbort` by itself.

### Tool reporting remains truthful

Confirm cooperative tools receive the signal and later results are suppressed after abort. Avoid claims that abort rolls back an already committed side effect.

## Test review

Verify each test would fail against the relevant losing implementation:

- no independent abort listener;
- callback-first terminal ordering;
- `isAbortError()`-based post-abort arbitration;
- stitchable-only cancellation during the registration gap;
- awaited direct provider cancellation;
- reader cancellation upgraded into operation abort.

Require both Node and Edge execution where the repository supports them.

## Repository hygiene

- no workflow or publisher files in the source branch;
- no generated cache/build output;
- changeset wording describes user-visible behavior;
- test timing bounds are discriminating and stable;
- current public base is an ancestor of the source head;
- source links and receipts name exact commits;
- existing upstream PR #16852 is acknowledged;
- public upstream contact remains unauthorized.

## Promotion gate

Change disposition from `REPAIR` to `HOLD` only after the hostile cancellation defect is fixed and focused current-head tests pass.

Change from `HOLD` to `READY` only after ordinary repository CI, complete-diff independent review, current duplicate/prior-art refresh, finalized issue/PR wording, and an explicit contribution route for the existing upstream PR.