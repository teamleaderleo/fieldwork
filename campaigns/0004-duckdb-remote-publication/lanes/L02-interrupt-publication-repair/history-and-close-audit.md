# S3 Close History and Ownership Audit

State: `active`

Lane: #103  
Campaign: #96  
Upstream contact authorized: `false`

## Why this file exists

The interrupt defect cannot be repaired safely by deleting `S3FileHandle`'s destructor-driven `Close()` without checking why that close was added and which successful writers still depend on it.

## History

### Original multipart write contract

DuckDB PR #3069 introduced S3 multipart writes. Its stated contract was that `FileSync` or `Close` finalizes the S3 file and prevents further writes.

### Destructor close added for successful exports

DuckDB PR #9758 added `S3FileHandle::~S3FileHandle() { Close(); }` because some successful S3 file handles were discarded without an explicit close. The motivating failure was `EXPORT DATABASE` producing table files but omitting `schema.sql` and `load.sql` because those small multipart uploads were never completed.

### Conditional close added for failed queries

DuckDB issue #12038 reported that an unrelated query error could still publish incomplete CSV/JSON or footerless Parquet to S3. PR #12031 changed the destructor to skip `Close()` while a C++ exception is actively unwinding and to suppress close exceptions.

The merged guard is:

```cpp
if (Exception::UncaughtException()) {
    return;
}
try {
    Close();
} catch (...) {
}
```

The issue-103 interruption path falls outside that guard. DuckDB has already captured the interruption in query state by the time writer members are destroyed, so no C++ exception is actively unwinding and the destructor completes the multipart upload.

## Current explicit-close audit

### CSV COPY

`WriteCSVFinalize` appends any suffix or final newline and calls `global_state.writer.Close()`. Successful CSV `COPY TO` does not need destructor completion.

### Parquet COPY

`ParquetWriter::Finalize` writes metadata, footer length, terminal magic bytes, then calls `writer->Close()` and releases the writer. Successful Parquet `COPY TO` does not need destructor completion.

### EXPORT DATABASE metadata files

`PhysicalExport::WriteStringStreamToFile` currently opens a generic file handle, writes `schema.sql` or `load.sql`, and calls `handle.reset()` without an explicit `Close()`. On S3 this still relies on destructor-driven completion.

## Consequence for repair selection

A blanket removal of destructor `Close()` would repair the observed cancellation publication but would reintroduce the successful-export failure that motivated PR #9758.

The viable directions are narrower:

1. add explicit `Close()` to successful generic writers such as `WriteStringStreamToFile`, complete the audit, then make unclosed S3 destruction non-publishing;
2. add an explicit committed/aborted state to the S3 handle or multipart upload, where successful close commits and failed teardown aborts;
3. let COPY failure teardown explicitly abort the remote handle while preserving destructor completion for unrelated legacy users;
4. use teardown-before-delete only as containment, since it still uploads and briefly publishes partial data before deletion.

## Source-level regression fixture

An owned extension patch adds a mock-server gate on the first multipart part and a C++ test that:

1. starts a large CSV `COPY TO S3`;
2. blocks the first multipart part response;
3. invokes `Connection::Interrupt()`;
4. releases the part;
5. asserts an interruption result and connection reuse;
6. asserts that failed teardown sends no successful multipart-complete POST.

The first build attempt failed while applying a malformed hand-written unified diff. That is retained as a fixture-authoring failure and carries no DuckDB conclusion. The patch was regenerated with verified hunk counts and rerun without changing the workload or expected invariant.

## Current decision

The historical evidence strengthens the need for an explicit success-versus-abort lifecycle. It also shows that the defect is a gap in the 2024 conditional-destructor fix rather than an unrelated new mechanism.

No upstream contact occurred.
