# Compaction Mutation Identity

## In simple words

Campaign #83 is in staged owned-fork implementation. Three behavior-neutral foundations are accepted. A turn-scoped receipt owner then merged while ownership review was unresolved; corrective Codex PR #17 removes it and installs one bounded session-state owner, the minimum live lifetime required for later manual compaction.

- Campaign issue: #83
- Programme: #14
- Parent campaign: #31
- Target hub: #8
- State: `implementing`
- Worker: GPT-5.6 Thinking
- Fieldwork dossier: merged PR #93
- Owned Codex base before correction: `teamleaderleo/codex@555332c9c4b92fe7426777297428a04dd11e605f`
- Corrective owned Codex PR: `teamleaderleo/codex#17`
- Public source pin: [Codex revision `3725f02cf38d856bc82bb46dd68ab61bb96ec6fc`](https://redirect.github.com/openai/codex/commit/3725f02cf38d856bc82bb46dd68ab61bb96ec6fc)
- Upstream contact: unauthorized

## Accepted owned-fork foundations

| Slice | Owned PR | Merge commit | Validation | Behavior change |
| --- | --- | --- | --- | --- |
| operation effect and receipt contract | `teamleaderleo/codex#3` | `f84e8d6fb48917965b7dacc1b28147663a28dd84` | full `codex-tools` suite passed | none |
| raw call/result identity validator | `teamleaderleo/codex#2` | `f68ad3830bf582ebd78f046f039be08510f48a9f` | focused `codex-core compaction_identity` suite passed | none; validator has no production caller |
| exposure wrapper effect delegation | `teamleaderleo/codex#12` | `e6b3017f4c725e0e6c48fc4e7fa703e365b2be67` | focused regression passed: 1 test, 3111 skipped | none |

These slices change no dispatch, compaction, retry, or user-visible behavior.

## Ownership correction

Codex PR #9 merged a receipt map into `TurnState` as `555332c9c4b92fe7426777297428a04dd11e605f`. That map cannot remain the canonical owner:

- a later manual compact operation has a different active turn;
- ordinary turn completion discards prior turn state before compaction reads it;
- resume and fork require reconstruction beyond process-local turn lifetime;
- keeping turn and session maps would create competing synchronization owners.

Corrective Codex PR #17 removes the turn map, its tests, and its workflow, then replaces it with exactly one owner on `SessionState`.

## Corrective live-owner slice

Codex PR #17 contains no dispatch or compaction behavior. It provides:

- one session-scoped map keyed by existing call identity;
- conservative late observations defaulting to `PotentialMutation`;
- repeated identity escalation to potentially mutating with ambiguous terminal and result state;
- shared terminal, persisted-result, and ambiguous-result transitions;
- `has_unreconciled_potential_mutation()` for later preflight;
- a 1,024-receipt bound;
- permanent `coverage_lost` after overflow, with no silent eviction and fail-closed preflight semantics;
- focused ordering, ambiguity, read-only, persistence-failure, and overflow tests.

Session scope is still only the live owner. Durable rollout restoration and compacted-checkpoint carry-forward remain separate stages.

## Next wiring stage

After the canonical owner merges, wire it at three exact seams:

1. begin only after the model call item is durable;
2. record terminal state after direct, code-mode, failed, blocked, or cancelled dispatch;
3. record result persistence after direct history insertion or nested code-mode delivery reaches its authoritative owner.

Do not infer persistence merely because a handler returned a value.

## Enforcement map

The later compaction slice must use one shared preflight contract at two boundaries in every implementation:

1. **Before request construction**
   - local compaction: before cloned history is converted with `for_prompt`;
   - remote v1: before the compact endpoint attempt builds request history;
   - remote v2: before prompt or retained-message input is built.
2. **Before replacement installation**
   - immediately before `Session::replace_compacted_history` in local, remote v1, and remote v2.

The preflight must reject when:

- raw history has any call/result identity defect;
- the live owner reports an unreconciled potentially mutating operation;
- live or durable receipt coverage is incomplete;
- a duplicate, conflicting, late, or reordered observation remains unreconciled.

The second check matters because tool futures or persistence state can change while a compaction request is in flight.

## Durable checkpoint boundary

A session-scoped owner is necessary but insufficient. Resume and fork reconstruction begins from the newest compacted checkpoint plus its surviving suffix. The implementation therefore needs both:

- versioned durable operation receipt updates before compaction; and
- the minimal unresolved or reconciled receipt set carried in the compacted checkpoint.

Do not put receipts only in replacement history and do not leave them only in an in-memory map.

## Remaining work

1. Validate and merge corrective PR #17.
2. Wire begin, terminal, and authoritative result-persistence transitions for direct and nested code-mode paths.
3. Define the versioned rollout/checkpoint representation and resume restoration.
4. Add the shared preflight at all six request and installation boundaries.
5. Add late-result reconciliation plus duplicate and causal-order rejection.
6. Prove complete identities continue normally and every ambiguous mutation fails closed without automatic replay.

## Stop rule

Do not claim a repair until compiled owned-fork tests cover complete, missing, duplicate, reordered, orphan, late, persistence-failure, and coverage-loss cases across local, remote v1, and remote v2 compaction, continuation, resume, fork, and retry. No upstream interaction is authorized.
