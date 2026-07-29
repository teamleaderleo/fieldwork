# SDK Behaviour and Integration

## In simple words

Map each SDK's architecture, public contracts, internal state, tests, service or provider boundaries, and realistic application behaviour. Let the evidence identify which correctness, safety, performance, compatibility, or ergonomics questions deserve narrower work.

- Programme hub: #13
- State: `ready`
- Coordinator: unclaimed
- Upstream contact: unauthorized

## Scouts

- #17 — Vercel AI SDK streaming and tool lifecycle — claimed
- #18 — Workers SDK local, test, and deployment lifecycle — ready
- #19 — OpenTelemetry context and lifecycle boundaries — claimed
- #20 — MCP transport and session lifecycle — ready
- #21 — Supabase client and runtime contracts — ready

## Current decision

The scouts may run independently. A scout starts with broad code and test reconnaissance. Open child experiments or campaigns only after evidence identifies a concrete behaviour, consequence, likely owning boundary, and falsifiable next question.
