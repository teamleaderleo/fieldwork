# Fix PR draft and fork trial: clean up failed startNodeSDK setup

## Status

- Draft implemented in user-owned fork: https://redirect.github.com/teamleaderleo/opentelemetry-js/pull/3
- Branch: `fieldwork/start-node-sdk-failure-cleanup`
- Base: `7b06368b7362a30ca69c178f43bd94dfbb36f85d`
- Initial source commit: `2ed8f4b846fc4a62d0e724e43264e7036d7065e7`
- Initial test commit: `3f79d0d93155edd82174d161caafd650aefdcfd7`
- Self-review source repair: `b7992b4e412a66f15bd4035bb7b47ad967586c39`
- Self-review regression test: `482cb975f78572bc65a9b263fb677b7a274e2fff`
- Current reviewed head: `482cb975f78572bc65a9b263fb677b7a274e2fff`
- Upstream issue or PR opened: `false`

## Title

`fix(sdk-node): clean up failed startNodeSDK setup`

## Problem

The experimental `startNodeSDK()` function originally registered supplied instrumentations before it created SDK components.

If component creation threw, the function logged an error and returned `NOOP_SDK`, but:

- an initially disabled instrumentation could already have been enabled;
- a context manager had already been constructed and enabled;
- the context manager was not globally registered and was not disabled;
- the returned no-op shutdown function could not reach either side effect.

The return value therefore overstated the amount of rollback performed.

## First implementation and self-review defect

The first fork implementation moved instrumentation registration until after component creation and global publication.

That fixed the component-creation path, but exact-head self-review found a new failure mode:

1. create trace, metric, log, context, and propagation components;
2. publish those components through process-global APIs;
3. call user-controlled instrumentation provider setters and `enable()`;
4. an instrumentation throws;
5. `startNodeSDK()` exits without returning a shutdown handle;
6. the newly published global providers remain installed.

The first implementation could therefore leak globally reachable providers on instrumentation-registration failure.

## Repaired ordering

The current fork head uses this sequence:

1. create SDK components;
2. register supplied instrumentations against those newly created trace, metric, and log providers explicitly;
3. if registration throws, disable the created context manager, start provider shutdown, and rethrow the original registration error;
4. only after registration succeeds, publish context, trace, metric, log, and propagation globals;
5. return the shutdown handle.

This preserves the original synchronous throw behavior for instrumentation failures while preventing the helper from publishing globals that the caller cannot later shut down.

Representative source shape:

```ts
try {
  registerInstrumentations({
    instrumentations: sdkOptions?.instrumentations?.flat() ?? [],
    loggerProvider: components.loggerProvider,
    meterProvider: components.meterProvider,
    tracerProvider: components.tracerProvider,
  });
} catch (registrationErr) {
  cleanupComponents(components);
  throw registrationErr;
}

// Process-global publication occurs only after registration succeeds.
```

## Why registration receives explicit providers

Registering before global publication would otherwise make `registerInstrumentations()` read the previous process globals.

Passing the newly created providers explicitly gives instrumentation the same provider objects the helper intends to publish without requiring those providers to become globally visible first.

This is particularly important for metrics because the metrics API does not provide the same proxy-retargeting behavior as tracing and logs.

## Why the instrumentation disposer is not used

The current instrumentation disposer disables every supplied instrumentation.

An instrumentation may have been enabled before `startNodeSDK()` received it. Registration does not re-enable that instrumentation, but the disposer would still disable it. Calling the disposer in a catch path would therefore let failed SDK setup disable externally established instrumentation state.

The patch cleans up helper-created SDK components but does not claim rollback of arbitrary side effects performed inside a throwing instrumentation.

## Tests implemented

File:

`experimental/packages/opentelemetry-sdk-node/test/start-failure-cleanup.test.ts`

Cases:

1. a configuration that fails component creation returns `NOOP_SDK`, does not enable the supplied instrumentation, and disables the context manager created during the failed attempt;
2. an instrumentation that throws from `enable()` causes no global context-manager or tracer-provider publication and causes the newly created tracer provider to receive shutdown;
3. successful component setup still registers and enables the supplied instrumentation.

## Scope

This patch does not solve:

- partial side effects inside an instrumentation that itself throws;
- repeated successful calls to `startNodeSDK()`;
- global registration result handling;
- provider cleanup when a later global registration is rejected;
- ownership-aware instrumentation disposal during normal shutdown;
- shutdown-error aggregation or asynchronous cleanup completion;
- a `MeterProvider` constructor that binds some readers before a later reader throws;
- trace-provider shutdown state.

## Review disposition

Work class: upstream-fork research.

Evidence class:

- production and test source: `source-read`;
- regression test: `target-test-prepared`;
- target execution: not retained.

Disposition: `EXECUTE` before promotion.

The branch is current against its pinned fork base, but repository dependencies are unavailable in the current work environment and no GitHub Actions run is visible for the fork head.

## Validation

```bash
npm ci
npm run compile
npm test --workspace=@opentelemetry/sdk-node -- --grep "startNodeSDK failure cleanup"
```

No test pass is claimed.

## Contact boundary

The implementation exists only in the user-owned fork. No upstream issue, pull request, comment, review, reaction, or direct backlink was created.
