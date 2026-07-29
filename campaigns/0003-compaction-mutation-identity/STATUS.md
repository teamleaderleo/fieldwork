# Compaction Mutation Identity

## In simple words

Campaign #83 has moved from source mapping into staged owned-fork implementation. The first three non-behavioral foundations are merged: tools have a conservative operation-effect contract, raw history has a privacy-safe call/result identity validator, and runtime wrappers preserve an explicit effect. A fourth slice is validating a turn-scoped live owner before any dispatch or compaction behavior changes.

- Campaign issue: #83
- Programme: #14
- Parent campaign: #31
- Target hub: #8
- State: `implementing`
- Worker: GPT-5.6 Thinking
- Fieldwork branch: `campaign/83-implementation-checkpoint`
- Owned Codex base after accepted slices: `teamleaderleo/codex@e6b3017f4c725e0e6c48fc4e7fa703e365b2be67`
- Public source pin: [Codex revision `3725f02cf38d856bc82bb46dd68ab61bb96ec6fc`](https://redirect.github.com/openai/codex/commit/3725f02cf38d856bc82bb46dd68ab61bb96ec6fc)
- Upstream contact: unauthorized

## Merged owned-fork foundations

1. `teamleaderleo/codex#3` — shared `ToolOperationEffect` and versioned terminal/result receipt contract; focused `codex-tools` suite passed; merged as `f84e8d6fb48917965b7dacc1b28147663a28dd84`.
2. `teamleaderleo/codex#2` — raw-history validator for missing, duplicate, reordered, orphaned, and unpairable client call/result identity; focused `codex-core` suite passed; merged as `f68ad3830bf582ebd78f046f039be08510f48a9f`.
3. `teamleaderleo/codex#12` — `ExposureOverride` preserves the wrapped runtime's operation effect; focused regression passed; merged as `e6b3017f4c725e0e6c48fc4e7fa703e365b2be67`.

These slices change no compaction or automatic-retry behavior.

## Active owned-fork slice

`teamleaderleo/codex#9` adds a turn-scoped receipt owner without wiring it to production dispatch. The candidate:

- keys live receipts by the existing call identity;
- conservatively creates a potentially mutating receipt for terminal or persistence observations that arrive before `begin`;
- escalates repeated call identity to potentially mutating and ambiguous instead of replacing prior state;
- reuses the shared ambiguity-preserving terminal/result state machine;
- exposes whether the turn contains an unreconciled potentially mutating operation;
- has focused tests for transition order, duplicate persistence, conflicting terminal outcomes, repeated begin, effect escalation, and late observations.

Turn scope is deliberate. Cross-turn retention, result-source ownership, rollout restoration, compacted-checkpoint carry-forward, and compaction enforcement remain later stages.

## Next wiring stage

After the live owner merges, wire it at three exact seams:

1. begin only after the model call item is durable;
2. record terminal state after direct, code-mode, failed, blocked, or cancelled dispatch;
3. record result persistence after direct history insertion or nested code-mode delivery reaches its authoritative owner.

Do not infer persistence merely because a handler returned a value.

## Enforcement map

The later compaction slice must use one shared preflight contract at two boundaries in every implementation:

1. **Before request construction**
   - local compaction: before cloned history is converted with `for_prompt`;
   - remote v1: before the compact endpoint attempt builds its request history;
   - remote v2: before its prompt/retained-message input is built.
2. **Before replacement installation**
   - immediately before `Session::replace_compacted_history` in local, remote v1, and remote v2.

The preflight must reject when:

- raw history has any call/result identity defect;
- the live owner reports an unreconciled potentially mutating operation;
- durable receipt coverage is incomplete after the persistence stage exists;
- a duplicate, conflicting, late, or reordered observation remains unreconciled.

The second check matters because tool futures or persistence state can change while a compaction request is in flight.

## Durable checkpoint boundary

A turn-scoped owner is necessary but insufficient. Resume and fork reconstruction begins from the newest compacted checkpoint plus its surviving suffix. The implementation therefore needs both:

- versioned durable operation receipt items before compaction; and
- the minimal unresolved/reconciled receipt set carried in the compacted checkpoint.

Do not put receipts only in replacement history and do not put them only in an in-memory map.

## Remaining work

1. Finish and merge the turn-scoped live owner.
2. Wire begin, terminal, and authoritative result-persistence transitions for direct and nested code-mode paths.
3. Define the versioned rollout/checkpoint representation and resume restoration.
4. Add the shared preflight and wire all six request/install boundaries.
5. Add late-result reconciliation plus duplicate and causal-order rejection.
6. Prove complete identities continue normally and every ambiguous mutation fails closed without automatic replay.

## Stop rule

Do not claim a repair until compiled owned-fork tests cover complete, missing, duplicate, reordered, late, and persistence-failure cases across local, remote v1, and remote v2 compaction. Any bounded durable owner must also prove explicit fail-closed behavior when coverage is lost. No upstream interaction is authorized.
