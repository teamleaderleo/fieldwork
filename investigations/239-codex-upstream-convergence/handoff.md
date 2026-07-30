# Codex convergence workspace handoff

Workspace: `investigations/239-codex-upstream-convergence/`  
Parent issue: [Fieldwork #239](https://github.com/teamleaderleo/fieldwork/issues/239)  
Coordinator lane: `J/O synthesis`  
State: `blocked on exact source-carrier execution and current-source proposal review`  
Snapshot date: 2026-07-31  
Current read-only upstream head: `a01a2d91461a57809e944de7758477b92617ab01`  
Workspace branch: `teamleaderleo/fieldwork:coordination/investigation-workspaces-2026-07-31`  
Workspace content head before this handoff commit: `27dac6507fe1ceefc90b124a2d8d0d6d2a947b96`  
Upstream contact authorized: `false`

## In simple words

The Codex portfolio now has one understandable lifecycle model, separate findings for source drift and ownership, explicit alternatives, a prior-art record, and a canonical-output index.

The remaining blockers are source execution and source-specific review. Append acknowledgement and terminal retention have exact owned carriers queued. MCP reconnect/publication needs comparison with current upstream reconnect behavior. Deferred discovery needs redesign around the standalone Code Mode host. Responses Lite needs a lower-level exact capability-prefix and retry fixture.

## Work completed

- defined the reusable Fieldwork investigation-workspace convention;
- created reusable front-door, finding, canonical-output, and handoff templates;
- created the #239 workspace and plain-language system map;
- explained why the Codex work expanded into several owners and proposals;
- recorded upstream drift, candidate classifications, prior art, and rejected approaches;
- accepted one internal convergence explainer while keeping source proposals pending or held;
- recorded the packaging decision and conflict-preservation rules;
- refreshed public upstream read-only through `a01a2d91461a57809e944de7758477b92617ab01`;
- proved that the latest one-commit delta leaves all declared active candidate source fences unchanged.

## Current canonical outputs

| Output | Status | Audience | Exact inputs | Limit |
| --- | --- | --- | --- | --- |
| `canonical/convergence-model.md` | `accepted` | anyone needing to understand #239 | problem map, drift ledger, alternatives, precedent | internal orientation only; no source acceptance |
| `findings/upstream-drift-and-overlap.md` plus `evidence/upstream-snapshot-2026-07-31.md` | `candidate` | current-source classifiers | upstream through `a01a2d...`, owned carrier heads | expires after relevant upstream drift or carrier publication |
| append acknowledgement packet | `pending` | ThreadStore/session reviewer | owned Codex #51/#52 | waits for source publication and complete-diff review |
| terminal producer-retention packet | `pending` | unified-exec reviewer | owned Codex #49/#53 | waits for exact run and source-only diff review |
| MCP refresh generation packet | `pending` | MCP runtime reviewer | owned Codex #46/#48 and upstream reconnect prior art | exact current-source comparison remains |
| deferred executable-authority packet | `disputed` | Code Mode/request reviewer | owned Codex #45 and standalone host migration | source owner and design require revision |
| Responses Lite first-generated capability packet | `held` | request/transport reviewer | historical source intent and stack diagnostics | lower-level exact-prefix and retry evidence required |
| MCP timeout outcome model | `candidate` in #134/#162 | MCP lifecycle reviewer | executed six-control matrix | modern high-level cancellation and manager retirement remain separate |

## Exact external and owned source state

| Repository or record | Branch or item | Exact head or generation | State |
| --- | --- | --- | --- |
| `openai/codex` | public `main` | `a01a2d91461a57809e944de7758477b92617ab01` | read-only inspected |
| `teamleaderleo/codex` | PR #52 carrier branch `fieldwork/83-direct-append-carrier-20260731` | `324ddccba14b2b0934e2c56cc0cda7ca04a56e6d` | open execution carrier |
| `teamleaderleo/codex` | intended append source branch | `fieldwork/83-append-outcome-upstream-97576b` | publish only after exact success |
| `teamleaderleo/codex` | PR #53 carrier branch `fieldwork/23-terminal-acd540-restack-carrier` | `d5028fc9771407aa7a9bafbceb7eba051b91de36` | open execution carrier |
| `teamleaderleo/codex` | intended terminal source branch | `fieldwork/23-terminal-97576-source` | publish only after exact success |
| `teamleaderleo/fieldwork` | workspace branch | `coordination/investigation-workspaces-2026-07-31` | candidate documentation branch |

## Current execution evidence

| Workflow | Exact carrier head | State at final retrieval | Evidence class | Limit |
| --- | --- | --- | --- | --- |
| `30582576317` — `fieldwork-83-append-outcome-current-upstream` | `324ddccba14b2b0934e2c56cc0cda7ca04a56e6d` | `queued` | execution pending | supplies no source-behavior result until completion |
| `30582012412` — `fieldwork-terminal-97576-shallow` | `d5028fc9771407aa7a9bafbceb7eba051b91de36` | `queued` | execution pending | supplies no source-behavior result until completion |

Historical focused receipts remain valid at their exact heads and pins. They carry no current-source status by themselves.

## Candidate dispositions

### Append acknowledgement

Disposition: `continuing — semantic residue; exact current-source execution pending`.

Current Codex still logs append failure without returning a caller-visible outcome. The next source slice should expose acknowledgement only. Typed persistence state, retry authority, duplicate reconciliation, compaction gating, and remote-effect settlement remain separate.

### Terminal producer-owned retention

Disposition: `continuing — mechanically conflicting, semantically complementary`.

Current upstream deque and lifecycle-ordering improvements remain valuable. The source candidate must add retention before best-effort broadcast while preserving those improvements.

### MCP reconnect and publication

Disposition: `continuing — upstream overlap requires exact comparison`.

Upstream explicit-refresh reconnect work may absorb part of the host-reconnect primitive. Newest-eligible-generation publication, accepted-result identity, captured active-call binding, and typed outcomes require separate verification.

### Deferred discovery and Code Mode

Disposition: `design-decision-ready for source-owner revision`.

The standalone host changes the correct execution boundary. The invariant remains: every model-visible direct or deferred tool needs a matching executable authority path.

### Responses Lite first-generated capability prefix

Disposition: `held`.

Logical trace repair and capability transmission are distinct. The full Code Mode regression overflows the default worker stack. A lower-level request fixture and failed-first-generated retry control should run before production source is accepted.

### MCP timeout outcome

Disposition: `design-decision-ready at the operation model; manager source pending`.

The executed matrix establishes separate caller deadline, cancellation delivery, transport, and remote-effect facts. Production work needs manager-owned generation-checked retirement and prohibits mutation replay while effect certainty is absent.

## Active disagreements

### How many canonical outputs should the Codex portfolio produce?

Selected packaging: one shared lifecycle explainer plus several bounded technical outputs. A future reviewer may combine candidates after source evidence proves shared ownership and compatible rollback. Current evidence favors separation.

### Does upstream explicit-refresh reconnect absorb owned Codex #46?

Evidence needed: exact current source and test comparison across the host call path, reconnect-intent retention, ordinary refresh reuse, and source-head behavior. Preserve both the upstream precedent and historical Fieldwork receipt until comparison completes.

### Where should deferred executable authority live?

Evidence needed: current standalone host capability publication, direct/deferred tool registry identity, loader dispatch path, and Responses Lite manifest construction. The old in-core placement provides historical intent, not current design authority.

## Blockers

1. append carrier `30582576317` remains queued;
2. terminal carrier `30582012412` remains queued;
3. the new Fieldwork workspace convention needs complete-diff review and independent acceptance before becoming general process authority;
4. MCP and deferred-discovery candidates require current-source source maps before new source branches;
5. every later public upstream action requires separate explicit authorization.

## Exact next actions

1. inspect `30582576317`; on success review the published append source head against `a01a2d...`, transfer exact receipts to #83/#239, and close #52 after successor proof;
2. inspect `30582012412`; on success review the published terminal source head against `a01a2d...`, transfer exact receipts to #23/#239, and close #53 after successor proof;
3. compare current upstream explicit-refresh reconnect behavior with owned Codex #46 and classify absorbed residue before restacking #48;
4. map standalone Code Mode host declaration, loader, and execution identity before rewriting #45;
5. build Responses Lite lower-level exact-prefix, trace, and retry controls on a clean current head;
6. independently review the Fieldwork workspace branch and decide whether to add the convention to `START_HERE.md`, `AGENTS.md`, and `COORDINATION.md` as general process authority.

## Expiry conditions

This handoff expires when:

- public upstream moves beyond `a01a2d91461a57809e944de7758477b92617ab01` in a relevant source area;
- carrier #52 or #53 changes head or run state;
- a canonical source branch publishes;
- issue #239 changes its invariant, authority boundary, or close condition;
- the workspace convention is accepted, revised, superseded, or rejected.

## Public interaction

Public upstream interaction performed: `false`.