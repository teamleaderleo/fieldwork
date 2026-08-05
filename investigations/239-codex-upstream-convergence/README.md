# Codex upstream convergence workspace

Workspace phase: `synthesize`  
Current transition state: `comparative-evaluation-active`

Parent issue: [Fieldwork #239](https://github.com/teamleaderleo/fieldwork/issues/239)  
Programme: [agent and CLI execution, #14](https://github.com/teamleaderleo/fieldwork/issues/14)  
Target hub: [Codex, #8](https://github.com/teamleaderleo/fieldwork/issues/8)  
General autonomous initiative: [#254](https://github.com/teamleaderleo/fieldwork/issues/254)  
Current read-only upstream pin: [`openai/codex@3016671bb077c43448b8fa88f3edfa9772e17058`](https://github.com/openai/codex/commit/3016671bb077c43448b8fa88f3edfa9772e17058)  
Canonical finding index: [`findings/F239-codex-upstream-convergence/finding.md`](../../findings/F239-codex-upstream-convergence/finding.md)  
Upstream contact authorized: `no`

## In simple words

Codex lets a model discover tools, call them, receive results, keep a conversation, reconnect services, run subprocesses, and resume later. Those actions cross several components. A tool can be advertised by one snapshot, executed by another runtime, reported to the model, stored to history, and replayed after restart.

Fieldwork found several places where those facts can drift apart. Examples include a stale MCP refresh publishing after a newer one, a timeout describing the caller's deadline while a remote mutation may still finish, a tool result entering live conversation memory while durable append fails, or terminal bytes reaching a producer while a later subscriber misses them.

Issue #239 asks which findings survive current Codex, which were absorbed upstream, which conflict with new code, and which deserve separate proposal-ready outputs. The current answer is one shared lifecycle model plus several bounded technical findings and carriers. The technical comparison is still active; no human design decision is currently blocking progress.

## Relationship to the canonical finding

The canonical technical conclusion and transition state live in [`F239`](../../findings/F239-codex-upstream-convergence/finding.md).

This workspace supplies:

- orientation and the whole-system map;
- source-drift and overlap evidence;
- alternatives and prior art;
- presentation-output status;
- exact carrier and handoff records.

Workspace evidence notes never replace the canonical finding. Accepted output status never grants source acceptance, merge authority, or upstream-contact authority.

## Why this investigation exists

Codex coordinates actions with side effects. The user and model need accurate answers to questions such as:

- Which tool definition authorized this call?
- Did the call reach the remote service?
- Did the remote effect finish, cancel, or remain unknown?
- Did Codex durably record the result it showed the model?
- Can resume, fork, compaction, or replay reconstruct the same logical history?
- Did a subprocess finish with all retained output?
- Can an older refresh replace a newer catalogue or runtime?

An incorrect answer can lead to duplicate retries, missing context, stale capability use, misleading success or timeout records, lost output, or recovery from the wrong source state.

## What we are doing

1. pin current public source and classify upstream drift;
2. map each candidate to the exact current ownership seam;
3. search current and historical prior art;
4. execute surviving bounded candidates on exact heads;
5. compare alternatives through controls that can make them lose;
6. turn accepted results into canonical findings and purpose-specific outputs;
7. retire temporary carriers after source and receipt transfer.

## Investigation areas

| Area | Exact question | Owner | Durable note or canonical finding | Canonical transition state |
| --- | --- | --- | --- | --- |
| Whole-system conclusion | Which ownership boundaries and packaging direction currently win? | #239 coordinator | [`F239`](../../findings/F239-codex-upstream-convergence/finding.md) | `comparative-evaluation-active` |
| Whole-system model | How do discovery, authority, execution, persistence, history, and recovery relate? | workspace synthesis | [`findings/problem-map.md`](findings/problem-map.md) | supplies F239 evidence |
| Upstream drift and overlap | Which historical candidates survive current source? | lane J | [`findings/upstream-drift-and-overlap.md`](findings/upstream-drift-and-overlap.md) | supplies F239 evidence |
| Prior art | Which upstream and Fieldwork changes already own parts of the problems? | J/O synthesis | [`precedent/fieldwork-and-upstream-prior-art.md`](precedent/fieldwork-and-upstream-prior-art.md) | retained evidence |
| Alternatives | Which packaging and implementation approaches should win? | coordinator | [`alternatives/approach-selection.md`](alternatives/approach-selection.md) | comparative evidence |
| Canonical outputs | Which presentations currently represent the work? | coordinator | [`canonical/README.md`](canonical/README.md) | output status only |
| Current continuation | What exact heads, runs, blockers, and next actions remain? | coordinator | [`handoff.md`](handoff.md) | follows F239 state |

## Evidence and source map

| Record | Exact identity | Purpose | Authority or limit |
| --- | --- | --- | --- |
| Public Codex source | `3016671bb077c43448b8fa88f3edfa9772e17058` | current read-only fence | later relevant drift expires current language |
| One-commit drift | `a01a2d... → 3016671...` | account-plan/auth/app-server change map | no declared append, terminal, MCP runtime, or deferred-authority fence overlap |
| Append current-pin carrier | `teamleaderleo/codex#80@401c2e5e6a37730aae3e8da95591cc6f56655cfc` | execute append acknowledgement on `a01a2d...` | run `30583967538` queued at refresh |
| Append historical carrier | `teamleaderleo/codex#52@324ddccba14b2b0934e2c56cc0cda7ca04a56e6d` | preserve exact historical carrier receipt | superseded by #80 for current-pin promotion |
| Terminal carrier | `teamleaderleo/codex#53@c4e0de2e54d804d1054afb90c30b7150a774151c` | reconstruct and execute terminal retention | run `30585540688` pending at refresh |
| Workspace integration | `integration/canonical-findings-workspaces-2026-07-31` | compose finding and workspace protocols | documentation/research only |

## Current established findings

- Model-visible capability and executable authority are separate facts.
- Publication controls future runtime visibility; prepared and active calls need captured authority.
- Caller timeout and cancellation delivery do not prove remote-effect absence.
- Live conversation and durable append acknowledgement can diverge.
- History reconciliation solves a later problem than original append acknowledgement.
- Best-effort live broadcast should not define the producer's final retained transcript.
- Historical green tests remain valid historical evidence while current-source claims require refresh.
- One shared model plus bounded technical findings is stronger than one mega-patch at the current ownership boundaries.

## Current upstream state

The prior workspace pin was `a01a2d91461a57809e944de7758477b92617ab01`.

Current public head is `3016671bb077c43448b8fa88f3edfa9772e17058`, one commit later. The commit adds Enterprise automation account-plan support and changes account, auth, rate-limit, app-server schema, backend-client, status, and related tests. It does not touch the declared append, terminal, MCP runtime, request-construction, or standalone Code Mode host source fences.

The active candidate classifications therefore carry forward to `3016671...` for those fences. A later relevant commit requires another overlap review.

## Current candidate picture

### Deferred discovery and Responses Lite

Historical owned source: `teamleaderleo/codex#45`.

The invariant remains: model-visible direct or deferred tools need a matching executable authority path. The standalone Code Mode host moved the correct owner, so the historical placement needs redesign. Logical websocket trace repair and first-generated capability delivery remain separate questions.

### MCP reconnect and publication

Historical owned sources: `teamleaderleo/codex#46` and `#48`.

Current upstream explicit-refresh reconnect work may absorb part of #46. Newest-eligible-generation publication, accepted-result identity, and prepared/active call binding remain under exact comparison.

### Append acknowledgement and result persistence

Current-pin execution carrier: `teamleaderleo/codex#80@401c2e5e6a37730aae3e8da95591cc6f56655cfc`, run `30583967538` queued at this snapshot.

Historical carrier #52 remains open for its exact-pin record but does not own current promotion. The first bounded source slice exposes append acknowledgement only. Typed `Persisted` versus `Ambiguous`, retry authority, duplicate reconciliation, compaction gating, and remote-effect settlement remain separate successors.

### Terminal output retention

Current carrier: `teamleaderleo/codex#53@c4e0de2e54d804d1054afb90c30b7150a774151c`, run `30585540688` pending at this snapshot.

The candidate must preserve current `VecDeque`, invalid-UTF-8 progress, bounded output, and close/drain ordering while adding producer-owned retention before best-effort broadcast.

### Timeout and cancellation certainty

Fieldwork #134 and #162 retain separate caller deadline, cancellation request/delivery, transport state, and remote-effect certainty. Production work still needs manager-owned generation-checked retirement and prohibits mutation replay while effect certainty is unknown.

## Active disagreements or missing evidence

- Whether upstream explicit-refresh reconnect fully absorbs owned #46 or leaves a bounded host-level residue.
- Where current deferred executable authority belongs after standalone-host migration.
- Whether current-pin append acknowledgement executes cleanly and what successor result state is justified.
- Whether terminal producer retention preserves all current deque/lifecycle behavior at the source-only head.
- Which bounded findings become separate proposal packets after exact execution and review.

These are technical comparisons and remain `comparative-evaluation-active`. Move to `design-decision-ready` only if a genuine policy, authority, cost, private-context, or irreversible-risk choice remains after the technical evidence settles.

## Alternatives

See [`alternatives/approach-selection.md`](alternatives/approach-selection.md).

The selected packaging is one shared lifecycle model plus several bounded technical outputs. The mega-patch, no-synthesis, immediate-single-answer, unsafe retry, cancellation-as-settlement, current-catalogue active-call binding, subscriber-owned completion, and stack-size-only directions remain declined or deferred for recorded reasons.

## Precedent and prior art

See [`precedent/fieldwork-and-upstream-prior-art.md`](precedent/fieldwork-and-upstream-prior-art.md).

The strongest precedents establish current ownership around `ThreadStore`, writer generations, immutable runtime snapshots, explicit freshness, request-stable tool snapshots, standalone Code Mode hosting, bounded output, lifecycle ordering, and deque-based decoding.

## Canonical outputs

See [`canonical/README.md`](canonical/README.md).

| Output | Audience | Status | Decision owner |
| --- | --- | --- | --- |
| [`canonical/convergence-model.md`](canonical/convergence-model.md) | internal orientation | `accepted` | #239 coordinator |
| current-source drift ledger | workers and reviewers | `candidate` | #239 coordinator |
| append acknowledgement packet | session/ThreadStore reviewer | `held` pending execution | successor finding owner |
| terminal retention packet | unified-exec reviewer | `held` pending execution | successor finding owner |
| MCP generation packet | runtime reviewer | `candidate` pending comparison | successor finding owner |
| deferred authority packet | request/Code Mode reviewer | `disputed` pending redesign | successor finding owner |

Output status describes a presentation artifact. It does not replace F239's transition state or grant source acceptance.

## Current blockers and next actions

1. inspect current-pin append carrier #80 and classify the exact source-only successor;
2. inspect terminal carrier #53 and review the published four-file source head;
3. compare upstream explicit-refresh behavior with #46/#48;
4. map standalone-host declaration, loader, and dispatch identity before rewriting #45;
5. materialize accepted bounded successor findings and stopped records;
6. retire execution carriers after receipt and successor transfer;
7. independently review the composed workspace/finding integration branch.

## Snapshot limits

This orientation expires when:

- public Codex moves in a declared active source fence;
- carrier #80 or #53 changes head or run state;
- a source-only successor publishes;
- #239 changes its invariant or close condition;
- the composed Fieldwork protocol branch is accepted, repaired, superseded, or rejected.

## Handoff

See [`handoff.md`](handoff.md) for exact heads, receipts, blockers, and continuation points.
