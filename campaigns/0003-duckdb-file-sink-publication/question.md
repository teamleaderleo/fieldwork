# Campaign 0003: DuckDB File-Sink Publication Under Failure

State: `claimed`

Programme: #16  
Target hub: #11  
Campaign issue: #55  
Parent scout: #28  
Upstream contact authorized: `false`

## In simple words

DuckDB can write a query result to a CSV or Parquet path. Many applications treat the appearance of that final path as proof that the export is finished. This campaign checks whether that assumption remains safe while the query is still running, after cancellation, after memory failure, and after the writing process is killed.

## Question

Across interruption, resource failure, abrupt process death, filesystem failure, and retry, what output can another process observe at the final destination, and which layer owns the step from "bytes are being written" to "this file is safe to consume"?

## Motivation

Scout #28 established a useful negative result: after ordinary interruption and out-of-memory failure, its tested single-file Parquet output was absent and temporary spill was cleaned. The scout did not observe the destination while the write was active and did not bypass cleanup with abrupt process death. Those two controls determine whether final-path existence can serve as a completion signal.

## Initial boundary

- Owned DuckDB fork: `teamleaderleo/duckdb@2c9e51aa33dd07e928edae66304430aeb038edd7`
- Initial client baseline: DuckDB Python 1.5.5
- Owned research PR: https://redirect.github.com/teamleaderleo/duckdb/pull/1
- Generated deterministic rows only
- Local filesystem on an owned GitHub Actions runner
- CSV and Parquet single-file `COPY`
- No upstream contact

## Publication states to distinguish

1. **Reserved** — DuckDB has selected a destination path.
2. **Opened** — the final path can exist while the query is still active.
3. **Growing** — another process can observe changing bytes.
4. **Writer-finalized** — the format writer has emitted its closing metadata or terminal bytes.
5. **Query-complete** — DuckDB has reported successful statement completion.
6. **Consumer-accepted** — a fresh reader can open the output and verify the expected rows and checksum.
7. **Application-published** — an application-specific completion marker, rename, or manifest makes the output eligible for downstream use.

The campaign must avoid collapsing these states into one word such as "written" or "complete."

## Initial lane

`L01-python-copy-publication` observes the destination throughout four deterministic cases for each format:

- normal completion;
- manual `connection.interrupt()` after output bytes become visible;
- abrupt process kill after at least 1 MiB reaches the final path;
- 16 MiB memory-limit failure during a spill-heavy ordered source query.

A fresh connection records existence, size, readability, row count, checksum, retry behavior, connection reuse, spill volume, and residue.

## Later branches

Open later lanes only when the first result distinguishes a boundary:

1. partitioned and rotated multi-file output;
2. source-level failpoints around writer finalize, close, and cleanup;
3. disk-full, permission, and filesystem-adapter faults;
4. cross-client cancellation and publication contracts;
5. application-level staging, rename, manifest, and checksum patterns.

## Stop conditions

Stop or narrow when the tested failure cannot produce observer-visible ambiguity, the consequence belongs entirely to an application convention with no DuckDB boundary, deterministic placement requires unsupported private facilities, another assignment owns the same question, or a proposed code change precedes a failing test and demonstrated consequence.

## Expected outputs

- a source-pinned publication lifecycle map;
- deterministic raw results and retained probe code;
- explicit negative results;
- a decision on source-level failpoints;
- a consumer-safe publication recommendation separated from any engine-change thesis;
- any upstream packet held for explicit human approval.
