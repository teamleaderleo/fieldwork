# Rust authority and replay patterns in current Codex

Date: 2026-07-31  
Fieldwork owner: F239 portfolio synthesis  
Base Fieldwork generation: `7c9a64b94dc50efe47816986b672323d1593f58c`  
Latest public Codex generation inspected: `f0c30e528a54bdf0fa9a4d52ff74b34383434811`  
Public upstream interaction: none

## Purpose

This note records current public Codex implementation patterns that sharpen the review standard for the active terminal, MCP, receipt, replay, and coordination proposals. It is not a new implementation owner and does not broaden any existing finding.

The recurring question is not whether one patch uses idiomatic syntax. It is whether the types, ownership boundaries, and transitions preserve the exact fact that a later decision depends on.

## 1. Persisted facts outrank caller-supplied assertions

Public Codex commit `f0c30e528a54bdf0fa9a4d52ff74b34383434811` derives report prompt metadata from the persisted rollout rather than accepting client tags.

Relevant source:

- `codex-rs/app-server/src/feedback.rs`.

The implementation removes reserved `prompt_hash` and `prompt_version` tags before applying metadata. It restores `prompt_hash` only when it can derive the value from persisted `SessionMeta` base instructions. A missing or unmatched rollout does not preserve the caller's unverified value.

General rule:

```text
untrusted projection input
-> remove reserved authority fields
-> reconstruct from canonical persisted state
-> publish only derived facts
```

This is the same rule required for Fieldwork projections, mutation receipts, and MCP callable authority: a UI, request, carrier, or dispatch packet may reference authoritative facts but may not assert them into existence.

## 2. Normalize only fields proven non-semantic

Public Codex commit `745603a5a1eb48b6f343633d622eeb72dd549d7b` removes top-level `internal_chat_message_metadata_passthrough` before rollout-trace item reconciliation, while retaining nested metadata as model-visible content.

Relevant source:

- `codex-rs/rollout-trace/src/reducer/conversation/normalize.rs`;
- `codex-rs/rollout-trace/src/reducer/conversation_tests.rs`.

The boundary is intentionally narrow:

- one top-level field is classified as transport/passthrough metadata and excluded from semantic identity;
- nested occurrences remain part of the item and conflicting reuse is rejected;
- call-id reuse is allowed only after this declared normalization.

General rule:

```text
semantic equality != whole serialized object equality
semantic equality != remove every field with a familiar name
semantic equality = typed or deliberately field-scoped canonicalization
```

This directly informs the MCP authority proposal. Whole `ToolInfo` JSON equality is too broad, but an untyped ad hoc subset is too fragile. The durable form should be a named authority key whose routing, schema, capability, and execution fields are deliberately owned, while presentation and transport fields are explicitly excluded.

## 3. Coupled checkpoints advance together or not at all

Public Codex commit `6256a7ccc7948231befc33d7d61b369041e6eb16` repairs thread-history projection after malformed or rejected rollout lines.

Relevant source:

- `codex-rs/thread-store/src/thread_history.rs`;
- `codex-rs/thread-store/src/thread_history/materialize.rs`;
- adjacent projection tests.

The projection has two coupled coordinates:

- durable byte offset;
- logical rollout ordinal.

Advancing the byte checkpoint past a rejected line without resolving whether that line consumed an ordinal can make later valid history unreachable. The repair introduces an explicit `RolloutProjectionStep` with either a projected line or a skipped ordinal range, and applies rows plus both checkpoints in one database transaction.

General rule:

```text
one logical durable prefix
= every coordinate describing that prefix
```

If progress is described by `(byte_offset, ordinal)`, `(epoch, sequence)`, `(source_head, reviewed_head)`, or `(generation, publication winner)`, updating only one coordinate produces a state that is individually well-typed but collectively false.

For receipt replay, checkpoint installation must therefore validate and install epoch, next sequence, coverage, operation state, and durable history boundary as one transition. For coordination, a projection must bind finding, spec, observed facts, and source/review generations rather than only one token.

## 4. Preserve uncertainty until later evidence resolves it

The same thread-history repair does not immediately classify every malformed line as consuming or not consuming an ordinal. It retains rejected or unknown lines until a later valid ordinal distinguishes a same-ordinal retry from a consumed range. Unexplained gaps remain errors.

General rule:

```text
unknown now
!= absent
!= failed
!= safe to skip
```

A later event may disambiguate an earlier acknowledgement loss, malformed record, cancellation request, or stale candidate. Good lifecycle logic retains that uncertainty explicitly instead of collapsing it into success or failure for control-flow convenience.

This supports the current receipt vocabulary's `Ambiguous` states, but only after wire records are validated by a replay/domain owner. A permissive Serde DTO should preserve the observation; it should not directly grant compaction or retry authority.

## 5. Parse fallback data only when it becomes necessary

The thread-history change prefers an item's event timestamp and parses the rollout timestamp only when the item needs it as a fallback. An invalid fallback timestamp therefore does not reject an item that already has authoritative event time.

General rule:

```text
validate required authority eagerly
validate optional fallback when selected
```

This avoids two opposite defects:

- accepting an invalid value that becomes authoritative later;
- rejecting valid work because an unused fallback is malformed.

The same distinction should guide MCP live fallback, cached definitions, compatibility fields, and older-peer defaults.

## 6. Producer-owned terminal state should be bounded and transferred

Owned Codex source PR #93 at `7f15307fd2c157d8a139310d2e8243f3f2b391a4` records terminal output into a producer-owned `HeadTailBuffer` before best-effort broadcast.

The current design uses capped buffers and drains the authoritative completion buffer into the observer transcript at close. It does not retain an unbounded `Vec<u8>` or clone an unlimited transcript.

General rule:

```text
producer state -> authoritative bounded completion
broadcast -> notification/projection
close -> explicit ownership transfer or reconciliation
```

Carrier #94 failed at formatting before target controls, so the source remains prepared rather than current-head executed.

## 7. Behavioral metadata must survive transparent wrappers

Owned Codex source PR #99 at `860f6babd420587dccc9e0d414f18ed157690958` adds a conservative `ToolExecutor::operation_effect()` contract. Unclassified executors default to `PotentialMutation`.

Current source inspection found that `ExposureOverride` forwards `kind()` and `execute()` but not `operation_effect()`. An explicit read-only executor therefore becomes potentially mutating after wrapping.

That failure is conservative, not unsafe, but it proves a broader Rust rule:

```text
transparent wrapper
=> forward every behaviorally relevant capability
```

A wrapper that changes authority may deliberately reclassify. A wrapper that only changes exposure should preserve effect identity. Focused tests must exercise the wrapped object graph, not only the base trait implementation.

## 8. Async side effects need cancellation ownership

Owned reconnect source PR #101 at `df954cf690e360771b3a2753eaee8a508da21d6c` establishes bounded exactly-one reconnect and malformed-config failure atomicity for ordinary completion.

Its production method arms `reconnect_on_next_refresh()` before awaiting the refresh. If that future is cancelled after the arm but before consumption, a later unrelated refresh may inherit the request.

The accepted bounded claim does not include this interval. The next lifecycle control should prove either:

- the operation is owned to completion once armed; or
- an RAII/transactional guard commits or clears the arm on every exit path.

General rule:

```text
shared side effect before .await
=> explicit cancellation semantics
```

## Review standard distilled

A strong Rust/lifecycle proposal should answer all of the following:

1. Which type owns the authoritative fact?
2. Is the value raw wire data, validated domain state, or a projection?
3. Which fields determine semantic identity, and which are transport or presentation only?
4. Which coordinates must advance atomically?
5. How are unknown, absent, failed, stale, and ambiguous represented distinctly?
6. Can a transparent wrapper drop or change behavioral metadata?
7. What happens if an async future is cancelled between preparation and commit?
8. Is retained state byte-, count-, time-, and lifecycle-bounded where required?
9. Does a green test exercise the actual selected object graph and forbidden side effects?
10. Can stale or caller-supplied data overwrite producer- or persistence-owned truth?

## Exact next discriminators

- Receipt wire: execute the formatted exact source, but keep compaction authority outside the permissive wire DTO until replay validation produces domain state.
- Tool effect: format and execute the trait controls, then add wrapper-preservation coverage before dispatch integration.
- MCP authority: replace generic serialized equality with a named authority key and prove mismatch causes zero pre-dispatch side effects.
- Reconnect: retain the accepted 250 ms bounded claim and add cancellation-after-arm coverage separately.
- Terminal: produce a formatting-clean current-public-head source and rerun the nine exact controls.
- Replay: prefer direct typed source over repeated textual generator repair; install checkpoint plus tail only after complete validation.

## Boundary

This note is source analysis and owned-proposal review synthesis. It changes no Codex product source, grants no merge or public-upstream authority, and does not upgrade any proposal's evidence class.