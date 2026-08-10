# Upstream issue draft — first Codex issue candidate

> Hold for explicit public-contact authorization. Refresh the source links and duplicate search before posting.

## Title

Unified exec can omit command output when its completion listener starts late or falls behind

## Body

Unified exec can receive stdout or stderr from a command and still leave those bytes out of the completed tool result. Since Codex uses that result to decide what to do next, it can miss the line that explains a failure, a timeout, or a successful command.

Both the local output collector and the completion watcher read from broadcast receivers that can miss chunks sent before subscription or after falling behind.

The local output collector skips lagged chunks:

[`process.rs`](https://github.com/openai/codex/blob/c607da9f371bb66a41cc772c6ddf1989d28137d3/codex-rs/core/src/unified_exec/process.rs#L602-L632)

```rust
Err(tokio::sync::broadcast::error::RecvError::Lagged(_)) => continue,
```

The completion watcher uses the same handling while it builds the final transcript. If it subscribes late or falls behind, it can't recover the missing chunks.

### What I tested

I added a test that sends output before `start_streaming_output` subscribes. The change keeps that output and includes it in the completed command item.

I added another test that forces a live receiver to report `Lagged`. The live receiver misses chunks, but the completion copy still has the bytes received by `UnifiedExecProcess` within the existing output cap.

I ran the same lag test with invalid UTF-8 and added a test that checks a partial streaming transcript is replaced with the process-owned copy.

### Proposed change

[This implementation](https://github.com/teamleaderleo/codex/pull/144) adds a second `HeadTailBuffer` to `UnifiedExecProcess`. Each output chunk goes into that buffer before Codex broadcasts it. When output closes, the completion watcher replaces its partial transcript with the retained copy.

The completed command result then no longer depends on whether the listener kept up.
