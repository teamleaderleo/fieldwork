# MCP TypeScript v2 concurrent reconnect ownership

Date: 2026-07-30

Fieldwork lane: #66
Campaign: #65
Programme: #13
Target hub: #7
Parent scout: #20
Worker: ChatGPT GPT-5.6 Thinking acting for `teamleaderleo`
Upstream contact authorized: `false`

## In simple words

The v2 TypeScript client can keep several MCP HTTP response streams open at once. Each stream may receive its own instruction telling the client how long to wait before reconnecting.

The client currently stores only the most recently received wait value for the whole transport. As a result, when stream A fails to reconnect, its next retry can use stream B's instruction instead of A's.

This was reproduced through the public transport API with a real local HTTP server. It occurs in both directions:

- another stream can delay A from 50 ms to 5000 ms;
- another stream can make A retry after 50 ms when A's server instructed 5000 ms.

The second direction is the stronger consequence because it can make the client reconnect earlier than the affected stream's server requested.

The transport also records only one reconnect-cancellation callback. Closing a transport with two default reconnect timers cancels the newer timer and leaves the older timer pending until it fires. The older callback does not perform a fetch after close because the transport-wide abort guard stops it. That is a bounded timer-retention and wake-up issue in the tested path, not a demonstrated post-close network reconnect.

## Verdict

**Confirmed SDK behaviour and credible v2 issue candidate.**

Evidence level:

- protocol text: documented;
- source ownership: observed at the pinned revision;
- real class probes: executed;
- public `start()` / `send()` HTTP reproduction: executed;
- supported Node matrix: executed on Node 20, 22, and 24;
- duplicate search: no matching upstream issue or pull request found;
- production frequency and aggregate impact: unknown;
- upstream report: held, not filed.

The strongest finding is ready for synthesis and for a held issue-first packet. Severity should remain moderate until a workload probe measures reconnect volume, service load, latency, or rate-limit effects under realistic concurrent long-running requests.

## Pins and write boundary

- Public SDK source: `modelcontextprotocol/typescript-sdk@cc4b41617ce3601b1290d67216ea0b194a3cd9ac`
- Package: `@modelcontextprotocol/client@2.0.0`
- Owned fork base: `teamleaderleo/typescript-sdk@cc4b41617ce3601b1290d67216ea0b194a3cd9ac`
- Owned fork probe head: `teamleaderleo/typescript-sdk@4c8e2e1715357f68033dd75570ef76059a3726c8`
- Owned fork draft PR: `teamleaderleo/typescript-sdk#1`
- Successful final workflow run: `30476941445`
- Fieldwork branch: `lane/66-mcp-concurrent-reconnect-ownership`
- Retrieval date: 2026-07-30

The public SDK repository remained read-only. No upstream issue, pull request, comment, reaction, branch, or message was created.

## Question tested

When two or more reconnectable Streamable HTTP response streams overlap, do server `retry` values, pending reconnect schedules, abort signals, replay tokens, and terminal callbacks remain isolated to the stream that owns them?

## Protocol contract

The reviewed Streamable HTTP specification establishes these relevant properties:

1. A request may receive an SSE response stream.
2. A server may send an event ID, close the current connection without ending the logical stream, and instruct the client to reconnect.
3. Before such a close, the server should send the standard SSE `retry` field, and the client must respect that value.
4. A client may keep multiple SSE streams connected simultaneously.
5. Event IDs and replay are associated with the stream that was disconnected; replay must not cross into another stream.

The specification does not state in one sentence that retry storage must be implemented as a per-stream field. The conformance inference is still strong: it permits concurrent streams, attaches the retry instruction to a stream connection being closed, and requires the client to respect that instruction. A last-writer-wins transport field can cause the client to use a different stream's instruction.

## Source ownership map

At the pinned SDK revision:

### Per transport

- `_serverRetryMs?: number`
- `_cancelReconnection?: () => void`
- `_abortController?: AbortController`
- reconnect options and scheduler
- session ID and protocol version

### Per stream or reconnect chain

- `StartSSEOptions`, including resumption token, request signal, replay message ID, and stream-end callback
- local `lastEventId`
- local priming-event and response flags
- `_scheduleReconnection(..., attemptCount)` parameter

### Data flow

1. Every `_handleSseStream()` call constructs its own parser.
2. Every parser's `onRetry` callback writes into the same transport field `_serverRetryMs`.
3. `_getNextReconnectionDelay()` reads that one field before considering stream-specific attempt backoff.
4. `_scheduleReconnection()` records the returned cancellation function in one transport slot, overwriting any prior slot.
5. `close()` calls the currently recorded function and then aborts the transport-wide controller.
6. A reconnect callback checks both transport and request abort signals before issuing its GET.

This creates a mixed ownership model: replay and abort state are mostly threaded per stream, while retry advice and schedule cancellation are transport-wide.

## Probe inventory

The owned fork draft PR contains three focused probe files and one fork-only workflow.

### 1. Class-level reconnect probe

`packages/client/test/client/streamableHttp.reconnectProbe.test.ts`

Covers:

- two pending schedules and one cancellation slot;
- cross-stream retry-delay overwrite;
- an A reconnect failure scheduling A again with B's delay;
- stale older callback after transport close;
- request-scoped abort before callback fire;
- successful reopen/drop cycles resetting attempt count to zero.

### 2. Public HTTP transport probe

`packages/client/test/client/streamableHttp.reconnectPublicProbe.test.ts`

Uses only public lifecycle methods for the transport under test:

- `start()`;
- `send()` for two JSON-RPC requests;
- real local HTTP POST responses carrying SSE streams;
- real resumed HTTP GET with `Last-Event-ID`;
- real 503 response on the resumed GET;
- custom scheduler only for deterministic observation and callback execution.

The server sends protocol-faithful priming events with `retry`, `id`, and empty `data` fields.

### 3. Default timer probe

`packages/client/test/client/streamableHttp.reconnectTimerProbe.test.ts`

Uses the built-in `setTimeout` scheduler with fake time to count pending timers before close, after close, and after the surviving timer fires.

### 4. Fork-only CI

`.github/workflows/fieldwork-reconnect-probe.yml`

- exact lockfile install with `pnpm@10.26.1`;
- Node 20, 22, and 24 matrix;
- no write permissions;
- no upstream interaction.

## Execution record

### Initial real-class run

Workflow run `30476158789`: success.

This confirmed the original three observation tests against the actual v2 repository rather than the synthetic transcription from Scout #20.

### Strengthened class-level run

Workflow run `30476331779`: success.

This added the failed-reopen consequence and negative abort controls.

### Public HTTP run

The first public-server fixture failed on all three Node versions because its priming event and request-body handling did not drive the intended reconnect path. The failure observed zero schedules and was treated as a fixture failure, not SDK evidence.

The fixture was corrected to:

- consume the POST body fully;
- send `retry`, `id`, and `data:` in the SSE priming event;
- allow time for actual HTTP stream processing.

Workflow run `30476742547`: success on Node 20, 22, and 24.

### Final matrix

Workflow run `30476941445`: success on Node 20, 22, and 24.

The inspected Node 22 job reported:

- 36 test files passed;
- 806 tests passed;
- frozen-lockfile install passed;
- all three reconnect probe files passed.

The command caused Vitest to run the complete client suite as well as the named probe files. This provides broader compatibility evidence but does not replace targeted consequence testing.

## Confirmed findings

### F1. Retry advice is last-writer-wins across concurrent streams

**Evidence:** source-observed and public-probe-observed.

Sequence:

1. Stream A receives an SSE priming event with retry value A and event ID `a-1`.
2. Stream B receives another priming event with retry value B and event ID `b-1`.
3. A's scheduled reconnect runs.
4. The resumed GET carries `Last-Event-ID: a-1`, confirming that the reconnect belongs to A.
5. The server rejects that GET with 503.
6. The next schedule for A uses retry value B.

The replay cursor remains A's while the delay comes from B. That cleanly separates the affected stream's identity from the shared delay field.

### F2. Coupling can retry too late or too early

**Evidence:** public-probe-observed.

Both orderings reproduced:

| Stream A instruction | Later stream B instruction | A's next delay after failed resume |
| --- | --- | --- |
| 50 ms | 5000 ms | 5000 ms |
| 5000 ms | 50 ms | 50 ms |

Consequences:

- longer-than-instructed delay can postpone result recovery;
- shorter-than-instructed delay can create earlier reconnect traffic than A's server requested;
- repeated concurrent streams can make retry timing depend on unrelated stream ordering.

The early-retry direction is the stronger protocol concern because the client does not wait the affected stream's provided interval.

### F3. Only the newest pending reconnect has a recorded cancellation callback

**Evidence:** source-observed and class-probe-observed.

With two schedules A then B:

- A's cancellation function is not called by `close()`;
- B's cancellation function is called once.

This result holds for the custom scheduler contract and follows directly from the single `_cancelReconnection` field.

### F4. The older default timer remains pending after close

**Evidence:** timer-probe-observed.

With two default 60-second reconnect timers:

- two timers are pending before close;
- one timer remains pending after close;
- the surviving timer eventually fires;
- the transport abort guard stops it before fetch;
- no timer remains afterward.

Demonstrated consequence:

- pending timer retention and a later callback wake-up after close.

Not demonstrated:

- network reconnect after close;
- post-close error callback;
- message delivery after close.

### F5. Abort guards prevent stale callback network resurrection in tested paths

**Evidence:** class-probe-observed.

- Firing the older uncancelled callback after transport close performs no fetch and emits no error.
- Firing a pending callback after its request-scoped abort performs no fetch.

This limits the cancellation-slot finding. It is not presently evidence that closed transports reconnect over the network.

### F6. Successful reopen/drop cycles reset the attempt parameter

**Evidence:** class-probe-observed; owned by Lane #67 for consequence and terminal-policy analysis.

A nominally successful GET whose resumable SSE body then closes without a JSON-RPC response schedules the next attempt at zero. The probe repeated this beyond `maxRetries` cycles.

This lane records the observation but does not promote it separately. Upstream #2098 already owns adjacent failed-open exhaustion and dead response-channel behavior. Lane #67 will determine whether successful reopen/drop cycles produce a distinct unbounded or resource consequence.

## Negative results and narrowed claims

1. **No post-close fetch:** the surviving callback is guarded by the aborted transport.
2. **No request-aborted fetch:** the request signal prevents resurrection.
3. **No post-close error in the tested callback path.**
4. **No evidence that replay tokens cross streams:** A's real resumed GET carried A's own `Last-Event-ID`.
5. **No duplicate upstream issue found:** searches for the exact fields, concurrent SSE retry coupling, and reconnect-cancellation ownership returned no matching issue or pull request.
6. **No reader-lock leak claim inherited:** that separate upstream claim remains disputed and was not part of this probe.
7. **No production incident established:** frequency, scale, and end-user impact remain unmeasured.

## Alternative explanations tested

### “The shared field is harmless because only one stream reconnects at a time”

Unsupported. The public fixture creates two request SSE streams, each schedules its own reconnect, and A's later schedule uses B's value.

### “The result exists only because private methods were called”

Unsupported. The same retry coupling reproduced through public `start()` and `send()` methods with a real HTTP server and resumed GET.

### “The result is a Node runtime quirk”

Unsupported across the tested range. The final matrix passed on Node 20, 22, and 24.

### “The wrong delay is actually paired with B's replay cursor”

Unsupported. The resumed GET carried A's event ID while its next delay came from B.

### “The cancellation slot causes the closed transport to reconnect”

Unsupported by the current controls. An older timer survives, but the abort guard prevents fetch.

## Consequence ranking

### 1. Early reconnect against stream-local server advice

Highest current concern.

A stream can receive a long retry interval and then retry using a shorter interval supplied by an unrelated stream. Under service overload, maintenance, throttling, or intermediary recovery, that can increase request pressure and defeat the server's intended reconnect pacing for the affected stream.

Evidence supports the mechanism. Aggregate load impact still needs measurement.

### 2. Delayed result recovery

A stream can retry using another stream's longer value. Long-running requests or subscriptions may recover later than their own server advised, increasing visible latency and timeout risk.

### 3. Pending timer or scheduled-task retention after close

One older default timer remains until its deadline. A custom platform scheduler may likewise retain a background task whose cancellation handle was overwritten. The built-in callback is guarded, so the current demonstrated cost is retention and wake-up rather than network activity.

### 4. Diagnostic ambiguity

Logs and scheduler traces may attribute a delay to an attempt count without exposing that the value came from another stream. This makes intermittent concurrent failures difficult to explain.

## Duplicate and adjacent upstream work

### Upstream #2499

Covers loss of an incoming resumption token when a resumed stream closes before a new id-bearing event. It does not cover retry-delay coupling across streams.

### Upstream #2098

Covers failed-open retry exhaustion and a live POST path without a usable response channel. It does not cover a stream using another stream's retry value. Successful reopen/drop budget semantics remain adjacent and are assigned to Lane #67.

### Upstream PR #2541

Adds server-side keepalive timers with explicit per-session or per-request ownership and cleanup. This is useful architectural precedent that stream lifecycle timers can be kept per stream, but it is not evidence about the client finding or a proposed client fix.

## Held v2 issue packet

### Proposed title

`StreamableHTTPClientTransport shares SSE retry state across concurrent streams`

### Summary

`StreamableHTTPClientTransport` supports concurrent request SSE streams, but stores the most recently parsed SSE `retry` value once per transport. After stream A and stream B receive different retry values, a failed resumed GET for A schedules A's next retry using B's value.

The behavior reproduces through the public transport API with a real local HTTP server on Node 20, 22, and 24. It can make A retry either later or earlier than A's own server instruction.

### Pinned version

- `@modelcontextprotocol/client@2.0.0`
- source commit `cc4b41617ce3601b1290d67216ea0b194a3cd9ac`

### Minimal sequence

1. Start one `StreamableHTTPClientTransport` with a deterministic reconnect scheduler.
2. Send request A; return an SSE priming event with `retry: 5000`, `id: a-1`, and empty data; close the response.
3. Send request B; return an SSE priming event with `retry: 50`, `id: b-1`, and empty data; close the response.
4. Execute A's reconnect callback.
5. Observe a GET carrying `Last-Event-ID: a-1`; return HTTP 503.
6. Observe A's next scheduled retry at 50 ms rather than 5000 ms.
7. Reverse the values to observe the delayed-recovery direction.

### Expected behavior requiring maintainer confirmation

Retry advice for a resumable SSE stream should remain associated with that stream's reconnect chain, or the transport should define and document a transport-wide policy that still guarantees each stream's required retry interval is respected.

### Demonstrated impact

- cross-stream retry timing;
- earlier or later retry than the affected stream instructed;
- ordering-dependent recovery under concurrent long-running requests.

### Separate lower-impact observation

The transport also stores one reconnect cancellation callback. Closing with two pending default timers leaves the older timer pending until it fires, although the abort guard prevents a network request. This may belong in the same issue as supporting ownership evidence or in a separate cleanup issue, depending on maintainer preference.

### Evidence to attach if authorized

- public HTTP regression test from the owned fork;
- Node 20/22/24 workflow result;
- source ownership map;
- exact expected and observed scheduler traces;
- negative controls showing no post-close network resurrection.

## Recommended design directions for maintainer discussion

These are alternatives, not implementation commitments.

### A. Per-stream reconnect state object

Keep retry delay, attempt count, cancellation handle, request signal, resumption token, replay ID, and terminal callback together for one stream.

Advantages:

- direct ownership;
- independent cancellation;
- clear cleanup and diagnostics;
- supports concurrent streams naturally.

### B. Map reconnect state by stream identity

Use a stable internal stream key, resumption token, or generated reconnect-chain ID.

Advantages:

- can preserve the existing transport-wide coordinator;
- explicit enumeration and close-all cleanup.

Risks:

- resumption tokens can change;
- needs careful terminal deletion and replay-ID handling.

### C. Conservative transport-wide retry policy

If maintainers intend retry advice to be transport-wide, combine values according to an explicit safe policy rather than last writer wins.

For example, using the maximum active retry value would avoid retrying earlier than any active stream instructed, but it would still delay other streams and would need specification justification. This is weaker than per-stream ownership.

### D. Enforce one reconnectable stream

Reject or serialize multiple reconnectable streams.

This would simplify state but conflicts with the protocol's allowance for simultaneous SSE streams and may reduce supported concurrency. It is included only as a boundary option.

## Follow-up work

1. Lane #67 should quantify successful reopen/drop cycling and define terminal response-channel state.
2. Lane #68 should test accepted-work replay and duplicate execution in Stensibly after the transport fixture is stable.
3. A small load probe should measure requests per minute and recovery latency when unrelated streams alternate low and high retry values.
4. A custom-scheduler probe should model mobile or background-task schedulers where an uncancelled task has a larger cost than a dormant Node timer.
5. Upstream issue filing remains subject to explicit human authorization.

## Decision

- Lane result: `confirmed`
- Campaign disposition: continue
- Upstream packet: ready and held
- Recommended priority: run Lane #67 next; keep the retry-coupling issue packet first in the upstream queue
- Upstream contact: none

## Verification

Owned fork:

```sh
corepack enable
pnpm install --frozen-lockfile
pnpm --filter @modelcontextprotocol/client test -- \
  streamableHttp.reconnectProbe.test.ts \
  streamableHttp.reconnectPublicProbe.test.ts \
  streamableHttp.reconnectTimerProbe.test.ts
```

CI evidence:

- final workflow run: `teamleaderleo/typescript-sdk` run `30476941445`
- Node 20: success
- Node 22: success
- Node 24: success
- inspected Node 22 suite: 36 files and 806 tests passed

## Handoff

State: ready-for-synthesis

Scope supported:

- interface: yes;
- mechanism: yes;
- public-path reproduction: yes;
- multi-runtime execution: yes;
- production consequence magnitude: not yet measured.

Durable artifacts:

- this report;
- owned fork draft PR `teamleaderleo/typescript-sdk#1`;
- three probe files;
- fork-only workflow and successful run `30476941445`.

Decision needed:

- approve or hold the v2 issue packet;
- decide whether the timer-retention observation belongs in the same issue;
- dispatch Lane #67 for retry-budget and terminal-state research.
