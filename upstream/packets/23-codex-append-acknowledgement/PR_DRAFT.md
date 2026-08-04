# Upstream pull request draft — refresh required

> Do not post this exact draft. The retained source is an implementation proof on an older public pin. Recreate the semantic change on current main and rerun all gates after maintainers agree on the issue boundary.

## Title

fix(core): expose append acknowledgement from session history writes

## Summary

- return whether the required live-thread append acknowledged from `Session::record_conversation_items()`;
- preserve in-memory history updates, analytics, and raw-response delivery;
- preserve fire-and-log behavior for existing callers that ignore the result;
- add deterministic pre-write and commit-then-error controls;
- prove that an append error is not absence or retry authority.

## Semantics

- `true`: no live append is required, or the live append returned success;
- `false`: the append returned an error.

`false` intentionally covers both definite pre-write failure and unknown commit outcome. The commit-then-error control writes the item and then returns an error.

## Intended source fence

- `codex-rs/core/src/session/mod.rs`
- `codex-rs/core/src/session/turn_tests.rs`
- `codex-rs/thread-store/src/in_memory.rs`

## Retained evidence

Owned implementation proof: `teamleaderleo/codex#140@babc761faeb1bf618aa4a9495236336f6d63f006` over public base `2b5bdcf67547860f2e5c5a605009a70026796b2b`.

At that exact pin:

- formatting passed;
- four exact append-outcome controls passed;
- complete `codex-thread-store` passed;
- exact three-file fence passed;
- complete-diff review `4842611857` found no code issue.

Latest public source inspected at `7325f348a2ff9e1a7dd931ed9ad65f365d064146` still loses the append result, but `session/mod.rs` has changed since the proof base. The delivery source and all receipt identifiers must be replaced after refresh.

## Required refreshed test plan

```sh
cd codex-rs
cargo fmt --all -- --check
cargo test -p codex-core --lib --locked -- --list
# Resolve and run each append-outcome test by one exact full-name match.
cargo test -p codex-thread-store --locked
```

Also run current project-declared ordinary gates and verify one direct-child commit with only the three intended files.

## Non-goals

- caller policy changes;
- typed persistence certainty;
- retry, replay, or duplicate reconciliation;
- compaction/resume policy;
- operation receipt ownership;
- remote-effect settlement.

No public upstream interaction has occurred.