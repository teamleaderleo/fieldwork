# DataFusion and Polars reproducible analytical publication

Issue: #122

State: dual-engine target execution complete for the first bounded cancellation controls

Worker: Archive

Upstream contact authorized: false

## Question

When a Parquet-producing query is cancelled after output work starts, what becomes visible, what retained upload state remains, how quickly does execution stop, and which component owns cleanup?

The investigation treats cancellation request, computation stop, writer stop, publication, multipart cleanup, commit status, and cleanup latency as separate observable events. It does not infer cleanup from a returned query error.

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

The inspected sink path does not explicitly call `BufWriter::abort()` on cancellation or writer-task error. This produced the executed engine-level hypothesis below.

### Polars

`LazyFrame.collect_concurrently()` produces an `InProcessQuery`. `cancel()` sets the shared `ExecutionState` stop token. `ExecutionState::should_stop()` raises `query interrupted` only where an executor or sink calls it.

The streaming Parquet I/O writer consumes encoded row groups, finishes the Parquet writer, drops its buffered writer, and closes the file on the normal path. The first local execution therefore classifies the cancellation-observation horizon rather than assuming that setting the token interrupts every writer phase.

## Executed dependency control

`probes/object-store-abort` pins `object_store` to version `0.13.2` and instruments multipart calls through the public writer API.

Exact-head run `30545721329` passed source retrieval, source-anchor checks, dependency selection, formatting, compilation, the Rust test, execution, and evidence upload.

All three cases crossed the multipart threshold and submitted three parts:

| Mode | Multipart started | Parts submitted | Complete calls | Abort calls |
| --- | ---: | ---: | ---: | ---: |
| explicit abort | 1 | 3 | 0 | 1 |
| drop only | 1 | 3 | 0 | 0 |
| successful shutdown | 1 | 3 | 1 | 0 |

Dropping the pinned writer is observably distinct from both successful publication and explicit cleanup.

## DataFusion target execution

Exact executed source head `f45f7d793b3aa94b83c719c1131ceedaabe54644`, run `30579974405`:

- one multipart upload began;
- 1,605 parts were submitted;
- complete calls: `0`;
- abort calls: `0`;
- upload object dropped: `1`;
- final object visible through the tracking store: `false`.

The success control completed exactly once and exposed the final object.

This is `target-executed` for the bounded tracking-store behavior. It proves that dropping the outer DataFusion sink future can drop upload ownership without invoking explicit abort. Whether a real provider retains billable multipart parts remains an inference until a provider-faithful store exposes that state.

## Polars local target execution

Exact head `fe24af28d966e9459ff5a268bffd6b44b768251c`, Polars revision `36e414b4cb1e74e7a171995b35b83c1163974324`, run `30623286118`, job `91132573948`, artifact `8790351996`, artifact digest `sha256:fc233e0f31d1b7c6cc74d2c1da9e96dbb4d782ab399a34ff4266cc73ce1b2abb`.

The focused control generated one million uncompressed rows and waited until the requested final path exposed nonzero bytes.

### Cancellation after first visible bytes

- first observed final-path bytes: `8,192`;
- barrier reached after `58 ms`;
- cancellation request issued: `true`;
- query outcome: `completed_after_cancel_request`;
- query error: none;
- total elapsed time: `1,546 ms`;
- final file size: `246,101,878` bytes;
- Parquet valid: `true`;
- readable rows: `1,000,000`.

### Same-path retry control

- outcome: completed successfully;
- elapsed time: `1,448 ms`;
- final file size: `246,101,878` bytes;
- Parquet valid: `true`;
- readable rows: `1,000,000`.

This is `target-executed` for the bounded local publication behavior. The cancellation request did not interrupt the active sink after final-path bytes became visible. The sink completed normally and published the full file. The result does not show partial-file corruption, a failed query reported as success, or a retry failure.

The remaining question is cancellation responsiveness and publication semantics: where is the last observation point at which the shared stop token can still prevent or interrupt local Parquet publication?

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

## Current comparative result

The two first controls expose different ownership risks:

- DataFusion outer-task cancellation can terminate publication without explicit multipart abort in the bounded tracking-store harness.
- Polars local cancellation after final-path visibility can allow the writer to finish and publish a complete file after the cancellation request.

Neither result should be summarized as generic “cancellation is broken.” They identify separate questions:

- **DataFusion:** who owns provider cleanup after the writer task is dropped?
- **Polars:** which writer and pipeline phases observe the cancellation token, and what completion semantics are promised after the request?

## Next controls

### DataFusion

1. use a provider-faithful multipart store that exposes retained parts;
2. block after the first accepted part;
3. cancel the outer sink;
4. settle all tasks;
5. record abort, complete, retained-part state, final visibility, and cleanup latency;
6. retry with a unique attempt identity and the same logical destination.

### Polars

1. cancel immediately after `collect_concurrently()` returns, before final-path visibility;
2. cancel after input execution begins but before any final-path bytes appear;
3. cancel at first final-path visibility;
4. request cancellation during finalization/close through a deterministic writer barrier;
5. compare explicit `cancel()` with dropping the `InProcessQuery` handle;
6. repeat with a temporary-path-plus-atomic-replace publication strategy;
7. retain query outcome, stop latency, file-operation order, final-path visibility, footer validity, row count, and same-path retry behavior for every case.

A repair candidate becomes justified only after the last effective token-observation point and the intended completion contract are explicit.

## Promotion gate

Promote a target-specific child only after exact reproduction, a deterministic timing barrier, a classified visible or retained side effect, a likely owning subsystem, and an equivalent negative control.

Promotion triggers include publication after a reported interruption, silent retained multipart state, unbounded cleanup, commit-state ambiguity reported as definite, or materially incomplete cancellation documentation.

Healthy negative results remain valid. No upstream contact occurred.
