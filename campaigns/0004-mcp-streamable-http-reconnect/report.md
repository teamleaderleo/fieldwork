# MCP Streamable HTTP reconnect campaign synthesis

Date: 2026-07-30

Fieldwork campaign: #65  
Programme: #13  
Target hub: #7  
Parent scout: #20  
Upstream contact authorized: `false`

## In simple words

The campaign separated four things that are easy to blur together:

1. retry advice for one resumable response stream;
2. terminal ownership after one request times out;
3. replay of a stored result after transport loss;
4. a new application request after the original result is uncertain.

Two client-side defect candidates survived exact public execution in the supported 2025-era compatibility transport:

- one stream can use another stream's SSE `retry` value;
- a request can report timeout while its resumable reconnect chain continues issuing GET requests and later produces an unknown-message diagnostic.

The server-side Stensibly lane found a dependency-version boundary instead of a new defect:

- exact SDK 1.29.0 loses a request-scoped terminal result after the SSE stream is closed;
- exact published SDK 1.30.0 stores and replays that result without re-executing the handler;
- the bug is already owned and repaired upstream;
- current hosted Stensibly is stateless JSON-response mode and does not expose that session-replay path.

## Protocol-era boundary

These findings concern the SDK's supported 2025-era Streamable HTTP compatibility path, which uses sessions, GET reconnects, SSE event IDs, and `Last-Event-ID`.

Protocol revision `2026-07-28` has no protocol session, GET stream endpoint, or `Last-Event-ID` resumption. The campaign does not project legacy reconnect findings onto that native modern path.

## Exact lane results

### Lane #66 — concurrent reconnect ownership

Durable report: PR #82, merged.

Confirmed:

- request stream A receives retry advice and event ID A;
- request stream B later receives different retry advice and event ID B;
- A reconnects through a GET carrying A's own `Last-Event-ID`;
- if that GET fails, A's next delay uses B's later retry value.

Both directions executed on Node 20, 22, and 24:

| A instruction | Later B instruction | A next delay |
| ---: | ---: | ---: |
| 50 ms | 5000 ms | 5000 ms |
| 5000 ms | 50 ms | 50 ms |

The transport also records one reconnect-cancellation callback. With two pending timers, close can leave the older timer alive until it fires, although abort guards prevented network resurrection in the tested path.

Disposition:

- confirmed client defect candidate;
- narrow title: `StreamableHTTPClientTransport shares SSE retry state across concurrent streams`;
- upstream packet remains held for explicit authorization.

### Lane #67 — request timeout and reconnect terminal state

Durable report: PR #90, merged.

The original `maxRetries` concern narrowed:

- successful reopen cycles legitimately reset the consecutive failed-open count;
- `maxRetries` is not a total lifetime budget for a resumable stream.

A deeper terminal-state defect then reproduced against source and exact published `@modelcontextprotocol/client@2.0.0` on Node 20, 22, and 24:

1. a default v2 client negotiates the 2025-era path;
2. one request starts a resumable SSE reconnect chain;
3. the request deadline expires;
4. the caller receives `Request timed out` and cancellation is sent;
5. the transport continues issuing resumed GET requests with `Last-Event-ID`;
6. a late result is reported for an unknown message ID.

The default scheduler generated real HTTP traffic after caller settlement.

Disposition:

- confirmed client terminal-ownership candidate;
- keep separate from the retry-value coupling issue;
- retain `maxRetries` wording as a documentation clarification, not a limit-bypass bug;
- upstream packet remains held for explicit authorization.

### Lane #68 — Stensibly result loss, replay, and application retry

Durable report: PR #104, merged. PR #100 was closed unmerged as its older conflicting generation.

Current hosted Stensibly:

- POST-only;
- stateless JSON-response mode;
- session IDs disabled;
- fresh server and transport per request;
- no event store or GET resume path.

Exact SDK 1.29.0 stateful fixture:

- a real Stensibly mutation commits one item and one creation event;
- `closeSSEStream()` removes the live request stream;
- only the priming event is stored;
- the terminal result is not replayable;
- the reconnect GET returns no result;
- the original caller times out;
- an exact new application retry enters the handler again but returns the original item and preserves one durable effect.

Exact published SDK 1.30.0 fixture:

- two request-stream events are stored;
- one reconnect GET returns the original result;
- handler execution remains one during transport replay;
- a later exact new request raises handler entries to two while durable item/event count remains one.

The 1.29 defect is already tracked and repaired by the SDK's store-first response work on the v1.x and v2 lines. No duplicate upstream report is warranted.

Disposition:

- upgrade to at least verified SDK 1.30.0 before enabling stateful request-scoped replay;
- keep operation receipts and exact idempotency because transport replay does not prevent a client from sending a new request after uncertainty;
- duplicate transport delivery was not demonstrated by the final lane fixture;
- current hosted exposure is absent because stateful replay is disabled.

## Ownership model

| Concern | Correct owner |
| --- | --- |
| retry delay | one reconnect chain / response stream |
| failed-open retry count | one reconnect chain |
| request deadline | protocol request operation |
| reconnect termination after request settlement | request-linked stream lifecycle |
| session and event replay | server transport plus event store |
| duplicate response settlement | client request map |
| durable mutation deduplication | application idempotency contract |
| uncertainty reconciliation | application receipt or read path |

A shared transport may host many request streams, but stream-local retry and terminal state cannot be stored as one transport-global value.

## Evidence ranking

### Confirmed and novel

1. Cross-stream SSE retry-state coupling.
2. Resumable GET activity continuing after request timeout.

Both have exact source and published-package execution on Node 20/22/24 and are scoped to the 2025 compatibility path.

### Confirmed supporting behavior

- one reconnect cancellation slot can leave an older timer pending;
- `maxRetries` counts consecutive failed opens;
- application exact retry can re-enter a handler while preserving one durable effect.

### Existing upstream ownership

- SDK 1.29 request-scoped terminal result loss after stream disconnection;
- corresponding store-first repair in fixed SDK releases;
- standalone dead-response-channel behavior already tracked separately.

### Negative results

- no evidence that native 2026 Streamable HTTP uses legacy GET resumption;
- no duplicate durable Stensibly mutation under exact retry;
- no duplicate transport result delivery in the final Lane #68 fixture;
- no evidence that enabling a session ID alone would create durable hosted replay;
- no authorization to file or comment upstream.

## Recommended next actions

1. Keep the two client packets separate and narrow.
2. Reduce each to one standalone public reproduction before any contact decision.
3. Upgrade Stensibly's SDK independently of upstream reporting.
4. Retain the 1.29 negative fixture and invert it to a replay-success regression after upgrade.
5. Preserve receipts and exact idempotency as application-level recovery.
6. Treat hosted stateful replay as a separate architecture decision requiring stable routing, shared event storage, expiry, authorization, and observability.

## Campaign decision

State: `complete — packets held`

- Lane #66: confirmed client defect candidate, merged evidence.
- Lane #67: confirmed client terminal-ownership candidate, merged evidence.
- Lane #68: fixed dependency exposure and hosted recovery boundary, merged evidence.
- Upstream contact: none.
- Filing authorization: absent.

## Durable records

- Lane #66: Fieldwork PR #82.
- Lane #67: Fieldwork PR #90.
- Lane #68: Fieldwork PR #104.
- Superseded Lane #68 generation: PR #100, closed without merge.
- Campaign synthesis: this report and PR #102.
- Owned SDK fixture: `teamleaderleo/typescript-sdk#1`.
- Owned Stensibly fixture: `teamleaderleo/stensibly#565`.
