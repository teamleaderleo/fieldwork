# Native Multipart Abort Experiment

State: `running`

Lane: #103  
Campaign: #96  
Owned DuckDB branch: `fieldwork/103-s3-interrupt-abort`  
Owned draft PR: https://redirect.github.com/teamleaderleo/duckdb/pull/4  
Upstream contact authorized: `false`

## Candidate lifecycle

Successful explicit or legacy implicit close continues to call `FinalizeUpload()`.

Failed destruction caused by active C++ exception unwinding or an owning client context that remains interrupted instead calls `AbortUpload()`.

Multipart abort:

1. clears pending write buffers without flushing them;
2. waits for already-started part uploads to finish;
3. sends `DELETE ?uploadId=...`;
4. marks the upload terminal;
5. avoids `CompleteMultipartUpload`.

## Regression expectation

The source-level mock test requires:

- interrupted query error;
- connection reuse;
- at least one completed part upload;
- zero successful multipart-complete POSTs;
- exactly one successful multipart-abort DELETE.

## Review findings before results

### Positive

- Native abort matches S3 multipart semantics.
- It avoids upload-then-delete visibility.
- It releases hidden parts instead of merely abandoning them.
- It preserves legacy successful implicit close when no failure signal is visible.

### Risks

- Network cleanup from a destructor can block during exception unwinding.
- Destructor exceptions remain suppressed, so abort failure requires logging or retained state to become diagnosable.
- `ClientContext::IsInterrupted()` covers interruption and timeout state, not every error already converted into query state.
- Waiting for detached upload threads needs a terminal-state audit for every exception path.
- A concurrent late flush would need an explicit upload lifecycle state rather than only a Boolean finalized flag.

## Preferred long-term ownership if the experiment works

1. add an explicit COPY failure callback or writer abort contract;
2. invoke native multipart abort from controlled failed-query teardown;
3. keep destructors as bounded safety nets rather than the primary transaction boundary;
4. migrate known successful implicit-close users to explicit `Close()`;
5. report abort failures through query diagnostics or logging.

## Status interpretation

A passing experiment establishes that native abort is technically viable in the pinned source and mock fixture. It does not establish that destructor-driven abort is the final API design.

No upstream contact occurred.
