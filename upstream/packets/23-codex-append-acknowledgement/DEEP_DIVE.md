# Deep dive

## Problem

`Session::record_conversation_items` updates live conversation history, attempts to append rollout items through `LiveThread`, and emits raw response items. At current public Codex `670f69416bf91c5dfd8b58669e78050b584ff053`, the `LiveThread::append_items` result is logged inside `persist_rollout_items` and discarded before returning to the session caller.

A caller therefore cannot tell whether the authoritative append acknowledged. This blocks later receipt work from recording conservative persistence certainty at the correct boundary.

## Selected interface change

The selected source returns `bool` from `record_conversation_items`:

- `true` when no live thread exists, because the ephemeral session's live history remains authoritative for its lifetime;
- `true` when the live append returns success;
- `false` when the live append returns an error.

`persist_rollout_response_items` returns the same acknowledgement. A private checked helper performs the append and returns the result. Existing `persist_rollout_items` callers retain fire-and-log behavior by discarding the checked helper's return value.

Current analytics and raw-item emission remain in place. The acknowledgement reports only rollout persistence.

## Persistence states

### Ephemeral session

There is no `LiveThread`. `record_conversation_items` returns `true` after updating live history. This means the session's in-memory conversation record remains authoritative; it does not claim disk durability.

### Acknowledged live append

`LiveThread::append_items` returns success. The caller receives `true`, and the test reloads live-thread history and confirms the response item is present.

### Pre-write failure

The in-memory test store consumes a one-shot fault before extending durable history. The caller receives `false`, and reloaded history lacks the response item.

### Commit-then-error acknowledgement loss

The in-memory test store extends durable history and then consumes a one-shot error. The caller receives `false`, while reloaded history contains the response item.

This case proves that a generic append error cannot authorize retry. The durable effect may already exist.

## Why the return value stays boolean in this unit

The smallest prerequisite is observability at the session boundary. Typed certainty belongs in a successor slice with states such as:

- confirmed absence before write;
- acknowledged persistence;
- ambiguous commit or acknowledgement loss.

That successor also needs a stable operation identity and one session-lifetime receipt owner. Unit 23 supplies the observable append input only.

## Current-source reconciliation

The validated source at `926e0bc5a32b136f31b9eaae75e2de4abc20fa95` is a direct child of public `4642370542739d5dd080b0c87a9de06a6435d3db` and changes exactly three Rust files.

Public Codex advanced to `670f69416bf91c5dfd8b58669e78050b584ff053`. GitHub's merge engine reports the validated source conflicts with current `codex-rs/core/src/session/mod.rs`. Current session code contains newer image-preparation analytics and session changes. The two test-support files remain mechanically reusable.

The selected current approach therefore:

1. starts from exact public `670f6941...`;
2. copies validated `turn_tests.rs` and `in_memory.rs` blobs from `926e0bc5...`;
3. applies the small acknowledgement change semantically to current `session/mod.rs`;
4. preserves current analytics and raw response emission;
5. asserts the exact three-file source fence;
6. runs formatting, four unique exact controls, and the complete thread-store package;
7. publishes one direct-child clean source commit only after success.

## Test support

`InMemoryThreadStore` receives two one-shot, test/debug-only controls:

- fail the next non-empty append before writing;
- write the next non-empty append and then return an error.

Ordinary behavior stays unchanged when neither control is armed. Each control is consumed once.

## Risks and controls

- **Silent semantic drift:** current `session/mod.rs` is patched by exact anchors and fails when an expected anchor count differs from one.
- **Partial test selection:** the workflow lists library tests, requires exactly one full-name match for each declared suffix, then runs each with `--exact`.
- **Carrier pollution:** execution files live only on the carrier branch; the published source commit contains exactly the three Rust files.
- **Stale base:** the clean source parent is asserted as exact public `670f6941...`.
- **Retry misuse:** packet drafts explicitly state that `false` merges definite omission and ambiguous acknowledgement loss.
- **Public process violation:** upstream remains read-only until invitation and explicit contact authorization exist.

## Successor boundary

Deferred work:

- typed `Absent/Persisted/Ambiguous` certainty;
- durable operation receipt ownership;
- stable direct and nested Code Mode identities;
- replay and duplicate reconciliation;
- retry authority;
- compaction, resume, fork, rollback, and remote settlement policy.
