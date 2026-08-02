# TanStack Query async-throttle acknowledgement

## State

`HOLD — exact-head execution not yet available`

Owner: `chatgpt:gpt-5.6-thinking`  
Created: `2026-08-02`  
Claim scope: mechanism  
Public upstream contact authorized: `no`

## Bounded question

When the async storage persister coalesces a save into an already scheduled execution, does the coalesced caller's returned promise wait for the latest arguments to be written?

## Exact subject

- target: `TanStack/query`;
- pinned public source: `31c7f374e28081289ea4d3fae46a0792fc56e737`;
- clean fork base: `teamleaderleo/query:base/upstream-20260802`;
- characterization PR/head: `teamleaderleo/query#1` at `fd462d0453caf0a1d8c4f687de0578d28e87b109`;
- candidate PR/head: `teamleaderleo/query#2` at `8c4fac973582b70159f4309eb2c5e12a7d1674af`.

## Why this matters

`persistQueryClientSave()` awaits `persister.persistClient()`. The shipped async storage persister implements `persistClient()` with `asyncThrottle()`. Callers can therefore reasonably treat the returned promise as the completion of the requested durable save.

`asyncThrottle()` intentionally retains only the latest arguments. Current source uses a boolean `isScheduled`. If a scheduled execution already exists, another call updates `lastArgs` and returns from the async wrapper immediately. The existing scheduled call eventually executes the latest arguments, but the further coalesced caller has already received a resolved promise.

This creates a false acknowledgement: `await persistQueryClientSave()` can complete before the snapshot represented by that call reaches storage.

## Characterization

Target-native test: `packages/query-async-storage-persister/src/__tests__/asyncThrottleAcknowledgement.test.ts`.

Sequence:

1. first execution begins and is deliberately held;
2. second call schedules the next execution;
3. third call replaces the pending arguments;
4. third call's promise settles before the first execution is released;
5. the later scheduled run eventually executes the third arguments.

The characterization branch changes no production source.

## Candidate

The candidate replaces the boolean scheduled flag with the actual scheduled promise:

- the first caller creating a scheduled execution receives that promise;
- later callers coalesced into the same pending execution receive the same completion;
- `lastArgs` still selects the latest snapshot;
- calls arriving during an active execution may still schedule exactly one later execution;
- interval throttling and error callback behavior remain unchanged.

Changed files:

- `packages/query-async-storage-persister/src/asyncThrottle.ts`;
- `packages/query-async-storage-persister/src/__tests__/asyncThrottleAcknowledgement.test.ts`.

Public API shape is unchanged.

## Prior-art and scope

Searches on `2026-08-02` found no equivalent current issue, pull request, or Fieldwork lane under the searched async-throttle, coalesced-promise, and persistence-acknowledgement terms. Repeat before promotion.

The standard async persister already serializes and coalesces physical writes, so a broad stale-write claim against the shipped persister was rejected. This experiment is specifically about the completion contract returned to callers.

Excluded:

- custom persisters that independently allow overlapping writes;
- core restore cancellation and provider teardown;
- changing throttling interval or coalescing policy;
- adding a new public flush API;
- public upstream interaction.

## Execution state

Opening fork-local PRs 1 and 2 did not yet produce workflow runs visible to the GitHub connector. No pass or failure is inferred from the empty run list.

Required gates:

1. `pnpm nx run @tanstack/query-async-storage-persister:test:lib` or the repository-equivalent package target;
2. formatting, lint, and TypeScript for the changed package;
3. complete source diff review;
4. ordinary repository CI actually triggered for the exact candidate head.

## Stop condition

Stop after the exact characterization and candidate tests execute and the two-file candidate diff is reviewed. Do not widen into general persister durability APIs without separate evidence.
