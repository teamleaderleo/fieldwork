# Stensibly MCP result replay, loss, and duplicate-execution boundaries

Date: 2026-07-30

Fieldwork lane: #68  
Campaign: #65  
Programme: #13  
Primary target hub: #7  
Parent scout: #20  
Owned testbed: `teamleaderleo/stensibly`  
Worker: ChatGPT GPT-5.6 Thinking under Stensibly callsign `Kestrel`  
Upstream contact authorized: `false`

## In simple words

This lane separates four outcomes after an MCP response stream breaks:

1. **lost result** — work committed, result never reaches the caller;
2. **duplicate delivery** — the same stored result arrives more than once;
3. **duplicate handler execution** — a new application request runs the tool again;
4. **duplicate durable effect** — durable state is created or changed twice.

Stensibly's hosted MCP endpoint is stateless JSON-response mode. It does not use MCP sessions, an event store, or `Last-Event-ID` replay. Its current recovery controls are durable operation receipts and exact idempotency fingerprints.

A test-only stateful fixture exposed a dependency-version boundary:

- Stensibly resolves `@modelcontextprotocol/sdk@1.29.0`.
- On 1.29.0, `closeSSEStream()` after the real mutation commits stores only the priming event. The terminal result is lost, the replay GET has nothing to return, and the original call times out.
- A new exact retry enters the handler again but returns the same item and leaves one item plus one `item.created` event.
- Exact `@modelcontextprotocol/sdk@1.30.0` stores the terminal result. With the same Stensibly store, one replay GET returns the original result with one handler execution. A later exact new request raises the handler total to two while durable effect count stays one.

The 1.29 defect is already tracked by [the request-scoped SSE terminal replay issue](https://redirect.github.com/modelcontextprotocol/typescript-sdk/issues/2151). [The v2 store-first repair](https://redirect.github.com/modelcontextprotocol/typescript-sdk/pull/2342) and [the v1.x disconnected-response backport](https://redirect.github.com/modelcontextprotocol/typescript-sdk/pull/2547) already own the SDK changes. No duplicate upstream issue is needed.

## Verdict

**Confirmed dependency exposure with a verified fixed upgrade.**

| Boundary | Result |
| --- | --- |
| Hosted Stensibly today | Not using stateful MCP replay |
| SDK 1.29 stateful test | Terminal result lost; caller times out |
| SDK 1.29 exact application retry | Handler runs again; durable effect remains one |
| SDK 1.30 stateful test | Result stored and replayed; handler remains at one |
| SDK 1.30 later exact retry | Handler total becomes two; durable effect remains one |
| Duplicate result delivery | Not demonstrated |
| Duplicate durable execution | Not demonstrated |

Operational decision:

> Do not enable stateful request-scoped SSE replay while pinned to SDK 1.29.0. Upgrade to at least verified 1.30.0 or migrate to an appropriate v2 release, retain the replay fixture, and keep receipts/idempotency as a separate application guarantee.

## Pins and artifacts

- Stensibly main reviewed: `teamleaderleo/stensibly@20241e668fb493b7f389df8b9df7f229bcadff68`
- Stensibly branch: `keel/mcp-ambiguous-retry-idempotency`
- Final probe head: `teamleaderleo/stensibly@6d3023eb6b9575806ef56117e729006a6c307694`
- Stensibly PR: #565
- Affected package: `@modelcontextprotocol/sdk@1.29.0`
- Verified fixed package: `@modelcontextprotocol/sdk@1.30.0`
- SDK 1.29 source commit: `e12cbd7078db388152f6e839abdbe09ba01f3f32`
- SDK 1.30 release merge: `2d889f2b329e46680ec9bdd565de4616c497825a`
- Stensibly full CI run: `30482498842`
- SDK 1.30 upgrade probe run: `30483192362`
- Fieldwork PR: #104
- Retrieval date: 2026-07-30

The public SDK repository remained read-only. No issue, pull request, comment, reaction, branch, or message was created upstream.

## Hosted Stensibly boundary

`src/mcp-http.ts` configures the production-facing endpoint with:

- `sessionIdGenerator: undefined`;
- `enableJsonResponse: true`;
- POST handling only;
- a fresh server/transport per request;
- no event store.

An abandoned response can create an ambiguous result, but current hosted recovery comes from application evidence:

- `get_operation_receipt` identifies the committed event and item;
- an exact idempotent retry returns the original item;
- a changed request under the same key conflicts.

The stateful replay defect is not active in the hosted endpoint today.

## Real Stensibly fixtures

### Hosted ambiguity fixture

`test/mcp-ambiguous-retry-idempotency.test.ts`:

1. sends `create_item` through the real hosted MCP handler;
2. lets the mutation commit;
3. abandons the successful response body;
4. recreates the app;
5. reconciles through `get_operation_receipt`;
6. retries the exact mutation;
7. tries a changed mutation under the same key.

Observed:

- first handler execution commits one item/event;
- exact retry enters the handler again and returns the original item;
- changed request enters and returns a conflict;
- durable count remains one item and one creation event.

### Stateful 1.29 characterization

`test/mcp-stateful-session-replay.test.ts` uses public SDK classes plus Stensibly's real SQLite store:

1. creates a sessionful server with an event store;
2. commits a real `createItem` mutation;
3. calls `closeSSEStream()` before returning the tool result;
4. captures the priming token;
5. observes the client GET with `Last-Event-ID`;
6. inspects stored request events and server errors;
7. waits for caller timeout;
8. submits an exact new retry and conflict control.

Observed on 1.29.0:

- handler count at loss: one;
- durable item/event count: one/one;
- request-stream event store: priming event only;
- server error: `No connection established for request ID`;
- replay GET: issued with the priming cursor;
- original caller: times out;
- exact retry: second handler entry, same item, still one durable effect;
- changed retry: conflict, still one durable effect.

### Exact 1.30 upgrade probe

`probes/mcp-stateful-replay-v130/` installs exactly `@modelcontextprotocol/sdk@1.30.0` and reuses Stensibly's real store.

Run `30483192362` recorded:

- transport replay handler calls: `1`;
- request-stream event count: `2`;
- replay GET cursor: `event-3`;
- observed tokens: `event-3`, then result token `event-4`;
- result item equals the committed item;
- durable item count: `1`;
- durable creation-event count: `1`;
- explicit exact retry total handler calls: `2`;
- exact retry returns the same item;
- durable counts remain one/one.

## Source mechanism

### SDK 1.29

The request-scoped `send()` path stores the event only while a live stream controller exists. `closeSSEStream()` removes that registration, so the terminal response skips persistence and later triggers `No connection established`.

The standalone SSE path already stores before checking the live stream. The defect is an asymmetry in request-scoped response handling.

### SDK 1.30

The v1.x backport makes the event store the source of truth:

- persist the response even when the stream is disconnected;
- re-read stream registration after storage;
- avoid double delivery when replay races a write;
- release request correlations once the result is replayable;
- throw only when the response cannot be made replayable.

Release 1.30.0 contains that merge, and the exact package probe confirms it in execution.

### Current v2

The v2 repair implements corresponding store-first behavior in the split server package with disconnected-store and replay regression tests.

Protocol revision 2026-07-28 still has no protocol sessions or `Last-Event-ID` resumption. These repairs concern the supported 2025-era compatibility transport.

## Findings

### F1. Lost result, handler rerun, and duplicate durable effect are distinct

A result can be lost after one commit. A later new request can run the handler again. Exact idempotency can still keep durable effect count at one.

### F2. SDK 1.29 cannot fulfill request-scoped replay after `closeSSEStream()`

The client reconnects correctly. The missing component is server persistence of the terminal result.

### F3. SDK 1.30 repairs replay without re-execution

The terminal result is stored and delivered by replay. The tool handler remains at one during transport recovery.

### F4. Transport replay does not replace application idempotency

A client may still issue a new request after uncertainty. That request enters the handler. Stensibly's fingerprint prevents a second durable effect.

### F5. Current production exposure is limited

The hosted endpoint is stateless, so the 1.29 replay bug is a future-enable/dependency risk rather than a current hosted-session incident.

### F6. No new upstream report is warranted

The exact issue and fixed releases already exist on v1.x and v2 lines.

## Negative results

- No duplicate durable item or creation event occurred.
- No duplicate transport result delivery occurred.
- No production database, credential, deployment, or irreversible external mutation was used.
- No evidence supports removing receipts/idempotency after transport replay is repaired.
- No evidence says protocol-native 2026 sessions exist; they do not.

## Verification

Stensibly CI run `30482498842` passed:

- typecheck;
- 953 Bun tests across 193 files, zero failures, 5,408 assertions;
- 111 Convex tests across 36 files;
- Cloudflare Worker bundle;
- runtime parity.

SDK 1.30 probe run `30483192362` passed after installing the exact published package and executing the real Stensibly store replay fixture.

```sh
bun install
bun run typecheck
bun test test/mcp-ambiguous-retry-idempotency.test.ts test/mcp-stateful-session-replay.test.ts
bun test

cd probes/mcp-stateful-replay-v130
bun install
bun run probe
```

## Owned recommendation

1. Upgrade Stensibly from SDK 1.29.0 to at least verified 1.30.0 before stateful replay enablement.
2. Treat v2 migration as separate dependency work, not the minimum repair for this bug.
3. After upgrade, invert the 1.29 characterization into a replay-success regression.
4. Retain hosted ambiguity, receipt, exact retry, and conflict controls.
5. Keep sessionful transport disabled until the upgraded fixture is part of the standard suite.

## Decision

- Lane result: `confirmed dependency exposure with verified fixed release`
- Hosted current exposure: no
- Stateful 1.29 outcome: lost result
- Stateful 1.30 outcome: replayed result, one handler execution
- Exact new retry: second handler execution, one durable effect
- Upstream packet: none; exact duplicate already fixed
- Campaign: ready for synthesis
- Upstream contact: none

## Handoff

State: `ready-for-synthesis`

Durable artifacts:

- this report;
- Fieldwork PR #104;
- Stensibly PR #565;
- 1.29 characterization test;
- exact 1.30 upgrade probe and workflow;
- CI runs `30482498842` and `30483192362`.

Decision needed:

- approve dependency upgrade work separately;
- preserve Lane #66 and #67 as separate client-side findings;
- synthesize Campaign #65 without filing a duplicate upstream issue.
