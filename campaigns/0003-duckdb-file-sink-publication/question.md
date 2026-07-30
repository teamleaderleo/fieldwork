# Campaign 0003: DuckDB File-Sink Publication Under Failure

State: `complete`

Programme: #16  
Target hub: #11  
Campaign issue: #55  
Parent scout: #28  
Upstream contact authorized: `false`

## In simple words

DuckDB can write directly to the filename that another program is watching. For a brand-new local file, that filename can appear before the export has finished. A hard process death can therefore leave a partial final file.

DuckDB also supports `USE_TMP_FILE`. It writes `tmp_<name>`, closes the completed writer, and then moves the file into place. DuckDB 1.5.5 enabled that mode automatically for an existing local single-file destination, but not for a fresh one.

## Question

Across interruption, resource failure, abrupt process death, filesystem failure, and retry, what output can another process observe at the final destination, and which layer owns the step from "bytes are being written" to "this file is safe to consume"?

## Boundary completed

L01 covered:

- DuckDB Python 1.5.5;
- local Ubuntu filesystem;
- generated deterministic rows;
- single-file CSV and Parquet `COPY`;
- fresh direct output;
- explicit `USE_TMP_FILE true`;
- replacement of an existing local file;
- manual interruption;
- 16 MiB memory failure;
- exact-threshold abrupt process death;
- retry and stale temporary residue.

Owned source base: `teamleaderleo/duckdb@2c9e51aa33dd07e928edae66304430aeb038edd7`  
Final research head: `teamleaderleo/duckdb@d9d14e7f1d51694237029354ef637b0806878290`  
Owned research PR: https://redirect.github.com/teamleaderleo/duckdb/pull/1

## Publication states distinguished

1. **Reserved** — DuckDB has selected a destination path.
2. **Opened** — a direct final path or a temporary path exists.
3. **Growing** — another process can observe changing bytes.
4. **Writer-finalized** — the format writer has emitted its terminal bytes and closed.
5. **DuckDB-published** — temporary output has been moved to the final path.
6. **Client-returned** — the Python call has returned control to application code.
7. **Consumer-accepted** — a fresh reader verifies expected rows and checksum.
8. **Application-published** — an application-specific marker or manifest admits the output downstream.

The trial showed that DuckDB publication can precede client return by a small interval. At first sighting after temporary-file publication, both CSV and Parquet were exact and readable.

## Main findings

### Fresh direct output

The final pathname appeared and grew during the active query. An exact-threshold hard kill left:

- a readable CSV containing 16,384 of 100,000,000 requested rows;
- an unreadable Parquet file missing its terminal footer.

A plain final-path existence check can therefore accept incomplete CSV without detecting the failure.

### Ordinary failure cleanup

Manual interruption and low-memory failure removed the tested partial direct output and left the connection reusable. The 16 MiB low-memory case spilled about 209 MB before failure, then cleaned its temporary directory.

### Temporary-file publication

`USE_TMP_FILE true` on a fresh local path kept the final pathname absent during the incomplete write. On success, the final file was exact at first sighting. On hard death, only `tmp_<name>` remained.

### Existing local destination

DuckDB automatically chose temporary-file mode. The previous valid output remained exact through interruption and hard process death. A retry replaced the output and removed stale temporary residue.

## Source decision

The local single-file implementation behaved coherently when temporary-file mode was active. This campaign does not currently support an engine-fix thesis.

The actionable contract is:

- use `USE_TMP_FILE true` or an application-owned staging-and-publish step when creating a new local file whose final pathname signals completion;
- expect automatic staging for the tested existing local single-file replacement path;
- treat any `tmp_<name>` left after process death as recoverable residue;
- avoid extending this result to remote and multi-file outputs.

## Boundaries left open

Source resolution disables or forbids this temporary-file mechanism for several important cases:

1. remote and object-store paths;
2. partitioned output;
3. rotated multi-file output;
4. per-thread output.

Other unresolved boundaries are:

- close, move, disk-full, and permission faults;
- concurrent writers sharing one final and `tmp_<name>` path;
- filesystems with weak move durability or atomicity;
- cross-client option and cancellation contracts.

## Ranked continuation

1. Remote and object-store publication.
2. Partitioned and rotated directory publication.
3. Source failpoints around writer close and `MoveFile`.
4. Concurrent same-path writers and stale temporary collisions.
5. Cross-client behavior and user-facing documentation.

## Stop decision

The initial lane met its stop condition: the baseline is reproducible, the consumer-visible consequence is demonstrated, the source boundary is mapped, negative results are retained, and the next decisions are bounded.

No upstream contact occurred. No upstream packet was opened.

## Outputs

- `lanes/L01-python-copy-publication/report.md`
- retained probe code in the owned DuckDB fork
- durable compact result JSON under `lanes/L01-python-copy-publication/artifacts/results/`
- successful workflow run `30472702522`
- workflow artifact digest `sha256:162b10cfa7cc5fbb7b360b02836d236592de55aeb4cd2728298fa86117a8a02d`
