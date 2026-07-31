# Upstash Box cancellation receipt target materialization

Issue: #388  
Parent comparison: PR #372  
Exact target: `upstash/box@b55d832d6e3ae0156e32d21ea3863e231dfff9cd`  
State: `target-executed / workflow-retirement`  
Upstream contact authorized: no

## In simple words

Exact target execution confirms a compatibility-preserving cancellation receipt can be shared across TypeScript, async Python, and generated synchronous Python without publishing a false terminal run state.

The selected repair keeps legacy `cancel()` return contracts, adds an explicit immutable request receipt, shares one at-most-once request across concurrent and later callers, and leaves `Run.status` unchanged until an authoritative server update arrives.

All execution used mocked/local requests. No hosted Box API call, account, credential, payment, or private data was involved.

## Exact identities

- exact target-executed Fieldwork head: `088ab886efad5fea2ac13df0cb5baa8e2776e550`;
- exact target checkout: `b55d832d6e3ae0156e32d21ea3863e231dfff9cd`;
- workflow run: `30641892410`;
- job: `91193643138`;
- Fieldwork integrity: `30641892400`, success;
- artifact: `8797795255`;
- artifact digest: `sha256:4cb0d91d25ba77472d260365df9c9a8786455b78d66bf3af9db8b78d71ed6fe0`;
- exact target diff SHA-256: `7860396fc6a3706c3322e936896656a261900d2d91718405c7393a19052ef626`;
- durable receipt: `upstash-box-cancel-receipt.json`;
- checkout classification: `exact-head`.

The uploaded receipt recorded actual and expected Fieldwork and target heads as equal, target checkout match `true`, technical gate status `success`, evidence class `target-executed-local-mocked`, hosted-provider call `false`, and credentials used `false`.

## Selected compatible API

Legacy contracts remain:

- TypeScript `cancel(): Promise<void>`;
- Python async/sync `cancel() -> None`.

New explicit receipt APIs:

- TypeScript `requestCancel(): Promise<RunCancellationReceipt>`;
- Python `request_cancel() -> RunCancellationReceipt`.

Receipt state:

- request state: `accepted | failed`;
- outcome state: always `unknown` locally;
- optional fixed diagnostic: `cancellation request failed`;
- immutable/frozen;
- shared across concurrent and later callers;
- no automatic replay.

`accepted` means the local request completed successfully. It does not claim the remote run reached a terminal cancelled state.

## Runtime ownership

### TypeScript

One private Promise is assigned before request execution. Concurrent and later callers receive the same Promise and receipt object. Abandoning one wait does not cancel the shared request.

### Async Python

One private `asyncio.Task` owns the request. Every waiter joins through `asyncio.shield`, so cancelling one waiter does not cancel the shared operation or prevent another waiter from receiving the receipt.

### Generated sync Python

One lock and shared `Future` select a single request owner. Other threads wait on the same result. The generator maps `AsyncCancellationCoordinator` to `SyncCancellationCoordinator` while continuing to generate the synchronous client from async source.

## Exact target results

### TypeScript

- focused existing plus Fieldwork controls: 21/21 passed;
- full SDK suite: 29 files, 385 tests passed;
- TypeScript build: success;
- repository package formatting/lint: success;
- valid accepted receipt, fixed failure receipt, shared concurrent identity, no replay, no false terminal state, and later authoritative status replacement were all exercised.

### Python

- focused async and cancellation-repair controls: 7/7 passed;
- full SDK suite: 185 passed, 12 deselected;
- sync generation executed twice and produced byte-identical non-empty diffs;
- JS/Python public parity: success;
- Ruff lint: success;
- Ruff format: success;
- MyPy: success on async client, generated sync client, cancellation coordinator, and public types;
- async shared request, cancelled-waiter survival, fixed failure prose, sync thread sharing, immutable frozen receipt, no replay, legacy `None`, and later authoritative status replacement were exercised.

## Target source shape

The generated target diff changes the TypeScript SDK, async Python source of truth, generated sync Python, public exports/types, parity documentation, and target-native tests.

The durable Fieldwork carrier retains:

- fail-closed transformation scripts;
- TypeScript target-native controls;
- Python async/sync target-native controls;
- this exact receipt and report.

The transformation scripts require every source fragment to match exactly once before writing and therefore fail closed on target drift.

## Evidence boundary

Established for exact public source and local mocked execution:

- compatibility of the selected public API family;
- one shared request and receipt across concurrent callers;
- cancelled async waiter isolation;
- fixed failure diagnostics without provider response detail;
- no false terminal status;
- later authoritative status replacement;
- no replay for later callers;
- deterministic generated sync output;
- repository-declared TypeScript and Python tests, formatting, lint, typecheck, build, and parity gates.

Not established:

- hosted endpoint semantics or provider idempotency;
- whether a real remote run stops, continues, or completes naturally;
- server-side terminal outcome truth;
- billing or production concurrency behavior;
- public maintainer acceptance;
- merge or release readiness.

## Final transition

Retain the scripts, controls, durable receipt, exact run/artifact identities, and target-diff hash. Remove the temporary execution workflow, run workflow-free Fieldwork integrity, then perform complete-diff review from compatibility, concurrency/cancellation, privacy/diagnostics, generator parity, and evidence-currentness perspectives.

The connected author account may provide technical self-review from those perspectives but cannot satisfy eligible independent acceptance.

No merge, release, deployment, account, credential, payment, private-data access, spending, or public-upstream interaction is authorized.
