# Codex append acknowledgement — direct current-source materialization

## In simple words

The accepted append-acknowledgement source previously lived on public Codex `a01a2d...`. Public Codex advanced through three unrelated commits.

The exact accepted source blobs now sit in one source commit directly parented by current inspected public Codex `464237...`. This removes the stale-base question without regenerating or editing the source.

A separate one-file carrier owns renewed formatting, four exact controls, and the complete `codex-thread-store` package.

## Exact identity

- Fieldwork issue: #83.
- Current read-only public Codex: `4642370542739d5dd080b0c87a9de06a6435d3db`.
- Current owned source PR: `teamleaderleo/codex#97`.
- Current source branch: `fieldwork/83-append-outcome-464237`.
- Current source head: `926e0bc5a32b136f31b9eaae75e2de4abc20fa95`.
- Current source parent: `4642370542739d5dd080b0c87a9de06a6435d3db`.
- Current execution carrier: `teamleaderleo/codex#98`.
- Carrier head at opening: `8161e9ee3423d78768263e8838bd6e4800178902`.
- Accepted predecessor source: `teamleaderleo/codex#84@d8299b7fdf3aaf7ebc46d2cac840828cf97fc2a2`.
- Accepted predecessor run: `30583967538`.
- Accepted predecessor review: `4823945751`.
- Public upstream interaction: none.

## Source construction

The current source commit uses the current public tree as its base and replaces exactly three paths with the accepted predecessor blobs.

| Path | Accepted blob SHA |
| --- | --- |
| `codex-rs/core/src/session/mod.rs` | `b43fb385b8738600f942845fde1b4400fef3dd41` |
| `codex-rs/core/src/session/turn_tests.rs` | `cd78a86704d6fe152fde0b522c8f8bc2927c36c5` |
| `codex-rs/thread-store/src/in_memory.rs` | `bbf69a3c7fb85076eaf0ebcd1d5799433caae9a4` |

The resulting current-source tree commit is `926e0bc5a32b136f31b9eaae75e2de4abc20fa95`.

## Exact diff

Comparison from public `464237...` to current source `926e0bc...`:

- status: one commit ahead;
- merge base: `464237...`;
- changed files: exactly three;
- `session/mod.rs`: 15 additions, 7 deletions;
- `session/turn_tests.rs`: 148 additions;
- `thread-store/src/in_memory.rs`: 27 additions.

No workflow, generator, evidence, or temporary file exists in the source branch.

## Behavior retained

The current source preserves the accepted bounded contract:

- `Session::record_conversation_items` returns canonical append acknowledgement;
- live conversation history still records the prepared item before durable append;
- raw response item publication remains after the append attempt;
- no `LiveThread` means success under ephemeral live-memory authority;
- acknowledged append returns success;
- pre-write failure returns failure;
- commit-then-error acknowledgement loss returns failure;
- ordinary callers of `persist_rollout_items` keep fire-and-log behavior through the checked helper;
- in-memory deterministic failure hooks distinguish failure before write from failure after authoritative write.

## Current execution carrier

Carrier #98 is stacked directly on source #97 and changes one workflow file:

```text
.github/workflows/fieldwork-83-append-outcome-464237.yml
```

It requires:

1. exact source parent relation;
2. exact three-file source fence;
3. exact one-file carrier fence;
4. `cargo fmt --all -- --check`;
5. unique full-name resolution for four declared tests;
6. four executions using `--exact`;
7. complete `codex-thread-store` package.

Declared tests:

```text
append_outcome_ephemeral_history_is_authoritative
append_outcome_reports_successful_live_append
append_outcome_reports_prewrite_failure
append_outcome_reports_commit_then_error_as_failure
```

## Evidence state

| Claim | Evidence class | Support | Limit |
| --- | --- | --- | --- |
| Current source is directly parented by public `464237...` | `source-read` | commit and compare metadata | none for source identity |
| Current source reuses the accepted three blobs | `source-read` | exact blob SHAs | target execution remains renewed separately |
| Predecessor behavior passed four exact controls | `target-executed` | run `30583967538` | predecessor base `a01a2d...` |
| Current source behavior passes renewed controls | `Unknown` | carrier #98 | update after carrier conclusion |

## Current disposition

Source disposition: `ACCEPT byte-identical current materialization; EXECUTE renewed target controls`.

The source clears the direct-current-head packaging prerequisite at the Git identity and diff level. Final promotion still requires:

- successful current carrier receipt;
- independent complete-diff review at `926e0bc...`;
- source PR, issue #83, F83 finding, F239 synthesis, and carrier retirement records synchronized.

## Boundary

This source exposes append acknowledgement only. Typed `Absent/Persisted/Ambiguous`, duplicate reconciliation, receipt replay, compaction gates, external outcome certainty, and retry authority remain successor work.

No merge, deployment, credentials, production mutation, or public upstream interaction is authorized.
