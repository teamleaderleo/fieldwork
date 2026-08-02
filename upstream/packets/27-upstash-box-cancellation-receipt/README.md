# Unit 27 — Upstash Box cancellation-request receipt

## Disposition

`RETIRE`

Retired on `2026-08-03` by explicit user priority decision. The technical finding and retained candidate remain valid research records, but this repository and contribution do not justify more Fieldwork time relative to higher-impact targets.

This is a priority stop, not a claim that the behavior is correct or that the prior evidence was invalid.

## Why this unit is retired

- The target has limited demonstrated adoption compared with available Fieldwork targets.
- The remaining TypeScript stream repair, current-head execution, clean-fork publication, and API naming work would consume meaningful effort.
- No evidence in this packet establishes broad user impact, ecosystem dependence, production frequency, billing consequence, or maintainer demand.
- A much larger and actively used target, uv, has an open cache-corruption report with multiple real-user power-loss observations and a target-executed Fieldwork reproducer.

## Preserved technical result

At the inspected Upstash Box source, cancellation request delivery, local observer shutdown, and remote terminal state are conflated. The retained candidate:

- preserves TypeScript and Python `cancel()` return contracts;
- adds one immutable request receipt per in-memory `Run` object;
- avoids publishing a remote terminal outcome from local request delivery;
- shares one request within one object;
- passes the historical TypeScript and Python target gates recorded in this packet.

The unresolved repair is also preserved: TypeScript agent-stream cancellation and timeout share one abort path, so a real cancellation-request abort can be reported as `Stream timed out` and terminal `cancelled`. The packet's selected repair records first abort ownership and classifies caller-requested local shutdown as `detached` while preserving iterator rejection.

## Exact retained identities

- Historical public base executed: `upstash/box@b55d832d6e3ae0156e32d21ea3863e231dfff9cd`
- Last current public head inspected: `upstash/box@9f7533c645f6b519f612aa977f6f4acf86655db7`
- Target-executed Fieldwork carrier head: `1e7909da440ab631fcea11d4d3777d2bce107277`
- Workflow-free carrier head: `ccaa28e40c5689aec7ad78c7f18c354e9966d7fd`
- Retained ordered patch SHA-256: `d30874c96f8e39350b9d725c58a6034554c561b073cb04969849ff2778c09e88`
- Packet branch: `p0/435-unit-27-upstash-box-cancellation-receipt`
- Public upstream interaction: none

## Evidence retained

Historical execution remains available in [TESTS.md](./TESTS.md), including:

- TypeScript focused: 21/21;
- TypeScript complete: 385/385, build and formatting passed;
- Python focused: 7/7;
- Python complete: 185 passed, 12 deselected;
- deterministic generated sync output;
- parity, Ruff, and MyPy passed.

The exact patch series and receipt remain under [`patches/`](./patches/README.md) and [`receipts/`](./receipts/target-executed-b55d832.json).

## Packet navigation

- [Deep dive](./DEEP_DIVE.md)
- [Related repository and contract context](./RELATED_CONTEXT.md)
- [Approaches](./APPROACHES.md)
- [Tests and receipts](./TESTS.md)
- [Upstream issue draft](./UPSTREAM_ISSUE.md)
- [Upstream pull-request draft](./UPSTREAM_PR.md)
- [Historical review guide](./REVIEW.md)
- [Retained patch series](./patches/README.md)

## Reopening trigger

Reopen only if one of the following appears:

- substantial target adoption or a documented downstream dependency;
- repeated public reports of cancellation-state confusion;
- maintainers request a cancellation receipt or remote-status correction;
- another contributor supplies the stream-path repair and current target execution;
- the same design becomes necessary for a larger shared SDK surface.

## Final handoff

State: `RETIRE`  
Source candidate: preserved, not promoted  
Clean target branch: none  
Internal carrier: close as retired research  
Further implementation or execution: stopped  
Public upstream contact: unauthorized and none performed
