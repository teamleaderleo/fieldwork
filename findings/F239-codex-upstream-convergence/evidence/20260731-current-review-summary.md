# Current review summary

Date: 2026-07-31

## What changed in this pass

- The canonical F239 and F23 files were corrected so their present-tense state matches the active source and execution records.
- A package/dependency map was added without treating dependency presence as defect proof.
- Rollout JSONL, metadata SQLite, and history-projection SQLite were separated into distinct owners and repair paths.
- Fieldwork #390 now owns the non-exclusive rollout/SQLite reconciliation investigation.
- Terminal producer retention is being restacked on the latest inspected public Codex head `3d1d26915a303c3b4765828f973f5464f8c28c5c` because the delta is file-disjoint from its four-file fence.

## Review conclusions

- Execution carriers remain disposable and are never merge candidates.
- Owned source PRs can be reviewed and eventually merged only after exact-head execution, complete-diff review, and explicit authority for that merge.
- Public upstream remains read-only.
- Historical green receipts retain value for exact trees, while present-tense claims expire when overlapping public source moves.
- The strongest new investigation is persistence reconciliation, because current Codex intentionally permits canonical JSONL to lead rebuildable SQLite views after partial failure.

## Next bounded work

- materialize and execute the latest-head terminal source;
- re-review MCP reconnect against the overlapping public delta;
- build the #390 fault-injection state matrix;
- examine exact/native/Git/generated dependency ownership and version coherence.
