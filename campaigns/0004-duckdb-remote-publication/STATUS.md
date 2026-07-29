# Campaign 0004 Status

State: `claimed`

Campaign issue: #96  
Programme: #16  
Target hub: #11  
Upstream contact authorized: `false`

## Current result

L01 is complete. DuckDB Python 1.5.5 with the bundled `httpfs` extension can return `InterruptException` while completing an S3 multipart upload at the requested final key.

- CSV can be a readable deterministic prefix of the requested export.
- Parquet can be a completed object that rejects reads because terminal metadata is absent.
- Hard process death leaves an incomplete multipart upload rather than a final object.
- Same-key retry does not remove the older incomplete upload.
- Remote `USE_TMP_FILE true` does not create local-style staging.

The reviewed request-order probe now passes 18/18 checks after correcting worker-termination and bucket-setup weaknesses. The correctness result remained unchanged.

## Active lane

- #103 — source-level regression and repair ownership for interrupted S3 publication.

## Historical boundary

- PR #9758 added destructor-driven S3 close to preserve successful `EXPORT DATABASE` metadata files.
- issue #12038 / PR #12031 skipped destructor close only during active C++ exception unwinding.
- manual interruption reaches writer teardown after the error is captured, while the client interrupt flag is still set.
- current CSV, Parquet, and BLOB successful copy paths close explicitly; core export metadata writing still relies on implicit close.

## Running owned experiments

1. **Current-source regression** — deterministic mock S3 server blocks the first multipart part, interrupts the query, and expects current code to fail the no-completion invariant.
2. **Interrupt containment** — draft owned PR #3 skips implicit S3 close while the owning context remains interrupted. It can prevent publication but leaves an incomplete upload.
3. **Native multipart abort** — draft owned PR #4 discards pending buffers, waits for in-flight parts, sends `AbortMultipartUpload`, and requires zero completion requests plus one abort request.

The builds are narrowed to the `unittest_httpfs` target. Patch-authoring and build-environment failures are retained separately and carry no DuckDB conclusion.

## Durable evidence

- L01 report and compact result summary
- L02 request-order trace and compact trace result
- reviewed integration result and probe code review
- close history and successful-writer audit
- held upstream issue draft and history addendum
- containment and native-abort experiment notes
- owned DuckDB research branches and workflow artifacts

## Decision gate

Issue-level reporting is supported and held for human approval.

A code proposal requires:

1. a source-level failing regression;
2. passing success and ordinary-error controls;
3. a choice between explicit failure callback, native multipart abort, or a wider file-handle abort contract;
4. a plan for successful implicit-close users;
5. observable abort-error handling.

No upstream contact occurred.
