## In simple words

The terminal-settlement defect confirmed on public Tantivy PR 2999 has a small proposal-native repair that executed successfully on the exact PR head.

The repair keeps the persistent-worker architecture. It changes only the failed flush barrier: wait for every old-epoch acknowledgement, preserve the first error, return it after all old-epoch work has settled, and skip next-epoch handoff on any error.

The exact repair regression passed, as did the two existing successful prepare/rollback controls.

Evidence class: `target-executed`.

## Exact target and carrier

Public proposal:

```text
quickwit-oss/tantivy PR 2999
head 039e02e00af3befe4a17e679af6fedfcfdee3d44
```

Owned candidate carrier:

```text
teamleaderleo/tantivy#10
head 2e098fa2fee844de8678dbf40bdf0ab52fc2f753
```

Workflow run:

```text
31587716349
```

Job:

```text
94085313068
```

The job passed exact checkout/base fencing, transient patch/test materialization, Rust setup, formatting, locked-graph build, exact enumeration, the repair discriminator, adjacent controls, and final carrier hygiene.

## Production delta under execution

The public proposal currently fails fast on each old-epoch flush acknowledgement using `?`.

The candidate instead:

1. initializes `first_flush_error = None`;
2. receives every current `worker_flushes` result;
3. converts a disconnected receiver to the existing `WORKER_FLUSH_FAILED` error;
4. retains the first worker/disconnect error;
5. continues receiving later acknowledgements;
6. logs later errors without replacing the primary error;
7. returns the primary error only after all current-epoch acknowledgements have settled;
8. reaches the existing next-epoch handoff only on all-success.

No worker lifecycle, rollback, segment-update, or successful-commit logic is otherwise changed.

## Exact regression

```text
indexer::index_writer::fieldwork_pr2999_settle_all_flushes::prepare_commit_failure_waits_for_every_old_epoch_flush
```

The regression uses the same deterministic failure shape as the characterization but reverses the expected boundary:

- the first old-epoch flush is a synthetic worker error;
- a real writer-status bomb kills new admission;
- a second old-epoch path performs real `index_documents()` publication through the live `SegmentUpdater`;
- that second path is held physically blocked;
- a separate thread calls `prepare_commit()`;
- the test verifies `prepare_commit()` does not return during a 500 ms unresolved-flush window;
- the test then releases the real old-epoch publication;
- publication succeeds;
- the late flush acknowledgement is successfully delivered, proving its receiver stayed alive;
- only then does `prepare_commit()` return;
- the returned error remains the original synthetic primary error.

The exact test passed in 0.52 seconds.

## Adjacent controls

Both existing tests passed:

```text
indexer::index_writer::tests::test_prepare_with_commit_message
indexer::index_writer::tests::test_prepare_but_rollback
```

## Decision

For the terminal-settlement invariant, this persistent-worker candidate supersedes the older join/replace repair if PR 2999 is the architecture under discussion.

The old architecture repair remains valid evidence for current public `main` at its pinned revision, but it should not be proposed as the repair for PR 2999.

This candidate is now concrete enough for a human upstream note if one is desired later. No upstream contact has been made.

Automated upstream contact: prohibited.

Human-performed upstream interaction recorded: none.
