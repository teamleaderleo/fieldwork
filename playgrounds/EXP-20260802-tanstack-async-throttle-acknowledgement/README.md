# TanStack Query async-throttle acknowledgement

## State

`COMPLETE — candidate technically accepted; public contact unauthorized`

Owner: `chatgpt:gpt-5.6-thinking`  
Created: `2026-08-02`  
Claim scope: mechanism  
Public upstream contact authorized: `no`

## Bounded question

When the async storage persister coalesces a save into an already scheduled execution, does the coalesced caller's returned promise wait for the latest arguments to be written?

## Exact subject

- public and fork base: `31c7f374e28081289ea4d3fae46a0792fc56e737`;
- characterization: `teamleaderleo/query#1@fd462d0453caf0a1d8c4f687de0578d28e87b109`;
- accepted source candidate: `teamleaderleo/query#2@02fc79ee3ca4597c667d16bfa955b9af4da68c5c`;
- retired execution carrier: `teamleaderleo/query#3@23aad017e91aa14536b083941eb6226b6fd21df6`;
- source fence: throttle implementation, focused target-native test, and patch changeset.

## Why this matters

`persistQueryClientSave()` awaits `persister.persistClient()`. The shipped async storage persister implements `persistClient()` with `asyncThrottle()` around serialization and `storage.setItem()`.

The original `asyncThrottle()` retained the latest arguments behind an `isScheduled` boolean. A call made while a later execution was already scheduled updated `lastArgs` and returned from the async wrapper immediately. Its snapshot was eventually executed by the earlier scheduled caller, but its own promise had already resolved.

That is a false completion acknowledgement: awaiting a save can finish before that call's selected snapshot reaches storage.

## Characterization

The target-native test holds execution 1, schedules value 2, then coalesces value 3. Under the original implementation, the value-3 caller settles while only value 1 has executed. After release, the physical executions are `[1, 3]`.

The defect concerns completion ownership, not write serialization: the original implementation already serializes physical executions and selects the latest pending arguments.

## Selected repair

Each pending execution generation owns one exact shared promise.

- calls coalesced before execution receive the same promise and update that generation's latest arguments;
- the shared promise settles only after those selected arguments execute;
- once execution begins, a new call creates one independent later generation;
- the later generation waits for actual current-execution completion, then observes the existing post-completion throttle interval;
- function failures still flow through the existing `onError` boundary;
- the public API remains unchanged.

Changed target files:

- `.changeset/fuzzy-rivers-wait.md`;
- `packages/query-async-storage-persister/src/asyncThrottle.ts`;
- `packages/query-async-storage-persister/src/__tests__/asyncThrottleAcknowledgement.test.ts`.

## Repair history

The first promise-based candidate deferred initial execution through a microtask. It passed the new acknowledgement checks but failed the repository's existing long-execution throttle control by collapsing `[first, latest]` into only `[latest]`.

The accepted source starts the scheduler immediately after assigning a captured deferred promise. This preserves first-call ownership while allowing calls during execution to create one later coalesced generation.

Two execution-carrier defects were also repaired without entering the source fence:

- pnpm cache setup originally ran before pnpm was installed;
- shallow merge checkout originally made the exact candidate-base check unreliable.

## Exact execution

Focused execution carrier run `30830369287`, job `91742521649`, passed:

- exact candidate-base verification;
- Ubuntu 24.04, Node 22, pnpm 11.9.0;
- frozen-lockfile installation;
- formatting of the source, existing test, new test, and changeset;
- all existing and new async-throttle tests;
- package ESLint;
- current TypeScript checking.

Ordinary source PR run `30830372063` also completed:

- affected `Test` job `91742530383`: passed;
- `Version Preview` job `91742530529`: passed;
- `Preview`: package build passed, publication failed at the fork-only preview publishing step.

The execution carrier is closed without merge. The candidate source contains no workflow file.

## Review

Exact-head complete-diff review `4846283466` examined the three-file candidate at `02fc79ee...` against base `31c7f374...` and recorded `ACCEPT — technically ready for owner/human review`.

That review confirms the source mechanism and evidence boundary. It is same-account technical review and does not claim human review or authorize public filing.

## Local executable model

The retained dependency-free model remains useful for the original acknowledgement distinction:

```sh
node playgrounds/EXP-20260802-tanstack-async-throttle-acknowledgement/model.mjs
```

Its earlier output demonstrates the original caller settling before the coalesced execution and the candidate caller remaining pending. Target-native execution above is the controlling evidence for the accepted source.

## Limits and next transition

Established:

- original false completion acknowledgement;
- exact shared-promise identity for one pending generation;
- independent later-generation ownership;
- preservation of the existing long-execution throttle behavior;
- formatting, focused tests, lint, TypeScript, affected checks, and version-preview compatibility.

Still required immediately before any authorized public filing:

- refresh public main and duplicate/prior-art state;
- read current TanStack contribution and disclosure policy;
- confirm the candidate head and three-file fence have not moved;
- obtain the owner's exact public-contact authorization.

No public issue, pull request, comment, review, reaction, release, or deployment was created in the canonical upstream repository.
