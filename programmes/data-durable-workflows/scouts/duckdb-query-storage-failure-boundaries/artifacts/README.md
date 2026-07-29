# DuckDB issue 28 retained artifacts

## In simple words

These files preserve the successful deterministic run used by the DuckDB boundary scout.

## Run identity

- Fieldwork issue: #28
- DuckDB Python and embedded engine: 1.5.5
- Testbed: `teamleaderleo/narrative-duckdb`
- Testbed base: `c9418ffa81f85e320d1367c91ccefd9faf4e0721`
- Testbed successful head: `558765d3703e0a1fa9374b30562af398693301a2`
- Testbed draft PR: `teamleaderleo/narrative-duckdb#1`
- Workflow run: `30468216997`
- Workflow artifact ID: `8730475009`
- Workflow artifact digest: `sha256:3368164ed21226ab5945c16c9f341c3d4bfdf1abf3501a9676e199e578d6c45b`
- Execution date: 2026-07-29
- Upstream contact authorized: `false`

## Files

- `issue28_probe.py` — runner copied from the successful testbed head.
- `results/duckdb-1.5.5-ubuntu-24.04.json` — raw output copied from the successful workflow artifact.

## Reproduction

Create a Python 3.13 environment, install `duckdb==1.5.5`, then run:

```text
python artifacts/issue28_probe.py --output issue28-latest.json
```

The original testbed installed the CPython 3.13 Linux wheel with SHA-256:

```text
078e6a60dd8eedde5832f45422ca5c4a6b8c837aeabd8a56ca0b7d933f588053
```

The runner uses generated integers, hashes, temporary database files, and generated Parquet only. Probe execution makes no network calls.
