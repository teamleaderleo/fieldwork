# Campaign 0003: Compaction Mutation Identity

State: `investigating`

Campaign issue: #83

Programme: #14

Parent campaign: #31

Primary target: #8

Upstream contact authorized: `false`

## In simple words

A tool call is written to history before its handler runs. Its result is written later, after the provider response may already be complete. Compaction can then replace the raw history after prompt normalization has inserted a synthetic `aborted` result, preserved duplicate or reordered results, or removed an orphan late result.

This campaign will prevent a mutation from crossing compaction until its completion and durable result identity agree, or an explicit reconciliation records the outcome.

## Exact question

Can local compaction, remote compaction v1, and remote compaction v2 reject or pause incomplete mutation identity before replacement, carry a bounded operation receipt into the checkpoint, and resume only after late, duplicate, or causally reordered results are reconciled?

## Source boundary

- Public source: [Codex revision `3725f02cf38d856bc82bb46dd68ab61bb96ec6fc`](https://redirect.github.com/openai/codex/commit/3725f02cf38d856bc82bb46dd68ab61bb96ec6fc)
- Owned fork inspection: `teamleaderleo/codex@2b7b93081361b77f8ddaceaf362a09765b4153bf`
- Parent evidence: #38 / PR #64 and #43 / PR #81
- Public source remains read-only.

## Current answer

Raw history records call and result variants but carries no durable operation-effect classification or terminal completion receipt. A compaction-only validator therefore cannot distinguish a harmless read from a mutation without either guessing from tool names or conservatively treating every client-executed call as potentially mutating.

The recommended implementation is staged:

1. define a bounded operation-effect and terminal-receipt contract at dispatch;
2. persist the receipt alongside the call/result lifecycle;
3. validate raw history plus receipts before every compaction implementation;
4. preserve compacted operation evidence needed for resume, fork, retry, and late-result reconciliation.

## Stop condition

Complete identities continue normally. Missing, duplicate, reordered, and late potentially mutating calls fail closed without replay across local, remote v1, and remote v2 compaction. The compiled owned-fork tests must establish this before the campaign is accepted.
