# Codex convergence problem map

Owner: coordinator synthesis for Fieldwork #239  
Parent canonical finding: [`F239`](../../../findings/F239-codex-upstream-convergence/finding.md)  
Claim scope: system map with bounded source-read and executed findings linked elsewhere  
Current upstream pin: `3016671bb077c43448b8fa88f3edfa9772e17058`  
Upstream contact authorized: `no`

## In simple words

Imagine a restaurant with several ledgers:

- the menu says which meals exist;
- the kitchen roster says which cook can make each meal;
- the order ticket identifies one request;
- the kitchen may finish, cancel, or keep cooking after the waiter stops waiting;
- the waiter tells the customer what happened;
- the register records the result;
- the closing book lets tomorrow's staff resume from the same truth.

Codex has a similar chain for tools. Difficult bugs appear when two ledgers disagree. The model can see a tool whose executable authority moved. A timeout can describe the caller's deadline while a remote mutation remains possible. Live conversation can contain a result that durable history missed. A subprocess can produce bytes before a live listener subscribes.

Issue #239 studies those disagreements as separate invariants and decides which bounded repairs or stopped records belong together.

## End-to-end chain

```text
model and turn configuration
→ capability manifest and tool catalogue
→ runtime generation and binding
→ operation identity and dispatch
→ local or remote execution
→ cancellation, timeout, transport, and remote-effect settlement
→ model-visible result
→ durable append acknowledgement
→ history projection, compaction, resume, fork, and replay
→ reviewable source and retained evidence
```

Every arrow is an ownership boundary. The same user-visible symptom can originate at different arrows and require different evidence.

## Capability manifest

The request tells the model which tools exist and how to call them. Responses Lite can carry tool information in input items rather than the top-level tools array. Startup prewarm and websocket reuse can compress later requests.

Questions:

- Did the first generated turn receive the complete model-visible capability prefix?
- Did an untraced prewarm response become an unsafe parent for a generated request?
- Can a deferred tool become direct without an executable loader or host authority?
- Does manifest identity match the runtime that executes the call?

Current owners: Fieldwork #85, historical owned Codex #45, and the standalone Code Mode host boundary.

## Runtime generation and publication

MCP refresh can build a new connection set while an older refresh is still running. The manager decides which candidate becomes visible.

Questions:

- Which refresh generation may publish?
- Does explicit host reload force fresh connections while ordinary refresh reuses healthy clients?
- Can a late older refresh replace a newer catalogue?
- Does an accepted refresh return its own catalogue or a later global snapshot?
- Does reconnect intent survive cancelled replacement?

Current owners: Fieldwork #84, owned Codex #46/#48, and current upstream reconnect/reconciliation work.

## Prepared and active call authority

Publication controls future visibility. A prepared or running call may still belong to an earlier runtime generation.

Questions:

- Which runtime identity authorized and received the call?
- Can a refresh silently redirect a prepared call?
- Does the result preserve original operation lineage?
- What happens to active calls when a generation retires?

The call should retain captured identity unless an explicit invalidation contract says otherwise.

## Dispatch and operation identity

A result is useful only when tied to the logical operation that produced it.

Questions:

- Was the operation dispatched?
- Can retry create a second effect?
- Can begin and result items duplicate, reorder, or separate through compaction?
- Do resume and fork preserve the same operation identity?

Current owner: Fieldwork #83 and adjacent receipt work.

## Timeout, cancellation, and remote effect

The caller may stop waiting before remote execution reaches a terminal state.

Separate facts include:

1. caller deadline reached;
2. request dispatched or withheld;
3. cancellation requested;
4. cancellation delivery completed, failed, or timed out;
5. server observed cancellation where a fixture can prove it;
6. transport remained live, closed, or became unknown;
7. external effect committed, was prevented, was reconciled absent, or remains unknown.

A delivered cancellation can coexist with a later committed mutation. A timeout result therefore describes local observation until stronger settlement evidence exists.

Current owners: Fieldwork #134 and #162.

## Local result formation

Codex turns an execution outcome into a model-visible item and live conversation history.

Questions:

- Did the item preserve the correct tool-call identity?
- Did error wording collapse distinct terminal states?
- Did malformed or partial output become misleading success?
- Did live conversation retain the item when durable append failed?

This is the bridge between execution facts and persistence facts.

## Durable append acknowledgement

Live result insertion can precede `LiveThread::append_items`. Current session code can log an append error without returning an outcome to the caller.

Questions:

- Did the append fail before writing?
- Did it commit and then lose acknowledgement?
- Can the caller distinguish persisted, absent, and ambiguous?
- Which state permits compaction, retry, resume, or cleanup?

Current current-pin carrier: owned Codex #80 at `401c2e5e6a37730aae3e8da95591cc6f56655cfc`, workflow `30583967538` queued at the workspace refresh.

## History projection, compaction, and replay

Canonical rollout items feed reconstructed conversation history, metadata, compaction, resume, fork, and traces. Current upstream normalizes passthrough metadata and preserves executor paths in read-command actions.

Questions:

- Do live memory and durable history describe the same logical items?
- Can metadata-only differences create duplicate replay items?
- Does compaction preserve operation and persistence identity?
- Can resume or fork select the wrong writer generation or prefix?
- Which append outcome is sufficient for projection or compaction?

Upstream owns substantial writer, projection, and reconciliation behavior. Caller-visible append acknowledgement and remote-effect settlement remain separate.

## Subprocess and terminal output

Execution paths publish live deltas and later construct a completion transcript.

Questions:

- Is output retained before best-effort broadcast?
- Can a late or lagging subscriber miss bytes the producer received?
- Does close/drain capture trailing bytes?
- Does cancellation terminate the full process tree?
- Can restart recover a process or only its retained transcript?

Current terminal carrier: owned Codex #53 at `c4e0de2e54d804d1054afb90c30b7150a774151c`, workflow `30585540688` pending at refresh.

Producer-owned retention, hard termination, Windows containment, remote settlement, and restart reattachment remain separate findings.

## Evidence and canonical source

Fieldwork has a delivery chain of its own:

```text
historical finding
→ current source application
→ exact-name/count preflight
→ target-native execution
→ complete-diff review
→ canonical source branch
→ bounded proposal or stopped record
→ carrier retirement
```

Execution workflows can prove behavior while remaining unsuitable as delivery source. Canonical source and evidence-producing carrier require separate identities.

## Why the portfolio expanded

The initial findings shared words such as tool, timeout, history, reconnect, and result. Current source showed distinct owners:

- request construction;
- standalone Code Mode host;
- MCP runtime manager;
- operation lifecycle;
- session live memory;
- ThreadStore append and writer generation;
- rollout reconstruction;
- unified-execution process and transcript handling.

Combining them too early would create a patch whose tests and authority claims cannot be reviewed independently. The expansion reflects discovered ownership boundaries, not one vague mega-problem.

## Retained independent invariants

1. Model-visible capability must match an executable authority path.
2. Only an eligible MCP refresh generation may publish its own accepted result.
3. Prepared and active calls retain captured runtime and operation identity.
4. Caller timeout, cancellation delivery, transport, and remote-effect certainty remain separate.
5. Model-visible results receive an explicit durable append outcome.
6. Compaction, retry, resume, and fork consume persistence and operation facts conservatively.
7. Terminal transcript retention begins at the non-lossy producer boundary.
8. Evidence carriers remain separate from canonical source and retire after receipt transfer.

## Main synthesis question

What is the smallest set of independently reviewable findings and proposals that covers the surviving invariants without pretending one layer proves another?

The current answer in F239 is one shared lifecycle model plus bounded findings for capability authority, MCP publication, operation outcome, append acknowledgement, terminal retention, and carrier hygiene.
