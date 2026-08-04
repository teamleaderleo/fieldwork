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

When output closes, the completion watcher replaces its partial transcript with that producer-owned buffer:

```rust
reconcile_transcript(&transcript, &completion_buffer).await;
output_drained.notify_one();
```

The existing output cap, head/tail retention, omission marker, UTF-8 live-delta handling, cancellation grace, and synchronous fallback stay in place.

## Files

- `codex-rs/core/src/unified_exec/async_watcher.rs`
- `codex-rs/core/src/unified_exec/async_watcher_tests.rs`
- `codex-rs/core/src/unified_exec/process.rs`
- `codex-rs/core/src/unified_exec/process_tests.rs`

## Tests

The focused tests cover:

- output emitted before the completion listener subscribes;
- a deliberately lagged live receiver while the completion buffer retains the bytes;
- invalid UTF-8 through the same lag path;
- replacement of a partial streamed transcript with the producer-owned transcript;
- local and exec-server producer ordering;
- normal close, cancellation grace, bounded output, and synchronous fallback behavior.

Prepared implementation proof: `teamleaderleo/codex#144@b2a704c708748462d7893fe82cf8971f00ca751e`.

Corrected paired execution run `30699322569`:

- baseline library: `2,129/2,129`;
- source focused controls: `12/12`;
- source library: `2,133/2,133`;
- integration targets compiled;
- formatting and exact four-file fence passed.

All four source-base files were still byte-identical on public head `78f00743f92cf4fb875ddadcd30293c5201b48ac` when the packet was last refreshed.

## Follow-ups

Timeout triggers, process-tree cleanup, bytes arriving after forced termination, conversation-history persistence, and remote execution settlement stay in their own issue tracks.

No public upstream interaction has occurred.
