# Codex convergence approach selection

Owner: coordinator synthesis for Fieldwork #239  
Parent canonical finding: [`F239`](../../../findings/F239-codex-upstream-convergence/finding.md)  
Technical state: `comparative-evaluation-active`  
Selected packaging direction: one lifecycle model plus bounded technical findings and outputs  
Current public source boundary: `3016671bb077c43448b8fa88f3edfa9772e17058`  
Upstream contact authorized: `no`

## In simple words

The easiest-looking plan was one giant Codex fix: make tools, reconnect, timeout, persistence, history, and terminal output agree in one stack.

Source reading showed several independent owners and several different meanings of “finished.” A call can be dispatched without settling remotely. A result can reach the model without durable append acknowledgement. A runtime can publish a new catalogue while an older call still owns its captured authority. A producer can retain output that a live subscriber misses.

The selected packaging keeps those meanings separate, proves each invariant at its real owner, and later presents several bounded outputs. The packaging direction is selected. The technical candidates remain under comparison and execution.

## Selection criteria

A viable direction should:

1. preserve current source ownership;
2. make each invariant independently falsifiable;
3. prevent success in one layer from being treated as success in another;
4. survive source drift through exact fences and expiry rules;
5. preserve exact execution evidence and negative results;
6. minimize authority widening and unsafe retry;
7. support bounded review, rollback, and carrier retirement;
8. give readers one understandable map without hiding disagreement.

## Investigation-format alternatives

### A — issue thread only

Attraction:

- one live coordination surface;
- immediate visibility;
- no repository structure.

Why it loses:

- chronology obscures the current answer;
- independent workers have no stable paths;
- exact diff review is unavailable;
- expired and current conclusions mix together.

Retained use: issue #239 remains the live routing surface. Canonical findings and workspace files carry durable reasoning.

### B — one shared mega-report

Attraction:

- one file to open;
- simple publication shape.

Why it loses:

- parallel edits collide;
- early synthesis can erase disagreement;
- partial source drift can expire one section while the whole file appears current;
- evidence from one owner can silently support another.

Retained use: one concise front door plus separate findings, evidence, alternatives, precedent, outputs, and handoff.

### C — one issue for every observation

Attraction:

- clear ownership and labels;
- independent discussion.

Why it loses:

- excessive coordination for subquestions that still feed one conclusion;
- repeated background and source maps;
- weak side-by-side comparison before promotion.

Retained use: create a new issue when a finding becomes independently actionable, as with Yjs #275.

### D — independent worker conclusions without synthesis

Attraction:

- maximal parallelism;
- several viewpoints quickly.

Why it loses:

- repeated source work and incompatible vocabularies;
- no declared current answer;
- disagreement remains hidden across files.

Retained use: workers own evidence notes; the canonical finding reconciles the current conclusion.

### E — immediate single canonical answer

Attraction:

- simple message;
- apparent convergence.

Why it loses:

- open technical comparisons become hidden assumptions;
- a clean narrative can outrun current-source execution;
- absorbed and stopped candidates lose their value.

Retained use: allow `candidate`, `held`, `disputed`, `stopped`, and `accepted` records while F239 remains comparative.

### F — database or generated dashboard first

Attraction:

- queryable state and automatic stale-input detection;
- portfolio-scale indexes.

Why it loses now:

- schema choices would precede a proven human workflow;
- generated views can hide reasoning and authorship;
- automation complexity would become another authority layer.

Reopening trigger: the file protocol has stable identifiers, states, transitions, and real adoption evidence.

## Codex technical and packaging alternatives

### 1 — one end-to-end mega-patch

Candidate scope:

- deferred loader and capability prefix;
- MCP reconnect and publication;
- operation identity and timeout;
- append outcome and history;
- terminal output retention.

Why it loses:

- request construction, Code Mode host, MCP manager, session, ThreadStore, rollout reducer, and unified execution have different owners;
- one test stack cannot establish authority, remote-effect, persistence, replay, and transcript claims;
- compatibility and rollback differ by layer;
- current source may absorb one invariant while rejecting another.

Reopening trigger: accepted bounded findings converge on one source owner, one compatibility boundary, and one composed execution gate.

### 2 — treat every append error as definitely absent

Attraction:

- simple failure state;
- automatic retry appears safe.

Why it loses:

A write can commit and then lose acknowledgement. Retrying can duplicate a logical result. The conservative state is ambiguous until reconciliation proves presence or absence.

Current direction: first expose append acknowledgement through carrier #80. Add typed persistence states in a separate successor with prewrite and commit-then-error controls.

### 3 — use live conversation as durable truth

Attraction:

- the model already sees the result;
- simple active-session behavior.

Why it loses:

Resume, fork, restart, compaction, and other readers depend on durable sources. Live memory can be authoritative for one ephemeral session without proving durable recovery.

Current direction: retain live result formation and durable append acknowledgement as separate facts.

### 4 — persisted result proves remote execution settled

Attraction:

- one receipt appears to answer the whole operation;
- simple compaction and retry policy.

Why it loses:

Persistence records Codex's local observation. A timeout item can persist while the remote mutation continues or commits later.

Current direction: link operation identity and persistence without collapsing external-effect certainty.

### 5 — cancellation delivery proves no remote effect

Attraction:

- easy timeout wording;
- immediate retry.

Why it loses:

A server can receive cancellation and still commit. Delivery proves a message event, not effect absence.

Current direction: record caller deadline, cancellation request/delivery, transport state, and remote-effect certainty independently.

### 6 — close the shared MCP service whenever one request times out

Attraction:

- bounded caller return;
- stalled transport is removed.

Why it loses:

- unrelated requests share the service;
- stale timeout work can close a replacement generation;
- operation lineage can disappear;
- catalogue publication needs manager ownership.

Current direction: request-scoped cancellation first; manager-owned generation-checked retirement only when delivery fails or stalls. Never replay a mutation while outcome is unknown.

### 7 — rebuild every MCP connection on every refresh

Attraction:

- simple freshness story;
- no reuse ambiguity.

Why it loses:

- ordinary unchanged refresh should preserve healthy ready clients;
- active calls and shared reconnect work can be disrupted;
- reconnect cost and failure surface increase.

Current direction: ordinary reconciliation reuses eligible clients; explicit freshness preserves reconnect intent and publishes through the manager.

### 8 — bind active calls to whichever catalogue is current at completion

Attraction:

- one global current snapshot;
- simple result lookup.

Why it loses:

A prepared or active call was authorized by a captured runtime. A later refresh can change schema, approval metadata, annotations, filters, hooks, or file-input behavior.

Current direction: capture runtime and operation identity at preparation or dispatch. Publication affects future calls.

### 9 — terminal completion depends on live subscribers

Attraction:

- one streaming path;
- less retained state.

Why it loses:

Broadcast is best-effort. A late or lagging subscriber can miss bytes the producer received. Completion can then differ from the bounded actual transcript.

Current direction: retain at the non-lossy producer boundary before broadcast, preserving bounded head/tail policy.

### 10 — mechanically cherry-pick historical terminal source

Attraction:

- quick restack;
- historical patch identity.

Why it loses:

Current source improved decode buffering and invalid-UTF-8 progress in the same files. Choosing one conflict side can discard real upstream behavior.

Current direction: reconstruct the semantic retention change on current source and run old plus new controls through carrier #53.

### 11 — increase Tokio worker stack and accept the Responses Lite candidate

Attraction:

- the full regression passes with a larger stack;
- no immediate request-path redesign.

Why it loses:

The default-stack overflow reveals a deep or recursive path. A stack-size increase hides the boundary and does not establish production safety or causation.

Current direction: use stack size only as a discriminator; build lower-level exact-prefix and retry controls.

### 12 — wait for upstream to stop changing

Attraction:

- fewer restacks;
- cleaner final diffs.

Why it loses:

Codex development is continuous. Waiting creates stale evidence and postpones useful classification.

Current direction: exact pins, narrow fences, drift ledgers, explicit expiry, and bounded successor branches.

## Current comparative table

| Criterion | Bounded findings and outputs | Mega-patch | Independent notes only | Immediate single answer |
| --- | --- | --- | --- | --- |
| Source-owner fidelity | strong | weak | strong | unclear |
| Independent falsifiability | strong | weak | strong | weak |
| Reader orientation | strong | superficially strong | weak | strong but premature |
| Preserves disagreement | strong | weak | weakly visible | weak |
| Rollback and review scope | bounded | broad | bounded but fragmented | unclear |
| Current-source readiness | partial; executing | absent | partial | absent |
| Selected packaging | **yes** | no | no | no |

## Current technical comparisons

| Area | Plausible directions still under comparison | Discriminating evidence |
| --- | --- | --- |
| Append acknowledgement | bounded acknowledgement prerequisite versus broader typed result state | carrier #80 exact execution, source-only diff, prewrite and commit-then-error successors |
| Terminal retention | producer-owned retention preserving current deque/lifecycle behavior versus current subscriber path | carrier #53 exact nine-control execution and four-file review |
| MCP refresh | upstream explicit reconnect absorption versus surviving host/generation residue | exact current manager call paths and overlapping-generation tests |
| Deferred authority | current standalone-host loader/dispatch design versus retirement of historical candidate | capability declaration, collision identity, loader, dispatch, first-turn request controls |
| Responses Lite | transport prefix defect versus test-stack artifact | lower-level prefix/retry fixture and first failing future boundary |

These comparisons keep F239 `comparative-evaluation-active`. None currently requires a non-delegable human choice.

## Selected direction

Use:

```text
one shared orientation model
+ canonical findings for current technical conclusions
+ independently owned evidence and alternatives
+ purpose-specific presentation outputs
+ exact current-source carriers and successor branches
+ retained stopped and superseded records
```

This direction wins because it preserves ownership, supports parallel work, makes alternatives lose through evidence, and keeps negative results useful.

## Clearing conditions

F239 can leave comparative evaluation when:

1. current-pin append carrier #80 settles and its source successor is reviewed or its failure retained;
2. terminal carrier #53 settles and its source successor is reviewed or its failure retained;
3. MCP reconnect/publication is compared against current manager behavior;
4. deferred authority is mapped to the standalone host or stopped;
5. Responses Lite receives a lower-level production-representative fixture or a retained stop;
6. each active candidate becomes a separate canonical finding, a stopped record, or a closed historical record;
7. temporary carriers transfer receipts and retire with successor mapping;
8. the composed finding/workspace protocol receives exact-head review.

A human design decision is requested only when further technical work cannot choose among remaining options because the choice depends on authority, values, private context, cost tolerance, or irreversible risk.
