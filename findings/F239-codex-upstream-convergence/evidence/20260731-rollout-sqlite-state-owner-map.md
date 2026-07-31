# Codex rollout and SQLite state-owner map

Date: 2026-07-31  
Evidence class: `source-read`  
Public source pin: `openai/codex@5548c95d66e29aeb994a982db8a378d9453694b0`  
Upstream interaction: read-only

## Finding

Current local thread persistence has three related representations with separate owners:

1. rollout JSONL is the canonical durable replay history;
2. the state database is a queryable metadata index;
3. the thread-history database is a queryable turns/items projection with its own byte-offset and ordinal checkpoint.

A successful write or repair at one representation cannot prove the other two are current.

## Exact source owners

| Fact | Current owner | Current source |
| --- | --- | --- |
| canonical replay records | `RolloutRecorder` / local live writer | `codex-rs/rollout/src/recorder.rs`; `codex-rs/thread-store/src/local/live_writer.rs` |
| active-thread lifecycle | `LiveThread` | `codex-rs/thread-store/src/live_thread.rs` |
| append-derived metadata observation | `ThreadMetadataSync` | `codex-rs/thread-store/src/thread_metadata_sync.rs` |
| metadata index and startup backfill | rollout state-DB adapter / `codex_state::StateRuntime` | `codex-rs/rollout/src/state_db.rs` |
| turns/items projection | local thread-history materializer | `codex-rs/thread-store/src/local/thread_history_materialization.rs` |
| projection checkpoint and transaction | local thread-history store | `codex-rs/thread-store/src/local/thread_history.rs` |
| listing fallback and read repair | rollout recorder plus local thread-store listing | `codex-rs/rollout/src/recorder.rs`; `codex-rs/thread-store/src/local/list_threads.rs` |

## Write ordering and caller-visible facts

### Canonical history before projection

For paginated history, the local writer flushes rollout JSONL before projecting into SQLite. The source comment is explicit: SQLite is a rebuildable view and may lag JSONL after failure, while it must never get ahead of canonical history.

History projection failure is logged as a warning from the live writer and the canonical write returns success. Therefore:

- rollout durability can be established while the history projection remains stale;
- append success does not establish turns/items query freshness;
- a later materialization pass owns catch-up.

### Metadata follows canonical append

`LiveThread::append_items` first persists rollout items. It then derives metadata and calls `update_thread_metadata`.

If the canonical append succeeds and metadata update fails, the caller receives an error after replay history is already durable. That result is an ambiguous composite fact:

- canonical append: succeeded;
- metadata index update: failed;
- caller operation: returned error.

A retry policy must preserve those separate facts or it can duplicate replay records while trying to repair metadata.

### Lazy creation and flush

New rollout files can be created lazily. `Persist` may write the initial `SessionMeta`; `Flush` persists queued records; each can advance the canonical file and trigger projection. Metadata synchronization defers create metadata until history exists and can defer resume-derived metadata until a later append.

This protects empty failed initialization from appearing durable, while introducing a real ordering boundary between opening a live writer, materializing canonical history, and publishing metadata.

## History-projection invariants already present

The current materializer has several conservative controls:

- it reads from the saved byte offset and expected ordinal;
- it projects only newline-terminated records;
- it leaves a trailing partial record for a later pass;
- invalid or unknown lines are held pending until a later ordinal can resolve whether they consumed history;
- a same-ordinal valid retry can replace a rejected write without advancing only one checkpoint;
- a later ordinal can authorize an explicit skipped ordinal range only when the number of rejected lines can cover the gap;
- rollout shrinkage, backward ordinals, unexplained ordinal gaps, and checkpoint mismatch are errors;
- rows and the byte/ordinal checkpoint advance in one `BEGIN IMMEDIATE` transaction;
- transaction failure keeps SQLite behind the rollout instead of claiming unmaterialized data.

These are strong local invariants. They do not supply a complete user-facing rebuild operation or prove that every read surface triggers reconciliation.

## Listing and repair paths

Default unsectioned listing uses `ScanAndRepair`:

1. scan rollout files first, overfetching up to twice the requested page;
2. repair the state DB for filesystem hits;
3. query SQLite;
4. reconcile DB-only filtered hits when needed;
5. fall back to the filesystem page when SQLite is absent or errors.

Search performs fuller reconciliation because title and preview can depend on metadata beyond the rollout head. Ordinary metadata-filtered listing can use lighter read repair for filesystem hits.

Several paths have a stricter dependency on SQLite:

- explicit `use_state_db_only` listing skips scan and repair;
- relation and section filters route through the state DB;
- section-position ordering errors when the state DB is unavailable;
- non-owning `get_state_db` opens only an existing database whose startup backfill is already complete;
- startup initialization waits for the backfill gate and can fail after a bounded timeout.

This explains how valid rollout files can remain readable while a particular list or relation surface omits them. It does not prove the root cause of any public report until the exact caller flags and database state are reproduced.

## Recovery gaps worth testing

### R1 — Metadata-index absence

Create valid rollouts, remove selected metadata rows, and exercise:

- default unfiltered listing;
- metadata-filtered listing;
- search;
- `use_state_db_only` listing;
- relation listing;
- section listing;
- direct read and resume.

Expected result: every surface declares whether it repairs, falls back, returns partial results, or requires the state DB. Silent omission should be distinguishable from an intentional DB-only contract.

### R2 — History projection lag

Inject a failure after canonical flush and before or during the history projection transaction.

Expected result:

- canonical rollout remains readable;
- projection checkpoint never advances past applied rows;
- a later materialization catches up idempotently;
- list/read APIs that use turns/items expose a bounded stale or recovery state rather than treating projection freshness as canonical durability.

### R3 — Metadata failure after append

Inject metadata-update failure after a durable append.

Expected result:

- caller evidence distinguishes `history durable / metadata stale` from total append failure;
- retrying metadata does not append duplicate rollout items;
- restart reconciliation restores metadata from canonical history;
- observability records which boundary failed.

### R4 — Partial, rejected, and unknown lines

Cover trailing partial JSON, malformed complete lines, unknown future variants with and without ordinals, same-ordinal corrected retries, and later valid ordinals.

Expected result: byte and ordinal checkpoints remain coupled, valid neighboring records remain recoverable, and skipped ranges are explicit and counted.

### R5 — Interrupted startup backfill

Interrupt the backfill owner, expire its lease, and initialize a second process.

Expected result: one process owns the lease at a time, stale ownership can be recovered, complete state is durable, and non-owning readers never mistake an incomplete backfill for a current index.

### R6 — Bounded cost

Exercise large histories and large rollout directories.

Measure:

- files scanned per page;
- bytes read from rollout heads and histories;
- rows and WAL bytes written;
- startup gate duration;
- search and filtered-list repair amplification;
- retry behavior after repeated projection failure.

The current two-page overfetch is a bounded page heuristic, not a complete-directory rebuild guarantee.

## Proposed state vocabulary

A future repair API or receipt should distinguish at least:

- `CanonicalOnly`: rollout durable, one or more projections stale or absent;
- `Projected`: canonical rollout and required projections agree through a named checkpoint;
- `Recovered`: stale or absent projection rebuilt from canonical history;
- `Skipped`: malformed or unsupported record excluded with exact offset/ordinal evidence;
- `Ambiguous`: canonical write succeeded while a later required projection or metadata publication failed;
- `Failed`: canonical history itself could not be established or read.

This vocabulary is a proposal for investigation and tests. It is not current Codex API behavior.

## Relationship to existing findings

- F83 append acknowledgement owns caller-visible acknowledgement for a bounded write. This lane owns reconciliation among canonical history, metadata index, and history projection after split outcomes.
- Receipt replay owns durable operation identity and retry/compaction consequences. It can consume reconciliation facts but should not infer them.
- SDK/runtime coherence can test which recovery behavior is exposed through app-server and SDK surfaces, but the local store remains the source owner.

## Recommended next source packet

Start with tests and a source-neutral receipt before implementing a user command:

1. add fault-injection controls around canonical flush, metadata update, projection transaction, and startup backfill;
2. record the exact state reached at each boundary;
3. exercise every read/list mode against the same fixture;
4. identify whether an existing repair entrypoint can be safely exposed or whether a new bounded reconciliation owner is required.

A repair command should follow only after the state-owner and idempotence controls are executed.

## Limits

- This note establishes current source ordering and API routing, not frequency or user impact.
- Public issue reports remain reports until reproduced at an exact source revision.
- The public source can move and expire present-tense claims.
- No merge, product change, deployment, credentials, or public upstream interaction occurred.
