# Rejected candidate 0001: caller-generated OpenCode message IDs

Date: 2026-07-30

## Candidate

The candidate generated a distinct `msg_t3_<uuid>` value and passed it as `messageID` to every OpenCode `promptAsync` request.

## Executable result

Fieldwork workflow run `30494924940` established:

- the focused steering specification passed;
- all 30 existing OpenCode adapter tests passed after updating two strict request snapshots;
- the first server typecheck failure came from a reversed `Fiber` type annotation in the campaign restart test, not from this production candidate.

Those results are insufficient to establish protocol safety.

## Rejection reason

OpenCode message IDs are not opaque UUID-shaped strings.

OpenCode's internal `MessageID.ascending()` generator encodes a monotonic timestamp/counter prefix. Its session loop compares user and assistant message IDs lexicographically when deciding whether processing has advanced. A separately generated `msg_t3_<uuid>` can sort after the assistant ID and recreate the infinite-loop class reported against non-ascending caller IDs.

The public `@opencode-ai/sdk` package accepts an optional string `messageID` but does not export the official generator. The generator lives in private `@opencode-ai/core`, so T3 cannot import it as a supported dependency. Duplicating the private algorithm would also couple T3 to an undocumented OpenCode invariant and remains unsafe for external OpenCode servers with clock or version differences.

## Decision

Rejected.

Do not commit this candidate to T3 production source, even though the focused tests passed.

The corresponding over-prescriptive T3 test was removed from the owned target branch. Recovery affinity must instead use a version-tolerant provider-generated identity capture path or an explicit supported provider idempotency/correlation API.

## Required replacement design

A replacement must answer all of these before implementation:

1. How does T3 observe the exact provider-generated user message ID for every initial and steering prompt?
2. How is the ordered ID list persisted under one active T3 run/turn without relying on a later unrelated command?
3. What happens if T3 crashes after OpenCode accepts the prompt but before the ID is durably recorded?
4. How is the capture contract represented so Orchestration V2 can reuse it with `RunId`?
5. How does an external OpenCode server advertise compatible correlation behavior?

No upstream contact occurred.
