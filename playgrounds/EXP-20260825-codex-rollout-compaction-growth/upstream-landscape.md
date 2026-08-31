# Upstream route: corroborate the existing replacement-history issue

Date checked: 2026-08-25

Current public source: [OpenAI Codex `c3953649156e15b67e572cb9e38bc825a811c24e`](https://github.com/openai/codex/commit/c3953649156e15b67e572cb9e38bc825a811c24e)

## Decision

Corroborate [the existing subagent replacement-history issue](https://redirect.github.com/openai/codex/issues/31198) after human review. Do not open a new issue.

Seven of the eight measured rollouts above 1 GiB are subagent rollouts, so that issue owns most of the observed outliers. The largest rollout is a 13.26 GB VS Code/root rollout whose compacted checkpoints account for 91.4% of its bytes. That root-thread result adds useful scope: repeated `replacement_history` growth is not confined to inherited child histories.

The broader [session-rollout storage issue](https://redirect.github.com/openai/codex/issues/24948) already has extensive reports and maintainer discussion. The [oversized-rollout hydration issue](https://redirect.github.com/openai/codex/issues/29510) owns the RAM/crash consequence. Adding the same measurements to all three would fragment the evidence and create noise.

## Duplicate map

| Upstream item | Scope | Relation to this result | Route |
| --- | --- | --- | --- |
| [Replacement-history growth in subagents](https://redirect.github.com/openai/codex/issues/31198) | repeated full `compacted.replacement_history` in child rollouts | exact producer for seven of eight ≥1 GiB files; this result also adds a root rollout | **recommended corroboration** |
| [General rollout storage growth](https://redirect.github.com/openai/codex/issues/24948) | compaction history, tool output, compression, deletion | broad canonical storage discussion with substantial existing traffic | link mentally; do not add another near-duplicate comment |
| [CLI and Desktop storage growth](https://redirect.github.com/openai/codex/issues/34337) | multi-cause storage policy and a staged compression proposal | same product-level consequence; broader than this measurement | related, not a new owner |
| [Oversized rollout hydration](https://redirect.github.com/openai/codex/issues/29510) | app-server memory expansion while reading huge histories | downstream RAM consequence; the human owner already corroborated it | no additional comment recommended |
| [Image-heavy compacted rollouts](https://redirect.github.com/openai/codex/issues/34863) | inline PNG data copied through compaction | possible subtype, but this experiment did not inspect payload content | do not claim this subtype |
| [Image and subagent amplification](https://redirect.github.com/openai/codex/issues/35458) | screenshots plus compaction plus fork fan-out | related mechanism with a content-specific cause | do not claim this subtype |

## What the current source already fixes

Current `main` contains partial mitigations:

- cold rollout zstd compression exists, but `local_thread_store_compression` remains `UnderDevelopment`, defaults to disabled, and only processes files untouched for seven days;
- a recent change budgets images retained during remote compaction;
- paginated thread history and state-DB-first listing reduce some read pressure.

Those changes do not close this result. Current source still:

1. constructs every persisted compacted item with `replacement_history: Some(items.clone())`;
2. appends the new checkpoint without removing or referencing older checkpoint payloads;
3. loads every rollout line into a `Vec` in the full-history path;
4. exposes no enabled per-rollout or per-store byte budget.

No open pull request found by searches for replacement-history storage, rollout disk budgets, or compacted-checkpoint deduplication owns that persistence change.

## Reproduction strength

This packet has an independent current-version reproduction, not a fresh-profile minimal reproducer.

Established:

- the modification-time-fenced scan reruns byte-for-byte;
- all 6,246 compacted records contain the literal `replacement_history` field;
- those records account for 83.1% of 31.72 GiB;
- a same-store negative control is only 1.4% compacted by byte size;
- current public source identifies the append owner.

Not established:

- the smallest user action that deterministically creates the first oversized checkpoint;
- whether image, MCP, shell, browser, or another payload type dominates each replacement history;
- the exact source revision bundled into Desktop;
- a production-safe rewrite or garbage-collection boundary.

That is enough to corroborate an existing mechanism issue. A new issue would benefit from a fresh-profile end-to-end reproducer or a newly isolated producer that the existing issues do not own; neither condition is present.

## Proposed fix contract

The useful invariant is:

```text
stable replacement history of H bytes
        + N later compactions
        -> O(H + N × checkpoint_metadata) retained bytes
        not O(N × H)
```

A compatible implementation could use immutable content-addressed checkpoint payloads, with compacted records retaining only an object identity plus window metadata. A rewrite-based design is also possible, but it must preserve every checkpoint still reachable through resume, rollback, fork bases, window lineage, world-state replay, and late suffixes.

Regardless of representation, add three guardrails:

1. a regression that repeatedly compacts a stable large history and asserts sublinear physical growth;
2. per-record, per-rollout, and per-store byte telemetry with disk-pressure warnings or admission control;
3. bounded read/resume behavior that quarantines or summarizes an oversized rollout instead of hydrating it into an unbounded process heap.

Compression remains useful for cold history, but it is not the retention invariant. Active files can grow to multi-gigabyte size before the seven-day cold threshold, and reopening a compressed file materializes the logical JSONL again for append.

## Submission receipt

The human owner gave a bounded greenlight for one comment on the existing replacement-history issue. The exact body in `upstream-comment-draft.md` was submitted at `2026-08-25T15:44:38Z`; `upstream-submission.json` records the resulting comment URL and body digest.

The greenlight was consumed by that comment. No follow-up reply, edit, reaction, label, closure, or other upstream action is authorized.
