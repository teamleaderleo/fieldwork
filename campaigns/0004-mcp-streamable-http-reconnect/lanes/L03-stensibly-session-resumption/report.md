# MCP session replay, result delivery, and duplicate execution in Stensibly

Date: 2026-07-30

Fieldwork lane: #68
Campaign: #65
Programme: #13
Primary target hub: #7
Owned testbed: `teamleaderleo/stensibly`
Parent scout: #20
Worker: ChatGPT GPT-5.6 Thinking acting for `teamleaderleo`
Callsign: Keel
Upstream contact authorized: `false`

## In simple words

There are two different recovery mechanisms that can look similar from the outside.

### MCP transport replay

A stateful MCP server can store a result after the original response stream disappears. The client reconnects with its session ID and `Last-Event-ID`, and the server sends the stored result again.

The application tool does not run again. The result may be delivered more than once, so delivery is at least once while execution remains once.

### Application retry

Stensibly's current hosted MCP endpoint does not keep MCP sessions or SSE replay state. When a result is lost, the client must reconcile the operation receipt or send a new JSON-RPC request with the same application idempotency key.

That new request enters the tool handler again. Stensibly's exact-request idempotency returns the original item and prevents a second durable effect. A changed request under the same key is rejected.

These mechanisms are complementary:

- transport replay avoids handler re-entry when the server has the stored result;
- application idempotency protects explicit retries, missing replay state, client restarts, and stateless endpoints.

## Verdict

**The duplicate-execution concern is real, but ownership depends on the recovery path.**

Confirmed:

1. A v2 stateful Streamable HTTP server with an event store can replay one stored result multiple times while the tool execution count remains one.
2. Stensibly's current hosted MCP endpoint cannot perform that replay because it is POST-only, stateless, JSON-response mode, creates a server per request, and disables session IDs.
3. After an ambiguous Stensibly result, an exact application retry invokes `createItem` again but persists one item and one creation event.
4. Stensibly's operation receipt identifies the completed operation and advises against retrying when the durable result is already recorded.
5. A changed durable request under the same idempotency key conflicts and creates no second item.

Not supported:

- a claim that MCP transport replay itself re-executes a tool;
- a claim that current hosted Stensibly resumes an MCP session;
- a claim that application idempotency eliminates duplicate handler invocation;
- a claim that duplicate result delivery is duplicate durable execution.

## Pins and write boundary

### MCP TypeScript SDK

- Public source: `modelcontextprotocol/typescript-sdk@cc4b41617ce3601b1290d67216ea0b194a3cd9ac`
- Package line: v2, `@modelcontextprotocol/server@2.0.0`
- Owned fork session replay probe head: `teamleaderleo/typescript-sdk@d9fcf9d085f9c75bfec49d714a7a17ba1c5ad571`
- Owned fork draft PR: `teamleaderleo/typescript-sdk#1`
- Successful probe workflow: `30480085816`

### Stensibly

- Source pin: `teamleaderleo/stensibly@20241e668fb493b7f389df8b9df7f229bcadff68`
- Test branch: `keel/mcp-ambiguous-retry-idempotency`
- Test PR: `teamleaderleo/stensibly#565`
- Latest test head while report was drafted: `teamleaderleo/stensibly@8232f4c760884516f4359075a341348207e7c33c`

### Fieldwork

- Branch: `lane/68-stensibly-session-resumption`
- Owned path: this report

No upstream MCP issue, pull request, comment, reaction, branch, or message was created. No Stensibly deployment, hosted mutation, credential use, or irreversible operation was performed.

## Three identities that must remain separate

| Identity | Scope | What it answers | Replay or retry behavior |
| --- | --- | --- | --- |
| JSON-RPC request ID | one logical protocol request/response | which response settles which request | transport replay preserves the stored response ID; an application retry can use a new request ID |
| MCP event ID / `Last-Event-ID` | one resumable SSE stream | where event replay resumes | selects stored events after the last acknowledged event |
| Stensibly idempotency key | one durable application operation | whether a mutation is an exact retry or a conflicting new request | exact retry returns the original durable result; changed request conflicts |

Conflating these identities produces incorrect conclusions:

- seeing a response twice does not prove the tool ran twice;
- seeing the handler run twice does not prove two items were persisted;
- changing the JSON-RPC request ID does not create a new durable operation when the idempotency key and request fingerprint match;
- reusing an MCP event ID does not authorize a changed application mutation.

## Current Stensibly transport boundary

`src/mcp-http.ts` and `src/runner-mcp-http.ts` both implement the hosted boundary as follows:

- HTTP `POST` only;
- one newly constructed MCP server and transport per request;
- `sessionIdGenerator: undefined`;
- `enableJsonResponse: true`;
- server closed after request handling;
- no event store;
- no GET SSE resume endpoint;
- no DELETE session endpoint.

This is a deliberate stateless request/response profile. It supports durable application state through the ledger, not durable MCP transport state.

The existing Stensibly test named `mcp-http-reconnect.test.ts` proves that ledger state remains readable and writable after recreating the hosted app. It does not prove preservation of an MCP session, replay token, pending request, or SSE stream.

### Capability result

Current hosted Stensibly can recover by:

- reading durable state;
- reading an operation receipt;
- retrying the exact application request with the same idempotency key;
- recreating the app or client connection.

Current hosted Stensibly cannot recover by:

- resuming an MCP session ID;
- reconnecting a request SSE stream by `Last-Event-ID`;
- replaying a stored MCP result without invoking a new tool request.

## Stensibly application recovery contract

The MCP server instructions tell callers to:

1. use the same idempotency key for an exact mutation retry;
2. call `get_operation_receipt` when a mutation response is ambiguous;
3. inspect the recorded result before deciding whether to retry.

The operation receipt returns either:

- `recorded`, with operation, event ID, item ID, result identity, and `do_not_retry`; or
- `unknown`, with guidance to retry the exact same request using the same key.

Recent Stensibly work binds item creation and artifact attachment to canonical SHA-256 request fingerprints. Exact retries return the original result. Changed durable fields conflict. Legacy events missing a request fingerprint fail closed.

## Stensibly ambiguity probe

Owned test:

`test/mcp-ambiguous-retry-idempotency.test.ts`

### Fixture

- in-memory SQLite ledger;
- real hosted Stensibly MCP handler;
- real authentication and project authorization;
- real `create_item`, `get_operation_receipt`, `get_item`, and `list_work` tools;
- proxy counter around the ledger's `createItem` method;
- no production resources.

### Sequence

1. Initialize the hosted MCP endpoint.
2. Send `create_item` with a unique idempotency key.
3. Receive HTTP 200, then cancel the response body to model a client that loses or abandons result delivery.
4. Confirm the application handler ran once.
5. Recreate the hosted app over the same durable ledger.
6. Read the operation receipt.
7. Confirm it reports `item.created`, the recorded event ID and item ID, and `do_not_retry`.
8. Send the exact same `create_item` request again with a new JSON-RPC request ID and the same idempotency key.
9. Confirm the handler invocation count becomes two.
10. Confirm the retry returns the original item.
11. Confirm one item and one `item.created` event exist and the event ID matches the receipt.
12. Send a changed title under the same idempotency key.
13. Confirm the handler invocation count becomes three, the operation conflicts, and still one item exists.

### Initial assertion corrections

The first run expected `get_item` event entries to expose the idempotency key. That field is intentionally not part of the public item event projection. The test was corrected to reconcile by the receipt's durable event ID.

The second run matched an unstable wording fragment. The server correctly returned `Idempotency key was already used for a different operation`. The assertion was narrowed to the stable semantic phrase `different operation`.

These were test-contract corrections. Neither failure contradicted the one-effect behavior.

## V2 transport replay probe

Owned fork test:

`packages/server/test/server/streamableHttp.sessionReplayProbe.test.ts`

### Fixture

- v2 `McpServer`;
- `WebStandardStreamableHTTPServerTransport`;
- generated session ID;
- in-memory `EventStore`;
- resumable SSE response mode;
- one tool with an explicit execution counter;
- tool closes the original SSE stream, waits on a gate, and then returns a result;
- raw GET reconnect using session ID and `Last-Event-ID`.

### Sequence

1. Initialize and capture the MCP session ID.
2. Send one tool call.
3. The tool execution counter becomes one.
4. The server emits a priming event and closes the original response stream.
5. The tool completes after the stream is gone.
6. The event store records the final JSON-RPC result.
7. GET with the session ID and priming `Last-Event-ID` replays the final result.
8. A second GET with the same replay cursor replays the same final result again.
9. The tool execution counter remains one throughout.

### Execution result

Workflow `30480085816` passed the client and server probe suites on Node 20, 22, and 24.

The first server-probe run had already produced the correct replayed result, but the assertion searched for unescaped JSON inside MCP text content. The test was corrected to parse:

1. the SSE `data:` JSON;
2. the MCP result content;
3. the nested application JSON text.

After that correction, both replays returned:

```json
{
  "operationId": "operation-1",
  "executions": 1
}
```

The handler execution counter remained one.

## Confirmed findings

### F1. Transport replay is result replay, not request re-execution

**Evidence:** SDK source, existing SDK tests, executed counter probe.

The event store records outbound JSON-RPC messages by stream. A `Last-Event-ID` GET asks the server to send stored events after the cursor. It does not submit the original `tools/call` again.

The counter probe replayed the final result twice while executing the tool once.

### F2. Transport result delivery is at least once

**Evidence:** executed counter probe.

The same replay cursor could retrieve the stored final result more than once. This is duplicate delivery of one stored response.

Consumers and protocol layers must use request/response identity to settle one logical request once and treat later duplicates as duplicates or diagnostics.

### F3. Application retry re-enters the handler

**Evidence:** Stensibly ambiguity probe.

An exact retry is a new JSON-RPC `tools/call`. The Stensibly handler and ledger method are entered again.

Application idempotency therefore cannot be described as exactly-once execution. It provides a single durable effect for an exact retry.

### F4. Stensibly exact idempotency prevents duplicate durable creation

**Evidence:** existing fingerprint tests and new MCP ambiguity probe.

The exact retry returned the original item. One item and one creation event remained. A changed request under the same key conflicted and created nothing else.

### F5. The operation receipt is the preferred recovery path

**Evidence:** MCP instructions, receipt contract, ambiguity probe.

After ambiguous delivery, the receipt can establish that the operation was recorded and identify its result without invoking the mutation again.

The exact retry remains a fallback for an `unknown` receipt or a client that cannot perform reconciliation.

### F6. Current hosted Stensibly has an MCP replay capability gap

**Evidence:** source-observed.

Because sessions and event storage are disabled, the hosted endpoint cannot replay a completed MCP result after response loss. It relies on application receipts and idempotency instead.

This is not automatically a defect. It is a deliberate simpler transport profile with different recovery costs and guarantees.

### F7. A stateful hosted mode would require lifecycle ownership beyond one request

**Evidence:** source mapping and SDK server contract.

Enabling session replay would require at least:

- stable session routing across HTTP requests;
- persistent or shared event storage;
- GET resume handling;
- DELETE/session cleanup handling;
- session expiry and resource bounds;
- authentication and authorization checks on resumed streams;
- multi-instance ownership or shared state;
- observability for session, request, stream, event, and durable operation identities.

Changing `sessionIdGenerator` alone would be insufficient because Stensibly currently creates and closes the transport per POST.

## Failure and risk matrix

| Situation | MCP transport action | Application action | Handler runs | Durable effect |
| --- | --- | --- | ---: | ---: |
| Stateful replay after lost stream | GET with session + `Last-Event-ID` | none | 1 | 1 |
| Same stored result replayed twice | two replay GETs | none | 1 | 1 |
| Stateless ambiguous result, receipt found | new read request | read receipt/item | 1 | 1 |
| Stateless exact mutation retry | new `tools/call` | same idempotency key and exact request | 2 | 1 |
| Stateless changed request under same key | new `tools/call` | changed durable input | 2 successful entries plus conflict entry | 1 |
| Retry without idempotency protection | new `tools/call` | unrestricted mutation | potentially 2 | potentially 2 |

The final row is the application danger. MCP does not provide exactly-once durable mutation semantics by itself.

## Relationship to current Stensibly incident #490

Incident #490 reports tool disappearance, ambiguous mutation outcomes, and failed continued use in ChatGPT. This lane does not establish that the TypeScript SDK reconnect finding caused that incident.

It provides a sharper recovery model:

- when the current Stensibly endpoint returns or loses a JSON result, there is no MCP session replay to recover it;
- the caller must receive a visible result, read an operation receipt, or retry exactly;
- host-level tool disappearance can prevent both the original mutation and its reconciliation path;
- durable idempotency protects the ledger only when the client retains the operation key and can call the tool surface again.

Thus #490 still spans host routing, executable tool availability, result delivery, and application recovery. The reconnect investigation explains one transport capability boundary but does not collapse the incident into one SDK root cause.

## Negative and narrowed results

1. **No duplicate tool execution from transport replay:** the counter remained one.
2. **No claim that one handler invocation means one delivery:** the stored result was replayed twice.
3. **No claim that application retry is exactly once:** the handler was entered again.
4. **No second durable item from exact retry:** one item and one creation event remained.
5. **No MCP session resume on current hosted Stensibly:** the endpoint has no session or GET path.
6. **No evidence that enabling sessions alone would fix ChatGPT tool disappearance:** host routing and executable binding remain separate.
7. **No upstream defect packet from this lane:** the observed v2 replay behavior is expected and correctly separates delivery from execution.

## Recommended Stensibly actions

### 1. Merge the ambiguity regression test after normal review

The test captures the existing intended contract:

- ambiguous result;
- receipt reconciliation;
- exact retry;
- handler re-entry;
- one durable effect;
- changed-request conflict.

### 2. Make operation identity easy to retain

Every write result and typed ambiguity response should expose or preserve:

- idempotency key;
- durable result identity;
- operation receipt lookup inputs;
- request ID for diagnostics;
- guidance to read receipt before retry.

### 3. Keep the hosted transport profile explicit

Documentation and diagnostics should state that the hosted endpoint is stateless JSON-response mode and that reconnect means a new request over durable application state, not MCP session replay.

### 4. Evaluate stateful replay as a separate campaign

A future stateful transport trial should answer:

- whether replay materially improves ChatGPT sustained-use recovery;
- whether the host sends and preserves session and event headers;
- how sessions route across Worker instances;
- how event stores are bounded and expired;
- how authentication changes during a session;
- whether the added complexity improves the actual #490 failure path.

This should not be implemented as a small toggle in the current hosted handler.

## Campaign synthesis

### Lane #66

Confirmed SDK defect candidate: concurrent client streams can overwrite each other's retry delay. This remains the first held upstream issue packet.

### Lane #67

Confirmed and narrowed: `maxRetries` bounds consecutive failed opens. Successful long-lived reopen/drop cycles alone are not a separate defect. Documentation can be clearer.

### Lane #68

Confirmed separation of guarantees:

- stateful transport replay can redeliver a stored result without re-execution;
- current Stensibly hosted transport does not support that path;
- exact application retry re-enters the handler while preserving one durable effect;
- operation receipts are the lowest-cost reconciliation mechanism for current Stensibly.

## Decision

- Lane result: `confirmed boundary and negative duplicate-execution result for transport replay`
- SDK issue from this lane: none
- Stensibly test improvement: ready after CI and review
- Hosted session replay capability: separate design campaign, not immediate implementation
- Campaign #65 primary upstream packet: Lane #66 retry-state isolation
- Upstream contact: none

## Verification

### MCP TypeScript SDK stateful replay

Owned fork workflow:

- run `30480085816`;
- Node 20: success;
- Node 22: success;
- Node 24: success;
- server replay counter probe: success.

### Stensibly application retry

Owned Stensibly PR:

- `teamleaderleo/stensibly#565`;
- Bun unit test: `test/mcp-ambiguous-retry-idempotency.test.ts`;
- full CI result to be recorded in the issue handoff after the final assertion correction.

## Handoff

State: ready-for-synthesis after final Stensibly CI confirmation

Scope supported:

- MCP stateful result replay: yes;
- replay execution count: yes;
- duplicate delivery: yes;
- current hosted Stensibly session capability: yes, source-observed absence;
- application retry handler count: yes;
- application durable-effect count: yes;
- production ChatGPT host root cause: no.

Durable artifacts:

- this report;
- Stensibly draft PR #565;
- SDK fork draft PR #1;
- SDK workflow run `30480085816`;
- Fieldwork lane branch.

Decision needed:

- synthesize Campaign #65;
- review and merge the Stensibly regression test separately;
- keep Lane #66's issue packet held for explicit authorization;
- decide whether a stateful hosted Stensibly transport trial deserves its own campaign.
