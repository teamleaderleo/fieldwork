# Upstash Box cancellation receipt target materialization

Issue: #388  
Parent comparison: PR #372  
Execution parent: PR #389 exact head `1e7909da440ab631fcea11d4d3777d2bce107277`  
Exact target: `upstash/box@b55d832d6e3ae0156e32d21ea3863e231dfff9cd`  
State: `target-executed / workflow-retirement`  
Upstream contact authorized: no

## In simple words

Exact target execution confirms a compatibility-preserving cancellation receipt can be shared across TypeScript, async Python, and generated synchronous Python without publishing a false terminal run state.

The selected repair keeps legacy `cancel()` return contracts, adds an explicit immutable request receipt, shares one at-most-once request across concurrent and later callers, and leaves `Run.status` unchanged until an authoritative server update arrives.

Repeated TypeScript calls still abort the currently attached local observer, including an observer attached after the shared provider request settled, while the provider request itself is not replayed. All execution used mocked/local requests. No hosted Box API call, account, credential, payment, or private data was involved.

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
- checkout classification: `exact-head`;
- pull-request event SHA: `6f6a93e27b1a77ab707189bcb19fcd41292f5b91`.

The uploaded receipt records equal actual and expected Fieldwork and target heads, target checkout match `true`, technical gate status `success`, evidence class `target-executed-local-mocked`, hosted-provider call `false`, and credentials used `false`.

The earlier run `30641892410` remains historical evidence for head `088ab886efad5fea2ac13df0cb5baa8e2776e550`. It does not carry forward to the later-observer TypeScript control or the generated-sync materialization correction without the replacement run above.

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
- no automatic provider-request replay.

`accepted` means the local request completed successfully. It does not claim the remote run reached a terminal cancelled state.

## Runtime ownership

### TypeScript

One private Promise is assigned before request execution. Concurrent and later callers receive the same Promise and receipt object. Every request method call aborts the currently attached local observer, but only the first call starts the provider request.

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
- accepted and failed receipts, concurrent identity, no replay, later-observer abort, no false terminal state, and later authoritative status replacement were exercised.

### Python

- focused async and cancellation-repair controls: 7/7 passed;
- full SDK suite: 185 passed, 12 deselected;
- sync generation executed twice and produced byte-identical non-empty diffs;
- JS/Python public parity: success;
- Ruff lint and formatting: success;
- MyPy: success on async client, generated sync client, cancellation coordinator, and public types;
- async shared request, cancelled-waiter survival, fixed failure prose, sync thread sharing, immutable frozen receipt, no replay, legacy `None`, and later authoritative status replacement were exercised.

## Target source shape

The generated target diff changes the TypeScript SDK, async Python source of truth, generated sync Python, public exports/types, parity documentation, and target-native tests.

The workflow-free Fieldwork carrier retains:

- fail-closed transformation scripts;
- TypeScript target-native controls;
- Python async/sync target-native controls;
- the exact current receipt and this report.

The transformation scripts require every source fragment to match exactly once before writing and therefore fail closed on target drift.

## Evidence boundary

Established for exact public source and local mocked execution:

- compatibility of the selected public API family;
- one shared provider request and receipt across concurrent callers;
- repeated TypeScript local-observer cancellation without provider replay;
- cancelled async waiter isolation;
- fixed failure diagnostics without provider response detail;
- no false terminal status;
- later authoritative status replacement;
- deterministic generated sync output;
- repository-declared TypeScript and Python tests, formatting, lint, typecheck, build, and parity gates.

Not established:

- hosted endpoint semantics or provider idempotency;
- whether a real remote run stops, continues, or completes naturally;
- server-side terminal outcome truth;
- billing or production concurrency behavior;
- public maintainer acceptance;
- merge or release readiness.

## Transition

The temporary target workflow is retired on the workflow-free successor after transferring the exact receipt above. Run workflow-free Fieldwork integrity, then complete the six-file review from compatibility, concurrency/cancellation, privacy/diagnostics, generator parity, and evidence-currentness perspectives.

The connected author account may provide technical self-review from those perspectives but cannot satisfy eligible independent acceptance.

No merge, release, deployment, account, credential, payment, private-data access, spending, or public-upstream interaction is authorized.
