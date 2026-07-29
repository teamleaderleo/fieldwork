# L01: S3-Compatible Publication Baseline

State: `claimed`

Campaign: #96  
Programme: #16  
Target hub: #11  
Worker: `chatgpt:gpt-5.6-thinking`  
Owned path: `campaigns/0004-duckdb-remote-publication/lanes/L01-s3-compatible-publication/`  
Upstream contact authorized: `false`

## In simple words

DuckDB uploads remote files differently from local files. Large S3 writes are divided into parts. Those parts can exist without a completed object that readers can open. This lane tests whether cancellation and process death leave hidden uploaded parts behind, whether retry clears them, and whether the final object ever becomes visible before all parts are completed.

## Assignment

For generated CSV and Parquet output through DuckDB Python 1.5.5 and the pinned `httpfs` extension, run a deterministic S3-compatible matrix for completion, interruption, hard process death, same-key retry, and `USE_TMP_FILE true`. Record final objects, multipart uploads, part counts and bytes, reader checksums, connection recovery, and cleanup.

## Pins

- DuckDB fork base: `teamleaderleo/duckdb@2c9e51aa33dd07e928edae66304430aeb038edd7`
- Core extension configuration: `.github/config/extensions/httpfs.cmake`
- Pinned httpfs source: `duckdb/duckdb-httpfs@df92a34d29eb589591adfadba89fa8df874e54ea`
- DuckDB Python: 1.5.5
- MinIO: `RELEASE.2025-07-23T15-54-02Z`
- Runner: Ubuntu 24.04 and Python 3.13
- Owned research PR: https://redirect.github.com/teamleaderleo/duckdb/pull/2

The workflow records the downloaded MinIO binary SHA-256, Python dependency freeze, extension metadata, runner information, and unabridged JSON.

## Source map

### Local temporary publication does not extend to remote paths

`src/planner/binder/statement/bind_copy.cpp` in DuckDB core resolves remote destinations to `use_tmp_file=false` before considering an explicit local temporary-file value. The local `tmp_<name>` and move sequence established in campaign #55 therefore does not provide the remote publication boundary.

### Multipart initialization and visibility

The pinned `httpfs` source creates an `S3MultiPartUpload` whenever an S3 file is opened for writing. The part size is derived from the configured maximum file size and maximum part count, with a minimum S3 part size of 5 MiB.

A multipart upload is initialized with `POST ?uploads`. Full buffers are sent with `PUT ?partNumber=...&uploadId=...`. The final object is created by `POST ?uploadId=...` containing the completed part list.

This implies three separately observable states:

1. upload ID exists;
2. one or more uploaded parts exist;
3. completed object exists.

The probe must not collapse them into one state.

### Finalization and exception boundary

`S3FileHandle::Close()` calls `FinalizeUpload()`, which calls multipart `Finalize()`. Finalization flushes all buffers and completes the multipart upload.

The `S3FileHandle` destructor returns immediately when an exception is currently unwinding. The pinned multipart implementation contains initialization, part upload, and completion requests, but no abort-multipart request. The initial hypothesis is therefore that ordinary interruption after part upload can leave an incomplete multipart upload even though no final object exists.

Hard process death also bypasses close and completion.

### Retry boundary

S3 permits several multipart upload IDs for one object key. A successful retry can complete a new upload and publish a correct object while an older incomplete upload remains separately stored. The lane explicitly records upload IDs before and after retry rather than treating a readable final object as complete cleanup.

## Deterministic workload

Rows come from `range` with:

- `i::BIGINT` as the key;
- two concatenated MD5 values as a fixed-width payload;
- exact row counts and arithmetic checksum;
- one DuckDB execution thread;
- generated data only.

The probe sets:

- `s3_uploader_max_filesize='100MB'`;
- `s3_uploader_max_parts_per_file=20`;
- `s3_uploader_thread_limit=2`.

This selects the 5 MiB minimum part size and allows failure placement after an uploaded part without creating a large retained object.

## Initial hypotheses

H1. While a multipart upload and parts are active for a new key, the completed object remains absent.

H2. Natural completion publishes an exact object only after multipart completion.

H3. Ordinary interruption after at least one uploaded part leaves no final object but retains an incomplete multipart upload.

H4. Hard process death after at least one uploaded part leaves no final object but retains an incomplete multipart upload.

H5. Same-key retry publishes an exact object without removing the older incomplete upload.

H6. `USE_TMP_FILE true` on an S3 path is accepted but does not create a `tmp_` object key because remote option resolution disables the local staging mechanism.

## Acceptance checks

For CSV and Parquet:

- natural output is exact by count and checksum;
- at least one multipart part is observed;
- no completed object is visible while an upload for the new key remains active;
- interruption raises and leaves the connection reusable;
- interruption and process death leave no completed object;
- incomplete multipart uploads remain after both failures;
- same-key retry succeeds and leaves the old upload ID observable;
- remote `USE_TMP_FILE true` succeeds without a `tmp_` key;
- explicit cleanup aborts all retained uploads and deletes all objects.

## Current status

The source map and first probe are committed on the owned fork branch. The MinIO-backed workflow is running. No result is claimed yet.
