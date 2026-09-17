## In simple words

Vercel AI SDK keeps generation, tool execution, UI reconstruction, and resumable-stream storage in separate owners.

The core `streamText` path owns model steps and passes one merged abort signal into provider calls and local tools. Explicitly aborting that signal stops the provider/tool path and emits an `abort` stream part. Cancelling a reader follows a different path: it cancels Web Stream readers while leaving the abort signal untouched.

A synthetic Web Streams probe reproduced the consequence of that split. Reader cancellation closed the source connection while already-running tool-like work completed; its result then failed to enter the cancelled stream. Explicit abort stopped the work with `AbortError`.

The repository tests each side of this boundary separately, including explicit abort during tool execution and reader cancellation with partial UI persistence. I found no pinned-revision test that combines reader cancellation with an in-flight local tool. That combination is the realistic next branch.

**Recommendation: additional scout.** Build one provider-independent public-API reproduction using `streamText`, a mock model, and a delayed side-effecting local tool. Cancel `result.stream` after tool execution begins, then record whether the tool completes, what callbacks fire, and how result promises settle. Promote to a campaign only after that reproduction confirms an observable SDK consequence.

## Assignment record

- Fieldwork lane: issue #17
- Programme: `sdk-integration-lifecycle` (#13)
- Target hub: `vercel-ai` (#2)
- Worker: `teamleaderleo`
- Claim scope: `interface`
- Upstream contact authorized: `false`
- Upstream contact performed: `false`
- Fixes implemented: none
- Upstream repository: `https://github.com/vercel/ai`
- Pinned revision: `2b872b0db3769decf69945830c66a897c1e37347`
- Revision source: `main` head retrieved 2026-07-29
- Fieldwork branch base: `85f4213cf13165910f3401f6dc0c9dd031ad2527`

## Method and evidence limits

I read the pinned source, repository guidance, focused unit tests, and the resumable-stream documentation. Source access used the GitHub connector at the exact revision. A local upstream checkout was unavailable, so the probe uses platform Web Streams and AbortController primitives to isolate the ownership boundary. It models the mechanism; it does not count as a full AI SDK reproduction.

Evidence labels used below:

- **Source-verified:** direct reading at the pinned revision.
- **Test-verified:** an upstream test asserts the behavior at the pinned revision.
- **Probe-verified:** the included synthetic probe produced the result locally on Node `v22.16.0`.
- **Interpretation:** a bounded conclusion from the listed source, test, or probe evidence.

## Public and internal entrypoints

| Layer | Entrypoint | Role | State owner |
|---|---|---|---|
| Package root | `packages/ai/src/index.ts` | Re-exports core generation, tools, UI, and UI stream APIs. | None; export surface only. |
| Core text API | `packages/ai/src/generate-text/index.ts` → `streamText` | Public streaming entrypoint; returns `StreamTextResult`. | `DefaultStreamTextResult` owns final promises, stitched stream, tools, and output configuration. |
| Single provider call | `experimental_streamLanguageModelCall` / `streamLanguageModelCall` | Converts prompts/tools, calls `LanguageModelV4.doStream`, normalizes provider chunks. | Its transform owns parsed tool-call lookup, accumulated model-call content, response ID, and timing data. |
| Local tool execution | `executeToolsFromStream` → `executeToolCall` | Resolves approvals, queues executable tool calls, runs them after `model-call-end`, emits preliminary/final outputs. | Per-call execution function owns tool timeout signal, callbacks, elapsed time, and output/error conversion. |
| Step assembly | `DefaultStreamTextResult` event processor in `stream-text.ts` | Collects content, request metadata, steps, response messages, finish state, and combined usage. | Result instance and per-step locals. |
| Model-message persistence conversion | `toResponseMessages` | Converts step content into assistant/tool model messages for later steps or application persistence. | Stateless conversion; ordering map is local to one conversion. |
| Server UI conversion | `toUIMessageStream` → `handleUIMessageStreamFinish` | Converts core parts into UI chunks, injects response IDs, reconstructs final UI message for callbacks. | Callback reducer owns a cloned/continued assistant message and abort marker. |
| Client UI reducer | `processUIMessageStream` | Applies UI chunks to text, reasoning, tool, approval, metadata, and data-part state. | `StreamingUIMessageState`: message, active text/reasoning maps, partial tool inputs, finish reason. |
| Chat controller | `AbstractChat.makeRequest` | Sends, resumes, consumes, stops, classifies disconnect/error/abort, and auto-submits follow-up turns. | `AbstractChat` owns messages/status/error, one `activeResponse`, its AbortController, and a serial job executor. |
| HTTP transport | `HttpChatTransport.sendMessages` / `reconnectToStream` | POSTs chat state and GETs an active stream. | Transport configuration; application endpoint owns durable stream lookup. |
| React hook | `useChat` | Creates/reuses `Chat`; calls `resumeStream()` on mount when `resume` is true. | React holds the Chat instance and subscriptions; Chat owns lifecycle state. |

## Lifecycle traces

### 1. Normal streaming path

**Source-verified**

1. `streamText` creates `DefaultStreamTextResult`.
2. The result standardizes the initial prompt and prepares merged cancellation/timeout signals.
3. `streamStep` calls `prepareStep`, resolves model/tools/settings, and wraps `streamLanguageModelCall` setup in the retry function.
4. `streamLanguageModelCall` calls `LanguageModelV4.doStream` and normalizes provider V4 chunks.
5. `executeToolsFromStream` forwards normalized chunks and holds executable local tool calls.
6. The result event processor accumulates content and exposes `start`, `start-step`, content/tool chunks, `finish-step`, and `finish`.
7. `toResponseMessages` converts completed step content into assistant/tool messages.
8. A continuation step starts when client tool calls have matching outputs/denials, or provider-executed deferred calls remain, and the stop condition remains open.
9. Final promises resolve when the event processor flushes after at least one recorded step.

The stitchable stream serializes initial approval execution and each model step into one outward stream. `teeStream()` uses `ReadableStream.tee()` for every consumer-facing stream or promise consumption path, with buffering called out in source comments.

### 2. Tool-call lifecycle

**Source-verified and test-verified**

1. Provider `tool-call` chunks enter `parseToolCall`.
2. Parsed calls are indexed by `toolCallId` for approval requests and provider-executed results.
3. Invalid client-side calls emit a typed `tool-error`; provider-executed invalid calls follow provider handling.
4. `executeToolsFromStream` resolves approval policy.
5. Calls needing user approval emit an approval request and pause execution until a later request carries the response.
6. Automatically approved calls emit request and response records, then enter execution.
7. Executable local calls are collected until `model-call-end`.
8. At `model-call-end`, all collected local tools run concurrently through `Promise.all`.
9. `executeToolCall` validates tool context, invokes start callbacks, creates a tool signal from the shared abort signal plus tool timeout, consumes preliminary outputs, and converts success or thrown errors into typed output parts.
10. The step waits for these executions before its transform can finish and before continuation logic can run.
11. Non-provider-executed results become a separate model `tool` message; provider-executed results remain in assistant content.
12. Tool results are sorted to match tool-call order before the next model step.

Upstream tests cover local execution, tool errors, invalid inputs, approval flows, provider-executed results, multi-step continuation, runtime/tool context, sandbox selection, callbacks, and abort during tool execution.

### 3. Cancellation and abort

There are three distinct paths.

#### Explicit core abort

**Source-verified and test-verified**

- Caller `abortSignal` is merged with total, step, first-chunk, and chunk timeout signals.
- The merged signal reaches provider `doStream` and local `executeToolCall`.
- The outer result wrapper observes the signal, invokes `onAbort`, emits an `abort` part with a serializable reason, and closes.
- The upstream `streamText` test “abort during tool execution” triggers the caller AbortController inside a tool and asserts an `abort` part plus `onAbort` with zero completed steps.

#### Chat `stop()`

**Source-verified**

- `AbstractChat.stop()` aborts the active response controller.
- `sendMessages` passes that signal to `fetch`.
- `makeRequest` classifies the resulting abort as `isAbort`, returns status to `ready`, retains generated tokens, and invokes chat `onFinish` from `finally`.

For resumable streams, the documentation defines this client abort as a disconnect from the HTTP reader. The application must expose a dedicated server stop endpoint to persist the partial response, cancel underlying work, and clear the active stream record.

#### Reader cancellation

**Source-verified, test-verified, and probe-verified**

- `StreamTextResult.stream` delegates cancellation to the stitchable stream.
- `createStitchableStream.cancel()` calls each inner cancellation callback, calls each inner reader’s `cancel()`, clears readers, and marks the outer stream closed.
- This function has no AbortController and cannot flip the caller/timeout signal used by provider calls or tools.
- The UI conversion layer calls its `onEnd`/legacy `onFinish` callback on transform cancellation and reports `isAborted: false` unless an explicit `abort` chunk passed through.
- A pinned `stream-text.test.ts` case asserts that reader cancellation calls the UI stream callback with partial content and `isAborted: false`.
- Separate pinned tests assert that core `streamText({ onFinish })` does not fire when the UI reader is cancelled early.

**Interpretation:** cancellation, explicit abort, and server-side stop carry different lifecycle meanings. The source and tests make this distinction intentional at the stream/UI boundary. The remaining question concerns already-running local tool work when only reader cancellation occurs.

### 4. Retries

**Source-verified and test-verified**

- `prepareRetries` defaults `maxRetries` to 2 and rejects negative or non-integer settings.
- The retry helper uses retry headers when reasonable and exponential backoff otherwise; focused utility tests cover `retry-after-ms`, `retry-after`, HTTP dates, multiple attempts, and abort-aware delay.
- In `streamStep`, retry wraps the promise that creates the provider stream: `retry(() => streamLanguageModelCall(...))`.
- Once `doStream` returns a `ReadableStream`, later chunk consumption occurs outside that retry closure.
- A provider stream error rejects result promises and reaches `consumeStream` error handling.
- A stream that closes with no semantic output and no terminal chunk emits `NoOutputGeneratedError`.
- A stream that closes after semantic output, before a finish chunk, resolves with partial output and `finishReason: 'other'`.

**Interpretation:** automatic retries cover call setup/rejection before a usable stream is returned. The core API does not replay a partially consumed model stream. This branch aligns with side-effect safety and requires no campaign from this scout.

### 5. Reconnects

**Source-verified, test-verified, and documentation-verified**

1. React `useChat({ resume: true })` calls `chat.resumeStream()` from an effect.
2. `AbstractChat` asks its transport to `reconnectToStream({ chatId, ... })` before changing status.
3. `HttpChatTransport` defaults to `GET /api/chat/{chatId}/stream`.
4. HTTP `204` means no active stream and leaves chat status unchanged.
5. A response body is parsed into UI chunks and fed through the same client reducer used for a new response.
6. The reducer continues the last assistant message when its role is `assistant`; otherwise it creates a new assistant message.
7. Chat tests cover resumed-stream overlap with a newer request and guard `activeResponse` cleanup by object identity.

The application owns the active stream ID, durable stream bytes, chat-to-stream mapping, resume endpoint, and completion cleanup. The official guide demonstrates Redis plus `resumable-stream`; those products are examples, while the ownership boundary is the stable contract.

### 6. Persistence

Persistence exists at two levels.

#### Model conversation persistence

**Source-verified**

- `toResponseMessages` converts core content into assistant and tool model messages.
- Sources and empty text are excluded.
- Local tool outputs/errors become `tool` messages.
- Provider-executed tool results remain assistant content.
- Denied approvals add an execution-denied tool result.
- Tool results preserve call order.
- Recorded response messages feed later `streamText` steps and are exposed through `responseMessages`.

#### UI message persistence

**Source-verified and test-verified**

- `toUIMessageStream` maps core parts to UI chunks and can inject a stable message ID.
- `handleUIMessageStreamFinish` reconstructs the assistant message for `onEnd`, detects continuation by message ID, includes original history, and reports finish reason and explicit abort state.
- The client reducer mutates one assistant message through streaming text/reasoning/tool states.
- The resumable-stream guide persists user messages before generation, saves an active stream ID, saves the reconstructed message list on end, and clears the active stream ID.

## Focused test map

| Area | Primary tests at the pin | Coverage read |
|---|---|---|
| Core streaming and multi-step lifecycle | `packages/ai/src/generate-text/stream-text.test.ts` | Chunk order, promises, callbacks, errors, partial truncation, tools, approvals, continuation, timeouts, abort, UI conversion. |
| Stream queue/cancellation primitive | `packages/ai/src/util/create-stitchable-stream.test.ts` | Queueing, errors, reader cancellation propagation, cancellation callbacks, immediate termination. |
| Retry timing/policy | `packages/ai/src/util/retry-with-exponential-backoff.test.ts` | Retry headers, exponential delay, multiple retries, provider-like retryable errors. |
| Model-message conversion | `packages/ai/src/generate-text/to-response-messages.test.ts` | Assistant/tool conversion and ordering. |
| UI reducer | `packages/ai/src/ui/process-ui-message-stream.test.ts` | Text/reasoning/tool state transitions, chunk validation, metadata/data parts. |
| Chat lifecycle | `packages/ai/src/ui/chat.test.ts` | send/regenerate/stop, status, partial messages, errors/disconnects, auto-send, resumed-stream races. |
| HTTP transport | `packages/ai/src/ui/default-chat-transport.test.ts` and transport tests | Request bodies, SSE parsing, reconnect request/204 behavior. |
| React resume wiring | React `useChat` tests around `packages/react/src/use-chat.ts` | Hook lifecycle and resume invocation. |

### Coverage gap retained

I found explicit-abort-during-tool coverage and reader-cancel coverage as separate cases. I found no pinned-revision test combining:

1. a local tool whose `execute` has begun,
2. cancellation of `result.stream` or its UI derivative by the consumer,
3. observation of the tool side effect, result delivery, callbacks, and result promises.

This is a search result for the inspected test suite, not a claim about every downstream application or provider package.

## Synthetic probe

Artifacts:

- `artifacts/synthetic-cancellation-probe.mjs`
- `artifacts/synthetic-cancellation-probe.output.json`

Run:

```bash
node programmes/sdk-integration-lifecycle/scouts/vercel-ai-stream-tool-lifecycle/artifacts/synthetic-cancellation-probe.mjs
```

The probe uses a source `ReadableStream`, an async `TransformStream` stage representing tool execution, and a separate AbortController representing the shared provider/tool signal.

Observed result:

```json
[
  {
    "mode": "reader-cancel",
    "events": [
      "tool-start",
      "tool-complete",
      "result-delivery-error:TypeError",
      "source-cancel:consumer-stopped"
    ],
    "sourceCancelled": true,
    "sharedAbortSignalAborted": false
  },
  {
    "mode": "explicit-abort",
    "events": [
      "tool-start",
      "tool-abort:AbortError",
      "source-cancel:cleanup"
    ],
    "sourceCancelled": true,
    "sharedAbortSignalAborted": true
  }
]
```

**Probe-verified conclusion:** Web Stream reader cancellation can close the stream while an async stage governed by a separate signal keeps running. Completion can occur after cancellation, followed by failure to deliver the result into the closed stream. Explicit abort reaches that stage and stops it.

**Boundary:** the probe mirrors the relevant primitives and ownership split. It does not execute `streamText` itself.

## Realistic branch candidates

### Candidate A — consumer cancellation during in-flight local tool execution

- Evidence: source ownership split, separate upstream tests, synthetic probe.
- User-visible consequence under test: side-effecting local tool completes after the consumer has stopped reading; result and step completion may become unavailable to the caller.
- Provider independence: high; local tool and Web Streams path.
- Reproduction status: mechanism reproduced; public AI SDK path pending.
- Recommended disposition: **additional scout**.
- Next scout question: “After a local tool starts in `streamText`, what happens when the sole consumer cancels `result.stream` without aborting the supplied signal?”
- Required observations: tool completion/side effect, tool callbacks, `onAbort`, core `onFinish`/`onEnd`, UI `onEnd`, `steps`, `toolResults`, and unhandled rejection behavior.
- Promotion gate: a minimal public-API reproduction at a pinned revision with a clear consequence and an invariant the SDK can enforce.
- Stop gate: cancellation is documented and tested as connection-only for this exact core path, or the real SDK pipeline aborts/awaits work safely despite the synthetic mechanism.

### Candidate B — silent provider truncation after partial output

- Evidence: pinned test explicitly resolves partial text, one step, `finishReason: 'other'`, and no `onError` when the provider stream closes after output without `finish`.
- Realistic consequence: application persistence can treat a silently truncated response as a completed request while its last UI text part may retain streaming state until conversion policy changes it.
- Recommended disposition: **finding**, with an optional narrow scout only if a target application relies on finish reason or persisted part state.
- Promotion gate: a provider-independent UI-message reproduction shows a persistent incorrect status, duplicate continuation, or data loss.
- Stop gate: application handles `finishReason: 'other'` as partial completion, or the behavior is part of the documented contract.

### Candidate C — retry after stream start

- Evidence: retry closure ends when a stream object is returned; stream failures are handled by stream/error logic; partial streams preserve output.
- Consequence: automatic replay after partial output would risk duplicate text and duplicate tool side effects.
- Recommended disposition: **stop** for a general retry campaign. Retain as a lifecycle finding.

### Candidate D — resumable-stream storage and server stop behavior

- Evidence: transport and guide assign active-stream storage, stream replay, persistence, and underlying cancellation to the application.
- Recommended disposition: **stop** as an SDK defect branch. Application integration audits may still test stale stream IDs, stop races, and persistence correctness.

### Candidate E — callback semantics across cancellation paths

- Evidence: UI conversion callback runs on reader cancellation with `isAborted: false`; core generation `onFinish` remains uncalled in the corresponding cancellation tests; chat `onFinish` runs from `finally` after `stop()`.
- Recommended disposition: **finding**. The split is test-enforced. Any follow-up should target reference clarity or a demonstrated application error, matching the lane’s documentation-only stop condition.

## Recommendation

**Additional scout: consumer cancellation during in-flight local tool execution.**

This lane should hand off its code/test map and synthetic mechanism probe. It should avoid a campaign claim until the public AI SDK pipeline reproduces the consequence. The next scout can stay small:

- one pinned revision,
- one mock provider stream emitting a local tool call and finish,
- one delayed tool with an observable side effect,
- one reader cancelled after tool start,
- one explicit-abort control case,
- callback/promise/event capture,
- no network provider and no upstream contact.

The other branches resolve to findings or stops under the lane’s rules.

## Handoff summary

- Revision pinned: yes.
- Entrypoints and state owners mapped: yes.
- Streaming traced: yes.
- Tool calls traced: yes.
- Cancellation traced: yes.
- Retries traced: yes.
- Reconnects traced: yes.
- Persistence traced: yes.
- Tests mapped: yes.
- Synthetic probe built and run: yes.
- Realistic branch candidates identified: yes.
- Upstream contacted: no.
- Fixes implemented: no.
- Final disposition: **additional scout**.
