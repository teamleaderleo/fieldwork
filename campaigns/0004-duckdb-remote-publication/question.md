# Campaign 0004: DuckDB Remote Publication Under Failure

State: `claimed`

Programme: #16  
Target hub: #11  
Campaign issue: #96  
Parent campaign: #55  
Parent scout: #28  
Upstream contact authorized: `false`

## In simple words

A local export can be hidden behind a temporary filename until it is complete. An object store uses uploads and object keys instead of a local rename. This campaign checks what a reader can see while DuckDB is uploading, what remains when the writer is interrupted or killed, and which signal should mean that the object is ready.

## Question

For DuckDB `COPY` to an S3-compatible object store, what can consumers and operators observe before statement completion and after interruption, process death, retry, or multipart abandonment, and which completion contract is safe when local temporary-file publication is unavailable?

## Pins

- Owned DuckDB fork base: `teamleaderleo/duckdb@2c9e51aa33dd07e928edae66304430aeb038edd7`
- DuckDB Python client: 1.5.5
- DuckDB core httpfs pin: `duckdb/duckdb-httpfs@df92a34d29eb589591adfadba89fa8df874e54ea`
- MinIO server release: `RELEASE.2025-07-23T15-54-02Z`
- Owned research branch: `teamleaderleo/duckdb:fieldwork/96-remote-publication`
- Owned research PR: https://redirect.github.com/teamleaderleo/duckdb/pull/2
- Generated data only
- No production object store, private credentials, or upstream contact

## Initial lane

`L01-s3-compatible-publication` runs CSV and Parquet against a local MinIO service and records:

1. final-object visibility during multipart upload;
2. ordinary interruption after at least one part is uploaded;
3. hard process death after at least one part is uploaded;
4. retry to the same key;
5. incomplete multipart uploads before and after retry;
6. remote `USE_TMP_FILE true` behavior;
7. exact fresh-reader count and checksum;
8. explicit cleanup of retained uploads and objects.

## Decision gate

Promote a source-level or documentation candidate only when the retained matrix distinguishes a consequential DuckDB behavior from ordinary S3 multipart semantics and emulator-specific behavior.
