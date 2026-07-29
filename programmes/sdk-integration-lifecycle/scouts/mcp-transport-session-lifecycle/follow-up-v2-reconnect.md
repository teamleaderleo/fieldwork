# MCP TypeScript SDK v2 reconnect follow-up

Date: 2026-07-30

Fieldwork scout: #20
Fieldwork PR: #42
Programme: #13
Target hub: #7
Upstream contact authorized: `false`

## Scope

This follow-up checks the scout's reconnect candidates against the v2 release notice, current upstream issue inventory, the exact v2 source pin, and an executable probe committed only to the owned fork.

## Pins

- MCP TypeScript SDK upstream: `modelcontextprotocol/typescript-sdk@cc4b41617ce3601b1290d67216ea0b194a3cd9ac`
- Owned fork: `teamleaderleo/typescript-sdk@cc4b41617ce3601b1290d67216ea0b194a3cd9ac`
- Fork probe commit: `teamleaderleo/typescript-sdk@bc951da9a949d9a948d8fda4933c47abcc5f19f1`
- Fork draft PR: `teamleaderleo/typescript-sdk#1`
- Fieldwork report head before this follow-up: `teamleaderleo/fieldwork@1e7ef12f5957a83cde5d656b9a267fde97ccb1f3`

External references in this report remain read-only and use `redirect.github.com`.

## Release-line check

The pinned source is the v2 `main` branch and implements the 2026-07-28 protocol revision. The repository asks for v2 issues while pull requests are limited during release settling. This changes the eventual upstream packet from a speculative patch to an issue-first report. It does not change the source finding because the scout already pinned the v2 revision.

## Upstream issue landscape

### Existing issue: preserve the resumption token across an empty resumed stream

- [Upstream #2499](https://redirect.github.com/modelcontextprotocol/typescript-sdk/issues/2499) reports that `_handleSseStream()` initializes `lastEventId` to `undefined`, so a resumed stream that closes before receiving another id-bearing event can lose its incoming `Last-Event-ID` on the next reconnect.
- This overlaps the scout's resumption-token concern closely enough that Fieldwork should not draft a second issue for the same behavior.
- Campaign use: treat #2499 as an adjacent dependency and include its fixed/unfixed state in any reconnect matrix.

### Existing issue: retry exhaustion can leave a live POST path with no response stream

- [Upstream #2098](https://redirect.github.com/modelcontextprotocol/typescript-sdk/issues/2098) reports the default two-attempt reconnect ceiling, weak error context, and a dead-channel state where later POSTs can succeed while responses never arrive.
- The issue includes a runnable local reproducer and asks maintainers to choose among reset, fail-fast, or indefinite retry behavior.
- Fieldwork should not duplicate the failed-open exhaustion report.
- The scout's repeated successful reopen/drop candidate is adjacent but distinct: each successful GET open returns control to `_handleSseStream()`, and a later stream close schedules a fresh attempt at count zero. `maxRetries` therefore bounds consecutive failed opens, not the number of reopen/drop cycles in one unstable period.

### Existing issue: claimed reader-lock memory leak is disputed

- [Upstream #1959](https://redirect.github.com/modelcontextprotocol/typescript-sdk/issues/1959) claims that omission of `reader.releaseLock()` leaks parser and decoder state on every reconnect.
- A later issue comment supplies unit and end-to-end counter-probes in which the reader and stream become unreachable and heap stays approximately flat.
- Fieldwork result: do not promote the reader-lock claim without an independent heap dominator chain that identifies a retained owner outside the local `processStream()` scope.

## Source-backed concurrent-state finding

At the pinned v2 revision:

- `_serverRetryMs` is one transport field.
- `_cancelReconnection` is one transport field.
- `_handleSseStream()` may run for multiple request or GET streams and writes every parsed SSE `retry` value into `_serverRetryMs`.
- `_scheduleReconnection()` reads `_serverRetryMs`, records one returned cancel callback in `_cancelReconnection`, and overwrites that slot when another stream schedules.
- `close()` invokes only the currently recorded callback before aborting the transport-wide controller.

The type documentation describes `attemptCount` as belonging to a specific stream, while the retry delay and cancellation slot are transport-wide. This is a concrete ownership mismatch, not yet a confirmed user-visible defect.

## Owned-fork executable probe

Draft PR [teamleaderleo/typescript-sdk#1](https://redirect.github.com/teamleaderleo/typescript-sdk/pull/1) adds three tests against the real v2 class rather than a transcription:

1. Schedule two reconnects and observe that `close()` calls only the second returned cancel callback.
2. Parse `retry: 50` on stream A, then `retry: 5000` on stream B, then schedule A again and observe a 5000 ms delay.
3. Repeatedly open a resumable GET successfully, close its SSE body without a response, and observe each next scheduler call with attempt count zero beyond `maxRetries` cycles.

The tests intentionally assert current behavior. They are reconnaissance evidence, not proposed regression expectations.

### Verification status

- Branch and probe commit created in the owned fork.
- Draft PR created in the owned fork.
- No upstream branch, issue, comment, reaction, PR, or message was created.
- No GitHub Actions run was visible for the fork commit at the time of this follow-up. Treat the probe as source-compiled in intent but not CI-verified until a workflow run or independent local execution is captured.

## Ranked campaign candidates after duplicate filtering

### 1. Concurrent reconnect ownership and teardown

Question: can two active SSE request streams schedule independent reconnects whose retry values, timers, aborts, and stream-end callbacks remain isolated?

Minimum test:

- two streams with different SSE `retry` fields;
- custom scheduler returning two distinct cancel callbacks;
- interleaved graceful close and reader-error paths;
- transport close before either callback fires;
- assert per-stream delay, cancellation, no resurrection, and one terminal callback per stream.

Decision gate:

- If all behavior remains isolated despite shared fields, record the invariant and close the candidate.
- If one stream changes another's delay or leaves an uncancelled scheduled callback with observable work after close, prepare one v2 issue.

### 2. Reconnect budget and dead-channel state machine

Question: what event resets the retry budget, and what state should the transport enter after it cannot maintain a response channel?

Minimum test:

- failed open sequence;
- successful open followed immediately by close, repeated beyond `maxRetries`;
- successful open with at least one message, then close;
- POST after terminal reconnect state;
- explicit assertions for connected, reconnecting, exhausted, closed, and session-reset behavior.

Issue routing:

- Add evidence to #2098 when the result is the same dead-channel state.
- Draft a separate issue only if successful reopen/drop cycles produce a distinct unbounded loop or resource consequence not covered by #2098.

### 3. Session resumption and duplicate execution in Stensibly

Question: after the server accepts work but the client loses the response stream, can a resumed request recover the result without repeating side effects?

Minimum owned trial:

- server records acceptance and a durable operation id;
- response stream drops before result delivery;
- client reconnects with session, protocol version, and resumption token;
- verify event replay, result identity, cancellation, and idempotency;
- compare legacy and 2026-era cancellation behavior.

This trial should not begin until the reconnect ownership fixture is deterministic enough to distinguish SDK behavior from application idempotency behavior.

## Held upstream issue drafts

### Draft A — Concurrent Streamable HTTP streams share retry and reconnect-cancellation state

**Summary**

`StreamableHTTPClientTransport` supports concurrent request SSE streams, but server retry delay and pending reconnect cancellation are stored once per transport. Two streams can therefore overwrite each other's retry timing and cancellation handle.

**Pinned revision**

`cc4b41617ce3601b1290d67216ea0b194a3cd9ac`

**Observed source path**

`packages/client/src/client/streamableHttp.ts`

**Minimal reproduction**

1. Construct one transport with a custom `reconnectionScheduler` that returns distinct cancel functions.
2. Allow stream A to parse `retry: 50` and close before a JSON-RPC response.
3. Allow stream B to parse `retry: 5000` and close before a response.
4. Schedule A's next reconnect and close the transport before callbacks fire.
5. Observe that A uses 5000 ms and only the latest cancel callback is invoked.

**Expected behavior requiring maintainer confirmation**

Retry advice and pending reconnect cancellation should be scoped to the SSE stream that produced or scheduled them, or the transport should explicitly enforce only one reconnectable stream at a time.

**Potential impact**

Cross-stream recovery delay, scheduled work surviving close until the transport-wide abort guard runs, confusing custom scheduler behavior, and harder diagnosis under concurrent long-running requests.

**Duplicate check**

Adjacent to #2499 and #2098, but neither issue describes shared retry delay or a single cancellation slot across concurrent streams.

**Evidence still required before filing**

A CI-passing real-class test and one test that fires the older callback after close to demonstrate whether the surviving schedule has any consequence beyond extra scheduler work.

### Draft B — `maxRetries` resets after every successful SSE reopen, allowing repeated reopen/drop cycles

**Summary**

Reconnect attempt count increments only when `_startOrAuthSse()` rejects. When the GET succeeds and its SSE body then closes without a response, `_handleSseStream()` schedules the next reconnect with attempt count zero. A server or intermediary that repeatedly accepts and immediately drops the stream can therefore cycle beyond `maxRetries`.

**Pinned revision**

`cc4b41617ce3601b1290d67216ea0b194a3cd9ac`

**Expected behavior requiring maintainer confirmation**

Define whether `maxRetries` bounds only consecutive HTTP open failures or the full unstable reconnect episode. If it is the latter, successful opens should not reset the budget until the response channel demonstrates useful stability.

**Potential impact**

Unbounded reconnect activity against an endpoint that repeatedly returns a nominally successful but unusable SSE stream.

**Duplicate check**

#2098 covers exhaustion after failed opens and the resulting dead response channel. This draft should become either a focused addition to #2098 or a separate issue only after an observable distinct consequence is reproduced.

**Evidence still required before filing**

Capture scheduler calls and HTTP GET count over a bounded interval with a real local server, then show CPU, request-rate, log, or resource impact.

## Negative and deferred packets

- Do not file a duplicate of #2499.
- Do not file the reader-lock memory-leak claim from #1959 without new retention evidence.
- Do not propose a reconnect-state implementation before maintainers define the desired terminal state after response-channel loss.
- Do not contact upstream until a human explicitly authorizes the issue packet.

## Recommendation

Open one Fieldwork campaign for concurrent reconnect ownership, retry-budget semantics, and the owned session-resumption trial. Keep Draft A as the first upstream candidate. Route Draft B through #2098 unless the real-server probe proves a separate consequence.
