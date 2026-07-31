# Rust authority and replay patterns in current Codex

Date: 2026-07-31  
Fieldwork owner: F239 portfolio synthesis  
Base Fieldwork generation: `7c9a64b94dc50efe47816986b672323d1593f58c`  
Latest public Codex generation inspected: `5e8b22488f224a1c426f3bdcd41c8715894ef3b4`  
Public-head observation boundary: 2026-07-31T11:01:47Z  
Public upstream interaction: none

## Purpose

This note records current public Codex implementation patterns that sharpen the review standard for the active terminal, MCP, receipt, replay, and coordination proposals. It is evidence and synthesis, not a new implementation owner, and it does not promote any owned candidate beyond its existing evidence class.

The recurring question is not whether a patch uses clever or idiomatic syntax. It is whether types, ownership boundaries, and transitions preserve the exact fact that a later decision depends on.

## 1. Persisted facts outrank caller-supplied assertions

Public Codex commit `f0c30e528a54bdf0fa9a4d52ff74b34383434811` derives report prompt metadata from the persisted rollout rather than accepting reserved client tags.

Relevant source:

- `codex-rs/app-server/src/request_processors/feedback_processor.rs`.

The implementation removes client-provided `prompt_hash` and `prompt_version` authority and restores `prompt_hash` only when it can derive the value from persisted `SessionMeta` base instructions. Missing or unmatched rollout evidence does not preserve the caller's assertion.

General rule:

```text
untrusted projection input
-> remove reserved authority fields
-> reconstruct from canonical persisted state
-> publish only derived facts
```

A UI, request, carrier, or dispatch packet may reference authoritative facts. It may not assert them into existence.

## 2. Normalize only fields proven non-semantic

Public Codex commit `745603a5a1eb48b6f343633d622eeb72dd549d7b` removes top-level `internal_chat_message_metadata_passthrough` before rollout-trace item reconciliation while retaining nested occurrences as model-visible content.

Relevant source:

- `codex-rs/rollout-trace/src/reducer/conversation/normalize.rs`;
- adjacent reducer controls.

The boundary is deliberately narrow:

- one top-level field is classified as transport metadata and excluded from semantic identity;
- nested occurrences remain semantic;
- conflicting call-ID reuse remains rejected.

General rule:

```text
semantic equality != whole serialized object equality
semantic equality != delete every field with a familiar name
semantic equality = typed or deliberately field-scoped canonicalization
```

For MCP callable authority, whole-`ToolInfo` JSON equality is too broad, while an unnamed ad hoc subset is too fragile. The durable form should be a named authority key whose routing, schema, capability, and execution fields are deliberately owned.

## 3. Coupled checkpoints advance together or not at all

Public Codex commit `6256a7ccc7948231befc33d7d61b369041e6eb16` repairs thread-history projection after malformed or rejected rollout lines.

Relevant source:

- `codex-rs/thread-store/src/thread_history.rs`;
- `codex-rs/thread-store/src/thread_history/materialize.rs`;
- adjacent projection controls.

The projection has two coupled coordinates:

- durable byte offset;
- logical rollout ordinal.

Advancing one without resolving the other can make later valid history unreachable. The repair represents projection steps explicitly and applies rows plus both checkpoints in one database transaction.

General rule:

```text
one logical durable prefix
= every coordinate describing that prefix
```

The same rule applies to `(epoch, sequence)`, `(source_head, reviewed_head)`, `(generation, publication_winner)`, and coordination projections that bind structured intent to live facts.

## 4. Preserve uncertainty until later evidence resolves it

The thread-history repair does not immediately classify every malformed line as consuming or not consuming an ordinal. It retains uncertainty until a later valid ordinal distinguishes a same-ordinal retry from a consumed range. Unexplained gaps remain errors.

General rule:

```text
unknown now
!= absent
!= failed
!= safe to skip
```

This supports explicit ambiguous receipt states, but only after a replay/domain owner validates wire records. A permissive Serde DTO may preserve an observation; it must not directly grant compaction or retry authority.

## 5. Validate optional fallback data when it becomes authoritative

The thread-history change prefers an item's event timestamp and parses a rollout timestamp only when the item needs it as a fallback. An invalid unused fallback does not reject an item that already has authoritative event time.

General rule:

```text
validate required authority eagerly
validate optional fallback when selected
```

This avoids both accepting an invalid value that later becomes authoritative and rejecting valid work because unused fallback data is malformed.

## 6. Credential authority follows execution-environment ownership

Public Codex commit `bf4d3f51ea70ce70ab7fabce7a66f328fef49e57` prevents executor-owned MCP servers from inheriting host-owned ChatGPT actor credentials or host OAuth state.

Relevant source areas:

- MCP connection startup and authentication;
- effective server ownership/environment checks;
- connection identity and authentication-status controls.

The accepted boundary is fail closed:

- host ChatGPT authentication is available only to local, host-owned MCP servers;
- executor-owned servers do not receive hosted actor credentials;
- executor-owned servers do not consult the host OAuth store;
- environment-backed `Authorization` is rejected for this path so host secrets are not resolved into an executor-owned connection;
- a non-local server using `auth = "chatgpt"` requires an acceptable explicit static authorization value;
- unsupported authentication fails before connection.

General rule:

```text
credential source authority
follows execution-environment ownership
not product-name resemblance or routing convenience
```

This is precedent and review criteria for the owned MCP proposals. It is not evidence that the current captured-call or reconnect candidates already enforce the credential boundary. Their future controls must prove the negative side effects directly: no hosted credential forwarding, no host OAuth lookup, no environment-secret resolution, and no connection before acceptable executor-owned credentials exist.

## 7. Catalogue authority and executable-content authority may have different owners

Public Codex commit `5e8b22488f224a1c426f3bdcd41c8715894ef3b4` loads and caches the host skill provider catalogue during world-state contribution, then reuses that catalogue for model-visible listings and shadow selection.

The same change deliberately preserves Core-owned full prompt injection for a selected host skill. A provider entry can determine discovery metadata while Core's snapshot remains authoritative for the selected skill's full executable instructions.

General rule:

```text
discovery catalogue authority
may differ from
selected executable-content authority
```

A single feature name does not imply a single source of truth for every field. The owner of names and descriptions may differ from the owner of full prompt contents, credentials, runtime clients, or durable results. Tests must prove both the positive source and the forbidden substitute source.

This sharpens MCP and tool exposure review: advertised catalogue state, callable authority, selected runtime identity, and execution payload must be named separately rather than folded into one generic freshness object.

## 8. Producer-owned terminal state should be bounded and transferred

Owned Codex source PR #93 at `7f15307fd2c157d8a139310d2e8243f3f2b391a4` records terminal output into a producer-owned `HeadTailBuffer` before best-effort broadcast.

The design uses capped buffers and drains the authoritative completion buffer into observer state at close. It does not retain an unbounded transcript or clone unlimited output.

General rule:

```text
producer state -> authoritative bounded completion
broadcast -> notification or projection
close -> explicit ownership transfer or reconciliation
```

Carrier #94 failed formatting before target controls. The source remains prepared rather than current-head executed.

## 9. Behavioral metadata must survive transparent wrappers

Owned Codex source PR #106 at `b76d46832f8426cb8acb4031b00f41069c7d7014` adds a conservative `ToolExecutor::operation_effect()` contract. Unknown executors default to `PotentialMutation`, and the exact trait-level source passed its focused controls and complete `codex-tools` package through carrier #107 run `30623517422`.

Current Core inspection found that `ExposureOverride` forwards execution, exposure, readiness, cancellation, hooks, telemetry, and diff behavior but does not forward `operation_effect()`. A wrapped explicitly read-only executor therefore falls back to potential mutation.

That fallback is conservative, not unsafe, but it proves a broader rule:

```text
transparent wrapper
=> forward every behaviorally relevant capability
```

A wrapper that intentionally changes authority should reclassify explicitly. A wrapper that only changes exposure should preserve effect identity. Controls must exercise the selected object graph, not only the base trait implementation.

## 10. Async side effects need cancellation ownership

Owned reconnect source PR #101 at `df954cf690e360771b3a2753eaee8a508da21d6c` establishes bounded exactly-one reconnect and malformed-config failure atomicity for ordinary completion.

Its production method arms `reconnect_on_next_refresh()` before awaiting the refresh. Cancellation or future drop after the arm but before consumption can leave a latent reconnect request for a later unrelated refresh.

General rule:

```text
shared side effect before .await
=> explicit cancellation semantics
```

The next lifecycle control should prove either that the operation is owned to completion once armed or that an RAII/transactional guard commits or clears the arm on every exit path. Successful reload also needs a post-publication tool call to prove the replacement runtime is usable, not merely initialized.

## 11. Time-dependent decisions need a validity horizon

The observed-generation coordination experiment correctly binds structured records, live facts, and carrier observations to exact digests and generation labels. A separate review found that exact input identity alone is insufficient for time-dependent authority.

An authorization can be current at observation time and expire later without any record bytes changing. A historically exact projection must therefore not grant present authority indefinitely.

General rule:

```text
exact historical inputs
!= current decision authority
```

Time-sensitive projections should carry an observation boundary and the next derived invalidation horizon, or expose separate `inputs_current` and `decision_current` results.

## Review standard distilled

A strong Rust/lifecycle proposal should answer all of the following:

1. Which type owns the authoritative fact?
2. Is the value raw wire data, validated domain state, or a projection?
3. Which fields determine semantic identity, and which are transport or presentation only?
4. Which coordinates must advance atomically?
5. How are unknown, absent, failed, stale, and ambiguous represented distinctly?
6. Does credential authority match execution-environment ownership?
7. Are catalogue metadata and selected executable contents owned separately where required?
8. Can a transparent wrapper drop or change behavioral metadata?
9. What happens if an async future is cancelled between preparation and commit?
10. Is retained state bounded by bytes, count, time, and lifecycle where required?
11. Does a green test exercise the actual selected object graph and forbidden side effects?
12. Can stale, caller-supplied, or merely similar data overwrite producer- or persistence-owned truth?
13. Can wall-clock movement invalidate a decision even when every content generation is unchanged?

## Exact next discriminators

- Receipt wire: complete the one-file repair that removes compaction decisions from the permissive DTO; replay must validate version, identity, epoch, ordering, coverage, and legal state before producing domain authority.
- Tool effect: preserve the executed trait source, then add wrapper-forwarding coverage before dispatch integration.
- MCP authority: use a named callable-authority key and prove mismatch causes zero approval, hook, rewrite, credential, and dispatch side effects.
- MCP credentials: prove executor-owned paths never consult or receive host-owned actor/OAuth/environment credentials.
- Reconnect: retain the bounded exact-one claim; separately test cancellation after arm and successful post-reload tool use.
- Terminal: publish a formatting-clean current-public-head source and rerun the nine exact controls.
- Cancellation: distinguish cancellation requested, cleanup settled, and cleanup unconfirmed after a bounded deadline; do not manufacture ordinary abort certainty.
- Replay: prefer typed direct source over repeated textual generator repair and install checkpoint plus tail only after complete validation.
- Coordination: separate exact input currentness from time-dependent decision currentness.

## Boundary

This note is source analysis and owned-proposal review synthesis. It changes no Codex product source, grants no merge or public-upstream authority, and does not upgrade any proposal's evidence class.
