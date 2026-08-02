# TanStack Query async-throttle acknowledgement

## State

`HOLD — target execution unavailable`

Owner: `chatgpt:gpt-5.6-thinking`  
Created: `2026-08-02`  
Claim scope: mechanism  
Public upstream contact authorized: `no`

## Bounded question

When the async storage persister coalesces a save into an already scheduled execution, does the coalesced caller's returned promise wait for the latest arguments to be written?

## Exact subject

- public source: `31c7f374e28081289ea4d3fae46a0792fc56e737`;
- fork main: fast-forwarded cleanly to that public head;
- characterization PR/head: `teamleaderleo/query#1` at `fd462d0453caf0a1d8c4f687de0578d28e87b109`;
- corrected candidate PR/head: `teamleaderleo/query#2` at `52fbc9824d628ef0e724a145ce4af06139c50d3f`.

## Why this matters

`persistQueryClientSave()` awaits `persister.persistClient()`. The shipped async storage persister implements `persistClient()` with `asyncThrottle()` around serialization and `storage.setItem()`.

Current `asyncThrottle()` retains the latest arguments behind an `isScheduled` boolean. A further call made while one later execution is already scheduled updates `lastArgs` and returns from the async wrapper immediately. Its snapshot is eventually executed by the earlier scheduled caller, but its own promise has already resolved.

This is a false completion acknowledgement: awaiting a save can complete before that call's latest snapshot reaches storage.

## Characterization

The target-native test holds execution 1, schedules value 2, then coalesces value 3. Before execution 1 is released:

- current code reports the value-3 caller settled;
- only value 1 has executed.

After release, current code executes `[1, 3]`.

Characterization file: `packages/query-async-storage-persister/src/__tests__/asyncThrottleAcknowledgement.test.ts`.

## Corrected candidate

The candidate replaces the boolean scheduled flag with the scheduled promise. Creation uses `Promise.resolve().then(...)` so the shared promise is assigned before scheduling begins.

- callers coalesced into one pending execution share its completion;
- latest-argument selection remains unchanged;
- one later execution can still be scheduled while a current execution is running;
- interval and error-callback behavior remain unchanged;
- public API shape is unchanged.

Changed files:

- `packages/query-async-storage-persister/src/asyncThrottle.ts`;
- `packages/query-async-storage-persister/src/__tests__/asyncThrottleAcknowledgement.test.ts`.

## Rejected first candidate

Initial candidate head `8c4fac973582b70159f4309eb2c5e12a7d1674af` used an immediately invoked async function. An isolated model showed assignment-order failure: the function cleared `scheduledPromise` before the outer assignment completed, then the first promise was reinstalled. Calls during the active execution therefore joined the active promise and no later execution was scheduled.

That head is rejected and superseded by `52fbc9824d628ef0e724a145ce4af06139c50d3f`.

## Local executable model

Command:

```sh
node playgrounds/EXP-20260802-tanstack-async-throttle-acknowledgement/model.mjs
```

Observed output at Node runtime in the work container:

```json
{"name":"current","beforeRelease":{"coalescedSettled":true,"executions":[1]},"after":{"executions":[1,3]}}
{"name":"candidate","beforeRelease":{"coalescedSettled":false,"executions":[1]},"after":{"executions":[1,3]}}
```

Evidence class: isolated executable model, not target-native execution.

## Prior art and exclusions

No equivalent current issue, pull request, or Fieldwork lane was found under the searched async-throttle, coalesced-promise, and persistence-acknowledgement terms. Repeat before promotion.

A broad stale-write claim was rejected because the shipped async persister already serializes and coalesces physical writes. This lane concerns the returned completion contract only.

Excluded:

- custom persister write serialization;
- restore cancellation and provider teardown;
- a new public flush API;
- public upstream interaction.

## Execution blocker

After synchronizing fork `main` and retargeting PRs 1–2, the fork still exposed no workflow runs or commit statuses. Local repository checkout also failed because the execution container could not resolve `github.com`, so dependencies and the Nx package target could not be run.

No target-executed pass is claimed.

## Required next gates

1. run the package-native async-storage-persister test target at the exact heads;
2. run format, lint, TypeScript, and affected build targets;
3. review the complete two-file candidate diff;
4. repeat prior-art and policy checks before any promotion.
