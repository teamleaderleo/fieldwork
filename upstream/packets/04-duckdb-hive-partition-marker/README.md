# Unit 04 — DuckDB literal Hive default-partition marker

## Disposition

**HOLD**

The owned candidate reserves raw `__HIVE_DEFAULT_PARTITION__` for SQL NULL and URL-escapes the exact literal value before directory creation. Historical native execution accepts the mechanism; current-head execution refreshes it with UUID and nested multi-column controls.

Public submission remains blocked by DuckDB's current request to avoid LLM-generated pull requests and by the absence of authorization to contact public upstream.

## Canonical records

| Record | Location |
| --- | --- |
| packet directory | `upstream/packets/04-duckdb-hive-partition-marker/` |
| packet branch | [`teamleaderleo/fieldwork:upstream/04-duckdb-hive-partition-marker`](https://github.com/teamleaderleo/fieldwork/tree/upstream/04-duckdb-hive-partition-marker/upstream/packets/04-duckdb-hive-partition-marker) |
| owned target branch | [`teamleaderleo/duckdb:upstream/04-hive-default-partition-marker`](https://github.com/teamleaderleo/duckdb/tree/upstream/04-hive-default-partition-marker) |
| owned research PR | [`teamleaderleo/duckdb#18`](https://github.com/teamleaderleo/duckdb/pull/18) |
| historical evidence PR | [`teamleaderleo/duckdb#7`](https://github.com/teamleaderleo/duckdb/pull/7) |
| owning finding | [`teamleaderleo/fieldwork#223`](https://github.com/teamleaderleo/fieldwork/issues/223) |
| unit coordination | [`teamleaderleo/fieldwork#435`](https://github.com/teamleaderleo/fieldwork/issues/435) |
| existing public issue | [`duckdb/duckdb#24308`](https://github.com/duckdb/duckdb/issues/24308) |

## Exact revisions

- current public base inspected: `63094a6f725af5045113dda74e291c7d604f6a88`;
- historical public base executed: `de477da7606fc2d857f81117f0140d0550a5c42c`;
- historical owned evidence head: `85a2cf96a2e6fe67157ca0d8d8b7dc1494a8e058`;
- temporary current-head carrier: `a69d945a7b8d42ec17fb716e33a816f7c6b93e58`;
- exact clean source head: recorded in the latest unit 04 handoff on issue #435 after materialization;
- exact packet head: recorded in the latest unit 04 handoff on issue #435 after final packet receipt updates.

## Intended clean diff

1. `src/execution/operator/persistent/physical_copy_to_file.cpp`
2. `test/sql/copy/parquet/parquet_hive_default_collision.test`

The clean source generation must contain only these two changes relative to public base `63094a6f725af5045113dda74e291c7d604f6a88`.

## Evidence summary

| Evidence | Result |
| --- | --- |
| unpatched ordinary control, run `30599146006`, job `91065692552` | expected failure: two rows expected, one SQL NULL row observed |
| historical applied-patch run `30599145476`, job `91057888706` | pass: original native 11-assertion regression |
| Fieldwork characterization run `30580996108` | pass: target behavior and artifact evidence retained |
| current materialization run `30674271134`, job `91298159055` | current-head expanded matrix; exact terminal result recorded in `TESTS.md` and #435 handoff |

## Packet contents

- [`DEEP_DIVE.md`](./DEEP_DIVE.md) — source map, failure model, compatibility, risks, and reversing evidence;
- [`APPROACHES.md`](./APPROACHES.md) — selected mechanism, alternatives, losing approaches, and prior art;
- [`TESTS.md`](./TESTS.md) — exact commands, matrix, historical receipts, and current execution;
- [`UPSTREAM_ISSUE.md`](./UPSTREAM_ISSUE.md) — duplicate-check result and authorized-human supplemental detail;
- [`UPSTREAM_PR.md`](./UPSTREAM_PR.md) — policy-held human rewrite brief;
- [`REVIEW.md`](./REVIEW.md) — full-diff review and continuation gate.

## Remaining blockers

1. DuckDB's current contribution guide asks contributors to avoid LLM-generated pull requests.
2. Public upstream contact is unauthorized.
3. A fresh independently human-authored source and test replacement requires current native and ordinary gates.

Execution gaps retained as limits: external readers, non-Parquet formats, Windows, remote object stores, and full-suite coverage.

## Continuation gate

A human continuation should start from the public issue and current source, independently derive a fresh implementation, run the target-native and ordinary project gates, recheck current policy and duplicate work, then request explicit authorization before contacting DuckDB.

The latest issue #435 handoff is the generation receipt for the exact source head, packet head, terminal tests, and public-contact state.
