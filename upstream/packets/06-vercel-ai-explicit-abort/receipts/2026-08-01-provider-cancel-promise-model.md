# Provider cancellation promise model — 2026-08-01

## Question

Does the existing stream returned by `streamLanguageModelCall()` wait for a provider-controlled `ReadableStream.cancel()` promise before its own `cancel()` promise settles?

This decides whether the pre-registration code in `stream-text.ts`:

```ts
await languageModelStream.cancel(getAbortReason());
```

can retain the internal setup task when provider cleanup rejects or remains pending.

## Exact modeled stack

The source head `92079da650430d8376a7eeef2436910b44393411` returns:

```ts
const standardizedStream = providerStream.pipeThrough(transform);
return createAsyncIterableStream(standardizedStream);
```

`createAsyncIterableStream()` adds one more identity `TransformStream`. The dependency-free probe reproduced that exact cancellation stack with native Web Streams.

## Command

Executed with Node `v22.17.0`:

```bash
node <<'NODE'
function deferred() {
  let resolve;
  const promise = new Promise(r => (resolve = r));
  return { promise, resolve };
}
async function settle(p, ms = 30) {
  return Promise.race([
    Promise.resolve(p).then(() => 'resolved', () => 'rejected'),
    new Promise(r => setTimeout(() => r('pending'), ms)),
  ]);
}

(async () => {
  const requested = deferred();
  const cleanup = deferred();
  const reason = new Error('stop');
  const provider = new ReadableStream({
    cancel(value) {
      requested.resolve(value);
      return cleanup.promise;
    },
  });
  const standardized = provider.pipeThrough(new TransformStream());
  const returned = standardized.pipeThrough(new TransformStream());
  const cancellation = returned.cancel(reason);
  console.log({
    requested: (await requested.promise) === reason,
    cancellation: await settle(cancellation),
    cleanup: await settle(cleanup.promise),
  });
})();
NODE
```

Observed:

```json
{"requested":true,"cancellation":"resolved","cleanup":"pending"}
```

A second probe made the provider `cancel()` return `Promise.reject(new Error('cleanup failed'))`, installed an `unhandledRejection` listener, and observed:

```json
{"cancellation":"resolved","unhandled":[]}
```

## Result

Evidence class: `model-executed`.

The existing returned stream requests provider cancellation, settles its own cancellation promise while provider cleanup remains pending, and contains provider cleanup rejection. Therefore the `await languageModelStream.cancel(...)` expression at this exact source revision already waits only for the request-level cancellation promise, not provider-controlled cleanup completion.

## Correction to prior packet

The earlier packet treated the pre-registration `await` as a retained hostile-provider blocker. The exact modeled Web Streams stack disproves that premise.

A proposed extra wrapper around `streamLanguageModelCall()` was also modeled. Its claimed ordinary-cancellation negative control failed because the existing pipe chain already has request-level cancellation settlement. That wrapper direction was discarded and recorded on owned-fork PR #12.

## Retained target-native gate

Owned-fork PR #12 at `7ae1794889d9dd22eeef9faf4f33d01330c0918d` adds a target-native regression for:

- pending provider cleanup;
- rejected provider cleanup;
- exact abort-reason delivery.

Repository CI run `30691171818` is the exact-head execution gate.

## Limit

This model proves Web Streams cancellation-promise behavior for the exact layering used by the target. Target-native execution remains required for package integration, typing, formatting, and runtime-matrix confidence.
