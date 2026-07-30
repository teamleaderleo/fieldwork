# DuckDB immutable native characterizations

State: `target-test-executing`

Owned issues: #223 and #240  
Owned DuckDB PRs: `teamleaderleo/duckdb#7` and `teamleaderleo/duckdb#8`  
Immutable public source: `duckdb/duckdb@de477da7606fc2d857f81117f0140d0550a5c42c`  
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

## Expected target outcomes

### FOLLOWING overflow

Current source should fail the assertions requiring an offset beyond the signed 64-bit range to produce an empty frame for every row and partition.

The independent `1 FOLLOWING` control must pass first.

### Hive marker collision

Current source should fail the assertions requiring SQL NULL and literal `__HIVE_DEFAULT_PARTITION__` to retain distinct directory and round-trip identities.

The independent raw-marker compatibility control must pass first.

## Evidence boundary

- broad DuckDB PR workflow failures: invalid for target behavior;
- minimal pinned native controls and characterizations: executing;
- source repairs: held until the exact native logs settle;
- public issue or pull-request interaction: absent.
