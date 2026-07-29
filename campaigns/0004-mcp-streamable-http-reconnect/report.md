# MCP TypeScript v2 Streamable HTTP reconnect campaign

Date: 2026-07-30

Fieldwork campaign: #65
Programme: #13
Target hub: #7
Parent scout: #20
Upstream contact authorized: `false`

## In simple words

This campaign tested whether the v2 TypeScript SDK correctly keeps reconnect state separate when several MCP HTTP response streams overlap, whether its retry ceiling has a real lifecycle hole, and whether lost results cause duplicate application execution.

One client defect candidate survived real execution:

> A reconnecting stream can use another stream's SSE `retry` value.

Two broader concerns were narrowed:

- `maxRetries` counts consecutive failures to open the next stream; successful long-lived reconnects resetting that count are not a separate defect by themselves.
- stateful MCP result replay can deliver the same stored result more than once while executing the tool once; application retry is a separate path that can re-enter the handler and therefore needs durable idempotency.

## Source pins

- MCP TypeScript SDK: `modelcontextprotocol/typescript-sdk@cc4b41617ce3601b1290d67216ea0b194a3cd9ac`
- SDK v2 package line: `@modelcontextprotocol/client@2.0.0`, `@modelcontextprotocol/server@2.0.0`
- Owned SDK fork probe head: `teamleaderleo/typescript-sdk@d9fcf9d085f9c75bfec49d714a7a17ba1c5ad571`
- Stensibly: `teamleaderleo/stensibly@20241e668fb493b7f389df8b9df7f229bcadff68`

## Lane results

### Lane #66 — concurrent reconnect ownership

Result: **confirmed SDK defect candidate**.

Public HTTP reproduction:

1. Stream A receives a priming event with its own `retry` value and event ID.
2. Stream B receives a different `retry` value and event ID.
3. A's reconnect performs a real GET carrying A's `Last-Event-ID`.
4. When that GET fails, A's next scheduled delay uses B's value.

Both directions reproduced:

| A instruction | Later B instruction | A next delay |
| ---: | ---: | ---: |
| 50 ms | 5000 ms | 5000 ms |
| 5000 ms | 50 ms | 50 ms |

The shorter direction can make A reconnect earlier than A's server instructed. The longer direction can delay result recovery.

Supporting cleanup finding:

- two pending reconnects share one recorded cancellation callback;
- close cancels the newest default timer and leaves the older timer pending;
- the older callback later fires but transport abort guards prevent a fetch or error in the tested path.

Verification:

- public and class-level probes;
- Node 20, 22, and 24;
- final client workflow `30476941445`;
- lane report in PR #82.

Held upstream packet:

`StreamableHTTPClientTransport shares SSE retry state across concurrent streams`

This is the campaign's first upstream candidate.

### Lane #67 — reconnect budget and terminal state

Result: **confirmed behavior; separate defect promotion rejected**.

With `maxRetries: 2`:

- six successful primed reopen/drop cycles all scheduled at attempt zero;
- two consecutive failed GET opens used attempts zero and one, then ended the affected request stream once;
- a later independent JSON response succeeded on the same transport;
- a resumed stream that delivered the awaited result ended cleanly and scheduled no further reconnect.

Interpretation:

- `maxRetries` is the maximum number of consecutive failures to open the next SSE stream;
- it is not a total lifetime limit for a resumable logical stream;
- the option wording is broader than the implementation and deserves clarification;
- standalone dead response-channel behavior remains correctly routed to upstream #2098.

Verification:

- source-tree fixture on Node 20, 22, and 24;
- published `@modelcontextprotocol/client@2.0.0` fixture on Node 20, 22, and 24;
- source workflow `30477560619`;
- release-artifact workflow `30478067730`;
- lane report in PR #90.

### Lane #68 — result replay and duplicate execution

Result: **confirmed ownership boundary**.

Stateful v2 server replay:

- event-store-backed server stores the final result after the original SSE stream closes;
- two GET reconnects with the same session and `Last-Event-ID` each replay the result;
- tool execution count remains one.

Current hosted Stensibly:

- POST-only;
- stateless JSON response;
- session IDs disabled;
- one transport created and closed per request;
- no event store or GET resume path.

Stensibly ambiguous retry test:

- first mutation commits while the response body is abandoned;
- operation receipt identifies one item and says `do_not_retry`;
- exact retry enters `createItem` again and returns the original item;
- one item and one creation event remain;
- changed durable input under the same idempotency key conflicts.

Verification:

- SDK replay workflow `30480085816` on Node 20, 22, and 24;
- Stensibly CI `30480313838` with typecheck, 952 Bun tests across 192 files, Convex tests, Worker bundle, and runtime parity;
- Stensibly PR #565;
- lane report in PR #100.

No MCP SDK defect packet came from Lane #68. The replay behavior correctly separates duplicate result delivery from duplicate execution.

## Evidence ranking

### 1. Cross-stream retry-value coupling

Status: confirmed and novel after duplicate search.

Evidence:

- source ownership mismatch;
- private-method control;
- real class execution;
- public `start()` / `send()` reproduction;
- real local HTTP POST and resumed GET;
- replay cursor proves the reconnect belongs to A;
- both shorter and longer delay directions;
- Node 20/22/24 matrix.

Remaining evidence before upstream filing:

- a concise standalone reproduction suitable for the v2 issue template;
- optional workload measurement showing reconnect volume or latency impact;
- explicit human authorization to contact upstream.

### 2. One reconnect cancellation slot

Status: confirmed lower-impact cleanup issue.

Evidence:

- one cancellation field;
- newest-only cancellation;
- older default timer remains after close.

Narrowing control:

- stale callback is blocked from network activity by abort guards.

Recommended routing:

- supporting evidence in the retry-state issue, or a separate cleanup issue only if a platform scheduler demonstrates larger retained-work cost.

### 3. Standalone response-channel terminal state

Status: real adjacent concern, already tracked upstream in #2098.

Recommended routing:

- do not duplicate;
- add per-request versus standalone-channel distinctions only after authorization.

### 4. Retry-count reset after successful open

Status: confirmed mechanism; defect promotion rejected.

Recommended routing:

- documentation clarification, not a bug report titled as limit bypass.

### 5. Session replay duplicate execution

Status: disproved.

Stateful replay redelivers a stored result without resubmitting the tool call.

### 6. Stateless exact retry duplicate durable effect

Status: disproved for Stensibly's protected create path.

The handler runs again, but exact request fingerprinting preserves one item and one creation event.

## Protocol and application ownership

| Concern | Correct owner |
| --- | --- |
| retry delay for one SSE reconnect chain | transport stream state |
| reconnect attempt count | reconnect chain / stream-open sequence |
| cancellation of one pending reconnect | reconnect chain scheduler state |
| session and event replay | server transport and event store |
| duplicate response settlement | client protocol request map |
| durable mutation deduplication | application idempotency contract |
| ambiguity reconciliation | application receipt/read path |

The campaign's main failure comes from storing stream-local retry advice at transport scope.

## Held upstream issue packet

### Proposed title

`StreamableHTTPClientTransport shares SSE retry state across concurrent streams`

### Summary

The v2 client supports concurrent request SSE streams but stores the latest parsed SSE `retry` value once per transport. After A and B receive different retry values, a failed resumed GET for A schedules A's next retry using B's value.

### Minimal sequence

1. Construct one transport with a deterministic reconnect scheduler.
2. Send request A; server returns SSE priming event `retry: 5000`, `id: a-1`, empty data, then closes.
3. Send request B; server returns `retry: 50`, `id: b-1`, empty data, then closes.
4. Execute A's reconnect callback.
5. Observe GET `Last-Event-ID: a-1`; server returns 503.
6. Observe A's next schedule at 50 ms rather than 5000 ms.
7. Reverse the values to reproduce delayed recovery.

### Expected behavior requiring maintainer confirmation

Retry advice should remain associated with the SSE stream/reconnect chain that received it, or the transport must document and enforce a policy that respects every active stream's required interval.

### Demonstrated impact

- unrelated streams change each other's reconnect timing;
- a stream may retry earlier than its server instructed;
- a stream may recover later than its server instructed;
- behavior depends on event ordering among concurrent requests.

### Supporting cleanup observation

The transport also records one reconnect cancellation callback. Closing with two pending default timers leaves the older timer pending until it fires, although abort guards prevent a network request.

### Duplicate check

- #2499: resumption token loss, different behavior;
- #2098: failed-open exhaustion/dead response channel, different behavior;
- no matching issue or pull request found for cross-stream retry coupling.

## Recommended next actions

1. Keep the issue packet held until explicit authorization.
2. Reduce the public HTTP fixture to one standalone reproduction file for the v2 issue template.
3. Optionally measure early-retry request volume and delayed-recovery latency under alternating retry values.
4. Review Stensibly PR #565 as an owned regression test.
5. Treat a stateful hosted Stensibly transport as a separate design campaign, not a small toggle.
6. Preserve all negative findings in any upstream packet so the claim remains narrow.

## Campaign decision

State: ready-for-synthesis

- Primary confirmed SDK defect candidate: cross-stream retry-value coupling.
- Secondary cleanup finding: one cancellation slot / older timer retention.
- Existing issue routing: standalone dead-channel behavior to #2098.
- Documentation candidate: clarify `maxRetries` as consecutive failed stream opens.
- Session replay: works as result replay without tool re-execution.
- Stensibly exact retry: handler re-entry with one durable effect.
- Upstream contact: none.

## Durable artifacts

- Scout PR #42;
- Campaign Lane #66 PR #82;
- Campaign Lane #67 PR #90;
- Campaign Lane #68 PR #100;
- SDK fork draft PR `teamleaderleo/typescript-sdk#1`;
- Stensibly ready PR `teamleaderleo/stensibly#565`;
- this campaign report.
