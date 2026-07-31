# Codex mutation receipt live owner — current source map and restack contract

## In simple words

The historical live receipt owner is useful evidence, but it cannot be copied onto current Codex as a blob set.

Current Codex has advanced by 160 public commits from the historical owned owner and has changed session, state, tool registry, Code Mode, app-server, fork, resume, and thread-store code. The historical owner also keys receipts by a direct call ID string and imports receipt state from `codex-tools`.

The current restack should instead:

- use the protocol-owned receipt vocabulary selected in #95/#99;
- key the canonical session ledger by `ToolOperationId` from the beginning;
- preserve direct and Code Mode identity without parallel maps;
- keep one session-scoped owner;
- add live transitions before durable replay;
- consume current append acknowledgement for direct result persistence;
- preserve exact selected-runtime effect through wrappers and dispatch.

## Exact identity

- Public Codex: `4642370542739d5dd080b0c87a9de06a6435d3db`, read-only.
- Receipt wire source: owned Codex #95 at `15414d7e5da8109e03dca24111664b272e4a5717`.
- Tool effect source: owned Codex #99 at `860f6babd420587dccc9e0d414f18ed157690958`.
- Append source: owned Codex #97 at `926e0bc5a32b136f31b9eaae75e2de4abc20fa95`.
- Historical canonical owner: `f9da1593f2499f6acde081d405c1a5df4ee2ea00`.
- Historical direct persistence: `1d9cc9709bb4c71b7b388e2baf0ab131e5585a61`.
- Historical selected-runtime begin: `73ae22f90300d632833f9e4a531c4dd857c5db36`.
- Historical effect wrapper: `e6b3017f4c725e0e6c48fc4e7fa703e365b2be67`.
- Retrieval date: `2026-07-31`.
- Public upstream interaction: none.

## Historical slices

### Session owner

Historical owner changes covered:

```text
codex-rs/core/src/session/mod.rs
codex-rs/core/src/session/tool_operation.rs
codex-rs/core/src/state/mod.rs
codex-rs/core/src/state/session.rs
codex-rs/core/src/state/tool_operation_receipts.rs
codex-rs/core/src/state/tool_operation_receipts_tests.rs
codex-rs/core/src/tools/lifecycle.rs
```

The accepted design moved live receipts from turn lifetime to session lifetime, capped retained receipts at 1,024, preserved evidence on overflow, treated late observations conservatively, escalated repeated identity, and exposed a fail-closed preflight query.

### Direct result persistence

Historical direct persistence changed:

```text
codex-rs/core/src/session/mod.rs
codex-rs/core/src/session/turn.rs
codex-rs/core/src/session/turn_tests.rs
```

It extracted direct function, MCP, custom, and client-executed tool-search call IDs from `ResponseInputItem`, recorded persistence only after the authoritative append outcome, and recorded ambiguity after append failure.

### Selected runtime begin

Historical selected-runtime begin changed:

```text
codex-rs/core/src/tools/lifecycle.rs
codex-rs/core/src/tools/registry.rs
codex-rs/core/src/tools/registry_tests.rs
```

It moved receipt begin from generic lifecycle start to the exact selected runtime boundary, preserved the runtime’s declared effect, kept unsupported calls conservative, and closed certain pre-dispatch failures.

### Exposure wrapper

Historical wrapper delegation changed:

```text
codex-rs/core/src/tools/registry.rs
codex-rs/core/src/tools/registry_tests.rs
```

It ensured an exposure override delegated `operation_effect()` to the underlying runtime.

## Why blob carry-forward is unsafe

A comparison from historical owner `f9da1593...` to current public `464237...` is diverged:

```text
ahead_by: 160
behind_by: 38
merge_base: 20dafe201d91d4405eef05ecd1db0257f13a9ac8
```

Current public source has broad changes across session and protocol surfaces, including:

- standalone Code Mode host/runtime separation;
- new app-server thread and item models;
- resume and fork metadata changes;
- updated tool and MCP surfaces;
- session state changes;
- rollout reconstruction and thread-store changes.

The current `state/mod.rs` and `state/session.rs` blobs differ from the historical owner. A direct historical blob replacement could erase unrelated current behavior.

The current owner therefore requires semantic source authoring against exact current files.

## Current ownership model

### Protocol

`codex-protocol` owns:

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

### Tools

`codex-tools` owns executable runtime behavior and re-exports:

```text
ToolOperationEffect
```

`ToolExecutor::operation_effect()` defaults to `PotentialMutation`.

### Core session

`codex-core` owns one canonical live ledger on `SessionState`.

### Persistence

Rollout and thread-store code persist protocol-owned receipt records and compacted checkpoints.

## Revised live ledger key

Historical code keyed the map by:

```text
String call_id
```

Current source should key by:

```text
ToolOperationId
```

Examples:

```text
Direct(call_id)
CodeMode(cell_id, runtime_tool_call_id)
```

This prevents a later nested Code Mode slice from adding a second owner or inventing synthetic host identity.

## Candidate live ledger

A current owner needs at least:

```text
receipts: HashMap<ToolOperationId, ToolOperationReceipt>
coverage_lost: bool
```

A later durable generation adds:

```text
receipt_epoch
next_update_sequence
replay_status
lineage ownership
retirement watermark
```

The first live slice should remain behavior-neutral outside receipt observation and avoid claiming durable restoration.

## Required transitions

### Begin

```text
begin(operation_id, effect)
```

Rules:

- first identity inserts a pending receipt;
- repeated identity escalates effect to `PotentialMutation`;
- repeated identity marks terminal and result state ambiguous;
- capacity exhaustion sets permanent coverage loss;
- no existing evidence is silently evicted.

### Terminal

```text
record_terminal(operation_id, terminal_state)
```

Rules:

- missing identity creates a conservative potential-mutation receipt;
- identical terminal state is idempotent;
- conflicting or invalid transition becomes ambiguous;
- terminal observation alone does not establish result persistence or external outcome.

### Result persistence

```text
record_result_persisted(operation_id)
record_result_ambiguous(operation_id)
```

Rules:

- missing identity creates conservative evidence;
- duplicate persistence becomes ambiguous;
- append failure becomes ambiguous even when the item may have committed;
- direct and Code Mode identities cannot update each other.

### Query

```text
receipt(operation_id)
has_unreconciled_potential_mutation()
coverage_lost()
```

The preflight query remains unused by compaction until replay, checkpoint, and retirement work lands.

## Exact selected-runtime boundary

Receipt begin should occur after the registry selects the executable runtime and before handler dispatch.

This boundary knows:

- the actual runtime object;
- the actual operation effect;
- direct call identity;
- whether dispatch can begin.

Unsupported tool names remain potential mutations and can close as certain pre-dispatch failures.

Payload incompatibility after runtime selection retains the selected runtime effect and closes as a pre-dispatch failure.

Generic lifecycle notification is too early because it lacks the exact selected runtime effect.

## Exposure wrappers

Every wrapper around a `ToolExecutor` must delegate `operation_effect()` unless the wrapper intentionally tightens the effect conservatively.

Current controls should cover:

- hidden exposure override;
- direct exposure override;
- deferred exposure;
- namespaced alias;
- dynamic runtime wrapper;
- direct/plaintext invocation;
- optional Code Mode host fallback where the same runtime survives selection.

A missing delegation defaults to `PotentialMutation`, which is safe while reducing read-only continuity. A wrapper must never downgrade a potentially mutating runtime to read-only.

## Direct result boundary

Current direct result persistence should stack on append source #97 and the live owner.

The direct in-flight drain remains the likely result owner for:

```text
FunctionCallOutput
McpToolCallOutput
CustomToolCallOutput
client ToolSearchOutput
```

Server-executed search output stays outside the client receipt path.

The transition order:

1. extract `ToolOperationId::Direct(call_id)`;
2. convert the response input into a response item;
3. append to live history;
4. call the authoritative rollout append boundary;
5. mark `Persisted` after success;
6. mark `Ambiguous` after failure;
7. publish raw response items as current behavior requires.

Handler completion remains terminal observation, not persistence evidence.

## Nested Code Mode boundary

The current live owner must accept `ToolOperationId::CodeMode` before nested delivery is wired.

The nested slice later needs:

- cell identity;
- runtime tool call identity;
- exact selected nested runtime effect;
- authoritative nested result append boundary;
- source-qualified terminal and persistence updates.

Synthetic host call IDs remain transport metadata.

## Recommended source slices

### Slice 1 — live ledger only

Likely fence:

```text
codex-rs/core/src/session/mod.rs
codex-rs/core/src/session/tool_operation.rs
codex-rs/core/src/state/mod.rs
codex-rs/core/src/state/session.rs
codex-rs/core/src/state/tool_operation_receipts.rs
codex-rs/core/src/state/tool_operation_receipts_tests.rs
```

Behavior:

- one session-scoped `ToolOperationId` ledger;
- no production begin caller;
- focused transitions and capacity controls;
- no compaction, replay, or retry behavior.

### Slice 2 — wrapper effect delegation

Likely fence:

```text
codex-rs/core/src/tools/registry.rs
codex-rs/core/src/tools/registry_tests.rs
```

### Slice 3 — selected-runtime begin and terminal closure

Likely fence:

```text
codex-rs/core/src/tools/lifecycle.rs
codex-rs/core/src/tools/registry.rs
codex-rs/core/src/tools/registry_tests.rs
```

### Slice 4 — direct result persistence

Stack on current append source and the live owner:

```text
codex-rs/core/src/session/turn.rs
codex-rs/core/src/session/turn_tests.rs
```

`session/mod.rs` append changes already live in #97 and should not be duplicated.

## Required exact controls

### Live ledger

1. potential mutation reconciles only after terminal plus persisted result;
2. persistence before terminal stays blocked and later reconciles;
3. duplicate persistence becomes ambiguous;
4. conflicting terminal outcomes become ambiguous;
5. repeated identity escalates effect and ambiguity;
6. late terminal observation creates conservative evidence;
7. late result observation creates conservative evidence;
8. read-only pending receipt does not block mutation preflight;
9. explicit persistence failure stays ambiguous;
10. overflow sets coverage loss without eviction;
11. direct and Code Mode identity remain distinct;
12. duplicate direct identity cannot collide with Code Mode identity.

### Selected runtime

1. read-only runtime effect reaches receipt begin;
2. default runtime remains potential mutation;
3. unsupported call closes before dispatch;
4. incompatible payload closes before dispatch with selected effect;
5. terminal transition occurs once when finish hooks race or repeat;
6. exposure wrapper preserves runtime effect.

### Direct result

1. direct identity classifier covers each direct output variant;
2. server search output stays excluded;
3. append success marks persisted;
4. append failure marks ambiguous;
5. duplicate result observation becomes ambiguous;
6. result without begin remains unreconciled;
7. direct output cannot update Code Mode identity.

## Current disposition

Disposition: `AUTHOR current live ledger directly; split wrapper, selected-runtime, and direct-result wiring into bounded successors`.

The historical owner remains design and test evidence. Current source should use protocol types and `ToolOperationId`, and should avoid carrying historical workflow files or turn-scoped residue.

## Boundary

- Synthetic tests and owned source only.
- No compaction gate, durable replay, retry, deployment, production mutation, or public upstream interaction.
