# Foundational Libraries, Databases, and Linux Systems Scout — Round 001

Date: 2026-07-30  
Programme: [Open-Source Ecosystems](../../STATUS.md)  
Scout issue: [#211](https://github.com/teamleaderleo/fieldwork/issues/211)

## In simple words

The strongest foundational candidates use tiny inputs to expose data loss, incorrect results, parser state errors, or silent lifecycle failure. DuckDB currently offers several pure-SQL cases. libarchive offers compact binary fixtures and buffer-boundary tests, although the first PPMd candidate gained an active fix during review. systemd offers high-consequence state-loss bugs that need VM or namespace execution.

## DuckDB first wave

Repository: `duckdb/duckdb`

### Deep dive — reserved Hive partition collision

Issue: [partitioned COPY collision issue](https://redirect.github.com/duckdb/duckdb/issues/24308)  
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
- output paths are distinct;
- existing Hive-compatible reads still recognize the default marker.

### Design questions

A fix needs a reversible namespace rule for literal values equal to the reserved marker. Candidate directions:

- escape the literal marker to a distinct on-disk value during writes;
- include an explicit encoded-literal prefix;
- reject the collision with a clear error until a compatibility-safe encoding is chosen.

The read side must preserve existing Hive datasets. A writer-only escaping rule with backward-compatible reading may offer the smallest boundary.

### Other DuckDB candidates

- [large FOLLOWING-frame issue](https://redirect.github.com/duckdb/duckdb/issues/24307) — huge offsets produce non-empty frames and full-table members.
- [high-precision median issue](https://redirect.github.com/duckdb/duckdb/issues/24314) — `quantile_cont` and `median` miscompute two DECIMAL(38,0) values.
- [optimizer divergence A](https://redirect.github.com/duckdb/duckdb/issues/24306), [B](https://redirect.github.com/duckdb/duckdb/issues/24303), and [C](https://redirect.github.com/duckdb/duckdb/issues/24302) — optimizer-disabled queries return different results.
- [`equi_width_bins()` loop issue](https://redirect.github.com/duckdb/duckdb/issues/24282) — integer division can yield a zero step.

All are pure-SQL candidates. Run the partition collision first because its storage consequence and owning code are already clear.

## libarchive reference and capability queue

Repository: `libarchive/libarchive`

### Active-fix stop — PPMd small-buffer issue

The [PPMd small-buffer issue](https://redirect.github.com/libarchive/libarchive/issues/3337) gained [active PR #3340](https://redirect.github.com/libarchive/libarchive/pull/3340) during the live review refresh.

The pull request owns the same consequence and reproducer boundary:

- PPMd exhausts one input block and reads ahead into another;
- the additional consumed bytes were not included in the input count;
- the bytes can be replayed on the next read and corrupt extraction;
- the regression uses four PPMd entries with 1000-byte input blocks.

Stop independent implementation. Retain it as a strong parser-state packet:

- distinguish physical input supplied from logical input consumed;
- account for refill reads at one authoritative boundary;
- prevent reads beyond the pack-stream boundary;
- preserve a fixture whose behavior changes only with caller read size;
- run focused and adjacent 7-Zip controls.

### Remaining candidate queue

1. [Windows signed-shift issue](https://redirect.github.com/libarchive/libarchive/issues/3283) — file-information conversion reaches undefined behavior under CLANG64 UBSan.
2. [`locale_charset` declaration issue](https://redirect.github.com/libarchive/libarchive/issues/3338) — one CMake configuration misses the declaration.
3. [wide-inode cpio test issue](https://redirect.github.com/libarchive/libarchive/issues/3314) — tests fail intermittently on filesystems whose inode numbers exceed archive fields.

These remain capability- or configuration-gated. Recheck pull requests and issue comments before promotion.

### Duplicate stop — standalone AppleDouble entries

The [standalone AppleDouble issue](https://redirect.github.com/libarchive/libarchive/issues/3310) already has [a focused fix PR](https://redirect.github.com/libarchive/libarchive/pull/3334).

The source itself documents the filename-only `._` detection as brittle. `is_mac_metadata_entry()` checks only whether the final path component begins with `._`; the reader then consumes it as metadata for a following entry. The active fix validates the following ordinary tar header and preserves standalone files.

Retain this as a model for ambiguous-parser fixes:

- state the heuristic;
- demonstrate the false match with a real fixture;
- validate the contextual pairing before consuming input;
- cover valid pairs, mismatches, adjacent standalone entries, and end-of-archive.

## systemd first wave

Repository: `systemd/systemd`

### Deep dive — oomd registration loss

Issue: [oomd reload-registration issue](https://redirect.github.com/systemd/systemd/issues/43174)  
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

- [router-advertisement solicitation issue](https://redirect.github.com/systemd/systemd/issues/43205) — a discarded lifetime-zero advertisement cancels pending solicitation.
- [TPM renumbering issue](https://redirect.github.com/systemd/systemd/issues/43210) — device numbering races during switchroot.
- [journald resume crash](https://redirect.github.com/systemd/systemd/issues/43168) — requires suspend/resume reproduction or a virtualized equivalent.

## Environment map

| Candidate | Current CI | Privileged | VM | Windows | Kernel/device |
|---|---:|---:|---:|---:|---:|
| DuckDB partition collision | yes | | | | |
| DuckDB window/median cases | yes | | | | |
| libarchive CMake/inode cases | yes | | | | |
| libarchive signed shift | | | | yes | |
| systemd oomd reload | | likely | yes | | cgroup v2/PSI |
| systemd router advertisement | | yes | optional | | network namespace |
| systemd TPM renumbering | | | yes | | TPM/vtpm |

## Return

- **Promote first:** DuckDB partition-path collision.
- **Parallel pure-SQL queue:** DuckDB window frame and high-precision median.
- **Active-fix reference:** libarchive PPMd short reads through PR #3340; stop duplicate implementation.
- **VM promotion:** systemd oomd registration through Linux Fieldwork.
- **Capability queues:** libarchive Windows signed shift and systemd TPM renumbering.
- **Stop duplicate implementation:** PPMd small-buffer handling and standalone AppleDouble parsing.
- **Next expansion:** curl/HTTP parsing and container lifecycle after the first promoted fixtures are executable.