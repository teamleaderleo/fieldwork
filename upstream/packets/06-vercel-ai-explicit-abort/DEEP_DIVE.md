# Deep dive — explicit abort terminal ownership

## Question

When a caller-provided `AbortSignal` fires during `streamText`, which state transition owns the result, and which work may continue asynchronously?

## Source lineage

1. Public pin `2b872b0db3769decf69945830c66a897c1e37347` exposed the pending-read gap.
2. Maintainer-authored upstream PR #16852 at `0ef2ae9a7f143d90972b4ff217046e0b04ea67f1` added independent abort observation, root rejection, outward abort, and reader cancellation.
3. Owned characterization PR #1 at `e685a4c92a5869aec306718ab5a440b7cb4fa5b1` broadened root/derived, pre-abort, local-tool, multi-consumer, callback-stall, and provider-error coverage.
4. Owned repair PR #7 at `19a9dbe26b48af848f3202fa0c409ed67d034c7d` moved outward terminal mechanics before observability and made post-abort provider values/errors yield to abort.
5. Internal materialization PR #8 reconciled the five-file candidate onto public main `e84b8bc8154030cdb7469b0e0b8cd8b9354f19a0`, producing clean source head `92079da650430d8376a7eeef2436910b44393411`.

## Current control flow

The resilient outward stream installs one abort listener and retains one `abortPromise` latch. The first caller abort:

1. selects the abort path;
2. rejects the five result roots;
3. enqueues one outward abort part when the stream remains open;
4. closes the outward controller and removes its abort listener;
5. requests cancellation of the stitchable reader;
6. invokes application and telemetry abort callbacks without awaiting them.

A provider `reader.read()` result or error arriving after the latch exists yields to the same abort path. Ordinary consumer cancellation still cancels only that consumer-owned stream path.

## Result ownership

Direct roots:

- finish reason;
- raw finish reason;
- usage;
- steps;
- initial response messages.

Text, content, final step, output, tool collections, response metadata, and response messages derive from those roots. Rejecting roots once is the decisive public-settlement operation.

## Provider registration gap

The provider may return a `ReadableStream` after the caller signal fires but before that stream is registered with the stitchable owner. Cancelling the empty stitchable owner cannot reach this stream later, so the candidate checks the signal and directly cancels the returned provider stream.

Current code awaits that direct cancellation. `ReadableStream.cancel()` is provider-controlled through its underlying source and can reject or remain pending. Awaiting it leaves the internal setup task and captured state retained after public result settlement. The selected repair is a handled cancellation request:

```ts
void languageModelStream.cancel(getAbortReason()).catch(() => {});
return;
```

The exact implementation should keep timeout cleanup before the request and should add target-native controls for rejection and indefinite pending.

## Callback boundary

`notify()` catches individual callback failures. Detaching it is appropriate because observability follows terminal selection. A pending or rejecting callback must never hold public settlement, outward closure, or provider cancellation.

## Tool boundary

Cooperative local tools receive the operation signal. The SDK suppresses a later success claim after abort ownership. The SDK cannot undo a side effect already committed outside its process; issue and PR text must state this limit plainly.

## Compatibility boundary

The contribution preserves the difference between:

- operation abort through the caller signal;
- one consumer ending or cancelling its reader;
- ordinary provider failure before abort ownership;
- incomplete provider close, which belongs to a separate campaign.

## Strongest current conclusion

The terminal-ordering direction is supported by exact prior target execution. The current-main branch is source-materialized but still requires one concrete cancellation repair and current-head execution before promotion.