# Codex Rust MCP tool-timeout cancellation

Status: matrix executed; legacy mechanism narrowed; direct source candidate pending lifecycle ownership

Fieldwork issue: #134  
Campaign: #133  
Outcome-model follow-up: #162  
Owned fork experiment: `teamleaderleo/codex#22`  
Upstream contact authorized: false

## Exact execution identity

- Public source pin: `openai/codex@5989dcc470695fc3f25a7eb3e90c014ef56d7d2a`
- Owned experiment base and probes: `teamleaderleo/codex@2f7d44ea57758e913b196c6b14a432b0761efe8d`
- Executed owned experiment head: `teamleaderleo/codex@e322eb92a6745616953bc00a3db8046c499dc6a7`
- Fieldwork workflow head: `b427bd826c7d35e0088cc43b2638ace996ffdce6`
- Completed matrix run: `30512864849`
- Rust SDK dependency: `rmcp = 3.0.0`
- Execution date: 2026-07-30

The experiment-head delta is one harness repair: both candidate transformations are scoped to `RmcpClient::call_tool`. Earlier runs stopped at the preceding `resources/read` block. The repaired workflow formats generated candidate Rust before executing behavior.

## Baseline defect

The real Codex `RmcpClient::call_tool` probe proves the current legacy timeout path can return while the remote request remains active:

```text
caller reports tools/call timeout
server observes cancellation = false
delayed synthetic mutation completes = true
follow-up request succeeds = true
```

A persisted timeout output therefore records what Codex told the model. It does not settle the remote operation.

## Required fact separation

The cancellation and receipt layers must retain these facts independently:

1. caller deadline reached;
2. request dispatched or not dispatched;
3. cancellation requested;
4. cancellation delivery completed, failed, or timed out;
5. server cancellation observed where the fixture can prove it;
6. transport terminal, closed, resumable, or unknown;
7. external effect committed, prevented, reconciled absent, or outcome unknown.

Cancellation delivery never proves that a mutation did not commit. The ignored-cancellation control receives cancellation and commits later.

## Executed controls

Every baseline/candidate variant ran the same six controls:

1. cooperative legacy cancellation, delayed effect, and follow-up request;
2. user elicitation longer than the configured tool timeout;
3. modern `2026-07-28` HTTP request-stream behavior;
4. cancellation delivery blocked by a server that stops reading;
5. server receives cancellation and deliberately commits anyway;
6. timed-out request alongside an unrelated concurrent request.

All expected assertions passed in run `30512864849`.

## Matrix results

### Baseline: current Codex outer timeout

- preserves elicitation-aware active-time accounting;
- sends no legacy cancellation;
- cooperative delayed mutation completes after timeout;
- follow-up and unrelated concurrent requests remain usable;
- caller return remains bounded on the stalled transport because the request future is dropped;
- modern pending request stream remains open.

Disposition: confirmed defect baseline.

### Candidate A: SDK-native request timeout

Mechanism: place the legacy deadline in `PeerRequestOptions.timeout` while retaining the outer timeout only for requested-modern handling.

Executed result:

- cooperative server observes cancellation and stops the delayed effect;
- unrelated concurrent request completes and the connection stays healthy;
- user elicitation time is charged against the deadline, causing cancellation during the user wait;
- cancellation delivery can stall beyond the caller bound when the server stops reading;
- ignored cancellation still permits a late commit;
- modern request-stream behavior remains unchanged.

Disposition: useful SDK control; unsuitable as the universal Codex policy.

### Candidate B: pause-aware explicit cancellation

Mechanism: retain the legacy `RequestHandle`, wait on `handle.rx` under Codex active-time accounting, then await `handle.cancel()` after timeout.

Executed result:

- preserves elicitation pause semantics;
- cooperative server observes cancellation and stops the delayed effect;
- unrelated concurrent request completes and the connection stays healthy;
- awaiting cancellation can stall beyond the caller bound on a wedged transport;
- ignored cancellation still permits a late commit;
- modern request-stream behavior remains unchanged.

Disposition: request-scoped semantics are sound; unbounded cancellation delivery violates the caller deadline.

### Candidate C: pause-aware bounded cancellation with transport escalation

Mechanism: retain the legacy `RequestHandle`, preserve active-time accounting, give `handle.cancel()` a 100 ms delivery bound, and cancel the shared service when delivery fails or stalls.

Executed result:

- preserves elicitation pause semantics;
- cooperative cancellation remains request-scoped when delivery succeeds;
- unrelated concurrent request completes and the connection remains healthy on the successful-delivery path;
- stalled cancellation delivery returns within the bound and closes the unhealthy service;
- ignored cancellation still permits a late commit;
- modern request-stream behavior remains unchanged.

Disposition: leading legacy mechanism, pending connection-generation and manager-owned retirement work.

## Remaining lifecycle blocker

The experiment closes the `RunningService` directly. A production candidate needs ownership above that object:

1. fence or classify dispatch during cancellation resolution;
2. bind delayed teardown to the exact connection generation;
3. prevent an older timeout task from closing a newer service;
4. replace a dead stored `ClientState::Ready` entry;
5. reconnect, reinitialize, and republish catalogue state through the manager;
6. preserve unrelated calls or deliver typed invalidation;
7. retain the timed-out operation lineage through recovery;
8. prohibit automatic replay of a potential mutation while effect certainty is absent.

This lifecycle owner overlaps Campaign #84 publication generations and Campaign #83 operation receipts. The layers remain separate source changes.

## Modern protocol boundary

The matrix confirms that all three candidate transformations leave the high-level modern HTTP path unchanged. The pending request SSE stream remained open after caller timeout while a follow-up request succeeded.

Modern `call_tool` also owns MRTR / `input_required` rounds. A complete solution needs an SDK-owned cancellable high-level operation or an equivalent terminal stream contract. Raw request substitution would lose lifecycle behavior.

## Receipt consumption

Fieldwork #162 owns the behavior-neutral internal execution states:

```text
NotDispatched
RemoteResultReceived
LocalFailureUnclassified
LocalTimeoutOutcomeUnknown
```

Campaign #83 may later map those typed facts into conservative receipt readiness. Generic error strings, delivered cancellation, or a persisted timeout result provide insufficient settlement evidence.

## Next bounded action

Design one manager-owned legacy retirement primitive with:

- connection-generation token;
- dispatch fence or explicit invalidation;
- bounded request cancellation;
- generation-checked transport retirement;
- reconnect/reinitialize/publication receipt;
- no mutation replay.

Apply it on a clean current-main Codex branch only after the ownership contract is reviewed. Keep modern high-level cancellation in its SDK lifecycle lane.

No upstream contact occurred.
