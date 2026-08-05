# Authority-token propagation across agent runtimes

## In simple words

Agent systems increasingly solve backend races with explicit authority tokens: a deadline, an epoch, an event sequence, a continuation cursor, or a live registry owner.

That does not automatically make the user-facing state correct.

A backend may correctly reject a stale writer while the UI still duplicates an assistant message. A durable interrupt may correctly order old and new work while the visible transcript has no durable interrupted outcome. A client may resume one visual message cleanly while the abandoned backend operation continues running after the caller has stopped waiting.

This note maps where authority is created, how it is invalidated, and whether it survives through transport and replay into the visible message or status surface.

## Retrieval boundary

- Vercel AI SDK current observed source: `965b9c69d046378c06be6f7f9f01421a18188530`
- Vercel async-video clean repair candidate: `teamleaderleo/ai#30` head `5fa70d44a06c2f84f03ae3c5c98326a72a0500e9`
- TanStack AI observed source: `aade077647556a7ea17d7ddf73bd4e7dc0258301`
- TanStack durable-run merge: PR `#1015`, commit `d9d1e1f3dbaddf3703a8cdc7d32bd591aaa3fae6`
- OpenCode V1 observed source: `f0afb6750e63ee0a60b052914531bde0afb9bc2b`
- OpenCode V2 durable interrupt merge: PR `#30850`, commit `12e38866ed0722953f5943c2b3e138613ff00ea3`
- Retrieval date: 2026-08-05
- Upstream contact authorized: `false`

## Map

| System / seam | Authority token | Scope | Invalidation rule | Backend surface protected | Visible-state mapping | Current gap or limit |
| --- | --- | --- | --- | --- | --- | --- |
| Vercel async video | wall-clock deadline plus caller abort | one submitted provider operation | deadline expiration or caller abort wins settlement | polling waits, webhook finalization, retries, status settlement, terminal acceptance | promise resolves/rejects; no remote-job UI identity | local timeout abandons the wait but does not cancel the provider job |
| TanStack durable sandbox | distributed lease plus monotonic `driverEpoch` | one durable run across hosts | a higher epoch supersedes the previous driver | event-log append and terminal run-record write | replay aligns journal output against stored stream so the UI receives only the remainder | the epoch is meaningful only where every mutation and replay path checks or derives from it |
| OpenCode V2 interruption | durable aggregate event sequence | one session's admitted intent versus interrupt requests | work admitted after the interrupt sequence is protected; older wakeups become stale | process-local coordinator demand and active runner interruption | no transcript message or durable interrupted outcome is projected | durable request authority stops before durable activity outcome and front-facing projection |
| OpenCode V1 session state | in-memory runner registry plus live status publication | one process-local session runner | runner deletion / internal idle / status update | prompt admission, cancellation, `/session/status` | live busy/idle state and assistant result | no explicit generation token spans runner state, registry release, and delayed status publication |
| Vercel Workflow Harness | serializable `resumeFrom` / `continueFrom` plus stream-part context | one durable workflow turn across executions | a new execution continues from the persisted cursor; terminal close ends the turn | sandbox session continuation and workflow output writer | continuation drops duplicate `start`/`finish`, replays part preludes, and keeps one assistant message | correct visual continuity depends on preserving both execution cursor and presentation-part context |
| Vercel Chat resume | active response state plus transport reconnect stream | one browser chat response | new request/abort replaces active response | one client-side stream processor | reconnect feeds chunks into an adopted or new assistant message | message identity can be weaker than stream identity; known resume-adoption issue retained as comparison evidence |

## Pattern 1 — settlement authority is not execution ownership

The Vercel video deadline answers a narrow but important question: may this local SDK call still publish a provider result?

It deliberately does not answer whether the remote job was cancelled, whether another observer may attach to that job, or how a later UI should represent the abandoned operation.

This separation is correct. Conflating local timeout with remote cancellation would create false lifecycle claims. A future first-class operation handle would need a separate durable identity and explicit cancel/query semantics.

## Pattern 2 — writer fencing needs replay fencing

TanStack's `driverEpoch` is stronger than a simple lock because a superseded host can continue running after lease loss. The epoch is checked on append and terminalization, preventing the loser from poisoning the successor's log or run record.

That backend fence is paired with replay alignment: a takeover reads journaled output, aligns it against the stored event log, and appends only the remainder. Without the second half, the backend could be single-writer-correct while the user still sees duplicated text.

This is the clearest current example of a rear-facing authority token being carried through to front-facing delivery correctness.

## Pattern 3 — durable intent ordering can stop before durable outcome

OpenCode V2 records `session.next.interrupt.requested` and uses its aggregate sequence as the boundary between old and new intent. Delayed old wakeups cannot restart work at or before that boundary, and later admitted prompts are protected.

The design explicitly does not claim a durable `Interrupted` activity outcome and does not project the request into the transcript. That is an honest boundary, but it leaves a later design question: which durable activity identity and projected status will tell a reconnected client what actually happened after interruption was requested?

The V1 path has the inverse profile: it exposes immediate live status, but the authority is process-local and not represented by a durable sequence or generation identity.

## Pattern 4 — presentation continuity has its own state machine

Vercel Workflow Harness persists more than a backend session cursor. It also serializes active text parts, reasoning parts, and pending tool inputs.

On continuation it:

- drops duplicate assistant-message `start` chunks;
- drops intermediate `finish` chunks;
- restores required part-start preludes before deltas;
- writes one terminal `finish` only when the turn truly completes;
- closes the workflow writer only at the terminal boundary.

This demonstrates that execution continuity and presentation continuity are separate contracts. A durable session can resume correctly while the UI stream remains malformed unless the presentation state machine is also checkpointed.

## Front-facing and rear-facing review questions

For any new durable or resumable agent runtime, review both sides.

### Rear-facing

1. What token names the authoritative writer or operation?
2. Is it durable across process loss and host movement?
3. Which mutations are fenced: append, metadata, terminalization, cleanup, cancellation?
4. Can losing work continue after authority loss, and are its late errors/results adopted?
5. Does timeout mean local abandonment, cooperative cancellation, or provider-confirmed cancellation?

### Front-facing

1. Which visible message, status row, or tool part belongs to the authoritative run?
2. Does reconnect carry a message identity as well as a stream cursor?
3. Can a stale terminal event overwrite a newer busy/running state?
4. Can replay duplicate already-rendered text or tool arguments?
5. Does a durable interrupt/cancel outcome appear in the transcript or status projection?
6. Are partial text/reasoning/tool states checkpointed, or only backend execution state?

## Candidate avenues

### A. Authority-token propagation conformance model

Create a small cross-runtime model with three stores:

- authoritative backend run record;
- append-only delivery log;
- visible message/status projection.

Exercise takeover, timeout, reconnect, cancellation, and delayed terminal publication. The model should demonstrate which combinations of deadline, epoch, sequence, and cursor are sufficient for each layer.

Evidence class today: architecture design only.

### B. TanStack final-result persistence

The current source still appears to let a persistence transform capture a result before a later middleware transform changes the live result. The current-head target test is the deciding evidence path.

Evidence class today: source-read plus exact-head test registered.

### C. OpenCode V1 generation identity

Do not select a production repair from the current timed-out stale-idle probe. First prove the test service identity and name the exact blocked barrier. A stronger future design may require a per-generation publication token rather than only reordering delete/set operations.

Evidence class today: source concern; current direct-service probe invalidated.

### D. Vercel resume message identity

Retain as comparison evidence. A transport reconnect cursor should not silently choose visible message ownership from the last assistant role when the resumed stream's message identity is not yet known.

Evidence class today: known/publicly reported comparison, no duplicate lane.

## Current conclusion

The most reusable ecosystem lesson is:

> Authority must be propagated, not merely established.

A backend deadline, epoch, or sequence is only as strong as the last user-visible side effect it governs. Correct systems either carry that token through every mutation and projection, or introduce a second explicit cursor/identity contract at the transport and presentation layers.

This map supports further bounded probes. It does not by itself promote a new defect or authorize upstream contact.
