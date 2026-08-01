# Deep dive — Unit 09 UI-stream SSE keep-alive

## In simple words

AI SDK converts typed UI message chunks into SSE bytes, optionally tees those canonical bytes to a persistence consumer, and sends the other branch to the HTTP client. The selected repair adds ignorable SSE comments only after that split. The client receives an immediate body byte and periodic idle bytes while persistence continues to receive the original protocol stream.

The owned candidate has executed package, repository, Node HTTP, controlled proxy, and repeated cancellation evidence. A public pull request now implements the same repair family and broadens parser and documentation coverage. The owned source remains useful because it protects validation ordering and client cancellation when the persistence branch stays active.

## Governing invariant

> Optional liveness bytes may affect only the client transport branch and must preserve canonical UI data, persisted SSE bytes, disabled behavior, bounded reads, and terminal cleanup.

## Current behavior at the historical base

- entrypoint: `createUIMessageStreamResponse()` or `pipeUIMessageStreamToResponse()` and the `streamText` or agent wrappers that delegate to them;
- state owner: the UI-message response helper owns JSON-to-SSE conversion, tee placement, response construction, and cancellation propagation;
- caller-visible result: an HTTP response whose first body byte arrives only when the source produces data or completes;
- side effects: optional `consumeSseStream` receives a tee branch for persistence or resumable consumption;
- cleanup owner: stream readers, response cancellation, and the optional independent consumer;
- persistence boundary: canonical SSE is teed before any client-only liveness wrapper;
- relevant ordering: interval validation must occur before source locking, teeing, or callback invocation; client cancellation must retire client timers without waiting for an independent tee consumer.

## Source map

| Area | Exact path and symbol | Responsibility | Relevant tests |
| --- | --- | --- | --- |
| client liveness pump | [`createSseKeepAliveStream`](https://github.com/teamleaderleo/ai/blob/b4b572631f6f288f296d1dcbb6d69e5e848cd9fb/packages/ai/src/ui-message-stream/create-sse-keep-alive-stream.ts) | opening comment, idle timer, one source read, demand check, close/error/cancel cleanup | [`create-ui-message-stream-response-keep-alive.test.ts`](https://github.com/teamleaderleo/ai/blob/b4b572631f6f288f296d1dcbb6d69e5e848cd9fb/packages/ai/src/ui-message-stream/create-ui-message-stream-response-keep-alive.test.ts) |
| Fetch response | [`createUIMessageStreamResponse`](https://github.com/teamleaderleo/ai/blob/b4b572631f6f288f296d1dcbb6d69e5e848cd9fb/packages/ai/src/ui-message-stream/create-ui-message-stream-response.ts) | validate, transform, tee, persistence callback, client wrapper | same test |
| Node response | [`pipeUIMessageStreamToResponse`](https://github.com/teamleaderleo/ai/blob/b4b572631f6f288f296d1dcbb6d69e5e848cd9fb/packages/ai/src/ui-message-stream/pipe-ui-message-stream-to-response.ts) | transfer client stream into `ServerResponse` | [`pipe-ui-message-stream-to-response-keep-alive.test.ts`](https://github.com/teamleaderleo/ai/blob/b4b572631f6f288f296d1dcbb6d69e5e848cd9fb/packages/ai/src/ui-message-stream/pipe-ui-message-stream-to-response-keep-alive.test.ts) |
| public option | [`UIMessageStreamResponseInit`](https://github.com/teamleaderleo/ai/blob/b4b572631f6f288f296d1dcbb6d69e5e848cd9fb/packages/ai/src/ui-message-stream/ui-message-stream-response-init.ts) | optional `keepAliveMs` API | helper propagation tests |
| stream-text helpers | [`stream-text-ui-response-keep-alive.test.ts`](https://github.com/teamleaderleo/ai/blob/b4b572631f6f288f296d1dcbb6d69e5e848cd9fb/packages/ai/src/generate-text/stream-text-ui-response-keep-alive.test.ts) | verifies both response entrypoints forward the option | same |
| agent helpers | [`create-agent...test.ts`](https://github.com/teamleaderleo/ai/blob/b4b572631f6f288f296d1dcbb6d69e5e848cd9fb/packages/ai/src/agent/create-agent-ui-stream-response-keep-alive.test.ts), [`pipe-agent...test.ts`](https://github.com/teamleaderleo/ai/blob/b4b572631f6f288f296d1dcbb6d69e5e848cd9fb/packages/ai/src/agent/pipe-agent-ui-stream-to-response-keep-alive.test.ts) | verifies agent wrappers forward the option | same |

## Reproduction or characterization

### Setup

- exact behavior-executed source: `7c8b95b12e7a47e0f614ff949b645e546488eea7`;
- environment: Ubuntu 24.04, Node `v22.23.1`, pnpm `10.33.4`;
- carrier: [`teamleaderleo/ai#6`](https://github.com/teamleaderleo/ai/pull/6);
- workflow: `30506032517`, job `90755875694`;
- fixture: a real Node HTTP server, an idle UI source, and a forwarding proxy with a 450 ms idle cutoff.

### Baseline result

The pinned helper emits no body while an open source remains silent. A server or intermediary that waits for a body byte may withhold the response head; a byte-silence deadline may close the stream.

### Candidate result

- the first client body chunk was the opening SSE comment before UI data;
- the controlled proxy remained open through 1,050 ms of source silence with 75 ms comments;
- canonical `data: [DONE]\n\n` completion remained present;
- exact receipt: `{"candidateHead":"7c8b95b12e7a47e0f614ff949b645e546488eea7","node":"v22.23.1","openingByte":"pass","proxyIdleLiveness":"pass"}`.

## Failure model

1. A healthy UI stream opens and remains silent before its first typed chunk or while waiting for later work.
2. The canonical converter has no bytes to emit.
3. The HTTP implementation or proxy sees no response-body activity.
4. The response head may remain unseen by the client, or a proxy idle deadline may close the connection.
5. Retrying can create reconnect churn even though the underlying operation remains healthy.

Steps 1–4 were reproduced in the controlled Node/proxy boundary. Deployment-specific timeout values and prevalence remain environment-dependent.

## Consequence and claim boundary

### Established

- immediate comments produce a real client body byte before UI data in Node;
- periodic comments preserve the controlled proxy connection past its cutoff;
- comments remain outside the persisted SSE branch in target tests;
- disabled output remains canonical;
- one source read stays pending during idle periods;
- candidate client cancellation clears timers and requests source-branch cancellation without awaiting a sibling tee branch;
- complete owned-fork CI and changeset verification pass at `b4b57263...`.

### Inferred

- the same standards-compatible comments should provide liveness through intermediaries that forward SSE comment bytes and reset their idle deadline on body traffic;
- interval selection should remain below the relevant intermediary cutoff with operational margin.

### Unknown or unmeasured

- every proxy, CDN, runtime adapter, browser, or transport topology;
- one universal interval;
- ecosystem frequency;
- final maintainer API preference;
- public PR acceptance or merge timing.

## Selected implementation

The wrapper owns transport liveness after JSON-to-SSE conversion and after the persistence tee. It emits `: stream-open\n\n` immediately and `: keep-alive\n\n` after silent intervals. Real data resets timer ownership. A single `reader.read()` remains pending. Comments are skipped when downstream demand is absent. Close, source error, and client cancellation retire timer state.

Validation belongs before source locking and tee/callback side effects. Invalid intervals therefore throw while the input remains unlocked and persistence callbacks remain untouched.

Client cancellation clears local state and issues reader cancellation asynchronously. A tee branch's cancellation promise can wait for its sibling branch; the client response must be able to finish cancellation independently of a persistence consumer.

## Compatibility analysis

- public API: one optional `keepAliveMs?: number`; disabled by default;
- source compatibility: additive;
- binary or wire compatibility: disabled output unchanged; enabled client wire gains SSE comments;
- persistence or format compatibility: persistence receives canonical bytes before client wrapping;
- platform behavior: relies on Web Streams and SSE comment semantics already used by the response path;
- performance and allocation: one reader, one timer, one bounded race of one comment plus one real chunk;
- cancellation, retry, and recovery: timer clears on all terminal paths; client cancellation avoids sibling-tee settlement;
- generated output: one patch changeset; no lockfile;
- migration or rollback: remove `keepAliveMs` to recover previous byte behavior.

## Adversarial and edge controls

- repeated 100-cycle open/cancel soak;
- client cancellation while persistence branch remains active;
- source close and canonical completion;
- source error propagation;
- invalid zero, negative, infinite, and NaN intervals before ownership transfer;
- slow downstream demand without comment accumulation;
- one pending source read across several idle intervals;
- real data resetting the idle interval;
- Fetch, Node, streamText, and agent option propagation;
- persistence byte equality.

## Review risks

1. **Comments could enter stored or replayed data.** Placement after the persistence tee and explicit byte comparison protect this boundary.
2. **Long-idle streams could accumulate reads or comments.** One retained read and demand-gated enqueueing bound the work.
3. **Cancellation could hang behind persistence.** The owned candidate avoids awaiting the tee-branch cancellation promise and tests an active independent branch.
4. **Invalid configuration could trigger persistence work before throwing.** The owned candidate validates before tee/callback side effects.
5. **One interval could be marketed as universal.** Documentation should instruct operators to choose a value below their actual intermediary cutoff.

## Public replacement comparison

Public PR [`vercel/ai#17921`](https://github.com/vercel/ai/pull/17921) uses the same API and post-tee SSE-comment design. It adds SDK `parseJsonEventStream` coverage, four reference updates, troubleshooting guidance, and a Node example. Its public head is `21cd681724103701c3596770d7252a7ef0ad18db`.

Two source-review concerns remain at that exact head:

- validation happens inside `createKeepAliveSseStream()` after `createUIMessageStreamResponse()` may already tee and invoke `consumeSseStream`;
- `cancel()` returns `reader.cancel(reason)`, so a client cancellation can await the cancellation promise of a tee branch while the persistence sibling remains active.

The public tests cover direct source cancellation and parser invisibility. They do not cover invalid-option ordering through the response helper or client cancellation with a live `consumeSseStream` branch.

## Reversing evidence

Reopen the disposition if:

- the public pull request closes without an equivalent accepted fix;
- current `main` adopts another design that omits the two retained edge controls;
- source or execution shows the owned cancellation strategy loses a required error or violates a target contract;
- maintainers request a distinct validation or lifecycle patch and upstream contact receives exact authorization.

## Adjacent work excluded

- provider or model health detection;
- application-level operation timeouts;
- reconnect identity and replay policy;
- proxy-specific deployment support matrices;
- changes to the public reporter's production deployment;
- upstream review comments or submissions without authorization.
