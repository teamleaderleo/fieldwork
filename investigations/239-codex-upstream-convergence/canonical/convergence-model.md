# What the Codex convergence initiative is doing

Canonical status: `accepted for internal orientation`  
Canonical technical finding: [`F239`](../../../findings/F239-codex-upstream-convergence/finding.md)  
Parent issue: [Fieldwork #239](https://github.com/teamleaderleo/fieldwork/issues/239)  
Claim scope: plain-language system and investigation model  
Current upstream pin: `3016671bb077c43448b8fa88f3edfa9772e17058`  
Source proposal authority: `none`  
Upstream contact authorized: `no`

## In simple words

Codex gives an AI tools and lets it act. Several parts of Codex must tell the same story:

1. the model sees a tool;
2. a real runtime can execute that exact tool;
3. the call keeps one identity;
4. timeout and cancellation describe what Codex actually knows;
5. the result reaches the model;
6. durable history accepts or rejects the result explicitly;
7. resume and replay reconstruct the same logical operation;
8. subprocess completion includes the bounded output Codex retained.

Fieldwork found gaps at several handoffs. Issue #239 checks each finding against current Codex, keeps the parts that still apply, separates overlapping ideas, executes surviving candidates, and prepares bounded proposal packets.

## The five-year-old version

Codex has several notebooks.

One notebook lists the tools. One says which machine can run them. One records what the model asked. One records what the machine did. One stores the answer for later.

Trouble begins when the notebooks disagree.

The tool notebook can say “calculator” while the calculator runtime was replaced. The model can hear “timeout” while the remote service keeps working. The live conversation can remember an answer that durable history missed. The terminal can receive words before a live listener subscribes.

The initiative labels each notebook, checks every handoff, and decides which repairs belong together.

## Why anyone should care

Tool calls can perform real actions. A user may trust Codex to avoid a duplicate retry, preserve a result after restart, reconnect to the intended service, or show complete retained output.

These facts have different consequences:

- **visible** — the model was told a tool exists;
- **bound** — a specific runtime can execute it;
- **dispatched** — the request left Codex;
- **cancel requested** — Codex asked execution to stop;
- **remote effect settled** — the action committed, was prevented, or was reconciled absent;
- **result observed** — Codex formed a local answer;
- **result persisted** — durable history accepted the answer;
- **history reconciled** — resume, fork, compaction, and replay agree on the logical item.

Collapsing those facts into one success or failure string creates unsafe guesses. The initiative gives each fact an owner and an evidence rule.

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

### Tool visibility and executable authority are separate

A request can contain a tool declaration while the executable loader or host path remains missing or mismatched. The standalone Code Mode host moved this boundary, so the historical deferred-loader source placement needs redesign.

### MCP refresh has future-publication and active-call questions

An explicit refresh can require fresh connections. Overlapping refreshes also need an eligible-generation rule. A prepared or active call still needs its captured runtime identity after a newer generation publishes.

### Timeout says when the caller stopped waiting

Timeout alone says nothing definitive about a remote mutation. Cancellation delivery also leaves room for a server that commits anyway. Operation outcome requires separate dispatch, cancellation, transport, and remote-effect facts.

### Live conversation and durable history can disagree

Current session code can place a result in live memory, attempt a durable append, log an error, and continue without returning an append outcome. A prewrite failure and a commit-then-error acknowledgement loss need different recovery behavior, yet both can look like an error.

### History reconciliation solves a later problem

Current upstream improves item reconciliation, metadata normalization, projection, writer lifecycle, and execution provenance. Those changes help resume, replay, and client attribution. They cannot tell the original caller whether its append was acknowledged.

### Live output broadcast may lose delivery

Best-effort broadcast is useful for responsive streaming. Terminal completion needs a producer-owned bounded transcript so a late or lagging subscriber cannot define the final output.

### Historical green tests expire as current-source claims

A test at an exact old head remains valid historical evidence. Current, portable, conflict-free, and proposal-ready claims require a fresh source pin, source fence, exact tests, and complete-diff review.

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

Each owner answers a different question. Combining them too early would produce a patch where one passing test appears to validate unrelated behavior.

## The independent proposal areas

### Capability and deferred execution

Goal: every model-visible direct or deferred tool has an executable authority path with matching identity.

Owner area: request construction and standalone Code Mode host.

### MCP refresh publication

Goal: explicit refresh requests freshness, ordinary refresh reuses eligible clients, and only an eligible generation publishes its own accepted result.

Owner area: MCP runtime manager.

### MCP operation outcome

Goal: preserve dispatch, cancellation, transport, remote-effect, and operation-lineage facts without unsafe replay.

Owner area: MCP client plus manager-owned retirement and recovery.

### Append acknowledgement and result persistence

Goal: expose canonical append outcome and conservatively represent persisted, absent, or ambiguous state before compaction, retry, or cleanup consumes it.

Owner area: session, `LiveThread`, and `ThreadStore` boundary.

### Terminal producer-owned retention

Goal: preserve current bounded output and decode behavior while retaining completion bytes before best-effort broadcast.

Owner area: unified-execution producer and completion path.

### Carrier retirement and evidence transfer

Goal: keep temporary workflows away from delivery source, preserve immutable receipts, and close stale carriers after successor mapping.

Owner area: Fieldwork review and convergence process.

## What we declined

The current evidence declines these directions:

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

The plan combines one shared explanation with several bounded technical findings and outputs.

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

## What “settled” means for #239

Issue #239 can leave comparative evaluation when every current and historical candidate has one honest state:

- `review-ready` — one canonical finding and exact evidence are ready for examination;
- `delivery-gate-ready` or `land-ready` — one accepted implementation has only named landing gates left;
- `design-decision-ready` — technical work is sufficient and one genuine human choice remains;
- `stopped` — upstream absorption, disproved premise, obsolete source boundary, or explicit scope stop is retained;
- `closed` — accepted work is merged, archived, or otherwise has no active transition.

Every temporary carrier must transfer evidence and successor links before retirement.

## Current state

At this snapshot:

- F239 is `comparative-evaluation-active`;
- public upstream is `3016671bb077c43448b8fa88f3edfa9772e17058`;
- the one-commit delta after `a01a2d...` changes account-plan and related app-server/auth/status paths, leaving every declared active candidate source fence unchanged;
- current-pin append carrier #80 is `401c2e5e6a37730aae3e8da95591cc6f56655cfc`, with run `30583967538` queued at refresh;
- terminal carrier #53 is `c4e0de2e54d804d1054afb90c30b7150a774151c`, with run `30585540688` pending at refresh;
- MCP reconnect/publication needs exact comparison with current reconnect work;
- deferred discovery needs redesign around the standalone Code Mode host;
- Responses Lite needs a lower-level exact-prefix and retry fixture;
- public upstream remains read-only.

The exact continuation record lives in [`../handoff.md`](../handoff.md). The canonical transition state and conclusion live in [`F239`](../../../findings/F239-codex-upstream-convergence/finding.md).
