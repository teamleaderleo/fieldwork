# Campaign 0004: DuckDB Remote Publication Under Failure

State: `claimed`

Programme: #16  
Target hub: #11  
Campaign issue: #96  
Parent campaign: #55  
Parent scout: #28  
Upstream contact authorized: `false`

## In simple words

A local export can be hidden behind a temporary filename until it is complete. An object store uses multipart uploads and object keys instead of a local rename.

The initial S3-compatible lane found that DuckDB can return `InterruptException` and still complete a multipart upload at the requested final key. CSV may be a valid smaller dataset; Parquet may be a completed key with unreadable contents.

A request trace proved that failed-query cleanup checked the absent final key first, then writer destruction uploaded buffered parts and completed the multipart upload. Repair lane #103 now owns the source-level regression and repair decision.

## Question

For DuckDB `COPY` to an S3-compatible object store, what can consumers and operators observe before statement completion and after interruption, process death, retry, or multipart abandonment, and which completion contract is safe when local temporary-file publication is unavailable?

The active repair question is:

> How should failed `COPY` teardown abort or suppress remote publication so `InterruptException` cannot leave a new final object?

## Pins

- Owned DuckDB fork base: `teamleaderleo/duckdb@2c9e51aa33dd07e928edae66304430aeb038edd7`
- Current research head: `teamleaderleo/duckdb@46d8d13f18e558ff6de44182aaf64ba1ccf686f0`
- DuckDB Python client: 1.5.5
- DuckDB core httpfs pin: `duckdb/duckdb-httpfs@df92a34d29eb589591adfadba89fa8df874e54ea`
- MinIO server release: `RELEASE.2025-07-23T15-54-02Z`
- MinIO SHA-256: `eef6581f6509f43ece007a6f2eb4c5e3ce41498c8956e919a7ac7b4b170fa431`
- Owned research PR: https://redirect.github.com/teamleaderleo/duckdb/pull/2
- Generated data only
- No production object store, private credentials, or upstream contact

## Established findings

1. Natural CSV and Parquet multipart completion produced exact objects.
2. Hard process death left no final object and retained an incomplete multipart upload.
3. Same-key retry produced an exact new object while the older incomplete upload remained.
4. Remote `USE_TMP_FILE true` created no staging object and followed direct multipart behavior.
5. Manual interruption after an uploaded part completed the multipart upload and published a final object before returning `InterruptException`.
6. CSV published a readable deterministic prefix.
7. Parquet published a completed object without terminal metadata.
8. A transparent proxy recorded `HEAD` 404 for the final key after interruption, followed by remaining part uploads and successful multipart completion.
9. No object delete and no abort-multipart request occurred.

## Lanes

- **L01 — S3-compatible publication baseline:** complete.
- **L02 / issue #103 — interrupt publication repair:** claimed.

## Decision gate

A held upstream issue draft is supported by the current evidence.

A code PR draft requires:

1. a source-level failing regression;
2. an audit of S3 users that rely on destructor-driven completion;
3. a choice between explicit close plus multipart abort, extension-specific failed-teardown abort, core cleanup reordering, or a broader file-handle abort contract.

No upstream contact occurred.
