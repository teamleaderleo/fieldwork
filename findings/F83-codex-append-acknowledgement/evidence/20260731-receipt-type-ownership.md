# Codex mutation receipt type ownership — protocol state and tool effect

## In simple words

The historical receipt foundation placed operation effect and receipt lifecycle types in `codex-tools`. The current durable wire candidate places equivalent types in `codex-protocol`.

Carrying both would create two vocabularies for one operation. A runtime could classify an operation with one enum while persistence, compaction, resume, fork, and rollback serialized another.

Current Codex already gives `codex-tools` a dependency on `codex-protocol`. The clean ownership is:

- `codex-protocol` owns durable receipt vocabulary and serialization;
- `codex-tools` re-exports only `ToolOperationEffect` for `ToolExecutor` implementations;
- `codex-core` owns the canonical session ledger and lifecycle transitions;
- rollout and thread-store code persist protocol records;
- compaction, resume, fork, rollback, continuation, and retry consume the same protocol-owned state.

## Exact identity

- Public Codex source: `4642370542739d5dd080b0c87a9de06a6435d3db`, read-only.
- Receipt wire source: owned Codex #95 at `15414d7e5da8109e03dca24111664b272e4a5717`.
- Tool effect source: owned Codex #99 at `860f6babd420587dccc9e0d414f18ed157690958`.
- Tool effect carrier: owned Codex #100 at `d835c7966cc86d54838e4ecc4860905874f77057`.
- Historical tools-owned contract: `f84e8d6fb48917965b7dacc1b28147663a28dd84`.
- Historical selected-runtime begin: `73ae22f90300d632833f9e4a531c4dd857c5db36`.
- Retrieval date: `2026-07-31`.
- Public upstream interaction: none.

## Historical ownership

Historical commit `f84e8d6...` added these types to `codex-tools`:

```text
ToolOperationEffect
ToolOperationReceipt
ToolOperationTerminalState
ToolOperationResultState
TOOL_OPERATION_RECEIPT_VERSION
```

It also added `ToolExecutor::operation_effect()` with a conservative default.

That location was useful for the first behavior-neutral foundation because the runtime trait needed effect classification and no durable rollout protocol existed yet.

Later historical core work imported all receipt state from `codex-tools` into the session owner.

## Current durable ownership requirement

The receipt must cross crate and process boundaries:

- rollout JSONL serialization;
- thread-store persistence;
- compacted checkpoint carriage;
- resume and fork reconstruction;
- rollback tombstones;
- deferred continuation checkpoints;
- app-server or client diagnostics;
- future schema and TypeScript exports where needed.

`codex-protocol` is the existing owner for these cross-boundary records. Its public wire types derive Serde, JSON Schema, and TypeScript bindings.

The current receipt wire source therefore owns:

```text
ToolOperationEffect
ToolOperationTerminalState
ToolOperationResultState
ToolOperationReceipt
ToolOperationId
ToolOperationReceiptActivation
ToolOperationReceiptUpdate
ToolOperationReceiptCheckpoint
```

## Current tool contract

Owned Codex #99 adds a narrow stacked source slice:

```text
codex-rs/tools/src/lib.rs
codex-rs/tools/src/tool_executor.rs
codex-rs/tools/src/tool_executor_tests.rs
```

It:

1. re-exports `codex_protocol::tool_operation::ToolOperationEffect` from `codex-tools`;
2. adds `ToolExecutor::operation_effect()`;
3. defaults every unclassified executor to `PotentialMutation`;
4. permits an explicit `ReadOnly` override;
5. leaves terminal state, result state, logical identity, epoch, update, and checkpoint types out of `codex-tools`.

This preserves runtime ergonomics while keeping one durable vocabulary.

## Dependency direction

Current `codex-rs/tools/Cargo.toml` already contains:

```text
codex-protocol = { workspace = true }
```

The re-export creates no new crate dependency and no cycle.

Preferred imports:

### Runtime implementation

```rust
use codex_tools::ToolOperationEffect;
```

### Session ledger, persistence, replay, and checkpoint code

```rust
use codex_protocol::tool_operation::ToolOperationEffect;
use codex_protocol::tool_operation::ToolOperationReceipt;
use codex_protocol::tool_operation::ToolOperationId;
```

The types remain identical because the tools import is a re-export.

## Rejected alternatives

### Duplicate protocol and tools enums

Rejected because conversion code could lose versions, ambiguity, unknown variants, or future fields. Exhaustive matching would also split across two enum families.

### Keep all receipt state in `codex-tools`

Rejected for the current design because durable rollout and app-server protocol records would depend on execution-layer types and would need separate schema/export treatment.

### Keep effect only in `codex-tools` as a distinct enum

Rejected because every receipt begin would require conversion at the dispatch boundary. A future enum variant could be conservatively collapsed or silently mismatched.

### Move the executable trait into protocol

Rejected because `ToolExecutor` owns runtime behavior, futures, output, search metadata, exposure, and dispatch-facing capabilities. Protocol should own data vocabulary, not executable trait behavior.

## Source sequence consequence

The canonical live-owner restack should use the current stack:

1. #95 protocol-owned wire vocabulary;
2. #99 tools re-export and effect method;
3. exposure wrapper delegation in `codex-core`;
4. session-scoped owner using protocol types;
5. selected-runtime begin and certain pre-dispatch closure;
6. direct-result persistence using current append acknowledgement;
7. durable receipt envelope and replay.

The historical `codex-tools/src/tool_operation.rs` file should not be carried into the current stack.

## Exact controls

Tool effect source #99 includes:

```text
unclassified_executor_is_potentially_mutating
executor_can_declare_read_only_effect
```

Carrier #100 requires unique full-name resolution, `--exact` execution, formatting, exact source and carrier fences, and the complete `codex-tools` package.

Later core controls must prove:

- exposure wrappers delegate the selected runtime effect;
- direct/plaintext and dynamically exposed runtimes retain their exact effect;
- unsupported calls remain conservative;
- incompatible payload failures preserve the selected runtime effect;
- receipt begin happens once at the selected dispatch boundary.

## Current disposition

Disposition: `SELECT protocol-owned receipt vocabulary with tools re-export of effect`.

This selection removes one architecture fork before the current live-owner restack. It creates no public behavior change by itself.

## Boundary

- Owned source and synthetic tests only.
- No compaction gate, retry change, external mutation, deployment, or public upstream interaction.
