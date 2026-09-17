# Publication and cancellation contract

Issue: #122

Status: authoritative guidance synthesis and executable expectations

Retrieved: 2026-07-30

Upstream contact authorized: false

## Purpose

A query cancellation is not a single storage event. It can stop computation while a writer, multipart upload, final object, or table commit remains active. This contract separates five outcomes that tests and APIs must report independently:

1. query execution result;
2. final-object or final-file visibility;
3. multipart or staged-write cleanup;
4. commit status;
5. cleanup and cancellation latency.

The contract applies to the DataFusion and Polars comparison in #122 and informs the DuckDB remote-publication work in #96/#103. It is an evaluation model, not a claim that either comparison target currently violates it.

## Normative expectations

### 1. Failed work must not become committed output

Before a successful commit boundary, data may exist as buffered bytes, temporary files, uploaded parts, uncommitted blocks, or uniquely named data files. It must not appear as successful final output.

For an aborted operation:

- an existing destination must remain unchanged unless overwrite was explicitly committed;
- a new destination must remain absent from ordinary reads and listings of committed output;
- a table or dataset must not reference files produced by the failed attempt;
- a Parquet object must not be considered published merely because some bytes exist.

Amazon S3 creates the object only when `CompleteMultipartUpload` succeeds. Hadoop's output-commit model states that aborted task output must not become visible. Iceberg separates data-file creation from table publication and exposes new files only through an atomic metadata commit.

### 2. Graceful cancellation must attempt explicit cleanup

When the process is alive and owns the upload identifier, graceful cancellation or writer failure should:

1. stop or join outstanding part uploads;
2. call the backend's explicit abort or rollback operation;
3. verify cleanup where the backend exposes an inspection API;
4. preserve the initiating query or writer error;
5. report cleanup failure separately.

Dropping a writer is not an abort contract. The executed `object_store` 0.13.2 control in PR #219 demonstrated that after three parts were submitted, explicit abort called abort once, successful shutdown called complete once, and drop-only called neither.

Amazon S3 warns that in-flight part uploads can finish after an abort request. Its API guidance says a caller may need to abort again and should verify that `ListParts` is empty. That verification belongs in the strong S3 experiment, not just an `abort_calls == 1` assertion.

### 3. Lifecycle cleanup is a safety net, not the graceful path

A process can crash, lose power, or lose credentials before it can abort. Provider lifecycle policies are therefore required operational backstops for long-lived buckets used by analytical writers.

They do not replace explicit cleanup during an ordinary cancellation:

- S3 recommends an `AbortIncompleteMultipartUpload` lifecycle rule and continues billing uploaded parts until completion or abort;
- GCS multipart guidance recommends lifecycle cleanup when neither complete nor abort occurs;
- Azure keeps uncommitted blocks outside the committed blob and garbage-collects inactive uncommitted blocks after about one week.

Tests should distinguish immediate client cleanup from later provider garbage collection.

### 4. Cancellation request and cancellation completion are different states

An API must say whether `cancel()`:

- only sets a token or drops a future;
- waits until computation stops;
- waits until writers stop;
- waits until remote cleanup completes;
- returns a cleanup receipt or only a query error.

Polars documents cancellation as occurring at the earliest convenient point, and its handle sets a shared token. DataFusion's `DataSink` contract says the sink should perform required commit or rollback before returning, but cancellation by dropping the result stream may drop the sink future rather than allow it to return. The DataFusion experiment must therefore inspect callbacks after the stream is dropped instead of inferring cleanup from prompt task cancellation.

### 5. Commit status must be explicit, including unknown

Storage and table commits can succeed while the acknowledgement is lost. A reliable API needs at least these states:

- `not_started`;
- `aborted`;
- `committed`;
- `unknown`.

`unknown` must not be collapsed into either success or failure. Iceberg's commit API requires an unknown-state error when it cannot determine whether a commit succeeded and warns that cleanup is unsafe while status is unknown.

For file publication, an equivalent receipt should include the destination, attempt identifier, complete request status, final-object observation, and cleanup status.

### 6. Retry and overwrite behavior must be attempt-safe

Every attempt should have a unique identifier. Retrying to the same destination must define whether it:

- fails if the destination exists;
- conditionally creates only when absent;
- replaces only a known prior version;
- resumes the same upload;
- starts a new upload and cleans the old one.

S3 supports conditional writes on multipart completion. Hadoop's S3A committers use job and task commit records rather than treating a directory rename as an atomic object-store operation. Iceberg writes uniquely named files and commits table state by changing a metadata pointer.

A retry test is incomplete unless it checks retained state from the first attempt and the final contents from the second.

### 7. Cleanup errors must not mask the initiating error

The caller should retain the original cancellation, deadline, computation, or writer error as the primary result. Cleanup information should be attached as a structured secondary result containing:

- attempted operation;
- backend and upload identifier;
- elapsed time;
- success, failure, or unknown status;
- retained parts or blocks if observable;
- final-object visibility;
- retryability.

A cleanup failure can be operationally severe without rewriting the historical cause of the query failure.

### 8. Bounded cleanup must be observable

Graceful cleanup needs its own timeout and metrics. Waiting forever for abort defeats cancellation; returning instantly without acknowledging abandoned work hides cost and correctness risk.

Record at least:

- time from cancellation request to computation stop;
- time to writer-task termination;
- time to abort request;
- time to verified cleanup;
- whether cleanup continued after the query result was returned.

## Backend expectations

| Backend mechanism | Before commit | Commit action | Graceful failure expectation | Verification or backstop |
| --- | --- | --- | --- | --- |
| S3 multipart upload | parts stored and billable; final object absent | `CompleteMultipartUpload` | settle in-flight parts, abort, verify; preserve primary error | `ListParts` empty; lifecycle abort rule |
| GCS XML multipart upload | uploaded parts not committed to final object | complete multipart request | explicit abort when upload ID is owned | abort endpoint; lifecycle cleanup |
| Azure block blob | uncommitted blocks excluded from ordinary blob content | `Put Block List` | do not commit failed blocks; expose retained uncommitted state | `Get Block List`; automatic inactive-block GC after about one week |
| Local file | temporary or partial file | atomic replacement where supported | close and delete temporary output; do not replace destination | directory and file checks; fsync policy where durability is claimed |
| Iceberg-style table | data and metadata files may exist but are unreferenced | atomic metadata-pointer update | do not attach failed files; handle unknown commit state conservatively | snapshot metadata, orphan-file cleanup after status is known |

## Required experiment outcomes

### Successful publication control

- query returns success;
- complete or close occurs exactly once;
- final object is readable as Parquet;
- schema, row count, and content hash match;
- no incomplete upload remains.

### Cancellation before output begins

- no multipart upload or final output;
- bounded cancellation return;
- retry behaves like a first attempt.

### Cancellation after the first accepted part

Preferred result:

- query reports cancellation;
- no final object appears;
- abort is attempted after in-flight work is settled;
- retained parts become zero;
- cleanup receipt is available;
- retry succeeds according to the declared overwrite policy.

Degraded but reportable result:

- no final object appears;
- retained upload state remains;
- the result explicitly reports incomplete cleanup and the applicable lifecycle backstop.

Unacceptable result:

- failed or cancelled query publishes final output;
- cleanup is silently omitted;
- commit status is unknown but reported as definite success or definite failure;
- cleanup failure replaces the initiating error without preserving it.

### Cancellation during finalization

This case must classify the commit result as committed, aborted, or unknown. A test must not assume that a lost client acknowledgement means the final object is absent.

### Ordinary writer failure

Use a non-cancellation error after output begins. The same no-publication and cleanup guarantees should apply, while the primary result remains the writer error.

## Experiment changes for PR #219

The next DataFusion barrier should record:

- first part accepted;
- `DataSinkExec` result stream dropped;
- writer task aborted or completed;
- multipart abort and complete callbacks;
- final object visibility;
- retained part count after any in-flight part settles;
- cleanup latency and whether it outlives the dropped result stream;
- same-destination retry.

The first Polars barrier should use a local temporary destination before adding remote storage. It should cancel after row-group output begins and record temporary-file existence, footer validity, final-path visibility, cancellation latency, and retry. A later remote control can then separate Polars execution cancellation from the selected object-store writer's cleanup behavior.

## Authoritative source records

| Source | Locator | Supported claim | Limitation |
| --- | --- | --- | --- |
| Amazon S3 User Guide | https://docs.aws.amazon.com/AmazonS3/latest/userguide/abort-mpu.html | S3 creates the object on successful multipart completion; abandoned uploads should be aborted; parts are billable | provider-specific |
| Amazon S3 multipart overview | https://docs.aws.amazon.com/AmazonS3/latest/userguide/mpuoverview.html | completion and abort semantics; in-flight parts may race abort; conditional completion is available | provider-specific |
| Amazon S3 AbortMultipartUpload API | https://docs.aws.amazon.com/AmazonS3/latest/API/API_AbortMultipartUpload.html | repeated abort and `ListParts` verification may be required | provider-specific |
| Amazon S3 lifecycle guide | https://docs.aws.amazon.com/AmazonS3/latest/userguide/mpu-abort-incomplete-mpu-lifecycle-config.html | lifecycle abort is recommended as an operational backstop | day-granularity cleanup, not immediate cancellation |
| Google Cloud Storage XML API | https://docs.cloud.google.com/storage/docs/xml-api/delete-multipart | explicit multipart abort endpoint | XML multipart path only |
| Azure `Put Block` and `Put Block List` APIs | https://learn.microsoft.com/en-us/rest/api/storageservices/put-block and https://learn.microsoft.com/en-us/rest/api/storageservices/put-block-list | blocks remain uncommitted until block-list commit; inactive blocks are garbage-collected after about one week | Azure block-blob semantics differ from S3 multipart uploads |
| Azure `Get Block List` API | https://learn.microsoft.com/en-us/rest/api/storageservices/get-block-list | committed and uncommitted blocks can be inspected separately | provider-specific |
| Apache Hadoop S3A Committers | https://hadoop.apache.org/docs/current/hadoop-aws/tools/hadoop-aws/committers.html | aborted work must not become visible; object-store rename is unsafe; pending multipart uploads require commit or abort handling | batch-job architecture, not a direct engine API contract |
| Apache Iceberg reliability and specification | https://iceberg.apache.org/docs/latest/ and https://iceberg.apache.org/spec/ | uncommitted files remain outside table state; table updates use atomic metadata commits and optimistic concurrency | table-format publication, not standalone file export |
| Apache Iceberg `TableOperations` contract | https://iceberg.apache.org/javadoc/nightly/org/apache/iceberg/TableOperations.html | unknown commit state must remain explicit and makes cleanup unsafe | table commit API |
| Rust `object_store` multipart documentation | https://docs.rs/object_store/latest/object_store/trait.MultipartUpload.html | drop cannot clean parts on S3/GCS; explicit abort and lifecycle rules are recommended | latest docs; PR #219 separately pins and executes 0.13.2 |

## Decision rule

A target-specific child is justified when the engine-level barrier demonstrates one of:

- publication after reported failure;
- retained multipart or temporary state without an explicit cleanup receipt;
- an unbounded cancellation or cleanup path;
- commit-state ambiguity collapsed into a definite result;
- a documentation contract that materially understates these outcomes.

A clean negative result should be retained as a verified guarantee and used as the comparison baseline. No upstream contact occurred.
