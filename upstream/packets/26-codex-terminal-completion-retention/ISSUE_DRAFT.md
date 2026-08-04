# Upstream issue draft — first Codex issue candidate

> Hold for explicit public-contact authorization. Refresh the public source and overlap search immediately before posting.

## Title

Unified exec can lose command output when the live listener starts late or falls behind

## Body

I started looking into this because some tool calls would time out or finish without enough output to explain what had happened. While tracing that, I found a separate problem in unified exec: Codex can receive command output and still leave it out of the completed tool result.

### Where this happens

When Codex runs a shell command or another command-based tool, `UnifiedExecProcess` collects the command's stdout and stderr. It sends live chunks through a broadcast channel, and `start_streaming_output` subscribes to that channel and builds the transcript used when the command completes.

The current local output collector skips anything reported as `Lagged`:

[`process.rs` on the latest public source checked](https://github.com/openai/codex/blob/c607da9f371bb66a41cc772c6ddf1989d28137d3/codex-rs/core/src/unified_exec/process.rs#L602-L632)

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
    Err(tokio::sync::broadcast::error::RecvError::Closed) => {
        // ...
        break;
    }
}
```

The completion watcher has the same behavior while it builds the transcript:

[`async_watcher.rs` on the latest public source checked](https://github.com/openai/codex/blob/c607da9f371bb66a41cc772c6ddf1989d28137d3/codex-rs/core/src/unified_exec/async_watcher.rs#L88-L110)

```rust
let chunk = match received {
    Ok(chunk) => chunk,
    Err(RecvError::Lagged(_)) => {
        continue;
    },
    Err(RecvError::Closed) => {
        output_complete = true;
        break;
    }
};

process_chunk(
    &mut pending,
    &transcript,
    // ...
    chunk,
).await;
```

A listener may either start after the command has already printed something or fall behind when a command produces a lot of output. In either case, unified exec can receive bytes that never reach the transcript returned in the completed tool result.

### What we've confirmed

The tests force both timing conditions and check that the proposed completion buffer retains the output:

- output emitted before `start_streaming_output` subscribes is present in the completed command item after the fix;
- a deliberately lagged receiver misses chunks while the completion buffer retains all bytes within the existing cap;
- the same lag test covers invalid UTF-8 bytes;
- a partial streaming transcript is replaced with the completion buffer at completion.

The examples below describe what can follow when a missing chunk contained information Codex needed; they haven't each been reproduced as separate product bugs.

### Why do we care?

```text
A test prints the real failure early
        ↓
the listener misses that chunk
        ↓
the completed result contains later output without the failure
        ↓
Codex may rerun the test or inspect the wrong file
```

```text
A script prints a prompt and waits for input
        ↓
the prompt is missing from the completed result
        ↓
the command later times out without an explanation
        ↓
Codex may increase the timeout or repeat the same command
```

```text
A command succeeds and prints the useful summary
        ↓
the listener misses some or all of that summary
        ↓
Codex receives an empty or incomplete completed result
        ↓
Codex may repeat work that already succeeded
```

This probably isn't what starts a timeout. It can remove the output that would explain the timeout and guide the next action. The same loss can affect commands that finish normally.

### Proposed change

The proposed implementation keeps a second bounded `HeadTailBuffer` beside `UnifiedExecProcess`. Each chunk goes into that completion buffer before the live broadcast:

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

The producer records the chunk, then sends the live update:

```rust
Self::record_output_chunk(&output_buffer, &completion_buffer, &bytes).await;
let _ = output_tx.send(bytes);
output_notify.notify_waiters();
```

At completion, the watcher replaces its partial transcript with the retained completion copy:

[`async_watcher.rs` in the implementation proof](https://github.com/teamleaderleo/codex/blob/b2a704c708748462d7893fe82cf8971f00ca751e/codex-rs/core/src/unified_exec/async_watcher.rs#L148-L151)

```rust
reconcile_transcript(&transcript, &completion_buffer).await;
output_drained.notify_one();
```

The completed result would keep using the existing capped head/tail representation. Large command output would still keep the beginning and ending plus the omission marker.

### What this changes, and what stays separate

A late or lagging live listener would stop deciding what appears in the completed result. The live display could still miss an update, including an interactive prompt. Output lost before it reaches `UnifiedExecProcess`, or output arriving after the current cancellation-grace window, would stay outside this change. The completed item would continue to represent the capped history for the whole process rather than only the output since the last poll.

I put together the four-file implementation and tests here: `teamleaderleo/codex#144`.

At that exact source revision:

- 12 focused terminal-output controls passed;
- the complete source `codex-core` library passed alongside a green paired baseline;
- integration targets compiled;
- formatting and the four-file source fence passed.

The implementation shows the current behavior and one possible repair. The question is:

**Should the completed unified-exec result come from the bounded output kept by the component that received it, rather than from whichever chunks reached the live listener?**

### Follow-ups

The timeout trigger itself, reliable delivery of interactive prompts, process cleanup after cancellation, output that arrives after forced termination, and remote execution state sit in other parts of the execution lifecycle. They can follow as separate investigations.

No public upstream interaction has occurred.
