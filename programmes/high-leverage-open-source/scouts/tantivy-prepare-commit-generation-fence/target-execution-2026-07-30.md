# Tantivy `prepare_commit` generation-fence target execution — 2026-07-30

## Status

Evidence class: `target-executed` for the selected multi-worker lifecycle path.

Production repair: absent.

Upstream contact authorized: `false`.

Upstream contact performed: `false`.

## Exact inputs

- public source pin: [`quickwit-oss/tantivy@667132fa7ab4a30e0c1870d791f23902ebfc6152`](https://redirect.github.com/quickwit-oss/tantivy/commit/667132fa7ab4a30e0c1870d791f23902ebfc6152);
- owned fork branch: `teamleaderleo/tantivy:fieldwork/prepare-commit-generation-fence`;
- executed owned head: `b92909ef3d5ac5695d1c85b1b0cb52a03ee51e49`;
- focused workflow: `30513367302`;
- exact compiler: Rust `1.88.0`;
- generated `Cargo.lock` SHA-256: `5c858d36e690fc2078ec707b251f60ff5ca2fd56c83eb284d2937d8db35908dd`;
- `cargo metadata` SHA-256: `6290ad8e475756aee3f72a862e264292fa706c43fd665a42795c63232fbc04b0`.

Rust 1.88 was used because the pinned source's declared Rust 1.86 conflicts with `tantivy-common`'s direct `time ^0.3.47` dependency. That compatibility finding is recorded separately in #200.

## Executed test

The repository-native test is:

```text
indexer::index_writer::prepare_commit_generation_fence::
prepare_commit_failure_leaves_next_generation_live_and_accepts_late_old_segment
```

The test controls worker order directly:

1. retire the repository-created indexing workers;
2. install three old-generation worker handles in a deterministic order;
3. let the first worker join successfully;
4. make the second worker return a synthetic old-worker failure;
5. hold the third old worker until after `prepare_commit()` returns;
6. observe that one replacement worker has already been started on the new document channel;
7. add a new-generation document after the failed preparation;
8. release the unjoined old worker and allow it to publish a segment through the shared `SegmentUpdater`;
9. call a later `commit()`;
10. query the index for both the old-generation and new-generation terms.

## Result

The target test passed:

```text
running 1 test
...prepare_commit_failure_leaves_next_generation_live_and_accepts_late_old_segment ... ok

1 passed; 0 failed
```

The executed behavior was:

- `prepare_commit()` returned the synthetic old-worker error;
- the replacement generation's `IndexWriterStatus` remained alive;
- one replacement worker was already installed;
- `add_document()` accepted a new-generation document;
- the unvisited old worker remained live after its `JoinHandle` was dropped;
- that old worker published its segment after `prepare_commit()` had returned;
- a later `commit()` succeeded;
- both the late old-generation document and the newly admitted document were searchable.

This confirms the source-read lifecycle model. It does **not** show index corruption: the later commit retained both documents consistently in this controlled path. It does show that failed commit preparation is not a generation fence and does not leave the writer in a terminal or reconciled state.

## Adjacent controls

The same generated dependency graph ran the selected adjacent controls:

```text
test_prepare_for_store ... ok
test_prepare_with_commit_message ... ok
test_prepare_but_rollback ... ok

3 passed; 0 failed
```

The separate `test_rollback` filter collected zero tests at this source pin. It supplies no additional rollback evidence beyond `test_prepare_but_rollback`.

Clippy also passed in the focused workflow.

The ordinary owned Unit Tests workflow for the exact head was still running at receipt creation and must be recorded separately when complete.

## Candidate consequence

Admission blocking alone is insufficient. Even if new documents were rejected after the returned error, the unjoined prior-generation worker could still publish through the shared updater unless cleanup or publication ownership is also fenced.

A repair should choose and prove one complete contract:

1. join every old worker and collect all terminal results before starting replacements;
2. retire or poison the writer on any old-worker failure and reconcile remaining workers;
3. generation-tag segment publication and reject late old-generation output;
4. or combine an explicit failed-preparation state with total cleanup ownership.

## Required next controls

- worker panic rather than returned `TantivyError`;
- failure in the first worker before any replacement starts;
- multiple unvisited old workers;
- replacement-worker spawn failure;
- rollback after failed preparation with every old and replacement worker accounted for;
- opstamp and delete-queue ordering around late publication;
- throughput comparison for a join-all-before-replace repair;
- exact full repository gate on any source candidate.

## Boundary

Keep the lifecycle result separate from #200's Rust-version/dependency contradiction.

No public Tantivy issue, pull request, review, comment, reaction, branch, or message was created or changed.
