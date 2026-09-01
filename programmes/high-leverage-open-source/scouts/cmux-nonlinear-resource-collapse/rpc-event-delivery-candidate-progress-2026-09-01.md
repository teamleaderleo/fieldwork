# cmux event-delivery candidate progress — 2026-09-01

Owned fork: `teamleaderleo/cmux`  
Branch: `fieldwork/nonlinear-resource-collapse`  
Upstream contact authorized: `false`

## Confirmed owner

The resource owner is the daemon client's decoded push-event fan-out, before downstream proxy or PTY output limits run. A blocked callback queue retained every offered 32 KiB event in both proxy and PTY tests:

- 1 MiB -> 32 callbacks
- 10 MiB -> 320 callbacks
- 50 MiB -> 1,600 callbacks
- 200 MiB -> 6,400 callbacks

Both 200 MiB blocked cases raised RSS from roughly 10 MiB to roughly 217 MiB. Healthy delivery finished with 0–3 callbacks pending at the measurement point.

## Candidate A: direct reservation around Dispatch callbacks

A first candidate reserves before `subscription.queue.async`, releases after the callback, and removes only the overflowing subscription.

Initial policy:

- 8 MiB / 4,096 events per subscription
- 64 MiB / 16,384 events per RPC client

Validation run `33568990950` passed its focused ownership tests and the full `CmuxRemoteDaemon` package (31 tests). This proves a simple admission budget can preserve subscription isolation and release accounting correctly.

Limitation: callbacks already submitted to an externally blocked Dispatch queue cannot be removed. The retained memory is bounded by the admission cap, but cleanup cannot purge that queued payload until the target queue runs.

## Candidate B: owned bounded delivery queue

A stronger candidate now owns undelivered events inside `RemoteDaemonEventDeliveryQueue<Event>` and schedules drains in batches of 16. Only one drain block is outstanding per subscription.

Important teardown behavior:

- overflow stops admission;
- queued payload entries are cleared immediately;
- the shared process budget is released immediately for those cleared entries;
- one terminal error is retained for ordered delivery;
- the overflowing stream/PTY subscription is removed without retiring neighboring subscriptions;
- future frames check the subscription before base64 decoding, so removed subscriptions stop producing new decoded `Data`;
- transport teardown cancels subscription delivery queues and releases queued reservations.

The drain block retains the delivery owner until it executes. This is necessary so removing the subscription mapping during overflow does not destroy the terminal error before it can be delivered.

### Storage-accounting repair

The first owned-queue version advanced an array head and decremented budget counters after delivery but left the delivered `Entry` in the backing array until the whole queue drained. That made accounting lower than actual retained payload.

`event_delivery_budget_candidate_storage_repair.patch` changes the backing store to `[Entry?]` and nils the consumed slot before running the handler. Cleared backlog slots are also nilled before the array is released. The budget now tracks actual retained payload slots closely rather than optimistic logical progress.

### Test repair

The initial full-package attempt (`33569293187`) reached the candidate source successfully, then failed in a test-only generic expression that tried to coalesce stream and PTY generic snapshot types. The source candidate compiled. A later patch converts each generic snapshot to one non-generic tuple before comparison/printing.

A second test was scheduler-sensitive: it expected a second 4-byte event to overflow while the target queue was free to drain the first event. Commit `17a1533ee15bf0f08352817184e3d8dac95cdfb3` adds an explicit delivery gate so overflow is deterministic before the queue is released. This keeps the unregister-without-deadlock check meaningful.

## Current candidate limits under evaluation

The owned-queue implementation currently uses:

- proxy subscription: 96 MiB / 65,536 events
- PTY subscription: 16 MiB / 16,384 events
- process-wide shared budget: 128 MiB / 131,072 events

These are conservative compared with measured healthy callback occupancy. The next executed gate is a 200 MiB healthy/blocked run for both stream and PTY. The decision after that run is whether to retain these generous local ceilings while relying on the 128 MiB shared breaker, or lower the ceilings toward the earlier 8/64 MiB policy.

## Landing rule

Do not promote either event-delivery candidate into production source until the owned-queue version passes:

1. full `CmuxRemoteDaemon` package;
2. 200 MiB healthy stream and PTY controls;
3. 200 MiB blocked stream and PTY cases with queued payload released at overflow;
4. cleanup with shared budget back at zero;
5. identity/isolation tests showing only the overflowing subscription is retired.

After that, stack the already-green downstream proxy `NWConnection.send` budget behind it and run the remote-workspace slow-reader suite. The two bounds protect different owners and should remain independently testable.