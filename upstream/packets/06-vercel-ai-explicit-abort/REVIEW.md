# Review guide — unit 06

## Current disposition

`EXECUTE`

Canonical source: `teamleaderleo/ai` branch `upstream/06-explicit-abort-nonblocking` at `92079da650430d8376a7eeef2436910b44393411`.

Exact cancellation-regression candidate: `teamleaderleo/ai#12` at `7ae1794889d9dd22eeef9faf4f33d01330c0918d`.

Exact repository CI run: `30691171818`.

## Review fence

### Canonical production candidate

Review exactly five files against public base `e84b8bc8154030cdb7469b0e0b8cd8b9354f19a0`:

1. `.changeset/slow-streams-abort.md`
2. `packages/ai/src/generate-text/stream-text.ts`
3. `packages/ai/src/generate-text/stream-text.test.ts`
4. `packages/ai/src/generate-text/stream-text-explicit-abort.test.ts`
5. `packages/ai/src/generate-text/stream-text-explicit-abort-races.test.ts`

### Exact-semantics regression

Review one additional test file on PR #12:

6. `packages/ai/src/generate-text/stream-language-model-call-cancellation.test.ts`

The PR #12 diff contains no production change.

## Corrected cancellation finding

The pre-registration path awaits:

```ts
await languageModelStream.cancel(getAbortReason());
```

An earlier review treated this as a join on provider-controlled cleanup. Exact native Web Streams modeling reproduced the target's two `pipeThrough()` layers and disproved that premise:

- cancellation reached the provider with the exact reason;
- the outer cancellation promise resolved while provider cleanup remained pending;
- provider cleanup rejection created no unhandled rejection.

Review receipt: `receipts/2026-08-01-provider-cancel-promise-model.md`.

The current gate is execution of the target-native regression, rather than a production repair to the cancellation line.

## Claim-by-claim inspection

### Public results settle on explicit abort

Inspect the abort listener, `rejectResultPromises()`, and pre-aborted/setup catch paths. Confirm one abort operation rejects roots once.

### Outward settlement precedes observability

Confirm abort enqueue, controller close, listener cleanup, and reader cancellation request occur before detached `notify()`.

### Later provider outcomes lose

Inspect both the successful `reader.read()` path and catch path. Once abort owns the result, neither a value nor an ordinary provider error may enqueue/error a competing outward outcome.

### Registration-gap ownership

Confirm a provider stream created after abort is directly cancelled because it is absent from the stitchable owner's registered set. Confirm the returned model-call stream cancellation promise has request-level settlement through target-native tests.

### Consumer cancellation remains separate

Inspect `cancel(reason)` on the outward `streamText` stream and existing controls. It must preserve operation-signal ownership and avoid invoking `onAbort` by itself.

Do not infer provider cleanup completion from the outer cancellation promise. The target's existing stream layers intentionally decouple those promises.

### Tool reporting remains truthful

Confirm cooperative tools receive the signal and later results are suppressed after abort. Avoid claims that abort rolls back an already committed side effect.

## Test review

Verify each test would fail against the relevant losing implementation:

- no independent abort listener;
- callback-first terminal ordering;
- `isAbortError()`-based post-abort arbitration;
- stitchable-only cancellation during the registration gap;
- cancellation request omitted or sent with the wrong reason;
- provider cleanup rejection escaping as an unhandled rejection;
- reader cancellation upgraded into operation abort.

Require both Node and Edge execution where the repository supports them. Record the exact shard containing `stream-language-model-call-cancellation.test.ts`.

## Rejected approach review

PR #12 previously contained an extra cancellation wrapper. A model-executed negative control showed that wrapper could not preserve the claimed difference between explicit-abort and ordinary provider-cleanup waiting. The branch was reset, and the current PR contains one regression file only.

Confirm the complete current diff before reviewing; stale comments on the discarded head remain historical evidence.

## Repository hygiene

- no workflow or publisher files in the canonical source branch;
- no workflow files in PR #12;
- no generated cache/build output;
- changeset wording describes user-visible behavior;
- test timing bounds are discriminating and stable;
- current public base is an ancestor of the source head;
- source links and receipts name exact commits;
- existing upstream PR #16852 is acknowledged;
- superseded carriers #9–#11 are excluded from the canonical diff;
- public upstream contact remains unauthorized.

## Promotion gate

Keep `EXECUTE` while run `30691171818` is queued or incomplete.

Move to `HOLD` if target-native execution passes but canonical exact-head repository CI, independent review, or contribution routing remains open.

Move to `READY` only after:

1. PR #12 exact-head regression execution passes;
2. the regression is merged into the canonical source branch;
3. ordinary repository CI passes on that exact canonical head;
4. complete-diff independent review finds no blocking issue;
5. current duplicate/prior-art refresh and issue/PR drafts are synchronized;
6. an explicit contribution route accounts for existing upstream PR #16852.
