# Repair Design Review: S3 Publication After Failed Query Teardown

State: `active`

Campaign: #96  
Lane: #103  
Upstream contact authorized: `false`

## Established failure

DuckDB can return an interruption error for `COPY ... TO 's3://...'` while destructor-driven S3 close completes a multipart upload at the requested final key. The request trace establishes that failed-query cleanup checks the absent key before the owned writer is destroyed; S3 handle destruction then uploads remaining buffers and completes the multipart upload.

## Review of the first native-abort experiment

The fork-only native-abort experiment proves that `AbortMultipartUpload` is technically reachable, but it is not a safe repair candidate in its current form.

1. Failed teardown waits without a bound for every active upload worker.
2. A stalled request can therefore turn cancellation cleanup into an indefinite wait.
3. S3 abort is not a one-request guarantee when part uploads are still in flight; bounded waiting, repeated abort, and residual-part verification need their own policy.
4. The experiment branch mixes probes, obsolete failing workflows, and implementation commits, so its complete diff is not reviewable as a narrow repair.

Native abort remains a required lifecycle follow-up, not the first containment patch.

## Clean manual-interrupt containment candidate

The clean owned candidate is retained at:

https://redirect.github.com/teamleaderleo/duckdb/pull/5

It starts at the pinned DuckDB base and contains one HTTPFS patch plus one focused workflow.

The candidate preserves successful implicit S3 close, but skips destructor-driven `Close()` while the owning client remains manually interrupted. Its native fixture covers:

1. destruction returning before a blocked multipart-part response is released;
2. interrupted SQL `COPY` returning an error without multipart completion;
3. successful implicit destruction still completing multipart upload.

### Self-review corrections

- The first patch revisions had malformed hunk counts and produced no code result.
- The first compiling revision inserted a helper inside another test function and failed compilation.
- Direct handle controls initially supplied a second `ClientContextFileOpener`; the client-specific `OpenerFileSystem` already injects that opener and rejects a second one. The controls now use the same opener path as production `COPY`.
- Upload workers own a shared multipart-upload object containing the filesystem, HTTP input, path, and configuration they use. The direct destruction control does not rely on dereferencing the destroyed S3 handle.

The current exact-head result remains pending. No passing claim is recorded here.

## Scope limit: query deadlines

`ClientContext::IsInterrupted()` represents manual interruption. `max_execution_time` throws `InterruptException` from a deadline check without setting that manual interrupt state.

Therefore the clean candidate must be described as **manual-interrupt containment only** until an independent timeout matrix says otherwise. A pinned MinIO/proxy deadline trace is queued on the research branch.

## Explicit-close audit

The core file API exposes `FileHandle::Close()` explicitly, and the base `FileHandle` destructor is empty. S3 multipart commit from `S3FileHandle::~S3FileHandle()` is extension-specific rather than a general core destructor guarantee.

Successful writers reviewed so far:

- CSV finalization explicitly closes its writer.
- Parquet finalization writes the footer, calls `Close()`, and resets the writer.
- `EXPORT DATABASE` metadata uses a raw file handle, writes `schema.sql` or `load.sql`, and then resets the handle without an explicit close. This is the historical success case that motivated destructor-driven S3 completion.

This makes a second repair direction plausible:

1. require explicit S3 close for successful publication;
2. add explicit close to the export metadata writer;
3. make unclosed S3 destruction non-publishing;
4. add native success controls for CSV, Parquet, and `EXPORT DATABASE`.

Advantages:

- covers manual interrupt, query deadline, worker error, and other captured query failures without guessing their source;
- aligns multipart completion with an explicit success operation;
- avoids adding a query-failure API solely for one filesystem.

Risk:

- external or extension code may rely on the historical S3-only implicit-close behavior even though the base file API does not promise it.

## Core failed-teardown signal

`CopyToFileGlobalState` already tracks `initialized` and `finalized`. Its destructor explicitly treats `initialized && !finalized` as a query failure before finalization.

`ClientContext::EndQueryInternal` also receives `success=false` before it resets the active query and destroys executor-owned operator state.

A narrower compatibility-preserving alternative is therefore possible:

1. set an atomic query-teardown state before active-query destruction;
2. expose whether teardown is ending in failure;
3. let S3 handle destruction skip publication for any failed query, not only manual interruption;
4. clear the state immediately after active-query destruction.

Advantages:

- preserves successful implicit close for existing callers;
- covers manual interruption, deadline failure, worker error, and ordinary captured query errors;
- uses the actual query outcome rather than inferring it from an exception or timeout clock.

Risks:

- adds a cross-component core API for a filesystem teardown concern;
- needs tests for success, failure, abandoned results, connection destruction, and concurrent upload tasks;
- does not clean retained multipart uploads.

## Current ranking

1. **Core failed-teardown signal plus non-publishing S3 destruction.** Best compatibility/coverage balance if the transient state is reliable during all writer destruction.
2. **Explicit successful close; unclosed S3 destruction does not publish.** Cleanest semantic contract, subject to a broader caller audit and compatibility decision.
3. **Manual-interrupt containment.** Smallest immediate patch, but incomplete for deadlines and other captured failures.
4. **Native multipart abort during failed teardown.** Required eventually, but only after bounded waiting and residual-part policy are specified.
5. **Finalize-then-delete ordering.** Containment backstop only; it transfers and briefly publishes failed output before deletion, and deletion can fail.

## Next evidence

1. finish the clean exact-head native build and runtime controls;
2. finish the independent `max_execution_time` trace;
3. prototype the transient failed-teardown state in an owned branch if timeout reproduces;
4. run explicit-close compatibility controls for CSV, Parquet, and `EXPORT DATABASE`;
5. keep multipart garbage collection as a separate bounded lifecycle lane.

No upstream contact occurred.
