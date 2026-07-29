# Issue 103 Probe Code Review

State: `active`

## Reviewed files

- owned Python request-order proxy and interrupt probe;
- owned MinIO workflow;
- source-level httpfs mock-server patch and workflow.

## Findings in the Python trace probe

### 1. Thread completion was logged too early

The probe called `thread.join(timeout=30)` and then emitted `query_thread_finished` without first checking `thread.is_alive()`.

The result object later recorded the actual state, but the trace label could overstate completion. A subsequent connection-reuse query also ran even if the query thread remained alive.

Correction:

- calculate `thread_finished` immediately after the join;
- emit either `query_thread_finished` or `query_thread_still_running`;
- issue one bounded second interrupt/join for cleanup;
- skip connection reuse and close-on-main-thread operations while another thread still owns the connection;
- fail the probe when the worker does not terminate.

### 2. Bucket creation suppressed every exception

The setup code caught `Exception` around `create_bucket` and ignored it. That treats an existing bucket and an authentication, endpoint, or network error as equivalent.

Correction:

- suppress only the expected already-exists/already-owned responses;
- propagate every other setup error.

### 3. Assertions were more credential-specific than needed

The proxy evidence is about request class and ordering. Assertions tied to one access-key ID are less stable when credential refresh is enabled.

Correction:

- count successful multipart part and completion requests by target/query class;
- record credential identity as attribution data rather than as the main behavioral predicate.

### 4. Proxy buffering changes timing

The transparent Python proxy forwards request bodies after buffering them in memory. This can change the exact partial row count and part timing.

This does not invalidate the observed causal order, because the proxy forwards signed requests unchanged and records the final-key check, part uploads, completion response, and query result. It does mean exact prefix size is an outcome of that fixture rather than a universal constant.

Correction:

- keep row-count claims fixture-scoped;
- use the C++ mock-server gate for deterministic source-level placement;
- retain MinIO as the protocol-level consequence test.

## Source-level fixture review

### Initial failures

1. The first patch had malformed hunk counts.
2. The regenerated patch had one overly broad wrapper hunk.
3. After patch application succeeded, the runner lacked the linker requested by DuckDB's debug configuration.

These are fixture-authoring and build-environment failures. None is treated as a DuckDB result.

### Current source-level invariant

The C++ test blocks the first multipart part response, interrupts the connection, releases the response, and expects:

- query result contains an interruption error;
- the connection remains reusable;
- at least one multipart part succeeded;
- no successful multipart-complete POST occurred.

Current DuckDB is expected to fail the final assertion. The workflow treats that failing assertion as the evidence target and fails if the test unexpectedly passes.

## Next code changes

1. complete the source-level failing regression;
2. add the Python probe corrections above;
3. add a natural-success control to the C++ fixture;
4. add an ordinary non-interrupt expression-error control;
5. test a repair candidate only after those controls pass.

No upstream contact occurred.
