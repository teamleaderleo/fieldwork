# cmux live journal resource-collapse result

## In simple words

The actual managed journal forwarder now has a measured scaling curve on the owned fork. Fake cmux-tui session sockets fed the real `journal_forwarder::start` path, while a local HTTP endpoint either ACKed immediately or accepted one POST and then stopped responding.

With the HTTP consumer stalled, resident memory rose from roughly 8.6 MiB at one session to 18.3 MiB at ten, 62.1 MiB at fifty, and 148.6 MiB at 128. Asking for 200 sessions stayed near 146.5 MiB because the source discovers at most 128 sessions. Every stalled run made exactly one HTTP request while all active producers completed their 300-record burst.

This is the source mechanism showing up in process memory: one shared POST owner is blocked while every session worker keeps feeding the shared pending pool.

The healthy 50-session control exposed an additional bend. It generated 15,000 records against an immediate loopback ACK server, yet the forwarder made only nine HTTP requests and reached about 103 MiB RSS. The nominal 100-record threshold therefore does not keep later busy-period batches near 100 records. Once the first POST owns the flusher, records can accumulate behind it; when the flusher regains control it drains the whole pending vector, and the later body-size split happens after that large retained set already exists.

## Execution receipt

Owned fork: `teamleaderleo/cmux`  
Branch: `fieldwork/nonlinear-resource-collapse`  
Workflow run: https://github.com/teamleaderleo/cmux/actions/runs/33552750156  
Job: `journal-runtime`  
Job ID: `100005989142`  
Checked-out head: `7757893fabe2a592b590443b78e8ef4a0e5d5da4`  
Pinned upstream ancestry base: `8ef183f1e5de765b183aec9d1799f17a0848ae84`  
Runner: Ubuntu 24.04.4

The harness compiled and executed successfully. Artifact `journal-runtime-results` was uploaded as artifact ID `9818282831` with six JSON result files.

## Harness

The live example creates resolver-compatible cmux-tui Unix sockets in a private temporary `XDG_RUNTIME_DIR`. Each fake session performs the same identity request and `session.journal.subscribe` exchange the forwarder expects, then emits real `stream_item` JSON envelopes.

The forwarder under test is the actual `chatmux_relay::journal_forwarder::start` implementation from the checked-out branch. The harness does not replace the pooling or HTTP code.

For this run each active session emitted:

- 300 journal records;
- 1,024-byte payload string per record;
- records as quickly as the Unix socket would accept them.

The HTTP modes were:

- `ack`: read each complete POST and immediately return HTTP 200 with an empty cursor map;
- `stall`: read the first complete POST and hold the connection until harness cancellation.

RSS came from `ps -o rss=`. FD count came from `/proc/self/fd` on Linux.

## Measured stalled curve

| Requested | Accepted | Generated records | HTTP requests | Baseline RSS KiB | Loaded RSS KiB | RSS delta KiB | Baseline FDs | Loaded FDs | Cleanup FDs |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | 1 | 300 | 1 | 4,920 | 8,572 | 3,652 | 14 | 18 | 12 |
| 10 | 10 | 3,000 | 1 | 4,756 | 18,332 | 13,576 | 23 | 45 | 12 |
| 50 | 50 | 15,000 | 1 | 4,900 | 62,072 | 57,172 | 63 | 165 | 12 |
| 128 | 128 | 38,400 | 1 | 5,080 | 148,568 | 143,488 | 141 | 399 | 12 |
| 200 | 128 | 38,400 | 1 | 5,220 | 146,456 | 141,236 | 213 | 471 | 12 |

At scale, the retained-memory slope is roughly 3.7–3.9 KiB of RSS per generated 1 KiB payload record after fixed process costs. That multiplier includes parsed `serde_json::Value` ownership, strings/containers, allocator overhead, and the in-flight HTTP batch. It is a measured process-level ratio for this harness, not a universal per-record constant.

The 128→200 plateau is the expected discovery cap. Requested fake session listener FDs still exist in the harness baseline at 200, which is why baseline and loaded FD counts continue upward even though accepted producer count stays at 128.

## Healthy control

Requested/accepted sessions: 50  
Generated records: 15,000  
HTTP requests: 9  
Baseline RSS: 4,988 KiB  
Loaded RSS: 103,016 KiB  
Cleanup RSS: 103,080 KiB  
Baseline FDs: 63  
Loaded FDs: 163  
Cleanup FDs: 12

The healthy control is important for two reasons.

First, the harness can complete real POST/ACK cycles and tear down descriptors. Loaded FDs drop to 12 after cancellation, below the pre-forwarder baseline because fake listener sockets and the HTTP server are closed as part of harness cleanup.

Second, an immediate local ACK still permits a large producer burst to outrun the single flusher. Fifteen thousand records produced only nine POSTs. This is consistent with the source sequence where one initial threshold batch occupies the flusher, `pool.pending` grows during that POST, and the next flush takes the entire pending vector. `post_with_retry` later splits over-size serialized bodies. The split occurs after the large record set has already been collected and cloned into batch state, which can explain why the healthy 50-session high-water RSS exceeds the stalled 50-session high-water.

## Cleanup interpretation

Descriptor cleanup converged cleanly in every run: 12 FDs remained after cancellation regardless of requested session count.

RSS did not return close to the initial `ps` value inside the same process. Cleanup RSS was approximately equal to loaded high-water RSS:

- stalled 1: 8,640 KiB;
- stalled 10: 18,400 KiB;
- stalled 50: 62,152 KiB;
- stalled 128: 148,648 KiB;
- stalled 200: 146,544 KiB;
- healthy 50: 103,080 KiB.

The live objects have strong cancellation ownership and the FD result shows their sockets close, while the allocator keeps the process high-water pages resident. This means post-cleanup RSS alone cannot distinguish leaked journal values from freed allocations retained by the allocator in this one-cycle harness. A repeated same-process cycle and/or allocator trim measurement is the next discriminator for reusable high-water versus still-live records.

For the performance invariant, the pre-cleanup curve is already enough to establish the amplification mechanism: retained process memory grows with aggregate producer records while one shared consumer is occupied, and the nominal batch threshold does not cap the pending pool.

## Failure threshold and first owner

Smallest source threshold: the first record arriving after the busy pending pool has already reached its threshold while `pool.flushing == true`.

Smallest measured scale in this harness: one session can accumulate beyond the first 100-record batch when the HTTP request stalls. The nonlinear operational risk appears as aggregate producer rate rises because all sessions share the same consumer.

The first owner whose resource count stops converging is `PoolState.pending` behind one `post_with_retry` owner.

The resource that saturates first is resident heap used by retained journal values/batches. Socket/FD counts scale with subscribed sessions but remain controlled and clean up deterministically.

## Consequence

Primary consequence: **memory pressure and growing journal-delivery lag**.

At sufficiently high producer volume or outage duration this can progress to allocator pressure, process memory exhaustion, and relay outage. Recovery can also be expensive because the large pending vector is converted into large batches and recursively split by body size after aggregation.

## Production repair now justified

The runtime result supports moving the memory bound to ingress instead of relying on the later HTTP body split.

A lossless repair should:

1. keep one bounded in-flight batch;
2. bound the shared pending pool by both record count and retained bytes;
3. when the busy pending pool reaches that bound, stop reading more journal stream items until the flusher drains capacity;
4. wake blocked session workers when pending records move into the next batch;
5. make cancellation wake blocked producers immediately;
6. preserve journal replay/cursor semantics instead of dropping events.

Backpressuring the Unix journal subscription is the preferred mechanism because the journal stream is the durable source; an in-memory drop would trade memory collapse for event loss.

## Evidence limits

The source sockets are protocol-faithful fake sessions rather than full cmux-tui daemon processes. The forwarder, pooling logic, retry path, HTTP client, session discovery, and cancellation path are production code.

This run measures one burst per process. It establishes high-water scaling and FD teardown; it does not yet establish whether repeated load/cleanup cycles ratchet RSS beyond the first allocator high-water.

The healthy control used an empty cursor map because cursor correctness was outside this resource test. That prevents durable cursor advancement but does not change the in-memory producer/consumer path exercised during the one burst.

Evidence label: **Executed / Observed runtime curve**.

Upstream remains read-only. Upstream contact authorization remains `false`.
