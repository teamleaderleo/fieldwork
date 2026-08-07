# C API Arrow multi-column ownership refresh — 2026-08-08

## Status

`SUPERSEDED DUPLICATE — canonical confirmation is private PR #29; active repair is #32`

This note records a useful current-main source refresh that was started from a stale handoff. It does not supersede the canonical completed characterization in [`arrow-capi-zero-copy-ownership.md`](arrow-capi-zero-copy-ownership.md).

## What happened

Before the current packet state was re-read, a new private characterization was prepared on public DuckDB source `e500d77864fe565f90e68f06d729c25b11e775c5` and opened as `teamleaderleo/duckdb#34`.

The canonical packet was then refreshed and showed that the same ownership defect had already been confirmed more strongly by closed private PR `teamleaderleo/duckdb#29`, with focused repair `teamleaderleo/duckdb#32` already active.

PR #34 was therefore retitled as a superseded duplicate and closed without merge. No public upstream interaction occurred.

## Useful retained observation

The current-main refresh still establishes that the source pattern remained present at `duckdb/duckdb@e500d77864fe565f90e68f06d729c25b11e775c5` on 2026-08-07:

- `duckdb_data_chunk_from_arrow` still assigns root ownership inside the per-column loop;
- primitive `DirectConversion` remains zero-copy through `FlatVector::SetData`.

This is compatibility/relevance evidence for the already-confirmed #29 defect. It is not a separate characterization result and should not create a second repair lane.

## Canonical evidence

Use the packet's existing lane instead:

- confirmed characterization: `teamleaderleo/duckdb#29`;
- exact pre-fix signature:

```text
root release count after source chunk destroy=1
surviving second output=-9999,-9999,-9999
```

- focused repair: `teamleaderleo/duckdb#32`;
- repair model: one shared root owner assigned to every column state.

As of this 2026-08-08 continuation, #32's focused repair workflow and ordinary Main are both green on its pinned base. Artifact inspection and current-main refresh are the meaningful next ownership steps.

## Cleanup receipt

- duplicate private PR: `teamleaderleo/duckdb#34`;
- state: closed;
- merged: false;
- production source changes: none;
- public DuckDB writes: none.

## Authority

- public DuckDB contact: not authorized;
- public repository writes: none;
- this note does not claim a new unit;
- do not reopen #34 unless it serves a specifically different current-main validation purpose.
