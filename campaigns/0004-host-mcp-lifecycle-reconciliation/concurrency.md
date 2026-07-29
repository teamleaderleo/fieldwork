# MCP Refresh Generation and Reconnect Ordering

## In simple words

The first host-reload candidate uses the existing `reconnect_on_next_refresh()` switch. That switch proves the basic boundary, yet it cannot identify which desired-state update owns the reconnect.

Codex tracks pending runtime refresh with one boolean and pending reconnect with another boolean. When a publication is already running, a host config reload can set both booleans. The older publication may claim the reconnect switch before the new config publication starts. The queued publication then sees a fresh connection created for the older desired state and can reuse it when the connection configuration is unchanged.

Campaign #84 therefore needs a generation-bound refresh contract before accepting the one-line reconnect call as the full repair.

## Current owners

### Session refresh invalidation

`McpRefresh` contains:

- `pending: AtomicBool`;
- a semaphore that serializes publication;
- `invalidate()` to set pending;
- `claim()` to swap pending to false;
- a guard that restores pending when a claimed refresh ends before publication.

This preserves work across cancellation and coalesces repeated invalidations. It does not preserve the identity or ordering of desired-state revisions.

### Runtime reconnect intent

`McpRuntime` contains:

- `reconnect_pending: AtomicBool`;
- `reconnect_on_next_refresh()` to set it;
- `replace()` to swap and claim it;
- a guard that restores the switch if publication does not finish.

This preserves reconnect intent across a failed publication. It binds the intent to whichever `replace()` call arrives first.

## Adversarial sequence

1. Publication A claims the current refresh invalidation and computes desired state A.
2. Host reload installs desired state B, marks refresh pending, and sets reconnect pending.
3. Publication A reaches `McpRuntime::replace()` and claims reconnect pending.
4. Publication A creates a fresh client using desired state A.
5. The refresh loop observes another pending invalidation.
6. Publication B computes desired state B.
7. Publication B reaches `replace()` with reconnect pending already cleared.
8. When connection configuration is unchanged, publication B can reuse A's fresh client and its catalogue.

The final runtime can therefore carry desired configuration B with remote identity and catalogue captured during publication A.

## Required regression

A compiled test should hold publication A after it has computed desired state and before it calls runtime replacement. While held:

- apply host MCP config B;
- request reconnect for B;
- release A;
- allow the queued publication to finish;
- assert that B receives a client initialized for B's accepted generation;
- assert that A's older captured binding remains usable for A;
- assert that no late A result overwrites B.

A stable endpoint should expose an initialization generation or deterministic catalogue marker so the test can distinguish client creation from config publication.

## Candidate contracts

### Generation-bound reconnect request

Replace the boolean reconnect switch with a monotonic minimum generation:

- every accepted desired-state change receives a generation;
- host reload requests fresh connections for generation B;
- publication A cannot consume B's reconnect request;
- publication B claims reconnect when its generation reaches the requested generation;
- superseded requests remain observable in a typed outcome.

### Serialized explicit host refresh

Acquire the refresh publication gate, install config B, and publish a fresh runtime before releasing the host reload call.

This is simpler for an explicit host action and gives the caller completion semantics. It can block on server startup and needs a clear timeout and partial-failure contract.

### Refresh ticket

Create a ticket containing:

- desired-state generation;
- reconnect requirement;
- source reason such as host reload, auth change, notification, explicit user refresh, or recovery;
- per-server expected connection identity;
- supersession state.

The publisher accepts tickets in order and records typed outcomes. This is the broadest match for #84's notification and concurrent-relist requirements.

## Current recommendation

Keep the one-line host reconnect candidate as a bounded baseline and basic regression. Promote a generation or ticket before adopting it as the complete host/MCP refresh repair.

The next test after the basic reconnect case should exercise the adversarial sequence above. The notification-driven relist slice should use the same generation vocabulary so a late `tools/list` result cannot overwrite a newer host reload or reconnect.
