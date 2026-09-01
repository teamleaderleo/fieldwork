# cmux PTY notification write-liveness candidate receipt

Date: 2026-09-01
Worker: ChatGPT
Upstream contact authorized: `false`
Owned fork: `teamleaderleo/cmux`
Candidate run: `33561533202`
Candidate head: `cc558390af891a0d98b0b1f25c8b0ff435bd26b4`

## In simple words

The same non-WebSocket write-liveness owner now covers both request/response RPCs and fire-and-forget daemon notifications. This closes the reproduced PTY-input case where one allowed 256 KiB notification could pin a bridge worker and the shared daemon write lane while the remote helper remained alive but stopped reading.

## Red-to-green sequence

Red run `33561215118` used 256 KiB `writePTY` payloads, matching the bridge's default maximum single write. With the helper refusing stdin after startup, notification-only populations of 1, 10, 50, and 200 callers all remained past a 1.75-second convergence bound. Direct `client.stop()` released each population.

Candidate commit `cc558390af891a0d98b0b1f25c8b0ff435bd26b4` routes non-WebSocket notifications through the existing one-second write-liveness helper. On expiry the client retires the transport and returns a write error to the notification caller. WebSocket notification behavior retains the existing path.

## Green gate

Run `33561533202`, GitHub-hosted macOS 15 arm64:

- package outside the known upstream-parallel-flaky timeout suite: **26 tests passed**, 2.195 s;
- preserve-after-PTY-timeout discriminator alone: **passed**, 0.247 s;
- blocked-cancellation discriminator alone: **passed**, 2.167 s;
- responsive 200-caller request control: **passed**, 1.259 s;
- physical request-write stall sequence 1 / 10 / 50 / 200: **passed**, 5.241 s;
- notification-only 256 KiB PTY-write stall sequence 1 / 10 / 50 / 200: **passed**, 4.561 s;
- complete focused scaling suite: **passed**, 11.064 s.

## Owner and consequence

The repaired owner is the process-wide serialized non-WebSocket daemon write lane. A physical stdio write now has a one-second liveness owner regardless of whether the caller expects an RPC response.

For PTY input, this means a bridge's bounded local input window can no longer strand its RPC worker indefinitely on one daemon notification. A write-liveness failure becomes a transport failure that bridge/reconnect ownership can observe and recover from.

## Remaining RPC edge

`callIfIdle` still enters `writeQueue.sync` directly. In ordinary use it carries a tiny keepalive `hello` and only registers when no application call is pending. A deterministic red would need a transport whose pipe has enough capacity for the preceding bounded application write to succeed but too little for the keepalive frame, making the keepalive itself the first blocked writer. That edge remains source-visible and unproven at runtime.

## Evidence limits

- The one-second write-liveness value is validated against these owned-fork scenarios, not a production latency distribution.
- The probe uses a synthetic helper process and real client code; end-to-end remote workspace recovery is outside this receipt.
- Upstream remained read-only; no maintainer contact occurred.
