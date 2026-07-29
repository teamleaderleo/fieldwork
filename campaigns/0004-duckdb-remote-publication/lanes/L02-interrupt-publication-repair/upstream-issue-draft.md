# Held upstream issue draft

Status: `held`  
Upstream contact authorized: `false`  
Likely routing: DuckDB core and/or `httpfs`; decide after source-level fixture and ownership review.

## Candidate title

`COPY TO S3 can publish a partial final object after returning InterruptException`

## Draft body

### Description

Interrupting a multipart `COPY` to an S3-compatible endpoint can return `InterruptException` to the caller while DuckDB completes the multipart upload and publishes an object at the requested final key.

The resulting object depends on the format:

- CSV can be a readable, internally consistent prefix of the requested dataset;
- Parquet can be a completed object whose contents are missing terminal magic bytes/footer and cannot be read.

This means the caller observes failure while an independent consumer can observe a final object that was created after cancellation.

### Reproduction environment

- DuckDB Python: 1.5.5
- loaded `httpfs` extension version: `827222f`
- corresponding public `httpfs` source pin: `df92a34d29eb589591adfadba89fa8df874e54ea`
- Python: 3.13.14
- Ubuntu 24.04, Linux x86_64
- one DuckDB execution thread
- S3-compatible endpoint: MinIO `RELEASE.2025-07-23T15-54-02Z`
- uploader settings:
  - `s3_uploader_max_filesize='100MB'`
  - `s3_uploader_max_parts_per_file=20`
  - `s3_uploader_thread_limit=2`

The workload uses generated rows only:

```sql
COPY (
    SELECT
        i::BIGINT AS i,
        md5(i::VARCHAR) || md5((i + 1)::VARCHAR) AS payload
    FROM range(50000000) t(i)
) TO 's3://bucket/result.csv' (
    FORMAT CSV,
    HEADER true
);
```

Run the statement on one thread, observe the S3 multipart upload, and call `connection.interrupt()` after at least one 5 MiB part has completed.

Equivalent behavior was reproduced with `FORMAT PARQUET, COMPRESSION ZSTD`.

### Actual behavior

For both formats:

1. DuckDB created a multipart upload.
2. At least one part completed.
3. The client called `connection.interrupt()`.
4. DuckDB checked the requested final key and received HTTP 404.
5. DuckDB uploaded remaining buffered parts.
6. DuckDB sent `CompleteMultipartUpload` and received HTTP 200.
7. The query returned `InterruptException`.
8. The connection remained reusable.

No `DeleteObject` and no `AbortMultipartUpload` request was sent.

A transparent request trace recorded the following CSV sequence:

```text
create multipart      200
upload part 1         200
connection.interrupt()
HEAD final key        404
upload part 2         200
upload part 3         200
complete multipart    200
query returns InterruptException
```

The published CSV contained 204,800 rows from the requested 50,000,000 rows. Its key range and arithmetic checksum exactly matched rows 0 through 204,799, so the object was a valid-looking prefix.

Two additional runs without the tracing proxy each published the same 256,000-row prefix.

The traced Parquet object was 7,974,056 bytes with a two-part multipart ETag. DuckDB rejected it because final magic bytes/footer were absent. Two additional runs reproduced the same incomplete-format result.

### Expected behavior

When `COPY` returns `InterruptException`, DuckDB should avoid publishing a new final object for that failed statement.

For multipart S3 output, failed-query teardown should either:

- abort the incomplete multipart upload; or
- otherwise guarantee that the final key is absent after failure.

A completed partial object at the requested key is especially risky for CSV because the file can be readable and provide no inherent indication that most source rows are missing.

### Source-level observation

The observed request order matches the following teardown sequence:

1. `CopyToFileGlobalState` performs best-effort removal while the final object is still absent.
2. Owned writer members are destroyed after the destructor body.
3. `S3FileHandle` destruction calls `Close()` when no C++ exception is currently uncaught.
4. `Close()` calls `FinalizeUpload()` and completes the multipart upload.

The mapped multipart implementation has initialization, part upload, and completion requests, but no abort-multipart request.

### Controls

- Natural CSV and Parquet completion produced exact row counts and checksums.
- Hard process death after one uploaded part left no final object and retained an incomplete multipart upload.
- Same-key retry published an exact new object but did not remove the older incomplete upload.
- `USE_TMP_FILE true` did not create a staging object for the remote path.
- Explicit cleanup after each controlled case removed all retained objects and multipart uploads.

### Reproducibility

The interrupt-publication behavior was observed in:

- one broad CSV case;
- one broad Parquet case;
- two focused CSV repeats;
- two focused Parquet repeats;
- one request-traced CSV case;
- one request-traced Parquet case.

### Open repair question

The narrowest repair may belong in one or both of these areas:

- `httpfs`: abort an uncommitted multipart upload when a file handle is destroyed without successful explicit close;
- DuckDB core: ensure failed `COPY` teardown does not attempt removal before writer destruction can publish the object.

A source-level regression and audit of callers that rely on destructor-driven S3 completion should precede a code change.

---

## Fieldwork notes

Do not submit this draft until a human explicitly authorizes upstream contact.

Before submission:

- replace source-pin shorthand with the target repository's preferred version information;
- attach or link a minimal source-level regression if available;
- decide whether the report belongs in DuckDB core or `httpfs`;
- omit MinIO implementation claims beyond the controlled S3-compatible reproduction;
- preserve the distinction between established request order and proposed repair ownership.
