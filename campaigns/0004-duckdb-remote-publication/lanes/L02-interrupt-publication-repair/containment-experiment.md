# S3 Interrupt Containment Experiment

State: `running`

Lane: #103  
Campaign: #96  
Owned DuckDB branch: `fieldwork/103-s3-interrupt-containment`  
Upstream contact authorized: `false`

## Question

At S3 file-handle destruction time, does DuckDB's owning `ClientContext` still report the query as interrupted?

If yes, the extension can distinguish this cancellation path from ordinary successful implicit close without relying on `std::uncaught_exceptions`.

## Candidate

The owned extension patch:

1. retains the owning `ClientContext` weak reference even when credential refresh is disabled;
2. checks `context->IsInterrupted()` in `S3FileHandle::~S3FileHandle()`;
3. skips destructor-driven `Close()` when the owning query is interrupted.

## Expected result

The deterministic C++ regression should pass its core invariant:

- query reports interruption;
- connection remains reusable;
- at least one multipart part was uploaded;
- no successful multipart-complete POST occurs during teardown.

## Limits

This candidate does not implement `AbortMultipartUpload`.

A passing result would therefore mean:

- the partial final object is no longer published;
- the incomplete multipart upload remains stored until lifecycle cleanup removes it.

It also covers interruption state only. Other failures that have been converted into query state may need an explicit failure callback or commit/abort state.

## Why run it

The experiment answers an ownership question before adding a wider API:

- whether the extension can observe the relevant cancellation state at destruction;
- whether explicit query-to-file abort plumbing is required for this case;
- whether native multipart abort can be layered onto the same branch.

The candidate is not an upstream proposal. No upstream contact occurred.
