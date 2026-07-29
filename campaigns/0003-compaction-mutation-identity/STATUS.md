# Compaction Mutation Identity

## In simple words

Campaign #83 has moved from source mapping into staged owned-fork implementation. The first three non-behavioral foundations are merged: tools have a conservative operation-effect contract, raw history has a privacy-safe call/result identity validator, and runtime wrappers preserve an explicit effect. A fourth slice is validating a bounded session owner for direct-call receipts.

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

`teamleaderleo/codex#13` is the clean restack of direct-call receipt ownership. The candidate:

- captures the selected runtime effect at direct dispatch;
- records terminal outcome through the shared lifecycle path;
- marks result persistence only after authoritative rollout append succeeds;
- marks failed persistence ambiguous;
- retains receipts across the originating turn in session state;
- caps retained receipts at 1,024;
- sets explicit `coverage_lost` on overflow and does not evict potentially mutating evidence.

Nested code-mode calls, resume restoration, compacted-checkpoint carry-forward, and compaction enforcement remain outside this slice.

## Enforcement map

The next source slice must use one shared preflight contract at two boundaries in every implementation:

1. **Before request construction**
   - local compaction: before cloned history is converted with `for_prompt`;
   - remote v1: before the compact endpoint attempt builds its request history;
   - remote v2: before its prompt/retained-message input is built.
2. **Before replacement installation**
   - immediately before `Session::replace_compacted_history` in local, remote v1, and remote v2.

The preflight must reject when:

- raw history has any call/result identity defect;
- direct receipt coverage is incomplete;
- a potentially mutating receipt lacks one unambiguous terminal outcome and one persisted result;
- a duplicate, conflicting, late, or reordered observation remains unreconciled.

The second check matters because tool futures or persistence state can change while a compaction request is in flight.

## Durable checkpoint boundary

Live session receipts alone are insufficient. Resume and fork reconstruction begins from the newest compacted checkpoint plus its surviving suffix. The implementation therefore needs both:

- live receipt items or an equivalent durable operation ledger before compaction; and
- the minimal unresolved/reconciled receipt set carried in the compacted checkpoint.

Do not put receipts only in replacement history and do not put them only in an in-memory map.

## Remaining work

1. Finish and merge the bounded direct-call owner.
2. Define the versioned rollout/checkpoint representation and resume restoration.
3. Add the shared preflight and wire all six request/install boundaries.
4. Add late-result reconciliation plus duplicate and causal-order rejection.
5. Prove complete identities continue normally and every ambiguous mutation fails closed without automatic replay.

## Stop rule

Do not claim a repair until compiled owned-fork tests cover complete, missing, duplicate, reordered, late, persistence-failure, and receipt-overflow cases across local, remote v1, and remote v2 compaction. No upstream interaction is authorized.
