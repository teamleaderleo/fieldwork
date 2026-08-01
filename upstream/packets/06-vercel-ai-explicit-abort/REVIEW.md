# Review guide — unit 06

## Current disposition

`HOLD`

Canonical source: `teamleaderleo/ai` branch `upstream/06-explicit-abort-nonblocking` at `3035f6e5a3ef6ff9236c8d1b08f4ea3dfe852c15`.

Current-public-base branch: `upstream/06-public-main-base` at `e84b8bc8154030cdb7469b0e0b8cd8b9354f19a0`.

Canonical owned-fork review PR: `teamleaderleo/ai#13`.

Exact Verify Changesets run: `30691402294`.  
Exact ordinary CI run: `30691402306`.

## Review fence

Review exactly six files:

1. `.changeset/slow-streams-abort.md`
2. `packages/ai/src/generate-text/stream-text.ts`
3. `packages/ai/src/generate-text/stream-text.test.ts`
4. `packages/ai/src/generate-text/stream-text-explicit-abort.test.ts`
5. `packages/ai/src/generate-text/stream-text-explicit-abort-races.test.ts`
6. `packages/ai/src/generate-text/stream-language-model-call-cancellation.test.ts`

The canonical diff contains no workflow or publisher file.

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

The target-native regression is now canonical at `3035f6e5…`.

## Claim-by-claim inspection

### Public results settle on explicit abort

Inspect the abort listener, `rejectResultPromises()`, and pre-aborted/setup catch paths. Confirm one abort operation rejects roots once.

### Outward settlement precedes observability

Confirm abort enqueue, controller close, listener cleanup, and reader cancellation request occur before detached `notify()`.

### Later provider outcomes lose

Inspect both the successful `reader.read()` path and catch path. Once abort owns the result, neither a value nor an ordinary provider error may enqueue or error a competing outward outcome.

### Registration-gap ownership

Confirm a provider stream created after abort is directly cancelled because it is absent from the stitchable owner's registered set. Confirm the returned model-call stream cancellation promise has request-level settlement through the canonical regression.

### Consumer cancellation remains separate

Inspect `cancel(reason)` on the outward `streamText` stream and existing controls. It must preserve operation-signal ownership and avoid invoking `onAbort` by itself.

Do not infer provider cleanup completion from the outer cancellation promise. The target's existing stream layers decouple those promises.

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

PR #12 previously contained an extra cancellation wrapper. A model-executed negative control showed that wrapper could not preserve the claimed difference between explicit-abort and ordinary provider-cleanup waiting. The branch was reset, the wrapper was removed, and PR #12 merged one regression file only.

## Canonical self-review

PR #13 contains an exact-head complete-diff self-review at `3035f6e5…` with a conditional source accept. It records:

- the six-file fence;
- the historical target-executed repair receipts;
- the model-executed cancellation correction;
- the discarded wrapper direction;
- the queued exact-head CI state;
- the absence of workflow and publisher files.

This self-review cannot serve as independent final acceptance.

## Repository hygiene

- no workflow or publisher files in the canonical source branch;
- no generated cache/build output;
- changeset wording describes user-visible behavior;
- test timing bounds are discriminating and stable;
- current public base is an ancestor of the source head;
- source links and receipts name exact commits;
- existing upstream PR #16852 is acknowledged;
- superseded carriers #9–#11 are excluded from the canonical diff;
- public upstream contact remains unauthorized.

## Promotion gate

Keep `HOLD` while either exact-head run remains queued or incomplete.

Move to `READY` only after:

1. Verify Changesets `30691402294` passes;
2. ordinary CI `30691402306` passes on exact canonical head `3035f6e5…`;
3. an independent complete-diff disposition finds no blocking issue;
4. current duplicate/prior-art refresh and issue/PR drafts remain synchronized;
5. an explicit contribution route accounts for existing upstream PR #16852.

A product failure returns the unit to `REPAIR` with the exact failing assertion or gate recorded.
