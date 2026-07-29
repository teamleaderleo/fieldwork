# L02: S3 COPY Interrupt Publication Repair

State: `claimed`

Campaign: #96  
Lane issue: #103  
Programme: #16  
Target hub: #11  
Worker: `chatgpt:gpt-5.6-thinking`  
Owned path: `campaigns/0004-duckdb-remote-publication/lanes/L02-interrupt-publication-repair/`  
Upstream contact authorized: `false`

## In simple words

The caller cancels an S3 export and receives `InterruptException`, but DuckDB can still finish the multipart upload and publish the requested object key.

A transparent proxy now proves the order:

1. DuckDB uploads at least one part.
2. The caller interrupts the query.
3. DuckDB checks the final key and receives 404 because the multipart upload is not complete yet.
4. DuckDB uploads remaining buffered parts.
5. DuckDB sends `CompleteMultipartUpload` successfully.
6. The query thread finishes with `InterruptException`.

No object delete and no multipart abort request occurred.

CSV became a valid smaller table. Parquet became a completed object that readers rejected. This is established behavior in the pinned fixture, not only a timing inference.

## Established input from L01

The reproduction uses DuckDB Python 1.5.5, the bundled `httpfs` extension, a pinned MinIO service, generated `range` rows, one execution thread, and a 5,504,856-byte observed multipart part.

After `connection.interrupt()`:

- DuckDB returned `InterruptException`;
- the connection remained reusable;
- the multipart upload was completed rather than retained as incomplete;
- two CSV repeats published exactly 256,000 rows from a requested 50,000,000 rows;
- two Parquet repeats published the same 10,620,166-byte object without terminal magic bytes/footer.

L01 retains the broad and repeated raw provenance.

## Request-order trace

### Pins

- DuckDB research head: `teamleaderleo/duckdb@46d8d13f18e558ff6de44182aaf64ba1ccf686f0`
- DuckDB Python: 1.5.5
- loaded httpfs extension version: `827222f`
- pinned httpfs source: `duckdb/duckdb-httpfs@df92a34d29eb589591adfadba89fa8df874e54ea`
- MinIO release: `RELEASE.2025-07-23T15-54-02Z`
- MinIO SHA-256: `eef6581f6509f43ece007a6f2eb4c5e3ce41498c8956e919a7ac7b4b170fa431`
- transparent proxy: Python `ThreadingHTTPServer` forwarding signed requests unchanged from `127.0.0.1:9002` to MinIO at `127.0.0.1:9000`
- workflow run: `30482062384`
- artifact: `8736071557`
- artifact digest: `sha256:f41813d7e6d94362a2a04992f9d5294ba540d99729943fe44bfd1d3d605b23f9`
- checks: 16 passed, 0 failed

### CSV sequence

The trace recorded:

| Relative time | Event | Result |
|---:|---|---|
| 1.003120 s | create multipart upload | HTTP 200 |
| 1.063228 s | upload part 1 | HTTP 200 |
| 1.085262 s | caller invokes `connection.interrupt()` | one 5,504,856-byte part observed |
| 1.087631 s | `HEAD` requested final key | HTTP 404 |
| 1.102966 s | upload part 2 completes | HTTP 200 |
| 1.122000 s | upload part 3 completes | HTTP 200 |
| 1.125075 s | complete multipart upload | HTTP 200 |
| 1.126111 s | query thread finishes | `InterruptException` |

No DELETE request and no abort-multipart request appeared.

The published CSV object was:

- 14,634,499 bytes;
- multipart ETag with three parts;
- readable as 204,800 rows;
- minimum `0`;
- maximum `204799`;
- checksum `20,971,417,600`, exactly matching the prefix from 0 through 204,799.

The row count differs from the earlier repeated fixture because the proxy changes request timing. The invariant remains the same: a failure result published a valid deterministic prefix at the final key.

### Parquet sequence

The trace recorded:

| Relative time | Event | Result |
|---:|---|---|
| 2.124971 s | create multipart upload | HTTP 200 |
| 2.173395 s | upload part 1 | HTTP 200 |
| 2.179972 s | caller invokes `connection.interrupt()` | one 5,504,856-byte part observed |
| 2.182144 s | `HEAD` requested final key | HTTP 404 |
| 2.203413 s | upload part 2 completes | HTTP 200 |
| 2.206202 s | complete multipart upload | HTTP 200 |
| 2.206734 s | query thread finishes | `InterruptException` |

No DELETE request and no abort-multipart request appeared.

The published Parquet object was:

- 7,974,056 bytes;
- multipart ETag with two parts;
- rejected by DuckDB because final magic bytes/footer were absent.

### What the trace establishes

The final key does not exist when failed-query cleanup checks it. Multipart completion occurs afterward and before the query returns its interruption result.

This proves the publication is not an S3 listing-delay artifact and is not merely an observer race. The upload is deliberately completed through the close path after cancellation.

## Source mechanism

### Core cleanup order

`CopyToFileGlobalState::~CopyToFileGlobalState()` performs best-effort removal of paths it created when the query failed before operator finalization.

A C++ destructor body runs before member destruction. The final object is absent during that body because only an incomplete multipart upload exists. The observed `HEAD` 404 corresponds to this cleanup attempt.

### Writer ownership

`BufferedFileWriter` owns its `FileHandle` through a `unique_ptr`. Its successful `Close()` flushes buffered bytes and calls `handle->Close()`. It has no custom failed-teardown destructor contract.

After the copy global-state destructor body returns, owned writer state is destroyed and releases the S3 file handle.

### S3 destructor completion

The pinned `S3FileHandle` destructor skips `Close()` only while a C++ exception is actively uncaught. At the observed destruction point, the interrupt has already been converted into query state rather than remaining an uncaught C++ exception, so the destructor calls `Close()`.

`S3FileHandle::Close()` calls `FinalizeUpload()`. Multipart `Finalize()` flushes all remaining buffers and sends `CompleteMultipartUpload`.

The proxy trace aligns exactly with this source path.

## Causal conclusion

The cleanup-order hypothesis is now established for the pinned fixture:

1. failed-query cleanup checks/removes the absent final object;
2. writer member destruction follows;
3. S3 handle destruction treats teardown as successful close;
4. remaining buffers are uploaded;
5. multipart completion publishes the partial final object;
6. the caller receives `InterruptException`.

## Candidate repair seams

### A. Abort multipart upload on failed teardown

Add an explicit abort path in `httpfs` and invoke it when the writer is destroyed without successful format finalization.

Advantages:

- prevents publication;
- releases uploaded parts;
- maps directly to S3 multipart semantics;
- avoids upload-then-delete cost and visibility windows.

Risks:

- requires a reliable distinction between successful explicit close and failed-query destruction;
- may affect callers that rely on destructor-driven completion;
- needs abort-error and retry handling.

### B. Complete writer teardown before core path removal

Make `CopyToFileGlobalState` release file states before its best-effort removal loop, so destructor-driven completion happens before deletion.

Advantages:

- narrower core change;
- can restore the post-failure invariant that the final object is absent when deletion succeeds.

Risks:

- deliberately completes and transfers partial data before deleting it;
- creates an observation window;
- delete can fail;
- hidden multipart work remains unresolved when completion fails;
- weaker than native abort semantics.

### C. Make successful S3 completion explicit

Require successful writer finalization to call `Close()` and make unclosed S3 handle destruction abort rather than publish.

Advantages:

- aligns final-key publication with explicit writer success;
- prevents destructor teardown from committing failed work.

Risks:

- requires an audit of every S3 writer and generic file-handle user that may rely on implicit close;
- abandoned multipart uploads still need abort unless destruction performs it.

### D. Add a generic file-handle abort contract

Expose an abort/cancel operation through the core file API and allow remote filesystems to implement native abort behavior.

Advantages:

- represents the semantic distinction directly;
- reusable for other remote writers and side-effecting filesystems.

Risks:

- widest API and compatibility surface;
- should follow evidence that narrower extension-specific ownership is insufficient.

## Current repair ranking

1. **Explicit successful close plus S3 abort on uncommitted destruction.** Best semantic match, subject to an implicit-close audit.
2. **Extension-specific abort invoked from COPY failure teardown.** Narrower operational path if core can communicate failure ownership safely.
3. **Core teardown-before-delete ordering.** Useful containment or regression backstop, but weaker because it publishes then deletes.
4. **Generic file-handle abort API.** Retain only if the extension-specific seams cannot express ownership safely.

## Remaining evidence

1. Locate or add a deterministic source-level test using the httpfs mock server.
2. Audit S3 handle users for implicit destructor completion.
3. Verify whether other ordinary write exceptions follow the same sequence.
4. Implement and test the narrowest viable repair in an owned branch.
5. Test success, interrupt, writer exception, retry, and hard process death.

## Current decision

A held upstream issue packet is now warranted and is retained in this lane.

A code PR draft remains premature until a source-level failing test and implicit-close audit identify the owning component. The evidence already supports issue-level reporting; the next work determines whether the repair belongs primarily to DuckDB core, `httpfs`, or a coordinated change.

No upstream contact occurred.
