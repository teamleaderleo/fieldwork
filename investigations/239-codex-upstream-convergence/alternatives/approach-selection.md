# Codex convergence approach selection

Owner: coordinator synthesis for Fieldwork #239  
Decision state: `selected direction; bounded proposals still require exact-head review`  
Upstream contact authorized: `false`

## In simple words

The easiest-looking plan was one giant Codex fix: make tools, reconnect, timeout, persistence, history, and terminal output agree in one stack. Source reading showed several independent owners and several different meanings of “done.”

The selected approach keeps those meanings separate, proves each one at its real owner, and later presents several bounded canonical outputs. This costs more bookkeeping and gives reviewers much cleaner decisions.

## Selection criteria

The chosen approach should:

1. preserve current upstream ownership;
2. make each invariant independently testable;
3. prevent one successful layer from being mistaken for success in another;
4. survive upstream source drift;
5. preserve exact execution evidence;
6. minimize authority widening and retry risk;
7. allow independent proposals, stopped results, and negative findings;
8. give a new reader a plain-language system map.

## Investigation-format alternatives

### Alternative A — keep everything in issue #239

Attractive parts:

- one live command surface;
- immediate visibility;
- no repository-file setup.

Costs:

- long comment history obscures the current answer;
- independently owned findings have no stable paths;
- exact diff review is unavailable;
- alternatives and expired conclusions become difficult to compare;
- readers reconstruct the model from chronology.

Disposition: issue #239 remains the live notification and coordination surface. Repository workspace files carry the durable model, findings, alternatives, canonical outputs, and handoff.

### Alternative B — one shared mega-report

Attractive parts:

- one file to open;
- simple final publication path.

Costs:

- parallel workers collide on shared prose;
- early editor choices can erase useful disagreement;
- one conclusion can silently inherit evidence from another area;
- a source-pin change can expire only part of the report while making the whole file appear current.

Disposition: use a concise front door plus separate finding files and explicit canonical outputs.

### Alternative C — one issue for every observation

Attractive parts:

- clear ownership and discussion boundaries;
- easy label and state tracking.

Costs:

- issue proliferation for facts that still belong to one decision;
- repeated background and source maps;
- cross-issue synchronization overhead;
- weak place for side-by-side alternatives before promotion.

Disposition: create a new issue when a finding becomes an independently actionable invariant, campaign, decision, or proposal. Keep intermediate findings in the workspace.

### Alternative D — let every agent write a final answer independently

Attractive parts:

- maximal parallelism;
- several viewpoints emerge quickly.

Costs:

- repeated source work;
- incompatible vocabularies and source pins;
- unclear evidence authority;
- no declared present answer.

Disposition: agents own separate findings. A coordinator compares them and declares canonical candidates or accepted outputs.

### Alternative E — select one canonical answer immediately

Attractive parts:

- simple message;
- quick apparent convergence.

Costs:

- source drift can invalidate the answer;
- unresolved policy and compatibility choices become hidden assumptions;
- a clean narrative can outrun the evidence.

Disposition: allow `candidate`, `disputed`, and several purpose-specific `accepted` outputs.

### Alternative F — build a database and generated dashboard first

Attractive parts:

- queryable state;
- automated indexes and stale-input detection;
- potential scale across all targets.

Costs:

- schema decisions would precede proven human workflow;
- generated views can hide reasoning and authorship;
- the repository would carry automation complexity before the canonicalization rules settle.

Disposition: prove the file convention first. Later automation can index stable paths, statuses, exact heads, evidence classes, and successor links.

## Codex packaging alternatives

### Alternative 1 — one end-to-end mega-patch

Candidate content:

- deferred loader;
- Responses Lite first-turn behavior;
- MCP reconnect and publication;
- operation identity and timeout;
- append outcome and history;
- terminal retention.

Why it loses:

- request construction, Code Mode host, MCP manager, session, ThreadStore, rollout reducer, and unified execution have different owners;
- one test stack cannot establish every authority, persistence, execution, and recovery claim;
- compatibility and rollback differ by layer;
- upstream can accept or absorb one invariant while rejecting another.

Selected direction:

Produce several independently reviewable source proposals plus one system-level explainer.

### Alternative 2 — treat every append error as definitely unpersisted

Attractive parts:

- simple failure enum;
- automatic retry appears safe.

Why it loses:

A write can commit and then lose acknowledgement. Retrying can duplicate a result or side effect record. The correct conservative state is `Ambiguous` until reconciliation proves presence or absence.

Selected direction:

First expose append acknowledgement. Add typed `Persisted/Ambiguous` behavior in a separate source slice with prewrite and commit-then-error controls.

### Alternative 3 — use live conversation history as durable truth

Attractive parts:

- the model already sees the result;
- ephemeral tests remain simple;
- no immediate wait for storage.

Why it loses:

Resume, fork, process restart, and other readers depend on durable sources. Live memory can remain authoritative for one active ephemeral session while still providing no durable recovery proof.

Selected direction:

Retain live history and durable append outcome as separate facts.

### Alternative 4 — use persisted result as proof that remote execution settled

Attractive parts:

- one receipt appears to answer the whole operation;
- simple compaction and retry policy.

Why it loses:

Persistence records Codex's local observation. A timeout item can persist while the remote mutation continues or commits later.

Selected direction:

Operation settlement and result persistence remain separate dimensions linked by operation identity.

### Alternative 5 — treat cancellation delivery as proof of no remote effect

Attractive parts:

- easy timeout wording;
- retry can begin immediately.

Why it loses:

A server can receive cancellation and still commit. Transport delivery proves a message event, not effect absence.

Selected direction:

Record caller deadline, cancellation request and delivery, transport terminal state, and external-effect certainty independently.

### Alternative 6 — close the shared MCP service whenever one request times out

Attractive parts:

- bounded caller return;
- stalled transport is removed.

Why it loses:

- unrelated requests share the service;
- an old timeout task can close a newer replacement;
- catalogue and reconnect publication need manager ownership;
- operation lineage can disappear during recovery.

Selected direction:

Use request-scoped cancellation first, then manager-owned generation-checked retirement when delivery fails or stalls. Automatic mutation replay remains prohibited while outcome is unknown.

### Alternative 7 — always rebuild every MCP connection on every refresh

Attractive parts:

- no reuse ambiguity;
- simple freshness story.

Why it loses:

- ordinary unchanged refresh should retain healthy ready clients;
- active calls and shared reconnect work can be disrupted;
- reconnect cost and startup failure increase.

Selected direction:

Separate ordinary reconciliation from explicit freshness requests. Preserve reconnect intent across cancelled replacement and let the manager publish only an eligible generation.

### Alternative 8 — bind a call to whichever MCP catalogue is current at completion

Attractive parts:

- one global current snapshot;
- simple result lookup.

Why it loses:

A prepared or active call was authorized by a captured runtime. A later refresh can change schema, approval metadata, annotations, visibility, hooks, or file-input behavior.

Selected direction:

Capture runtime and operation identity at preparation or dispatch. Publication affects future calls; active calls retain their original authority unless explicitly invalidated.

### Alternative 9 — keep terminal completion dependent on live subscribers

Attractive parts:

- one streaming path;
- less retained state.

Why it loses:

Broadcast is best-effort. A late or lagging subscriber can miss bytes the producer received. Completion then differs from actual bounded retained output.

Selected direction:

Retain output at the non-lossy producer boundary before broadcast. Keep live deltas best-effort and preserve the existing bounded head/tail policy.

### Alternative 10 — cherry-pick historical terminal source and resolve conflicts mechanically

Attractive parts:

- quick restack;
- preserves historical commit identity.

Why it loses:

Current upstream improved decode buffering and invalid-UTF-8 progress in the same files. Choosing one conflict side discards real current behavior.

Selected direction:

Reconstruct the semantic retention change on current source, preserve upstream deque behavior, then run exact old and new controls.

### Alternative 11 — increase the Tokio worker stack and accept the Responses Lite source candidate

Attractive parts:

- the full regression passes with a larger stack;
- minimal immediate source change.

Why it loses:

The default-stack overflow reveals a deep or recursive execution path. A stack-size increase hides the boundary and gives no evidence that production behavior is safe or that the candidate caused the depth.

Selected direction:

Use the larger stack as a discriminator only. Build lower-level request and trace controls, isolate the first failing future boundary, and retain production source on hold.

### Alternative 12 — wait for upstream to stop changing

Attractive parts:

- fewer restacks;
- cleaner final diff.

Why it loses:

Codex development is continuous. Waiting creates stale evidence and postpones useful classification.

Selected direction:

Use exact pins, narrow source fences, current-head drift ledgers, and outputs that expire explicitly when their relevant inputs change.

## Why the selected approach wins

The selected approach creates one coherent system model and several bounded delivery candidates:

```text
shared orientation and source intelligence
+ independently owned findings
+ exact evidence and prior art
+ explicit alternatives
+ purpose-specific canonical outputs
+ exact-head handoff and retirement ledger
```

This approach preserves disagreement, supports parallel work, reduces reviewer scope, and keeps a strong negative result valuable. It also matches current Codex ownership: request snapshots, runtime managers, operation lifecycle, ThreadStore, rollout reducers, and process-output producers each enforce their own invariant.

## Clearing conditions

The selected packaging becomes ready for final canonical decisions when:

1. carriers #52 and #53 complete or retain exact failure receipts;
2. current head `745603a5a1eb48b6f343633d622eeb72dd549d7b` receives candidate-by-candidate overlap review;
3. MCP reconnect/publication source paths are compared with upstream #34952/#35151 and current manager code;
4. deferred discovery is redesigned around the standalone Code Mode host;
5. accepted source heads receive complete-diff and exact-test review;
6. each output names its audience, claim boundary, risks, alternatives, and successor issue.