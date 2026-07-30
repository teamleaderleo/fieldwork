# DuckDB immutable native characterizations

State: `target-executed`

Owned issues: #223 and #240  
Owned DuckDB PRs: `teamleaderleo/duckdb#7` and `teamleaderleo/duckdb#8`  
Immutable public source: `duckdb/duckdb@de477da7606fc2d857f81117f0140d0550a5c42c`  
Exact Hive test head: `520052d13b567cd5546289b9e4f31c4cb4ca99cc`  
Exact window test head: `cac295334e56fd816aaefb13d09dc2716795aa2c`  
Exact execution source head: `b0b0e757c864e8f5bfd153749d318663bcd0ea47`  
Native execution run: `30579081717`  
Fieldwork integrity run: `30579081580`  
Upstream contact authorized: `false`

## Why this runner exists

The owned DuckDB pull requests are intentionally one-file native SQLLogic characterizations over an immutable historical source commit.

DuckDB's current repository workflow resolves external extensions from moving revisions. On the immutable core pin, the current `test_utils` extension no longer compiles because its `Load(DuckDB&)` override targets a newer extension API. The public-style PR runs therefore failed before either native test executed.

That failure is dependency drift in the broad CI harness, not evidence for or against either target behavior.

## Pinned execution

The Fieldwork workflow:

1. checks out exact public core `de477da...`;
2. stages the exact one-file tests from owned commits;
3. configures a minimal Debug build with only the in-tree Parquet extension;
4. builds DuckDB's native `unittest` runner;
5. invokes tests through the repository `build/*/test/run` wrapper;
6. proves independent ordinary FOLLOWING and raw Hive-marker controls pass;
7. requires both defect characterizations to fail without parser, catalog, internal, or unknown-command errors;
8. retains both logs as one workflow artifact.

Run `30579081717` passed this complete gate. Both independent controls passed. Both characterizations failed at the intended result boundary on every retry.

## Executed target outcomes

### FOLLOWING overflow

The exact `INT64_MAX FOLLOWING` query should produce empty frames for every row because each requested frame lies beyond the partition.

Observed result:

```text
0  0  NULL
1  3  [0, 1, 2]
2  3  [0, 1, 2]
```

Row zero remains empty. Later rows overflow the frame-start addition and expand to the whole partition. The independent ordinary `1 FOLLOWING` control passed first.

Evidence class: `target-executed`.

Leading bounded repair direction: on overflow of an `EXPR_FOLLOWING_ROWS` frame start, saturate to the current partition end. Keep RANGE and GROUPS behavior outside this source slice.

### Hive marker collision

The exact partitioned write contains two logical values:

- literal string `__HIVE_DEFAULT_PARTITION__` with row id 1;
- SQL NULL with row id 2.

The native scan should return both rows with distinct logical identities. It returned only:

```text
1  NULL  2
```

The literal-marker row disappeared because both logical values map to the same partition directory. The independent NULL compatibility control proved that SQL NULL still writes the raw Hive marker and reconstructs as SQL NULL.

Evidence class: `target-executed`.

Leading bounded repair direction: encode or escape literal partition values that equal the reserved Hive default marker while preserving the current raw marker for SQL NULL and compatibility reads.

## Evidence boundary

- broad DuckDB PR workflow failures: invalid for target behavior;
- minimal pinned native controls and characterizations: `target-executed`;
- exact behavioral receipts: retained by run `30579081717`;
- production source repairs: absent;
- performance and compatibility impact of either repair: unmeasured;
- public issue or pull-request interaction: absent.

## Current disposition

**ACCEPT both bounded target findings. HOLD production repair acceptance until each issue receives a direct owned source patch, focused native regression, ordinary affected-suite gates, and complete-diff review.**
