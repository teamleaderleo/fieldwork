# Deep dive — explicit abort terminal ownership

## Question

When a caller-provided `AbortSignal` fires during `streamText`, which state transition owns the result, and which work may continue asynchronously?

## Source lineage

1. Public pin `2b872b0db3769decf69945830c66a897c1e37347` exposed the pending-read gap.
2. Maintainer-authored upstream PR #16852 at `0ef2ae9a7f143d90972b4ff217046e0b04ea67f1` added independent abort observation, root rejection, outward abort, and reader cancellation.
3. Owned characterization PR #1 at `e685a4c92a5869aec306718ab5a440b7cb4fa5b1` broadened root/derived, pre-abort, local-tool, multi-consumer, callback-stall, and provider-error coverage.
4. Owned repair PR #7 at `19a9dbe26b48af848f3202fa0c409ed67d034c7d` moved outward terminal mechanics before observability and made post-abort provider values/errors yield to abort.
5. Internal materialization PR #8 reconciled the five-file candidate onto public main `e84b8bc8154030cdb7469b0e0b8cd8b9354f19a0`, producing clean source head `92079da650430d8376a7eeef2436910b44393411`.
6. Continued cancellation analysis modeled the exact native Web Streams layers returned by `streamLanguageModelCall()` and encoded the result as a target-native regression through PR #12.
7. PR #12 squash-merged the regression into canonical source head `3035f6e5a3ef6ff9236c8d1b08f4ea3dfe852c15`.
8. Owned-fork review PR #13 compares that exact head with current-public-base `e84b8bc8154030cdb7469b0e0b8cd8b9354f19a0` through a six-file fence.
9. A broader source pass mapped retry, tool, stitchable-stream, async-iterator, pre-abort, and sibling `generateText` boundaries. Its retained model results live in `receipts/2026-08-01-adjacent-stream-lifecycle-scout.md`.

## Current control flow

The resilient outward stream installs one abort listener and retains one `abortPromise` latch. The first caller abort:

1. selects the abort path;
2. rejects the five result roots;
3. enqueues one outward abort part when the stream remains open;
4. closes the outward controller and removes its abort listener;
5. requests cancellation of the stitchable reader;
6. invokes application and telemetry abort callbacks without awaiting them.

A provider `reader.read()` result or error arriving after the latch exists yields to the same abort path. Ordinary consumer cancellation remains consumer-scoped.

## Result ownership

Direct roots:

- finish reason;
- raw finish reason;
- usage;
- steps;
- initial response messages.

Text, content, final step, output, tool collections, response metadata, and response messages derive from those roots. Rejecting roots once is the decisive public-settlement operation.

## Provider registration gap

The provider may return a `ReadableStream` after the caller signal fires but before that stream is registered with the stitchable owner. Cancelling the empty stitchable owner cannot reach this stream later, so the candidate checks the signal and directly cancels the returned model-call stream:

```ts
if (abortSignal?.aborted) {
  cleanupStepTimeouts();
  await languageModelStream.cancel(getAbortReason());
  return;
}
```

The packet originally treated this `await` as provider cleanup authority. Exact modeling corrected that premise.

## Cancellation promise layers

At source head `92079da650430d8376a7eeef2436910b44393411`, `streamLanguageModelCall()` creates:

```ts
const standardizedStream = providerStream.pipeThrough(normalizationTransform);
return createAsyncIterableStream(standardizedStream);
```

`createAsyncIterableStream()` adds a fresh identity `TransformStream`. A dependency-free Node `v22.17.0` probe reproduced this exact stack.

When the provider source's `cancel()` returned a never-settling promise:

- cancellation reached the provider with the exact reason;
- the outer returned stream's `cancel()` promise resolved within the bound;
- provider cleanup remained pending.

When provider `cancel()` rejected:

- the outer cancellation promise resolved;
- an `unhandledRejection` listener observed zero events.

Therefore the pre-registration `await` joins the request-level outer-stream cancellation promise. It does not join provider-controlled cleanup completion at this exact source revision.

Receipt: `receipts/2026-08-01-provider-cancel-promise-model.md`.

## Discarded wrapper direction

A proposed wrapper around `streamLanguageModelCall()` attempted to detach explicit-abort cancellation while preserving awaited ordinary cancellation. The model showed ordinary cancellation already settles before provider cleanup through the existing pipe layers. The wrapper introduced an extra reader and lifecycle boundary without creating the claimed distinction.

The branch was reset to the clean source head. PR #12 retains the correction in its discussion and merged one target-native regression file only.

## Callback boundary

`notify()` catches individual callback failures. Detaching it is appropriate because observability follows terminal selection. A pending or rejecting callback cannot hold public settlement, outward closure, or the provider cancellation request.

## Tool boundary

Cooperative local tools receive the operation signal. The SDK suppresses a later success claim after abort ownership. The SDK cannot undo a side effect already committed outside its process; issue and PR text must state this limit plainly.

Tool-input lifecycle callbacks also preserve their intended ordering. `invokeToolCallbacksFromStream()` forwards the current chunk before awaiting the callback, but local execution begins only after the later `model-call-end` chunk crosses that same transform. A pending input callback blocks the later trigger, so no callback/tool-execution race was established.

## Pre-aborted operation boundary

A pre-aborted `streamText` call settles its outward abort result immediately, while the background setup task continues through start and step callbacks, invokes `doStream()` with the already-aborted signal, then cancels the returned stream before stitchable registration.

The canonical pre-abort regression checks result settlement and callback cardinality for `onAbort`, `onEnd`, and `onError`. It does not count `onStart`, `onStepStart`, `onLanguageModelCallStart`, or provider invocation.

`generateText()` follows the same first-attempt convention. Its first provider attempt receives the merged abort signal without an earlier `throwIfAborted()` guard; later steps perform that guard. The provider V4 interface defines `abortSignal` as the signal for cancelling the operation.

This yields a compatibility-sensitive contract question:

- core may rely on provider cooperation and preserve lifecycle callbacks for attempted work;
- core may short-circuit provider invocation to protect against non-cooperative custom providers;
- core may preserve selected observability callbacks while guarding the provider boundary only.

The current evidence does not select among these safely. A wider change would affect both `streamText` and `generateText`, so it remains outside the six-file candidate pending cross-API characterization.

## Shared async-iterator boundary

`createAsyncIterableStream()` and `asAsyncIterableStream()` expose streams through `for await`. Their `next()` implementation cleans up on normal completion, explicit `return()`, and explicit `throw()`. A source error rejects `reader.read()` before cleanup runs.

A Node `v22.16.0` model reproduced the exact helper flow:

- the original source error reached the consumer;
- the SDK-created stream remained locked;
- acquiring a new reader failed with `TypeError`;
- native `ReadableStream` async iteration released the lock;
- catching the read error, calling `cleanup(false)`, and rethrowing released the lock while preserving the original error.

This helper serves text, object, UI, agent, workflow, transcription, and translation streams. The finding therefore has a wider source and compatibility fence than unit 06 and should receive a separate target-native Node/Edge characterization.

## Stitchable terminate boundary

`createStitchableStream.terminate()` issues inner `reader.cancel()` calls without awaiting or attaching a rejection handler. A raw rejecting inner stream produced one modeled unhandled rejection. Adding one identity transform contained it, and the relevant `streamText` inner streams pass through transform layers before registration.

No current `streamText` manifestation was established. The result remains a utility-contract hazard and negative product-path result, rather than a blocker for this unit.

## Compatibility boundary

The contribution preserves the difference between:

- operation abort through the caller signal;
- one consumer ending or cancelling its reader;
- ordinary provider failure before abort ownership;
- incomplete provider close, which belongs to a separate campaign;
- shared async-iterator cleanup after a source error, which belongs to a separate follow-up;
- pre-aborted first-attempt policy across streaming and non-streaming generation, which requires cross-API characterization.

## Strongest current conclusion

The terminal-ordering direction is supported by exact prior target execution. The clean current-main production candidate has no newly demonstrated source defect. Canonical source head `3035f6e5a3ef6ff9236c8d1b08f4ea3dfe852c15` includes a target-native regression for the corrected cancellation semantics.

The broader pass produced one separate model-confirmed async-iterator ownership defect and two negative or unresolved results. None belongs in the current six-file fence.

Promotion is held on exact-head Verify Changesets run `30691402294`, ordinary CI run `30691402306`, and independent complete-diff acceptance. Every current job exists in the queue and zero jobs have started, so the present blocker supplies no product-test conclusion.
