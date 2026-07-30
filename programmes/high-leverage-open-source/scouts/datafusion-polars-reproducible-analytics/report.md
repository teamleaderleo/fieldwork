# DataFusion and Polars reproducible analytical publication

Issue: #122

State: active source pass and first executable control

Worker: Archive

Upstream contact authorized: false

## Question

When a Parquet-producing query is cancelled after output work starts, what becomes visible, what retained upload state remains, how quickly does execution stop, and which component owns cleanup?

The first pass treats cancellation, output publication, and multipart cleanup as separate observable events. It does not infer cleanup from a returned query error.

## Exact source set

Retrieved 2026-07-30:

- DataFusion revision `455a3add52d051a20df9960a726ee9acb98528a3`
- DataFusion `object_store` dependency `0.13.2`
- object-store release source revision `7a65b75b0d26fd8a282999462cb7030fb85fdcc3`
- Polars revision `36e414b4cb1e74e7a171995b35b83c1163974324`

No owned DataFusion or Polars fork was available at activation. External repositories remain read-only. The executable carrier lives in Fieldwork.

## Source ownership map

### DataFusion

The cancellation benchmark states that execution should stop quickly after the output stream is dropped. The Parquet sink creates an `object_store::buffered::BufWriter`, writes record batches, and reaches `writer.close().await` on the normal writer-task path.

The pinned object-store writer has three distinct outcomes:

- successful shutdown completes a buffered or multipart object;
- explicit `abort()` cleans partial multipart state where the backend supports it;
- dropping a multipart upload is not equivalent to abort for S3- and GCS-style stores.

The inspected DataFusion sink path does not explicitly call `BufWriter::abort()` on cancellation or writer-task error. This is a probe lead, not a defect claim. Execution must determine whether another owner performs cleanup.

### Polars

`LazyFrame.collect(background=True)` produces an `InProcessQuery`. Explicit cancellation and dropping that handle set a shared cancellation token. The streaming Parquet I/O writer consumes encoded row groups, finishes the Parquet writer, drops its buffered writer, and closes the file on the normal path.

The first execution must locate cancellation observation relative to row-group encoding, footer finalization, file visibility, and remote cleanup.

## First executable control

`probes/object-store-abort` pins `object_store` to version `0.13.2` and instruments multipart calls through the public writer API.

It records three cases after crossing the multipart threshold:

1. explicit abort — abort is called, complete is not called;
2. drop-only — neither abort nor complete is called;
3. successful shutdown — complete is called, abort is not called.

This control establishes the dependency contract needed to interpret a later DataFusion sink cancellation. It does not claim DataFusion currently drops without cleanup.

## Shared publication matrix

For each engine:

1. successful single-file Parquet publication;
2. cancellation before the first output write;
3. cancellation after at least one part or buffered segment is accepted;
4. cancellation during finalization where a deterministic barrier is possible;
5. ordinary writer failure after output begins;
6. retry to the same destination and to a fresh destination.

Capture exact source and runtime configuration, plans, trigger timing, return latency, file or request order, visible outputs, multipart state, Parquet footer validity, row counts, schema, hashes, and cleanup errors.

## Promotion gate

Promote a target-specific child only after exact reproduction, a deterministic timing barrier, a classified visible or retained side effect, a likely owning subsystem, and an equivalent negative control.

Healthy negative results remain valid. No upstream contact occurred.
