# Authority-token propagation across agent runtimes

## In simple words

Agent systems increasingly solve backend races with explicit authority tokens: a deadline, an epoch, an event sequence, a persistence barrier, a continuation cursor, or a live registry owner.

That does not automatically make the user-facing state correct.

A backend may correctly reject a stale writer while the UI still duplicates an assistant message. A durable interrupt may correctly order old and new work while the visible transcript has no durable interrupted outcome. A client may resume one visual message cleanly while the abandoned backend operation continues running after the caller has stopped waiting.

This note maps where authority is created, how it is invalidated, and whether it survives through transport and replay into the visible message or status surface.

## Retrieval boundary

- Vercel AI SDK current observed source: `965b9c69d046378c06be6f7f9f01421a18188530`
- Vercel async-video finalized owned repair: `teamleaderleo/ai#30` head `5fa70d44a06c2f84f03ae3c5c98326a72a0500e9`
- TanStack AI observed source: `aade077647556a7ea17d7ddf73bd4e7dc0258301`
- TanStack durable-run merge: PR `#1015`, commit `d9d1e1f3dbaddf3703a8cdc7d32bd591aaa3fae6`
- OpenCode V1 observed source: `f0afb6750e63ee0a60b052914531bde0afb9bc2b`
- OpenCode V2 durable interrupt merge: PR `#30850`, commit `12e38866ed0722953f5943c2b3e138613ff00ea3`
- LangGraphJS observed source: `6ac60da74f6b9e29d20b111a7947ac3060f1d2dd`
- LangGraph sync durability merge: PR `#2604`, commit `42ec39460bfe0c3be017fb043c668c3204c8a175`
- Retrieval date: 2026-08-06
- Upstream contact authorized: `false`

## Map

| System / seam | Authority token | Scope | Invalidation or commit rule | Backend surface protected | Visible-state mapping | Current gap or limit |
| --- | --- | --- | --- | --- | --- | --- |
| Vercel async video | wall-clock deadline plus caller abort | one submitted provider operation | deadline expiration or caller abort wins settlement | polling waits, webhook finalization, retries, status settlement, terminal acceptance | promise resolves/rejects; no remote-job UI identity | local timeout abandons the wait but does not cancel the provider job |
| TanStack durable sandbox | distributed lease plus monotonic `driverEpoch` | one durable run across hosts | a higher epoch supersedes the previous driver | event-log append and terminal run-record write | replay aligns journal output against stored stream so the UI receives only the remainder | the epoch is meaningful only where every mutation and replay path checks or derives from it |
| OpenCode V2 interruption | durable aggregate event sequence | one session's admitted intent versus interrupt requests | work admitted after the interrupt sequence is protected; older wakeups become stale | process-local coordinator demand and active runner interruption | no transcript message or durable interrupted outcome is projected | durable request authority stops before durable activity outcome and front-facing projection |
| OpenCode V1 session state | Runner generation state plus process-local registry/status publication | one process-local session runner | completion must not release visible idle authority after replacement work becomes active | prompt admission, cancellation, `/session/status` | live busy/idle state and assistant result | current source has a confirmed stale-idle race; owned repair `teamleaderleo/opencode#3` is executing |
| LangGraph Pregel `sync` durability | completed-superstep snapshot of tracked persistence promises | one completed superstep | task writes and checkpoint persistence caused by that superstep settle before next dispatch | scheduler progression and completed-superstep checkpoint boundary | invoke/stream/streamEvents share the scheduler barrier | `async` deliberately allows visible execution progress to lead durable checkpoint state |
| Vercel Workflow Harness | serializable `resumeFrom` / `continueFrom` plus stream-part context | one durable workflow turn across executions | a new execution continues from the persisted cursor; terminal close ends the turn | sandbox session continuation and workflow output writer | continuation drops duplicate `start`/`finish`, replays part preludes, and keeps one assistant message | correct visual continuity depends on preserving both execution cursor and presentation-part context |
| Vercel Chat resume | active response state plus transport reconnect stream | one browser chat response | new request/abort replaces active response | one client-side stream processor | reconnect feeds chunks into an adopted or new assistant message | message identity can be weaker than stream identity; known resume-adoption issue retained as comparison evidence |

## Pattern 1 — settlement authority is not execution ownership

The Vercel video deadline answers a narrow but important question: may this local SDK call still publish a provider result?

It deliberately does not answer whether the remote job was cancelled, whether another observer may attach to that job, or how a later UI should represent the abandoned operation.

This separation is correct. Conflating local timeout with remote cancellation would create false lifecycle claims. A future first-class operation handle would need a separate durable identity and explicit cancel/query semantics.

The owned repair now has a clean three-file head, complete focused execution, independent full acceptance, and an exact-diff review. It is ready in the fork without implying upstream acceptance.

## Pattern 2 — writer fencing needs replay fencing

TanStack's `driverEpoch` is stronger than a simple lock because a superseded host can continue running after lease loss. The epoch is checked on append and terminalization, preventing the loser from poisoning the successor's log or run record.

That backend fence is paired with replay alignment: a takeover reads journaled output, aligns it against the stored event log, and appends only the remainder. Without the second half, the backend could be single-writer-correct while the user still sees duplicated text.

This is the clearest current example of a rear-facing authority token being carried through to front-facing delivery correctness.

## Pattern 3 — durable intent ordering can stop before durable outcome

OpenCode V2 records `session.next.interrupt.requested` and uses its aggregate sequence as the boundary between old and new intent. Delayed old wakeups cannot restart work at or before that boundary, and later admitted prompts are protected.

The design explicitly does not claim a durable `Interrupted` activity outcome and does not project the request into the transcript. That is an honest boundary, but it leaves a later design question: which durable activity identity and projected status will tell a reconnected client what actually happened after interruption was requested?

The V1 path has the inverse profile: it exposes immediate live status, but the authority is process-local and not represented by a durable sequence or generation identity. A target-native characterization now proves that an older idle publication can overwrite replacement-visible busy state. The owned repair serializes normal prompt-run completion and replacement admission; shell and wider durable lifecycle semantics remain explicit non-claims.

## Pattern 4 — presentation continuity has its own state machine

Vercel Workflow Harness persists more than a backend session cursor. It also serializes active text parts, reasoning parts, and pending tool inputs.

On continuation it:

- drops duplicate assistant-message `start` chunks;
- drops intermediate `finish` chunks;
- restores required part-start preludes before deltas;
- writes one terminal `finish` only when the turn truly completes;
- closes the workflow writer only at the terminal boundary.

This demonstrates that execution continuity and presentation continuity are separate contracts. A durable session can resume correctly while the UI stream remains malformed unless the presentation state machine is also checkpointed.

## Pattern 5 — durability strength can be an execution-mode choice

LangGraph's repaired `durability: "sync"` mode snapshots and awaits persistence work caused by the completed superstep before the scheduler prepares and dispatches the next one.

The snapshot is important: it makes the barrier causal and bounded. Writes scheduled later cannot extend a superstep that is already complete.

`async` mode has the opposite positive control: the next node may start while prior persistence is still pending. A live stream can therefore lead recoverable checkpoint state by design. Consumers must not translate “observed in the stream” into “durably committed” without carrying the selected durability mode and event semantics through the integration.

## Front-facing and rear-facing review questions

For any new durable or resumable agent runtime, review both sides.

### Rear-facing

1. What token names the authoritative writer, operation, or completed commit unit?
2. Is it durable across process loss and host movement?
3. Which mutations are fenced: append, metadata, terminalization, cleanup, cancellation, checkpoint writes?
4. Can losing work continue after authority loss, and are its late errors/results adopted?
5. Does timeout mean local abandonment, cooperative cancellation, or provider-confirmed cancellation?
6. If durability is selectable, which scheduler transitions wait in each mode?

### Front-facing

1. Which visible message, status row, checkpoint event, or tool part belongs to the authoritative run?
2. Does reconnect carry a message identity as well as a stream cursor?
3. Can a stale terminal event overwrite a newer busy/running state?
4. Can replay duplicate already-rendered text or tool arguments?
5. Does a durable interrupt/cancel outcome appear in the transcript or status projection?
6. Are partial text/reasoning/tool states checkpointed, or only backend execution state?
7. Can streamed progress be newer than the recoverable durable checkpoint under the selected mode?

## Candidate avenues

### A. Authority-token propagation conformance model

The dependency-free three-store model now executes:

- authoritative backend run record;
- append-only delivery log;
- visible message/status projection.

It demonstrates stale visible idle despite backend epoch fencing, duplicate replay without alignment, and late visible completion after local timeout authority. Evidence class: `model-executed`.

### B. TanStack final-result persistence

The current source still appears to let a persistence transform capture a result before a later middleware transform changes the live result. The target-native regression now reaches package build and the product transform path; its artifact-network side effect has been removed so the next run can decide the actual result-order assertion.

Evidence class today: source-read plus target execution repaired; distinguishing rerun pending.

### C. OpenCode V1 idle authority

The current source has target-native distinguishing evidence: expected replacement-visible `busy`, received stale `idle`.

Owned repair carrier: `teamleaderleo/opencode#3`. It introduces a normal-run finishing state, atomic admission handles, a session semaphore, and a bounded regression. Evidence class: `target-executed defect + repair-prepared`; repair execution pending.

### D. LangGraph superstep durability

Retain the merged sync barrier as a positive conformance reference. The important review dimension is not only whether checkpoint writes eventually settle, but whether scheduler and emitted-state ordering match the durability mode the caller selected.

Evidence class: merged upstream repair and source review; no new defect lane.

### E. Vercel resume message identity

Retain as comparison evidence. A transport reconnect cursor should not silently choose visible message ownership from the last assistant role when the resumed stream's message identity is not yet known.

Evidence class: known/publicly reported comparison, no duplicate lane.

## Current conclusion

The most reusable ecosystem lesson is:

> Authority must be propagated, not merely established.

A backend deadline, epoch, sequence, persistence barrier, or registry owner is only as strong as the last user-visible side effect it governs. Correct systems either carry that token through every mutation and projection, or introduce a second explicit cursor/identity contract at the transport and presentation layers.

This map supports further bounded probes. It does not by itself authorize upstream contact.
