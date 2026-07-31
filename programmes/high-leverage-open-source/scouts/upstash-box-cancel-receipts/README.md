# Upstash Box cancellation receipt probe

Parent finding: Fieldwork #329.

## Question

Does a failed remote cancellation request remain distinguishable from a server-confirmed terminal cancelled state, and do concurrent callers share one cancellation operation?

## Exact target

- repository: `upstash/box`;
- source head: `b55d832d6e3ae0156e32d21ea3863e231dfff9cd`;
- TypeScript SDK: `packages/sdk/src/client.ts`;
- Python source of truth: `packages/python-sdk/upstash_box/_async/client.py`.

## Current source prediction

Both SDKs:

1. attempt the remote cancellation request;
2. suppress request failure;
3. set local run status to `cancelled`;
4. create one independent request for each concurrent caller.

The TypeScript `cancel()` method also aborts any `AbortController` already attached to the run before the remote request settles.

## Controls

The carrier copies two test files into the exact target checkout.

Current-behavior controls assert:

- HTTP 500/503 does not reject `cancel()`;
- local status becomes `cancelled` after request failure;
- an attached TypeScript observer controller is aborted before cancellation settlement;
- concurrent callers send duplicate remote requests;
- the internal authoritative update path can later replace the local cancelled state with natural completion.

The controller and later-completion controls call the target's internal `Run._update` helper directly. They establish ordering and mutable-state mechanics. They do not independently execute the complete streaming parser or prove that a real hosted server event arrives after cancellation.

Strict reversing controls require a future repair to:

- avoid claiming terminal cancelled state after request failure;
- give concurrent callers one shared cancellation owner.

Vitest `it.fails` and strict pytest `xfail` keep those reversing controls executable while the exact current source still carries the defect. A repair that satisfies either control will intentionally turn this characterization carrier red until the expected disposition is updated.

## Evidence boundary

This probe uses repository-native mocks. It proves SDK request handling, attached-controller ordering, and local state transitions. It does not prove whether a real hosted Box run continues, stops, emits a later event, completes naturally, or incurs further cost after a cancellation request fails.

A hosted reproducer would require separate account, cost, and data authority. No credential, payment, private repository, hosted execution, or public upstream interaction is included here.
