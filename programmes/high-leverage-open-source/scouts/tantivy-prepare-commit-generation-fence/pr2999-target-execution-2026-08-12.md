## In simple words

The exact terminal-settlement discriminator against public Tantivy PR 2999 has executed successfully.

PR 2999 changes Tantivy from join-and-replace indexing workers to persistent workers separated by epoch flush acknowledgements. That removes the old partial-replacement-generation mechanism, but the proposal still returns from `prepare_commit()` on the first failed flush acknowledgement.

The owned discriminator confirmed the consequence on the exact public proposal head: the caller can receive the prepare failure while another old-epoch publication is still physically blocked and capable of publishing later through the live `SegmentUpdater`.

Evidence class: `target-executed`.

## Exact execution

Public proposal under test:

```text
quickwit-oss/tantivy PR 2999
head 039e02e00af3befe4a17e679af6fedfcfdee3d44
```

Owned execution carrier:

```text
teamleaderleo/tantivy#6
head 13a8e467e34bd92a30a8244c84b75ae29fbbe13a
```

Workflow run:

```text
31585651203
```

Job:

```text
94078755377
```

The workflow passed every stage: exact-head checkout, base/carrier fence, test-only materialization, Rust setup, locked-graph build, exact test enumeration, discriminator execution, adjacent controls, and final carrier hygiene.

The exact discriminator passed:

```text
indexer::index_writer::fieldwork_prepare_failure_barrier::prepare_commit_error_returns_before_other_epoch_flushes_settle
```

Adjacent controls passed:

```text
indexer::index_writer::tests::test_prepare_with_commit_message
indexer::index_writer::tests::test_prepare_but_rollback
```

## What the passing discriminator proves

The test installs two deterministic old-epoch flush receivers in the proposal's real `worker_flushes` owner.

The first receiver is preloaded with a worker error. A real `IndexWriterStatus` bomb is dropped to reproduce the failed worker's admission-killing consequence.

The second old-epoch publication is held behind a test gate. It uses the target's real `index_documents()`, a real new segment, its delete cursor, and the live `SegmentUpdater`.

`prepare_commit()` returns the first worker error while that second publication is still blocked.

Only after the return does the test release the second publication. `index_documents()` then completes successfully through `SegmentUpdater`.

The late worker cannot deliver its flush acknowledgement because the early-return path dropped the remaining receiver.

Therefore the selected invariant is violated on the exact PR 2999 head:

```text
failed prepare visible to caller
    does not imply
all old-epoch publication authority has settled
```

The failed worker's status bomb still kills new admission. The confirmed gap is specifically terminal settlement of the rest of the old epoch.

## Candidate direction

The smallest proposal-native repair is to change the flush barrier from fail-fast to settle-all:

1. take all current `worker_flushes`;
2. receive every acknowledgement;
3. retain the first worker/disconnect error as the primary error;
4. continue waiting on later acknowledgements;
5. log later errors without replacing the primary error;
6. if any error occurred, return it only after every old-epoch acknowledgement has settled;
7. do not hand any worker a next-epoch task on an error path;
8. preserve the existing next-epoch handoff only on all-success.

Because a failed persistent worker already kills `IndexWriterStatus`, this architecture does not appear to need the old candidate's partial-generation rollback/rebuild machinery for this particular invariant.

This candidate direction remains `source-read` until executed.

## Parallel stale-delete lead

The PR author's automated-review follow-up exposed a separate `delete_all_documents()` problem: pending uncommitted deletes can survive a stamper rewind and later overlap newly reused opstamps.

A current-main owned characterization is being executed separately. Its primary test manually synchronizes `IndexWriter::committed_opstamp` after successful commits, explicitly neutralizing public issue #2666 so the pending-delete defect can be classified independently.

Automated upstream contact: prohibited.

Human-performed upstream interaction recorded: none.
