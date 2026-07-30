# Codex convergence problem map

Owner: coordinator synthesis for Fieldwork #239  
Claim scope: system map with bounded source-read and executed findings linked elsewhere  
Current upstream pin: `745603a5a1eb48b6f343633d622eeb72dd549d7b`  
Upstream contact authorized: `false`

## In simple words

Imagine a restaurant run by several ledgers:

- the menu says which meals exist;
- the kitchen roster says which cook can make each meal;
- the order ticket identifies the customer's request;
- the kitchen may finish, cancel, or keep cooking after the waiter gives up waiting;
- the waiter tells the customer what happened;
- the register records the result;
- the closing book lets tomorrow's staff resume from the same truth.

Codex has the same kind of chain for tools. The difficult bugs appear when two ledgers disagree. The tool list can describe one runtime while another handles the call. A timeout can describe the waiter's deadline while the kitchen continues. The live conversation can contain a result that the durable rollout failed to store. A subprocess can produce bytes that a later listener never receives.

Issue #239 studies those disagreements as separate invariants and then decides which bounded repairs belong together.

## The end-to-end chain

```text
model and turn configuration
→ capability manifest and tool catalogue
→ runtime generation and binding
→ operation identity and dispatch
→ remote or local execution
→ cancellation, timeout, and terminal outcome
→ local result item
→ durable append acknowledgement
→ history projection, compaction, resume, fork, and replay
→ reviewable source and retained evidence
```

Every arrow is an ownership boundary. The same user-visible failure can originate at different arrows and require different evidence.

## 1. Capability manifest

The request tells the model which tools exist and how to call them. For Responses Lite, tool information can live in input items rather than the top-level tools array. Startup prewarm and incremental websocket reuse can compress later requests.

Questions:

- Did the first generated turn receive the complete model-visible capability prefix?
- Did an untraced prewarm response become an unsafe parent for a generated request?
- Can a deferred tool become direct without an executable loader or host authority?
- Does the manifest identity match the runtime that will execute the call?

Current Fieldwork owner: #85 and owned Codex #45.

## 2. Runtime generation and publication

MCP refresh can build a new connection set and catalogue while an older refresh is still running. The runtime manager decides which candidate becomes visible.

Questions:

- Which refresh generation may publish?
- Does explicit host reload force fresh connections?
- Can a late older refresh replace a newer catalogue?
- Does an accepted result return its own catalogue or whichever generation is current later?
- Does reconnect freshness survive overlapping refresh attempts?

Current Fieldwork owner: #84 and owned Codex #46/#48.

## 3. Prepared and active call authority

Publication controls future visibility. A call already prepared or running may still belong to an earlier runtime generation.

Questions:

- Which runtime identity authorized and received the call?
- Can a refreshed catalogue silently redirect a prepared call?
- Does the result preserve the original operation lineage?
- What happens to active calls when a generation is retired?

This boundary needs captured runtime identity and typed invalidation. It should not be inferred from whichever catalogue is visible when the call completes.

## 4. Dispatch and operation identity

A result is meaningful only when it can be tied to the logical operation that produced it.

Questions:

- Was the operation dispatched?
- Can a retry create a second side effect?
- Can begin and result items be duplicated, reordered, or separated by compaction?
- Does resume or fork preserve the same operation identity?

Current Fieldwork owner: #83 and adjacent receipt work.

## 5. Timeout, cancellation, and remote effect

The caller may stop waiting before the remote operation reaches a terminal state.

Facts that require separate representation:

1. caller deadline reached;
2. request dispatched or withheld;
3. cancellation requested;
4. cancellation delivery completed, failed, or timed out;
5. server observed cancellation where the fixture can prove it;
6. transport remained live, closed, or became unknown;
7. external effect committed, was prevented, was reconciled absent, or remains unknown.

A delivered cancellation can coexist with a later committed mutation. A timeout result therefore describes local observation until stronger settlement evidence exists.

Current Fieldwork owner: #134 and #162.

## 6. Local result formation

Codex turns an execution outcome into a model-visible response item and live conversation history.

Questions:

- Did the result item preserve the correct tool call identity?
- Did error wording collapse distinct terminal states?
- Did malformed or partial output become a misleading success?
- Did local conversation retain the result when durable persistence failed?

This is the bridge between execution facts and persistence facts.

## 7. Durable append acknowledgement

The live result can be added to memory before `LiveThread::append_items` succeeds. Current Codex logs append errors at the session boundary and returns no outcome to the caller.

Questions:

- Did the append fail before writing?
- Did the append commit and then lose acknowledgement?
- Can the caller distinguish `Persisted` from `Ambiguous`?
- Which state permits compaction, retry, resume, or cleanup?

Owned Codex #51 exposes the bounded append acknowledgement prerequisite. Typed result-persistence state remains a later slice.

## 8. History projection, compaction, and replay

Canonical rollout items feed reconstructed conversation history, thread metadata, compaction, resume, fork, and traces. Upstream continues to change these paths, including passthrough-metadata normalization at current head.

Questions:

- Do live memory and durable history describe the same logical items?
- Can metadata-only differences create duplicate or divergent replay items?
- Does compaction preserve operation and persistence identity?
- Can resume or fork select the wrong writer generation or history prefix?
- Which append outcome is sufficient for projection or compaction?

Current upstream prior art owns substantial writer, projection, and reconciliation behavior. It leaves the caller-facing append outcome and operation settlement questions open.

## 9. Subprocess and terminal output

Local and remote execution paths publish live deltas and later construct a completion transcript.

Questions:

- Is output retained before best-effort broadcast?
- Can a lagging or late subscriber lose bytes that the producer already received?
- Does close/drain capture trailing bytes?
- Does cancellation terminate the full process tree?
- Can restart recover a process or only its retained transcript?

Owned Codex #49/#53 covers producer-owned bounded transcript retention. Hard termination, Windows containment, remote settlement, and restart reattachment remain separate.

## 10. Evidence and canonical source

Fieldwork also has a delivery chain:

```text
historical finding
→ current source application
→ exact-name/count preflight
→ target-native execution
→ complete-diff review
→ canonical source branch
→ proposal packet or stopped record
→ carrier retirement
```

Execution workflow files can prove behavior while remaining unsuitable as the final source. The canonical source head and the evidence-producing carrier therefore require separate identities.

## Why the Codex portfolio expanded

The initial findings shared words such as tool, timeout, history, reconnect, and result. Source reading showed several distinct state owners:

- request construction;
- Code Mode host;
- MCP runtime manager;
- operation and call lifecycle;
- session live memory;
- thread-store append;
- rollout reconstruction;
- unified execution process and transcript handling.

Combining them too early would create a patch whose tests and authority claims could not be reviewed independently. The expansion reflects discovered ownership boundaries rather than one vague mega-problem.

## Independent invariants currently retained

1. The model-visible capability manifest must match an executable authority path.
2. Only the newest eligible MCP refresh generation may publish its own accepted result.
3. Prepared and active calls retain captured runtime and operation identity.
4. Caller timeout, cancellation delivery, transport state, and remote-effect certainty remain separate facts.
5. Model-visible results receive an explicit durable append outcome.
6. Compaction, retry, resume, and fork consume persistence and operation facts conservatively.
7. Terminal transcript retention begins at the non-lossy producer boundary.
8. Evidence carriers remain separate from canonical source and retire after receipt transfer.

## Main synthesis question

The portfolio should produce the smallest set of independently reviewable proposals that covers the surviving invariants without pretending that one layer proves another.

That likely means several canonical outputs rather than one patch:

- capability and deferred-loader authority;
- MCP refresh generation publication;
- MCP timeout and operation outcome;
- append acknowledgement and typed persistence outcome;
- terminal producer-owned retention;
- carrier retirement and exact-head evidence policy.