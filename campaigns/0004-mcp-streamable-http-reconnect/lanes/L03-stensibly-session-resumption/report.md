# MCP session replay, result delivery, and duplicate execution in Stensibly

Date: 2026-07-30

Fieldwork lane: #68
Campaign: #65
Programme: #13
Target hub: #7
Owned testbed: `teamleaderleo/stensibly`
Parent scout: #20
Worker: ChatGPT GPT-5.6 Thinking acting for `teamleaderleo`
Callsign: Keel
Upstream contact authorized: `false`

## In simple words

Two different recovery mechanisms were tested.

### Stateful MCP replay

A stateful MCP server can store a result after the original SSE response disappears. The client reconnects with its session ID and `Last-Event-ID`, and the server sends the stored result again.

The result may be delivered more than once. The tool does not run again.

### Stateless application retry

Stensibly's current hosted MCP endpoint has no MCP sessions, GET resume path, or event store. After an ambiguous result, the client reads an operation receipt or sends a new tool request with the same Stensibly idempotency key.

That new request enters the handler again. Exact-request idempotency returns the original item and preserves one durable effect. A changed request under the same key conflicts.

## Verdict

**Confirmed boundary:** transport replay provides at-least-once result delivery with one tool execution; Stensibly application retry can invoke the handler again while preserving one durable effect.

Confirmed:

1. A v2 stateful Streamable HTTP server replayed one stored final result twice while the tool execution counter remained one.
2. Current hosted Stensibly cannot perform MCP session replay because it is POST-only, stateless JSON-response mode, creates and closes a transport per request, disables session IDs, and has no event store.
3. After an abandoned Stensibly result, the operation receipt identified the completed item and advised `do_not_retry`.
4. Retrying the exact mutation entered `createItem` again and returned the original item.
5. One item and one `item.created` event existed after the retry.
6. A changed request under the same idempotency key entered the handler, conflicted, and created nothing else.

Not supported:

- MCP result replay re-executes the tool;
- current hosted Stensibly resumes MCP sessions;
- application idempotency prevents duplicate handler invocation;
- duplicate delivery proves duplicate durable execution;
- the TypeScript SDK reconnect finding alone explains Stensibly incident #490.

## Pins and artifacts

### MCP TypeScript SDK

- Public source: `modelcontextprotocol/typescript-sdk@cc4b41617ce3601b1290d67216ea0b194a3cd9ac`
- v2 package line: `@modelcontextprotocol/server@2.0.0`
- Owned fork probe head: `teamleaderleo/typescript-sdk@d9fcf9d085f9c75bfec49d714a7a17ba1c5ad571`
- Owned fork draft PR: `teamleaderleo/typescript-sdk#1`
- Successful workflow: `30480085816`

### Stensibly

- Source pin: `teamleaderleo/stensibly@20241e668fb493b7f389df8b9df7f229bcadff68`
- Test head: `teamleaderleo/stensibly@8232f4c760884516f4359075a341348207e7c33c`
- Ready PR: `teamleaderleo/stensibly#565`
- Successful CI: `30480313838`

### Fieldwork

- Branch: `lane/68-stensibly-session-resumption`
- Owned path: this report

No MCP upstream issue, pull request, comment, reaction, branch, or message was created. No hosted Stensibly mutation, deployment, credential use, or irreversible operation was performed.

## Identity model

| Identity | Owner | Purpose | Recovery behavior |
| --- | --- | --- | --- |
| JSON-RPC request ID | protocol request | associates one response with one logical request | replay preserves the stored response ID; application retry may use a new ID |
| MCP event ID / `Last-Event-ID` | resumable SSE stream | selects the replay cursor | causes stored events after the cursor to be sent again |
| Stensibly idempotency key | durable application operation | recognizes exact retry versus conflicting request | exact retry returns original durable result; changed request conflicts |

These identities are independent:

- a response delivered twice does not prove two executions;
- a handler entered twice does not prove two items;
- a new JSON-RPC ID does not create a new durable operation when the Stensibly key and request fingerprint match;
- an MCP replay cursor does not authorize changed application input.

## Current Stensibly transport boundary

`src/mcp-http.ts` and `src/runner-mcp-http.ts` both use:

- `POST` only;
- a newly constructed server and transport per request;
- `sessionIdGenerator: undefined`;
- `enableJsonResponse: true`;
- no event store;
- no GET SSE resume endpoint;
- no DELETE session endpoint;
- server close after each request.

This profile preserves application state through the ledger, not transport state through an MCP session.

The existing `mcp-http-reconnect.test.ts` proves that ledger state survives app recreation. It does not prove session ID preservation, replay-token preservation, pending-request continuation, or SSE resumption.

## Stensibly recovery contract

The MCP instructions direct callers to:

1. retain the idempotency key;
2. call `get_operation_receipt` after an ambiguous write;
3. inspect the receipt or durable state before retrying;
4. retry only the exact request with the same key when appropriate.

The receipt returns:

- `recorded`, with operation, event ID, item ID, result identity, and `do_not_retry`; or
- `unknown`, with guidance to retry the exact request using the same key.

Recent Stensibly work binds creation and artifact retries to canonical SHA-256 request fingerprints. Exact retries return the original result. Changed durable inputs conflict.

## Stensibly ambiguity probe

Test:

`test/mcp-ambiguous-retry-idempotency.test.ts`

### Fixture

- in-memory SQLite ledger;
- real hosted Stensibly MCP handler;
- real token authentication and project authorization;
- real `create_item`, `get_operation_receipt`, `get_item`, and `list_work` tools;
- proxy counter around `createItem`;
- no production resources.

### Executed sequence

1. Initialize the endpoint.
2. Send `create_item` with a unique idempotency key.
3. Receive HTTP 200 and cancel the response body to model result-delivery loss.
4. Observe `createItem` invocation count `1`.
5. Recreate the app over the same ledger.
6. Read the operation receipt.
7. Observe `item.created`, one event ID, one item ID, and `do_not_retry`.
8. Send the exact mutation again with a new JSON-RPC ID and the same idempotency key.
9. Observe `createItem` invocation count `2`.
10. Receive the original item.
11. Read the item and observe one `item.created` event matching the receipt event ID.
12. List work and observe one item.
13. Send a changed title under the same key.
14. Observe `createItem` invocation count `3`, a `different operation` conflict, and still one item.

### Verification

Stensibly CI run `30480313838` passed:

- typecheck;
- 952 Bun tests across 192 files, including this test;
- Convex tests;
- Cloudflare Worker bundle;
- runtime-parity job.

Two earlier runs corrected test assumptions rather than product behavior:

- `get_item` intentionally omits the idempotency key from its public event projection, so reconciliation now uses the receipt's event ID;
- the conflict assertion now matches the stable semantic phrase `different operation`.

## V2 stateful replay probe

Test:

`packages/server/test/server/streamableHttp.sessionReplayProbe.test.ts`

### Fixture

- v2 `McpServer`;
- `WebStandardStreamableHTTPServerTransport`;
- generated session ID;
- in-memory `EventStore`;
- resumable SSE response mode;
- one tool with an execution counter;
- tool closes the original SSE stream, waits, and then returns a result;
- GET reconnect using session ID and `Last-Event-ID`.

### Executed sequence

1. Initialize and capture the session ID.
2. Submit one tool call.
3. Observe execution count `1`.
4. Read the priming event ID after the tool closes the original stream.
5. Let the tool finish while no live response writer exists.
6. Confirm the event store records the final JSON-RPC result.
7. GET with session ID and priming `Last-Event-ID`.
8. Receive the stored result with `{ "operationId": "operation-1", "executions": 1 }`.
9. Repeat the same GET replay.
10. Receive the same stored result again.
11. Observe execution count remains `1`.

### Verification

Workflow `30480085816` passed the client and server probe suites on Node 20, 22, and 24. The conformance workflow for the same head also passed.

The first replay run already returned the correct result but used a string assertion against escaped JSON inside MCP text content. The final test parses the SSE envelope, MCP result, and nested application JSON.

## Findings

### F1. MCP transport replay does not resubmit the request

The event store records outbound JSON-RPC messages by stream. A GET with `Last-Event-ID` asks the server to send stored messages after the cursor. It does not call `tools/call` again.

The counter remained one across two result replays.

### F2. Transport result delivery is at least once

The same replay cursor returned the stored final result more than once. Duplicate result delivery is therefore possible and expected in the tested replay model.

The protocol/client layer must use response identity to settle one logical request once and classify later copies as duplicates or diagnostics.

### F3. Application retry re-enters the handler

A Stensibly exact retry is a new `tools/call`. The handler and ledger method run again.

Application idempotency provides one durable effect, not exactly-once execution.

### F4. Exact Stensibly idempotency prevents duplicate durable creation

The exact retry returned the original item. One item and one creation event remained. Changed durable input under the same key conflicted.

### F5. Receipt reconciliation is cheaper than mutation retry

When a receipt is recorded, reading it identifies the result without entering the mutation handler again. The exact retry is a fallback for an unknown receipt or a client unable to reconcile.

### F6. Current hosted Stensibly has no MCP replay path

Because sessions, event storage, and GET handling are disabled, hosted Stensibly relies on receipts and idempotency after ambiguous result delivery.

This is a deliberate simpler profile, but its recovery guarantees and costs differ from a stateful MCP endpoint.

### F7. Enabling stateful replay requires system ownership beyond one flag

A production stateful mode would require:

- stable session routing across requests and instances;
- persistent/shared event storage;
- GET resume handling;
- DELETE/session cleanup;
- session expiry and resource limits;
- authentication and authorization on resumed streams;
- observability for session, request, stream, event, and durable-operation IDs;
- clear behavior during token expiry and deployment replacement.

Setting a session ID generator while still creating and closing one transport per POST would not provide a durable session.

## Recovery matrix

| Situation | Tool handler entries | Result deliveries | Durable effects |
| --- | ---: | ---: | ---: |
| Stateful replay after stream loss | 1 | 1 or more | 1 |
| Same stored result replayed twice | 1 | 2 | 1 |
| Stateless ambiguity followed by receipt read | 1 | original may be lost; receipt delivered | 1 |
| Stateless exact mutation retry | 2 | retry result delivered | 1 |
| Changed mutation under same key | prior successful entries plus conflict entry | conflict delivered | 1 |
| Retry without application idempotency | potentially 2 | potentially 2 | potentially 2 |

MCP does not provide exactly-once durable mutation semantics by itself.

## Relationship to Stensibly incident #490

This lane does not prove that SDK reconnect bookkeeping caused #490.

It establishes a relevant recovery boundary:

- current hosted Stensibly has no MCP result replay;
- an ambiguous mutation must be reconciled by receipt/state or retried exactly;
- host-level tool disappearance can remove both the original mutation path and the receipt-reconciliation path;
- idempotency protects the ledger only when the client retains the key and can call the tool surface again.

Incident #490 still spans host routing, executable-tool availability, result delivery, and application recovery.

## Negative results

1. Transport replay did not duplicate tool execution.
2. One tool execution did not imply one result delivery.
3. Application retry was not exactly-once execution.
4. Exact application retry did not duplicate durable creation.
5. Current hosted Stensibly did not resume an MCP session.
6. Enabling sessions alone would not address host tool disappearance.
7. This lane produced no MCP upstream defect packet; the v2 replay behavior worked as intended.

## Recommended actions

### Stensibly

1. Review and merge PR #565 as a regression for ambiguous result recovery.
2. Keep idempotency key, operation receipt inputs, durable result ID, and reconciliation guidance visible in mutation outcomes and typed ambiguity errors.
3. Document that hosted reconnect currently means a new request over durable application state, not MCP session replay.
4. Treat stateful hosted replay as a separate design campaign rather than a small handler toggle.

### MCP campaign

1. Keep Lane #66's cross-stream retry-state isolation issue as the primary held upstream packet.
2. Keep Lane #67 as a narrowed documentation/terminal-state result.
3. Record this lane as evidence that session replay correctly separates duplicate delivery from duplicate execution.

## Decision

- Lane result: `confirmed boundary`
- Transport duplicate execution: disproved
- Transport duplicate delivery: confirmed
- Stensibly exact retry handler re-entry: confirmed
- Stensibly duplicate durable effect under exact retry: disproved
- Current hosted Stensibly session replay: unavailable
- SDK issue from this lane: none
- Stensibly test improvement: ready for review
- Upstream contact: none

## Handoff

State: ready-for-synthesis

Scope supported:

- MCP stateful result replay: yes;
- replay execution count: yes;
- duplicate delivery: yes;
- current hosted Stensibly session capability: source-confirmed absence;
- application retry handler count: yes;
- application durable-effect count: yes;
- production ChatGPT host root cause: no.

Durable artifacts:

- this report;
- Stensibly PR #565;
- SDK fork PR #1;
- SDK workflow `30480085816`;
- Stensibly CI `30480313838`.

Campaign synthesis:

- Lane #66: confirmed SDK defect candidate;
- Lane #67: confirmed behavior, defect promotion rejected;
- Lane #68: confirmed separation of result replay, handler retry, and durable idempotency.
