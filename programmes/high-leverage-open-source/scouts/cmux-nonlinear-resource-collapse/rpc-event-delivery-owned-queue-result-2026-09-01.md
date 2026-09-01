# cmux owned event-delivery queue result — 2026-09-01

Owned fork: `teamleaderleo/cmux`  
Branch: `fieldwork/nonlinear-resource-collapse`  
Upstream contact authorized: `false`

## Candidate

The preferred candidate replaces one unbounded `DispatchQueue.async` callback per decoded proxy/PTY event with an owned `RemoteDaemonEventDeliveryQueue<Event>`.

The queue:

- owns undelivered payload until a subscriber can run;
- schedules at most one drain block at a time;
- drains in batches of 16;
- applies a per-subscription byte/event ceiling and one process-wide shared ceiling;
- clears queued payload immediately on overflow or cancellation;
- nils consumed backing-array slots before handler execution so counters track actual retained payload rather than logical progress;
- retains one terminal failure for ordered delivery;
- removes an overflowing or terminal subscription from the RPC map before terminal callback execution;
- guards subscription lookup before base64 decode, so frames arriving after retirement no longer create decoded `Data`.

Current candidate limits under evaluation:

- proxy subscription: 96 MiB / 65,536 events
- PTY subscription: 16 MiB / 16,384 events
- shared process budget: 128 MiB / 131,072 events

## Full-package gate

Run: `33570183838`  
Job: `100062226955`  
Head: `13e41e79ad3c1bbcb1d8ea7b7ffdd8ef840de710`

Result: success.

The complete `CmuxRemoteDaemon` package passed 34 tests with the candidate layered over the fork. Deterministic tests covered FIFO terminal ordering, byte/event admission, immediate payload release before a blocked target queue resumes, cancellation without stale handler delivery, timeout-isolation compatibility, and overflow-handler unregister behavior.

## 200 MiB scaling result

Payload: 32 KiB/event, 6,400 events.

| Kind | Consumer | Baseline RSS | Loaded RSS | Handled data | Terminal errors | Owner pending after load |
| --- | --- | ---: | ---: | ---: | ---: | --- |
| proxy stream | healthy | 10,336 KiB | 215,632 KiB | 6,400 | 0 | 0 bytes / 0 events |
| proxy stream | blocked | 10,064 KiB | 109,424 KiB | 0 | 1 after release | 0 bytes / 0 events |
| PTY | healthy | 10,288 KiB | 215,632 KiB | 6,400 | 0 | 0 bytes / 0 events |
| PTY | blocked | 10,320 KiB | 26,912 KiB | 0 | 1 after release | 0 bytes / 0 events |

The blocked stream stopped accepting events at the 96 MiB local ceiling; the blocked PTY stopped at the 16 MiB local ceiling. Overflow purged admitted-but-undelivered payload immediately, leaving one small queued terminal event and zero shared/local payload reservations while the target queue remained blocked.

The immediate-retirement repair is visible in RSS and submit time. Before it, the same blocked 200 MiB synthetic loop continued decoding later frames after overflow and ended near 216 MiB RSS. With the map retired before terminal callback delivery, blocked proxy RSS was ~109 MiB and blocked PTY RSS ~27 MiB, and the PTY loop completed in ~96 ms instead of ~844 ms. Future frames return before base64 decode once the subscription is gone.

## RSS interpretation

Healthy 200 MiB cases still finish near ~216 MiB RSS despite zero queued payload because the synthetic test deliberately decodes 200 MiB sequentially in one process and the macOS allocator keeps that high-water. The owner counters are the direct retention metric for this layer. The blocked cases provide the stronger resource discriminator because retirement stops most later decode work.

## Remaining gate before source promotion

A PTY-specific deterministic retirement test is staged on the fork to mirror the existing stream assertion: the attachment must disappear from `ptySubscriptions` while its callback queue is still blocked, before terminal error delivery.

A composition workflow is also staged to apply both independent bounds in one checkout:

1. the RPC decoded-event delivery queue;
2. the downstream `RemoteDaemonProxySession` `NWConnection.send` byte/send budget and loopback response-header ceiling.

That workflow runs full `CmuxRemoteDaemon`, full `CmuxRemoteWorkspace`, a healthy 200-session proxy control, and both per-session and process-wide slow-reader breakers. Production promotion stays behind those gates.