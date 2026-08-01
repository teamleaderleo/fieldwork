# Tests — Unit 04: preserve the literal Hive default-partition marker

## Current test contract

Distinct logical partition values must retain distinct path identities, readback values, and filter constants:

- SQL NULL → raw `__HIVE_DEFAULT_PARTITION__`;
- literal `__HIVE_DEFAULT_PARTITION__` → `%5F_HIVE_DEFAULT_PARTITION__`;
- literal `%5F_HIVE_DEFAULT_PARTITION__` → `%255F_HIVE_DEFAULT_PARTITION__`.

Current test at exact source head:

- [`test/sql/copy/parquet/parquet_hive_default_collision.test`](https://github.com/teamleaderleo/duckdb/blob/1c931ed41822f0e27d66afb636be2730695dcf8d/test/sql/copy/parquet/parquet_hive_default_collision.test)

## Exact source and execution

- public base: `81fcce7fa76a320dc65be54cb0825e5315ac6f5b`;
- clean source head: `1c931ed41822f0e27d66afb636be2730695dcf8d`;
- execution carrier head: `67d78b2611cab36eb9736685ff86b6020e5a6667`;
- execution run: [`30696673877`](https://github.com/teamleaderleo/duckdb/actions/runs/30696673877);
- execution job: `91360634513`;
- execution carrier PR: [`teamleaderleo/duckdb#19`](https://github.com/teamleaderleo/duckdb/pull/19).

The carrier workflow checks out `1c931ed...` directly. Its workflow commit does not enter the source build.

## Exact commands in the owner-review carrier

```bash
make test_ci
make -j4 format_tools
make format-check-silent enum-integrity-check extension-patch-check -j2 -Otarget
make generate-files
git diff --exit-code

cmake -S . -B build/unit04-owner-review -G Ninja \
  -DCMAKE_BUILD_TYPE=Debug \
  -DBUILD_EXTENSIONS=parquet \
  -DFORCE_COLORED_OUTPUT=1
cmake --build build/unit04-owner-review --target unittest --parallel 2
./build/unit04-owner-review/test/run \
  'test/sql/copy/parquet/parquet_hive_default_collision.test'
./build/unit04-owner-review/test/run
```

The workflow first asserts that the clean source is one commit over the exact public base and changes only the two owned files.

## Regression matrix

| Case | Purpose | Expected result |
| --- | --- | --- |
| fixed filename, literal plus SQL NULL | reproduce destructive collision | two rows, two files, raw NULL directory plus encoded literal directory |
| equality filter on literal marker | exercise path-derived filter pruning | returns only literal row |
| `IS NULL` filter | exercise path-derived NULL pruning | returns only NULL row |
| `{uuid}` filenames | separate file uniqueness from partition identity | both logical values survive and read distinctly |
| encoded-token alias | prove codec injectivity | marker, `%5F...` literal, and NULL use three distinct paths and values |
| nested `(region, p)` | exercise value segment beneath repeated parents | north and south retain literal and NULL children independently |
| raw marker compatibility | retain established Hive NULL contract | raw marker reads as SQL NULL |

## Historical and current evidence

| Generation | Exact source | Run / job | Result | Interpretation |
| --- | --- | --- | --- | --- |
| Fieldwork characterization | DuckDB `de477da7606fc2d857f81117f0140d0550a5c42c` | run `30580996108` | pass | target behavior and retained artifact evidence |
| unpatched control | owned PR #7 head `85a2cf96a2e6fe67157ca0d8d8b7dc1494a8e058` | run `30599146006`, job `91065692552` | expected failure | two rows expected; one SQL NULL row observed |
| historical patched control | public base `de477da...` plus retained patch | run `30599145476`, job `91057888706` | pass | original native regression accepted mechanism |
| prior current-head materialization | base `63094a6f725af5045113dda74e291c7d604f6a88`, clean `866c8ee8e479789000dbd3acc1fd5a0444af41c2` | run `30674271134`, job `91298159055` | pass | fixed-name, UUID, nested, and raw-marker matrix passed |
| refreshed stock Main | clean `1c931ed41822f0e27d66afb636be2730695dcf8d` | run `30696400414` | pending with zero jobs | queue/approval receipt, no code evidence |
| refreshed owner-review carrier | clean `1c931ed41822f0e27d66afb636be2730695dcf8d` | run `30696673877`, job `91360634513` | queued when this packet generation was written | exact-head prepare, focused, and complete native runner |

## Source review of new controls

### Encoded-token alias

DuckDB's URL encoder leaves underscores unchanged and encodes percent as `%25`. The selected marker escape `%5F...` therefore remains distinct from a user's literal string `%5F...`, which writes as `%255F...`. The existing URL decoder reverses each spelling to its intended literal.

### Filter pruning

`MultiFileReader` derives Hive partition constants through `HivePartitioning::GetValue` before file open. Equality and `IS NULL` filters therefore test the reader/planner path that can prune files using directory values.

## Clean-generation verification

Comparison `81fcce7...1c931ed` shows:

- one commit ahead;
- zero commits behind;
- exactly two changed files;
- source: +5/-1;
- target test: new file;
- no workflow, patch carrier, or Fieldwork path in the clean source branch.

## Executed scope limits

Historical/current evidence covers Ubuntu 24.04, local filesystem paths, Parquet, and DuckDB's native SQLLogic runner. The current exact-head carrier also requests the complete native unit-test runner.

Unexecuted limits retained:

- external Spark/Arrow/Polars readers;
- Windows;
- remote object stores;
- format-specific matrices outside Parquet.

## Current test disposition

**EXECUTE.** The implementation and test source are accepted for owner inspection. Formal `READY` follows a successful terminal result from run `30696673877`; any failure must be preserved and repaired on unit 04 before the disposition advances.
