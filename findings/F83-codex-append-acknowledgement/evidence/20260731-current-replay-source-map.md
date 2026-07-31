# Codex mutation receipt replay — current source map and bounded next slice

## In simple words

Current Codex already reconstructs conversation history, world-state baselines, turn settings, compaction windows, and rollback boundaries from rollout records. Mutation receipts should join that reconstruction path.

The historical receipt replay generator points at the correct general owners, but it is too weak to publish as source. It forces a full rollout scan whenever any receipt exists, carries no compacted receipt checkpoint into the reconstruction base, has incomplete bounds and recovery rules, and tests only a small fraction of the required failure cases.

The next source branch should be rebuilt directly on current source after the canonical live receipt owner is current-pin source. It should preserve the existing reverse-segment reconstruction algorithm, add a bounded receipt checkpoint base plus post-checkpoint tail, validate into temporary state, and install the ledger only after complete replay success.

## Exact source boundary

- Public repository: `openai/codex`, read-only.
- Inspected head: `4642370542739d5dd080b0c87a9de06a6435d3db`.
- Retrieval date: `2026-07-31`.
- Current receipt wire source: `teamleaderleo/codex#95@15414d7e5da8109e03dca24111664b272e4a5717`.
- Historical replay carrier: `teamleaderleo/codex#78@e2d796a17fd6aa0b1053ca80c6daa36f8e03de2f`.
- Historical replay run: `30584251271`, failed during source generation before formatting or Rust tests.
- Public upstream contact authorized: `false`.

## Current reconstruction owner

Current history reconstruction lives in:

```text
codex-rs/core/src/session/rollout_reconstruction.rs
codex-rs/core/src/session/rollout_reconstruction_tests.rs
```

`Session::reconstruct_history_from_rollout` currently:

1. scans rollout items newest to oldest;
2. groups records into active turn segments;
3. applies rollback as “skip the newest N finalized user-turn segments”;
4. selects the newest surviving compaction replacement history;
5. stops scanning older records after replacement history and required resume metadata are known;
6. replays the surviving history tail forward;
7. rebuilds world-state baselines in chronological order;
8. returns history, previous turn settings, reference context, world state, and context-window lineage.

The algorithm already provides the key concept needed by receipt replay: rollback-aware segment survival plus a checkpoint base and chronological tail.

## Current installation owner

`Session::record_initial_history` in:

```text
codex-rs/core/src/session/mod.rs
```

selects new, resumed, and forked history behavior, calls rollout reconstruction for resumed and forked history, and applies the reconstructed values to session state.

Receipt replay should return one validated ledger with the reconstruction result. The session should install it in the same locked state update that installs replacement history and resume metadata.

A partial receipt replay must never mutate the live owner before the complete selected receipt segment validates.

## Current rollout vocabulary owner

`RolloutItem` lives in:

```text
codex-rs/protocol/src/protocol.rs
```

The current variant family includes session metadata, response items, inter-agent communication, turn context, compaction, world state, and events. A receipt rollout envelope therefore expands a widely matched enum.

Adding:

```text
RolloutItem::ToolOperationReceipt(...)
```

requires deliberate treatment in every exhaustive consumer. Workspace compilation is necessary, while compilation alone cannot prove correct consumer semantics.

Consumers fall into four categories:

1. **must consume** — session reconstruction and receipt diagnostics;
2. **must preserve** — rollout read/write, fork filtering, copied history, retained history;
3. **must carry or summarize** — compaction and checkpoint creation;
4. **must ignore deliberately** — model history projection, user-visible event projection, world-state reconstruction.

Every ignored match arm should remain explicit so later protocol additions cannot silently disappear.

## Current compaction base

`CompactedItem` and its construction paths carry replacement history and context-window lineage. Receipt replay needs one bounded checkpoint base associated with the same compaction epoch.

The current wire source defines:

```text
ToolOperationReceiptCheckpoint
```

with:

- version;
- epoch ID;
- next sequence;
- coverage loss;
- bounded receipt entries.

The historical replay generator adds activation and update rollout records but never installs a checkpoint into compaction. That omission forces reconstruction to scan every receipt-bearing rollout back to epoch activation.

The preferred replay input is:

```text
newest supported surviving receipt checkpoint
+ ordered receipt updates after its next_sequence
```

Receipt checkpoint carriage and ordinary receipt updates may land in separate source slices. Replay acceptance requires both before long-session promotion.

## Rollback behavior

Current reverse reconstruction treats rollback as skipping finalized user-turn segments. Receipt updates attached to a skipped segment should also disappear when they prove pre-dispatch or branch-local state.

Receipt replay needs an additional removed-tail scan for operations whose external effect may survive the rollback:

- terminal external effects become retained historical receipt knowledge;
- certain pre-dispatch failures may leave with the skipped segment;
- possible dispatch becomes an ambiguity tombstone.

This cannot be implemented by dropping every receipt record in a rolled-back turn.

## Fork behavior

Forked initial history flows through the same reconstruction owner, which makes it the correct place to restore receipt knowledge. Dispatch ownership still requires branch classification.

A reconstructed receipt should carry one of:

```text
current_thread
parent_owned
inherited_terminal
inherited_ambiguous
```

The child session can install inherited terminal and ambiguity knowledge. Parent-active receipts remain blocked from child dispatch until explicit reconciliation or transfer authority exists.

## Historical generator map

The historical generator targeted these source areas:

```text
codex-rs/protocol/src/tool_operation.rs
codex-rs/protocol/src/protocol.rs
codex-rs/core/src/state/tool_operation_receipts.rs
codex-rs/core/src/state/mod.rs
codex-rs/core/src/state/session.rs
codex-rs/core/src/session/rollout_reconstruction.rs
codex-rs/core/src/session/mod.rs
codex-rs/core/src/session/rollout_reconstruction_tests.rs
```

That general map remains useful. The generated implementation and workflow remain execution machinery rather than source authority.

## Defects in the historical replay candidate

### 1. Source generation failed before execution

Run `30584251271` stopped on a stale `world state receipt unreachable` anchor. Formatting, focused tests, workspace compilation, source-fence verification, and publication never ran.

Evidence class: generator failure only.

### 2. Global full-history scan

The generator computes whether any receipt record exists anywhere in the rollout. When one exists, it disables the normal early-stop condition after replacement history and resume metadata are known.

That turns every receipt-enabled long session into a full reverse scan, including histories with many compaction snapshots and large inherited segments.

Correct behavior uses a receipt checkpoint base and post-checkpoint tail.

### 3. Checkpoint type remains unused

The wire source defines a bounded checkpoint, while the replay generator folds only activation and update records. Compaction never emits or restores the checkpoint.

This leaves the claimed compaction/resume contract incomplete.

### 4. Invalid state can be reset too loosely

A later activation resets the generator ledger’s invalid and coverage-loss fields. A new epoch should clear prior invalid state only after an authoritative activation/checkpoint transition proves that the previous uncertainty is outside the new epoch’s safety boundary.

An arbitrary later activation record cannot erase a missing, conflicting, or unsupported mutation receipt.

### 5. Bounds cover entry count only

The generator caps retained operation identities at 1,024. It lacks explicit limits for:

- receipt update count;
- encoded or decoded bytes;
- epoch count;
- duplicate count;
- checkpoint entry count at deserialization;
- string identity lengths;
- rollback-tail tombstones.

Protocol and replay owners need bounded inputs before allocating or cloning unrestricted receipt vectors and strings.

### 6. Replay failure has weak diagnostics

The generated ledger records broad `invalid` and `coverage_lost` booleans. It does not retain the first failing sequence, expected sequence, version, epoch, operation identity digest, or failure class.

A privacy-safe typed replay error should support tests and operator diagnosis without recording tool arguments or results.

### 7. Two replay controls leave major gaps

The historical workflow declares two rollback-aware replay controls. Missing discriminators include:

- conflicting duplicate sequence;
- sequence gap;
- sequence regression;
- unknown version;
- unsupported checkpoint version;
- checkpoint plus tail;
- duplicate activation;
- activation after invalid tail;
- capacity loss;
- bounded input overflow;
- rollback ambiguity tombstone;
- parent-owned fork receipt;
- process restart;
- current live owner reconciliation.

### 8. Substring test filters

The historical workflow uses substring filters for several groups. A green run could execute zero, one, or several tests without proving the intended exact set.

Current carriers should enumerate test inventory, require one full-name match per declared control, and execute using `--exact`.

### 9. Generated publication obscures source review

The workflow generates a multi-file patch and publishes a source branch only after execution. This can work for bounded mechanical restacks, while the replay change has enough semantic ownership that direct source authoring and complete-diff review are preferable.

## Required replay model

### Validation result

Replay should return:

```text
Valid(ledger)
Invalid(replay_error)
CoverageLost(coverage_error)
Unsupported(version_error)
```

The session installs one explicit fail-closed state for every non-valid result. It should never substitute an empty healthy ledger.

### Typed replay errors

Candidate privacy-safe errors:

```text
update_before_activation
unsupported_version
empty_epoch
wrong_epoch
sequence_gap
sequence_regression
conflicting_duplicate
invalid_operation_identity
checkpoint_overflow
update_overflow
identity_length_overflow
coverage_lost
rollback_ownership_conflict
checkpoint_tail_conflict
```

Each error can carry bounded sequence and epoch digests where useful.

### Temporary ledger

Replay builds a temporary ledger from checkpoint and tail. It checks every bound and sequence rule before session installation.

### Current live owner

The durable ledger and live operation owner must converge into one canonical session-owned state. A replay-only map beside a live-only map would create competing authorities.

The current-public replay branch should therefore wait until the canonical live owner and direct-result persistence are current-pin source, or it should explicitly port that owner in the same reviewed stack.

## Recommended source sequence

### Slice A — current-pin wire

Owner: Codex #95/#96.

State: source exists; execution queued at this record.

### Slice B — current-pin canonical live owner

Port the accepted session-scoped owner, selected-runtime begin, terminal transitions, direct-result persistence, conservative duplicate handling, and coverage loss directly onto current public source.

Resolve the current `registry_tests.rs` conflict semantically. Preserve current direct/plaintext tool behavior and reintroduce only the exact receipt controls.

### Slice C — rollout envelope

Add the protocol-owned activation/update envelope and the `RolloutItem` variant. Compile every target and classify each consumer as consume, preserve, carry, or deliberately ignore.

### Slice D — bounded checkpoint and replay

Add checkpoint carriage, validate-then-install replay, typed errors, rollback-aware tombstones, and branch ownership.

Keep this slice separate from compaction blocking behavior.

### Slice E — checkpoint emission

Emit the bounded receipt checkpoint at compaction persistence, with expected history and receipt epochs.

### Slice F — compaction enforcement

Enable shared preflight at all six local/remote request and installation boundaries after durable restoration and safe retirement work.

## Candidate source fence for the replay slice

The exact fence should remain small enough for complete-diff review. The likely minimum is:

```text
codex-rs/protocol/src/tool_operation.rs
codex-rs/protocol/src/protocol.rs
codex-rs/core/src/state/tool_operation_receipts.rs
codex-rs/core/src/state/mod.rs
codex-rs/core/src/state/session.rs
codex-rs/core/src/session/rollout_reconstruction.rs
codex-rs/core/src/session/mod.rs
codex-rs/core/src/session/rollout_reconstruction_tests.rs
```

Checkpoint emission adds compaction owners and should remain a successor fence.

The exact current source map must be refreshed after the live-owner restack because current state files and lifecycle call sites may move.

## Required exact controls

### Ledger unit controls

1. activation installs an empty epoch;
2. update before activation fails closed;
3. identical immediate duplicate is idempotent;
4. conflicting duplicate fails closed;
5. sequence gap fails closed;
6. sequence regression fails closed;
7. wrong epoch fails closed;
8. unsupported version remains explicit;
9. invalid identity fails closed;
10. retained-entry overflow sets coverage loss;
11. update-count overflow fails closed;
12. identity-length overflow fails closed.

### Reconstruction controls

1. direct identity restores;
2. Code Mode identity restores;
3. newest supported checkpoint becomes the base;
4. post-checkpoint updates replay in order;
5. older checkpoint and tail stay outside the active ledger;
6. rolled-back certain pre-dispatch update disappears;
7. rolled-back possible dispatch becomes a tombstone;
8. rollback metadata and history remain synchronized;
9. parent-active receipt becomes parent-owned in child;
10. inherited terminal receipt remains terminal;
11. invalid tail installs fail-closed state;
12. unknown version never becomes an empty ledger.

### Compatibility gates

- exact focused names with `--exact`;
- complete `codex-protocol` package;
- focused `codex-core` reconstruction module;
- full workspace compile after `RolloutItem` expansion;
- existing rollback, compaction, world-state, resume, and fork tests;
- exact changed-file fence;
- independent complete-diff review.

## Current disposition

Disposition: `REPAIR historical generator; retain source map; hold replay implementation until current-pin live owner exists`.

The next implementation action is the current-source live-owner restack, not another replay generator rerun.

## Boundary

- Source reading and owned-fork work only.
- Synthetic fixtures only.
- Public `openai/codex` remains read-only.
- No credentials, production mutations, merge, deployment, or public upstream interaction.
