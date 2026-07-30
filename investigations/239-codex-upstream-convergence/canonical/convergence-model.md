# What the Codex convergence initiative is doing

Canonical status: `accepted for internal orientation`  
Parent issue: [Fieldwork #239](https://github.com/teamleaderleo/fieldwork/issues/239)  
Claim scope: plain-language system and investigation model  
Current upstream pin: `a01a2d91461a57809e944de7758477b92617ab01`  
Source proposal authority: `none`  
Upstream contact authorized: `false`

## In simple words

Codex gives an AI tools and lets it act. For that to work safely, several parts of Codex must tell the same story:

1. the model sees a tool;
2. a real runtime can execute that exact tool;
3. the call keeps one identity;
4. timeout and cancellation describe what Codex actually knows;
5. the result reaches the model;
6. the result reaches durable history;
7. resume and replay reconstruct the same story;
8. subprocess completion includes the output Codex retained.

Fieldwork found gaps at several of those handoffs. Issue #239 checks every finding against current Codex, keeps the ones that still apply, separates overlapping ideas, executes the surviving candidates, and prepares clean proposal packets.

## The five-year-old version

Codex has several notebooks.

One notebook lists the tools. One notebook says which machine is running them. One notebook records what the model asked. One notebook records what the machine did. One notebook saves the answer for later.

Trouble begins when the notebooks disagree.

The tool notebook can say “calculator” while the calculator machine was replaced. The model can hear “timeout” while the remote machine keeps working. The conversation can remember an answer while the disk copy missed it. The terminal can print words before the listener arrives.

We are labeling each notebook, checking every handoff, and deciding which repairs belong together.

## Why anyone should care

Tool calls can perform real actions. A user may trust Codex to avoid a duplicate retry, preserve the result after restart, reconnect to the intended service, or show the complete retained output.

The following facts have different consequences:

- **visible** — the model was told a tool exists;
- **bound** — a specific runtime can execute it;
- **dispatched** — the request left Codex;
- **cancel requested** — Codex asked execution to stop;
- **remote effect settled** — the action committed, was prevented, or was reconciled absent;
- **result observed** — Codex formed a local answer;
- **result persisted** — durable history accepted the answer;
- **history reconciled** — resume, fork, compaction, and replay agree on the logical item.

Collapsing those facts into one success or failure string creates dangerous guesses. The initiative gives each fact an owner and an evidence rule.

## The system model

```text
capability manifest
      ↓
runtime generation and authority
      ↓
operation identity and dispatch
      ↓
execution, timeout, cancellation, and settlement
      ↓
model-visible result
      ↓
durable append acknowledgement
      ↓
history, compaction, resume, fork, and replay
```

Subprocess execution has a parallel output chain:

```text
process output producer
      ↓
bounded retained transcript
      ↓
best-effort live broadcast
      ↓
terminal completion item
```

Fieldwork tests the arrows. A component can behave correctly while the next handoff still loses information.

## What we have established so far

### 1. Tool visibility and executable authority are separate

A request can contain a tool declaration while the executable loader or host path remains missing or mismatched. The standalone Code Mode host moved this boundary, so the historical deferred-loader candidate needs a current design.

### 2. MCP refresh has future-publication and active-call questions

An explicit refresh can require fresh connections. Overlapping refreshes also need a newest-eligible-generation rule. A prepared or active call still needs its captured runtime identity after a newer generation publishes.

### 3. Timeout says when the caller stopped waiting

Timeout alone says nothing definitive about a remote mutation. Cancellation delivery also leaves room for a server that commits anyway. Operation outcome requires separate facts for dispatch, cancellation, transport, and remote effect.

### 4. Live conversation and durable history can disagree

Current session code can place a result in live memory, attempt a durable append, log an error, and continue without returning an append outcome. A prewrite failure and a commit-then-error acknowledgement loss require different recovery behavior, yet both can look like an error.

### 5. History reconciliation solves a later problem

Current upstream is improving logical item reconciliation, metadata normalization, projection, writer lifecycle, and execution-provenance records. Those changes help resume, replay, and client attribution. They cannot tell the original caller whether its append was acknowledged.

### 6. Live output broadcast is allowed to lose delivery

Best-effort broadcast is useful for responsive streaming. Terminal completion needs a producer-owned bounded transcript so a late or lagging subscriber cannot define the final output.

### 7. Historical green tests expire as current-source claims

A test at an exact old head remains valid historical evidence. Current, portable, conflict-free, and proposal-ready claims require a fresh upstream pin, source fence, exact tests, and complete-diff review.

## Why this became several situations

The initial theme was “tool continuity.” Source reading revealed several independently owned state machines:

- request and prompt construction;
- Code Mode host execution;
- MCP runtime management;
- request and operation lifecycle;
- session live history;
- ThreadStore and writer generation;
- rollout projection and reconstruction;
- process and terminal output handling.

Each owner answers a different question. Combining them would produce a patch where one passing test could appear to validate unrelated behavior.

The portfolio expanded because the code exposed real boundaries. The new workspace makes those boundaries readable.

## The independent proposals we expect

### Capability and deferred execution

Goal: every model-visible direct or deferred tool has an executable authority path with matching identity.

Owner area: request construction and standalone Code Mode host.

### MCP refresh publication

Goal: explicit refresh requests freshness, ordinary refresh reuses eligible clients, and only the newest eligible generation publishes its own result.

Owner area: MCP runtime manager.

### MCP operation outcome

Goal: preserve dispatch, cancellation, transport, remote-effect, and operation-lineage facts without unsafe replay.

Owner area: MCP client plus manager-owned retirement and recovery.

### Append acknowledgement and result persistence

Goal: expose canonical append outcome and conservatively represent `Persisted` versus `Ambiguous` before compaction, retry, or cleanup consumes it.

Owner area: session, `LiveThread`, and `ThreadStore` boundary.

### Terminal producer-owned retention

Goal: preserve current bounded output and decode behavior while retaining completion bytes before best-effort broadcast.

Owner area: unified execution producer and completion path.

### Carrier retirement and evidence transfer

Goal: keep temporary workflows away from delivery source, preserve immutable receipts, and close stale carriers after successor mapping.

Owner area: Fieldwork review and convergence process.

## What we declined

We declined these directions:

- one mega-patch across all owners;
- automatic retry after any append error;
- using cancellation delivery as proof that a mutation never committed;
- binding active calls to whichever catalogue is newest at completion;
- rebuilding every MCP connection for every ordinary refresh;
- using live conversation as proof of durable recovery;
- using a persisted timeout item as proof of remote settlement;
- defining terminal completion through a best-effort subscriber;
- accepting a larger worker stack as the production repair for the Responses Lite diagnostic;
- cherry-picking historical source while discarding current upstream improvements.

The detailed tradeoffs live in [`../alternatives/approach-selection.md`](../alternatives/approach-selection.md).

## Why the selected plan is strongest

The plan combines one shared explanation with several bounded technical outputs.

That gives each reviewer:

- one source owner;
- one invariant;
- one exact current base;
- one changed-file fence;
- discriminating controls;
- explicit compatibility and recovery limits;
- relevant prior art;
- a clear accept, repair, hold, execute, or reject decision.

It also preserves negative results. An absorbed candidate can close with value because the ledger explains where upstream solved it.

## What “fixed” means for #239

Issue #239 can close when every current and historical candidate has one honest disposition:

- **proposal-ready** — current source-only head, exact execution, complete-diff review, prior-art classification, standalone packet, and no hidden prerequisite;
- **design-decision-ready** — evidence is executed and the remaining human choice, alternatives, and consequences are explicit;
- **absorbed or obsolete** — current evidence explains why the work should stop;
- **historical evidence only** — old receipts remain useful and a successor owns current work;
- **blocked** — exact failure and smallest continuation are durable.

Every temporary carrier must transfer its evidence and successor links before retirement.

## Current state

At this snapshot:

- public upstream is `a01a2d91461a57809e944de7758477b92617ab01`;
- the `745603... → a01a2d...` delta leaves every declared active candidate source fence unchanged;
- append acknowledgement carrier #52 is queued at head `324ddccba14b2b0934e2c56cc0cda7ca04a56e6d`;
- terminal retention carrier #53 is queued at head `d5028fc9771407aa7a9bafbceb7eba051b91de36`;
- MCP reconnect/publication needs exact comparison with current upstream reconnect work;
- deferred discovery needs redesign around the standalone Code Mode host;
- Responses Lite needs a lower-level exact-prefix and retry fixture;
- public upstream remains read-only.

The exact continuation record lives in [`../handoff.md`](../handoff.md).