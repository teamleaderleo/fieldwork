# Stensibly MCP result replay, loss, and duplicate-execution boundaries

Date: 2026-07-30

Fieldwork lane: #68  
Campaign: #65  
Programme: #13  
Primary target hub: #7  
Parent scout: #20  
Owned testbed: `teamleaderleo/stensibly`  
Worker: ChatGPT GPT-5.6 Thinking acting under the Stensibly callsign `Kestrel`  
Upstream contact authorized: `false`

## In simple words

This lane separates four outcomes that are easy to confuse after an MCP response stream breaks:

1. **lost result** — the server completed work, but the client never receives the result;
2. **duplicate delivery** — the same stored result reaches the client more than once;
3. **duplicate handler execution** — the application tool handler runs again;
4. **duplicate durable effect** — the application creates or changes durable state twice.

Stensibly currently has two different protection layers:

- its hosted MCP endpoint is stateless JSON-response mode, so it does not use MCP sessions, event-store replay, or `Last-Event-ID` resumption;
- its mutation layer uses exact idempotency fingerprints and operation receipts, so an ambiguous result can be reconciled and an exact retry returns the original durable object.

A test-only stateful server using Stensibly's exact installed SDK version exposed a known SDK defect. Stensibly is locked to `@modelcontextprotocol/sdk@1.29.0`. In that release, a request-scoped SSE stream closed with `closeSSEStream()` loses the terminal response instead of storing it for replay. The client sends a `Last-Event-ID` GET, but the event store contains only the priming event. The original call times out.

Stensibly's application idempotency still prevents a duplicate durable effect: a new exact retry runs the handler again but returns the same item and leaves one `item.created` event. A changed request under the same key is rejected.

This exact server-side replay defect is already tracked upstream as TypeScript SDK issue #2151 and fixed on the current v2 line by PR #2342. No duplicate upstream report is warranted.

## Verdict

**Confirmed dependency-version exposure with an application-level recovery control.**

- Current hosted Stensibly endpoint: not exposed to this stateful replay mechanism because it is stateless and POST-only.
- Test-only stateful path using Stensibly's pinned SDK 1.29.0: terminal result loss reproduced.
- Duplicate transport delivery: not demonstrated.
- Automatic replay without re-execution: unavailable on pinned 1.29.0 for this path.
- Explicit application retry: handler runs again.
- Duplicate durable effect: prevented by Stensibly's exact idempotency contract.
- Current v2 SDK line: upstream fix exists.

Operational decision:

> Do not enable sessionful request-scoped SSE replay in Stensibly while using SDK 1.29.0. Upgrade to a release containing the store-first fix, or carry a reviewed backport, before treating `closeSSEStream()` plus event-store replay as a recovery guarantee.

## Pins and write boundary

- Stensibly main revision reviewed: `teamleaderleo/stensibly@20241e668fb493b7f389df8b9df7f229bcadff68`
- Stensibly test branch: `keel/mcp-ambiguous-retry-idempotency`
- Stensibly test head under Kestrel continuation: `teamleaderleo/stensibly@308788ac592d56372c2b3a46e02c443c43cf4753`
- Stensibly PR: #565
- Installed MCP SDK: `@modelcontextprotocol/sdk@1.29.0`
- SDK 1.29.0 release commit inspected: `modelcontextprotocol/typescript-sdk@e12cbd7078db388152f6e839abdbe09ba01f3f32`
- Current v2 source pin used by Campaign #65: `modelcontextprotocol/typescript-sdk@cc4b41617ce3601b1290d67216ea0b194a3cd9ac`
- Existing upstream issue: `modelcontextprotocol/typescript-sdk#2151`
- Existing upstream fix: `modelcontextprotocol/typescript-sdk#2342`
- Retrieval date: 2026-07-30

The public SDK repository remained read-only. No issue, pull request, comment, reaction, branch, or message was created upstream.

## Hosted Stensibly boundary

`src/mcp-http.ts` constructs the production-facing hosted handler with:

- `sessionIdGenerator: undefined`;
- `enableJsonResponse: true`;
- POST handling only;
- a fresh server and transport per request;
- no event store.

Consequences:

- an abandoned response body can create an ambiguous result;
- there is no MCP session or transport replay to recover that result;
- application receipts and idempotency are the recovery mechanism;
- the request-scoped replay defect characterized below is not currently active in the hosted endpoint.

## Existing Stensibly application controls

### Ambiguous result and receipt

The existing PR #565 fixture sends `create_item` through the real hosted MCP handler, allows the mutation to commit, and abandons the successful response body.

After recreating the app:

- `get_operation_receipt` finds the committed item and event;
- the receipt advises against repeating the operation;
- the result ambiguity is resolved from durable evidence rather than from transport state.

### Exact retry

When the same durable request and idempotency key are submitted again:

- the `create_item` handler enters again;
- `StensiblyStore.createItem()` recognizes the exact operation fingerprint;
- it returns the original item;
- one item exists;
- one `item.created` event exists.

When the payload changes under the same key:

- the handler enters;
- the store rejects the operation as a conflicting reuse;
- no second item or creation event appears.

This proves that duplicate handler execution and duplicate durable effect are separate properties.

## Stateful replay fixture

The added test uses real public package classes from Stensibly's installed dependency:

- `Client`;
- `StreamableHTTPClientTransport`;
- `McpServer`;
- `WebStandardStreamableHTTPServerTransport`;
- the SDK `EventStore` contract;
- Stensibly's real in-memory SQLite `StensiblyStore`.

Fixture sequence:

1. Initialize a sessionful 2025-era Streamable HTTP client/server pair.
2. Send `create_item` with an exact idempotency key.
3. Commit the real Stensibly item and event.
4. Call `closeSSEStream()` before returning the tool result.
5. Capture the priming event ID.
6. Let the client issue its built-in `Last-Event-ID` replay GET.
7. Inspect event-store contents, server error, caller result, handler count, and durable state.
8. After caller timeout, issue a new exact application retry.
9. Issue a changed request using the same key as a conflict control.

No hosted database, credentials, deployment, or irreversible external mutation is used.

## Exact SDK 1.29 mechanism

At the inspected 1.29.0 release source, the request-scoped server `send()` path:

1. resolves the request's stream ID;
2. reads the current live stream mapping;
3. stores the response in the event store only inside a branch requiring a live controller and encoder;
4. after `closeSSEStream()`, the live stream mapping is gone;
5. the terminal response is therefore not stored;
6. when all request responses are ready, the missing stream causes `No connection established for request ID` to be thrown.

The standalone GET SSE path already used store-first semantics, so this was an asymmetry rather than a deliberate absence of replay support.

## Upstream duplicate and repair analysis

### Issue #2151

The existing issue describes the exact path:

- `closeSSEStream()` removes the active controller;
- the terminal result is not persisted;
- a later `Last-Event-ID` GET cannot replay it;
- `send()` throws because the live stream is missing.

This is a direct duplicate of the dependency behavior observed in the Stensibly fixture.

### PR #2342

The merged v2 fix changes request-scoped serving to:

- store events whenever the request remains in flight and an event store exists, independent of a live controller;
- re-read stream state after the storage await;
- skip only immediate delivery when disconnected;
- return cleanly after storing a terminal response for replay;
- replay and close a retired request stream correctly;
- include dedicated regression tests for disconnected storage and terminal response replay.

The fix is scoped to the legacy sessionful 2025 transport supported inside the v2 packages. It does not imply that protocol revision 2026-07-28 reintroduced session or `Last-Event-ID` semantics.

### Version conclusion

Stensibly's exact lock entry resolves `@modelcontextprotocol/sdk@1.29.0`, which predates the merged v2 store-first repair. No v1.x backport of #2342 was found during this lane. Later v1.x keep-alive work explicitly refers to #2151 as a separate pre-existing replay defect.

## Outcome matrix

| Scenario | Handler executions | Durable items/events | Result outcome |
| --- | ---: | --- | --- |
| Hosted uninterrupted request | 1 | one item / one creation event | result delivered |
| Hosted body abandoned after commit | 1 | one item / one creation event | result ambiguous; receipt reconciles |
| Hosted exact retry after ambiguity | 2 total | still one item / one creation event | original item returned |
| Hosted changed request under same key | +1 handler entry | still one item / one creation event | conflict returned |
| Stateful SDK 1.29 `closeSSEStream()` | 1 | one item / one creation event | terminal MCP result not stored; caller times out |
| Stateful SDK 1.29 replay GET | still 1 | unchanged | priming cursor resumes, but no terminal result exists to replay |
| Current v2 store-first implementation | 1 in upstream regression | application-dependent | stored terminal result replays without handler rerun |

## Findings

### F1. Hosted Stensibly does not currently rely on MCP session replay

**Evidence:** source-observed and test-observed.

The hosted endpoint is intentionally stateless JSON response mode. Its recovery contract is receipt plus idempotency, not session resumption.

### F2. Stensibly protects durable effects after ambiguous result loss

**Evidence:** executed Stensibly tests.

An exact retry can execute the handler again while preserving one durable item and one creation event. Payload drift under the same key is rejected.

### F3. Pinned SDK 1.29 loses request-scoped terminal results after `closeSSEStream()`

**Evidence:** exact release source and Stensibly stateful fixture.

The server stores the priming event, drops the terminal response, emits `No connection established`, and leaves the caller without a replayable result.

### F4. A replay GET cannot recover data that was never persisted

**Evidence:** fixture-observed.

The client reaches the server with the original `Last-Event-ID`, proving the reconnect path is active. The event store still contains only the priming event for that stream.

### F5. Result loss does not imply duplicate application state

**Evidence:** fixture-observed.

The first call commits once. The exact retry enters the handler again but returns the existing item. Durable effect count remains one.

### F6. The SDK defect is already known and repaired on v2 main

**Evidence:** upstream issue #2151, merged PR #2342, and current v2 tests described in that PR.

The appropriate owned action is dependency policy and upgrade verification, not a duplicate issue.

## Negative and narrowed results

1. No duplicate durable execution was observed.
2. No duplicate result delivery was observed on Stensibly's pinned 1.29 path; the result was lost instead.
3. The production hosted endpoint is not using the affected stateful transport mode.
4. The test does not prove that every newer package release contains the v2 fix under the old `@modelcontextprotocol/sdk` package name.
5. The test does not justify enabling stateful transport merely because the current v2 source is fixed; Stensibly must migrate and re-run its own fixture first.
6. No new upstream SDK report is needed because #2151 is exact.
7. No production data or credential path was exercised.

## Recommended owned follow-up

### Dependency gate

Before enabling stateful SSE replay:

1. choose the supported v2 package migration path;
2. pin an exact release containing the #2342 behavior;
3. port this fixture to the migrated package imports;
4. invert the replay-loss expectations so the terminal result must be stored and delivered;
5. assert handler count remains one during transport replay;
6. retain the exact application-retry control and conflict control;
7. run the full Stensibly typecheck, Bun tests, Convex tests, Worker bundle, and runtime parity suite.

### Product contract

Keep receipts and idempotency even after transport replay is available. Transport replay repairs result delivery; it does not replace application-level protection against a client issuing a new request after uncertainty.

## Decision

- Lane result: `confirmed dependency exposure with existing upstream fix`
- Hosted Stensibly exposure: no, under current stateless endpoint
- Stateful 1.29 replay result: lost terminal response
- Exact retry durable effect: deduplicated
- New upstream packet: no; duplicate #2151
- Owned action: dependency upgrade/backport gate before stateful enablement
- Campaign: synthesize and retain Lane #66/#67 client findings separately
- Upstream contact: none

## Verification

Stensibly branch fixture:

```sh
bun install
bun run typecheck
bun test test/mcp-ambiguous-retry-idempotency.test.ts test/mcp-stateful-session-replay.test.ts
bun test
```

Final CI status is recorded in the lane handoff and PR after the latest characterization commit completes.

## Handoff

State: provisional pending final characterization CI

Durable artifacts:

- this report;
- Stensibly PR #565;
- `test/mcp-ambiguous-retry-idempotency.test.ts`;
- `test/mcp-stateful-session-replay.test.ts`;
- SDK issue #2151 and merged fix PR #2342 evidence.

Decision needed after CI:

- mark the lane ready for synthesis if the characterization and recovery controls pass;
- preserve the v2 migration gate;
- avoid duplicate upstream contact.
