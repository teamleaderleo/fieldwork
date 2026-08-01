# Approaches considered

## 1. Depend on the broadcast subscriber transcript

### Approach

Keep completion output derived from chunks observed by the watcher/subscriber.

### Result

Rejected.

Broadcast delivery is best-effort. Early output can precede subscription, a receiver can lag beyond the ring, and receiver closure can discard delivery. Completion output then depends on timing instead of producer-observed bytes.

### Evidence

The original reproduction in [Fieldwork PR #33](https://github.com/teamleaderleo/fieldwork/pull/33) and the focused tests in [Codex PR #6](https://github.com/teamleaderleo/codex/pull/6) demonstrate output emitted before subscription and partial-stream completion behavior.

## 2. Increase broadcast capacity

### Approach

Make the broadcast ring larger so lag becomes less likely.

### Result

Rejected.

A larger ring reduces frequency and leaves the contract unchanged. Pre-subscription output remains absent, and sufficiently large or delayed output can still overrun the receiver.

## 3. Add a completion-only subscriber earlier

### Approach

Attach a dedicated subscriber near process start and collect every broadcast chunk for completion.

### Result

Rejected.

This still makes authoritative completion depend on broadcast delivery and task lifecycle. It also creates another receiver whose closure, scheduling, and shutdown behavior require coordination.

## 4. Retain an unbounded producer transcript

### Approach

Append every stdout/stderr byte to a producer-owned vector and return it at completion.

### Result

Rejected.

It solves timing loss and introduces unbounded memory growth for long-running or noisy processes.

## 5. Bounded producer-owned byte retention

### Approach

Retain raw bytes in bounded stdout/stderr deques before each best-effort broadcast attempt, then return the retained transcript at EOF.

### Result

Selected.

This establishes producer authority, decouples final output from subscriber timing, supports invalid UTF-8, and caps memory use.

### Key implementation choices

- Retain before broadcast.
- Keep raw bytes during collection.
- Evict oldest bytes when the cap is exceeded.
- Return retained bytes on normal EOF.
- Keep hard termination prompt.
- Reconcile retained and streamed views through suffix/prefix overlap.

## 6. Replace the streamed transcript outright

### Approach

At completion, discard the subscriber transcript and use only retained producer output.

### Result

Partially useful, then refined.

The bounded producer transcript can omit old bytes after eviction while the streamed transcript may contain them. Blind replacement could lose earlier streamed output. The selected reconciliation keeps useful streamed prefix data and appends the authoritative retained suffix without duplication.

## 7. Concatenate streamed and retained output

### Approach

Append retained output directly to streamed output.

### Result

Rejected.

The two views commonly overlap, which would duplicate bytes. The current patch computes suffix/prefix overlap before appending.

## 8. Patch the completion consumer only

### Approach

Teach `process.rs` to recover from lag without changing the producer.

### Result

Rejected.

A consumer cannot reconstruct bytes that no subscriber ever received. The producer must retain them.

## 9. Keep source and workflow in one branch

### Approach

Carry product code and the execution workflow together.

### Result

Used during early experiments, then rejected for the clean source handoff.

Shared carriers helped execute multiple units, yet they obscured source purity and created setup-only failures. The current source branch contains exactly four product/test files. Carrier logic stays separate.

## 10. Reuse the reviewed source blobs on current public main

### Approach

Take the exact four blobs from the live reviewed source in Codex PR #125 and commit them over current public main.

### Result

Selected for unit 26.

The four files were unchanged between the prior source base and current public main, so exact blob reuse creates a clean one-commit restack without manual code rewriting.

### Exact revisions

- Prior live source: `ee605985012dc1b768f03f6b450db16dd5c0467e`
- Current public base: `670f69416bf91c5dfd8b58669e78050b584ff053`
- Unit-owned source: `a020d7bd3e7f6886c3fbc21d75b3110586df08f5`
- Unit-owned tree: `9a067c244d464e863a7b50978826ac9930df680b`

## 11. Treat setup failures as product failures

### Approach

Use missing tools, shallow history, SHA-guard mismatches, or workflow reconstruction failures to judge the source patch.

### Result

Rejected under Fieldwork evidence policy.

The following remain setup/carrier evidence only:

- Codex PR #53 runs involving missing `just`, shallow history, and missing `uv`;
- Codex PR #94 source-branch consistency failure;
- any carrier run that stopped before source checkout and target tests.

## 12. Use the authoritative historical pass as current-head proof

### Approach

Declare the current restack ready because run `30587866332` passed the exact controls, full library gate, and integration compile on an earlier source revision.

### Result

Rejected.

That run is strong design and regression evidence. The current source head `a020d7...` still needs execution on current public base `670f694...`.

## 13. Contact public upstream now

### Approach

Open an upstream issue or pull request with the current source.

### Result

Deferred.

The target policy is invitation-only. This packet preserves issue and PR drafts for later use while making zero public-upstream writes.
