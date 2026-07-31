# Current-main receipt decision-boundary carrier

Date: 2026-07-31  
Canonical campaign: Fieldwork #83  
Exact Codex source base: `f7265553ea1510304f3091833dcbce65ef21f10c`  
Publisher branch: `fieldwork/83-current-main-domain-boundary-publisher-f72655`  
Publisher head: `0eb61e4efdc67cf628171dd7d5e8e3d65c7e7fe3`  
Output branch: `fieldwork/83-current-main-domain-boundary-f72655`

## Purpose

Current Codex `main` already owns receipt DTOs, a live session ledger, selected-runtime effect capture, lifecycle terminal updates, direct-result append observation, and a raw compaction identity validator. Review found that compaction decision authority still lives on the public serializable DTO and the two compaction safety checks remain disconnected from compaction entry points.

This first current-main repair creates one private core decision boundary without yet changing compaction behavior.

## Exact publisher fence

- `.github/scripts/fieldwork_83_current_main_domain_boundary.py`
- `.github/workflows/fieldwork-83-current-main-domain-boundary-f72655.yml`

The publisher branch is a direct descendant of `f7265553...` and differs by exactly these two files.

## Exact five-file product fence

- `codex-rs/tools/src/tool_operation.rs`
- `codex-rs/tools/src/tool_operation_tests.rs`
- `codex-rs/core/src/state/tool_operation_receipts.rs`
- `codex-rs/core/src/state/tool_operation_receipts_tests.rs`
- `codex-rs/core/src/session/tool_operation.rs`

## Repair contract

- removes `ToolOperationReceipt::is_compaction_ready()` from the public serializable DTO;
- keeps the DTO information-preserving and leaves future versions visible;
- moves the potential-mutation readiness predicate into the private core ledger;
- requires the current receipt version before a potentially mutating operation can be reconciled;
- exposes one session-owned `validate_compaction_tool_operation_state()` precondition that checks raw call/output identity and live mutation certainty under one state snapshot;
- leaves local and remote compaction call sites unchanged for the next stacked slice.

## Execution gate

- exact two-file publisher fence;
- exact five-file product fence after formatting;
- five uniquely resolved DTO controls with `--exact`;
- four uniquely resolved core controls with `--exact`;
- complete `codex-tools` package;
- `cargo check -p codex-core --lib --locked`;
- clean source-only output branch publication.

No merge, deployment, credentials, production mutation, or public upstream interaction is authorized.