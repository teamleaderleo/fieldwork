# Rust SDK relist ordering follow-up

Review date: 2026-07-30  
Official source: `modelcontextprotocol/rust-sdk@cb50ae7890d8a5daacae1a4ad95f395f06733c07`  
Related Codex campaign: #84  
Upstream contact authorized: `false`

## Question

Can a Rust MCP client safely relist and publish tools from `notifications/tools/list_changed` using the current SDK API, including concurrent notifications and out-of-order relist responses?

## Confirmed SDK behavior

The receive loop invalidates the affected SDK response cache before routing a notification.

Normal notification callbacks run in spawned service tasks. The receive loop continues processing responses while `ClientHandler::on_tool_list_changed` runs, so a callback can issue `context.peer.list_tools(...)` without inherently blocking response delivery.

`Peer<RoleClient>::list_tools` then:

1. returns a fresh cached response when available;
2. otherwise captures the private response-cache generation;
3. sends `tools/list`;
4. writes the response to the SDK cache only when the captured generation is still current;
5. returns the fetched result to the caller regardless of whether that cache write was accepted.

The SDK cache is therefore protected from an old in-flight response undoing notification invalidation. Application publication is not protected because the caller does not receive the generation or cache-write acceptance result.

## Ordering race

```text
server catalogue A
→ notification N1 invalidates cache and starts relist R1 at generation 1
→ server catalogue B
→ notification N2 invalidates cache and starts relist R2 at generation 2
→ server catalogue C
→ R2 completes first; SDK cache and application publish C
→ R1 completes late; SDK rejects its generation-1 cache write
→ R1 caller still receives Ok(B)
→ a naive application callback publishes B over C
```

The exact catalogue labels depend on when the server snapshots each request. The invariant is that a response rejected as stale for the SDK cache can still be returned as a successful raw relist result and published by application code.

## Why callback relisting alone is insufficient

A callback that simply runs `list_tools` and replaces an application catalogue has no public freshness token. Mutex serialization reduces concurrency but can still perform a redundant older relist after a newer notification unless the notification generation is recorded. Debouncing can reduce traffic but does not by itself prove that the published result belongs to the newest invalidation.

## Candidate SDK contract

A generic opt-in coordinator could expose one of these equivalent contracts:

### Accepted-result API

```text
relist_tools_current() -> {
  tools,
  generation,
  accepted_current: true | false
}
```

Only an accepted-current result may replace the application catalogue.

### Catalogue watch

The SDK owns notification coalescing and relist ordering, then publishes a stream or watch channel containing only accepted catalogue snapshots with monotonically increasing generations.

### Public ticket

The callback captures a public invalidation/relist ticket. A separate publish check verifies that the ticket remains the newest before application replacement.

The helper should remain opt-in. It should not silently replace application state, approval policy, request bindings, or model advertisements.

## Focused falsification fixture

Use a disposable in-process server with two controlled `tools/list` responses and two `notifications/tools/list_changed` events.

Assertions:

1. both callbacks can issue relists without deadlocking the receive loop;
2. R2 completes before R1;
3. the SDK cache retains R2's newer result after R1 completes;
4. both callers receive successful results under the current API;
5. a naive application publisher ends on R1's stale result;
6. the candidate coordinator ends on R2 and reports R1 as superseded;
7. abrupt transport closure, callback cancellation, and a third notification do not publish an older generation.

## Ownership split

- Rust SDK: notification routing, cache invalidation, relist request, freshness generation, coalescing, and accepted-result signal.
- Codex integration: remote identity and catalogue digest validation, catalogue revision publication, immutable request binding, approval authority, and stale-call policy.

## Prior-art search

No matching open issue or pull request surfaced for a tool-list-change relist coordinator or public cache-generation acceptance signal in the official Rust SDK repository during this review.

Public Rust SDK and Codex repositories remained read-only. No upstream issue, comment, reaction, pull request, or code write occurred.