# Reviewed Integration Result

State: `complete`

Lane: #103  
Campaign: #96  
Upstream contact authorized: `false`

## Probe revision

The request-order integration probe was revised after code review to:

- distinguish an actual worker exit from a join timeout;
- retry bounded interruption once for cleanup;
- skip connection reuse if another thread still owns the connection;
- suppress only expected bucket-exists responses;
- add an explicit thread-termination invariant.

## Provenance

- DuckDB research head: `teamleaderleo/duckdb@2c0a14014a73861f64fea8ad0fd03250e71401f3`
- workflow run: `30488634215`
- artifact: `8738736167`
- artifact digest: `sha256:db39fcf6e84399ef87042049945075af3b4ab6294616ff41e97d958d646650b8`
- checks: 18 passed, 0 failed
- DuckDB Python: 1.5.5
- pinned MinIO and httpfs values remain those recorded in L01/L02

## CSV

- one 5,504,856-byte multipart part observed before interruption;
- worker terminated;
- query result: `InterruptException`;
- connection reusable;
- multipart completed after interruption;
- final object existed;
- fresh reader accepted 202,752 rows;
- key range: 0 through 202,751;
- checksum: 20,554,085,376, exactly matching that prefix;
- no object delete or multipart-abort request after interruption.

## Parquet

- one 5,504,856-byte multipart part observed before interruption;
- worker terminated;
- query result: `InterruptException`;
- connection reusable;
- multipart completed after interruption;
- final object existed;
- fresh reader rejected the object because terminal magic bytes were absent;
- no object delete or multipart-abort request after interruption.

## Interpretation

The original integration conclusion survives the code-review corrections. The result does not depend on falsely labeling a live query thread as finished or reusing a connection while its query is still active.

Exact CSV prefix size remains timing-dependent and fixture-scoped. The invariant is that a failed statement publishes a valid-looking strict prefix at the final key.

No upstream contact occurred.
