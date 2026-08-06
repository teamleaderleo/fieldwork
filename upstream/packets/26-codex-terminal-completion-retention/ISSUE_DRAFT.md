# Upstream issue draft — first Codex issue candidate

> Hold for explicit public-contact authorization. Refresh the source links and duplicate search before posting.

## Title

Unified exec can omit command output when its completion listener starts late or falls behind

## Body

### Summary

Codex can receive stdout or stderr from a command and still leave those bytes out of the completed tool result.

Unified exec sends live output through a Tokio broadcast channel. The local collector skips chunks when its receiver reports `Lagged`, and the completion watcher does the same while it builds the final transcript. The watcher can also subscribe after the command has already printed something.

The completed result can therefore depend on when the listener started and whether it kept up.

### Where it happens

The local output collector currently does this:

[`process.rs` on the public source I checked](https://github.com/openai/codex/blob/c607da9f371bb66a41cc772c6ddf1989d28137d3/codex-rs/core/src/unified_exec/process.rs#L602-L632)

```rust
match receiver.recv().await {
    Ok(chunk) => {
        let mut guard = buffer.lock().await;
        guard.push_chunk(chunk.clone());
        drop(guard);
        let _ = output_tx.send(chunk);
        output_notify.notify_waiters();
    }
    Err(tokio::sync::broadcast::error::RecvError::Lagged(_)) => continue,
    Err(tokio::sync::broadcast::error::RecvError::Closed) => break,
}
```

The completion watcher follows the same rule:

[`async_watcher.rs` on the public source I checked](https://github.com/openai/codex/blob/c607da9f371bb66a41cc772c6ddf1989d28137d3/codex-rs/core/src/unified_exec/async_watcher.rs#L88-L110)

```rust
let chunk = match received {
    Ok(chunk) => chunk,
    Err(RecvError::Lagged(_)) => continue,
    Err(RecvError::Closed) => break,
};

process_chunk(&mut pending, &transcript, /* ... */, chunk).await;
```

When a receiver reports `Lagged`, the watcher skips those chunks and can't recover them later.

### What I tested

I made a test that sends output before `start_streaming_output` subscribes. The change keeps that output and includes it in the completed command item.

I made another test that sends enough output to make a live receiver report `Lagged`. The live receiver misses chunks, but the completion copy still has the bytes received by `UnifiedExecProcess` within the existing output cap.

I ran the same lag test with invalid UTF-8 to cover raw command bytes.

I also made a test that starts with a partial streaming transcript and checks that completion replaces it with the process-owned copy.

### Why it matters

The completed tool result is what Codex uses to decide what to do next.

If the missing output contains the real test failure, Codex can inspect the wrong code or rerun a test that already explained the problem. If it contains an interactive prompt, the command can time out without showing what it was waiting for. If it contains a success summary, Codex can repeat work that already finished.

The same loss can affect commands that finish normally.

### This happens before normal truncation

Unified exec already limits command output. `HeadTailBuffer` keeps the beginning and end, and it inserts an omission marker when it drops bytes from the middle. The model-facing formatter can apply another token limit and reports that truncation too.

Listener loss happens before either limit. It has no omission marker, and the amount lost depends on task timing and receiver speed. Two commands can print the same bytes and still produce different completed transcripts.

The change makes the existing limits operate on the output unified exec received instead of whichever chunks reached the live listener.

### The change

I added a second `HeadTailBuffer` to `UnifiedExecProcess`. Each local or exec-server output chunk goes into that completion buffer before Codex tries to broadcast it live.

[`process.rs` in the change](https://github.com/teamleaderleo/codex/blob/b2a704c708748462d7893fe82cf8971f00ca751e/codex-rs/core/src/unified_exec/process.rs#L444-L452)

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

When output closes, the completion watcher replaces its partial transcript with that retained copy:

[`async_watcher.rs` in the change](https://github.com/teamleaderleo/codex/blob/b2a704c708748462d7893fe82cf8971f00ca751e/codex-rs/core/src/unified_exec/async_watcher.rs#L148-L151)

```rust
reconcile_transcript(&transcript, &completion_buffer).await;
output_drained.notify_one();
```

Live output stays best effort, while the completed command result comes from the retained process output.

### Implementation and tests

The four-file change is here: [`teamleaderleo/codex#144`](https://github.com/teamleaderleo/codex/pull/144).

At that revision:

- 12 focused terminal-output tests passed;
- all 2,133 changed `codex-core` tests passed;
- all 2,129 tests passed on the paired unmodified baseline;
- the relevant integration targets compiled;
- formatting and the four-file source check passed.

Before sending a PR upstream, I'd recreate the change on current public main, run the new tests against unmodified main to record the expected failures, and rerun the same checks.

### Expected behavior

The completed unified-exec result should come from the output retained by the component that received the process bytes, rather than from the subset that reached a best-effort live listener.

### Related work

#35528 covers output caps, omitted-byte accounting, persistence, and other cases where information gets lost. This issue covers an earlier loss point: command output can disappear because of listener timing before the existing truncation rules run.
