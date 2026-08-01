# Deep dive — producer-owned terminal completion transcript

## Problem statement

Unified exec streams process output through a Tokio broadcast channel. Broadcast delivery is intentionally best-effort: a receiver can attach after early output, lag behind the ring, or disappear. Completion, however, needs an authoritative terminal transcript.

Before this change, the completion path could derive its final output from what a subscriber observed. That made final stdout/stderr dependent on subscriber timing. A process could complete successfully while its completion item omitted bytes that the producer had already read.

The failure has three important forms:

1. **Pre-subscription output loss.** The process emits bytes before the completion watcher subscribes.
2. **Lag loss.** The receiver falls behind the broadcast ring and receives `Lagged` instead of every chunk.
3. **Receiver closure.** Best-effort broadcast has no active receiver, yet the producer still owns valid output bytes.

## Selected design

The producer retains a bounded byte transcript for stdout and stderr while continuing to publish best-effort chunks.

### Producer authority

The output-reading task owns the bytes first. It appends each read to a bounded `VecDeque<u8>` before attempting broadcast delivery. Completion therefore has a producer-owned source independent of receiver timing.

The ordering rule is deliberate:

1. read bytes from stdout/stderr;
2. append them to retained output;
3. attempt best-effort broadcast;
4. continue through EOF;
5. return retained bytes to completion.

A closed or lagging receiver can affect live streaming while leaving final retained output intact.

### Bounded retention

Retention is bounded to prevent an unbounded process transcript from growing memory indefinitely. When capacity is exceeded, the oldest bytes leave the deque. Tests cover that cap and verify forward progress with invalid UTF-8.

The selected patch keeps raw bytes in the producer path. Conversion to display text occurs with lossy UTF-8 handling where required. Raw-byte retention avoids splitting assumptions during collection.

### Reconciliation

Completion can have two views:

- bytes already observed through streaming;
- the producer-retained authoritative transcript.

The patch reconciles them by finding suffix/prefix overlap. It appends only the non-overlapping retained suffix, which prevents duplicate output when both views contain the same tail/head boundary.

The focused process tests cover:

- output emitted before subscription;
- replacement of a partial streamed transcript with authoritative completion output;
- overlap handling.

### Normal EOF

Normal EOF collects the producer result and uses it to complete the process item. The final completion output survives best-effort broadcast failure.

### Hard termination

Hard termination has a separate latency contract. It must complete promptly even when an output receiver closes or the stream task remains in an awkward state. The tests preserve this behavior while adding retention.

## Exact current diff

Current public base:

- [`openai/codex@670f69416bf91c5dfd8b58669e78050b584ff053`](https://redirect.github.com/https://github.com/openai/codex/commit/670f69416bf91c5dfd8b58669e78050b584ff053)

Unit-owned source:

- [`teamleaderleo/codex@a020d7bd3e7f6886c3fbc21d75b3110586df08f5`](https://github.com/teamleaderleo/codex/commit/a020d7bd3e7f6886c3fbc21d75b3110586df08f5)
- tree `9a067c244d464e863a7b50978826ac9930df680b`
- [four-file comparison](https://github.com/teamleaderleo/codex/compare/670f69416bf91c5dfd8b58669e78050b584ff053...a020d7bd3e7f6886c3fbc21d75b3110586df08f5)

Changed files:

| File | Role |
|---|---|
| `async_watcher.rs` | retain raw producer bytes before best-effort broadcast; preserve EOF/termination behavior |
| `async_watcher_tests.rs` | exercise early output, lag/closure, invalid UTF-8, bounded retention, and termination |
| `process.rs` | reconcile streamed output with authoritative retained completion bytes |
| `process_tests.rs` | cover pre-subscription output and partial-stream reconciliation |

The unit-owned restack reuses the exact blobs from live source PR #125 at `ee605985012dc1b768f03f6b450db16dd5c0467e`. It adds no workflow file and no unrelated source change.

## Drift analysis

The prior live source base was `3d1d26915a303c3b4765828f973f5464f8c28c5c`. Current public main is `670f69416bf91c5dfd8b58669e78050b584ff053`, 24 commits later at the time of packet preparation.

Across that range:

- none of the four source/test files changed;
- `codex-rs/core/tests/suite/unified_exec.rs` gained one adjacent line;
- the four exact blobs applied cleanly over current public main.

This makes the restack mechanically clean while leaving one semantic duty: run current-head tests because adjacent integration behavior changed.

## Failure and evidence chronology

### Initial reproduction and prototype

[Fieldwork PR #33](https://github.com/teamleaderleo/fieldwork/pull/33) documented late-reader loss and the producer-retention design. [Codex PR #6](https://github.com/teamleaderleo/codex/pull/6) provided the first implementation and focused execution:

- formatting/fix/diff checks passed;
- new pre-subscription and reconciliation tests passed;
- 99 tests executed, 95 passed;
- four sandbox/network SIGABRT failures appeared baseline-like.

That work established feasibility and left packaging and execution cleanup.

### Source-only publication and carrier attempts

[Codex PR #49](https://github.com/teamleaderleo/codex/pull/49) published a four-file source-only restack. Shared and specialized carriers followed through PRs #50, #53, and #70. PR #53 recorded setup-only failures including missing `just`, shallow history, and missing `uv`; those runs provide no product evidence.

### Authoritative pass

[Fieldwork PR #268](https://github.com/teamleaderleo/fieldwork/pull/268) exported the strongest accepted execution. Run `30587866332` passed all nine exact controls, the full `codex-core` library gate, and integration-target compilation for source head `8c7ea38419d790032db459816980e6b4dd38f574`.

### Later source lineage

The four-file patch was republished across later public bases in Codex PRs #86, #91, #93, and #125. PR #94 failed a source-consistency guard before product execution.

PR #126 is the latest retained-head carrier. Its source guard, baseline build, and nine exact controls passed for PR #125 head `ee605985012dc1b768f03f6b450db16dd5c0467e`. The broader focused `codex-core` gate failed; the exact failure text remains unavailable in the retained connector response.

## Risks

### Stream-semantics risk

The patch changes ownership of the authoritative completion transcript. Review needs to verify that reconciliation never duplicates, truncates, or reorders bytes across stdout/stderr boundaries.

### Memory-cap risk

Bounded retention intentionally discards oldest bytes beyond the cap. The chosen cap and resulting user-visible semantics deserve explicit review.

### UTF-8 risk

The producer retains bytes and later performs lossy conversion. Tests cover invalid sequences and progress, while reviewers should inspect boundary behavior near the retention cap.

### Termination risk

Normal EOF waits for retained output; hard termination must stay prompt. The test suite contains dedicated termination cases because a seemingly safe await can create a shutdown hang.

### Current-head risk

The current restack is mechanically clean and unexecuted. A current-head carrier run remains required.

## Prior-art search

Searches of public Codex code, issues, and pull requests for the exact title and for terminal broadcast lag/completion transcript terms found no direct existing producer-retention implementation or duplicate proposal. One loose Windows desktop polling issue appeared and was excluded because it concerns a separate path.

No public-upstream comment, issue, branch, or pull request was created.
