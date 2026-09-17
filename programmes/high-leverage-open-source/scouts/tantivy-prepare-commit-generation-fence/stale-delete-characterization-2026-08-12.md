## In simple words

A separate Tantivy data-integrity defect raised during review of public PR 2999 reproduces on current public `main`: pending uncommitted deletes can survive `delete_all_documents()`, the stamper can reuse their old opstamp range, and those stale deletes can then remove a document added after the clear.

This characterization explicitly neutralizes the already-public stale-`committed_opstamp` defect in issue #2666. After every successful commit, the test synchronizes `IndexWriter::committed_opstamp` to the returned commit opstamp before continuing. The disappearing-document sequence still reproduces.

Evidence class: `target-executed`.

## Exact target

Public repository:

```text
quickwit-oss/tantivy
```

Current `main` pinned for this execution:

```text
1f32c1a8af0eb9d68bd3f5576caf20941364b657
```

At that revision, `delete_all_documents()` removes all segments and rewinds the stamper to `self.committed_opstamp`, but it does not reset or clear `DeleteQueue`.

`DeleteQueue` retains newly pushed delete operations in its pending writer vector until a consumer flushes them into the linked block history.

## Exact execution

Owned carrier:

```text
teamleaderleo/tantivy#9
head 538384feaf002caab7c59c2305dadbb1cf5aa2ee
base 1f32c1a8af0eb9d68bd3f5576caf20941364b657
```

Workflow run:

```text
31587032482
```

Job:

```text
94083126054
```

The job passed exact-base/carrier verification, test-only materialization, Rust setup, locked-graph build, exact test enumeration, all three characterization tests, and final carrier hygiene.

## Primary characterization

Exact test:

```text
indexer::index_writer::fieldwork_delete_all_stale_delete::pending_deletes_survive_delete_all_even_with_synced_commit_opstamp
```

The test:

1. creates and commits a document containing `hello`;
2. records the returned commit opstamp and writes it back into `IndexWriter::committed_opstamp`;
3. queues two uncommitted deletes for `hello`;
4. calls `delete_all_documents()` and verifies the rewind target is the synchronized committed opstamp;
5. commits the clear and synchronizes `committed_opstamp` again;
6. re-adds `hello` after the stamper has reused an opstamp covered by the pending delete range;
7. commits and synchronizes again;
8. verifies the newly added document has nevertheless disappeared.

The test passed, meaning the current defect shape was observed exactly as characterized.

This separates the finding from public issue #2666. A stale writer-level committed opstamp is not required for the pending-delete corruption path.

## Controls

Exact control:

```text
indexer::index_writer::fieldwork_delete_all_stale_delete::delete_all_without_pending_deletes_allows_readd
```

Passed: after a clear with no pending deletes, re-adding the same document leaves one live document.

Exact control:

```text
indexer::index_writer::fieldwork_delete_all_stale_delete::committed_delete_before_delete_all_does_not_delete_readd
```

Passed: a delete already committed before the clear does not later remove the re-added document.

Together these controls isolate the hazardous class to pending/uncommitted delete state crossing the clear boundary.

## Source model

Current `DeleteQueue` has two relevant storage forms:

```text
pending writer Vec<DeleteOperation>
linked immutable Blocks visible to cursors
```

`delete_all_documents()` currently changes neither form.

The exact reproduced sequence uses pending uncommitted deletes. Clearing only the pending writer vector would address that narrow reproduction.

A production repair should not be selected from that observation alone. Existing cursors can cause pending operations to flush into immutable blocks, so the next bounded question is whether an uncommitted delete can cross the clear boundary after it has already entered block history. If yes, the repair needs generation/reset semantics stronger than clearing the pending vector.

Evidence for that broader repair boundary remains `source-read` until a target test executes.

## Relation to public issue #2666

Public issue #2666 describes a distinct defect: `IndexWriter::committed_opstamp` is not updated after commits, so rollback and clear can rewind to the wrong committed boundary.

The characterization here manually repairs that field after every commit and still reproduces stale-delete corruption.

Therefore these should be treated as independent defects:

```text
#2666: wrong rewind boundary
this finding: delete state survives an otherwise-correct rewind boundary
```

Automated upstream contact: prohibited.

Human-performed upstream interaction recorded: none.
