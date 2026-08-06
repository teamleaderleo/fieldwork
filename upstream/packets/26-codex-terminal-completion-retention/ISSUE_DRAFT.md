# Upstream issue draft — first Codex issue candidate

> Hold for explicit public-contact authorization. Refresh the public source links and duplicate search immediately before posting.

## Title

Unified exec can omit command output when its completion listener starts late or falls behind

## Body

### Summary

Codex can receive stdout or stderr from a command and still leave those bytes out of the completed tool result.

Unified exec sends live output through a Tokio broadcast channel. The code that collects local process output skips chunks when its receiver reports `Lagged`. The completion watcher also skips `Lagged` chunks while building the transcript returned when the command finishes.

A completion listener can also subscribe after the command has already produced output. In both cases, the final transcript depends on when the listener started and whether it kept up with the broadcast channel.

### Current behavior

The local output collector currently handles lag like this:

[`process.rs` on the public source checked](https://github.com/openai/codex/blob/c607da9f371bb66a41cc772c6ddf1989d28137d3/codex-rs/core/src/unified_exec/process.rs#L602-L632)

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

The completion watcher follows the same rule while building the completed transcript:

[`async_watcher.rs` on the public source checked](https://github.com/openai/codex/blob/c607da9f371bb66a41cc772c6ddf1989d28137d3/codex-rs/core/src/unified_exec/async_watcher.rs#L88-L110)

```rust
let chunk = match received {
    Ok(chunk) => chunk,
    Err(RecvError::Lagged(_)) => continue,
    Err(RecvError::Closed) => break,
};

process_chunk(&mut pending, &transcript, /* ... */, chunk).await;
```

`Lagged` means that an internal receiver did not read the bounded broadcast channel quickly enough. It does not mean that the skipped output was unimportant. Once those chunks have been skipped, the completion watcher cannot reconstruct them.

### What we have confirmed

One test sends output before `start_streaming_output` subscribes. The proposed completion buffer preserves that early output and includes it in the completed command item.

A second test sends enough output to make a live receiver report `Lagged`. The live receiver misses chunks, while the proposed completion buffer retains the bytes accepted by `UnifiedExecProcess` within the existing output cap.

The same lag test also covers invalid UTF-8, so the retained completion state is based on raw command bytes rather than only successfully decoded text.

Another test starts with a partial streaming transcript and confirms that completion replaces it with the producer-owned bounded transcript.

These tests establish the listener-timing loss and show that producer-owned retention prevents it. They do not establish how often users encounter the problem or attribute every incomplete command result to this path.

### Why this matters

The completed tool result is part of the evidence Codex uses for its next decision. If the missing output contains the actual test failure, Codex can inspect the wrong code or rerun a test that already explained the problem. If the missing output contains an interactive prompt, the command can later time out without the result explaining what it was waiting for. If the missing output contains a success summary, Codex can repeat work that already completed.

This issue is not claiming that listener lag starts a timeout. It can remove the output that would explain the timeout or guide the next action. The same loss can affect commands that finish normally.

### Why this is not ordinary truncation

Unified exec already limits command output. `HeadTailBuffer` keeps a bounded beginning and ending and inserts an omission marker when it drops bytes from the middle. The model-facing formatter can apply another token limit and reports that truncation as well.

The listener-timing loss happens before those policies. It has no omission marker, and the amount lost depends on task scheduling and receiver speed. Two commands that print the same bytes can therefore produce different completed transcripts even when both are below the same configured output limits.

The proposed change does not remove either existing limit or send unlimited output to the model. It allows those limits to operate on the bounded output received by unified exec instead of on whichever chunks happened to reach the live listener.

### Proposed direction

The implementation proof adds a second bounded `HeadTailBuffer` to `UnifiedExecProcess`. Each local or exec-server output chunk is written to that completion buffer before the live broadcast is attempted.

[`process.rs` in the implementation proof](https://github.com/teamleaderleo/codex/blob/b2a704c708748462d7893fe82cf8971f00ca751e/codex-rs/core/src/unified_exec/process.rs#L444-L452)

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

When output closes, the completion watcher replaces its partial listener-built transcript with the bounded producer-owned copy:

[`async_watcher.rs` in the implementation proof](https://github.com/teamleaderleo/codex/blob/b2a704c708748462d7893fe82cf8971f00ca751e/codex-rs/core/src/unified_exec/async_watcher.rs#L148-L151)

```rust
reconcile_transcript(&transcript, &completion_buffer).await;
output_drained.notify_one();
```

Live output remains best effort. The change only separates live observation from the completed command record.

### Scope

This change would preserve output that reached `UnifiedExecProcess` before the existing completion boundary. It would not repair output lost by a driver or remote backend before that point. It would not guarantee bytes that arrive after the existing cancellation-grace window. It would not make interactive live prompts reliable, change process cleanup, or change remote execution settlement.

The completed item would continue to use the existing bounded head-and-tail representation for the whole process.

### Implementation and validation

The four-file implementation proof is available at [`teamleaderleo/codex#144`](https://github.com/teamleaderleo/codex/pull/144).

At that source revision:

- 12 focused terminal-output controls passed;
- the complete changed `codex-core` library passed with 2,133 tests;
- the paired unmodified baseline passed with 2,129 tests;
- the relevant integration targets compiled;
- formatting and the four-file source check passed.

Before submitting a patch, I would recreate it on current public main, add a direct baseline-red characterization for the new regressions, and rerun the same gates.

### Question

Should the completed unified-exec result come from the bounded output retained by the component that received the process bytes, rather than from the subset that reached a best-effort live listener?

### Related work

#35528 discusses output caps, omitted-byte accounting, persistence, and other residual-information problems. This report concerns an earlier loss point: command bytes can disappear because of listener timing before the existing truncation policies are applied.

No public upstream interaction has occurred.
