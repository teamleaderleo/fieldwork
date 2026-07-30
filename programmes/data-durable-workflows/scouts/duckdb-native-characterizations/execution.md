# DuckDB immutable native characterizations

State: `target-executed`

Owned issues: #223 and #240  
Owned DuckDB PRs: `teamleaderleo/duckdb#7` and `teamleaderleo/duckdb#8`  
Immutable public source: `duckdb/duckdb@de477da7606fc2d857f81117f0140d0550a5c42c`  
Exact Hive test head: `520052d13b567cd5546289b9e4f31c4cb4ca99cc`  
Exact window test head: `cac295334e56fd816aaefb13d09dc2716795aa2c`  
Exact Fieldwork execution source head: `908a9b55aaa506368b0480366d4e39ad7d59a183`  
Workflow merge revision: `6ac984c6eda13877b0cad7994c9e7348fd7de967`  
Native execution run: `30580996108`  
Fieldwork integrity run: `30580996072`  
Artifact: `8775602128`, digest `sha256:1a5643009c07488c685ce498bf5203ec72286ae742edbc44c472c2f495749d5c`  
Upstream contact authorized: `false`

## In simple words

Two small DuckDB tests now execute against one immutable source revision. Ordinary bounded window framing and ordinary SQL-NULL Hive marker behavior pass. The extreme window bound expands later rows to the whole partition, and a literal partition value equal to DuckDB's reserved Hive marker disappears when it collides with SQL NULL. These are accepted target findings; source repairs remain separate work.

## Why this runner existed

The owned DuckDB pull requests are intentionally one-file SQLLogic characterizations over an immutable historical source commit.

DuckDB's current broad repository workflow resolves external extensions from moving revisions. On the immutable core pin, the current `test_utils` extension no longer compiles because its `Load(DuckDB&)` override targets a newer extension API. Those broad runs stopped before either target test executed, so they provide dependency-drift evidence only.

The Fieldwork carrier excluded floating external extensions and built the exact source with the in-tree Parquet extension.

## Pinned execution

Run `30580996108`:

1. checked out exact public core `de477da...`;
2. staged the exact one-file tests from owned commits;
3. configured a Debug build with only the in-tree Parquet extension;
4. built DuckDB's native `unittest` runner;
5. invoked tests through the repository `build/*/test/run` wrapper;
6. ran independent ordinary FOLLOWING and raw Hive-marker controls;
7. required both characterizations to fail without parser, catalog, internal, or unknown-command errors;
8. retained both logs in artifact `8775602128`.

Both controls passed 1/1. Both characterizations failed at the intended result boundary on the initial run and both configured retries.

## Executed target outcomes

### FOLLOWING overflow

The exact `INT64_MAX FOLLOWING` query requests frames beyond the partition and expects every frame to be empty.

Observed result:

```text
0  0  NULL
1  3  [0, 1, 2]
2  3  [0, 1, 2]
```

Row zero remains empty. Later rows overflow the frame-start addition and expand to the whole partition. The independent ordinary `1 FOLLOWING` control passed first.

Evidence class: `target-executed`.

Leading bounded repair direction: saturate overflow of an `EXPR_FOLLOWING_ROWS` frame start to the current partition end. RANGE and GROUPS behavior remain outside this source slice.

### Hive marker collision

The partitioned write contains two logical values:

- literal string `__HIVE_DEFAULT_PARTITION__` with row id 1;
- SQL NULL with row id 2.

The native scan should return both rows with distinct identities. It returned only:

```text
1  NULL  2
```

The literal-marker row disappeared because both values map to the same partition directory. The independent compatibility control proved that SQL NULL still writes the raw Hive marker and reconstructs as SQL NULL.

Evidence class: `target-executed`.

Leading bounded repair direction: encode or escape literal partition values equal to the reserved Hive default marker while preserving the current raw marker for SQL NULL and compatibility reads.

## Evidence boundary

- broad historical-source workflow failures: invalid for target behavior;
- minimal pinned controls and characterizations: `target-executed`;
- exact raw logs: artifact `8775602128` retained for 30 days;
- production source repairs: absent;
- repair compatibility and performance: unmeasured;
- public upstream interaction: absent.

## Current disposition

**ACCEPT both bounded target findings. HOLD source-repair acceptance until each issue receives a direct owned patch, focused native regression, ordinary affected-suite gates, and complete-diff review.**

The temporary execution workflow is removed after this receipt transfer. The durable review surface is this file.