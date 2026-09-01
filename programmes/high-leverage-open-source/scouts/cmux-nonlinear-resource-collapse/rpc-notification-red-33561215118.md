# cmux PTY notification write-lane red

Date: 2026-09-01
Worker: ChatGPT
Upstream contact authorized: `false`
Owned fork: `teamleaderleo/cmux`
Red run: `33561215118`
Red head: `ddbcecd6d34a7415c02e226dd1b2b97e8c433989`

## In simple words

After the request/response write-liveness candidate was green, the remaining fire-and-forget notification path reproduced the same global stdio write-lane failure independently. A PTY write has no response phase and therefore no later response timeout that can retire the transport. If the remote helper remains alive while ceasing to read stdin, one realistic bridge-sized PTY notification can block its caller indefinitely and every later notification caller queues behind the same physical writer.

## Exact probe

The probe uses the existing `RemoteDaemonRPCClient.writePTY` path. The fake helper answers startup `hello`, then remains alive for ten seconds while refusing further stdin.

Each PTY notification carries a 256 KiB raw payload. `RemotePTYBridgeInputFlow` already uses 256 KiB as its default single-write ceiling, so this payload represents an allowed bridge write rather than a synthetic multi-megabyte RPC.

The scaling sequence is 1 / 10 / 50 / 200 concurrent `writePTY` callers. Each caller waits only for local notification-write completion; no ordinary request/response RPC is introduced to rescue the transport.

The convergence bound is 1.75 seconds. When a case misses that bound, the harness invokes direct `client.stop()` and requires all notification callers to unwind within another second. This is the clean-shutdown control.

## Red result

Run `33561215118`:

- request/response package gate outside the known upstream-parallel-flaky timeout suite: passed;
- both timeout-isolation tests executed alone: passed;
- request/response physical-write 1/10/50/200 sequence: passed;
- notification-only PTY write sequence: failed at every tested population.

Failures:

- N=1: notification writer remained beyond 1.75 s;
- N=10: all notification work remained governed by the same wedged lane;
- N=50: same;
- N=200: same.

The full notification test completed in 7.164 s because each failed case used direct transport teardown as its cleanup breaker rather than waiting for the helper's ten-second safety exit.

## Owner and consequence

Operation owner: `RemoteDaemonRPCClient.notify` → `writeQueue.sync` → synchronous stdio `FileHandle.write`.

Bridge caller owner: `RemotePTYBridgeSession` sends each reserved input write on its per-bridge `rpcQueue`, which calls `RemoteDaemonRPCClient.writePTY` synchronously.

Bridge-side input memory has independent limits (256 pending writes / 4 MiB pending bytes), but those limits do not give the daemon transport write a deadline. One blocked notification pins the bridge RPC worker and the shared daemon write lane; more bridges or callers add waiting work behind the same lane.

Consequence: stranded bridge workers and remote terminal input, duplicated waiting work during reconnect/replacement, and eventual thread/work-item pressure as logical attachments multiply.

## Candidate direction

The owned fork already has a one-second non-WebSocket write-liveness helper for request/response calls. The next candidate applies that same owner to notifications while preserving the WebSocket path. On liveness expiry it retires the transport and surfaces a write error to `writePTY` completion / resize callers, allowing bridge cleanup and reconnect ownership to proceed.

## Evidence limits

- This is a GitHub-hosted macOS synthetic transport probe with a real `RemoteDaemonRPCClient` and a fake helper process.
- It establishes local write-lane liveness and caller retention, not end-to-end remote terminal recovery behavior.
- The source-level `callIfIdle` keepalive write remains a separate lane entrypoint for follow-up.
- Upstream remained read-only; no maintainer contact occurred.
