# Foundational Libraries, Databases, and Linux Systems Scout — Round 001

Date: 2026-07-30  
Programme: [Open-Source Ecosystems](../../STATUS.md)  
Scout issue: [#211](https://github.com/teamleaderleo/fieldwork/issues/211)

## In simple words

The strongest foundational candidates use tiny inputs to expose data loss, incorrect results, parser state errors, or silent lifecycle failure. DuckDB currently offers several pure-SQL cases. libarchive offers compact binary fixtures and buffer-boundary tests. systemd offers high-consequence state-loss bugs that need VM or namespace execution.

## DuckDB first wave

Repository: `duckdb/duckdb`

### Deep dive — reserved Hive partition collision

Issue: [#24308](https://github.com/duckdb/duckdb/issues/24308)  
Owning code: `src/execution/operator/persistent/physical_copy_to_file.cpp`  
Adjacent test: `test/sql/copy/parquet/parquet_hive_null.test`

The partition directory builder emits:

```cpp
if (partition_value.IsNull()) {
    p_dir += "__HIVE_DEFAULT_PARTITION__";
} else {
    p_dir += HivePartitioning::Escape(partition_value.ToString());
}
```

A real SQL NULL and the literal string `__HIVE_DEFAULT_PARTITION__` therefore map to the same directory. Partitioned COPY can overwrite or merge files under one path and lose the distinction between rows.

The adjacent test file already covers:

- writing actual NULL as `__HIVE_DEFAULT_PARTITION__`;
- reading that marker as NULL;
- preserving the literal string `NULL` as a string.

It does not cover a literal value equal to the reserved marker.

### First executable probe

Add a test with two rows:

```sql
CREATE TABLE t AS
SELECT * FROM (VALUES ('__HIVE_DEFAULT_PARTITION__', 1), (NULL, 2)) v(p, id);

COPY t TO '...' (FORMAT PARQUET, PARTITION_BY (p), OVERWRITE);
```

Then assert:

- two rows survive a globbed read;
- one row remains SQL NULL;
- one row remains the exact literal string;
- the output paths are distinct;
- existing Hive-compatible reads still recognize the default marker.

### Design questions

A fix needs a reversible namespace rule for literal values equal to the reserved marker. Candidate directions:

- escape the literal marker to a distinct on-disk value during writes;
- include an explicit encoded-literal prefix;
- reject the collision with a clear error until a compatibility-safe encoding is chosen.

The read side must preserve existing Hive datasets. A writer-only escaping rule with backward-compatible reading may offer the smallest boundary.

### Other DuckDB candidates

- [#24307](https://github.com/duckdb/duckdb/issues/24307) — huge `ROWS ... FOLLOWING` offsets produce non-empty frames and full-table members.
- [#24314](https://github.com/duckdb/duckdb/issues/24314) — `quantile_cont` and `median` miscompute two DECIMAL(38,0) values.
- [#24306](https://github.com/duckdb/duckdb/issues/24306), [#24303](https://github.com/duckdb/duckdb/issues/24303), and [#24302](https://github.com/duckdb/duckdb/issues/24302) — optimizer-disabled queries return different results.
- [#24282](https://github.com/duckdb/duckdb/issues/24282) — `equi_width_bins()` can loop indefinitely when integer division yields a zero step.

All are pure-SQL candidates. Run #24308 first because its storage consequence and owning code are already clear.

## libarchive first wave

Repository: `libarchive/libarchive`

### Candidate queue

1. [#3337](https://github.com/libarchive/libarchive/issues/3337) — 7z PPMd decompression fails when callers use small read buffers. This is a strong current-CI parser/refill candidate.
2. [#3283](https://github.com/libarchive/libarchive/issues/3283) — signed left shift in Windows file-information conversion reaches undefined behavior under CLANG64 UBSan. Requires a Windows environment and an explicit policy for values above `INT64_MAX`.
3. [#3338](https://github.com/libarchive/libarchive/issues/3338) — `locale_charset` is used without a declaration in one CMake configuration. Investigate feature detection and header ownership.
4. [#3314](https://github.com/libarchive/libarchive/issues/3314) — cpio tests fail intermittently on filesystems with inode numbers wider than the archive format fields. Good portability/test-fixture candidate.

### Duplicate stop — standalone AppleDouble entries

Issue [#3310](https://github.com/libarchive/libarchive/issues/3310) already has [PR #3334](https://github.com/libarchive/libarchive/pull/3334).

The source itself documents the filename-only `._` detection as brittle. `is_mac_metadata_entry()` checks only whether the final path component begins with `._`; the reader then consumes it as metadata for a following entry. PR #3334 validates the following ordinary tar header and preserves standalone files.

Retain this as a model for ambiguous-parser fixes:

- state the heuristic;
- demonstrate the false match with a real fixture;
- validate the contextual pairing before consuming input;
- cover valid pairs, mismatches, adjacent standalone entries, and end-of-archive.

## systemd first wave

Repository: `systemd/systemd`

### Deep dive — oomd registration loss

Issue: [#43174](https://github.com/systemd/systemd/issues/43174)  
Subscriber: `src/oom/oomd-manager.c`  
Publisher: `src/core/varlink.c`  
Test area: `test/units/TEST-55-OOMD.sh`

The issue reproduces on systemd 259 and 261. `user@<uid>.service` is initially monitored for memory pressure. Running `systemctl --user daemon-reload` removes it from `oomctl`, while the unit stays active and retains `ManagedOOMMemoryPressure=kill`. Restarting oomd restores registration until the next reload.

Relevant behavior:

- oomd observes `io.systemd.ManagedOOM.SubscribeManagedOOMCGroups` through a persistent Varlink connection;
- `process_managed_oom_message()` removes a path when a message reports `MANAGED_OOM_AUTO`;
- PID 1 publishes initial and incremental ManagedOOM state from unit cgroup contexts;
- user managers report their own units through a separate Varlink direction.

### First executable probe

Use a VM with cgroup v2 and memory pressure support:

1. configure `ManagedOOMMemoryPressure=kill` on `user@.service`;
2. enable and start `systemd-oomd`;
3. create a lingering user and wait for initial registration;
4. capture Varlink/manager debug logs or instrument the send path;
5. run the user-manager reload;
6. identify the exact notification that removes the PID 1-owned path;
7. verify whether any later update attempts to restore it;
8. add a `TEST-55-OOMD.sh` assertion around the reload.

The key question is whether reload transiently reports AUTO from PID 1, clears cgroup runtime state, or triggers an update from the wrong manager without a matching re-registration.

### Other systemd candidates

- [#43205](https://github.com/systemd/systemd/issues/43205) — a lifetime-zero router advertisement cancels the pending initial solicitation even though networkd discards the advertisement. Route through a network namespace.
- [#43210](https://github.com/systemd/systemd/issues/43210) — TPM device renumbering race during switchroot. Route through a TPM-enabled VM.
- [#43168](https://github.com/systemd/systemd/issues/43168) — journald crash after resume. Requires suspend/resume reproduction or a virtualized equivalent.

## Environment map

| Candidate | Current CI | Privileged | VM | Windows | Kernel/device |
|---|---:|---:|---:|---:|---:|
| DuckDB #24308 | yes | | | | |
| DuckDB #24307/#24314 | yes | | | | |
| libarchive #3337/#3338/#3314 | yes | | | | |
| libarchive #3283 | | | | yes | |
| systemd #43174 | | likely | yes | | cgroup v2/PSI |
| systemd #43205 | | yes | optional | | network namespace |
| systemd #43210 | | | yes | | TPM/vtpm |

## Return

- **Promote first:** DuckDB #24308.
- **Parallel pure-SQL queue:** DuckDB #24307 and #24314.
- **Current-CI library probe:** libarchive #3337.
- **VM promotion:** systemd #43174 through Linux Fieldwork.
- **Capability queues:** libarchive #3283 and systemd #43210.
- **Stop duplicate implementation:** libarchive #3310.
- **Next expansion:** curl/HTTP parsing and container lifecycle after these first fixtures are executable.