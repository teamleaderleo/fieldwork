# Host Capability and MCP Catalogue Lifecycle Reconciliation

## What this campaign is deciding

Campaign #84 is no longer a broad search for every MCP edge case. It is deciding one concrete rule:

> When MCP state changes from generation A to generation B, future work may use B, while work already sampled or dispatched under A must retain A's identity and operation lineage until it reaches a proven terminal outcome.

This requires two controls:

1. **Publication control** — only the newest accepted refresh or relist result may publish a catalogue for future requests.
2. **In-flight authority control** — an existing call cannot silently switch from the runtime, schema, or approval authority it was sampled under.

## Current state

- Campaign issue: #84
- Programme: #14
- Parent campaign: #31
- Target hub: #8
- Priority: P0 after #83
- State: `investigating — implementation direction narrowed`
- Worker: GPT-5.6 Thinking
- Fieldwork branch: `campaign/84-host-mcp-lifecycle-reconciliation`
- Owned Codex reconnect draft: `teamleaderleo/codex#5`
- Public Codex schema reproduction revision: `a5082373f18119dc5d3eb993267c97f37880935d`
- Latest inspected public Codex revision: `9cf6b3905c102cf38b4f93ec2533261a99764d4d`
- Codex MCP dependency: `rmcp = 3.0.0`
- Latest inspected Rust MCP SDK release: `3.0.1`
- Upstream contact: unauthorized and unused

## What has been proved

### Explicit host reload can reconnect

The owned reconnect slice proves that host `refresh_mcp_config` can request a fresh client while ordinary reconciliation keeps its existing ready-client reuse behavior.

This is a valid primitive, not the complete repair. A boolean reconnect request does not identify which refresh generation owns the resulting publication.

### SDK cache freshness is not application publication freshness

The official Rust SDK reproduction used two overlapping relists:

```text
sdk_cache=catalogue_c
naive_application=catalogue_b
ticketed_application=catalogue_c
requests=3
```

The SDK retained current catalogue C internally, while an older successful callback still returned B to application code. Codex therefore needs its own accepted-current publication ticket.

Rust MCP SDK 3.0.1 does not change this conclusion. Its release fixes authentication resource selection, protocol-header errors, stateless initialize negotiation, and graceful subscription metadata.

### Cached A can execute through changed live B

The public Codex reproduction established:

```text
A advertises echo(message: string)
→ model emits {"message":"hello"}
→ B exposes echo(count: integer)
→ current dispatch invokes B
→ B rejects the A-shaped arguments
→ Codex returns B's error
```

Codex did not compare A and B before invocation. The server-side schema rejection is only containment for this fixture; another B implementation could accept or reinterpret A's fields.

Classification: `advertisement_execution_revision_mismatch`.

### A local timeout may leave A running

Fieldwork #134 and owned Codex PR #22 exercise the real Codex MCP client. Current legacy behavior is:

```text
caller reports timeout
MCP cancellation is not observed
server mutation completes later
follow-up request remains usable
```

A persisted timeout message proves what Codex told the model. It does not prove remote execution stopped.

## Ownership shared with Campaign #83

Campaign #83 now has one accepted session-scoped operation receipt owner. Merged owned-Codex slices record:

- selected runtime effect;
- lifecycle begin before hooks and handler execution;
- certain pre-dispatch failure closure;
- terminal observations;
- authoritative direct result persistence;
- ambiguity after persistence failure or conflicting observations.

Campaign #84 must reuse this owner. It must not create a second MCP-specific ledger.

The missing shared field is **execution certainty after dispatch**. At minimum, the result vocabulary must distinguish:

- certain pre-dispatch failure;
- confirmed remote completion or failure;
- confirmed cancellation or terminal stream closure;
- cancellation requested but delivery unknown;
- local timeout or dropped wait while the operation may still run;
- transport loss or resumable disconnect with unknown remote state.

A practical name for the last class is `MayStillRun`.

## Current implementation direction

### Legacy MCP timeout

The strongest candidate keeps Codex's elicitation-aware active-time clock, retains the SDK request handle, and explicitly requests cancellation when active time expires.

Cancellation delivery must be bounded and typed. Even confirmed delivery does not prove a mutation had not already committed.

### Prepared call authority

For a call already prepared by the sampling step:

- retain the captured runtime, client, schema, and authority;
- fail on that captured client instead of rerouting to B;
- allow current policy to add restrictions;
- defer policy relaxation until a newly sampled step.

### Cached startup exception

For a cached tool with no prepared call:

- wait for live B only as a bounded startup exception;
- compare A and B authority fingerprints before file rewrite, approval, or execution;
- execute B only after verified equality;
- otherwise return a typed revision mismatch and require a new sampling step.

### Future catalogue publication

Host reload, explicit reconnect, authentication change, server notification, and recovery should use one refresh-ticket vocabulary. Only an accepted-current ticket may publish.

## Next discriminating tests

1. Cancellation delivery fails or stalls.
2. Server receives cancellation but ignores it and commits later.
3. Session-expiry recovery attempts to replay a potential mutation.
4. Stateless modern HTTP stream closure proves terminal cancellation.
5. Stateful or resumable modern transport loses the local wait but may retain remote execution.
6. Refresh B publishes while timed-out operation A remains active; A's late result stays attached to A.
7. Older refresh or relist result finishes after newer publication and is rejected as superseded.
8. Cached A/live B equality and mismatch decisions happen before execution.

## Stop condition

The campaign can advance from investigation when compiled owned-fork tests prove:

- newest-generation publication;
- captured-call authority;
- typed A/B mismatch before execution;
- `MayStillRun` treatment for uncertain post-dispatch outcomes;
- no automatic mutation replay while terminal certainty is absent;
- host preserve, replace, clear, and reject reconstruction behavior across resume and fork.

Public Codex and the official Rust MCP SDK remain read-only. No upstream interaction occurs without a separate human decision.
