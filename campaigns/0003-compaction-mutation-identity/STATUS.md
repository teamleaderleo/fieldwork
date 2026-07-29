# Compaction Mutation Identity

## In simple words

Campaign #83 is claimed and source mapping has begun. The first finding is an ownership gap before compaction: call identity is durable, handler terminal state is primarily in memory, and result persistence happens later. Current raw history has no operation-effect field that lets a compaction gate isolate mutations safely.

- Campaign issue: #83
- Programme: #14
- Parent campaign: #31
- Target hub: #8
- State: `investigating`
- Worker: GPT-5.6 Thinking
- Fieldwork branch: `campaign/83-compaction-mutation-identity`
- Planned owned Codex branch: `fieldwork/83-compaction-mutation-identity`
- Public source pin: [Codex revision `3725f02cf38d856bc82bb46dd68ab61bb96ec6fc`](https://redirect.github.com/openai/codex/commit/3725f02cf38d856bc82bb46dd68ab61bb96ec6fc)
- Owned fork inspection pin: `teamleaderleo/codex@2b7b93081361b77f8ddaceaf362a09765b4153bf`
- Upstream contact: unauthorized

## Completed

- accepted parent evidence from L03 and L06;
- mapped call persistence, runtime terminal state, result persistence, prompt normalization, local replacement, and typed error options;
- confirmed that `CoreToolRuntime` exposes no operation-effect metadata;
- rejected an immediate tool-name heuristic as the campaign contract;
- selected a staged receipt-then-gate design for implementation.

## Active work

1. Define the smallest operation-effect and receipt API.
2. Identify the durable rollout/checkpoint representation.
3. Add compiled validator tests before wiring all compaction paths.
4. Add local, remote v1, and remote v2 integration coverage.

## Current implementation boundary

The first source change should introduce no automatic retry and no checkpoint migration. It should establish typed effect and terminal-state ownership plus focused validation tests. Compaction wiring follows only after the receipt has one clear persistence owner.

## Risks

- Defaulting every unknown tool to read-only would preserve the current replay risk.
- Defaulting every unknown tool to potentially mutating is safe but can block compaction after incomplete read calls.
- Tool-name heuristics would drift across native, dynamic, extension, MCP, app, shell, and code-mode paths.
- Adding a persisted receipt changes resume and fork compatibility and needs a versioned rollout contract.

## Stop rule

Do not claim a repair until compiled owned-fork tests cover complete, missing, duplicate, reordered, and late identities and prove that no ambiguous mutation is replayed.
