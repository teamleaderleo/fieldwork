# cmux remote-daemon notification write residual

## In simple words

The first production candidate on the owned cmux fork bounds ordinary request/response RPC calls across write admission, physical write, and response wait. That repair does not yet cover daemon notifications.

The remaining notification path is especially relevant to PTY traffic because `writePTY` and `resizePTY` call the synchronous `notify` helper. `notify` encodes a frame and enters the same global `RemoteDaemonRPCClient.writeQueue` with `writeQueue.sync { writePayload(...) }`. It has no response phase and therefore no per-call response timeout to eventually take ownership of a stalled transport.

A transport that remains alive while ceasing to read can therefore still make one notification occupy the physical write lane. Later request/response RPC calls are now expected to time out while waiting for that lane and stop the transport under the candidate fix, so a mixed workload may recover. A workload made only of notifications can still accumulate blocked producers until another liveness owner acts.

This is an open residual, not a confirmed post-fix collapse result yet.

## Exact owner

Target source file:

`Packages/macOS/CmuxRemoteDaemon/Sources/CmuxRemoteDaemon/Client/RemoteDaemonRPCClient+RPC.swift`

Relevant path:

- `writePTY(...)` builds parameters and calls `notify(method: "pty.write", ...)`;
- `resizePTY(...)` calls `notify(method: "pty.resize", ...)`;
- `notify(...)` encodes the frame;
- `notify(...)` synchronously enters the process-wide RPC client's serial `writeQueue`;
- `writePayload(...)` performs the transport write.

The macOS PTY bridge adds a natural producer multiplier. Each bridge session owns its own RPC queue, so multiple sessions can independently arrive at the same shared daemon write queue. Input buffering is capped per bridge, which limits bytes owned by one bridge, but many bridges can each retain one blocked producer behind the same transport owner.

## Why the current request fix helps only partially

Fork candidate commit:

`843accd73070a441ae4d24aa88e1a21bbbe02bc7`

Ordinary `call(...)` now computes an absolute deadline at entry, waits asynchronously for the write queue/physical write until that deadline, and stops the transport if the write phase misses it. That means a later ordinary call can act as a breaker for an earlier stalled notification.

Pure notification traffic has no equivalent local deadline yet. The non-WebSocket keepalive also needs to enter `writeQueue` before it can arm its own watchdog, so a notification already holding the queue can keep the keepalive from becoming the breaker.

## Next discriminator

Add a serialized macOS test using the same fake SSH transport as the request scaling probe:

1. complete `hello`;
2. helper remains alive and stops reading stdin;
3. issue PTY notification payloads from 1 / 10 / 50 / 200 producer contexts;
4. measure how many producers remain incomplete after a fixed bounded interval;
5. invoke `client.stop()` and require every producer plus the physical writer to release promptly;
6. run the same producer sequence against the responsive helper as the negative control.

A stronger realistic variant should use PTY-sized chunks instead of a synthetic multi-megabyte payload so the first observed knee represents the actual bridge producer size.

## Repair thesis if reproduced

Move physical-write liveness ownership below the distinction between calls and notifications. The transport write layer should have one bounded write-admission/write deadline shared by both paths. For request/response calls, the configured RPC deadline remains the overall call budget. For fire-and-forget notifications, a dedicated transport-write deadline should stop an unresponsive transport and return an error to the caller.

The existing timed-out PTY-attach cancellation path already contains a close cousin: it queues a cancellation write asynchronously and arms a one-second watchdog; failure to clear the write lane stops the transport. Any generic notification repair should preserve current wire frames and reuse the same ownership philosophy.

## Evidence label

- Notification owner and absence of a local write deadline: **Observed in source**.
- Multi-session amplification path: **Inferred from independent bridge RPC queues feeding one shared daemon write queue**.
- Post-request-fix runtime consequence: **Unknown until the dedicated notification scaling probe executes**.

Upstream remains read-only. Upstream contact authorization remains `false`.
