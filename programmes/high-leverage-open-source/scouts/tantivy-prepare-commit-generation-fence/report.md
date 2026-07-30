# Tantivy `prepare_commit` worker-generation fence

Date: 2026-07-30

Fieldwork: #180  
Programme: #114  
Target: `quickwit-oss/tantivy`  
Pinned source: [`667132fa7ab4a30e0c1870d791f23902ebfc6152`](https://redirect.github.com/quickwit-oss/tantivy/commit/667132fa7ab4a30e0c1870d791f23902ebfc6152)  
Upstream contact authorized: `false`

## In simple words

Tantivy changes to a new indexing-worker generation before it knows that the old generation finished successfully.

During `IndexWriter::prepare_commit()`, it replaces the document channel, takes all old worker handles, joins them one at a time, and starts a replacement worker after each successful join. A later worker error returns immediately. Replacement workers already started remain live, while old handles not yet visited are dropped and their threads can continue.

The failure mechanism tied to an old worker belongs to the old status object. It does not automatically kill the new status installed during the channel swap.

The source therefore does not yet prove that a failed commit preparation leaves one authoritative generation. A controlled target test is required before calling this an index-corruption defect.

## Exact source path

Reviewed files:

- `src/indexer/index_writer.rs`;
- `src/indexer/index_writer_status.rs`.

Relevant order:

```text
prepare_commit
  -> recreate_document_channel
       -> install new operation sender
       -> install new IndexWriterStatus
  -> take old workers_join_handle
  -> for each old worker
       -> join old worker
       -> propagate panic/error with ?
       -> add one replacement worker
  -> stamp and create PreparedCommit
```

The loop is not all-or-nothing. If worker A joins and replacement A starts, then worker B fails:

```text
new generation already has replacement A
prepare_commit returns Err
remaining old JoinHandles are dropped
remaining old threads may continue
new IndexWriterStatus remains alive
```

## Status-object ownership

Every indexing worker creates an `IndexWriterBomb` from the status object available when that worker is spawned.

When a worker exits normally, it defuses the bomb. When it exits through an error or panic, dropping the bomb kills that status object by removing its stored receiver and setting `is_alive = false`.

`recreate_document_channel()` replaces `self.index_writer_status` before old workers are joined. Old bombs therefore refer to the old status generation. Their failure cannot by itself poison the new status used by replacement workers and later `add_document()` calls.

## Why this matters

The public documentation says `prepare_commit()` flushes all pending indexing work and then returns a prepared commit that may be committed or aborted.

After an error, callers need a truthful terminal state:

- all old workers stopped and no old segment can publish;
- or the writer is retired and rejects new operations;
- or an explicit reconciliation state blocks a later commit;
- or a generation check proves late old publications are ignored.

The reviewed source does not make one of those outcomes explicit at the `IndexWriter` boundary.

## Strongest current hypothesis

A multi-worker failure can produce a mixed lifecycle:

```text
old generation partially joined
+ new generation partially started
+ prepare_commit returned Err
+ old publication may still be in flight
+ new document admission may remain available
```

This is a source-backed hypothesis, not executed evidence.

## Discriminating target test

Use at least three workers and deterministic barriers:

1. worker A completes successfully;
2. replacement A starts on the new channel;
3. worker B returns an injected indexing error;
4. worker C remains blocked before segment scheduling;
5. `prepare_commit()` returns the worker-B error;
6. attempt `add_document()` on the same writer;
7. release worker C and observe whether it schedules a segment;
8. attempt another commit;
9. inspect committed opstamp, searchable documents, segment inventory, and garbage-collection behavior.

Required assertions:

- whether new document admission succeeds after the failed preparation;
- whether old worker C can publish after the error was returned;
- whether the next commit includes, excludes, duplicates, or loses old-generation work;
- whether rollback retires old and replacement workers;
- whether the original worker error remains authoritative when cleanup also fails.

## Additional controls

Separate these failure classes:

- worker returns an ordinary indexing error;
- worker panics;
- replacement worker spawn fails after one or more replacements started;
- segment-updater scheduling fails after segment files are finalized;
- all workers succeed.

A repair must preserve ordinary multi-worker throughput and must not silently discard successfully indexed documents unless rollback is the declared contract.

## Candidate repair boundaries

### Join before replacement

Join every old worker and collect all outcomes before starting any replacement worker. On any failure, retire or reconstruct the writer explicitly.

This is the simplest generation fence, but it may increase the gap before the next generation is ready.

### Explicit failed-preparation state

Allow early replacement startup but mark the writer `preparation_failed` if any old worker fails. Block document admission and later commit until rollback or reconstruction joins every old and replacement worker.

This preserves overlap but adds a durable lifecycle state.

### Generation-tagged publication

Tag worker and segment-updater operations with a writer generation and reject publication from a generation whose preparation failed.

This is stronger but wider. It should not be selected unless the target test proves late publication reaches the updater.

## Duplicate and history check

A targeted issue search found no current report for partial replacement-worker startup plus unjoined old workers after `prepare_commit()` failure.

Historical change [`Prepare commit is public again`](https://redirect.github.com/quickwit-oss/tantivy/commit/8802d125f84fbd6dc1c3ef632bfa76d2cfa647ba) establishes API history only. It does not settle current failure ownership.

## Evidence classification

- source ordering and status ownership: `source-read`;
- failure state machine: `model-prepared`;
- repository-native regression: absent;
- target execution: absent;
- durable-index consequence: unconfirmed.

## Stop condition

Stop the first scout after one deterministic repository-native test establishes whether old-generation segment publication or new-generation admission remains possible after a later worker fails during `prepare_commit()`.

Do not prepare an upstream packet before target execution and duplicate/history refresh.

No upstream contact occurred.
