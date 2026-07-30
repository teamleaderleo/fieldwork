# Exact-source review receipt — Codex rollout append acknowledgement

Repository and pull request: `teamleaderleo/codex#84`  
Canonical branch: `fieldwork/83-append-outcome-a01a2d`  
Exact source head: `d8299b7fdf3aaf7ebc46d2cac840828cf97fc2a2`  
Exact source base: `a01a2d91461a57809e944de7758477b92617ab01`  
Current read-only public source inspected: `413492cd6c3a4d4f8dff6f406247ccda5a9d88aa`  
Work class: `upstream-fork research — clean source candidate`  
Independent source review: `4823945751`  
Upstream contact authorized: `no`

## In simple words

The source returns the durable rollout append acknowledgement from the Codex session boundary. Four exact controls prove ordinary success, ephemeral authority, pre-write failure, and commit-then-error acknowledgement loss.

The change stops at a boolean prerequisite. Typed persistence certainty, retry, replay, compaction, and remote-effect settlement remain separate work.

The complete current-public compare leaves the three source files untouched. The source is accepted for a bounded direct-current-head delivery gate.

## Complete diff

Exact changed-file fence:

- `codex-rs/core/src/session/mod.rs`;
- `codex-rs/core/src/session/turn_tests.rs`;
- `codex-rs/thread-store/src/in_memory.rs`.

No workflow, generated file, dependency, or unrelated source change appears in the canonical source PR.

## Claim receipts

| Claim | Evidence class | Evidence | Limit |
| --- | --- | --- | --- |
| Session caller receives append acknowledgement | `source-read` | complete diff at `d8299b7f...` | boolean only |
| Pre-write failure leaves tested durable history unchanged | `target-executed` | run `30583967538` | deterministic in-memory store fixture |
| Commit-then-error can coexist with durable presence | `target-executed` | run `30583967538` | cross-backend matrix remains outside scope |
| Ephemeral and acknowledged append paths remain successful | `target-executed` | run `30583967538` | exact target revision |
| Current public drift is file-disjoint | `source-read` | compare `a01a2d... → 413492...` | later relevant drift expires this receipt |

## Validation

Execution carrier: `teamleaderleo/codex#80@401c2e5e6a37730aae3e8da95591cc6f56655cfc`  
Workflow: `30583967538`

Executed gates:

- exact source application;
- exact three-file fence;
- formatting and diff hygiene;
- four unique full test names with `--exact`;
- complete `codex-thread-store` package;
- source-only publication after success.

Retained marker: `FIELDWORK_APPEND_OUTCOME_EXACT=4/4`.

## Current-public relation

The two public commits after `a01a2d...` change account-plan, authentication, rate-limit, app-server schema, protocol permission, sandbox, and TUI status files. None intersects the source fence.

The source remains mechanically direct and semantically unchanged within the reviewed boundary.

## Disposition

`ACCEPT` the bounded append-acknowledgement prerequisite at `d8299b7f...`.

Route to `Delivery Desk #160 D2` for one source-only child of `413492...`, renewed exact execution, fresh complete-diff review, and carrier retirement.

The builder may prepare the current-head child. Independent acceptance remains required. Merge and public upstream interaction remain unauthorized.
