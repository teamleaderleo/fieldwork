# Upstash Box cancellation receipt target materialization

Issue: #388  
Parent comparison: PR #372  
Exact target: `upstash/box@b55d832d6e3ae0156e32d21ea3863e231dfff9cd`  
State: `target-executed / workflow-retirement`  
Upstream contact authorized: no

## In simple words

Exact target execution confirms a compatibility-preserving cancellation receipt can be shared across TypeScript, async Python, and generated synchronous Python without publishing a false terminal run state.

The selected repair keeps legacy `cancel()` return contracts, adds an explicit immutable request receipt, shares one at-most-once remote request across concurrent and later callers, and leaves `Run.status` unchanged until an authoritative server update arrives.

A complete-diff review found one compatibility edge after the first green generation: TypeScript aborted the current local observer only when it created the shared remote request. A later observer attached after settlement would receive the cached receipt without being aborted. The repaired target now aborts the currently attached local observer on every `requestCancel()` or `cancel()` call while still issuing the remote cancellation request at most once.

All execution used mocked/local requests. No hosted Box API call, account, credential, payment, or private data was involved.

## Exact identities

- exact target-executed Fieldwork head: `1e7909da440ab631fcea11d4d3777d2bce107277`;
- exact target checkout: `b55d832d6e3ae0156e32d21ea3863e231dfff9cd`;
- workflow run: `30642924979`;
- job: `91197101877`;
- Fieldwork integrity: `30642923423`, success;
- artifact: `8798217638`;
- artifact digest: `sha256:5629a4706772b989c0ed2a88689569572d8c231eb23a19f468ed101adff1c3b4`;
- exact target diff SHA-256: `d30874c96f8e39350b9d725c58a6034554c561b073cb04969849ff2778c09e88`;
- durable receipt: `upstash-box-cancel-receipt.json`;
- checkout classification: `exact-head`.

The uploaded receipt recorded actual and expected Fieldwork and target heads as equal, target checkout match `true`, technical gate status `success`, evidence class `target-executed-local-mocked`, hosted-provider call `false`, and credentials used `false`.

The earlier green run `30641892410` and artifact `8797795255` remain historical evidence for the pre-review generation. They are superseded for promotion by the exact repaired generation above.

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
- no automatic remote-request replay.

`accepted` means the local HTTP request completed successfully. It does not claim the remote run reached a terminal cancelled state.

## Runtime ownership

### TypeScript

One private Promise is assigned before remote request execution. Concurrent and later callers receive the same Promise and receipt object. Every call aborts the currently attached local observer, including observers attached after the shared receipt settled, without replaying the remote request.

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
- valid accepted receipt, fixed failure receipt, shared concurrent identity, no remote replay, no false terminal state, later authoritative status replacement, and repeated local-observer cancellation after receipt settlement were exercised.

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
- one shared remote request and receipt across concurrent callers;
- repeated local observer abort without remote replay;
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
