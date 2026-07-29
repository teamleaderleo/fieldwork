# MCP TypeScript v2 reconnect budget and terminal response-channel state

Date: 2026-07-30

Fieldwork lane: #67
Campaign: #65
Programme: #13
Target hub: #7
Parent scout: #20
Worker: ChatGPT GPT-5.6 Thinking acting for `teamleaderleo`
Upstream contact authorized: `false`

## In simple words

The v2 TypeScript client has a setting named `maxRetries`. Source reading made it look as though a server could repeatedly accept an SSE reconnect, close it immediately, and evade the limit forever.

That behavior is real: six successful reopen-and-close cycles all started at retry attempt zero even with `maxRetries: 2`.

The deeper result is narrower than the initial concern. An HTTP 200 response that opens a resumable SSE stream is treated as a successful connection. When that live stream later closes without finishing the logical request, reconnecting again is consistent with the protocol's long-lived stream model. The configured limit currently bounds consecutive failures to open the next HTTP stream, not the lifetime or total number of successful stream connections.

A separate control showed the intended terminal path:

- two consecutive failed GET opens exhausted `maxRetries: 2`;
- the request's stream-end callback fired exactly once;
- the transport remained usable for a later independent JSON response.

A resumed stream that delivered the awaited JSON-RPC result also ended normally and scheduled no further reconnect.

## Verdict

**Confirmed behavior, but no separate defect promoted from successful reopen/drop cycles alone.**

The strongest supported conclusions are:

1. `maxRetries` is an open-failure budget, not a complete unstable-episode budget.
2. Its public wording is broader than the implemented behavior and should be clarified.
3. Per-request failed-open exhaustion reaches a terminal callback once and does not necessarily poison the whole transport.
4. The standalone response-channel failure already tracked by upstream #2098 remains the correct home for transport-wide dead-channel behavior.
5. Lane #66's cross-stream retry-value leak remains a real defect candidate because it changes the pacing of these otherwise valid reconnect chains.

Evidence level:

- source behavior: observed;
- public source-tree HTTP fixture: executed;
- published npm artifact fixture: executed;
- Node 20, 22, and 24: executed;
- higher-level subscription terminal callback: source-observed;
- distinct production consequence beyond #2098: not established;
- upstream contact: none.

## Pins and write boundary

- Public SDK source: `modelcontextprotocol/typescript-sdk@cc4b41617ce3601b1290d67216ea0b194a3cd9ac`
- Published package: `@modelcontextprotocol/client@2.0.0`
- Owned fork probe head: `teamleaderleo/typescript-sdk@96176c1a0041bbf011e9538f3ca3e88987779ee2`
- Owned fork draft PR: `teamleaderleo/typescript-sdk#1`
- Source-tree workflow run: `30477560619`
- Fieldwork release-probe branch head before this report: `teamleaderleo/fieldwork@72210fadb246da19f6fa4ed43eacb249a7342ac6`
- Published-package workflow run: `30478067730`
- Fieldwork PR: #90
- Retrieval date: 2026-07-30

The public SDK repository remained read-only. No upstream issue, pull request, comment, reaction, branch, or message was created.

## Question tested

Does `maxRetries` bound only consecutive HTTP-open failures or the full unstable reconnect episode, and what terminal state does the client expose after it can no longer open a response stream?

## Relevant source behavior

At the pinned revision:

1. `_scheduleReconnection(options, attemptCount)` rejects further scheduling when `attemptCount >= maxRetries`.
2. The reconnect callback calls `_startOrAuthSse(options)`.
3. If `_startOrAuthSse()` rejects, the callback schedules again with `attemptCount + 1`.
4. If `_startOrAuthSse()` succeeds, `_handleSseStream()` owns the newly opened body.
5. When that body later ends without a JSON-RPC response but remains resumable, `_handleSseStream()` calls `_scheduleReconnection(..., 0)`.
6. After the limit is exhausted, `_scheduleReconnection()` emits an error and calls `onRequestStreamEnd` for a per-request stream.
7. A caller such as modern `subscriptions/listen` routes `onRequestStreamEnd` into its logical state machine as a remote end.

The implementation therefore distinguishes:

- failure to establish the next HTTP/SSE stream;
- successful establishment followed by later stream closure;
- successful response delivery;
- caller or transport cancellation.

## Probe architecture

Two independent execution paths were used.

### A. Source-tree fixture

Owned fork file:

`packages/client/test/client/streamableHttp.reconnectBudgetProbe.test.ts`

The fixture runs inside the SDK's Vitest suite and imports the source implementation.

### B. Published release fixture

Fieldwork files:

- `campaigns/0004-mcp-streamable-http-reconnect/lanes/L02-reconnect-budget-terminal-state/probe/package.json`
- `campaigns/0004-mcp-streamable-http-reconnect/lanes/L02-reconnect-budget-terminal-state/probe/probe-release.mjs`
- `.github/workflows/mcp-v2-release-reconnect-probe.yml`

This fixture installs exactly `@modelcontextprotocol/client@2.0.0` from npm and uses only the public `StreamableHTTPClientTransport` surface against a real local HTTP server.

Both paths ran on Node 20, 22, and 24.

## Scenario matrix

| Scenario | HTTP behavior | Attempt sequence | Terminal callback | Result |
| --- | --- | --- | --- | --- |
| Successful primed reopen/drop | GET returns 200 SSE, sends retry + event ID, closes | `0, 0, 0, 0, 0, 0` with `maxRetries: 2` | none during six cycles | reconnect chain continues |
| Consecutive failed opens | GET returns 503 twice | `0, 1`, then exhausted | once | request stream ends |
| Useful resumed stream | GET returns 200 SSE with JSON-RPC response | one attempt at `0` | once after result stream ends | result delivered, no further schedule |
| Later independent request after per-request exhaustion | POST returns application/json | none | unrelated | result delivered successfully |

## Execution evidence

### Source-tree run

Workflow run `30477560619` passed on Node 20, 22, and 24.

The inspected Node 22 job reported:

- `streamableHttp.reconnectBudgetProbe.test.ts`: 3 tests passed;
- `streamableHttp.reconnectProbe.test.ts`: 6 tests passed;
- 37 test files passed;
- 809 tests passed.

### Published release run

Workflow run `30478067730` passed on Node 20, 22, and 24 after installing `@modelcontextprotocol/client@2.0.0` from npm.

The Node 22 output recorded:

#### Successful reopen/drop cycles

- attempts: `[0, 0, 0, 0, 0, 0]`;
- GET count: `6`;
- received `Last-Event-ID` values: `event-0` through `event-5`;
- emitted resumption tokens: `event-0` through `event-6`;
- stream-end count: `0`;
- errors: none.

#### Consecutive failed opens

- GET count: `2`;
- stream-end count: `1`;
- final error includes `Maximum reconnection attempts (2) exceeded.`;
- a later independent POST delivered `{ recovered: true }`.

#### Useful resumed response

- GET count: `1`;
- stream-end count: `1`;
- JSON-RPC result `{ ok: true }` delivered;
- no further reconnect schedule.

## Findings

### F1. `maxRetries` counts consecutive failed stream opens

**Evidence:** source-observed, source-tree executed, published-package executed.

The attempt value increments only when the GET/open path rejects. A successful HTTP 200 resets control to the stream reader. If the body later closes resumably, the next chain starts at zero.

This is the actual implemented contract.

### F2. Successful resumable closes can continue beyond `maxRetries`

**Evidence:** source-tree executed and published-package executed.

Six successful open/close cycles continued under `maxRetries: 2`, preserving and advancing replay event IDs.

This behavior alone is not enough to establish a bug. MCP and SSE both use reconnectable long-lived streams, and a successful connection can later end without terminating the logical stream.

### F3. Public wording is ambiguous

**Evidence:** source documentation observed.

The option is documented as the maximum number of reconnection attempts before giving up. That can reasonably be read as a total episode limit. The implementation instead treats it as the maximum number of consecutive failed attempts to open the next stream.

A clearer description would state that successful HTTP/SSE establishment resets the failed-open counter, even when the newly opened body closes before completing the logical request.

### F4. Per-request failed-open exhaustion terminates that stream once

**Evidence:** source-tree executed and published-package executed.

After two 503 responses:

- the limit error was emitted;
- `onRequestStreamEnd` fired once;
- no third retry was scheduled for that request stream.

For modern `subscriptions/listen`, the client wires this callback into the subscription state machine as a remote end. Thus this path has an explicit logical terminal signal.

### F5. Per-request exhaustion does not automatically close the transport

**Evidence:** published-package executed.

A later independent request on the same transport received a direct JSON response successfully after the earlier per-request stream exhausted its GET reopens.

This is appropriate for a transport supporting independent per-request response streams. One request's terminal failure need not poison unrelated requests.

### F6. A useful response terminates the reconnect chain

**Evidence:** source-tree executed and published-package executed.

When a resumed GET delivered the awaited JSON-RPC response, the client emitted the message, ended the stream once, and scheduled nothing further.

### F7. Standalone response-channel exhaustion remains a separate state

**Evidence:** source mapping and upstream #2098.

The per-request probe cannot disprove #2098's standalone GET dead-channel report. When later POST responses rely on one shared standalone GET, exhaustion of that channel can leave the transport accepting outbound work without a response path.

That transport-wide terminal-policy question should remain attached to #2098 rather than being duplicated here.

## Negative and narrowed results

1. **No separate issue solely for exceeding `maxRetries` through successful opens.** The name is ambiguous, but the mechanism can be a valid long-lived stream lifecycle.
2. **No evidence that per-request exhaustion poisons every future request.** A later direct JSON request succeeded.
3. **No evidence that useful response delivery loops.** It ended cleanly.
4. **No evidence of lost replay identity in the successful-cycle fixture.** `Last-Event-ID` advanced correctly each cycle.
5. **No duplicate issue found for successful-open reset semantics.** That absence does not itself turn the behavior into a defect.
6. **No terminal-policy implementation proposed.** The standalone shared-channel case requires a maintainer decision and is already tracked by #2098.

## Relationship to Lane #66

Lane #66 confirmed that concurrent streams can overwrite each other's SSE retry delay.

That finding changes the interpretation of repeated reconnects:

- repeated successful reconnects are not inherently wrong;
- reconnecting earlier or later because another stream changed the affected stream's retry value is wrong ownership;
- an indefinite valid chain amplifies the importance of keeping each chain's pacing independent.

Therefore Lane #66 remains the first upstream issue candidate. This lane supplies supporting lifecycle context and prevents an inflated claim about the retry-count reset.

## Upstream routing recommendation

### Do not open a separate bug titled “maxRetries can be exceeded”

That title would imply the option is a total lifetime limit, which the implementation and long-lived stream model do not establish.

### Documentation candidate

Clarify `StreamableHTTPReconnectionOptions.maxRetries` as the maximum number of consecutive failures to open the next SSE stream. State whether a successfully opened stream resets the count even when it later closes before logical completion.

### #2098 evidence packet

If upstream contact is later authorized, add a concise distinction to #2098:

- per-request stream exhaustion calls `onRequestStreamEnd` and does not necessarily poison unrelated requests;
- standalone shared-response-channel exhaustion can still leave future POST results undeliverable;
- maintainers should define the terminal state specifically for the standalone channel.

No comment was posted.

## Terminal-policy alternatives for the standalone channel

These remain design choices for maintainer discussion.

### A. Fail later sends immediately

After standalone GET exhaustion, reject sends whose response depends on that channel with a typed disconnected error.

### B. Reset and renegotiate the session

Clear unusable channel/session state and require the client layer to reconnect or initialize again.

### C. Continue reconnecting with bounded backoff

Keep the shared response channel alive as a long-lived connection while exposing its state to the client.

### D. Explicit channel-state API

Expose connected, reconnecting, exhausted, and closed states so hosts can decide policy.

The probes here do not choose among these alternatives.

## Decision

- Lane result: `narrowed / negative defect promotion`
- Behavior existence: confirmed
- Separate SDK defect from successful reopen/drop cycles: unsupported
- Documentation ambiguity: supported
- Standalone terminal-state issue: route to upstream #2098 if authorized
- Campaign: continue
- Next lane: #68, owned session resumption and duplicate-execution trial
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
  streamableHttp.reconnectBudgetProbe.test.ts
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

- source mechanism: yes;
- public source-tree reproduction: yes;
- published package reproduction: yes;
- Node 20/22/24 matrix: yes;
- separate production defect beyond #2098: no;
- documentation ambiguity: yes.

Durable artifacts:

- this report;
- Fieldwork PR #90;
- release probe package and script;
- workflow run `30478067730`;
- owned fork budget test and workflow run `30477560619`.

Decision needed:

- synthesize this as a negative/narrowed result;
- keep Lane #66 as the first held upstream issue;
- route standalone terminal-state evidence to #2098 only after explicit authorization;
- begin Lane #68.
