# Adjacent stream lifecycle scout — 2026-08-01

## In simple words

A deeper pass around the explicit-abort code found one separate stream-helper defect and two useful limits on the current unit. When an SDK async iterator encounters a source-stream error, it propagates the error but keeps its reader lock forever. A small Node model reproduced the leak and showed a one-catch repair that preserves the original error and releases the lock. The finding affects many streaming APIs, so it belongs in a separate follow-up rather than the six-file explicit-abort candidate.

The same pass weakened two easier theories. `createStitchableStream.terminate()` can expose a raw rejecting cancellation promise, but the transformed streams registered by `streamText` contain that rejection in the modeled path. Tool-input lifecycle callbacks also finish before local tool execution reaches its later `model-call-end` trigger.

A pre-aborted `streamText` operation still proceeds through setup and invokes the provider with an already-aborted signal. `generateText` follows the same first-attempt convention, and the provider interface explicitly assigns cancellation handling to the supplied signal. This remains a compatibility-sensitive design question and an uncovered test boundary, not a demonstrated unit-06 defect.

## Scope and exact revisions

- Fieldwork assignment: upstream unit 06, `fix(ai): make explicit abort settlement nonblocking`.
- Public target revision: `vercel/ai@e84b8bc8154030cdb7469b0e0b8cd8b9354f19a0`.
- Canonical owned candidate: `teamleaderleo/ai@3035f6e5a3ef6ff9236c8d1b08f4ea3dfe852c15`.
- Retrieval and execution date: `2026-08-01`.
- Model environment: Linux container, Node `v22.16.0`.
- Claim scope: mechanism and public stream interface.
- Network use: none for the models.
- Upstream contact authorized: no.

## Source map inspected

- `packages/ai/src/util/async-iterable-stream.ts`
- `packages/ai/src/util/async-iterable-stream.test.ts`
- `packages/ai/src/util/create-stitchable-stream.ts`
- `packages/ai/src/util/create-stitchable-stream.test.ts`
- `packages/ai/src/generate-text/stream-text.ts`
- `packages/ai/src/generate-text/stream-language-model-call.ts`
- `packages/ai/src/generate-text/invoke-tool-callbacks-from-stream.ts`
- `packages/ai/src/generate-text/execute-tools-from-stream.ts`
- `packages/ai/src/generate-text/generate-text.ts`
- `packages/provider-utils/src/retry-with-exponential-backoff.ts`
- `packages/provider-utils/src/delay.ts`
- `packages/provider/src/language-model/v4/language-model-v4-call-options.ts`
- stream and tool API reference documentation
- active upstream abort PR `#16852` at `0ef2ae9a7f143d90972b4ff217046e0b04ea67f1`

## Finding A — async iterator retains its reader lock after source error

### Current source behavior

`asAsyncIterableStream()` obtains one reader per async iterator. `next()` releases it when `read()` reports `done`, and `return()` / `throw()` release it through `cleanup()`. A rejection from `reader.read()` exits `next()` directly, skipping cleanup.

The existing source-error test verifies the propagated error and collected chunks. It does not inspect `stream.locked` or attempt to acquire another reader after the error.

The helper backs public streams across text generation, object generation, UI messages, agents, workflows, transcription, and translation.

### Model command

```sh
node /tmp/async-iterable-lock-probe.mjs
```

The probe copied the exact helper control flow, including the identity `TransformStream` added by `createAsyncIterableStream()`. It compared:

1. the current SDK helper;
2. the platform-native `ReadableStream` async iterator;
3. a candidate where `next()` catches `reader.read()` rejection, calls `cleanup(false)`, and rethrows the original error.

### Result

```json
{
  "sdkHelper": {
    "caughtName": "Error",
    "caughtMessage": "source failed",
    "lockedAfterError": true,
    "secondReaderAcquired": false,
    "secondReaderError": "TypeError: Invalid state: ReadableStream is locked"
  },
  "native": {
    "caughtName": "Error",
    "caughtMessage": "source failed",
    "lockedAfterError": false,
    "secondReaderAcquired": true
  },
  "fixed": {
    "caughtName": "Error",
    "caughtMessage": "source failed",
    "lockedAfterError": false,
    "secondReaderAcquired": true
  }
}
```

### Consequence

After an upstream stream error, the SDK-created stream remains locked to an iterator that has already failed. Further direct stream operations requiring an unlocked stream, including acquiring another reader, fail with `TypeError`. The original provider error still reaches the consumer.

This is an interface-level resource-ownership defect in the shared helper. The model does not establish how frequently applications reuse the same stream after an error or whether every runtime behaves identically.

### Narrow candidate

```ts
async next(): Promise<IteratorResult<T>> {
  if (finished) {
    return { done: true, value: undefined };
  }

  try {
    const { done, value } = await reader.read();

    if (done) {
      await cleanup(true);
      return { done: true, value: undefined };
    }

    return { done: false, value };
  } catch (error) {
    await cleanup(false);
    throw error;
  }
}
```

The distinguishing target-native regression should assert the source error identity, `stream.locked === false`, and successful acquisition of a new reader after iteration rejects. Node and Edge should both run because this helper is shared across environments.

### Disposition

Retain as a ranked follow-up outside unit 06. It changes `async-iterable-stream.ts`, has a wider API surface and owner than the explicit-abort terminal arbitration, and should receive its own target-native characterization and duplicate/prior-art refresh.

Evidence class: `source-read` plus `model-executed`.

## Finding B — `terminate()` raw rejection does not reproduce through the registered stream layers

### Suspicious source

`createStitchableStream.terminate()` invokes each `reader.cancel()` without awaiting or attaching a rejection handler. Its tests cover successful cancellation only.

### Model command

```sh
node /tmp/stitchable-cancel-probe.mjs
```

The probe used a stream whose underlying `cancel()` returned `Promise.reject(new Error('cleanup failed'))`, then compared zero, one, and two identity transform layers before acquiring the reader and issuing unobserved cancellation.

### Result

```json
[
  {
    "layers": 0,
    "unhandledRejections": ["cleanup failed"]
  },
  {
    "layers": 1,
    "unhandledRejections": []
  },
  {
    "layers": 2,
    "unhandledRejections": []
  }
]
```

### Interpretation

A raw inner stream can surface an unhandled rejection through `terminate()`. The model-call and tool streams registered by `streamText` pass through transform layers first, and the modeled rejection is contained there. No current `streamText` product manifestation was established.

Disposition: retain as a utility-contract hazard and negative result for unit 06. Reopen only with a real raw-stream call site or a target-native `streamText` reproduction.

Evidence class: `source-read` plus `model-executed`.

## Negative result — tool-input callbacks do not race local execution

`invokeToolCallbacksFromStream()` enqueues a tool-input or tool-call chunk before awaiting its lifecycle callback. That ordering initially suggested that local execution could begin while `onInputAvailable` remained pending.

The downstream `executeToolsFromStream()` queues tool calls but starts them only when the later `model-call-end` chunk crosses the same upstream transform. A pending input callback blocks that later chunk. Local tool execution therefore cannot begin before the input callback settles in this path.

Disposition: premise rejected. No change proposed.

Evidence class: `source-read`.

## Open design question — pre-aborted operations still invoke the first provider attempt

The canonical pre-aborted `streamText` regression checks public abort settlement but does not count provider calls or lifecycle callbacks. Source control flow shows:

1. the outward abort path settles and closes immediately;
2. background setup continues through `onStart`, step preparation, and model-call-start callbacks;
3. `doStream()` receives the already-aborted signal;
4. the returned model-call stream is cancelled before stitchable registration.

`generateText()` follows the same convention for its first attempt: it calls `doGenerate()` with the merged signal and calls `throwIfAborted()` only before later steps. The provider V4 contract describes the field as an “Abort signal for cancelling the operation,” assigning providers a direct cancellation boundary.

Possible interpretations:

- provider invocation is valid because every provider receives the already-aborted signal and owns cooperative cancellation;
- core should short-circuit before lifecycle callbacks and provider invocation to avoid work or side effects from a non-cooperative custom provider;
- public settlement should remain immediate while selected setup callbacks still run for observability, requiring a narrower provider-only guard.

A zero-provider-call assertion would change shared `streamText` / `generateText` convention and callback semantics. Current evidence does not choose that contract safely.

Disposition: record the test blind spot and defer implementation. A separate characterization should count `onStart`, `onStepStart`, `onLanguageModelCallStart`, and provider invocation for a pre-aborted signal across both APIs before selecting behavior.

Evidence class: `source-read`.

## Ranked branch candidates

1. **Async iterator releases reader lock after source error** — concrete shared-helper defect, minimal repair, model-confirmed, target-native test needed.
2. **Pre-aborted provider-attempt contract** — consequential but compatibility-sensitive; characterize both `streamText` and `generateText` before change.
3. **Raw stitchable terminate rejection containment** — utility-level hazard without a demonstrated product path.

## Unit-06 conclusion

The deeper pass found no new defect in the six-file explicit-abort terminal-ordering candidate. Its `HOLD` disposition remains appropriate while exact-head CI and independent review are absent. The async-iterator lock leak deserves separate follow-up and should not be folded into the current source branch.
