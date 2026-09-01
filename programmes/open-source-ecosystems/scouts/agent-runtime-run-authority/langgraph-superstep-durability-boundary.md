# LangGraph superstep durability authority

## In simple words

LangGraph uses a different authority boundary from the deadline, driver-epoch, and live-runner systems already mapped by this scout.

Its Pregel scheduler advances through supersteps. Each completed superstep can produce task writes and a checkpoint. The durability mode decides whether that persisted state must become authoritative before the scheduler may dispatch the next superstep.

This is a useful positive reference because the boundary is explicit and user-selectable:

- `sync` means persistence is part of the superstep commit barrier;
- `async` means later computation may begin while prior persistence is still pending;
- exit-oriented durability defers the strongest persistence settlement until run completion.

## Retrieval boundary

- Repository: `langchain-ai/langgraphjs`
- Merged repair: PR `#2604`, `fix(core): enforce sync durability barriers`
- Repair head: `363ad90b9fc9ff7ba70213e34956dc738f78a795`
- Merge commit: `42ec39460bfe0c3be017fb043c668c3204c8a175`
- Current observed source during this pass: `6ac60da74f6b9e29d20b111a7947ac3060f1d2dd`
- Retrieval date: 2026-08-06
- Upstream contact authorized: `false`

## Authority token

The effective token is the completed superstep plus a snapshot of every checkpointer promise scheduled by that run up to the boundary.

The repair added an await over the tracked persistence-promise set after the completed superstep schedules its checkpoint. Taking a promise-set snapshot gives the barrier two useful properties:

1. task writes and the checkpoint caused by the completed superstep must settle before `sync` execution advances;
2. persistence scheduled later cannot indefinitely extend the already-defined boundary.

This is not a writer epoch. It is a commit barrier over a causally scoped set of durable side effects.

## Prior behavior

Before the repair, checkpointer promises were tracked and awaited during final cleanup, but a completed superstep's persistence could overlap preparation and dispatch of the next superstep even when the caller selected `durability: "sync"`.

That made `sync` describe eventual run cleanup more accurately than scheduler ordering.

## Current behavior

After each completed superstep:

1. task writes have already been scheduled as tasks finish;
2. the loop schedules the completed-superstep checkpoint;
3. when durability is `sync`, the loop awaits the tracked persistence work;
4. only then does it emit the completed values/checkpoint metadata and continue scheduler progression.

The merged regression covers `invoke`, `stream`, and `streamEvents`, demonstrating that the barrier belongs to the shared scheduler rather than one presentation API.

A separate `async` control requires the next node to be able to start while prior persistence remains gated. The weaker ordering is therefore intentional, not a missing fence.

## Front-facing implication

A streaming caller can observe values, updates, messages, checkpoints, tasks, tools, or debug events. The durability mode does not make every emitted event itself a persisted acknowledgement.

For `sync`, the repaired completed-superstep boundary means scheduler progress and completed-superstep values/checkpoint metadata do not outrun the persistence caused by that superstep.

For `async`, callers must accept that visible execution progress can lead the durable checkpoint. A crash can therefore produce a replay/recovery boundary older than the latest output observed by a live client.

That distinction should be preserved in UI and operational documentation. A frontend should not infer “durably committed” from “streamed” without knowing the selected durability mode and event type.

## Comparison with other mapped systems

| System | Authority form | What waits |
| --- | --- | --- |
| Vercel async video | wall-clock deadline | local result settlement cannot occur after deadline authority |
| TanStack durable sandbox | lease plus monotonic driver epoch | stale drivers cannot append or terminalize; replay aligns the remainder |
| OpenCode V2 | durable aggregate event sequence | older wakeups cannot cross the interrupt/new-intent boundary |
| LangGraph Pregel `sync` | completed-superstep persistence-promise snapshot | next scheduler superstep cannot dispatch before causal persistence settles |

LangGraph is the clearest example here of durability strength being an explicit execution-mode choice rather than an invariant applied uniformly to every run.

## Review questions

1. Which emissions occur before versus after the completed-superstep persistence barrier?
2. Do custom checkpointers register all causally relevant writes in the tracked promise set?
3. Can a failed captured persistence promise partially advance externally visible state before its error reaches the caller?
4. Does recovery resume from the last completed durable superstep or from finer-grained pending writes?
5. Is the selected durability mode preserved across remote SDK/server boundaries and visible to operators?
6. Do UI consumers distinguish streamed progress from durably committed checkpoint state?

## Current disposition

Retain as a positive architecture and conformance reference.

No new LangGraph defect is promoted by this note. The relevant scheduler gap was already repaired upstream, with explicit positive and negative controls. Its value to Scout 528 is the authority model: a causally scoped persistence barrier whose strength is selected by execution mode.
