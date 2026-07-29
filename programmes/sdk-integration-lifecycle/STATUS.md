# SDK Integration and Lifecycle

## In simple words

Map where SDK state and contracts fail across streaming, retries, cancellation, transports, types, persistence, and observability. Scouts should return concrete branch candidates, not general SDK summaries.

- Programme hub: #13
- State: `ready`
- Coordinator: unclaimed
- Upstream contact: unauthorized

## Ready scouts

- #17 — Vercel AI SDK streaming and tool lifecycle
- #18 — Workers SDK local, test, and deployment lifecycle
- #19 — OpenTelemetry async context and retry correlation
- #20 — MCP transport and session lifecycle
- #21 — Supabase client and runtime contracts

## Current decision

The scouts may run independently. Open child campaigns only after a handoff identifies a concrete behavior or missing capability, consequence, likely owning boundary, and falsifiable next question.
