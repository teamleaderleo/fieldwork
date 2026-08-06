# Cloudflare Agent state projection boundary

## In simple words

Cloudflare Agents use a Durable Object as the rear-facing authority for one Agent instance. State is persisted in the object's SQLite storage and broadcast to WebSocket clients.

The browser client adds a second state machine:

- it remembers the server-reported agent identity;
- it keeps a local `state` value;
- `setState()` updates that value optimistically before server confirmation;
- reconnect may route the same client object to a different Agent instance.

This creates a useful front/rear review boundary even though the Durable Object itself serializes state mutations.

## Retrieval boundary

- Repository: `cloudflare/agents`
- Current observed head: `f9d71d65ffb31cb45c8594b5f3bd4eeb4a8560d1`
- Core server/client files: `packages/agents/src/index.ts`, `packages/agents/src/client.ts`
- State tests: `packages/agents/src/tests/state.test.ts`
- Ordering tests: `packages/agents/src/tests/msg-ordering.test.ts`
- Retrieval date: 2026-08-06
- Upstream contact authorized: `false`

## Authority model

The Durable Object instance is the primary state owner. Server-side `setState()` persists the new value and broadcasts a `CF_AGENT_STATE` frame. A newly connected client receives the current state from the object.

Within one WebSocket connection, message order is preserved. The repository's ordering test requires:

1. `CF_AGENT_IDENTITY` first;
2. state and MCP setup frames before application messages;
3. `onConnect` completion before client messages are processed.

The client treats server identity as authoritative and exposes an explicit `onIdentityChange` callback when reconnect resolves to another instance.

## Optimistic client state

`AgentClient.setState(state)` performs three actions immediately:

1. sends a state frame;
2. assigns `client.state = state`;
3. calls `onStateUpdate(state, "client")`.

A later server broadcast assigns the authoritative state and reports source `"server"`. A server rejection emits `CF_AGENT_STATE_ERROR` and invokes `onStateUpdateError`, but the client does not retain a previous value or automatically roll back its optimistic state.

This is an intentional optimistic-interface shape, but it means a consumer that needs confirmed state must distinguish client and server callbacks rather than treating every local update as committed.

## Reconnect and identity change

On WebSocket close the client resets its identity-ready state, but it does not clear `client.state`.

If server-side routing resolves the reconnect to a different Agent instance:

1. the identity frame arrives first;
2. `onIdentityChange` runs and the client updates `name` and `agent`;
3. the old instance's state remains in `client.state` until the new state frame arrives;
4. the new server state then replaces it.

The server ordering is correct and explicit. The front-facing integration must decide what to show during that identity-known/state-not-yet-refreshed interval.

This is not automatically a data-leak claim. A concrete security assessment would require an authenticated routing setup, tenant model, UI behavior, and proof that the stale value becomes observable across a forbidden identity boundary.

## Useful conformance tests

### Identity/state coherence

Reconnect one `AgentClient` object from instance A to instance B and require one of these declared behaviors:

- state is cleared when identity changes and stays unavailable until B's state arrives; or
- the client exposes the pair `(stateIdentity, state)` so consumers can reject a stale pairing; or
- the UI deliberately keeps A's state, with an explicit transition state, until B is hydrated.

The current API exposes identity change but not which identity produced the retained local state.

### Optimistic confirmation

Send two client updates with a server-side policy that rejects one. Verify that the application can distinguish:

- optimistic local value;
- rejected value;
- last server-confirmed value;
- later broadcast from another client.

The current callbacks provide source and error notification, but rollback/version policy belongs to the application.

### Multi-client convergence

Drive conflicting updates from two WebSocket clients. The Durable Object serializes server application order, and broadcasts should converge both clients on the final server value. A conformance test should record whether intermediate optimistic callbacks can arrive in a different semantic order from server confirmations.

## Connection to the wider map

| Layer | Authority |
| --- | --- |
| Durable Object storage | serialized persisted Agent state |
| WebSocket connection | ordered delivery from one Agent instance |
| identity frame | which Agent instance now owns the connection |
| optimistic local state | unconfirmed client intent |
| server state frame | confirmed visible state from the current object |

This architecture illustrates that a single-threaded durable backend does not remove the need for front-facing identity/version coherence. The rear-facing owner is strong; the remaining design choices concern how optimistic and reconnecting clients label the state they render.

## Current disposition

Retain as a positive architecture plus integration-test avenue.

Do not promote a correctness or security defect without a concrete application integration and executable identity/state reproduction. No upstream interaction occurred.
