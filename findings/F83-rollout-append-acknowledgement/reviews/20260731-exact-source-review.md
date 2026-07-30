# Exact-source review receipt — Codex rollout append acknowledgement

Repository and pull request: `teamleaderleo/codex#84`  
Canonical branch: `fieldwork/83-append-outcome-a01a2d`  
Exact source head: `d8299b7fdf3aaf7ebc46d2cac840828cf97fc2a2`  
Exact source base: `a01a2d91461a57809e944de7758477b92617ab01`  
Current public source inspected: `413492cd6c3a4d4f8dff6f406247ccda5a9d88aa`  
Work class: `upstream-fork research — clean source candidate`  
Independent review: `4823945751`  
Upstream contact authorized: `no`

## In simple words

The source returns the durable-history append acknowledgement from the Codex session boundary. Four exact controls prove ordinary success, ephemeral success, pre-write failure, and commit-then-error acknowledgement loss. The change deliberately stops before typed persistence certainty, retry, replay, or compaction policy.

The complete current-public drift leaves the three source files untouched. The source is accepted as the bounded prerequisite. Delivery waits for a direct child of the current public head so ancestry, execution, and review share one base.

## Complete diff

Exact changed-file fence:

- `codex-rs/core/src/session/mod.rs`;
- `codex-rs/core/src/session/turn_tests.rs`;
- `codex-rs/thread-store/src/in_memory.rs`.

No workflow, documentation, generated file, dependency, or unrelated source change appears in the canonical source PR.

## Disposition-relevant claims

| Claim | Evidence class | Evidence | Limit |
| --- | --- | --- | --- |
| Session caller receives the append acknowledgement | `source-read` | complete diff at `d8299b7f...` | boolean result only |
| Pre-write failure leaves durable history unchanged | `target-executed` | run `30583967538`, unique exact control | in-memory store fixture |
| Commit-then-error may coexist with durable presence | `target-executed` | run `30583967538`, unique exact control | backend matrix remains outside scope |
| Acknowledged append and ephemeral session remain successful | `target-executed` | run `30583967538`, two unique exact controls | exact target revision |
| Current public drift is file-disjoint | `source-read` | compare `a01a2d... → 413492...` | later relevant drift expires the review |

## Validation receipt

Execution carrier: `teamleaderleo/codex#80@401c2e5e6a37730aae3e8da95591cc6f56655cfc`  
Workflow: `30583967538`

Executed gates:

- source application to exact base;
- exact three-file fence;
- formatting and diff hygiene;
- four uniquely resolved full test names with `--exact`;
- complete `codex-thread-store` package;
- source-only publication after success.

Retained exact marker: `FIELDWORK_APPEND_OUTCOME_EXACT=4/4`.

## Current-public relation

The two public commits after `a01a2d...` change account-plan, authentication, rate-limit, app-server schema, protocol permission, sandbox, and TUI status files. None intersects the source fence.

Review conclusion within the fence: mechanically direct and semantically unchanged.

Preferred delivery action: replay the exact source directly onto `413492...`, renew execution, and obtain fresh complete-diff acceptance.

## Negative results and limits

- A returned append error cannot prove durable absence.
- The source does not distinguish `Absent` from `Ambiguous`.
- The source grants no retry authority.
- The source proves no remote tool-effect settlement.
- Receipt replay, compaction, resume, fork, and rollback remain separate.
- A green carrier is evidence for the source; the carrier is never the canonical implementation.

## Disposition

`ACCEPT` the bounded append-acknowledgement prerequisite at `d8299b7f...`.

`HOLD` proposal or delivery promotion until a direct-current-head child renews the exact receipt and receives fresh independent complete-diff review.

Next transition: Delivery Desk #160 D2.

Builder eligibility: self-review may prepare the restack; an independent reviewer must accept the direct-current-head source. Merge and public upstream interaction remain unauthorized.
