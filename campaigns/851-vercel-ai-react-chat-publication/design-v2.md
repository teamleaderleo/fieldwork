## In simple words

The first candidate for #851 made every React `replaceMessage` publication shallow. That removes repeated payload copies, but it applies the optimization to imperative user/tool updates too and leaves callback-held nested objects aliased to published snapshots.

A stronger design separates **ownership acquisition** from **publication**:

1. values entering mutable React streaming state are copied once so the SDK owns them;
2. every React stream publication copies only the message shell, `parts` array, and part shells;
3. ordinary non-stream replacements keep their current deep-detachment behavior.

That changes the asymptotic cost from repeatedly copying the complete accumulated assistant message to copying each incoming payload once plus O(number of parts) shells per publication.

## Current constraints established by source and target work

### React Compiler needs fresh part identity

The historical regression in #6466 / #6762 came from compiler memoization when a nested part object kept its identity while fields changed. Any replacement must publish fresh identities at least through each mutable part shell.

### First stream append also needs publication semantics

Core appends the first new assistant response with `pushMessage(response.state.message)`. React currently stores the mutable response object itself. Later chunks mutate that object. This is #852 and means an optimization limited to `replaceMessage` leaves the first publication mutable.

### `replaceMessage` is not stream-only

Core also calls the same state method for explicit user-message edits, tool approvals, and `addToolOutput`. Current React deep cloning therefore acts as a caller-value detachment boundary outside streaming. A blanket shallow replacement weakens that behavior.

### Stream callbacks expose provider/chunk objects

`tool-input-available` stores `chunk.input`, publishes, then invokes `onToolCall` with the tool-call chunk. Persistent data stores the data chunk, invokes `onData`, then publishes. Full-stream consumers also receive the processed chunk object.

With a shallow publication and no ownership split, a callback/consumer retaining one of those nested objects can mutate an already-published React snapshot.

## Proposed interface direction

Add one optional stream-publication capability to `ChatState`; existing framework implementations remain valid because the capability is optional.

Conceptually:

```ts
export interface ChatState<UI_MESSAGE extends UIMessage> {
  status: ChatStatus;
  error: Error | undefined;
  messages: UI_MESSAGE[];
  pushMessage: (message: UI_MESSAGE) => void;
  popMessage: () => void;
  replaceMessage: (index: number, message: UI_MESSAGE) => void;
  snapshot: <T>(thing: T) => T;

  // Optional optimized path for mutable streamed assistant state.
  publishStreamMessage?: (
    message: UI_MESSAGE,
    index: number | undefined,
  ) => void;
}
```

`AbstractChat.runUpdateMessageJob` would prefer this capability for stream writes:

```ts
const replaceIndex =
  response.state.message.id === this.lastMessage?.id
    ? this.state.messages.length - 1
    : undefined;

if (this.state.publishStreamMessage != null) {
  this.state.publishStreamMessage(response.state.message, replaceIndex);
} else if (replaceIndex != null) {
  this.state.replaceMessage(replaceIndex, response.state.message);
} else {
  this.state.pushMessage(response.state.message);
}
```

React implements `publishStreamMessage` with fresh message and part shells. Vue/Svelte/Angular and third-party states can continue using the existing path unchanged.

This one operation covers both first append (#852) and later replacement (#851).

## One-time stream ownership

Cheap publication is safe only if nested values in `response.state.message` are SDK-owned.

The cleanest boundary is inside the Chat invocation of `processUIMessageStream`:

- the original `UIMessageChunk` remains the value delivered to callbacks and full-stream consumers;
- React streaming state processes a deep-owned copy of any chunk that enters message state;
- a 64 KiB tool output is therefore copied once when its `tool-output-available` chunk enters state, not once for every later chunk.

Conceptually, `processUIMessageStream` gains an optional internal snapshot hook:

```ts
processUIMessageStream({
  ...,
  snapshotChunkForState,
});
```

For the React Chat path, the hook can reuse the React state's existing structured-clone capability. Other callers omit it and retain existing behavior.

Inside the transform, keep two values:

```ts
async transform(externalChunk, controller) {
  const chunk = shouldEnterMessageState(externalChunk)
    ? snapshotChunkForState?.(externalChunk) ?? externalChunk
    : externalChunk;

  // mutate state from `chunk`
  // invoke onToolCall/onData with `externalChunk`
  // enqueue `externalChunk` to downstream consumers
}
```

Transient data/error-only events should not be cloned merely because they pass through the processor; only chunks whose nested values can become part of mutable message state need ownership acquisition.

## Imperative output during an active response

`addToolOutput` can inject a caller-owned output directly into `activeResponse.state.message`, bypassing stream-chunk processing.

When the optimized stream-publication capability is active, this one ingress also needs an owned value before it is stored in the active response. Conceptually:

```ts
const activeOutput =
  this.state.publishStreamMessage != null
    ? this.state.snapshot(output)
    : output;
```

Use that owned value in `activeResponse.state.message`. The immediate ordinary `replaceMessage` remains deep-cloned exactly as today.

This can cost up to another full copy at the moment an imperative output is supplied, but it is O(payload size) once rather than O(accumulated message size × later chunks).

## Callback semantics

This design intentionally treats callbacks as observers/executors, not mutation APIs for internal chat state.

### onToolCall

Current order is state update → write → callback. With owned state:

- the first publication contains the provider input before callback mutation;
- callback mutation affects only the callback's external chunk object;
- future React publications continue using the SDK-owned input.

### onData

Current order for persistent data is state update → callback → write. With an owned state chunk:

- callback receives the original external data object;
- React state uses the owned copy;
- callback mutation does not mutate message state.

This is a behavioral tightening compared with accidental aliasing today. The public callback documentation describes observation/tool execution and provides explicit APIs such as `addToolOutput` for state changes; no supported mutation contract was found.

A human upstream packet should call this compatibility point out explicitly rather than hiding it.

## Why this is better than a WeakMap clone cache

A React-only cache from raw nested object identity to previously cloned payload could avoid repeated clones, but it cannot detect later in-place mutation of the same external object. It would silently freeze whichever version was cached first.

Owning the value at ingress makes that boundary explicit: external objects stop being state after ingestion. No deep comparison or mutation detection is required.

## Complexity target

For a stream with payload chunks `p1..pn` and message part counts `m1..mk`:

- current cost includes repeated recursive copies of all accumulated payloads at each publication;
- proposed payload-copy cost is approximately `sum(size(pi))` for state-entering payloads;
- publication cost is approximately `sum(mi)` small shell copies.

The upstream #18625 reproduction's 40 × 64 KiB outputs should therefore clone about final payload size once at ingress, plus shell overhead, instead of 104,857,600 cumulative output bytes.

## Required RED/GREEN tests

### Existing / prepared

1. 40x clone amplification reproduction — upstream documented.
2. fresh part identity / prior text snapshot stability — owned candidate.
3. React Compiler stale-part negative control — prepared.
4. React Compiler supported transition discriminator — prepared.
5. first assistant append alias (#852) — prepared.
6. imperative `addToolOutput` caller-value detachment — prepared.
7. callback-held tool input / data prior-snapshot immutability — prepared.

### Add for the v2 candidate

8. mutate the original transport `tool-output-available.output` after ingestion; later publications must retain the ingested value.
9. assert the original external output and React state output are different nested identities after ingestion.
10. assert a large output is cloned once at ingress and not recursively copied on unrelated later text/tool chunks.
11. retain ordinary user-message replacement deep-detachment behavior.
12. retain ordinary `addToolOutput` published detachment with and without an active response.
13. verify transient `data-*` chunks remain callback-only and do not acquire unnecessary structured-clone requirements.
14. run the full ordinary `@ai-sdk/react` suite and type-check.

## Decision

Design B/C from the campaign report can be combined:

**optional stream-specific publication + one-time state ownership at stream ingress**.

This is currently the strongest candidate because it addresses all four established constraints together:

- clone amplification;
- React Compiler part identity;
- first-publication immutability;
- caller/callback nested-object ownership.

The existing broad #91 patch remains useful for compiler characterization, but should not be promoted as the final implementation.

No third-party upstream mutation or automated upstream contact is authorized or performed.