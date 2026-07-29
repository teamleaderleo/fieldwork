# L01: Python COPY Publication Baseline

State: `claimed`

Campaign: #55  
Programme: #16  
Target hub: #11  
Worker: `chatgpt:gpt-5.6-thinking`  
Owned path: `campaigns/0003-duckdb-file-sink-publication/lanes/L01-python-copy-publication/`  
Upstream contact authorized: `false`

## In simple words

This lane watches the filename while DuckDB writes it. It then cancels the query, kills the process, or forces a memory failure and checks what another program would see. The main question is whether "the file exists" and "the export finished" mean the same thing.

## Assignment

For CSV and Parquet single-file `COPY`, compare normal completion, manual interruption, abrupt process death, and low-memory failure. Record active-write visibility, surviving bytes, fresh-reader behavior, retries, connection reuse, spill, and cleanup.

## Pins

- Owned DuckDB fork source: `teamleaderleo/duckdb@2c9e51aa33dd07e928edae66304430aeb038edd7`
- Research branch: `fieldwork/55-file-sink-publication`
- Owned research PR: https://redirect.github.com/teamleaderleo/duckdb/pull/1
- Python client: DuckDB 1.5.5
- Wheel SHA-256: `078e6a60dd8eedde5832f45422ca5c4a6b8c837aeabd8a56ca0b7d933f588053`
- Runner target: Ubuntu 24.04, Python 3.13, one DuckDB execution thread
- Retrieval and trial date: 2026-07-30

## Source map

### Engine operator

`src/execution/operator/persistent/physical_copy_to_file.cpp` separates `SINK`, `COMBINE`, and `FINALIZE` phases. Its global state owns the current file state, asynchronous file lifecycle work, output-path registry, row count, partition state, and flags for initialization and finalization.

The output registry has two distinct actions:

- reserve a path and optional written-file record;
- publish a created path into a list of files the operator knows it created.

This is an internal cleanup/accounting boundary. It is not itself an atomic operating-system publication step.

### Interruption

File lifecycle waits can call the client interruption check. Normal cancellation therefore has an opportunity to unwind through DuckDB cleanup rather than terminating the process in place. Abrupt process death deliberately bypasses that path.

### Format writers

CSV and Parquet have different consumer failure modes. A truncated CSV can remain parseable as a smaller table. A Parquet file normally needs terminal metadata and may reject an incomplete file. Both can still occupy the intended final pathname before successful statement completion.

## Hypotheses

H1. The final destination becomes visible before `COPY` reports success for both CSV and Parquet.

H2. Manual interruption removes the created destination and leaves the connection reusable, matching scout #28's post-failure result.

H3. Abrupt process death leaves the final destination because destructors and cleanup handlers do not run.

H4. A surviving CSV is likely readable as a truncated but otherwise ordinary table, while a surviving Parquet file is likely unreadable without its footer. Either outcome is unsafe when path existence is treated as completion.

H5. A default retry is blocked by the surviving final path until the application deletes, overwrites, or stages around it.

H6. A sufficiently low memory limit fails during the ordered source query before output publication; this is a negative control separating pre-writer failure from mid-writer interruption.

## Deterministic workload

Rows are generated from `range` with:

- `i::BIGINT` as the key;
- two concatenated MD5 strings as a fixed-width deterministic payload;
- one execution thread;
- exact row counts and arithmetic checksum;
- no network, private data, clock-derived values, or random seed.

Cases:

| Case | Rows | Trigger | Observer threshold |
|---|---:|---|---:|
| success | 500,000 | natural completion | path polling every 10 ms |
| interrupt | 50,000,000 | Python `connection.interrupt()` | after 256 KiB appears, or deadline |
| crash | 100,000,000 | operating-system process kill | after 1 MiB appears |
| low memory | 2,000,000 | 16 MiB limit plus `ORDER BY hash(i)` | path and temporary-directory polling |

## Acceptance checks

- Successful output is readable with the exact count and checksum.
- Manual interruption raises, removes the final output, and leaves the connection reusable.
- Process death occurs after the byte threshold and leaves the final path present.
- The surviving path blocks a default retry.
- Removing the surviving path permits a clean retry with exact count.
- Low-memory failure raises, leaves no final output, cleans temporary files, and leaves the connection reusable.

## Artifacts

The owned fork branch currently contains:

- `tools/fieldwork/issue55_file_sink_probe.py`
- `tools/fieldwork/requirements-issue55.txt`
- `.github/workflows/fieldwork-issue55-file-sink.yml`

Raw results will be copied into this owned lane after a successful controlled run.

## Current status

Probe dispatched. No result is claimed yet.
