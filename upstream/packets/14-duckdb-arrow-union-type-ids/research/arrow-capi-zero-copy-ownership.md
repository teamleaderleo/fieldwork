# DuckDB Arrow C API projected-column root ownership

Date: 2026-08-06

## Status

`CONFIRMED DEFECT — exact expected-negative reproduced; characterization carrier closed without merge`

No public write or public-upstream contact is authorized by this note.

## Exact evidence

Private characterization:

- PR: `teamleaderleo/duckdb#29` — closed without merge;
- immutable base: `58c019320e250a7b369efd756f84c6dfd68bedcb`;
- exact head: `b2017ce61d9c39c5faee8899bc4c50ca71a46bd0`;
- focused run/job: `31102985877` / `92620944568` — success;
- artifact: `8969221973`;
- artifact digest: `sha256:036913d4415c1473c7f1a66ebf582330f59c58f4b9e54c9f49db2db698e3861d`;
- artifact name: `fieldwork-capi-arrow-multicolumn-ownership`.

The carrier changed exactly one workflow, one CMake registration, and one focused test. It contained no production source.

## Corrected diagnosis

The initial broad suspicion—release during ordinary per-column conversion—was too strong. Generic Arrow conversion attaches each column's copied `ArrowArrayWrapper` to the output vector through auxiliary data, so the complete source `DataChunk` remains safe while all columns remain alive.

The real defect is **projected later-column lifetime**.

`duckdb_data_chunk_from_arrow` currently performs one root-wrapper copy per output column:

1. column zero copies the root while its release callback is non-null;
2. the caller's root release callback is nulled;
3. later columns copy the already-moved root and therefore receive wrappers whose `release` is null;
4. each output vector retains only its own per-column wrapper.

As a result, only column zero's wrapper is the real owner of the complete Arrow root. A reference to column two can outlive the original source chunk, but it retains only a no-op wrapper. Destroying the source chunk destroys column zero's real owner and releases the Arrow root while column two still aliases its buffer.

## Discriminating fixture

The expected-negative test:

1. creates two INT32 Arrow children;
2. installs a root release callback that increments a counter and overwrites column two with `-9999`;
3. converts through `duckdb_data_chunk_from_arrow`;
4. takes `Vector::Ref` to column two;
5. destroys the original output chunk while the later-column reference remains alive;
6. reads the surviving reference.

The existing C API Arrow conversion control passed first:

```text
All tests passed (10020 assertions in 1 test case)
```

The focused characterization then reproduced both exact signatures:

```text
root release count after source chunk destroy=1
surviving second output=-9999,-9999,-9999
```

The test expected release count zero and values `21,22,23` until the surviving projection was destroyed. Both assertions failed exactly as predicted.

## User-visible impact class

Any path that retains or projects a later Arrow-backed column while dropping the original multi-column chunk can observe:

- dangling zero-copy buffers;
- corrupted values;
- use-after-free with producers that actually free memory;
- failures that depend on projection order because column zero accidentally owns the root.

The deterministic test poisons rather than frees memory, so the proof does not depend on allocator behavior or an uncontrolled crash.

## Required ownership invariant

The complete incoming `ArrowArray` root must have **one shared owner**. Every DuckDB vector or nested vector that aliases any part of that root must retain the same shared owner, independent of column index or projection order.

Correct behavior:

- release count remains zero while any Arrow-backed output alias survives;
- dropping column zero does not release data used by column N;
- release count becomes one after the final alias is destroyed;
- no wrapper copy with a null release callback is treated as independent ownership.

## Preferred repair architecture

Use one transactional shared root owner:

1. validate root/schema structure before ownership transfer;
2. create one shared `ArrowArrayWrapper` outside the per-column loop;
3. temporarily disarm its release callback while conversion is in progress;
4. assign that same `shared_ptr` to every column's `ArrowArrayScanState`;
5. convert all columns;
6. on success, commit the original root release callback into the shared owner and null the caller's callback;
7. on failure, leave caller ownership intact and destroy only disarmed temporary references.

This architecture also supports:

- schema/runtime structural validation before dereference;
- failure-atomic ownership when no `DataChunk` is returned;
- dictionary, run-end, string, list, and extension aliases through the same root owner.

The detailed design is in [`arrow-capi-shared-root-repair-design.md`](arrow-capi-shared-root-repair-design.md).

## Repair tests

A repair must turn the confirmed expected-negative into a positive test and add at least:

1. column two survives source-chunk destruction;
2. column order reversed;
3. three columns, retaining only the last;
4. fixed-width and string combinations;
5. dictionary and run-end aliases;
6. nested list/struct child;
7. release count exactly one after final alias destruction;
8. validation failure leaves caller ownership intact;
9. later-column conversion failure leaves caller ownership intact;
10. success nulls caller release exactly once.

## Relationship to other active lanes

- PR #30 characterizes runtime schema/array child-count agreement.
- `arrow-capi-failure-ownership.md` covers ownership on conversion errors.
- `arrow-capi-shared-root-repair-design.md` unifies all three without broadening into Arrow stream or type-specific work.

## Disposition

The defect is established. The next source action should be one private repair carrier on exact current DuckDB main, preferably after the schema/array characterization resolves so validation ordering and ownership transfer can be repaired coherently.
