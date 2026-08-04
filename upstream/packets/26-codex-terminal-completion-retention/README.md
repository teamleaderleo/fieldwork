# Unit 26 — Codex terminal completion retention

## Current disposition

`ISSUE FIRST / TECHNICAL EVIDENCE COMPLETE / PUBLIC CONTACT HOLD`

This remains the first proposed Codex issue in the internal sequence after refreshing public source and duplicate state through `openai/codex@78f00743f92cf4fb875ddadcd30293c5201b48ac`.

The concrete failure is information loss: unified exec receives terminal bytes at the process producer, then relies on a best-effort broadcast subscriber to assemble the completed command transcript. Output emitted before subscription or skipped by a lagged receiver can therefore disappear from the completed item.

## Selected boundary

The process producer must retain one bounded authoritative transcript before broadcasting live deltas.

- producer-owned retention is authoritative for completion;
- broadcast remains best effort for live observation;
- late or lagged observers cannot erase producer-received terminal bytes;
- invalid UTF-8 remains retained as bytes;
- existing head/tail bounds remain in force;
- normal close replaces partial observer state from the producer-owned bounded transcript.

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

Latest public source inspected: `78f00743f92cf4fb875ddadcd30293c5201b48ac`, 95 commits after the implementation base.

All four source-base files remain byte-identical at that public head:

| File | Public-base/latest blob |
| --- | --- |
| `async_watcher.rs` | `d20a85843b1c108f94abb07a25c76cd7e156cb84` |
| `async_watcher_tests.rs` | `66fd8dba1194a17d1a1b19b3d257750fd88eb56e` |
| `process.rs` | `dd10930547f61f73b1ceb6c520e2f9db685c6a2a` |
| `process_tests.rs` | `e7f99e38ee731241e1b2a1cb6f590d4a560a5ad1` |

Recent public work added durable user-submission queues, paginated transcript history, and related session features, but did not modify this four-file terminal-output boundary. The implementation therefore remains mechanically file-disjoint from intervening public changes. Before an authorized PR, recreate it as a direct child of the then-current public head and rerun the gate.

Refreshed public issue and PR searches found no active proposal specifically covering completed unified-exec transcript loss caused by pre-subscription or lagged best-effort observers.

## Authoritative execution

Execution carrier `teamleaderleo/codex#137`, corrected run `30699322569`:

- baseline `codex-core` library: `2,129/2,129` passed;
- source exact terminal-retention controls: `12/12` passed;
- source `codex-core` library: `2,133/2,133` passed;
- integration targets compiled;
- formatting and exact four-file fence passed;
- paired baseline/source artifacts and logs retained.

Earlier failed carriers remain historical setup or wrong-gate evidence and do not weaken this paired receipt.

## Why this issue comes first

This is the clearest first contact because it has all four properties at once:

1. **Direct user-visible loss:** a completed command can omit stdout or stderr that Codex already received.
2. **Exact owner error:** a best-effort observer is allowed to own the final record instead of the producer.
3. **Bounded repair:** four files, no public API or generalized receipt framework.
4. **Strong evidence:** deterministic reproductions, paired full-library execution, integration compilation, and a reviewed clean source.

The next bounded issues are:

1. append acknowledgement at the session persistence boundary;
2. Responses Lite first-generated-request lineage after prewarm;
3. cleanup and remote-outcome visibility only where it does not duplicate existing public liveness reports.

Do not file an umbrella “Codex loses information” issue. Use the shared authority principle as context while keeping each failure independently actionable.

## Limits

This unit does not claim:

- recovery of bytes produced after the existing hard-termination grace boundary;
- unbounded output retention;
- process-tree cleanup or reattachment;
- durable conversation-history append;
- remote effect settlement;
- a general receipt architecture.

## Eventual issue approach

Lead with the concrete loss mechanism and the two deterministic cases. Ask whether producer-owned bounded retention is the intended authority boundary. Link near the end to Codex #144 as implementation evidence. Do not link execution carriers, Fieldwork packet machinery, or superseded sources.

No public upstream issue, comment, pull request, review, or reaction has occurred.