# Upstream pull request draft — use only after issue agreement

> Recreate the source as a direct child of current public main and rerun all gates before use.

## Title

fix(core): retain completed command output before live broadcast

## Summary

Unified exec currently uses broadcast receivers while collecting command output and again while building the completed transcript. Both paths skip `Lagged`, so output Codex already received can disappear before the completed tool result is created.

This change keeps a bounded completion buffer beside `UnifiedExecProcess`, records each chunk before sending the live update, and uses that buffer when the command completes.

## Current path

The local collector currently skips lagged chunks before adding them to its buffer:

```rust
match receiver.recv().await {
    Ok(chunk) => {
        buffer.lock().await.push_chunk(chunk.clone());
        let _ = output_tx.send(chunk);
    }
    Err(broadcast::error::RecvError::Lagged(_)) => continue,
    Err(broadcast::error::RecvError::Closed) => break,
}
```

The completion watcher also skips lagged chunks while building `transcript`:

```rust
let chunk = match received {
    Ok(chunk) => chunk,
    Err(RecvError::Lagged(_)) => continue,
    Err(RecvError::Closed) => break,
};

process_chunk(&mut pending, &transcript, /* ... */, chunk).await;
```

A listener can also subscribe after output has already been sent.

## New path

`UnifiedExecProcess` owns a second bounded `HeadTailBuffer` for the completed result:

```rust
async fn record_output_chunk(
    output_buffer: &OutputBuffer,
    completion_buffer: &OutputBuffer,
    chunk: &[u8],
) {
    completion_buffer.lock().await.push_chunk(chunk.to_vec());
    output_buffer.lock().await.push_chunk(chunk.to_vec());
}
```

Each producer records the chunk before broadcasting it:

```rust
Self::record_output_chunk(&output_buffer, &completion_buffer, &bytes).await;
let _ = output_tx.send(bytes);
output_notify.notify_waiters();
```

When output closes, the completion watcher replaces its partial transcript with that retained buffer:

```rust
reconcile_transcript(&transcript, &completion_buffer).await;
output_drained.notify_one();
```

The existing output cap, head/tail retention, omission marker, UTF-8 live-delta handling, cancellation grace, and synchronous fallback stay in place.

## Tradeoffs and open questions

### Backpressure

The local producer now copies each chunk into two bounded buffers before sending the live update. That removes the lossy intermediate collector, but it also moves buffer work closer to the command's stdout and stderr readers. A sustained-output test should check that concurrent stdout, stderr, and polling still complete without the queues backing up enough to stall the command.

### Live prompts

The completed result becomes more reliable. The live display can still miss an update. A missed interactive prompt may therefore show up only after the command times out. Reliable live interaction belongs in a separate change, possibly through replay, a retained snapshot, or an explicit lag signal.

### Earlier loss points

The completion buffer can only retain chunks that reach `UnifiedExecProcess`. Driver adapters and remote backends can have their own delivery gaps. The guarantee here should be phrased as the retained bounded copy of output accepted by this layer.

### Cancellation timing

The current 100 ms trailing-output grace stays in place. A test should cover chunks arriving immediately before, during, and after that boundary so the completion contract is explicit.

### Whole-process history

The completed item continues to represent the capped head/tail history for the whole process, even when earlier output has already been returned through polling. Maintainers may want to confirm that this is the intended meaning of the completed item.

### Internal state shape

The proof implementation uses two mutexes, one for the polling buffer and one for the completion buffer. A final patch could place both buffers under one `ProcessOutputState` mutex so each chunk advances both views under one lock. That would reduce lock traffic and remove a partial-update window if the output task is cancelled between the two writes.

## Files

- `codex-rs/core/src/unified_exec/async_watcher.rs`
- `codex-rs/core/src/unified_exec/async_watcher_tests.rs`
- `codex-rs/core/src/unified_exec/process.rs`
- `codex-rs/core/src/unified_exec/process_tests.rs`

## Current tests

The focused tests cover:

- output emitted before the completion listener subscribes;
- a deliberately lagged live receiver while the completion buffer retains the bytes;
- invalid UTF-8 through the same lag path;
- replacement of a partial streamed transcript with the retained completion transcript;
- local and exec-server producer ordering;
- normal close, cancellation grace, bounded output, and synchronous fallback behavior.

## Extra tests before an upstream patch

1. Sustained simultaneous stdout and stderr while another task polls and drains the polling buffer.
2. Repeated polling followed by completion, confirming that the final item still contains the capped whole-process history.
3. Output arriving around the trailing-output grace deadline.
4. App-server coverage showing live deltas followed by a consistent completed item.
5. Many concurrent noisy processes to check memory and scheduling behavior.

Prepared implementation proof: `teamleaderleo/codex#144@b2a704c708748462d7893fe82cf8971f00ca751e`.

Corrected paired execution run `30699322569`:

- baseline library: `2,129/2,129`;
- source focused controls: `12/12`;
- source library: `2,133/2,133`;
- integration targets compiled;
- formatting and exact four-file fence passed.

All four source-base files were still byte-identical on public head `c607da9f371bb66a41cc772c6ddf1989d28137d3` when the packet was last refreshed.

## Follow-ups

Timeout triggers, reliable live prompts, process-tree cleanup, bytes arriving after forced termination, conversation-history persistence, and remote execution settlement stay in their own issue tracks.

No public upstream interaction has occurred.
