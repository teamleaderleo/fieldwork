# Rust SDK relist ordering follow-up

Review date: 2026-07-30  
Official source: `modelcontextprotocol/rust-sdk@cb50ae7890d8a5daacae1a4ad95f395f06733c07`  
Related Codex campaign: #84  
Upstream contact authorized: `false`

## Result

Compiled confirmation: the SDK's private response-cache generation protects its own cache from an out-of-order stale relist response, but the current public `list_tools` result gives application code no indication that the SDK rejected that response as stale. A naive callback publisher can therefore roll its application catalogue back while the SDK cache remains current.

The retained fixture is:

`artifacts/rmcp-relist-ordering/`

Validation: one focused Rust test passed, zero failed. The lockfile and exact stdout are retained; the temporary workflow removed itself after committing the evidence.

## Question

Can a Rust MCP client safely relist and publish tools from `notifications/tools/list_changed` using the current SDK API, including concurrent notifications and out-of-order relist responses?

Current answer: not by treating every successful `list_tools` callback result as publishable. Application publication needs an additional freshness contract.

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

## Compiled ordering reproduction

The real SDK receive loop processed two ordinary `notifications/tools/list_changed` events. Each spawned callback issued a real overlapping `tools/list` request over an in-process duplex transport.

Controlled sequence:

```text
initial catalogue A is cached
→ N1 invalidates and starts R1; R1 waits
→ N2 invalidates again and starts R2
→ R2 returns catalogue C and publishes first
→ R1 returns catalogue B late
```

Retained output:

```text
sdk_cache=catalogue_c naive_application=catalogue_b ticketed_application=catalogue_c requests=3
```

Assertions proved:

1. both callbacks issued relists without blocking response delivery;
2. R2 completed before R1;
3. the SDK cache retained C after R1 completed;
4. both callback relists returned successful results;
5. the naive publisher ended on stale B;
6. the generation-ticketed publisher remained on C;
7. a final `list_tools` returned C from the SDK cache without a fourth server request.

Workflow evidence and retained blob identifiers are recorded in `artifacts/rmcp-relist-ordering/validation.md`.

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

The compiled fixture demonstrates that application-owned notification generation is enough to prevent the tested rollback. That does not make it a complete generic coordinator: reconnect, cancellation, subscription lag, failed relists, and principal changes still need explicit handling.

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

## Remaining test matrix

The core out-of-order callback case is complete. Remaining SDK-specific cases are:

1. third notification while R1 and R2 are in flight;
2. one relist fails after a newer result was accepted;
3. callback task cancellation;
4. abrupt transport closure and reconnect;
5. private cache-partition change during relist;
6. bounded subscription channel lag;
7. graceful and abrupt subscription endings;
8. coalesced coordinator behavior under notification bursts.

None of those remaining cases weakens the compiled two-notification result.

## Ownership split

- Rust SDK: notification routing, cache invalidation, relist request, freshness generation, coalescing, and accepted-result signal.
- Codex integration: remote identity and catalogue digest validation, catalogue revision publication, immutable request binding, approval authority, and stale-call policy.

## Prior-art search

No matching open issue or pull request surfaced for a tool-list-change relist coordinator or public cache-generation acceptance signal in the official Rust SDK repository during this review.

Public Rust SDK and Codex repositories remained read-only. No upstream issue, comment, reaction, pull request, or code write occurred.