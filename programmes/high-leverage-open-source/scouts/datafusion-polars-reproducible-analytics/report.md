# DataFusion and Polars reproducible analytical publication

Issue: #122

State: active executed dependency control and engine-level barrier design

Worker: Archive

Upstream contact authorized: false

## Question

When a Parquet-producing query is cancelled after output work starts, what becomes visible, what retained upload state remains, how quickly does execution stop, and which component owns cleanup?

The investigation treats cancellation, output publication, multipart cleanup, commit status, and cleanup latency as separate observable events. It does not infer cleanup from a returned query error.

## Exact source set

Retrieved 2026-07-30:

- DataFusion revision `455a3add52d051a20df9960a726ee9acb98528a3`
- DataFusion `object_store` dependency `0.13.2`
- object-store release source revision `7a65b75b0d26fd8a282999462cb7030fb85fdcc3`
- Polars revision `36e414b4cb1e74e7a171995b35b83c1163974324`

No owned DataFusion or Polars fork was available at activation. External repositories remain read-only. The executable carrier lives in Fieldwork.

## Source ownership map

### DataFusion

The cancellation benchmark states that execution should stop quickly after the output stream is dropped. `DataSinkExec` owns a one-item future awaiting `sink.write_all`. Dropping the result stream drops that future.

The Parquet sink owns writer tasks in DataFusion's Tokio-backed `JoinSet`. Tokio aborts every tracked task when the set is dropped. The sequential Parquet writer creates an `object_store::buffered::BufWriter` and reaches `writer.close().await` only on the normal writer-task path.

The inspected sink path does not explicitly call `BufWriter::abort()` on cancellation or writer-task error. This produces a precise engine-level hypothesis, not a defect claim: cancellation after multipart work begins may abort the writer task and drop the writer without invoking remote cleanup.

### Polars

`LazyFrame.collect(background=True)` produces an `InProcessQuery`. Explicit cancellation and dropping that handle set a shared cancellation token, documented as cancellation at the earliest convenient point.

The streaming Parquet I/O writer consumes encoded row groups, finishes the Parquet writer, drops its buffered writer, and closes the file on the normal path. The first execution must locate cancellation observation relative to row-group encoding, footer finalization, temporary-file visibility, final-path visibility, and close.

## Executed dependency control

`probes/object-store-abort` pins `object_store` to version `0.13.2` and instruments multipart calls through the public writer API.

Exact-head run `30545721329` passed source retrieval, source-anchor checks, dependency selection, formatting, compilation, the Rust test, execution, and evidence upload.

All three cases crossed the multipart threshold and submitted three parts:

| Mode | Multipart started | Parts submitted | Complete calls | Abort calls |
| --- | ---: | ---: | ---: | ---: |
| explicit abort | 1 | 3 | 0 | 1 |
| drop only | 1 | 3 | 0 | 0 |
| successful shutdown | 1 | 3 | 1 | 0 |

Dropping the pinned writer is therefore observably distinct from both successful publication and explicit cleanup.

## Authoritative publication contract

`publication-contract.md` converts provider and table-format guidance into testable expectations.

Core rules:

1. failed or cancelled work must not become committed output;
2. graceful failure must attempt explicit abort or rollback when the process owns the upload;
3. lifecycle cleanup is a crash backstop, not a substitute for ordinary cleanup;
4. cancellation request, computation stop, writer stop, and cleanup completion are separate states;
5. commit status must allow `unknown` and must not be guessed;
6. retries need unique attempt identity and declared overwrite behavior;
7. cleanup errors remain secondary to the initiating error;
8. cleanup latency and retained state must be observable.

The guidance is grounded in Amazon S3 multipart and lifecycle documentation, Google Cloud Storage multipart abort documentation, Azure committed/uncommitted block semantics, Hadoop's S3A output-commit model, Iceberg's atomic metadata commit and unknown-state contract, and the Rust `object_store` multipart contract.

## Shared publication matrix

For each engine:

1. successful single-file Parquet publication;
2. cancellation before the first output write;
3. cancellation after at least one part or buffered segment is accepted;
4. cancellation during finalization where a deterministic barrier is possible;
5. ordinary writer failure after output begins;
6. retry to the same destination and to a fresh destination.

Capture exact source and runtime configuration, plans, trigger timing, computation-stop latency, writer-stop latency, cleanup latency, file or request order, visible outputs, multipart state, Parquet footer validity, row counts, schema, hashes, cleanup errors, and commit status.

## Next engine-level barriers

### DataFusion

Use a registered tracking object store and a deterministic first-part barrier:

1. begin Parquet publication through the actual sink;
2. block after the first multipart part is accepted;
3. drop the `DataSinkExec` result stream;
4. settle in-flight work;
5. record writer-task termination, abort, complete, final visibility, retained parts, and latency;
6. retry to the same destination.

A strong success requires no final object, explicit cleanup, zero retained parts, a preserved cancellation result, and bounded cleanup. A no-object result with retained parts is degraded and must be explicitly reported rather than treated as clean cancellation.

### Polars

Start with a local temporary destination so execution cancellation is separated from a remote client implementation:

1. use deterministic generated input large enough to begin row-group output;
2. cancel after output starts;
3. inspect temporary and final paths;
4. test Parquet footer readability and row count;
5. measure cancellation and close timing;
6. retry the same and a fresh destination.

Add a remote writer only after the local publication boundary is classified.

## Promotion gate

Promote a target-specific child only after exact reproduction, a deterministic timing barrier, a classified visible or retained side effect, a likely owning subsystem, and an equivalent negative control.

Promotion triggers include publication after reported failure, silent retained multipart state, unbounded cleanup, commit-state ambiguity reported as definite, or materially incomplete cancellation documentation.

Healthy negative results remain valid. No upstream contact occurred.
