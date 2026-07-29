# Scout report: DuckDB query, storage, and interruption boundaries

## In simple words

DuckDB runs analytical queries inside the client process, so query cancellation, transaction state, temporary files, database files, extensions, and client connections meet in one runtime. This scout used generated data and fixed workloads to test what survives an interrupt, an out-of-memory failure, and an abrupt process exit. DuckDB 1.5.5 preserved statement atomicity, required an explicit rollback after cancelling work inside an explicit transaction, recovered a committed write from its WAL, discarded an uncommitted write, cleaned spill files after success and failure, and kept a sibling connection usable while another connection was cancelled. The strongest next campaigns concern file-sink publication during failure, cross-client cancellation contracts, and spill cost before an out-of-memory result.

## Disposition

- **Assignment:** Fieldwork issue #28
- **Programme:** `data-durable-workflows` (#16)
- **Target hub:** DuckDB (#11)
- **Worker:** `chatgpt:gpt-5.6-thinking`
- **State:** complete; ready for coordinator acceptance and campaign selection
- **Claim scope supported:** mechanism and interface; integration evidence applies to the declared Narrative DuckDB testbed only
- **Owned path:** `programmes/data-durable-workflows/scouts/duckdb-query-storage-failure-boundaries/`
- **Upstream contact authorized:** `false`
- **Upstream contact performed:** none

## Question and stop condition

**Scout question:** Which query, transaction, storage, extension, interruption, memory, and client boundaries deserve deeper campaigns under realistic deterministic workloads?

**Stop condition applied:** private-data scenarios, workloads without stable inputs and baselines, application SQL errors, and broad optimizer proposals stayed outside this scout. Generated integers, hashes, temporary database files, generated Parquet, and one owned testbed carried the evidence.

## Revision and environment pins

| Item | Pin | Role |
| --- | --- | --- |
| Fieldwork | `teamleaderleo/fieldwork@09fe47ac92ec9c0c333b4979011f6321795deff2` | claim-time protocol and report base |
| DuckDB core source | `duckdb/duckdb@11db31f8cec6e003d3d369c4b71579d4d7fd824d` | source map |
| DuckDB Python package | `duckdb==1.5.5` | executable client and embedded engine |
| Python-package provenance | `duckdb/duckdb-python@b236c8194ed14c7a7c685e0534dde501cc855b3a` | package release source recorded by PyPI |
| Parquet extension | DuckDB 1.5.5, `STATICALLY_LINKED` | extension and file-format boundary in the trial |
| Narrative DuckDB base | `teamleaderleo/narrative-duckdb@c9418ffa81f85e320d1367c91ccefd9faf4e0721` | owned testbed base |
| Narrative DuckDB trial head | `teamleaderleo/narrative-duckdb@558765d3703e0a1fa9374b30562af398693301a2` | successful deterministic probe |
| Runner | Ubuntu 24.04 hosted runner; Linux `6.17.0-1020-azure`; x86_64; glibc 2.39 | execution environment |
| Python | 3.13.14 | client runtime |

Retrieval and execution date: **2026-07-29**.

External source references:

- DuckDB core commit: https://redirect.github.com/duckdb/duckdb/commit/11db31f8cec6e003d3d369c4b71579d4d7fd824d
- DuckDB package release: https://pypi.org/project/duckdb/1.5.5/
- Python package provenance commit: https://redirect.github.com/duckdb/duckdb-python/commit/b236c8194ed14c7a7c685e0534dde501cc855b3a

## System model

A DuckDB client connection owns a `ClientContext`. Query preparation creates an executor and an active-query record. Autocommit statements receive a transaction at query start; query completion commits on success and rolls back on failure. An explicit transaction remains owned by the connection across statements. User interruption reaches the active executor through the connection context and marks an explicit transaction invalid when the error policy requires it. The caller then owns the recovery step: issue `ROLLBACK`, close the connection, or follow the binding's recovery contract.

Persistent database writes flow through transaction commit and the write-ahead log. Reopening a database replays durable WAL entries and validates supported WAL formats. Checkpointing rotates between the main WAL and a checkpoint WAL while protecting ordering with a WAL lock.

Operators that can externalize data register temporary-memory state with a database-level manager. Reservations depend on the database memory limit, per-query limit, thread count, connection count, and the presence of a temporary directory. A spill-capable operator may write substantially more temporary data than the configured memory limit before either succeeding or reporting out of memory.

Extensions load into a `DatabaseInstance`. The tested Parquet extension was statically linked to the exact DuckDB build, so the run covered extension availability and connection reuse while leaving dynamic installation, ABI mismatch, initialization failure, and load retry for later work.

## Code map

### Query execution and interruption

| Boundary | Owning code | Current behavior relevant to the scout |
| --- | --- | --- |
| Connection state | `src/main/client_context.cpp` | `ClientContext` owns interrupt state, transaction context, active query, executor, and connection lock. |
| Query begin | `ClientContext::BeginQueryInternal` | Creates an autocommit transaction when needed, assigns an active query ID, initializes progress and deadlines, and announces query begin. |
| Executor setup | `ClientContext::PendingPreparedStatementInternal` | Builds the executor and result collector, then exposes a pending result as the active open result. |
| Interrupt handling | `ClientContext::ExecuteTaskInternal` | Surfaces a pending user interrupt, records an interrupt error, and selects transaction invalidation behavior before ending the query. |
| Query end | `ClientContext::EndQueryInternal` | Cancels tasks, clears active query state, commits successful autocommit work, rolls back failed autocommit work, and invalidates an explicit transaction on qualifying failure. |
| Cleanup | `ClientContext::InitialCleanup` and `CleanupInternal` | Cancels remaining tasks, finalizes the active query, and resets the connection's interrupt state before later work. |

### Transaction ownership and rollback

| Boundary | Owning code | Current behavior relevant to the scout |
| --- | --- | --- |
| Transaction lifecycle | `src/transaction/transaction_context.cpp` | Begins one transaction per connection context, rejects nested begin, commits through `MetaTransaction`, and rolls back retained state on request or destruction. |
| Explicit transaction invalidation | `ClientContext::ExecuteTaskInternal` plus transaction validity checks | A user interrupt is treated as transaction-invalidating in the tested path. Later statements receive the aborted-transaction error until rollback. |
| Connection destruction | `ClientContext::Destroy`; `TransactionContext::~TransactionContext` | Active explicit work is rolled back as the connection context is destroyed. |

### Storage and recovery

| Boundary | Owning code | Current behavior relevant to the scout |
| --- | --- | --- |
| WAL availability | `src/storage/storage_manager.cpp` | Writable, loaded, file-backed databases expose a WAL; in-memory and read-only cases do not. |
| Checkpoint rotation | `StorageManager::WALStartCheckpoint` and `WALFinishCheckpoint` | Flushes and closes the main WAL, creates a checkpoint WAL for concurrent commits, then removes or promotes it when checkpointing finishes. |
| WAL replay | `src/storage/wal_replay.cpp` | Replays main and checkpoint WAL states; version 2 entries carry size and checksum checks, while version 3 adds encrypted-entry handling. |
| Transaction persistence | `src/transaction/duck_transaction.cpp` and WAL entry code | Committed transaction effects become replayable; uncommitted local state lacks a durable commit boundary. |

### Memory and spill

| Boundary | Owning code | Current behavior relevant to the scout |
| --- | --- | --- |
| Temporary-memory policy | `src/storage/temporary_memory_manager.cpp` | Tracks active operator states and calculates reservations from memory limit, temp-directory availability, threads, connections, and operator demand. |
| Buffer allocation and eviction | `src/storage/buffer_manager.cpp`, `src/storage/standard_buffer_manager.cpp`, buffer pool files | Owns the memory ceiling and temporary storage used by spill-capable operators. |
| Sort and COPY path | sort execution plus Parquet sink | External sort writes temp blocks; the Parquet sink publishes output after successful completion. |

### Extensions and clients

| Boundary | Owning code | Current behavior relevant to the scout |
| --- | --- | --- |
| Extension loading | `src/main/extension/extension_load.cpp`, `ExtensionManager` | Static extensions are exact-build components and are recorded as `STATICALLY_LINKED`; dynamic extensions use C/C++ ABI loading and initialization state. |
| Python binding | DuckDB Python connection implementation | Exposes `interrupt()`, transaction methods, query execution, and separate connections to the same database instance. |
| Connection isolation | `Connection`, `ClientContext`, transaction manager | Uncommitted state remains connection-local; commit changes visibility to sibling connections according to transaction snapshots. |

## Test and search map

The source search located focused coverage for the temporary-memory manager, external joins, API interruption, WAL replay, transactions, appenders, and extension loading. The scout retained a cross-boundary testbed because focused unit tests alone leave application-visible combinations unresolved:

- interrupt during a write in autocommit mode;
- interrupt during a read inside an explicit transaction, followed by another statement and rollback;
- abrupt process exit on each side of commit, then file reopen;
- sort spill feeding a Parquet sink under a fixed memory ceiling;
- cleanup of temporary files after success and out-of-memory failure;
- one connection executing and receiving interruption while a sibling connection remains usable.

The source search found no single retained case combining all of those ownership and recovery observations. This statement describes the searched revision and query set; it does not claim complete absence across every generated or downstream test suite.

## Deterministic workload contract

The retained runner is `artifacts/issue28_probe.py`. The raw output is `artifacts/results/duckdb-1.5.5-ubuntu-24.04.json`.

Common settings and inputs:

- one Python process except the deliberate crash children;
- DuckDB and Python versions pinned above;
- generated integer ranges only;
- `threads = 1` for spill trials;
- deterministic `hash(i)` sort key;
- deterministic `md5(i::VARCHAR)` payload;
- 100,000 × 100,000 cross products for interruptible work;
- timer-driven `connection.interrupt()` at 0.25 seconds;
- 50,000 inserted rows for crash recovery;
- 1,500,000 rows for sort and Parquet trials;
- 128 MB success baseline and 24 MB pressure case;
- temporary directories created per run and removed by the harness;
- no network during probe execution;
- no credentials, private data, or production files.

Exact testbed command:

```text
python fieldwork/issue28_probe.py --output fieldwork/results/issue28-latest.json
```

The GitHub Actions job used Python 3.13 and installed the pinned wheel with `pip --require-hashes`.

## Observed results

The successful run passed **26 of 26 declared invariants**.

### 1. Explicit transaction interruption

**Observed**

- A deterministic cross-product query received `InterruptException` after 0.2507 seconds.
- The connection's next statement received `TransactionException: Current transaction is aborted (please ROLLBACK)`.
- `ROLLBACK` succeeded.
- Reopening the database showed one persisted row; the 100 rows inserted inside the explicit transaction were absent.

**Interpretation**

The interrupt belongs to the active connection and ends the query. In this path it also invalidates the explicit transaction. Recovery ownership passes to the caller, which must roll back or close the connection before normal transaction-dependent work continues.

### 2. Autocommit write interruption

**Observed**

- An interrupted `INSERT ... SELECT` received `InterruptException` after 0.2512 seconds.
- The target table retained only its original row.
- The same connection immediately executed `SELECT 42` successfully.

**Interpretation**

The tested autocommit statement remained atomic. Query failure triggered automatic rollback and left the connection reusable.

### 3. Connection visibility and cancellation routing

**Observed**

- Connection A saw 101 rows inside its explicit transaction.
- Connection B saw one row before A committed and 101 after commit.
- While A ran the interruptible query, B returned `84` successfully.
- Interrupting A stopped A's query; B remained usable and still saw 101 rows.

**Interpretation**

The tested Python connections had separate client contexts and transaction views. Interruption targeted A's active query without cancelling B.

### 4. Abrupt exit and reopen

**Observed: uncommitted child**

- The child inserted 50,000 rows inside an explicit transaction and exited through `os._exit(17)` before commit.
- No WAL file existed before reopen.
- Reopen showed one row and checksum zero.

**Observed: committed child**

- The child inserted 50,000 rows, committed, and exited through `os._exit(18)` without closing the connection.
- Before reopen, the WAL existed and was 401,315 bytes.
- Reopen showed 50,001 rows and checksum 1,250,025,000.
- The WAL was absent after reopen.

**Interpretation**

The tested commit boundary survived abrupt process termination. Reopen replayed committed effects and discarded the completed WAL. Uncommitted effects remained absent.

### 5. Memory pressure, spill, cleanup, and Parquet

Workload:

```sql
COPY (
  SELECT i, md5(i::VARCHAR) AS payload
  FROM range(1500000) t(i)
  ORDER BY hash(i)
) TO '<generated path>' (FORMAT PARQUET, COMPRESSION ZSTD);
```

Settings: one thread and insertion-order preservation disabled.

**Observed: 128 MB baseline**

- Query succeeded.
- Output contained 1,500,000 rows with checksum 1,124,999,250,000.
- Peak temporary storage observed: 44,728,320 bytes.
- Temporary directory was empty after query and after connection close.
- A second connection reopened the generated Parquet and counted 1,500,000 rows.

**Observed: 24 MB pressure**

- Peak temporary storage observed: 109,445,120 bytes.
- Query reported `OutOfMemoryException` while requesting an additional 8.0 MiB at 18.2/22.8 MiB used.
- No Parquet output file remained.
- The same connection executed `SELECT 7` successfully afterward.
- Temporary directory was empty after query and after close.

**Interpretation**

The tested path cleans temporary files and avoids publishing a Parquet output after this out-of-memory failure. The operator can still write about 4.8 times the configured 22.8 MiB usable ceiling to temporary storage before reporting the allocation failure. The 128 MB baseline also spilled, showing that spill itself is ordinary behavior while spill volume and eventual success depend on operator demand and reservation choices.

### 6. Extension boundary

**Observed**

- `duckdb_extensions()` reported Parquet as installed, loaded, and `STATICALLY_LINKED` before and after the workload.
- A second connection reported the same state and read the generated file.

**Interpretation**

The run covered exact-build static extension availability and connection reuse. It provides no evidence for network installation, repository selection, dynamic ABI mismatch, extension initialization failure, or concurrent first load.

## Boundary separation

| Layer | Established in this scout | Open boundary |
| --- | --- | --- |
| SQL statement | Autocommit interrupted insert stayed atomic; explicit transaction required rollback after interrupt. | Other statement classes, streaming result consumption, multi-statement strings, and timeout settings. |
| Engine | Active-query cancellation, transaction invalidation, WAL replay, spill, cleanup, and connection-local visibility behaved consistently in the tested build. | Fault injection inside executor finalization, commit, checkpoint rotation, sink finalization, and allocation. |
| Client | Python `interrupt()` targeted one connection; the same connection or sibling remained usable according to transaction state. | C, CLI, JDBC, Node, R, ADBC, cursor wrappers, and connection pools. |
| Extension | Static Parquet remained available across connections and produced a valid file on success. | Dynamic extension installation, ABI/version compatibility, initialization rollback, and concurrent load. |
| Operating system and filesystem | `os._exit` supplied abrupt process termination; ordinary local filesystem calls preserved committed WAL recovery and removed temp files. | Power-loss semantics, short writes, failed `fsync`, full disk, permission changes, rename failure, network filesystems, and corrupted/truncated WAL. |
| Application | Narrative DuckDB supplied an owned, reversible execution surface with synthetic data. | A sustained application workflow, retries, process supervision, and user-visible recovery. |

## Negative results and dead ends

- The first interrupt harness used a Python scalar UDF as a deterministic gate. DuckDB's Python UDF registration pulled in NumPy, which the minimal environment lacked. The final runner removed the optional dependency and used timer-driven interrupts against large engine-native cross products.
- No partial Parquet output remained after the tested 24 MB out-of-memory failure.
- No temporary spill file remained after either the successful baseline or the failed pressure case.
- No uncommitted rows became visible after abrupt process exit.
- No committed rows were lost after abrupt process exit following `COMMIT`.
- A sibling connection experienced neither cancellation nor unusability when the first connection was interrupted.
- Static Parquet loading revealed no version or initialization failure. Dynamic extension behavior remains outside the evidence.
- The run establishes deterministic observations on one Linux filesystem and one released DuckDB build. It provides no benchmark claim and no ecosystem-wide client guarantee.

## Ranked campaign candidates

### 1. File-sink publication across interrupt, out of memory, and process death

**Rank reason:** highest unresolved correctness and recovery consequence at the boundary between SQL transaction outcome and externally visible files.

- **Current evidence:** the 24 MB Parquet path spilled 109,445,120 bytes, raised out of memory, and left no output. The 128 MB path published a valid file.
- **Consequence:** CSV, Parquet, extension-defined sinks, and partitioned exports can create user-visible files outside database transaction storage. A partial, stale, or prematurely discoverable file can enter a downstream workflow even when SQL reports failure.
- **Likely owning boundary:** physical COPY operators, file writer lifecycle, Parquet sink and finalize paths, partitioned-output naming, filesystem create/rename/close cleanup, client error return.
- **Evidence needed:** phase-targeted interruption and injected failures before first write, between row groups, during footer/finalize, during close, and during rename; assert path visibility, format validity, row count, checksum, temporary names, and retry behavior.
- **Bounded next question:** For each supported local sink publication mode, which failure points leave no artifact, a clearly temporary artifact, or a valid final artifact?
- **Recommendation:** open campaign.

### 2. Explicit-transaction cancellation contract across clients and timeout sources

**Rank reason:** directly observed recovery requirement with compatibility consequences for every binding that exposes cancellation or timeouts.

- **Current evidence:** Python interruption invalidated the explicit transaction; the next statement required `ROLLBACK`. Autocommit failure rolled back automatically and left the connection reusable.
- **Consequence:** a binding, pool, notebook, or job runner that surfaces only the query error may return an aborted connection to later work. Retry loops can repeatedly fail until rollback or replacement.
- **Likely owning boundary:** `ClientContext::ExecuteTaskInternal`, transaction invalidation policy, binding interrupt APIs, timeout adapters, cursor and pool cleanup.
- **Evidence needed:** a fixed matrix across Python, C API, CLI, JDBC, Node, R, and ADBC where available; manual interrupt and `max_execution_time`; read and write statements; explicit and autocommit transactions; exact post-error connection state.
- **Bounded next question:** Do supported clients expose one coherent recovery contract for user interrupt and execution timeout inside explicit transactions?
- **Recommendation:** open campaign, beginning with Python/C/CLI as the smallest cross-client slice.

### 3. Spill cost and memory-floor diagnostics before out of memory

**Rank reason:** observed resource consequence with a stable baseline and a clear measurement path.

- **Current evidence:** the 24 MB case wrote 109,445,120 temporary bytes before out of memory; the 128 MB success case wrote 44,728,320 bytes. Both cleaned up.
- **Consequence:** a low-memory workload may consume substantial disk and I/O before failure. Operators need predictable disk budgets, clear failure diagnostics, and controls that distinguish an impossible memory floor from ordinary spill.
- **Likely owning boundary:** `TemporaryMemoryManager`, buffer pool, external sort, Parquet COPY pipeline, operator minimum reservation, temp-directory capacity checks.
- **Evidence needed:** deterministic sweep over memory limits and row widths; peak temp bytes, allocation failure point, runtime, operator profile, output state, cleanup, and temp-directory-disabled case; repeat across one and several concurrent connections.
- **Bounded next question:** Can DuckDB identify and report the minimum feasible memory for this operator pipeline before producing disproportionate temporary I/O?
- **Recommendation:** open campaign after the coordinator accepts disk-amplification as the consequence threshold.

### 4. Crash injection through COMMIT and checkpoint WAL transitions

**Rank reason:** highest potential data-integrity consequence, paired with a green baseline that calls for deeper phase control before promotion.

- **Current evidence:** abrupt exit before commit discarded 50,000 rows; abrupt exit after commit recovered all 50,000 rows from a 401,315-byte WAL and removed the WAL on reopen.
- **Consequence:** failures between WAL flush, commit visibility, checkpoint marker, checkpoint-WAL promotion, main-file update, and cleanup could lose, duplicate, or reject durable state.
- **Likely owning boundary:** transaction commit, write-ahead log flush, `WALStartCheckpoint`, `WALFinishCheckpoint`, checkpoint WAL rename, replay version/checksum validation.
- **Evidence needed:** deterministic failpoints or filesystem shim at commit and checkpoint phases; reopen assertions for catalog and table changes; truncated and checksum-corrupt WAL fixtures; repeatable cleanup observations.
- **Bounded next question:** At every durable transition exposed by existing debug hooks or a local filesystem shim, does reopen yield exactly the last committed state or a clear corruption error?
- **Recommendation:** retain as a high-priority campaign candidate; begin after locating usable failpoints without carrying a large upstream patch premise.

### 5. Connection ownership, cursor aliases, streaming results, and cancellation routing

**Rank reason:** the tested separate-connection case passed, while client wrappers can create less obvious ownership relationships.

- **Current evidence:** two Python connections shared committed database state, isolated uncommitted changes, and routed interrupt to one active query.
- **Consequence:** cursor aliases, duplicated connections, module-level defaults, connection pools, and streaming results may share or retain a `ClientContext` differently. Wrong cancellation routing or close behavior can stop unrelated work, block forever, or return a poisoned connection.
- **Likely owning boundary:** Python connection and cursor wrappers, `Connection`, `ClientContext`, result ownership, database-instance cache, close and destruction paths.
- **Evidence needed:** deterministic matrix of `connect`, `cursor`, duplicate/clone APIs, streaming fetch, close during fetch, interrupt from another thread, and pool check-in after error.
- **Bounded next question:** Which Python client objects share cancellation and transaction ownership, and can the API make that ownership observable through tests and documentation?
- **Recommendation:** run a focused client scout or fold into candidate 2.

### 6. Dynamic extension load failure, ABI mismatch, and retry

**Rank reason:** important compatibility boundary with limited evidence from this scout.

- **Current evidence:** Parquet was statically linked, loaded from process start, and usable from both tested connections.
- **Consequence:** a dynamically loaded extension can fail verification, symbol lookup, ABI negotiation, initialization, or concurrent first load. Partial registration could leave a database instance in an ambiguous retry state.
- **Likely owning boundary:** `ExtensionManager::BeginLoad`, extension load state, dynamic library loader, C API version negotiation, load-failure cleanup, connection-facing SQL.
- **Evidence needed:** locally built synthetic extensions for successful load, declared initialization failure, unsupported C API version, missing symbol, concurrent load, and retry; no network access.
- **Bounded next question:** After every local dynamic-extension load failure class, does the database instance retain a clean, deterministic retry state across connections?
- **Recommendation:** run another scout before opening a campaign.

## Campaign decision

Promote candidates **1** and **2**. Candidate **3** has sufficient observed cost and a bounded sweep; promote it when the programme accepts temporary-disk amplification and failure diagnostics as a campaign consequence. Retain candidate **4** as the next data-integrity branch after confirming usable failpoints. Fold candidate **5** into candidate **2** unless the client object model expands beyond one campaign. Run a separate dynamic-extension scout for candidate **6**.

## Narrative DuckDB trial

- **Testbed:** `teamleaderleo/narrative-duckdb`
- **Base:** `c9418ffa81f85e320d1367c91ccefd9faf4e0721`
- **Branch:** `fieldwork/duckdb/issue-28-boundary-probe`
- **Successful head:** `558765d3703e0a1fa9374b30562af398693301a2`
- **Draft PR:** https://redirect.github.com/teamleaderleo/narrative-duckdb/pull/1
- **Workflow run:** `30468216997`
- **Artifact:** `fieldwork-duckdb-issue-28-results`, ID `8730475009`
- **Artifact digest:** `sha256:3368164ed21226ab5945c16c9f341c3d4bfdf1abf3501a9676e199e578d6c45b`
- **Rollback:** close the draft PR and delete the testbed branch after Fieldwork retains the runner and raw result
- **Private material retained:** none

The testbed result supports integration claims only for this declared runner and workflow. It supplies an owned execution surface, reproducible environment, and raw output; it does not establish adoption or a cross-platform client promise.

## Retained artifacts

- `artifacts/issue28_probe.py` — executable deterministic runner
- `artifacts/results/duckdb-1.5.5-ubuntu-24.04.json` — authoritative successful output
- Narrative DuckDB draft PR 1 — owned testbed execution record
- GitHub Actions artifact digest listed above — immutable run-output identity for the successful trial

## Evidence labels

- **Documented:** source-code lifecycle and ownership map at the pinned DuckDB core revision.
- **Observed:** all executable results, counts, checksums, errors, temporary-file peaks, WAL sizes, extension state, and connection behavior from the retained JSON.
- **Inferred:** likely operator and client consequences derived from documented ownership plus observed behavior.
- **Illustrative:** downstream workflows that might ingest partially published files or reuse an aborted pooled connection.
- **Unknown:** behavior on other clients, filesystems, operating systems, storage versions, dynamic extensions, checkpoint failpoints, disk-full conditions, and corrupted WAL input.

## Uncertainty and limitations

- The Python wheel packages a released DuckDB engine at v1.5.5, while the source map pins the then-current DuckDB core commit. Behavior claims come from v1.5.5 execution; source ownership claims come from the pinned core revision. A later campaign should align executable and source commits through a source build when line-level causality becomes necessary.
- Timer-driven interruption fixes the request time, while scheduler progress at that instant varies. Each query is deliberately large enough to remain active past the timer; the evidence establishes post-interrupt invariants, not a precise operator phase.
- The filesystem was the hosted runner's local Linux filesystem. Power loss, remote filesystems, full disk, failed sync, short writes, and permission changes remain open.
- The pressure case establishes one stable workload and two memory points. It is a baseline for a campaign, not a general performance result.
- Static Parquet provides extension evidence at an exact-build boundary. Dynamic extension lifecycle remains open.
- The crash child used `os._exit`, which skips language-level cleanup and models abrupt process termination. It does not emulate loss of completed kernel writes or machine power.

## Final recommendation

Accept this scout as complete. Open campaigns for file-sink publication and cross-client explicit-transaction cancellation. Decide whether the observed 109,445,120-byte spill before a 24 MB out-of-memory result clears the programme's threshold for a dedicated memory-pressure campaign. Preserve the WAL/checkpoint and dynamic-extension branches for targeted follow-up.
