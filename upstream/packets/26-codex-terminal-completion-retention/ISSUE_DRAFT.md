# Upstream issue draft — first Codex issue candidate

> Hold for explicit public-contact authorization. Refresh the source links and duplicate search before posting.

## Title

Unified exec can omit command output when its completion listener starts late or falls behind

## Body

Unified exec can receive stdout or stderr from a command and still leave those bytes out of the completed tool result. Since Codex uses that result to decide what to do next, it can miss the line that explains a failure, a timeout, or a successful command.

The problem is that live output and final output both depend on best-effort broadcast listeners.

The local output collector skips chunks when its receiver reports `Lagged`:

[`process.rs`](https://github.com/openai/codex/blob/c607da9f371bb66a41cc772c6ddf1989d28137d3/codex-rs/core/src/unified_exec/process.rs#L602-L632)

```rust
Err(tokio::sync::broadcast::error::RecvError::Lagged(_)) => continue,
```

The completion watcher does the same while it builds the final transcript:

[`async_watcher.rs`](https://github.com/openai/codex/blob/c607da9f371bb66a41cc772c6ddf1989d28137d3/codex-rs/core/src/unified_exec/async_watcher.rs#L88-L110)

```rust
Err(RecvError::Lagged(_)) => continue,
```

The watcher can also subscribe after the command has already printed something. In either case, it can't recover the missing chunks later.

### What I tested

I made a test that sends output before `start_streaming_output` subscribes. The change keeps that output and includes it in the completed command item.

I made another test that forces a live receiver to report `Lagged`. The live receiver misses chunks, but the completion copy still has the bytes received by `UnifiedExecProcess` within the existing output cap.

I ran the same lag test with invalid UTF-8, and I added a test that starts with a partial streaming transcript and checks that completion replaces it with the process-owned copy.

### The change

I added a second `HeadTailBuffer` to `UnifiedExecProcess`. Each output chunk goes into that completion buffer before Codex broadcasts it live. When output closes, the completion watcher replaces its partial transcript with the retained copy.

The live stream stays best effort. The completed command result no longer depends on whether the live listener kept up.

The existing output caps still apply, including the head-and-tail retention and omission marker.

### Implementation and tests

The four-file change is here: [`teamleaderleo/codex#144`](https://github.com/teamleaderleo/codex/pull/144).

At that revision:

- 12 focused terminal-output tests passed.
- All 2,133 changed `codex-core` tests passed.
- All 2,129 tests passed on the paired unmodified baseline.
- The relevant integration targets compiled.
- Formatting and the four-file source check passed.

Before sending a PR upstream, I'd recreate the change on current public main, run the new tests against unmodified main to record the expected failures, and rerun the same checks.

The completed unified-exec result should come from the output retained by the component that received the process bytes, not from the subset that reached a best-effort live listener.

### Related work

#35528 covers output caps, omitted-byte accounting, persistence, and other cases where information gets lost. This issue covers an earlier loss point: command output can disappear because of listener timing before the existing truncation rules run.
