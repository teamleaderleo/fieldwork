# Deep dive — producer-owned terminal completion output

## Failure mechanism

Unified exec has two different consumers of process output:

- live observers receive `ExecCommandOutputDelta` events through a Tokio broadcast channel;
- command completion needs one authoritative bounded transcript for `aggregated_output`.

Broadcast is intentionally best effort. A receiver can subscribe after the process has already emitted output or receive `Lagged` after falling behind the ring. That is acceptable for live progress. It is not acceptable when the same receiver-owned transcript becomes the completed command record.

The lost information is not hypothetical observer metadata. It is stdout/stderr already received by the process owner.

## Selected implementation

`UnifiedExecProcess` owns two bounded head/tail buffers:

1. the existing ordinary output buffer used by process reads;
2. a completion buffer reserved for the authoritative final transcript.

Both local and exec-server producer paths call one helper that writes the chunk to the completion buffer and ordinary output buffer before attempting broadcast.

### Local producer

The previous local path combined stdout and stderr through an intermediate broadcast receiver, then used another task to populate the Codex output buffer and live broadcast. That intermediate broadcast could lag before Codex retained the chunk.

The selected source consumes the split stdout/stderr `mpsc` receivers directly with the same `tokio::select!` merge shape. Each chunk is retained before the live broadcast send. This removes one unnecessary lossy hop.

### Exec-server producer

Each ordered server chunk is likewise written into both bounded buffers before broadcast and notification. Sequence filtering remains unchanged.

### Completion watcher

The streaming watcher still:

- emits live UTF-8 deltas under the existing event-size cap;
- ignores `Lagged` for live observation;
- enters the existing trailing-output grace after process exit;
- drains available broadcast events on normal output close.

Before it signals `output_drained`, it drains the producer-owned completion buffer and replaces the partial observer transcript with that authoritative bounded transcript.

This is replacement, not suffix/prefix overlap inference. Older packet descriptions of a standalone deque and overlap algorithm belong to superseded prototypes.

## Why replacement is correct here

The producer and observer transcripts use the same bounded `HeadTailBuffer` semantics. The producer buffer contains the complete bounded view of all chunks received by Codex, including bytes the observer missed. Replacing the observer transcript therefore removes timing dependence without duplicating overlapping chunks.

For synchronous command completion, the existing nonempty fallback remains authoritative. The producer transcript supplies background/unified-exec completion.

## Concurrency and shutdown

`OutputTaskGuard` still publishes output closure if the local output task exits. Producer writes occur before closure publication. The watcher observes closure with acquire ordering before its final drain.

The source does not widen the hard-termination contract. If producer bytes arrive only after the existing grace boundary, they are not newly guaranteed. The repair is specifically for information already received before the normal completion boundary but missed by the live subscriber.

## Bounded memory

The second buffer is bounded by the existing head/tail buffer implementation. The cost is one additional bounded transcript per active process, not unbounded output accumulation.

## Exact source and evidence

- source PR: `teamleaderleo/codex#144`
- base: `ee0247f95a6fe2b094ba2253d82cae2a2b4c2dff`
- head: `b2a704c708748462d7893fe82cf8971f00ca751e`
- review: `4856710273`
- corrected paired execution: run `30699322569`

Execution passed 12/12 focused controls, the complete source library (`2,133/2,133`), the paired baseline library (`2,129/2,129`), formatting, exact fence checks, and integration compilation.

## Current public drift

At public `7325f348a2ff9e1a7dd931ed9ad65f365d064146`, all four source-base files have the same blobs as at `ee0247f...`. The candidate is mechanically file-disjoint from intervening public changes.

## Wider architectural lesson

This finding is one instance of a recurring authority mistake:

- live broadcast is not final transcript authority;
- raw response delivery is not durable history acknowledgement;
- a non-generating prewarm response is not generated-turn lineage;
- a deadline or cancellation request is not terminal effect certainty.

The correct upstream strategy is not one umbrella rewrite. Preserve each piece of information at its owning boundary through small, separately reviewable issues.

## Non-goals

- general operation receipts;
- unbounded terminal history;
- process-tree termination;
- remote reattachment or settlement;
- conversation-history durability;
- bytes produced after the existing hard-termination grace boundary.

No public upstream interaction occurred.