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

The caller cancels an S3 export and receives `InterruptException`, but DuckDB can still finish the multipart upload and publish the requested object key. The CSV object can look like a valid smaller dataset. The Parquet object can exist while being unreadable.

This lane will identify the exact teardown order, add a source-level failing test, and decide whether the safe repair is multipart abort, cleanup reordering, explicit successful close, or a broader file-handle cancellation contract.

## Established input from L01

The reproduction uses DuckDB Python 1.5.5, the bundled `httpfs` extension, a pinned MinIO service, generated `range` rows, one execution thread, and a 5,504,856-byte observed multipart part.

After `connection.interrupt()`:

- DuckDB returned `InterruptException`;
- the connection remained reusable;
- the multipart upload was completed rather than retained as incomplete;
- two CSV repeats published exactly 256,000 rows from a requested 50,000,000 rows;
- two Parquet repeats published the same 10,620,166-byte object without terminal magic bytes/footer.

Raw provenance and the compact summary are retained in L01.

## Initial causal hypothesis

The current source suggests this order:

1. `CopyToFileGlobalState` enters failed-query destruction and tries to remove the final path.
2. The object key is absent because the multipart upload is incomplete.
3. The destructor body finishes; owned format-writer state is then destroyed.
4. `BufferedFileWriter` releases its S3 `FileHandle`.
5. `S3FileHandle::~S3FileHandle()` calls `Close()` because no C++ exception is uncaught at that destruction point.
6. `Close()` calls `FinalizeUpload()`, which completes the multipart upload.
7. The final partial object appears after the earlier removal attempt.

This is strongly supported by source and outcome, but the lane will retain it as a hypothesis until request ordering or a source-level test proves the sequence.

## Candidate repair seams

### A. Abort multipart upload on failed teardown

Add an explicit abort path in `httpfs` and invoke it when the writer is destroyed without successful format finalization.

Advantages:

- prevents publication;
- releases uploaded parts;
- maps directly to S3 multipart semantics.

Risks:

- requires a reliable distinction between successful implicit close and failed-query destruction;
- may affect callers that rely on destructor-driven completion;
- needs retry and abort-error handling.

### B. Complete writer teardown before core path removal

Make `CopyToFileGlobalState` release file states before its best-effort removal loop, so any destructor-driven completion happens before deletion.

Advantages:

- narrower core change;
- can restore the post-failure invariant that the final object is absent.

Risks:

- still completes and transfers a partial object before deleting it;
- creates a possible observation window;
- does not release hidden multipart work when completion fails;
- remote delete itself can fail.

### C. Make successful S3 completion explicit

Require successful writer finalization to call `Close()` and make unclosed S3 handle destruction abort or abandon rather than publish.

Advantages:

- aligns publication with explicit success;
- prevents destructor teardown from silently committing work.

Risks:

- requires an audit of all S3 writers and generic file-handle users that may depend on implicit close;
- abandoned uploads still need abort.

### D. Add a generic file-handle abort contract

Expose an abort/cancel operation through the core file API and allow remote filesystems to implement native abort behavior.

Advantages:

- represents the semantic distinction directly;
- reusable for other remote writers.

Risks:

- widest API and compatibility surface;
- premature unless narrower options fail.

## Planned evidence

1. Capture S3 request order around interruption.
2. Locate or add a deterministic httpfs mock-server fixture.
3. Reproduce both CSV and Parquet without Python timing dependence where feasible.
4. Assert caller error, final-key absence, multipart state, and connection reuse.
5. Test natural success and hard process death as controls.
6. Implement the narrowest viable repair in an owned branch.
7. Hold any upstream issue or PR packet for explicit human approval.

## Current decision

An upstream issue draft is warranted once the causal trace and source-level fixture are durable.

A code PR draft is premature until the lane determines which component owns abort semantics and verifies that successful implicit-close behavior is preserved or intentionally replaced.
