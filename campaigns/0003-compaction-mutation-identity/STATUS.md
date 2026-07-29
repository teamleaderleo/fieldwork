# Compaction Mutation Identity

## In simple words

Campaign #83 is in staged owned-fork implementation. The canonical session receipt owner now records lifecycle start, terminal outcome, and authoritative persistence for direct tool results. Owned Codex PR #20 reports persistence only after rollout append succeeds and marks append failure as ambiguous. Nested Code Mode delivery, durable reconstruction, safe receipt retirement, and compaction enforcement remain unwired.

- Campaign issue: #83
- Programme: #14
- Parent campaign: #31
- Target hub: #8
- State: `implementing`
- Worker: GPT-5.6 Thinking
- Fieldwork dossier: merged PR #93
- Current owned Codex main: `teamleaderleo/codex@1d9cc9709bb4c71b7b388e2baf0ab131e5585a61`
- Public source pin: [Codex revision `3725f02cf38d856bc82bb46dd68ab61bb96ec6fc`](https://redirect.github.com/openai/codex/commit/3725f02cf38d856bc82bb46dd68ab61bb96ec6fc)
- Upstream contact: unauthorized

## Accepted owned-fork foundations

| Slice | Owned PR | Merge commit | Validation | Behavior change |
| --- | --- | --- | --- | --- |
| operation effect and receipt contract | `teamleaderleo/codex#3` | `f84e8d6fb48917965b7dacc1b28147663a28dd84` | full `codex-tools` suite passed | none |
| raw call/result identity validator | `teamleaderleo/codex#2` | `f68ad3830bf582ebd78f046f039be08510f48a9f` | focused `codex-core compaction_identity` suite passed | none; validator has no production caller |
| exposure wrapper effect delegation | `teamleaderleo/codex#12` | `e6b3017f4c725e0e6c48fc4e7fa703e365b2be67` | focused regression passed: 1 test, 3111 skipped | none |
| canonical live owner plus lifecycle begin/terminal wiring | `teamleaderleo/codex#19` | `f9da1593f2499f6acde081d405c1a5df4ee2ea00` | focused owner and lifecycle suites, formatting, and diff hygiene passed | records live receipt state; no compaction gate |
| authoritative direct result persistence | `teamleaderleo/codex#20` | `1d9cc9709bb4c71b7b388e2baf0ab131e5585a61` | 4 direct transition tests, 1 identity-classification test, 9 owner tests, patch hygiene, and final-head V8 passed | direct results become persisted or ambiguous from authoritative append outcome; no compaction gate |

## Canonical live receipt contract

The accepted owner lives on `SessionState`, not `TurnState`.

- one session-scoped map is keyed by existing call identity;
- lifecycle start begins a conservative `PotentialMutation` receipt;
- lifecycle finish records completed, failed or blocked, and aborted terminal states;
- direct result persistence is recorded only after `record_conversation_items` reports authoritative rollout append success;
- direct append failure records an ambiguous result;
- a duplicate persistence observation becomes ambiguous;
- a result without prior begin creates conservative potential-mutation evidence and remains unreconciled because terminal coverage is missing;
- late observations default conservatively to `PotentialMutation`;
- repeated identity escalates to potentially mutating and marks terminal and result state ambiguous;
- `has_unreconciled_potential_mutation()` is available for later preflight;
- retained receipts are capped at 1,024;
- overflow sets permanent `coverage_lost`, does not silently evict evidence, and must fail closed later.

The earlier turn-scoped owner from Codex PR #9 was removed. Keeping both maps would have created competing synchronization owners, and a turn-only map would disappear before later manual compaction.

## Direct result boundary now accepted

The direct in-flight drain is the authoritative direct-result owner.

1. Extract call identity from direct function, MCP, custom-tool, and client-executed tool-search results.
2. Convert the result into a response item and append it to in-memory history.
3. Attempt authoritative rollout persistence.
4. Record `Persisted` only when that append succeeds.
5. Record `Ambiguous` when the append fails.
6. Leave server-executed tool-search results outside the client receipt path.

Handler return and terminal lifecycle completion are not persistence evidence.

## Sequence correction from recent Fieldwork review

The next stages are ordered to avoid turning long healthy sessions into permanent coverage-loss failures.

1. Move receipt begin to the durable call-item boundary and propagate the exact selected-runtime effect.
2. Add separate source-qualified nested Code Mode result delivery; direct and nested identities must not update each other.
3. Emit versioned receipt lineage into rollout state, restore it on resume and fork, and carry the minimal required evidence in compacted checkpoints.
4. Define safe retirement for reconciled receipts after their evidence is durable. Unresolved or ambiguous potential mutations must never be silently evicted.
5. Only then enable the raw-history plus receipt preflight before request construction and before replacement installation in local, remote v1, and remote v2 compaction.
6. Apply the resulting certainty contract to automatic retry and authority-aware fallback.

This order is consistent with adjacent campaigns:

- #84 requires captured-call authority across MCP catalogue generations and should reuse #83 receipts rather than create another lifecycle owner;
- #85 preserves the distinction between Direct and Code Mode execution surfaces;
- #86 depends on #83 mutation certainty before allowing or rejecting fallback.

## Durable checkpoint boundary

The session owner remains process-local. Resume and fork reconstruction requires:

- versioned receipt update rollout items before compaction;
- restoration into the live owner on resume or fork;
- the minimal unresolved or reconciled receipt set carried in each compacted checkpoint;
- a retirement rule proving that removed live entries remain recoverable from durable evidence.

Do not put receipts only in replacement history and do not leave them only in memory.

## Enforcement map

After authoritative nested result persistence, durable restoration, and safe retirement exist, one shared preflight must run twice in every compaction implementation:

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

1. Move begin/effect capture to the durable selected-call boundary.
2. Add source-qualified nested Code Mode result persistence.
3. Define versioned rollout receipt updates, checkpoint carry-forward, and resume/fork restoration.
4. Add safe retirement without silent loss of ambiguous mutation evidence.
5. Add the shared preflight at all six request and installation boundaries.
6. Add late-result reconciliation plus duplicate and causal-order rejection.
7. Prove complete identities continue normally and every ambiguous mutation fails closed without automatic replay.

## Stop rule

Do not claim a repair until compiled owned-fork tests cover complete, missing, duplicate, reordered, orphan, late, persistence-failure, coverage-loss, retirement, resume, and fork cases across local, remote v1, remote v2, continuation, and retry. No upstream interaction is authorized.
