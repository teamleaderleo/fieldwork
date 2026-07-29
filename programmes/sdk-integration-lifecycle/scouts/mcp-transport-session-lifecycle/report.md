# Scout: MCP transport and session lifecycle

- Fieldwork issue: #20
- Programme: #13 — `sdk-integration-lifecycle`
- Target hub: #7 — `mcp-typescript-sdk`
- Fieldwork revision: `09fe47ac92ec9c0c333b4979011f6321795deff2`
- Target revision: `cc4b41617ce3601b1290d67216ea0b194a3cd9ac`
- Retrieved: 2026-07-29
- Claim scope requested: `interface`
- Claim scope supported: `interface`, with mechanism-level synthetic probe evidence
- Upstream contact: unauthorized and unused

## In simple words

The SDK splits an MCP connection across two owners. The shared protocol class owns logical work: request IDs, pending promises, progress callbacks, cancellation signals, capability checks, response decoding, and settlement when a connection closes. Each transport owns delivery: child processes or HTTP requests, session headers, SSE streams, replay tokens, reconnect timers, and the moment a connection is declared closed.

That split is mostly explicit and carefully cleaned up. A transport close rejects old pending requests and aborts handlers; reconnecting a session allows future traffic to continue, while old request promises stay settled. The strongest campaign lead sits in Streamable HTTP reconnect control: the transport supports several concurrent SSE streams, yet retry delay and pending reconnect cancellation are held in transport-wide fields, and a successful reopen starts the retry count from zero again. A deterministic synthetic probe shows the resulting cross-stream coupling and unbounded reopen/drop loop in the transcribed state machine. An SDK-native regression test remains the next evidence gate.

## Asked

Which protocol and SDK boundaries own transport, session, capability negotiation, requests, progress, cancellation, errors, reconnect behaviour, and teardown, and which concrete behaviours deserve deeper campaigns?

## Evidence labels

- **documented** — stated by target documentation or public comments.
- **source-observed** — read directly in source at the pinned target revision.
- **test-observed** — covered by a named target test at the pinned revision.
- **probe-observed** — emitted by the retained synthetic probe in this scout.
- **inferred** — consequence derived from source or probe evidence; requires a stronger experiment before promotion as a defect.
- **unknown** — evidence remains insufficient.

## Revisions and protocol eras

**source-observed:** `packages/core/src/constants.ts` keeps `LATEST_PROTOCOL_VERSION` at `2025-11-25`, with legacy supported revisions from `2024-10-07` through `2025-11-25`.

**documented/source-observed:** the same SDK revision also implements an opt-in `2026-07-28` modern era through the wire-era registries and version-negotiation path:

| Axis | Legacy era | Modern era |
| --- | --- | --- |
| Protocol revisions | `2024-10-07` through `2025-11-25` | `2026-07-28` |
| Opening exchange | `initialize`, then `notifications/initialized` | `server/discover` |
| Capability lifetime | stored from initialization | carried in each request `_meta` envelope |
| Server-to-client input | JSON-RPC requests | `input_required` result and fresh retry request |
| Change delivery | unsolicited notifications | `subscriptions/listen` stream |
| Streamable HTTP cancellation | `notifications/cancelled` POST | close the request SSE stream |
| Default client posture | legacy | opt-in with `versionNegotiation` |

The report therefore pins both the SDK source revision and the two wire families it serves. The modern revision is implemented in the target source even though the exported legacy constant named `LATEST_PROTOCOL_VERSION` remains `2025-11-25`.

## Boundary map

| Concern | Primary owner | Key paths | Lifecycle summary |
| --- | --- | --- | --- |
| Transport contract | core protocol/transport seam | `packages/core-internal/src/shared/transport.ts` | `start`, `send`, `close`, callbacks, optional session/version and per-request-stream features |
| Request identity and correlation | shared protocol | `packages/core-internal/src/shared/protocol.ts` | monotonic numeric IDs, pending response map, result/error correlation |
| Capabilities | Client/Server plus era codec | `packages/client/src/client/client.ts`, `packages/server/src/server/server.ts` | local registration before connect; remote declarations stored per connection in legacy and read per request in modern |
| Progress | shared protocol | `packages/core-internal/src/shared/protocol.ts` | progress token equals request ID; optional timeout reset; unknown token reports out of band |
| Cancellation | shared protocol plus transport feature | `protocol.ts`, `client/streamableHttp.ts` | local abort settles caller; inbound cancellation aborts handler signal; modern HTTP closes per-request stream |
| Errors | wire codec, protocol, transport | `protocol.ts`, `errors/`, HTTP transport | tool result errors, JSON-RPC `ProtocolError`, local `SdkError`, HTTP `SdkHttpError`, out-of-band `onerror` |
| Connection teardown | shared protocol and each transport | `protocol.ts`, HTTP/stdio transports | transport emits `onclose`; protocol rejects pending requests, clears timers/progress, aborts handlers |
| HTTP session | Streamable HTTP transport | `client/streamableHttp.ts`, `server/streamableHttp.ts` | server issues session ID at initialize; client carries header; DELETE may terminate |
| SSE resumption | Streamable HTTP transport plus application event store | HTTP client/server transports | Last-Event-ID, event replay, retry delay, reconnect scheduler |
| stdio child lifecycle | stdio transport | `packages/client/src/client/stdio.ts` | spawn, newline JSON, pipe parsing, process close, escalating termination |
| Reconnect policy | host plus HTTP transport | Client connect and HTTP transport | preserved session/version skips fresh negotiation; old request promises remain settled |

## Capabilities

### Legacy era

**source-observed:** the client receives server capabilities in `InitializeResult` and stores them in `_serverCapabilities`. The server stores client capabilities from `initialize`. Capability registration is frozen once a protocol object has a transport.

**source-observed:** strict outbound capability enforcement is configurable through `enforceStrictCapabilities`; local handler registration continues to validate declared local capabilities. This creates two distinct checks:

1. local code may only register or emit surfaces its own declaration supports;
2. remote declaration enforcement can remain permissive for compatibility unless strict mode is enabled.

### Modern era

**source-observed:** the client automatically attaches protocol version, client identity, and client capabilities to every outgoing request and notification. The serving entry validates and lifts those reserved fields before handler dispatch. Server behaviour therefore reads the current request's declaration and cannot safely infer capability continuity from a previous request.

**campaign consequence:** a reconnecting host must preserve the negotiated era, while modern capability truth still arrives on each new request. Session continuity and capability continuity are related yet separate.

## Requests and responses

**source-observed:** `Protocol.request()` owns the logical request funnel:

1. resolve the wire-era codec;
2. reject a spec method absent from that era;
3. assign a numeric JSON-RPC ID;
4. add a progress token when requested;
5. attach the modern envelope when applicable;
6. register response, progress, abort, and timeout state;
7. call `transport.send()`;
8. decode the result through the era codec;
9. validate the neutral result schema;
10. remove per-request state on every exit path.

**source-observed:** inbound requests capture the current transport before invoking the handler. Their eventual response goes back through that captured transport, avoiding accidental delivery onto a replacement connection. Each handler receives an `AbortSignal`, session ID when supplied by the transport, related request/notification send functions, and HTTP request details when available.

**source-observed:** responses with unknown IDs and progress notifications with unknown tokens are surfaced through `onerror`. They never revive cleaned-up request state.

## Progress

**source-observed:** requesting progress registers a callback keyed by the same numeric request ID placed in `_meta.progressToken`. The callback receives the progress payload minus the token.

**source-observed:** `resetTimeoutOnProgress` restarts the per-leg timeout. `maxTotalTimeout` still caps the whole flow. A progress event received after request cleanup becomes an unknown-token error.

**unknown:** the desired host-facing policy for expected late progress after cancellation remains unstated. The current out-of-band error is diagnostically useful, though high-churn transports may treat a normal race as an alarming error.

## Cancellation

### Outbound caller cancellation

**source-observed:** caller abort and request timeout share the `cancel()` path. It removes the progress callback and settles the caller with an `SdkError`.

- Legacy HTTP, stdio, and shared-channel transports send `notifications/cancelled` with the request ID.
- Modern Streamable HTTP sets `hasPerRequestStream = true`; the protocol aborts that request's HTTP/SSE stream instead of sending a cancellation notification.

### Inbound cancellation

**source-observed:** `notifications/cancelled` looks up the inbound handler's `AbortController` and aborts its signal. A handler completion that arrives after the abort is suppressed before encoding or transport send.

### Late messages

**probe-observed:** the synthetic model delivered progress, cancelled the handler, removed the pending request, then delivered a response. The handler signal was aborted and the late response surfaced as `unknown response id 0`.

**inferred:** late response/progress policy deserves one focused campaign only if real transport timing produces noisy or misleading diagnostics. The base lifecycle itself settles deterministically.

## Errors

The SDK exposes several intentionally separate error surfaces:

| Surface | Owner | Example |
| --- | --- | --- |
| Tool/application result | tool handler | `isError` inside a successful `tools/call` result |
| JSON-RPC protocol failure | remote protocol | `ProtocolError` created from JSON-RPC error response |
| SDK lifecycle/validation | local SDK | `SdkError` for timeout, connection close, unsupported capability or era |
| HTTP transport | HTTP client transport | `SdkHttpError` with status and response details |
| Out-of-band diagnostics | protocol or transport callback | parse errors, unknown IDs/tokens, stream disconnects |

**source-observed:** modern Streamable HTTP converts a valid matching HTTP 400 JSON-RPC error body into an in-band `ProtocolError`. Legacy exchanges keep the earlier generic HTTP error behaviour.

**source-observed:** handler result encoding failures send JSON-RPC Internal Error so a successful handler cannot strand the requester until timeout. Handler-thrown numeric protocol codes are mapped through the era codec; other throws become Internal Error.

## Teardown

### Shared protocol

**source-observed:** transport `onclose` invokes `Protocol._onclose()`, which:

- swaps out the pending response map before callbacks run;
- clears progress callbacks and debounced notifications;
- clears every request timeout;
- swaps out all inbound handler abort controllers;
- clears the transport reference;
- calls the user `onclose` callback;
- rejects every pending outbound request with `SdkError(ConnectionClosed)`;
- aborts every in-flight inbound handler with the same error.

The Client override also settles every active `subscriptions/listen` state machine as a remote close before delegating to the shared teardown.

### Explicit client close

**source-observed:** `Client.close()` delegates to the transport and then clears per-connection client state even when transport close rejects: negotiated version, server capabilities and identity, instructions, discover result, subscriptions, debounce timers, and derived cache indexes.

### Streamable HTTP transport

**source-observed:** close cancels the currently recorded reconnect callback, aborts the transport-wide controller, and invokes `onclose`. Session termination is a separate `DELETE` operation; a successful response or allowed `405` clears the client session ID.

### stdio transport

**source-observed:** normal close ends stdin, waits, sends `SIGTERM`, waits again, and escalates to `SIGKILL`; the read buffer is cleared. Process exit invokes `onclose`, which reaches shared protocol teardown. The disposable era-probe sibling has a tighter private disposal path based on process exit so inherited pipe handles cannot stall cleanup.

## Session lifecycle and reconnects

### HTTP session establishment

**source-observed/test-observed:** a new legacy HTTP session starts without a session header. The client adopts `mcp-session-id` only from a successful initialization response. Session IDs on failed initialization or ordinary responses are ignored. Subsequent requests carry the stored session ID and negotiated protocol version.

### Session termination

**source-observed/test-observed:** `terminateSession()` sends HTTP DELETE with the session ID. `405` means the server declines explicit termination and is accepted by the client. Other failed statuses become typed HTTP errors.

### Replacing a transport

**source-observed:** a transport constructed with an existing `sessionId` is treated as a session-resuming reconnect. `Client.connect()` starts it, restores the previous negotiated protocol version onto the transport, and skips both `initialize` and `server/discover`.

**source-observed:** transport-initiated close runs protocol teardown but leaves the client's negotiated era available for a session resume. Explicit `Client.close()` clears it.

**probe-observed:** the synthetic session probe preserved `session-2`, closed the old connection, and confirmed the pending request ID `0` stayed settled. Session continuity permits future traffic; it does not revive an old promise.

### SSE replay

**source-observed:** an SSE event ID becomes the resumption token. A reconnecting GET sends `Last-Event-ID`; the server's application-supplied `EventStore` maps events back to streams and replays them. The event store is therefore a transport/application boundary carrying durability and deduplication responsibility.

## Transport-specific boundaries

### Streamable HTTP

Transport-owned:

- HTTP request construction and authentication;
- session and protocol headers;
- response media type handling;
- one POST/SSE stream per outbound request;
- Last-Event-ID replay;
- reconnect delay and scheduler;
- stream-level cancellation through `requestSignal`;
- optional session DELETE.

Protocol-owned:

- logical request ID and promise;
- progress and timeout state;
- conversion of matching response messages into result/error settlement;
- connection-close settlement.

Application-owned:

- event store implementation and retention;
- persistence of session ID, negotiated version, discovery verdict, and resumption token across process restarts;
- idempotency policy for operations whose result was lost;
- deciding whether a fresh request may safely repeat a side effect.

### stdio

Transport-owned:

- process spawn, environment, pipes, framing buffer, write backpressure, and process termination.

Protocol-owned:

- all JSON-RPC lifecycle state, cancellation notification, progress, and close settlement.

Application-owned:

- process restart policy and recovery of logical operations. There is no transport session ID, SSE replay, or automatic request continuation.

### Legacy SSE

This remains a compatibility transport with weaker typed HTTP error reporting and its own connection model. It belongs in cross-transport tests where the question concerns behaviour promised by the shared protocol surface, not Streamable HTTP-only replay.

### Custom transports

A custom transport must preserve the contract that callbacks are installed before `start()`, call `onclose` for local and remote shutdown, avoid sharing a transport instance between protocol objects, and set `hasPerRequestStream` only when `requestSignal` truly cancels one request without closing the whole channel.

## Test map

Located coverage at the pinned target revision:

| Test area | Representative path | Covered |
| --- | --- | --- |
| HTTP client transport | `packages/client/test/client/streamableHttp.test.ts` | session adoption, reconnect headers, DELETE, concurrent SSE delivery, priming events, one-stream reconnect, backoff, server retry field |
| Subscription lifecycle | `packages/client/test/client/listen.test.ts` | opening/open/closed state, stream end, local and remote settlement |
| Protocol eras | `packages/core-internal/test/shared/protocolEras.test.ts` | legacy/modern method and wire-era behaviour |
| Lifecycle E2E | `test/e2e/scenarios/lifecycle.test.ts` | initialization and close paths |
| HTTP E2E | `test/e2e/scenarios/transport-http.test.ts` | transport-level request flow |
| Server protocol | `packages/server/test/server/server.test.ts` | server capability and protocol behaviour |

**test-observed:** concurrent SSE streams are tested for independent message delivery.

**test gap observed during scout:** no located case combines concurrent streams with distinct SSE `retry` values, simultaneous scheduled reconnects, or repeated successful reopen-then-drop cycles against one finite `maxRetries` budget.

## Synthetic probe

Artifacts:

- `probe.mjs`
- `probe-output.json`

Environment:

- Node.js `v22.16.0`
- zero dependencies
- target source was read-only
- no external network or live MCP system

Invocation:

```sh
node programmes/sdk-integration-lifecycle/scouts/mcp-transport-session-lifecycle/probe.mjs
```

The probe is a small executable transcription of the relevant maps and fields. It preserves request cleanup, late-message handling, session-versus-request continuity, shared reconnect delay, one reconnect-cancel slot, and retry-attempt reset. It omits Fetch, ReadableStream parsing, authentication, event-store implementation, and target package code execution.

Observed output summary:

| Scenario | Result |
| --- | --- |
| cancellation plus late response | handler signal aborted; late response reported as unknown ID |
| session reconnect boundary | session ID preserved; old pending request never revived |
| shared retry delay | stream A's delay changed from `50` to `5000` after stream B supplied its retry value |
| single reconnect cancel handle | only the most recently scheduled reconnect record was cancelled |
| retry budget reset | five reopen/drop cycles each scheduled attempt `0`; terminal budget was never reached |

## Strongest supported finding

**source-observed:** `StreamableHTTPClientTransport` supports multiple concurrent SSE streams, while `_serverRetryMs` and `_cancelReconnection` are transport-wide fields. Every SSE parser can overwrite `_serverRetryMs`. Every schedule overwrites `_cancelReconnection`. When a stream successfully reopens and later ends again, `_handleSseStream()` calls `_scheduleReconnection(..., 0)`.

**probe-observed:** the transcribed state machine deterministically produces:

1. cross-stream retry-delay coupling;
2. an older scheduled timer outside the single recorded cancel handle;
3. repeated successful reopen/drop cycles that never consume a lifetime retry budget.

**inferred consequence:** one active stream can influence another stream's reconnect timing. Closing the transport aborts all fetches and prevents timer callbacks from reopening streams, though older scheduled callbacks may remain pending until their due time. `maxRetries` bounds consecutive failed reconnect opens; it does not bound a stream that repeatedly opens successfully and then drops before receiving a response.

**evidence boundary:** this scout has source evidence and a deterministic synthetic model. A campaign must add SDK-native regression tests using real `ReadableStream` and scheduler hooks before describing any row as a confirmed target defect.

## Failed hypotheses and negative results

- **Base close leaks pending protocol state — unsupported.** Shared teardown explicitly clears response, progress, timeout, debounce, and inbound abort state.
- **Session reconnect revives pending requests — unsupported.** Connection close settles old promises; session resume only affects subsequent traffic.
- **HTTP session ID can be poisoned by any response — unsupported.** The client adopts it only from a successful initialize response.
- **Modern cancellation still sends a cancellation POST — unsupported for per-request Streamable HTTP.** It aborts the request stream as required by the modern transport rule.
- **Concurrent SSE streams lack basic delivery coverage — unsupported.** The target test suite covers two simultaneous streams delivering independent responses.

## Alternative architectures

1. **Per-stream reconnect record** — hold retry value, attempt counter, timer cancel function, resumption token, request abort signal, and terminal callback in one stream-local object.
2. **Reconnect registry** — keep a transport-level map keyed by stream/request identity; `close()` cancels every scheduled entry, while each stream owns its retry value and count.
3. **Scheduler-only cancellation** — retain the current stream-local closure model but store every scheduler cancellation function in a set. This fixes teardown bookkeeping while leaving retry-delay coupling and lifetime budget semantics unresolved.
4. **Host-owned reconnection** — expose stream-end state and let the host rebuild transports. This reduces SDK policy but loses existing replay convenience and would be a significant public design change.

## Ranked campaign candidates

### 1. Streamable HTTP per-stream reconnect state isolation

- **Question:** Can concurrent SSE streams alter each other's retry delay or leave reconnect timers outside transport teardown bookkeeping?
- **Evidence now:** source-observed plus probe-observed.
- **Next experiment:** real transport test with two request streams, distinct `retry` fields, a custom scheduler capturing both callbacks, and transport close before either callback fires.
- **Acceptance signal:** each stream uses its own retry delay; close cancels every pending schedule; one stream's reconnect state cannot alter another's.
- **Why first:** narrow boundary, deterministic source mechanism, existing scheduler seam, direct lifecycle consequence.

### 2. Reconnect budget across successful reopen/drop cycles

- **Question:** What does `maxRetries` promise when each reconnect GET succeeds but its stream ends before a response?
- **Evidence now:** source-observed plus probe-observed.
- **Next experiment:** return a sequence of successful resumable GET streams that immediately close; assert a documented finite terminal outcome or revise the option description to define consecutive-open failures only.
- **Acceptance signal:** code and documentation agree on one bounded policy, with a test covering repeated reopen/drop cycles.
- **Why second:** potential infinite polling/resource use, though intended semantics need confirmation before implementation.

### 3. Session resume contract in Stensibly

- **Question:** When an MCP transport reconnects with a preserved session and protocol version, which Stensibly operation state survives, and how does the host avoid repeating a side effect whose response was lost?
- **Evidence now:** interface/source map plus synthetic session boundary.
- **Owned trial:** instrument one long-running Stensibly MCP operation, interrupt after server acceptance and before client result, reconnect with preserved session/version/resumption token, then record whether the operation result can be recovered without a second logical execution.
- **Acceptance signal:** an explicit host policy for operation identity, resumption, idempotency, and user-visible recovery.
- **Why third:** highest integration value, yet it requires a real owned trial. Add `testbed:stensibly` only when that branch begins.

### 4. Cancellation and late-message diagnostic policy

- **Question:** Should expected late progress/response after cancellation or timeout emit generic `onerror`, a typed race diagnostic, or silent drop?
- **Evidence now:** source-observed plus synthetic race.
- **Next experiment:** deterministic in-memory and HTTP tests injecting response/progress immediately before and after abort and close.
- **Acceptance signal:** one documented cross-transport policy with stable observable events.
- **Why fourth:** useful operational clarity; current cleanup remains correct, so impact must be demonstrated.

### 5. Custom transport lifecycle conformance probe

- **Question:** Can a compact conformance suite catch transports that omit `onclose`, misuse `hasPerRequestStream`, lose messages during `start`, or close the full channel for request-scoped abort?
- **Evidence now:** interface map.
- **Next experiment:** synthetic good/bad transports executed against `Protocol` and Client lifecycle invariants.
- **Acceptance signal:** reusable tests or examples that clearly separate protocol requirements from optional transport features.
- **Why fifth:** broad ecosystem value, with a larger acceptance and maintenance surface.

## Recommended branch plan

Open one bounded campaign combining candidates 1 and 2 only if the first real-transport test reproduces either cross-stream coupling or the lifetime retry-budget behaviour. Keep candidate 3 as a separate owned-integration campaign because host idempotency and operation recovery differ from transport timer correctness.

Do not prepare an upstream patch from this scout alone. The target contribution policy requests prior discussion for significant multi-module changes, and upstream contact remains unauthorized.

## Remaining uncertainty

- Whether transport-global retry delay is intentional policy for all SSE streams or accidental coupling.
- Whether `maxRetries` means consecutive failed opens or total reconnect cycles across one logical stream lifetime.
- Whether stale scheduled callbacks create measurable resource pressure in real runtimes before the transport abort guard makes them no-op.
- How server EventStore implementations handle replay identity, retention, and duplicate suppression under process or node replacement.
- Whether Stensibly currently persists enough operation identity to distinguish reconnect recovery from a fresh side-effecting request.
- How legacy SSE behaves under the same late-message and reconnect races.

## Decision gate

**Outcome: continue research.**

The scout supports an interface-level lifecycle map and two narrow mechanism hypotheses. Campaign 1 has the strongest next test. A code change becomes justified only after an SDK-native regression test demonstrates observable cross-stream coupling or teardown leakage. The Stensibly trial can proceed independently as owned integration work.

## Suggested next action

1. Open a Fieldwork campaign for a real Streamable HTTP concurrent-reconnect regression probe covering candidates 1 and 2.
2. Authorize a separate Stensibly trial only when an owned branch and rollback are ready; add `testbed:stensibly` at that point.

## Upstream contact

External contact remains unauthorized. No upstream issue, discussion, pull request, comment, reaction, or message was created.

## Handoff

```text
FIELDWORK HANDOFF
State: ready-for-synthesis
Batch: none
Campaign: none
Assignment: #20 — Scout MCP transport and session lifecycle
Claim scope supported: interface, plus mechanism-level synthetic probe evidence
Integration context: one proposed Stensibly session-resume trial; trial not begun and testbed label not added
Durable artifacts: programmes/sdk-integration-lifecycle/scouts/mcp-transport-session-lifecycle/report.md; probe.mjs; probe-output.json
Finding: Shared Protocol teardown cleanly settles logical work, while Streamable HTTP holds reconnect delay and cancellation bookkeeping at transport scope despite concurrent SSE streams. The retained synthetic model demonstrates cross-stream retry coupling, one recorded reconnect cancel slot, and retry-attempt reset after successful reopen. Real SDK transport tests remain required before defect promotion.
Evidence labels used: documented, source-observed, test-observed, probe-observed, inferred, unknown
Uncertainty: intent of global retry policy; lifetime meaning of maxRetries; real runtime impact; EventStore and Stensibly recovery behaviour
Decision needed: whether to open the real-transport reconnect campaign and separately authorize the Stensibly integration trial
Upstream contact authorized: no
```
