# MCP TypeScript v2 legacy reconnect budget and post-timeout lifecycle

Date: 2026-07-30

Fieldwork lane: #67  
Campaign: #65  
Programme: #13  
Target hub: #7  
Parent scout: #20  
Worker: ChatGPT GPT-5.6 Thinking acting for `teamleaderleo`  
Upstream contact authorized: `false`

## In simple words

The initial question was whether `maxRetries` can be bypassed when an SSE reconnect opens successfully and then closes again.

That behavior is real, but it is not the defect by itself. In the MCP 2025-era protocol, a server is allowed to open a resumable SSE connection, send an event ID, close the current HTTP connection, and have the client poll again. A successful reopen can therefore happen many times during one valid long-running request.

The deeper probe found a separate lifecycle problem:

1. a legacy request starts a resumable SSE reconnect chain;
2. the client-side request deadline expires;
3. the request promise rejects with `Request timed out`;
4. the SDK sends `notifications/cancelled` to the server;
5. the transport's pending reconnect chain is not stopped;
6. the default scheduler continues issuing real GET requests with `Last-Event-ID` after the caller has already received the timeout;
7. if a late response arrives on one of those resumed GETs, the protocol layer reports it as a response for an unknown message ID.

This reproduced against both the pinned source tree and the published `@modelcontextprotocol/client@2.0.0` package on Node 20, 22, and 24.

## Verdict

**Confirmed lifecycle defect candidate in the v2 SDK's legacy 2025-era Streamable HTTP compatibility path.**

The confirmed defect is not “successful reconnects exceed `maxRetries`.” The confirmed defect is:

> Settling a legacy request through timeout/cancellation does not terminate the transport-owned reconnect chain for that request.

Consequences demonstrated:

- resumed GET traffic continues after the request promise has rejected;
- cancellation and local network lifecycle disagree about whether the request is finished;
- a late result is surfaced as an unknown-ID error instead of being quietly ignored after cancellation;
- repeated successful reopen/drop cycles keep scheduling at attempt zero, so `maxRetries` does not eventually clean up this orphaned chain.

Scope:

- applies to the SDK v2 package's default 2025-era behavior and older supported protocol revisions;
- does not apply to a compliant 2026-07-28 Streamable HTTP exchange, which has no GET stream endpoint, protocol session, or `Last-Event-ID` resumption;
- a noncompliant 2026 server that emits resumable event IDs can still provoke the transport into a legacy-style GET, recorded as a secondary robustness boundary.

Severity should remain moderate pending production-frequency and request-volume measurements. The behavior creates real post-timeout network work and misleading diagnostics, but no data corruption or duplicate application execution has been demonstrated in this lane.

## Pins and write boundary

- Public SDK source: `modelcontextprotocol/typescript-sdk@cc4b41617ce3601b1290d67216ea0b194a3cd9ac`
- Published package: `@modelcontextprotocol/client@2.0.0`
- Owned fork probe head: `teamleaderleo/typescript-sdk@75a3d0331bdeb85539994eb351d31a6a5d37cb72`
- Owned fork draft PR: `teamleaderleo/typescript-sdk#1`
- Final source-tree workflow run: `30479313714`
- Published-package workflow run: `30479661274`
- Fieldwork PR: #90
- Retrieval date: 2026-07-30

The public SDK repository remained read-only. No upstream issue, pull request, comment, reaction, branch, or message was created.

## Protocol-era boundary

### 2026-07-28

The modern Streamable HTTP revision:

- uses one POST per request;
- scopes an SSE response stream to that POST;
- removes the standalone GET stream endpoint;
- removes protocol-level sessions;
- does not support resumable SSE through `Last-Event-ID`;
- treats closing the request's SSE stream as cancellation.

The SDK requires explicit opt-in to this era. A hand-constructed v2 client remains in the 2025-era mode by default.

### 2025-11-25 and earlier supported revisions

The legacy Streamable HTTP contract permits:

- an SSE priming event carrying an event ID;
- server-side closure of the current HTTP connection without ending the logical stream;
- polling through GET plus `Last-Event-ID`;
- a stream-local `retry` instruction the client must respect;
- multiple simultaneous SSE streams;
- cancellation through `notifications/cancelled` rather than closing the response stream.

Repeated successful polling is therefore valid. The request's cancellation state and its polling state still need to end together.

## Source ownership map

### Protocol request layer

The shared protocol layer owns:

- request ID and pending response handler;
- caller signal and request timeout;
- rejection of the caller promise;
- sending `notifications/cancelled` in the legacy era;
- deleting the response handler and timeout state after settlement.

It supplies a request-scoped `AbortSignal` to Streamable HTTP only when the negotiated era is modern and cancellation is implemented by closing the per-request stream.

### Streamable HTTP transport

The transport owns:

- SSE reader state;
- resumption token and replay ID threading;
- reconnect scheduler callbacks;
- retry attempt count;
- GET requests carrying `Last-Event-ID`.

Its reconnect callback checks `options.requestSignal` when one exists. Legacy requests receive no such signal. Sending `notifications/cancelled` does not alter the transport's reconnect state.

### Lifecycle mismatch

After a legacy timeout:

- protocol state says the request is settled and removes its response handler;
- server-facing protocol traffic says the request is cancelled;
- transport state can still say the request stream should be resumed.

That mixed ownership is the root cause supported by the probes.

## Probe inventory

### Source-tree tests in the owned fork

- `streamableHttp.reconnectBudgetProbe.test.ts`
- `streamableHttp.protocolEraProbe.test.ts`
- `streamableHttp.legacyTimeoutProbe.test.ts`
- earlier Lane #66 reconnect ownership probes

The final legacy-timeout suite tests:

1. a pending custom-scheduler reconnect after timeout;
2. real default-scheduler GET traffic after timeout;
3. a late resumed response after timeout;
4. cancellation notification delivery;
5. cleanup after explicit client close.

### Published release probe in Fieldwork

Files:

- `campaigns/0004-mcp-streamable-http-reconnect/lanes/L02-reconnect-budget-terminal-state/probe/package.json`
- `campaigns/0004-mcp-streamable-http-reconnect/lanes/L02-reconnect-budget-terminal-state/probe/probe-release.mjs`
- `.github/workflows/mcp-v2-release-reconnect-probe.yml`

The fixture installs exactly `@modelcontextprotocol/client@2.0.0` and uses public `Client` and `StreamableHTTPClientTransport` exports against local HTTP servers.

## Scenario matrix

| Scenario | Protocol era | Observed result |
| --- | --- | --- |
| Successful primed reopen/drop cycles | 2025 | attempts remain `0`; chain can continue beyond `maxRetries` |
| Consecutive GET-open failures | 2025 | attempts increment and exhaust at configured limit |
| Useful resumed JSON-RPC response | 2025 | result delivered; chain ends |
| Request timeout while reconnect is pending | 2025 | promise rejects and cancellation notification posts; reconnect remains live |
| Default scheduler after timeout | 2025 | real resumed GET count continues increasing after rejection |
| Late result after timeout | 2025 | client emits unknown-message-ID diagnostic |
| SSE closes without event ID | compliant 2026 | no GET reconnect; stream ends once |
| Modern response emits event ID | noncompliant 2026 | transport attempts legacy-style GET resumption |

## Execution evidence

### Source-tree matrix

Workflow run `30479313714` passed on Node 20, 22, and 24.

The inspected Node 22 job reported:

- 39 test files passed;
- 815 tests passed;
- all reconnect, era, and legacy-timeout probes passed;
- frozen-lockfile install passed.

### Published-package matrix

Workflow run `30479661274` passed on Node 20, 22, and 24 after installing `@modelcontextprotocol/client@2.0.0` from npm.

The inspected Node 22 output recorded:

- one cancellation notification;
- 20 resumed GETs by the time the request rejection was observed;
- four additional resumed GETs after rejection before the observation completed;
- replay IDs advancing from `call-0` through `call-23`;
- a separate late-response case producing:
  `Received a response for an unknown message ID`.

The exact count depends on scheduler timing. The load-bearing property is that the count increased after the request promise had already rejected.

Fieldwork integrity and external-reference-policy workflows also passed on the updated branch.

## Findings

### F1. `maxRetries` counts consecutive failures to open the next stream

**Evidence:** source-observed, source-tree executed, published-package executed.

A successful GET hands control back to the stream reader. If that body closes resumably, a new chain starts at attempt zero. This matches valid legacy polling and should be documented more precisely.

### F2. Successful polling beyond `maxRetries` is not independently defective

**Evidence:** protocol-documented and probe-executed.

Six successful open/close cycles continued under `maxRetries: 2` while preserving replay IDs. A total-cycle ceiling would terminate valid long-running streams unless the SDK also defined a stability or request-lifetime policy.

### F3. Legacy request timeout does not cancel its reconnect chain

**Evidence:** source-observed, source-tree executed, published-package executed.

The request deadline rejects the caller and sends `notifications/cancelled`. The legacy transport has no request-scoped abort signal, so a pending reconnect callback remains executable and can schedule the next GET.

### F4. The default scheduler performs real network work after timeout

**Evidence:** public published-package probe.

This is not limited to an artificial custom scheduler. The built-in timer path issued additional HTTP GET requests after the caller had already received the timeout.

### F5. A late result is diagnosed rather than ignored

**Evidence:** source-tree executed and published-package executed.

After timeout cleanup removes the response handler, a resumed result with the original request ID reaches `_onresponse()` and emits an unknown-message-ID error.

The 2025 cancellation specification says the sender should ignore a response arriving after cancellation. Treating this race as an error creates misleading diagnostics for an expected cancellation race.

### F6. Compliant modern Streamable HTTP avoids this path

**Evidence:** specification and era-control probe.

A modern response without resumable event IDs does not schedule a GET reconnect. Modern request timeout cancellation also has a request-scoped abort signal because closing the response stream is the cancellation mechanism.

### F7. Noncompliant modern event IDs expose a robustness gap

**Evidence:** source-tree era-control probe.

The transport does not gate GET resumption on protocol era. A server claiming 2026-07-28 that emits an event ID can cause a GET carrying both `MCP-Protocol-Version: 2026-07-28` and `Last-Event-ID`.

This is secondary. The primary confirmed issue remains the supported legacy path.

## Negative and narrowed results

1. Do not file “`maxRetries` can be exceeded” as the main bug.
2. No evidence shows that one exhausted per-request stream necessarily poisons unrelated direct-JSON requests.
3. Useful resumed response delivery terminates its chain normally.
4. No duplicate execution was demonstrated; that remains Lane #68's application-level question.
5. No data corruption was demonstrated.
6. No matching upstream issue was found for post-timeout reconnect continuation.
7. The standalone response-channel exhaustion tracked by upstream #2098 remains distinct.
8. The finding is not a compliant native-2026 reconnect defect.

## Held upstream issue packet

### Proposed title

`Legacy Streamable HTTP reconnects continue after the client request times out`

### Summary

In `@modelcontextprotocol/client@2.0.0`, a 2025-era request whose SSE response becomes resumable can keep polling through GET after the request deadline expires. The `Client` rejects with `Request timed out` and sends `notifications/cancelled`, but the transport's reconnect chain receives no request-scoped abort signal in the legacy era.

With the default scheduler, real GET requests continue after rejection. If a late response is delivered on a resumed GET, the client reports it as a response for an unknown message ID.

### Minimal sequence

1. Connect a default v2 `Client` to a server negotiating `2025-11-25`.
2. Send `tools/call` with a short request timeout.
3. Return a POST SSE response containing `retry`, an event ID, empty data, then close.
4. Return the same priming pattern from resumed GET requests.
5. Observe the request reject and `notifications/cancelled` arrive.
6. Observe further GET requests after rejection.
7. Optionally return the original JSON-RPC response from a later GET and observe the unknown-ID diagnostic.

### Expected behavior requiring maintainer confirmation

When a request settles through timeout or caller cancellation, the transport should stop any reconnect chain owned by that request. A late response racing with cancellation should be ignored or handled through an explicitly documented diagnostic policy consistent with the cancellation specification.

### Evidence to attach if authorized

- published-package reproducer;
- source-tree regression tests;
- Node 20/22/24 workflow results;
- protocol-era control proving modern compliant traffic does not enter the path;
- exact GET counts, cancellation receipt, and late-response error.

### Possible repair directions

These are discussion options, not committed fixes:

1. Thread a request-lifecycle abort signal through legacy Streamable HTTP too, while continuing to send `notifications/cancelled` as required by the legacy protocol.
2. Give each reconnect chain an explicit cancel/dispose operation keyed to the originating request.
3. Have `Protocol` invoke a transport request-stream teardown hook whenever any request settles through timeout or caller abort.
4. Treat late responses for locally cancelled request IDs as expected races rather than generic unknown-ID errors, using a bounded cancelled-ID tombstone if needed.

## Relationship to other work

- Lane #66 remains a separate confirmed legacy reconnect ownership issue: one stream can use another stream's retry interval.
- Upstream #2098 covers failed-open exhaustion and a dead standalone response channel.
- Upstream #2499 covers loss of an incoming resumption token.
- Lane #68 should test whether application work can execute twice or whether only result delivery is duplicated/lost.

## Decision

- Lane result: `confirmed, scope-corrected`
- Successful-cycle reset alone: negative defect promotion
- Post-timeout reconnect continuation: confirmed defect candidate
- Late-response unknown-ID diagnostic: confirmed supporting consequence
- Native compliant 2026 path: unaffected by this mechanism
- Campaign: continue
- Next lane: #68 after synthesis of this packet
- Upstream contact: none

## Verification

### Source tree

```sh
corepack enable
pnpm install --frozen-lockfile
pnpm --filter @modelcontextprotocol/client test -- \
  streamableHttp.reconnectProbe.test.ts \
  streamableHttp.reconnectPublicProbe.test.ts \
  streamableHttp.reconnectTimerProbe.test.ts \
  streamableHttp.reconnectBudgetProbe.test.ts \
  streamableHttp.protocolEraProbe.test.ts \
  streamableHttp.legacyTimeoutProbe.test.ts
```

### Published package

```sh
cd campaigns/0004-mcp-streamable-http-reconnect/lanes/L02-reconnect-budget-terminal-state/probe
npm install --ignore-scripts --no-audit --no-fund
npm test
```

## Handoff

State: ready-for-synthesis

Scope supported:

- protocol-era distinction: yes;
- source mechanism: yes;
- public source-tree reproduction: yes;
- published package reproduction: yes;
- default scheduler real-network consequence: yes;
- Node 20/22/24 matrix: yes;
- production frequency and aggregate load: not measured;
- duplicate execution: not tested here.

Durable artifacts:

- this report;
- Fieldwork PR #90;
- release probe package and script;
- release workflow run `30479661274`;
- owned-fork tests and source workflow run `30479313714`.

Decision needed:

- hold or authorize the upstream issue-first packet;
- decide whether the late-response diagnostic belongs in the same report;
- synthesize the corrected protocol-era scope into Campaign #65;
- begin Lane #68 only after retaining these cancellation/reconnect controls.
