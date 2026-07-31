# Current-main tool receipt review

Date: 2026-07-31  
Canonical campaign: Fieldwork #83  
Reviewed Codex head: `f7265553ea1510304f3091833dcbce65ef21f10c`  
Public upstream interaction: none

## Why the review target changed

The earlier current-pin stack was based on `4642370542739d5dd080b0c87a9de06a6435d3db`. The fork's `main` has since advanced through a separate receipt implementation and now contains overlapping work in `codex-tools`, the core session ledger, direct-result persistence, lifecycle terminal updates, selected-runtime dispatch capture, exposure-wrapper delegation, and raw compaction identity research.

The old and new histories diverge. Carrying the older live-ledger publisher onto the fork without review would duplicate receipt ownership and conceal conflicts.

## Accepted prerequisite

Codex #106 at `b76d46832f8426cb8acb4031b00f41069c7d7014` received an independent `ACCEPT` review for trait-level runtime effect vocabulary. The review correctly required transparent runtime adapters to preserve `operation_effect()` before selected-runtime claims.

Current `main` already contains that wrapper repair in `ExposureOverride::operation_effect()` and begins receipts from the selected runtime after registry lookup. Unsupported calls remain conservative and certain pre-dispatch failures receive terminal failure.

## Current-main implementation

Current `main` owns:

- receipt DTO and effect/terminal/result enums in `codex-rs/tools/src/tool_operation.rs`;
- session-scoped live receipts in `codex-rs/core/src/state/tool_operation_receipts.rs`;
- session transition methods in `codex-rs/core/src/session/tool_operation.rs`;
- selected-runtime begin and terminal closure in `codex-rs/core/src/tools/registry.rs` and lifecycle;
- authoritative direct-result append observation in `session/mod.rs` and `session/turn.rs`;
- raw call/output identity validation in `context_manager/compaction_identity.rs`.

## Blocker 1: compaction gates are disconnected

`validate_compaction_call_output_identity()` is defined and exported, but it has no caller in current `session/mod.rs`, `compact.rs`, or `compact_remote.rs`.

`Session::has_unreconciled_potential_mutation()` is also absent from those compaction paths.

Both local and remote compaction can therefore install replacement history without consulting either raw call/output identity or live mutation certainty. The focused workflow only runs `cargo test -p codex-core compaction_identity --locked`; it proves the helper in isolation and supplies no compaction-entry integration evidence.

Disposition: `REPAIR before compaction authority`.

## Blocker 2: wire DTO answers a domain decision

`codex_tools::ToolOperationReceipt` is public, serializable, and contains a public mutable `version` field. `is_compaction_ready()` ignores version support and treats every deserialized field combination as validated local state.

The live ledger calls this DTO predicate directly. A future-version or inconsistent receipt can therefore influence a compaction decision once durable decoding is introduced, and current local ownership has no separate validated-state boundary.

Disposition: remove decision authority from the DTO; keep the predicate private to validated core state.

## Blocker 3: identity is host-call-only

The live ledger is `HashMap<String, ToolOperationReceipt>` keyed by `invocation.call_id`.

`ToolCallSource::CodeMode` already carries `(cell_id, runtime_tool_call_id)`, yet begin, terminal, lookup, and lifecycle updates discard that source identity. Nested Code Mode operations therefore lack a stable source-qualified key and can collide with or be collapsed into a synthetic host call identity.

Direct-result persistence extracts model-visible output call IDs and records them by string. No nested Code Mode result-persistence path exists in the reviewed head.

Disposition: introduce one `ToolOperationId` used from begin through terminal, persistence, replay, and checkpoint ownership.

## Blocker 4: bounds cover count only

The session ledger caps retained receipt count at 1,024 and fails closed on overflow. Identity strings remain unbounded. Durable replay and nested Code Mode identity need component limits before accepting externally reconstructed state.

## Missing durable stages

Current `main` has no versioned activation/update/checkpoint envelope for receipts, no ordered replay owner, no checkpoint installation, no resume/fork restoration, and no retirement proof.

## Repair sequence

1. **Compaction enforcement:** privately validate local receipt readiness and call both raw identity and live mutation gates at every local and remote compaction entry before replacement history can be installed.
2. **Source-qualified identity:** replace string keys with Direct or Code Mode operation identity and preserve it across lifecycle and result persistence.
3. **Durable replay:** add bounded versioned activation, ordered updates, checkpoints, validation, resume/fork restoration, and fail-closed coverage loss.
4. **Append ambiguity:** retain the append-acknowledgement prerequisite so commit-then-error remains distinguishable from pre-write failure.

The cancelled old repair publisher #109 is evidence-free until a runner executes it and is no longer the preferred product path because its source ownership conflicts with current `main`.

No merge, deployment, credentials, production mutation, or public upstream interaction occurred.