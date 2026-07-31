# F83-codex-append-acknowledgement: Expose durable rollout append acknowledgement to the session caller

Finding state: `delivery-gate-ready`

Workstream: `J/K/O — Codex persistence and current-source review`  
Canonical Fieldwork issue: `#83`  
Canonical finding path: `findings/F83-codex-append-acknowledgement/finding.md`  
Canonical implementation: `teamleaderleo/codex#84`  
Exact implementation head: `d8299b7fdf3aaf7ebc46d2cac840828cf97fc2a2`  
Exact base or source revision: `openai/codex@a01a2d91461a57809e944de7758477b92617ab01`; current public relation checked through `413492cd6c3a4d4f8dff6f406247ccda5a9d88aa`  
Strongest evidence class: `target-executed`  
Reviewed input generation: `complete three-file source diff; carrier #80 run 30583967538; independent review 4823945751`  
Current review disposition: `ACCEPT bounded prerequisite; HOLD direct-current-head packaging`  
Desk routing: `not-entered`  
Upstream contact authorized: `no`

## In simple words

Codex first adds a tool result to the live conversation and then asks `ThreadStore` to append it to durable rollout history. The session boundary used to log a failed append and continue without telling its caller whether durable storage accepted the item.

The accepted prerequisite returns that append result. It proves that the caller can distinguish an acknowledged append from an error while keeping a later, more precise `Persisted` versus `Ambiguous` state as a separate change.

## Why we care

A restart, resume, fork, replay, or compaction path reads durable history rather than the active process's live memory. When the model has seen a result that durable history may have missed, later recovery can reconstruct a different operation history.

A commit-then-error acknowledgement loss creates a second risk: blindly retrying an item that was actually written can duplicate its durable record.

## What happens if we leave it alone

Observed source behavior before this prerequisite:

- live history receives the item;
- durable append is attempted;
- append errors are logged;
- the session caller receives no append outcome.

The exact frequency of storage errors is unknown. The consequence is bounded to callers that need persistence certainty for retry, compaction, cleanup, or recovery.

## Current finding

`Session::record_conversation_items` should return whether its canonical rollout append was acknowledged.

The retained implementation:

- returns `true` for an ephemeral session with no `LiveThread` because live memory is the declared authority for that session;
- returns `true` after an acknowledged live append;
- returns `false` after a pre-write failure;
- returns `false` after a commit-then-error acknowledgement loss even though durable history contains the item.

The boolean is intentionally a prerequisite rather than a final persistence model.

### Claim table

| Claim | Evidence class | Exact support | Limit |
| --- | --- | --- | --- |
| Current session code can expose append acknowledgement without changing the existing store owner | `source-read` | PR #84 three-file diff | Does not classify the error |
| Pre-write failure and commit-then-error can produce the same caller result while different durable histories exist | `target-executed` | exact controls in run `30583967538` | In-memory deterministic fixture, not filesystem fault injection |
| Ephemeral live history remains authoritative without a durable thread | `target-executed` | `append_outcome_ephemeral_history_is_authoritative` | Applies only when no `LiveThread` exists |
| Public drift through `413492cd...` is file-disjoint | `source-read` | complete `a01a2d... → 413492...` compare | Later relevant drift expires the review |

## System and ownership map

```text
Session::record_conversation_items
├── live ContextManager update
├── LiveThread::append_items through ThreadStore
├── raw response item publication
└── returned append acknowledgement
```

- Session owns ordering between live state, durable append, and raw-item publication.
- `LiveThread` and `ThreadStore` remain the canonical persistence owners.
- The in-memory store owns deterministic pre-write and after-write failure injection for tests.
- Retry, duplicate reconciliation, and compaction policy remain downstream consumers of a later typed state.

## Historical precedent

### Store-owned live writes

- Sources: openai/codex PRs #18882 and #21874.
- Principle supported: `LiveThread` and `ThreadStore` own canonical persistence and metadata layers remain separate.
- Important difference: those changes did not return append acknowledgement to the session caller.

### Asynchronous metadata projection

- Source: openai/codex PR #30669.
- Principle supported: canonical append acceptance and later metadata visibility are distinct completion facts.
- Important difference: this finding concerns canonical append acknowledgement only.

### Writer generation and failed shutdown

- Source: openai/codex PR #31155.
- Principle supported: writer identity and ambiguous completion remain relevant after an error.
- Important difference: shutdown cleanup does not answer the per-append caller contract.

## Approaches considered

### Retained approach: expose the bounded acknowledgement first

This matches the current Session/LiveThread boundary, has a three-file fence, and gives later typed persistence work a real input.

### Declined: treat every error as definitely unpersisted

A write can commit before its acknowledgement fails. Automatic retry can duplicate the durable item.

### Declined: use live conversation as durable truth

Live memory can be authoritative for one active ephemeral session. It cannot prove restart or cross-reader recovery.

### Deferred: `Persisted` versus `Ambiguous`

That state should consume this prerequisite and add reconciliation, retry, compaction, and receipt rules in a separate finding.

## Edge cases covered

| Edge case or control | Evidence | Result |
| --- | --- | --- |
| No live thread | exact test | returned `true` under ephemeral authority |
| Successful append | exact test plus loaded history | returned `true`; durable item present |
| Failure before write | exact test plus loaded history | returned `false`; item absent |
| Failure after write | exact test plus loaded history | returned `false`; item present |
| Complete thread-store compatibility | carrier package gate | package passed |

## Edge cases deferred or outside scope

| Edge case | Why deferred | Owning next record or reopening trigger |
| --- | --- | --- |
| Typed ambiguous state | Requires caller and policy consumers | successor F83 finding after current source packaging |
| Duplicate reconciliation | Requires stable item/operation identity | replay and typed-identity findings |
| Compaction and retry authority | Depends on typed persistence state | successor policy finding |
| Remote tool effect | Persistence records local observation only | MCP operation-outcome finding |
| Real filesystem commit-then-error | Current deterministic store fixture establishes the semantic split | integration fixture when a target store supports controlled injection |

## Exact execution and receipts

| Repository/head | Command or workflow | Platform/environment | Result | Evidence class |
| --- | --- | --- | --- | --- |
| `teamleaderleo/codex#80@401c2e5e6a37730aae3e8da95591cc6f56655cfc` | run `30583967538` | Linux owned current-pin carrier | four exact controls and complete `codex-thread-store` package passed | `target-executed` |
| `teamleaderleo/codex#84@d8299b7fdf3aaf7ebc46d2cac840828cf97fc2a2` | complete-diff review `4823945751` | owned source PR | accepted bounded prerequisite | `source-read` review |

## Complete-diff and compatibility review

- Changed-file fence: exactly `session/mod.rs`, `session/turn_tests.rs`, and `thread-store/src/in_memory.rs`.
- Source branch is one commit directly parented by `a01a2d...`.
- Public Codex is two file-disjoint commits ahead at `413492cd...`.
- Independent review accepted the source conclusion and retained the boolean limitation.
- Execution carrier #80 remains temporary and should close after all receipts transfer.
- Routine remaining work: direct-current-head child or explicit review acceptance of the proven file-disjoint base; final source-head receipt synchronization.

## Current disposition and desk routing

- Finding state: `delivery-gate-ready`
- Review disposition: `ACCEPT bounded prerequisite; HOLD direct-current-head packaging`
- Review Queue entry: none
- Delivery lane: `not-entered`
- Exact next transition: publish or confirm an exact `413492cd...` child with the identical three-file content, then synchronize source head, review receipt, #83, #84, and F239.
- Clearing condition: current-head source identity and final complete-diff receipt agree.
- Required subgates: current-head relation, exact source head, carrier retirement.
- Autonomous work remaining: current-head materialization and receipt transfer.
- Non-delegable human decision: none.

## Changes to the canonical conclusion

| Date | Pull request or commit | Change in conclusion |
| --- | --- | --- |
| 2026-07-31 | owned #51/#52 | Historical source and current-pin carrier established the prerequisite |
| 2026-07-31 | owned #80 run `30583967538` | Current-pin exact controls and thread-store package passed |
| 2026-07-31 | source PR #84 and review `4823945751` | Bounded prerequisite accepted; typed persistence remained separate |

## References

- Fieldwork issues #83 and #239.
- Owned Codex PRs #51, #52, #80, and #84.
- `findings/F239-codex-upstream-convergence/finding.md`.
- Public Codex source through `413492cd6c3a4d4f8dff6f406247ccda5a9d88aa`, read-only.
- Public upstream interaction: none.
