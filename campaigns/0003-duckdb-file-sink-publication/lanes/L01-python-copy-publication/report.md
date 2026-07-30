# L01: Python COPY Publication Baseline

State: `complete`

Campaign: #55  
Programme: #16  
Target hub: #11  
Worker: `chatgpt:gpt-5.6-thinking`  
Owned path: `campaigns/0003-duckdb-file-sink-publication/lanes/L01-python-copy-publication/`  
Upstream contact authorized: `false`

## In simple words

A DuckDB export can put bytes at the filename before the export has finished. If the process dies, those bytes can remain.

For a new CSV file, the leftover file can look like a perfectly ordinary but shorter table. For Parquet, the leftover file rejects reads because its footer is missing.

DuckDB also has a safer temporary-file mode. In that mode it writes `tmp_<name>`, closes the writer, and moves the completed file to the final name. DuckDB turns this mode on automatically when replacing an existing local file, but not when creating a brand-new local file. A caller that treats a new filename as a completion signal should request `USE_TMP_FILE true` or perform its own staging and publication step.

## Question answered

For local, single-file CSV and Parquet `COPY` through Python DuckDB 1.5.5:

- What can another process see while the export is active?
- What remains after cancellation, low-memory failure, and abrupt process death?
- How does `USE_TMP_FILE` change the publication boundary?
- What happens when replacing an existing output?
- Can a retry recover without manual deletion?

Remote filesystems, partitioned output, rotated output, and per-thread output remain outside this lane.

## Pins and provenance

- Owned DuckDB fork source base: `teamleaderleo/duckdb@2c9e51aa33dd07e928edae66304430aeb038edd7`
- Final owned research head: `teamleaderleo/duckdb@d9d14e7f1d51694237029354ef637b0806878290`
- Research branch: `fieldwork/55-file-sink-publication`
- Owned research PR: https://redirect.github.com/teamleaderleo/duckdb/pull/1
- Python client: DuckDB 1.5.5
- Wheel SHA-256: `078e6a60dd8eedde5832f45422ca5c4a6b8c837aeabd8a56ca0b7d933f588053`
- Runner: Ubuntu 24.04, Linux 6.17 Azure x86_64, Python 3.13.14
- DuckDB execution threads: 1
- Successful workflow run: `30472702522`
- Workflow artifact: `8732359343`
- Workflow artifact digest: `sha256:162b10cfa7cc5fbb7b360b02836d236592de55aeb4cd2728298fa86117a8a02d`
- Retrieval and trial date: 2026-07-30

## Source map

### Option resolution

`src/planner/binder/statement/bind_copy.cpp` registers `USE_TMP_FILE` as a generic write option and resolves it asymmetrically:

1. remote paths return `false` before considering the user option;
2. an explicit local `USE_TMP_FILE` value is respected;
3. without an explicit value, temporary-file mode is enabled only when the local destination already exists and the output is single-file, non-partitioned, and not stdout;
4. a brand-new local destination therefore defaults to direct writing;
5. an explicit `USE_TMP_FILE` cannot be combined with per-thread output, rotation, or partitioned output.

The default overwrite mode in this binder is `COPY_ERROR_ON_CONFLICT`, but the single-file temporary replacement path successfully replaced the tested existing output and stale temporary residue.

### Physical publication

`src/execution/physical_plan/plan_copy_to_file.cpp` rewrites the physical destination to `tmp_<base-name>` when temporary-file mode is active.

`src/execution/operator/persistent/physical_copy_to_file.cpp` separates sink, combine, and finalize work. Finalization:

1. flushes the last batch;
2. finalizes and closes the format writer;
3. drains lifecycle work;
4. moves `tmp_<base-name>` to the final pathname when temporary-file mode is active.

The global-state destructor performs best-effort removal of created paths when a query fails before finalize. Abrupt process death bypasses that destructor.

### CSV writer

`src/function/table/copy_csv.cpp` initializes the writer against the chosen physical path, flushes local writer state during combine, writes any suffix or terminal newline during finalize, and then closes the writer.

### Consumer distinction

CSV and Parquet fail differently after abrupt death:

- a truncated CSV can consist entirely of complete rows and parse as a valid smaller table;
- a truncated Parquet file normally lacks terminal metadata and rejects reads.

The CSV case is the more deceptive consumer failure because readability does not prove completeness.

## Deterministic workload

Rows were generated from `range` with:

- `i::BIGINT` as the key;
- two concatenated MD5 strings as a fixed-width payload;
- exact row counts and arithmetic checksums;
- one execution thread;
- no network, private data, clock-derived values, or random seed.

The controlled cases included:

| Case | Rows | Trigger |
|---|---:|---|
| normal direct output | 500,000 | natural completion |
| direct interruption | 50,000,000 | `connection.interrupt()` after output bytes appeared |
| exact direct crash | 100,000,000 | process kill immediately after at least 1 MiB was observed |
| low memory | 2,000,000 | 16 MiB limit plus `ORDER BY hash(i)` |
| explicit temporary success | 500,000 | `USE_TMP_FILE true` on a fresh path |
| explicit temporary crash | 100,000,000 | process kill after at least 1 MiB at `tmp_<name>` |
| existing-file interruption | 100,000,000 | automatic temporary mode, then interrupt |
| existing-file crash | 100,000,000 | automatic temporary mode, then process kill |

Fresh-reader checks recorded existence, size, readability, count, checksum, minimum, maximum, retry outcome, connection reuse, temporary-file residue, and spill cleanup.

## Findings

### 1. A fresh direct destination is visible during the active query

Both direct CSV and direct Parquet paths appeared and contained non-zero bytes while the writer process was still active.

At the exact crash threshold:

| Format | First non-zero observation | Size at trigger | Surviving consumer result |
|---|---:|---:|---|
| CSV | 0.114 s | 1,152,163 bytes | readable, 16,384 rows, checksum 134,209,536 |
| Parquet | 0.115 s visible; 0.215 s non-zero | 1,048,576 bytes observed; 2,097,152 after kill | rejected: missing final magic bytes/footer |

The requested workload contained 100,000,000 rows. The surviving CSV looked valid but contained only the prefix through row 16,383.

**Consequence:** final-path existence is not a safe completion signal for a brand-new direct output.

### 2. Ordinary interruption cleaned the direct output

For both formats:

- output bytes were present before interruption;
- DuckDB raised `InterruptException`;
- the final output was absent after unwind;
- the same connection executed another statement successfully.

Observed bytes before interruption were about 1.15 MiB for CSV and 2.68 MiB for Parquet.

This supports the cleanup path for an in-process, ordinary cancellation. It does not cover process death or operating-system termination.

### 3. Low-memory failure also cleaned the direct output, after substantial spill

With a 16 MiB limit and an ordered two-million-row source:

- a zero-byte destination path was observed while the query was active;
- the query failed with `OutOfMemoryException` at roughly 15.1/15.2 MiB used;
- the destination was absent afterward;
- the connection remained reusable;
- the temporary spill directory was empty after failure.

Peak observed spill was:

- CSV: 208,732,160 bytes;
- Parquet: 208,896,000 bytes.

This is another successful cleanup result and another example of disk use greatly exceeding the configured memory limit.

### 4. A retry recovered from direct crash residue

The initial hypothesis predicted that the surviving final path would block retry. It did not.

A new `COPY` to the same path succeeded for both formats, produced exactly 1,000 rows with checksum 499,500, and replaced the residue.

Source review explains this: once crash residue exists, DuckDB's default option resolution chooses temporary-file mode for that existing local destination.

### 5. Explicit temporary mode withheld the final path until writer finalization

With `USE_TMP_FILE true` on a fresh path:

- `tmp_<name>` appeared and grew during the active write;
- the final pathname appeared only after the temporary writer had been closed and moved;
- at the first observation of the final pathname, a fresh connection read the exact 500,000 rows and checksum 124,999,750,000;
- the temporary pathname was already absent.

The final pathname appeared a small interval before the Python worker wrote its post-`execute()` completion marker. This distinguishes two boundaries:

1. DuckDB has finalized and published the file;
2. the client call has returned control to application code.

The first boundary can precede the second. In the tested cases the file was complete at first sighting.

### 6. Hard death in explicit temporary mode protected the final path

After killing the writer once `tmp_<name>` exceeded 1 MiB:

- the final path remained absent;
- the temporary path remained;
- temporary CSV was readable as 18,432 rows;
- temporary Parquet rejected reads because its footer was missing.

A new explicit temporary-file retry succeeded without manual cleanup, produced exactly 2,000 rows with checksum 1,999,000, and removed the stale temporary path.

### 7. Replacing an existing local file uses temporary mode automatically

A valid 1,000-row output was created first. A second default `COPY` to the same local path used `tmp_<name>`.

On ordinary interruption:

- the original 1,000-row final file remained exact;
- the temporary path was removed;
- the connection remained reusable.

On abrupt process death:

- the original 1,000-row final file remained exact;
- a partial temporary path remained;
- a subsequent default retry produced exactly 2,000 rows and removed the stale temporary path.

This is the strongest positive result: replacing an existing local single file preserved the previous accepted version through both interruption and abrupt death.

## Hypothesis outcomes

| Hypothesis | Outcome |
|---|---|
| Fresh final destination becomes visible before direct `COPY` completes | supported |
| Ordinary interruption removes direct partial output and preserves connection reuse | supported |
| Abrupt process death leaves direct final-path residue | supported |
| Truncated CSV may parse while truncated Parquet rejects | supported |
| Direct crash residue blocks default retry | rejected |
| Low-memory failure occurs before any destination visibility | rejected; a zero-byte path appeared, then cleanup removed it |
| Explicit temporary mode keeps an incomplete file away from the final path | supported |
| Existing local single-file replacement is staged automatically | supported |
| Publication and Python API return are the same instant | rejected; final publication preceded the post-return marker |

## Practical contract for the tested boundary

### Creating a brand-new local single file

Use one of these patterns when the final pathname is a downstream completion signal:

- `COPY ... (USE_TMP_FILE true)`; or
- write to an application-owned staging name, validate it, then rename or publish a manifest.

A plain direct `COPY` to a fresh path exposes an in-progress final pathname and can leave a misleading partial CSV after process death.

### Replacing an existing local single file

DuckDB 1.5.5 automatically used its temporary-file path in the tested default configuration. The prior valid output survived interruption and abrupt death. Applications should still handle a stale `tmp_<name>` after process death and should avoid concurrent writers to the same final name until that collision boundary is tested.

### Boundaries that this result does not cover

Do not extend this conclusion to:

- remote or object-store paths, where source resolution disables temporary-file mode;
- partitioned output;
- rotated multi-file output;
- per-thread output;
- concurrent writers sharing one final or temporary name;
- filesystem failure during close or move;
- filesystems whose move operation is not atomic or durable;
- other clients or older/newer DuckDB versions.

## Failed trials and corrections

### V1: retry-blocked assumption

The first probe passed 30 of 32 expectations. The two failures showed that same-path retry succeeded instead of being blocked. The failed hypothesis was retained and the acceptance contract was corrected.

### V2 broad crash timing

The broad matrix correctly demonstrated crash residue, but its observer waited the full 30-second window before killing. That produced multi-gigabyte residue and did not satisfy the claimed one-MiB placement. A separate exact-threshold probe corrected the control and repeated the format distinction.

### First temporary-file acceptance rule

The first temporary-file matrix passed 44 of 46 checks. It incorrectly required the final path to remain absent until a post-`execute()` marker. The result showed that DuckDB publishes during finalization immediately before the client call returns. The corrected probe inspected the file at first sighting and verified exact content.

These were probe-contract errors, not DuckDB failures.

## Decision

L01 is complete.

The evidence supports a clear user-facing publication rule and does not yet support an engine repair. The local single-file mechanism behaves coherently when temporary mode is active. The highest-value next work is where that mechanism is unavailable or where the underlying filesystem can break the move/close assumptions.

## Ranked next lanes

1. **Remote and object-store publication** — highest priority. Source resolution disables temporary mode for remote paths, so test partial visibility, multipart residue, retries, and consumer signaling in owned emulators.
2. **Partitioned and rotated output** — high priority. Explicit temporary mode is unsupported; determine directory-level completion and whether manifests or returned file lists can form a safe contract.
3. **Close, move, disk-full, and permission faults** — source-level failpoints around writer close and `MoveFile`, with exact old-file/new-file/residue checks.
4. **Concurrent same-path writers and stale `tmp_<name>` collisions** — determine whether two writers can overwrite, remove, or publish each other's staging file.
5. **Cross-client contract** — verify option availability, cancellation behavior, and error recovery in C, CLI, JDBC, Node, R, and ADBC.
6. **Documentation and diagnostics** — only after confirming whether current public documentation already makes the fresh-path versus existing-path asymmetry explicit.

## Artifacts

Owned fork code:

- `tools/fieldwork/issue55_file_sink_probe.py` — retained V1 failed hypothesis;
- `tools/fieldwork/issue55_file_sink_probe_v2.py` — broad matrix;
- `tools/fieldwork/issue55_crash_threshold_probe.py` — exact crash placement;
- `tools/fieldwork/issue55_tmp_publication_probe.py` — retained first temporary-marker assumption;
- `tools/fieldwork/issue55_tmp_publication_probe_v2.py` — corrected temporary publication matrix;
- `tools/fieldwork/requirements-issue55.txt`;
- `.github/workflows/fieldwork-issue55-file-sink.yml`.

Durable compact results:

- `artifacts/results/issue55-broad-matrix.compact.json`;
- `artifacts/results/issue55-crash-threshold.compact.json`;
- `artifacts/results/issue55-tmp-publication.compact.json`.

The workflow artifact contains the unabridged JSON for the final successful run.
