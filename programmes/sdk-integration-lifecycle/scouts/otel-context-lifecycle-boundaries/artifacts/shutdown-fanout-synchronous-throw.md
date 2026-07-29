# Shutdown fanout after a synchronous processor exception

## In simple words

Shutdown is supposed to fan out across all owned processors and signal providers. Today, one custom trace processor that throws synchronously can stop that fanout before later trace processors, the logger provider, or the meter provider are even asked to shut down.

This is retained as a lower-level lead. The characterization source has not been executed in the current environment, so it is not yet promoted to a separate upstream candidate.

## Pinned scope

- repository: `open-telemetry/opentelemetry-js`
- revision: `7b06368b7362a30ca69c178f43bd94dfbb36f85d`
- packages: `@opentelemetry/sdk-trace` and `@opentelemetry/sdk-node`
- characterization branch: `fieldwork/nodesdk-shutdown-lifecycle-characterization`
- characterization commit: `c4b8b1ea44563c2ae826ea36f6906c84dfb67642`

## Source sequence

`MultiSpanProcessor.shutdown()` calls each processor's `shutdown()` while constructing a promise array:

https://redirect.github.com/open-telemetry/opentelemetry-js/blob/7b06368b7362a30ca69c178f43bd94dfbb36f85d/packages/sdk-trace/src/MultiSpanProcessor.ts#L64-L74

If one call throws synchronously, the loop exits before later processors are invoked and before `Promise.all` exists.

`NodeSDK.shutdown()` uses the same eager pattern across providers, in trace → logs → metrics order:

https://redirect.github.com/open-telemetry/opentelemetry-js/blob/7b06368b7362a30ca69c178f43bd94dfbb36f85d/experimental/packages/opentelemetry-sdk-node/src/sdk.ts#L365-L381

If trace-provider shutdown throws synchronously, logger- and meter-provider shutdown calls are never made.

## Characterization

New test file:

`experimental/packages/opentelemetry-sdk-node/test/lifecycle-shutdown-fanout-characterization.test.ts`

The test configures:

1. a first custom span processor whose first shutdown call throws synchronously;
2. a second span processor that records shutdown calls;
3. a log processor that records shutdown calls.

Source-predicted first-call result:

- the first processor is called once and throws;
- the second span processor is not called;
- the logger processor is not called;
- `NodeSDK.shutdown()` throws synchronously rather than returning a rejected promise.

The test makes the first processor succeed on a second call so the remaining providers can be cleaned up and the skipped calls can be observed.

## Why this matters

A fanout coordinator should usually attempt cleanup for every owned component even when one component fails. Failing to call later components can leave background workers, exporter queues, timers, or network resources active during process termination.

The synchronous-versus-asynchronous distinction is also externally visible:

- an asynchronous processor rejection produces a returned rejected promise after all shutdown calls have already been started;
- a synchronous processor throw escapes before later calls are started and before a promise is returned.

JavaScript's `Promise<void>` type does not prevent an implementation from throwing before returning its promise.

## Possible fixes

### At `MultiSpanProcessor`

Wrap each invocation so a synchronous throw becomes a rejection without stopping later invocation scheduling:

```ts
const promises = this._spanProcessors.map(spanProcessor =>
  Promise.resolve().then(() => spanProcessor.shutdown())
);
return Promise.all(promises).then(() => {});
```

This preserves rejection while ensuring every processor is scheduled.

An alternative is `Promise.allSettled()` plus an aggregated error policy, but that changes which error is surfaced and requires a contract decision.

### At `NodeSDK`

Apply the same defensive wrapping to each provider shutdown so every signal provider is attempted even when one provider throws synchronously.

### At provider implementations

Providers may also catch synchronous processor exceptions internally, but aggregate helpers should not rely entirely on every nested implementation being defensive.

## Relationship to existing candidates

This is adjacent to the promoted trace-provider shutdown-contract candidate, which currently focuses on one-shot shutdown and post-shutdown no-op behavior.

Do not automatically expand that issue draft. First decide whether the review unit should be:

- one broader trace shutdown-contract issue;
- a narrow `MultiSpanProcessor` fanout issue and PR;
- a separate NodeSDK aggregate-shutdown robustness issue;
- or a shared utility used by trace, logs, metrics, and NodeSDK.

## Prior-art search

A targeted search of open and closed `opentelemetry-js` issues for synchronous shutdown exceptions and skipped later processors did not return a direct match at the recorded check.

This negative search result is not proof that no related issue exists.

## Validation boundary

The test source is present in the fork, but dependencies are unavailable in the current work environment and no passing CI run is claimed.

Local command:

```bash
npm ci
npm run compile
npm test --workspace=@opentelemetry/sdk-node -- --grep "NodeSDK shutdown fanout characterization"
```

## Contact boundary

No upstream issue, pull request, comment, review, reaction, or direct backlink was created.