# Codex unified-exec authoritative completion transcript

## Status

- Fieldwork issue: `#23`
- Scout report: `report.md`
- Target repository: `teamleaderleo/codex`
- Pinned target revision: `3725f02cf38d856bc82bb46dd68ab61bb96ec6fc`
- Fork-only implementation branch: `fieldwork/23-unified-exec-authoritative-transcript`
- Fork-only pinned review base: `fieldwork/23-pinned-base`
- Draft implementation PR: `teamleaderleo/codex#6`
- Final reviewed head: `f0265ec46830ca7dc7cd059438e457378aa6b1bb`
- Upstream contact: none

## Campaign selected

The implementation follows the highest-ranked scout candidate: completed unified-exec command items can diverge from producer-captured subprocess output when the output-event subscriber starts late or falls behind the 64-entry broadcast channel.

The first code stage narrows the guarantee to terminal completion:

> A completed command item is assembled from producer-owned bounded output, independent of event-subscriber delivery.

Live output deltas remain best-effort in this stage.

## Implementation

Three Codex files change against the pinned target revision:

1. `codex-rs/core/src/unified_exec/process.rs`
2. `codex-rs/core/src/unified_exec/async_watcher.rs`
3. `codex-rs/core/src/unified_exec/async_watcher_tests.rs`

### Producer-owned completion buffer

`UnifiedExecProcess` now owns a second bounded `HeadTailBuffer` for command completion. The existing output buffer remains drainable by `exec_command` and `write_stdin` polling. The completion buffer is retained until output closes.

Each local or exec-server output chunk is recorded in this order:

1. completion buffer
2. drainable polling buffer
3. broadcast to live delta subscribers
4. output notification

Recording completion first favours terminal correctness if process cleanup interrupts the output task between awaits.

### Completion reconciliation

The streaming watcher continues to consume the broadcast and emit UTF-8-safe live deltas. It no longer builds the terminal transcript from those events.

After producer output closes, the watcher drains the producer-owned completion buffer into the command transcript and only then signals `output_drained`. The exit watcher already waits for `output_drained`, late network-denial classification, and the per-terminal interaction lock before emitting the completed command item.

The synchronous output collected for short-lived commands remains a fallback while the reconciled transcript is empty. A self-review pass removed a redundant branch that always preferred fallback output, because that could discard a richer producer transcript when reconciliation had already completed.

### Bounded memory

The patch keeps both producer buffers bounded by the existing `HeadTailBuffer` policy. Removing live transcript accumulation avoids retaining a third output copy. At steady state the process owns:

- one bounded drainable polling buffer
- one bounded completion buffer
- the existing 64-entry broadcast queue

## Regression coverage

### Pre-subscription output

`completed_item_includes_output_emitted_before_subscription` sends an output marker before `start_streaming_output`, waits until the producer captures it, starts the watcher and exit watcher, closes the process, and asserts the actual completed command item contains the marker.

This covers the first loss window directly.

### Partial transcript replacement

`reconcile_transcript_replaces_partial_stream_with_authoritative_output` constructs 128 identified chunks in the producer completion buffer while a simulated event transcript contains only chunks 64 through 127. Reconciliation must replace the partial transcript byte-for-byte and drain the producer source.

This models the deterministic 64-entry receiver-lag result retained in the scout artifacts.

## Verification

The implementation workbench used asserted source transformations and removed itself before the final code commit.

- `just fmt`: passed
- `just fix -p codex-core`: passed
- `git diff --check`: passed
- focused unified-exec run: 99 tests executed, 95 passed
- both new regression tests passed

Four existing integration cases failed in the hosted runner:

- glob-deny read policy
- network-denial background end event
- sandbox execution
- short-lived network-denial end event

Their subprocesses exited with the hosted filesystem-sandbox SIGABRT pattern. The broader `codex-core` run showed the same environmental failure class in unrelated sandbox and approval cases. No source assertion, compiler, formatter, fixer, or new regression failed.

A final review-only refinement restored transcript-first resolution and passed Rust formatting plus diff validation. It removed code and did not alter types or call signatures.

## Self-review findings

### Kept

- Producer output is the source of truth for terminal completion.
- Live delta delivery stays isolated from completion correctness.
- Local and exec-server paths share the same recording helper.
- Completion is written before polling output.
- Reconciliation transfers ownership and releases the retained completion buffer.
- The final PR is based on the pinned scout SHA and contains exactly three changed files.

### Deferred

1. Live deltas still silently continue after `RecvError::Lagged`; clients cannot identify a gap.
2. The local path still lacks sequence numbers and replay reads comparable to the exec-server path.
3. Two producer buffers can differ if the output task is interrupted between their two lock acquisitions. Completion is intentionally favoured.
4. Short-lived command collection and the watcher use different post-exit close windows. A later close-and-drain campaign should unify that lifecycle contract.
5. A production-path test that deterministically induces more than 64 live broadcast chunks would strengthen the helper-level lag regression.

## Synthesis

This patch removes the event subscriber from the terminal-completion trust boundary. Broadcast remains useful for responsive deltas and may lose messages without corrupting the final command item. The next logical campaign is sequence-aware live delivery with an explicit gap signal, followed by a common close-and-drain protocol for normal exit, interruption, termination, and capacity eviction.
