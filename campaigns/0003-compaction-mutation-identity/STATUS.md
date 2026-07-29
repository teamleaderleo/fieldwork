# Compaction Mutation Identity

## In simple words

Campaign #83 has moved from source mapping into staged owned-fork implementation. Three behavior-neutral foundations are merged: a conservative operation-effect and receipt contract, a raw call/result identity validator, and wrapper delegation that preserves explicit read-only classification. A bounded turn-scoped receipt owner is the current candidate. Compaction behavior remains unchanged.

- Campaign issue: #83
- Programme: #14
- Parent campaign: #31
- Target hub: #8
- State: `investigating`
- Worker: GPT-5.6 Thinking
- Fieldwork dossier: merged PR #93
- Owned Codex base at start: `teamleaderleo/codex@2b7b93081361b77f8ddaceaf362a09765b4153bf`
- Current owned Codex main after accepted foundations: `e6b3017f4c725e0e6c48fc4e7fa703e365b2be67`
- Public source pin: [Codex revision `3725f02cf38d856bc82bb46dd68ab61bb96ec6fc`](https://redirect.github.com/openai/codex/commit/3725f02cf38d856bc82bb46dd68ab61bb96ec6fc)
- Upstream contact: unauthorized

## Merged owned-fork foundations

| Slice | Owned PR | Merge commit | Validation | Behavior change |
| --- | --- | --- | --- | --- |
| operation effect and receipt contract | `teamleaderleo/codex#3` | `f84e8d6fb48917965b7dacc1b28147663a28dd84` | full `codex-tools` test suite passed | none |
| raw call/result identity validator | `teamleaderleo/codex#2` | `f68ad3830bf582ebd78f046f039be08510f48a9f` | focused `codex-core compaction_identity` suite passed | none; validator has no production caller |
| exposure wrapper effect delegation | `teamleaderleo/codex#12` | `e6b3017f4c725e0e6c48fc4e7fa703e365b2be67` | focused regression passed: 1 test, 3111 skipped | none |

## Active source slice

Owned PR `teamleaderleo/codex#9` adds a turn-scoped receipt map without dispatch or compaction wiring.

Accepted candidate rules:

- late terminal or persistence observations create a conservative `PotentialMutation` receipt;
- repeated call identity escalates the effect to `PotentialMutation` and marks the receipt ambiguous;
- duplicate persistence and conflicting terminal outcomes remain ambiguous;
- `has_unreconciled_potential_mutation()` reports any incomplete potentially mutating operation;
- receipts remain bounded by the turn in this stage.

A seven-test focused `codex-core` run is the merge gate.

## Superseded branches

- owned PR #8 and its clean restack #13 were closed because the session-wide ledger combined direct-call source assumptions, cross-turn retention, overflow policy, and wrapper edits before the turn owner and rollout persistence contracts were settled;
- duplicate wrapper restacks #10 and #11 were closed;
- no code from those branches is accepted.

## Next stages after the turn owner

1. Wire begin after the model call item becomes durable.
2. Record terminal state after direct, code-mode, failed, blocked, or cancelled dispatch.
3. Record result persistence at the authoritative direct-history and nested code-mode owners without merging those source paths.
4. Emit live operation receipts as rollout items.
5. Carry the minimal unresolved or reconciled receipt set into `CompactedItem` for resume and fork.
6. Consume both the raw-history validator and durable receipts before local, remote v1, and remote v2 normalization and replacement.
7. Add complete, missing, duplicate, reordered, orphan, late, resume, fork, and retry tests.

## Current implementation boundary

No source merged so far changes compaction, retry, or user-visible behavior. The first enforcement change remains blocked on one durable receipt owner and compiled integration tests.

## Risks retained

- Defaulting every unknown tool to read-only would preserve the replay risk.
- Tool-name heuristics would drift across native, dynamic, extension, MCP, app, shell, code-mode, and subagent paths.
- Turn-only receipts disappear before later compaction unless promoted into rollout state.
- Suffix-only receipt persistence is lost when reconstruction starts from the newest compacted checkpoint.
- Checkpoint-only receipts arrive too late for pre-compaction validation.
- Direct and nested code-mode result persistence require separate ownership.

## Stop rule

Do not claim a repair until compiled owned-fork tests cover complete, missing, duplicate, reordered, orphan, and late identities across every compaction implementation and prove that no ambiguous mutation is replayed after continuation, resume, fork, or retry.
