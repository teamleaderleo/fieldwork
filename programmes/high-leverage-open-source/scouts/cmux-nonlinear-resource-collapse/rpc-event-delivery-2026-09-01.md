# cmux RPC event-delivery retention — 2026-09-01

Worker: ChatGPT  
Upstream contact authorized: `false`  
Owned fork: `teamleaderleo/cmux`  
Experiment branch: `fieldwork/nonlinear-resource-collapse`  
Original upstream audit pin: `8ef183f1e5de765b183aec9d1799f17a0848ae84`

## Result

The remote daemon client has a second memory-retention layer before proxy/PTTY consumers enforce their own output limits.

`RemoteDaemonRPCClient` decodes `proxy.stream.data` and `pty.data` on its serial state queue, then submits one `subscription.queue.async` callback per event. There is currently no application-level byte or event ceiling on those queued callbacks. A slow or blocked subscriber can therefore retain decoded `Data` before `RemoteDaemonProxySession` or `RemotePTYBridgeSession` sees it.

## Proxy stream measurement

Run: `33567981998`  
Job: `100055426100`  
Measurement commit: `5d5038c1255b9e34860c0f4330b7086410ebed0c`

Payload size: 32 KiB/event.

Blocked callback queue:

| Offered data | Queued callbacks after submit | Baseline RSS | Loaded RSS |
| ---: | ---: | ---: | ---: |
| 1 MiB | 32 | 10,080 KiB | 11,200 KiB |
| 10 MiB | 320 | 9,936 KiB | 20,352 KiB |
| 50 MiB | 1,600 | 9,968 KiB | 61,744 KiB |
| 200 MiB | 6,400 | 10,096 KiB | 217,008 KiB |

Healthy callback queue stayed at 0–1 pending callback through 1/10/50/200 MiB offered. The 200 MiB healthy case submitted all 6,400 callbacks in about 860 ms and had zero callbacks pending at the measurement point.

## PTY measurement

Run: `33568393326`  
Job: `100056713196`  
Measurement commit: `4fe459d9970ea2eee8a4ffe6daebad8ca4e2cb66`

Payload size: 32 KiB/event.

Blocked callback queue:

| Offered data | Queued callbacks after submit | Baseline RSS | Loaded RSS |
| ---: | ---: | ---: | ---: |
| 1 MiB | 32 | 9,760 KiB | 10,832 KiB |
| 10 MiB | 320 | 10,016 KiB | 20,400 KiB |
| 50 MiB | 1,600 | 10,064 KiB | 61,840 KiB |
| 200 MiB | 6,400 | 10,064 KiB | 217,024 KiB |

Healthy PTY delivery stayed at 0–3 pending callbacks through the same scaling sequence. The blocked 200 MiB case retained all 6,400 callbacks and reproduced the proxy-stream curve almost exactly.

## Ownership conclusion

This is a shared `RemoteDaemonRPCClient` delivery-owner problem rather than a proxy-only problem. Downstream limits alone cannot bound retained bytes because the callback queue can accumulate decoded payload before downstream handlers execute.

The candidate repair should reserve capacity before `subscription.queue.async`, release it after the callback returns, and retire only the overflowing stream or PTY attachment. Future events for a retired subscription should avoid decoding payload data. Terminal error delivery should remain bounded and preserve ordered failure semantics.

Initial candidate ceilings to test:

- 8 MiB per subscription
- 4,096 queued events per subscription
- 64 MiB process-wide across remote event deliveries
- 16,384 queued events process-wide

These are deliberately above observed healthy callback occupancy while turning the blocked 200 MiB linear-retention sequence into a bounded failure. The already-tested downstream proxy candidate remains useful as defense in depth after this upstream owner is bounded.

## Evidence limits

The probes call the real event decode/delivery methods and real Dispatch queues on macOS, but use synthetic event payloads rather than a live remote daemon transport. The next gate should combine the shared delivery budget with the existing proxy slow-reader harness and PTY bridge tests, then run the complete `CmuxRemoteDaemon` and `CmuxRemoteWorkspace` packages.