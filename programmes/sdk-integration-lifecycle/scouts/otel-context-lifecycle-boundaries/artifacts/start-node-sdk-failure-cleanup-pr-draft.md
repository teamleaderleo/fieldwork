# Fix PR draft and fork trial: clean up failed startNodeSDK setup

## Status

- Draft implemented in user-owned fork: https://redirect.github.com/teamleaderleo/opentelemetry-js/pull/3
- Branch: `fieldwork/start-node-sdk-failure-cleanup`
- Base: `7b06368b7362a30ca69c178f43bd94dfbb36f85d`
- Initial source commit: `2ed8f4b846fc4a62d0e724e43264e7036d7065e7`
- Initial test commit: `3f79d0d93155edd82174d161caafd650aefdcfd7`
- Global-publication ordering repair: `b7992b4e412a66f15bd4035bb7b47ad967586c39`
- Registration-failure regression: `482cb975f78572bc65a9b263fb677b7a274e2fff`
- Cleanup error-preservation source: `7761527e910328fcfa26a089a070f0700a56c25d`
- Cleanup error-preservation tests and current head: `2482d8c49c8b6e01a282a36da55e48b4a4dc8747`
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

That fixed the component-creation path but introduced another failure:

1. create trace, metric, log, context, and propagation components;
2. publish those components through process-global APIs;
3. call user-controlled instrumentation provider setters and `enable()`;
4. an instrumentation throws;
5. `startNodeSDK()` exits without returning a shutdown handle;
6. the newly published globals remain installed.

## Repaired ordering

The current fork uses this sequence:

1. create SDK components;
2. register supplied instrumentations against the newly created trace, metric, and log providers explicitly;
3. if registration throws, clean up helper-created components and rethrow the registration error;
4. only after registration succeeds, publish context, trace, metric, log, and propagation globals;
5. return the shutdown handle.

Passing the newly created providers explicitly gives instrumentation the provider objects the helper intends to publish without exposing them globally before registration succeeds. This is especially important for metrics, whose API does not provide the same proxy retargeting behavior as tracing and logs.

## Cleanup error-preservation repair

A later self-review found that `cleanupComponents()` could still corrupt failure reporting:

- `contextManager.disable()` or a provider `shutdown()` could throw synchronously and replace the primary setup error;
- a rejected provider shutdown promise was ignored and could become an unhandled rejection;
- one cleanup failure could prevent later components from receiving cleanup.

The current helper treats rollback as best effort while preserving the primary error:

```ts
try {
  components.contextManager?.disable();
} catch (cleanupErr) {
  diag.error('Could not disable failed SDK context manager', cleanupErr);
}

safelyShutdownComponent('tracer provider', () =>
  components.tracerProvider?.shutdown()
);
```

`safelyShutdownComponent()` catches synchronous throws and attaches a rejection handler to asynchronous shutdown. Cleanup errors are reported through diagnostics and do not replace the component-creation or instrumentation-registration failure that caused rollback.

The synchronous helper still cannot wait for asynchronous cleanup completion before returning `NOOP_SDK` or rethrowing registration failure.

## Why the instrumentation disposer is not used

The current instrumentation disposer disables every supplied instrumentation.

An instrumentation may have been enabled before `startNodeSDK()` received it. Registration does not re-enable that instrumentation, but the disposer would still disable it. Calling the disposer in a catch path would therefore let failed SDK setup disable externally established instrumentation state.

The patch cleans up helper-created SDK components but does not claim rollback of arbitrary side effects performed inside a throwing instrumentation.

## Prepared tests

File:

`experimental/packages/opentelemetry-sdk-node/test/start-failure-cleanup.test.ts`

Cases:

1. component creation failure returns `NOOP_SDK`, does not enable supplied instrumentation, and disables the created context manager;
2. instrumentation registration failure publishes no global context manager or tracer provider and requests tracer-provider shutdown;
3. synchronous provider cleanup failure is reported without replacing the registration error;
4. rejected asynchronous provider cleanup is observed without replacing the registration error;
5. context-manager cleanup failure is reported and does not prevent later provider cleanup;
6. successful setup still registers and enables supplied instrumentation.

## Scope

This patch does not solve:

- partial side effects inside an instrumentation that itself throws;
- waiting for asynchronous cleanup completion before the synchronous helper returns or throws;
- repeated successful calls to `startNodeSDK()`;
- global registration result handling or partial process-global publication;
- provider cleanup when a later global registration is rejected;
- ownership-aware instrumentation disposal during normal shutdown;
- a `MeterProvider` constructor that binds some readers before a later reader throws;
- provider shutdown state and aggregate fanout contracts.

## Review disposition

Work class: upstream-fork research.

Evidence class:

- production and test source: `source-read`;
- regression tests: `target-test-prepared`;
- target execution: not retained.

Disposition: `EXECUTE` before promotion.

## Validation

```bash
npm ci
npm run compile
npm test --workspace=@opentelemetry/sdk-node -- --grep "startNodeSDK failure cleanup"
```

No test pass is claimed.

## Contact boundary

The implementation exists only in the user-owned fork. No upstream issue, pull request, comment, review, reaction, or direct backlink was created.
