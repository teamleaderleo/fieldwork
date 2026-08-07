# Upstream pull request draft — use only after issue agreement

> Recreate the source as a direct child of current public main and rerun all gates before use.

## Title

fix(core): retain completed command output before live broadcast

## Summary

Unified exec uses broadcast receivers for live command output and for the transcript returned when a command finishes. A listener can subscribe after output was sent or fall behind and skip chunks.

This change stores the polling and completion buffers together in one shared `OutputState`. Each producer updates both buffers under one mutex before broadcasting the live chunk. When the command closes, the completion watcher replaces its partial transcript with the retained completion buffer.

## Current path

The local collector can skip lagged chunks before adding them to its buffer:

```rust
Err(broadcast::error::RecvError::Lagged(_)) => continue,
```

The completion watcher uses the same handling while it builds the final transcript. It can also subscribe after the command has already produced output.

## New path

```rust
struct OutputState {
    output: HeadTailBuffer,
    completion: HeadTailBuffer,
}
```

The process exposes separate polling and completion views backed by the same `Arc<Mutex<OutputState>>`.

Each producer updates both views while holding that mutex:

```rust
let mut state = output_buffer.state.lock().await;
state.completion.push_chunk(chunk.to_vec());
state.output.push_chunk(chunk.to_vec());
```

The lock is released before the live broadcast. When output closes, the completion watcher drains the completion view into the completed transcript.

The existing output cap, head/tail retention, omission marker, UTF-8 live-delta handling, cancellation grace, and synchronous fallback stay in place.

## Files

- `codex-rs/core/src/unified_exec/async_watcher.rs`
- `codex-rs/core/src/unified_exec/async_watcher_tests.rs`
- `codex-rs/core/src/unified_exec/process.rs`
- `codex-rs/core/src/unified_exec/process_tests.rs`

## Tests

The focused tests cover:

- output emitted before the completion listener subscribes;
- a deliberately lagged live receiver while the completion view retains the bytes;
- invalid UTF-8 through the same lag path;
- replacement of a partial streamed transcript with the retained completion transcript;
- local and exec-server producer ordering;
- normal close, cancellation grace, capped output, and synchronous fallback behavior.

## Current implementation

Prepared implementation proof: `teamleaderleo/codex#144@d4ff73f50e30e96b6db4a08205c9d3600e15488e`.

Current-head CI:

- `v8-canary` run `31072774070`: passed;
- `blocking-ci` run `31072774224`: completed with repository-level failures;
- formatting, Rust benchmark smoke, cargo-shear, blob-size policy, cargo-deny, and codespell passed;
- manifest/SDK and platform Bazel failures prevented the blocking workflow from completing the useful Linux Bazel test, clippy, release-build, and argument-lint gates, which were cancelled.

The earlier paired run `30699322569` remains the complete execution receipt for the previous two-mutex head. The current single-mutex head is the preferred implementation shape, but a future public PR should be recreated on current main and receive a fresh complete gate.

## Before a public PR

1. Recreate the patch on current public main.
2. Run the new regressions against unmodified main and retain the expected failures.
3. Run the focused tests, complete `codex-core` library, integration compilation, formatting, and source-file fence.
4. Review the complete current-main diff.

No public pull request has been opened.
