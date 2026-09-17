# L01: S3-Compatible Publication Baseline

State: `complete`

Campaign: #96  
Programme: #16  
Target hub: #11  
Worker: `chatgpt:gpt-5.6-thinking`  
Owned path: `campaigns/0004-duckdb-remote-publication/lanes/L01-s3-compatible-publication/`  
Upstream contact authorized: `false`

## In simple words

DuckDB writes large S3 objects as multipart uploads. The final object key normally appears only when DuckDB completes the multipart upload.

Two failure modes behaved very differently:

- killing the process left no final object, but it left uploaded multipart parts that still consumed storage;
- calling `connection.interrupt()` after a part was uploaded returned `InterruptException` **and then published a final object anyway**.

For CSV, the published object was a readable, internally consistent prefix: 256,000 rows from a requested 50,000,000 rows. A consumer could mistake it for a successful smaller export. For Parquet, the published key contained a file without terminal magic bytes and could not be read.

The interrupt result repeated twice for each format. This is an actual correctness issue candidate. It is promoted to repair lane #103. No upstream contact occurred.

## Question answered

For generated single-file CSV and Parquet output through DuckDB Python 1.5.5 and the bundled `httpfs` extension:

- When does a completed S3 object become visible?
- What remains after manual interruption or hard process death?
- Does same-key retry clean older multipart work?
- Does remote `USE_TMP_FILE true` create a staging object?
- Can a failed statement still publish a final object?

Production AWS S3, other S3-compatible implementations, partitioned output, rotated output, per-thread output, and concurrent writers remain outside this lane.

## Pins and provenance

- DuckDB fork base: `teamleaderleo/duckdb@2c9e51aa33dd07e928edae66304430aeb038edd7`
- Final owned research head: `teamleaderleo/duckdb@98529427db7e99c2e4f7268c6c579216893a4458`
- Core extension configuration: `.github/config/extensions/httpfs.cmake`
- Pinned httpfs source: `duckdb/duckdb-httpfs@df92a34d29eb589591adfadba89fa8df874e54ea`
- Loaded httpfs extension version reported by DuckDB: `827222f`
- DuckDB Python: 1.5.5
- MinIO: `RELEASE.2025-07-23T15-54-02Z`
- MinIO commit: `7ced9663e6a791fef9dc6be798ff24cda9c730ac`
- MinIO binary SHA-256: `eef6581f6509f43ece007a6f2eb4c5e3ce41498c8956e919a7ac7b4b170fa431`
- Runner: Ubuntu 24.04, Linux 6.17 Azure x86_64, Python 3.13.14
- DuckDB execution threads: 1
- Owned research PR: https://redirect.github.com/teamleaderleo/duckdb/pull/2

Broad matrix:

- workflow run: `30480334339`
- artifact: `8735370197`
- artifact digest: `sha256:af0a35335a3ca4a59337d69ddf3a502874d6908ce283b5b696666e95d7dd16ff`
- acceptance summary: 42 passed, 8 failed; the failed expectations exposed the interrupt-publication result and two observer limitations described below.

Focused repeat matrix:

- workflow run: `30481103612`
- artifact: `8735732540`
- artifact digest: `sha256:0e8fbb05de6ae237fe5861a158d9c9f478e053de13358667c2a733f4f8cb8bd9`
- acceptance summary: 50 passed, 10 failed; eight failures came from an unsupported attempted early-flush option, while two expected readable-prefix checks deliberately failed for the repeated incomplete Parquet objects.

## Source map

### Remote destinations do not use local temporary-file publication

`src/planner/binder/statement/bind_copy.cpp` in DuckDB core resolves remote destinations to `use_tmp_file=false` before applying an explicit local temporary-file value. The local `tmp_<name>` and move sequence established in campaign #55 therefore does not provide the S3 publication boundary.

The observed `COPY ... (USE_TMP_FILE true)` cases succeeded but created no `tmp_` object key. They followed the same direct multipart path.

### Multipart states

The pinned `httpfs` source creates an `S3MultiPartUpload` whenever an S3 file is opened for writing. The configured part size is derived from maximum file size and maximum part count, with a minimum of 5 MiB.

`src/s3_multi_part_upload.cpp` separates these states:

1. initialize upload with `POST ?uploads`;
2. upload a part with `PUT ?partNumber=...&uploadId=...`;
3. complete the upload with `POST ?uploadId=...` and the part list.

An upload ID and uploaded parts are hidden from ordinary object readers until step 3 creates the completed key.

### Close and destructor behavior

`S3FileHandle::Close()` calls `FinalizeUpload()`, which calls multipart `Finalize()`. Finalization flushes remaining buffers and completes the multipart upload.

`S3FileHandle::~S3FileHandle()` skips `Close()` only when a C++ exception is currently uncaught. Otherwise it calls `Close()` as a best-effort destructor action.

The multipart implementation contains initialization, part upload, and completion requests. The mapped source has no abort-multipart request.

### Core cleanup ordering hypothesis

`CopyToFileGlobalState::~CopyToFileGlobalState()` performs best-effort removal of paths it created when the query failed before operator finalization.

That destructor body runs before its owned members are destroyed. During an incomplete multipart upload, the final object does not yet exist, so a removal attempt against the final key has nothing to delete. Later member destruction releases the format writer and its S3 file handle. The S3 file-handle destructor can then call `Close()` and complete the partial multipart upload.

`BufferedFileWriter` owns its `FileHandle` through a `unique_ptr`. Its explicit `Close()` flushes and closes on successful writer finalization, but it has no custom destructor that distinguishes successful close from failed-query teardown.

This ordering matches the observed result:

1. `connection.interrupt()` reports failure;
2. no incomplete upload remains;
3. a multipart ETag appears at the final key;
4. the final object contains only work produced before interruption.

The next lane must capture the exact request order or a source-level regression before this causal hypothesis is promoted from strongly supported to established.

## Deterministic workload

Rows came from `range` with:

- `i::BIGINT` as the key;
- two concatenated MD5 values as a fixed-width payload;
- exact row counts and arithmetic checksums;
- one execution thread;
- no private data, network source data, random seed, or clock-derived values.

The probe set:

- `s3_uploader_max_filesize='100MB'`;
- `s3_uploader_max_parts_per_file=20`;
- `s3_uploader_thread_limit=2`.

This selected the 5 MiB minimum part size. Failure placement waited until the observer saw at least one uploaded part of 5,504,856 bytes.

## Findings

### 1. Successful multipart output was exact

Natural completion produced:

| Format | Rows | Checksum | Object bytes | ETag |
|---|---:|---:|---:|---|
| CSV | 400,000 | 79,999,800,000 | 28,688,900 | multipart, 6 parts |
| Parquet | 400,000 | 79,999,800,000 | 8,648,130 | multipart, 2 parts |

Fresh DuckDB readers returned the exact row count, checksum, minimum, and maximum.

The observer saw upload IDs before final objects. One CSV poll briefly observed the completed object while the immediately adjacent multipart listing still returned the upload. That is a polling overlap at completion, not evidence that S3 readers saw part data as a completed object.

### 2. Hard process death left hidden multipart storage, not a final object

For both CSV and Parquet, the writer process was killed after one 5,504,856-byte part was visible.

After death:

- the final object key was absent;
- one incomplete multipart upload remained;
- the upload retained the completed first part;
- ordinary object listing did not expose those bytes.

A same-key retry produced an exact 2,000-row object with checksum 1,999,000. The older upload ID and its part remained after retry.

**Consequence:** successful retry does not prove storage cleanup. Applications or operators need an abort/lifecycle policy for abandoned multipart uploads after process death.

### 3. Manual interruption published a final object despite `InterruptException`

The broad matrix waited until at least one multipart part existed, then called `connection.interrupt()`.

For both formats:

- DuckDB raised `InterruptException`;
- the same connection remained usable;
- no incomplete multipart upload remained;
- a completed multipart object existed at the requested final key.

The broad run did not read those objects before retry, so a focused matrix repeated the placement twice per format and inspected the final object immediately.

### 4. CSV interruption produced a deceptive valid prefix

Both focused CSV repeats produced exactly the same result:

| Repeat | Interrupt trigger | Final bytes | ETag | Reader result |
|---|---:|---:|---|---|
| 1 | after first 5,504,856-byte part, 0.127 s | 18,320,899 | multipart, 4 parts | 256,000 rows |
| 2 | after at least two parts, 0.407 s | 18,320,899 | multipart, 4 parts | 256,000 rows |

The requested source had 50,000,000 rows. The published object contained:

- minimum `0`;
- maximum `255999`;
- checksum `32,767,872,000`, exactly equal to the arithmetic checksum for rows 0 through 255,999.

The file therefore looked like a normal, complete CSV dataset with no inherent signal that the statement had failed or that 49,744,000 rows were missing.

**Consequence:** a caller can receive a failure while a downstream consumer independently accepts a smaller valid table from the final key.

### 5. Parquet interruption published an invalid completed object

Both focused Parquet repeats produced exactly the same result:

| Repeat | Interrupt trigger | Final bytes | ETag | Reader result |
|---|---:|---:|---|---|
| 1 | after first 5,504,856-byte part, 0.343 s | 10,620,166 | multipart, 2 parts | missing final magic bytes/footer |
| 2 | after first 5,504,856-byte part, 0.458 s | 10,620,166 | multipart, 2 parts | missing final magic bytes/footer |

The object store considered each multipart upload complete and exposed the requested key, while DuckDB's Parquet reader rejected the contents.

**Consequence:** object existence and multipart completion do not imply format completeness after a cancelled statement.

### 6. Remote `USE_TMP_FILE true` did not create a staging key

For both successful CSV and Parquet cases:

- the option was accepted;
- no `tmp_` object key or upload was observed;
- the requested final key used direct multipart upload;
- the resulting object was exact.

This matches the core option-resolution path that disables local temporary-file mode for remote destinations.

## Hypothesis outcomes

| Hypothesis | Outcome |
|---|---|
| Active multipart parts remain hidden until completion | supported for the controlled observations |
| Natural completion publishes exact objects | supported |
| Ordinary interruption leaves no object and an incomplete upload | rejected; it completed and published a partial object |
| Hard process death leaves no object and an incomplete upload | supported |
| Same-key retry removes an older incomplete upload | rejected; older upload ID remained |
| Remote `USE_TMP_FILE true` creates local-style staging | rejected; option was accepted but no staging key appeared |
| A failed S3 `COPY` cannot publish the final key | rejected in four focused repeats |
| CSV and Parquet have the same consumer consequence | rejected; CSV was deceptively readable, Parquet was visibly invalid |

## Failed trials and corrections

### Empty-key bucket snapshot

The first broad run executed its cases and then failed while taking a bucket-wide snapshot because the helper attempted `HEAD` with an empty key. V2 corrected only that helper and retained the workload.

### Broad acceptance assumptions

The broad V2 run passed 42 of 50 checks. Six consequential failures showed that interrupted output was completed rather than left as an incomplete multipart upload. The remaining two were observer limitations: a completion-time listing overlap for CSV and a missed short-lived Parquet part before a two-part object completed.

### First focused cleanup helper

The first focused run reused the old empty-key helper after its first case. The corrected entrypoint patched only bucket-wide cleanup inspection.

### Unsupported early-flush option

The focused matrix attempted `BATCH_SIZE_BYTES '6MB'` as a distinguishing control. DuckDB 1.5.5 rejected that option for both CSV and Parquet before execution. Those eight case-level acceptance failures are probe-contract failures and provide no evidence about interrupt behavior.

The valid default-mode cases still repeated the interrupt-publication result twice for each format.

## Decision

L01 is complete.

The evidence supports an actual correctness issue candidate:

> An interrupted DuckDB S3 `COPY` can return `InterruptException` while completing a multipart upload at the requested final key. CSV may be a valid-looking prefix; Parquet may be an unreadable completed object.

This result is stronger than a documentation-only gap. It warrants a held upstream issue draft now and a code PR only after a source-level failing regression identifies a safe repair seam.

Repair lane #103 owns that next step. It will capture request ordering, test cleanup semantics, compare multipart abort against cleanup reordering, and prepare a fork-only patch or precise issue packet. Upstream contact remains unauthorized.

## Ranked continuation

1. **Interrupt publication repair — issue #103.** Produce a source-level failing regression and causal request trace. Highest priority.
2. **Abort-versus-delete semantics.** Determine whether failed-query teardown should abort multipart uploads, complete then delete, or expose a generic file-handle abort contract.
3. **Process-death multipart lifecycle.** Document or automate stale-upload cleanup without confusing retry success with cleanup success.
4. **Provider compatibility.** Repeat the established fixture against another owned S3 implementation or a tightly bounded AWS-compatible environment only when credentials and cost controls are explicitly authorized.
5. **Partitioned and rotated remote output.** Determine directory/prefix completion semantics after the single-object interrupt defect is isolated.

## Artifacts

Owned fork code:

- `tools/fieldwork/issue96_remote_publication_probe.py` — retained broad V1 and initial expectations;
- `tools/fieldwork/issue96_remote_publication_probe_v2.py` — corrected broad entrypoint;
- `tools/fieldwork/issue96_interrupt_phase_probe.py` — retained focused V1 cleanup failure;
- `tools/fieldwork/issue96_interrupt_phase_probe_v2.py` — corrected focused entrypoint;
- `tools/fieldwork/requirements-issue96.txt`;
- `.github/workflows/fieldwork-issue96-remote-publication.yml`.

Durable summaries are stored under `artifacts/results/`. The workflow artifacts retain the unabridged JSON, MinIO log and version, MinIO binary digest, and Python dependency freeze.
