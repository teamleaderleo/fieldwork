# Compaction Mutation Identity

## In simple words

Campaign #83 is in staged owned-fork implementation. The live receipt owner is now canonical and session-scoped: owned Codex PR #19 removed the prematurely merged turn map, installed one bounded owner on `SessionState`, and retargeted lifecycle begin and terminal transitions to it. Result persistence and compaction enforcement remain unwired.

- Campaign issue: #83
- Programme: #14
- Parent campaign: #31
- Target hub: #8
- State: `implementing`
- Worker: GPT-5.6 Thinking
- Fieldwork dossier: merged PR #93
- Current owned Codex main: `teamleaderleo/codex@f9da1593f2499f6acde081d405c1a5df4ee2ea00`
- Public source pin: [Codex revision `3725f02cf38d856bc82bb46dd68ab61bb96ec6fc`](https://redirect.github.com/openai/codex/commit/3725f02cf38d856bc82bb46dd68ab61bb96ec6fc)
- Upstream contact: unauthorized

## Accepted owned-fork foundations

| Slice | Owned PR | Merge commit | Validation | Behavior change |
| --- | --- | --- | --- | --- |
| operation effect and receipt contract | `teamleaderleo/codex#3` | `f84e8d6fb48917965b7dacc1b28147663a28dd84` | full `codex-tools` suite passed | none |
| raw call/result identity validator | `teamleaderleo/codex#2` | `f68ad3830bf582ebd78f046f039be08510f48a9f` | focused `codex-core compaction_identity` suite passed | none; validator has no production caller |
| exposure wrapper effect delegation | `teamleaderleo/codex#12` | `e6b3017f4c725e0e6c48fc4e7fa703e365b2be67` | focused regression passed: 1 test, 3111 skipped | none |
| canonical live owner plus lifecycle begin/terminal wiring | `teamleaderleo/codex#19` | `f9da1593f2499f6acde081d405c1a5df4ee2ea00` | focused owner and lifecycle suites, formatting, and diff hygiene passed | records live receipt state; no result-persistence or compaction gate |

## Canonical live receipt contract

The accepted owner lives on `SessionState`, not `TurnState`.

- one session-scoped map is keyed by existing call identity;
- lifecycle start begins a conservative `PotentialMutation` receipt;
- lifecycle finish records completed, failed or blocked, and aborted terminal states;
- late observations default conservatively to `PotentialMutation`;
- repeated identity escalates to potentially mutating and marks terminal and result state ambiguous;
- `has_unreconciled_potential_mutation()` is available for later preflight;
- retained receipts are capped at 1,024;
- overflow sets permanent `coverage_lost`, does not silently evict evidence, and must fail closed later.

The earlier turn-scoped owner from Codex PR #9 was removed. Keeping both maps would have created competing synchronization owners, and a turn-only map would disappear before later manual compaction.

## Next source stage: authoritative result persistence

Lifecycle completion is not result persistence. The next slice must mark a result persisted only after its authoritative owner accepts it.

1. **Direct calls**
   - preserve call identity beside each in-flight direct future;
   - after the successful `ResponseInputItem` is converted and appended through `record_conversation_items`, mark that call's result persisted;
   - if authoritative append fails after handler completion, mark the result ambiguous.
2. **Nested code-mode calls**
   - keep their source-qualified identity separate from direct calls;
   - mark persisted only when the code-mode delivery owner accepts the result;
   - do not let a direct call ID update a nested code-mode receipt or vice versa.

Do not infer persistence merely because a handler returned a value.

## Later durable persistence

The session owner remains process-local. Resume and fork reconstruction requires:

- versioned receipt update rollout items before compaction;
- restoration into the live owner on resume or fork;
- the minimal unresolved or reconciled receipt set carried in each compacted checkpoint.

Do not put receipts only in replacement history and do not leave them only in memory.

## Enforcement map

After authoritative result persistence and durable restoration exist, one shared preflight must run twice in every compaction implementation:

1. **Before request construction**
   - local compaction: before cloned history is converted with `for_prompt`;
   - remote v1: before compact request history is built;
   - remote v2: before prompt or retained-message input is built.
2. **Before replacement installation**
   - immediately before `Session::replace_compacted_history` in local, remote v1, and remote v2.

The preflight must reject when:

- raw history has any call/result identity defect;
- the live owner reports an unreconciled potentially mutating operation;
- live or durable receipt coverage is incomplete;
- a duplicate, conflicting, late, or reordered observation remains unreconciled.

The second check matters because tool futures or persistence state can change while a compaction request is in flight.

## Remaining work

1. Wire authoritative direct and nested code-mode result persistence.
2. Define versioned rollout receipt updates and resume/fork restoration.
3. Carry minimal receipt evidence through compacted checkpoints.
4. Add the shared preflight at all six request and installation boundaries.
5. Add late-result reconciliation plus duplicate and causal-order rejection.
6. Prove complete identities continue normally and every ambiguous mutation fails closed without automatic replay.

## Stop rule

Do not claim a repair until compiled owned-fork tests cover complete, missing, duplicate, reordered, orphan, late, persistence-failure, and coverage-loss cases across local, remote v1, and remote v2 compaction, continuation, resume, fork, and retry. No upstream interaction is authorized.
