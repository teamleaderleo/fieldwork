# Upstream issue draft

Status: draft only. Public upstream contact remains unauthorized.

## Proposed title

Session callers cannot observe rollout append acknowledgement

## Draft

### Summary

`Session::record_conversation_items` updates conversation history and attempts to append rollout response items through the live thread, but the append result is currently logged and discarded before reaching the session caller.

A caller that needs conservative persistence certainty therefore cannot distinguish an acknowledged append from an append error at the authoritative session boundary.

### Current behavior

At current source, the call path is:

```text
Session::record_conversation_items
  -> persist_rollout_response_items
  -> persist_rollout_items
  -> LiveThread::append_items
```

`persist_rollout_items` logs an append error and returns unit.

### Proposed bounded behavior

Return the append acknowledgement from `record_conversation_items` while preserving existing behavior for callers that ignore it:

| case | result | durable item |
| --- | --- | --- |
| ephemeral session | success | no live store; live session history is authoritative |
| acknowledged live append | success | present |
| pre-write append failure | failure | absent |
| commit-then-error acknowledgement loss | failure | present |

The final case is important: an append error does not prove that the durable write is absent.

### Proposed implementation boundary

- return a boolean acknowledgement from `record_conversation_items`;
- return the same acknowledgement from the response-item persistence helper;
- preserve fire-and-log behavior for other rollout-item callers through a private checked helper;
- add deterministic one-shot in-memory store controls for pre-write failure and commit-then-error;
- add four focused tests for the state table above.

### Explicit follow-up work

A boolean acknowledgement does not distinguish definite omission from ambiguous commit/acknowledgement loss. Typed persistence certainty, retry authority, duplicate reconciliation, receipt ownership, replay, and compaction policy belong in later changes.

### Validation

```sh
cd codex-rs
cargo fmt --all -- --check
cargo test -p codex-core --lib --locked '<each exact append-outcome test>' -- --exact --nocapture
cargo test -p codex-thread-store --locked
```

### Process note

This draft should be used only after an upstream invitation and explicit authorization to contact public upstream.
