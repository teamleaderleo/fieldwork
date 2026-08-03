# Upstream issue draft

> Do not post without both an OpenAI contribution invitation and explicit Fieldwork public-contact authorization. Re-check current public source and duplicate state immediately before use.

## Title

Expose durable append acknowledgement at the Codex session history boundary

## Body

### Problem

`Session::record_conversation_items` updates session history, attempts to append rollout items, and emits raw response items, but callers cannot observe whether the authoritative live-thread append acknowledged.

That makes it unsafe for later receipt or retry work to distinguish an acknowledged append from an error. A storage error is also not proof that the item is absent: an append may commit and then lose its acknowledgement.

### Proposed bounded prerequisite

Return a persistence acknowledgement from `record_conversation_items` while preserving existing caller behavior:

- no live thread: `true` under ephemeral-session authority;
- acknowledged live append: `true`;
- pre-write append failure: `false`;
- commit-then-error acknowledgement loss: `false` even when reloaded history contains the item.

The return is acknowledgement only. It does not authorize retry and does not distinguish definite absence from ambiguous commit.

### Intended source fence

- `codex-rs/core/src/session/mod.rs`
- `codex-rs/core/src/session/turn_tests.rs`
- `codex-rs/thread-store/src/in_memory.rs`

### Validation prepared in owned fork

On public base `670f69416bf91c5dfd8b58669e78050b584ff053`:

- four exact append-outcome tests passed;
- complete `codex-thread-store` package passed, 163/163;
- formatting passed;
- one direct-child, three-file source commit prepared and reviewed;
- pre-write failure and commit-then-error are tested separately.

### Explicit non-goals

- caller policy changes;
- typed persistence certainty;
- retry or replay authority;
- duplicate reconciliation;
- compaction, resume, fork, rollback, or remote-effect settlement.

### Process note

This draft is preserved only as a handoff artifact. No public upstream interaction has occurred.