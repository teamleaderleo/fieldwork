# Upstream pull request draft

> Do not post without both an OpenAI contribution invitation and explicit Fieldwork public-contact authorization. Rebase and rerun all current gates immediately before use.

## Title

fix(core): expose durable append acknowledgement from session writes

## Summary

- return the authoritative live-thread append result from `Session::record_conversation_items`;
- preserve existing in-memory history, analytics, raw-response emission, and fire-and-log behavior for callers that ignore the result;
- add deterministic one-shot test-store faults for pre-write failure and commit-then-error acknowledgement loss;
- test ephemeral authority, acknowledged persistence, definite pre-write failure, and ambiguous commit-then-error separately.

## Semantics

The returned boolean means only whether the append call acknowledged:

- `true`: no live store is required, or the live append returned success;
- `false`: the append returned an error.

`false` is not proof that the item is absent. The commit-then-error test persists the item and then reports an error, so callers must not use this result alone as retry authority.

This change does not modify current caller policy. Existing production call sites continue to ignore the result.

## Files

- `codex-rs/core/src/session/mod.rs`
- `codex-rs/core/src/session/turn_tests.rs`
- `codex-rs/thread-store/src/in_memory.rs`

## Prepared validation receipt

Owned-fork source prepared from public base `670f69416bf91c5dfd8b58669e78050b584ff053`:

- current source head: `16cb14688dac752a5a13c180e94355b199f240a7`;
- one direct-child commit, three files;
- four exact append-outcome controls passed, `4/4`;
- full `codex-thread-store` package passed, `163/163`;
- formatting passed;
- current source reviewed with no findings;
- tested and current source heads have identical blobs for all three changed files.

## Test plan

```sh
cd codex-rs
cargo fmt --all -- --check
cargo test -p codex-core --lib --locked -- --list
cargo test -p codex-core --lib --locked 'session::turn::tests::append_outcome_ephemeral_history_is_authoritative' -- --exact --nocapture
cargo test -p codex-core --lib --locked 'session::turn::tests::append_outcome_reports_successful_live_append' -- --exact --nocapture
cargo test -p codex-core --lib --locked 'session::turn::tests::append_outcome_reports_prewrite_failure' -- --exact --nocapture
cargo test -p codex-core --lib --locked 'session::turn::tests::append_outcome_reports_commit_then_error_as_failure' -- --exact --nocapture
cargo test -p codex-thread-store --locked
```

Before authorized delivery, resolve full test names from `--list`, require exactly one match per selector, rerun against the then-current public base, and update all revisions and counts.

## Non-goals

- typed persistence certainty;
- retry, replay, or duplicate policy;
- compaction or resume policy;
- operation receipt ownership;
- remote-effect settlement.

## Process note

This draft is an owned Fieldwork handoff artifact. Public upstream interaction performed: none.