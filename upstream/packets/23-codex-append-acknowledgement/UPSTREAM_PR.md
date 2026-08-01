# Upstream pull-request draft

Status: draft only. Public upstream contact remains unauthorized, and current Codex contribution policy requires an invitation for external code contributions.

## Proposed title

fix(core): return durable append acknowledgement from session writes

## Draft body

### What

Return the rollout append acknowledgement from `Session::record_conversation_items` and add deterministic tests for successful append, pre-write failure, and commit-then-error acknowledgement loss.

### Why

The current session path logs `LiveThread::append_items` errors and discards the result. Later persistence-receipt work needs the authoritative append outcome at the session caller.

An append error has two materially different durable states:

- the write can fail before persistence;
- the write can persist and then lose its acknowledgement.

Both return failure in this bounded prerequisite. Tests preserve the durable-state distinction so later logic cannot treat every failure as proof of absence.

### How

- `record_conversation_items` returns the response-item append acknowledgement;
- `persist_rollout_response_items` forwards the checked result;
- a private checked helper returns `true` for an ephemeral session or acknowledged live append and `false` for an append error;
- existing rollout-item callers retain fire-and-log behavior;
- `InMemoryThreadStore` gains one-shot pre-write and post-write error controls for tests;
- four focused tests cover the complete bounded state table.

### Source fence

- `codex-rs/core/src/session/mod.rs`
- `codex-rs/core/src/session/turn_tests.rs`
- `codex-rs/thread-store/src/in_memory.rs`

### Tests

```sh
cd codex-rs
cargo fmt --all -- --check
cargo test -p codex-core --lib --locked '<full append-outcome test name>' -- --exact --nocapture
cargo test -p codex-thread-store --locked
```

Exact focused controls:

- `append_outcome_ephemeral_history_is_authoritative`
- `append_outcome_reports_successful_live_append`
- `append_outcome_reports_prewrite_failure`
- `append_outcome_reports_commit_then_error_as_failure`

### Boundary

This change reports append acknowledgement only. It does not classify persistence certainty into typed states, authorize retry, reconcile duplicates, alter compaction, restore receipts during replay, or settle remote tool effects.

### Risk

Existing callers can ignore the new return value and retain current behavior. The test-store controls are one-shot and inactive during ordinary operation.

### Submission gate

Use this draft only after:

1. current clean source tests and ordinary gates pass;
2. complete current diff review accepts the exact source head;
3. a matching upstream issue exists when required;
4. upstream explicitly invites the contribution;
5. public-contact authorization is granted.
