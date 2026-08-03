# Tests and receipts

## Exact current gate

Carrier script executed from public base `670f69416bf91c5dfd8b58669e78050b584ff053`:

```sh
cd codex-rs
cargo fmt --all -- --check
cargo test -p codex-core --lib --locked -- --list
cargo test -p codex-core --lib --locked '<resolved full test name>' -- --exact --nocapture
cargo test -p codex-thread-store --locked
```

Declared selectors:

1. `append_outcome_ephemeral_history_is_authoritative`
2. `append_outcome_reports_successful_live_append`
3. `append_outcome_reports_prewrite_failure`
4. `append_outcome_reports_commit_then_error_as_failure`

The script lists library tests, requires exactly one full-name match for every selector, runs each resolved name with `--exact`, counts executions, and fails unless the count is four.

## Current materialization receipt

- Carrier PR: `teamleaderleo/codex#132`
- Carrier head: `4bd35b35dee5649c6ba5af4c3535af2081c58bfc`
- Run: `30674601315`
- Job: `91299123673`
- Generated/tested source head: `06971a3a2b95d70a809472bfbd6fe7884063a563`
- Source parent: `670f69416bf91c5dfd8b58669e78050b584ff053`
- Source fence: exactly three Rust files

Observed exact controls:

- `append_outcome_ephemeral_history_is_authoritative`: 1 passed; 0 failed; 2129 filtered out
- `append_outcome_reports_successful_live_append`: 1 passed; 0 failed; 2129 filtered out
- `append_outcome_reports_prewrite_failure`: 1 passed; 0 failed; 2129 filtered out
- `append_outcome_reports_commit_then_error_as_failure`: 1 passed; 0 failed; 2129 filtered out
- Guard: `FIELDWORK_APPEND_OUTCOME_EXACT=4/4`

Other results:

- `cargo fmt --all -- --check`: passed
- `cargo test -p codex-thread-store --locked`: 163 passed; 0 failed; 0 ignored; 0 measured; 0 filtered out
- Source publication: passed

No `running 0 tests` result was accepted for any declared selector.

## Current-head equivalence

Current clean source:

- Branch: `teamleaderleo/codex:fix/session-durable-append-acknowledgement`
- Head: `16cb14688dac752a5a13c180e94355b199f240a7`
- Parent: `670f69416bf91c5dfd8b58669e78050b584ff053`
- Review PR: `teamleaderleo/codex#136`

The tested and current commits diverge only by commit identity. Their product blobs are identical:

| file | tested head blob | current head blob |
| --- | --- | --- |
| `codex-rs/core/src/session/mod.rs` | `6a35b541245007424fd8f268a408225e9e262009` | `6a35b541245007424fd8f268a408225e9e262009` |
| `codex-rs/core/src/session/turn_tests.rs` | `cd78a86704d6fe152fde0b522c8f8bc2927c36c5` | `cd78a86704d6fe152fde0b522c8f8bc2927c36c5` |
| `codex-rs/thread-store/src/in_memory.rs` | `bbf69a3c7fb85076eaf0ebcd1d5799433caae9a4` | `bbf69a3c7fb85076eaf0ebcd1d5799433caae9a4` |

Therefore job `91299123673` validates the exact current product tree, while the record preserves that the job itself published `06971a3...`, not `16cb146...`.

## Current-head ordinary CI

Workflow runs associated with `16cb1468...`:

- v8-canary `30691381091`: success
- v8-canary `30753787181`: success
- blocking-ci `30691381212`: failure
- blocking-ci `30753787253`: failure

Passing current-head checks include:

- Rust formatting and benchmark smoke test;
- cargo-deny;
- codespell;
- cargo-shear;
- changed-area detection;
- blob-size policy.

The latest blocking run first fails in `repo-checks / build-test` at `verify_cargo_workspace_manifests.py`, which reports an unrelated stale `[features]` exception for `codex-rs/code-mode/Cargo.toml`. That file is outside the unit fence. Many Bazel/SDK jobs then fail or cancel under the blocking workflow. This is a repository-baseline gate, not a source-diff failure.

## Historical receipts

- Source #51 / run `30550323542`: four exact controls and 158 thread-store tests on historical base `b545c940...`; retired.
- Carrier #52 / failed run `30560746088`, job `90932794178`: transform failed before tests; zero controls; no source publication.
- Source #84 through carrier #80 / run `30583967538`, job `91010830120`: exact fences, four controls, complete package, review `4823945751`; predecessor.
- Source #97 through carrier #98 / run `30598744048`: exact fences, four controls, complete package; latest predecessor before current reconciliation.

Historical counts must not be substituted for the current receipt. The current complete package count is 163.

## Review receipt

- Source PR: `teamleaderleo/codex#136`
- Current source head: `16cb14688dac752a5a13c180e94355b199f240a7`
- Review: `4841949952`
- Result: no findings inside the three-file fence
- Explicit boundary: all four production callers currently ignore the returned acknowledgement.