# Tests — Unit 04: preserve the literal Hive default-partition marker

## Current test contract

The regression matrix exercises one invariant: SQL NULL and the literal string `__HIVE_DEFAULT_PARTITION__` must retain distinct partition directory identities and distinct readback values.

The current target-native test is:

- [`test/sql/copy/parquet/parquet_hive_default_collision.test`](https://github.com/teamleaderleo/duckdb/blob/866c8ee8e479789000dbd3acc1fd5a0444af41c2/test/sql/copy/parquet/parquet_hive_default_collision.test)

## Exact commands

```bash
cmake -S . -B build/unit04 -G Ninja \
  -DCMAKE_BUILD_TYPE=Debug \
  -DBUILD_EXTENSIONS=parquet \
  -DFORCE_COLORED_OUTPUT=1
cmake --build build/unit04 --target unittest --parallel 2
./build/unit04/test/run 'test/sql/copy/parquet/parquet_hive_default_collision.test'
```

## Matrix

| Case | Purpose | Expected result |
| --- | --- | --- |
| fixed filename, literal plus SQL NULL | reproduce the destructive path collision | two rows, two files, raw NULL directory plus encoded literal directory |
| `{uuid}` filenames | separate file uniqueness from partition identity | both logical values survive and read distinctly |
| nested `(region, p)` partitions | exercise the value segment under multiple parent directories | north/south each retain literal and NULL children |
| raw marker compatibility | retain the established Hive NULL representation | raw marker reads as SQL NULL |

## Historical characterization and candidate evidence

| Generation | Exact source | Run / job | Result | Interpretation |
| --- | --- | --- | --- | --- |
| Fieldwork target characterization | DuckDB `de477da7606fc2d857f81117f0140d0550a5c42c`; Fieldwork executed source `908a9b55...`; Hive test head `520052d13...` | [run `30580996108`](https://github.com/teamleaderleo/fieldwork/actions/runs/30580996108) | pass | established target behavior and retained artifact evidence; integrity runs `30580996072` and `30585895531` |
| unpatched ordinary control | owned PR #7 head `85a2cf96a2e6fe67157ca0d8d8b7dc1494a8e058`, source left unpatched | [run `30599146006`](https://github.com/teamleaderleo/duckdb/actions/runs/30599146006), job `91065692552` | expected failure | SQLLogic expected two rows and observed one row, SQL NULL with `id=2`; fixed filename collision reproduced |
| historical applied-patch control | public base `de477da7606fc2d857f81117f0140d0550a5c42c` plus retained patch | [run `30599145476`](https://github.com/teamleaderleo/duckdb/actions/runs/30599145476), job `91057888706` | pass | original 11-assertion regression passed through DuckDB's native runner |
| current-head focused materialization | public base `63094a6f725af5045113dda74e291c7d604f6a88`; temporary carrier `a69d945a7b8d42ec17fb716e33a816f7c6b93e58`; clean candidate `866c8ee8e479789000dbd3acc1fd5a0444af41c2` | [run `30674271134`](https://github.com/teamleaderleo/duckdb/actions/runs/30674271134), job `91298159055` | pass | configured DuckDB with Parquet, built the native test runner, passed the expanded fixed-name/UUID/nested/raw-marker matrix, then published the clean generation |
| clean-head stock Main workflow | clean candidate `866c8ee8e479789000dbd3acc1fd5a0444af41c2` | [run `30675412769`](https://github.com/teamleaderleo/duckdb/actions/runs/30675412769) | action required; zero jobs | GitHub did not start ordinary jobs for the clean force-pushed generation; this remains a CI receipt gap |

## Clean-generation verification

Comparison of public base `63094a6f725af5045113dda74e291c7d604f6a88` with candidate `866c8ee8e479789000dbd3acc1fd5a0444af41c2` shows one commit and exactly two changed files:

1. `src/execution/operator/persistent/physical_copy_to_file.cpp`;
2. `test/sql/copy/parquet/parquet_hive_default_collision.test`.

The temporary retained patch, temporary workflow, and `fieldwork/` staging path are absent from the clean generation.

## Test-source review

The test names its own fixture tables and output roots. Assertions cover:

- logical readback values and SQL NULL identity;
- exact raw and encoded partition directory names;
- distinct output file count for the overwrite case;
- UUID filenames under both directories;
- repeated nested parents;
- compatibility with existing raw NULL directories.

The UUID control closes a gap in the earlier test: unique files alone can preserve both payloads while the shared raw partition token still collapses both logical values to SQL NULL. The nested matrix closes a second gap by exercising the repair beneath multiple first-column partition directories.

## Executed scope limits

- Parquet target-native execution only;
- Ubuntu 24.04 GitHub Actions;
- local filesystem paths;
- no external reader matrix;
- no Windows run;
- no remote object-store run;
- no whole-repository full test suite;
- no substantive stock Main workflow jobs on clean head `866c8ee8e479789000dbd3acc1fd5a0444af41c2`.

## Terminal test disposition

The current-head focused native gate passed. Ordinary clean-head CI remains unavailable in the recorded run and must be rerun on any independently human-authored replacement before public submission is considered.
