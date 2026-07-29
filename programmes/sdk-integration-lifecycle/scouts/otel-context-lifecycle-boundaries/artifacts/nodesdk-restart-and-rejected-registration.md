# NodeSDK restart and rejected-registration characterization

## Status

- Date: 2026-07-30
- Target revision: `7b06368b7362a30ca69c178f43bd94dfbb36f85d`
- Current upstream `sdk.ts` blob verified unchanged at check time
- Fork branch: `fieldwork/nodesdk-shutdown-lifecycle-characterization`
- Upstream contact: none

## Added executable characterization

The fork branch adds:

`experimental/packages/opentelemetry-sdk-node/test/lifecycle-restart-and-registration-failure-characterization.test.ts`

It covers three additional lifecycle cases.

## 1. Rejected context manager remains enabled

Two SDK instances are configured with separate tracking context managers.

1. SDK A enables and globally registers manager A.
2. SDK B enables manager B.
3. Global registration rejects B because A is already registered.
4. NodeSDK ignores the failed registration result.
5. SDK B shutdown does not call `disable()` on manager B.

The second manager is therefore enabled by NodeSDK even though it never becomes the global manager, and NodeSDK retains no cleanup handle for it.

The default AsyncLocalStorage manager has a no-op `enable()`, so this consequence is more important for custom managers whose enable operation allocates hooks or other runtime resources.

## 2. Same SDK restart leaves tracing on a shutdown provider

One SDK instance is started, used, shut down, and started again.

1. First start creates tracer provider A and installs it as the trace proxy delegate.
2. Shutdown closes A.
3. Second start creates provider B and stores B in `_tracerProvider`.
4. Duplicate global registration fails, so the trace proxy remains delegated to A.
5. New spans created through the global API still use shutdown provider A and are not exported.
6. A later NodeSDK shutdown targets B.

This is a same-object restart failure, separate from two SDK instances competing for globals.

## 3. Same SDK restart leaves logs on a shutdown provider

The equivalent log path has the same ownership split:

1. logger provider A is installed globally and then shut down;
2. restart constructs provider B and stores B privately;
3. the logs API retains global provider A;
4. later shutdown targets B.

## Consequence

The observed lifecycle now has three related but separable failure classes:

1. repeated `start()` before shutdown silently splits ownership for traces and logs and fails differently for metrics;
2. `start()` after `shutdown()` creates new private providers while globals remain attached to shutdown providers;
3. failed global registration can leave newly enabled custom components outside both global use and NodeSDK cleanup.

## Patch impact

An instance start-state guard fixes classes 1 and 2 by making one NodeSDK object single-start for its lifetime.

It does not fix class 3 when two separate SDK objects compete for globals. That broader case requires registration-result ownership and cleanup decisions.

## Recommended ordering

1. Promote the minimal instance start-state guard.
2. Add explicit documentation that one NodeSDK instance is single-start and not restartable unless a disposal lifecycle is introduced.
3. Follow with a separate registration-transaction campaign for multiple instances and failed global registration.

## Validation boundary

The tests are source-reviewed and committed. Full monorepo execution remains pending because the work environment cannot retrieve dependencies and no fork Actions jobs were visible at recorded checks.

No upstream issue, pull request, comment, review, reaction, or direct backlink was created.