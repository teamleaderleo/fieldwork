## In simple words

Anthropic's streaming adapter already knows how to classify a provider SSE error as `APICallError` when that error is the first provider event. The identical valid error event later in the stream is emitted as the provider's raw `{ type, message }` object.

This means `overloaded_error` is retry-classifiable at stream startup (`statusCode: 529`, `isRetryable: true`) but becomes an untyped plain object after text/tool output has started. The public reports #18667 and #18669 describe that exact application failure mode.

A small provider-local fix can remove the inconsistency without designing automatic stream retry: construct the same `APICallError` for every parsed Anthropic SSE `error` event, then keep the first-chunk preflight behavior unchanged by throwing that instance when it appears first.

## Assignment

- Programme: `sdk-integration-lifecycle` / #13
- Target: `vercel-ai` / #2
- Lane: #860
- Worker: `chatgpt:gpt-5.6-sol`
- Public source pin: `vercel/ai@7d40fafc394a2c9033f931eb85c895e3817f4b58`
- Owned reproduction: `teamleaderleo/ai#105`
- Upstream mutation: prohibited and not performed

## Source map

### Provider stream contract

`packages/provider/src/language-model/v4/language-model-v4-stream-part.ts` intentionally permits:

```ts
{ type: 'error'; error: unknown }
```

The generic provider contract therefore cannot promise a typed error on its own.

### Anthropic adapter

`packages/anthropic/src/anthropic-language-model.ts` parses Anthropic SSE chunks using `anthropicChunkSchema`.

For a successful parsed Anthropic error event, the transform currently does:

```ts
case 'error': {
  controller.enqueue({ type: 'error', error: value.error });
  return;
}
```

Immediately below, the same `doStream()` implementation tees the transformed stream and inspects the first provider part. When that first provider part is an error, it builds:

```ts
new APICallError({
  message: error.message,
  url,
  requestBodyValues: body,
  statusCode: error.type === 'overloaded_error' ? 529 : 500,
  responseHeaders,
  responseBody: JSON.stringify(error),
  isRetryable: error.type === 'overloaded_error',
})
```

So the adapter already owns the request URL/body, response headers/body, and retry mapping necessary to produce a useful typed error.

### AI core forwarding

`packages/ai/src/generate-text/stream-language-model-call.ts` forwards provider stream parts that do not need special translation. A provider error part therefore keeps its `error` value.

`packages/ai/src/generate-text/stream-text.ts` forwards the enriched chunk downstream before its `onError` handling. It invokes `wrapGatewayError(part.error)`, but that helper only rewrites gateway-authentication errors and otherwise returns the original value.

Therefore Anthropic's raw mid-stream object naturally reaches both stream consumers and `onError`; there is no later generic normalization layer that repairs the provider asymmetry.

Evidence class: `source-read`.

## Public issue fit

- #18667 reports valid provider SSE errors after streaming has begun as plain objects, including `{ type: 'api_error', message: ... }`, `{ message: 'Internal server error' }`, and `{ message: 'Overloaded' }`. The report asks for stream retry or at minimum a typed, retry-classifiable error.
- #18669 extracts the smaller feature request: normalize mid-stream provider errors into public typed errors independently of automatic retry.

This lane addresses the Anthropic adapter subset where the provider payload already matches Anthropic's accepted `{ type, message }` schema. It does not claim a generic solution for message-only payloads from other adapters and does not implement stream retry.

Evidence class: `upstream-documented`.

## Runnable discriminator

Owned fork PR #105 adds `packages/anthropic/src/anthropic-midstream-error.repro.test.ts`.

The test is provider-only and network-free. It supplies an in-memory SSE response containing:

1. a valid `message_start`;
2. a text content block and text delta;
3. an Anthropic `error` event.

It contains three cases:

1. control: initial `overloaded_error` remains an `APICallError` with message `Overloaded`, status `529`, and `isRetryable: true`;
2. mid-stream `overloaded_error` must have the same classification;
3. mid-stream `api_error` must use the provider's existing first-error fallback mapping (`statusCode: 500`, `isRetryable: false`).

Expected current behavior: the first case passes; the latter two are RED because the stream contains the raw provider object.

Evidence class: `target-test-prepared`; execution unclaimed until the owned-fork test runs.

## Candidate diff

Keep the generic `LanguageModelV4StreamPart.error` contract unchanged.

Inside the Anthropic adapter, factor the existing mapping into one local builder, conceptually:

```ts
const createStreamError = (error: { type: string; message: string }) =>
  new APICallError({
    message: error.message,
    url,
    requestBodyValues: body,
    statusCode: error.type === 'overloaded_error' ? 529 : 500,
    responseHeaders,
    responseBody: JSON.stringify(error),
    isRetryable: error.type === 'overloaded_error',
  });
```

Then:

- parsed Anthropic `case 'error'` enqueues `createStreamError(value.error)`;
- the first-chunk guard throws the already-normalized `APICallError` when present;
- non-provider parser/validation errors retain their current fallback behavior.

This reuses policy already present in the provider rather than introducing new status/retry semantics.

## Why provider-local first

A new generic `StreamProviderError` may still be useful for providers that expose only a message or lack request/status context. Anthropic does not need that new abstraction to fix this concrete bug: it already has an error schema and already maps it to `APICallError` at stream start.

Provider-local parity is smaller, easier to regression-test, and can coexist with later generic normalization or stream retry.

## Negative/adjacent findings

- `maxRetries` remains out of scope because it wraps the initial model call, not a stream that has already been returned.
- Bedrock Anthropic issue #17124 is adjacent but already has fix PR #17125 for exception-frame parsing; do not duplicate it.
- No open PR matching #18667/#18669 or this Anthropic mid-stream classification fix was found during the overlap refresh.

## Promotion gates

1. Owned RED test reproduces the initial-vs-mid-stream classification split.
2. Candidate makes both mid-stream cases pass without changing first-chunk behavior.
3. Existing Anthropic package tests pass.
4. Anthropic package type-check/build pass.
5. `streamText` provider-free integration confirms `onError` receives the typed instance unchanged.
6. Full stream confirms the error part carries the same typed instance/classification.
7. Upstream overlap is refreshed immediately before any human delivery packet.

## Recommendation

Retain #860. If the owned reproduction executes as expected, implement the provider-local helper first. Treat generic message-only normalization and automatic stream recovery as separate follow-up questions.

No automated upstream contact is authorized or performed.
