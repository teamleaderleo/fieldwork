# Approaches — explicit abort settlement

## Selected approach

Use one abort-operation latch, settle public and outward state before observability callbacks, and make later provider outcomes defer to the selected abort.

For a provider stream returned after abort but before registration, cancel the directly owned stream. At the exact clean head, the stream returned by `streamLanguageModelCall()` already provides request-level cancellation settlement: its `cancel()` promise resolves after forwarding the request even when provider cleanup remains pending, and provider cleanup rejection is contained by the existing pipe chain.

### Why selected

- distinguishes operation abort from consumer cancellation;
- settles root promises while a provider read remains pending;
- prevents callback latency from delaying outward closure or cancellation request;
- prevents an ordinary provider error arriving after abort from replacing the caller-selected result;
- reaches a provider stream that the empty stitchable owner cannot cancel;
- preserves the existing stream cancellation contract without another wrapper layer.

## Retained prior approach: maintainer candidate

Upstream PR #16852 added independent abort observation and root settlement. It is the implementation provenance and current public prior art. Its original test covered `text` and `steps`; the owned characterization expands the observable contract.

Disposition: retain provenance and coordinate through the existing upstream work if contact is later authorized.

## Rejected: await `onAbort` and telemetry before terminal mechanics

A callback may return a never-settling promise. Awaiting notification makes logging or telemetry part of cancellation authority and delays provider cancellation plus outward closure.

Disposition: rejected.

## Rejected: classify the provider error by `isAbortError()` after the caller signal fired

A normal provider error may arrive immediately after caller abort. Error class cannot decide terminal ownership after the operation latch has already selected abort.

Disposition: rejected.

## Rejected: infer operation abort from one reader cancelling

Streams can have multiple consumers, persistence drains, or resumable clients. One reader ending is consumer-scoped and cannot automatically terminate shared work.

Disposition: rejected.

## Rejected: cancel only the stitchable owner during the registration gap

Before registration, the stitchable owner has no reference to the returned provider stream. Its cancellation cannot later reach that stream.

Disposition: rejected.

## Disproved blocker: the pre-registration `await` joins provider cleanup

The clean head contains:

```ts
await languageModelStream.cancel(getAbortReason());
```

The earlier packet assumed this awaited a provider-controlled cleanup promise. A dependency-free Node Web Streams probe reproduced the exact target layering:

```ts
providerStream.pipeThrough(transform).pipeThrough(identityTransform)
```

The returned cancellation promise resolved after requesting cancellation while the provider cleanup promise remained pending. A rejecting provider cleanup promise produced no unhandled rejection.

Disposition: premise disproved. Retain the direct cancellation call and add target-native regression coverage. Receipt: `receipts/2026-08-01-provider-cancel-promise-model.md`.

## Rejected: add another cancellation wrapper in `streamLanguageModelCall()`

A proposed wrapper attempted to detach cancellation only after explicit abort while preserving awaited ordinary cancellation. The exact Web Streams model showed the ordinary-cancellation negative control already resolves before provider cleanup through the existing pipe chain. The wrapper added a reader and another lifecycle boundary without creating the claimed distinction.

Disposition: rejected and removed. Owned-fork PR #12 preserves the correction in its thread.

## Deferred: explicit terminal-state enum

Earlier review preferred a named synchronous terminal state over using `abortPromise` existence as the latch. The retained implementation uses one promise identity and current tests distinguish the required races. A wider enum refactor adds review surface without current evidence of a separate defect.

Disposition: defer unless target-native controls expose ambiguous ownership.

## Deferred: typed incomplete provider close

Silent close without finish/error has a different compatibility and result-model question. Campaign #94 owns it.

Disposition: outside unit 06.

## Deferred: run-scoped resumable Stop

Durable cancellation ownership across requests requires run identity and conditional state writes. Campaign #95 owns it.

Disposition: outside unit 06.
