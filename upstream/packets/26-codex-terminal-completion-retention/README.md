# Unit 26 — Codex terminal completion retention

## Current disposition

`SUBMITTED — UPSTREAM ISSUE OPEN / MAINTAINER TRIAGE PENDING`

The owner reviewed the issue packet and filed [openai/codex#37207](https://redirect.github.com/openai/codex/issues/37207).

The report covers one concrete failure: unified exec can receive terminal bytes and still omit them from the completed command result when the completion listener subscribes late or falls behind.

## Selected boundary

The process producer retains the completion transcript before broadcasting live deltas.

- producer-owned retention is authoritative for completion;
- live delivery can still miss updates;
- late or lagged listeners cannot erase output already received by the process layer;
- invalid UTF-8 remains retained as bytes;
- existing head/tail limits remain in force;
- normal close replaces partial listener state with the retained transcript.

## Clean implementation proof

- Owned source PR: `teamleaderleo/codex#144`
- Base: `ee0247f95a6fe2b094ba2253d82cae2a2b4c2dff`
- Head: `b2a704c708748462d7893fe82cf8971f00ca751e`
- Branch: `fieldwork/26-terminal-completion-retention-source`
- Shape: one commit, four Rust files, 294 additions, 57 deletions

Files:

- `codex-rs/core/src/unified_exec/async_watcher.rs`
- `codex-rs/core/src/unified_exec/async_watcher_tests.rs`
- `codex-rs/core/src/unified_exec/process.rs`
- `codex-rs/core/src/unified_exec/process_tests.rs`

Review `4856710273` found no blocking issue inside the stated normal-close scope.

## Latest public comparison

Latest public source inspected before filing: `78f00743f92cf4fb875ddadcd30293c5201b48ac`, 95 commits after the implementation base.

All four source-base files remained byte-identical at that public head:

| File | Public-base/latest blob |
| --- | --- |
| `async_watcher.rs` | `d20a85843b1c108f94abb07a25c76cd7e156cb84` |
| `async_watcher_tests.rs` | `66fd8dba1194a17d1a1b19b3d257750fd88eb56e` |
| `process.rs` | `dd10930547f61f73b1ceb6c520e2f9db685c6a2a` |
| `process_tests.rs` | `e7f99e38ee731241e1b2a1cb6f590d4a560a5ad1` |

The duplicate search found no active proposal covering this specific late-or-lagged-listener loss in completed unified-exec output.

## Authoritative execution

Execution carrier `teamleaderleo/codex#137`, corrected run `30699322569`:

- baseline `codex-core` library: `2,129/2,129` passed;
- source exact terminal-retention controls: `12/12` passed;
- source `codex-core` library: `2,133/2,133` passed;
- integration targets compiled;
- formatting and exact four-file fence passed;
- paired baseline/source artifacts and logs retained.

## Submission receipt

- Upstream issue: [openai/codex#37207](https://redirect.github.com/openai/codex/issues/37207)
- State at filing: open
- Label at filing: `bug`
- Filed by the owner after reviewing the final four-section issue form
- Public implementation PR: none
- Owned implementation proof: `teamleaderleo/codex#144`

## Next state

Wait for maintainer triage. A public PR would require a separate owner decision and a fresh current-main restack, baseline-red regression run, and full gate.

No further public comment, reaction, pull request, review, or other upstream interaction is authorized.