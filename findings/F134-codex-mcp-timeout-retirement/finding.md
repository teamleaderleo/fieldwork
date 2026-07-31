# F134-codex-mcp-timeout-retirement: Retire only the exact timed-out MCP client and republish without replay

Finding state: `comparative-evaluation-active`

Workstream: `L — MCP cancellation, timeout certainty, retirement, and recovery`  
Canonical Fieldwork issue: `#134`  
Canonical finding path: `findings/F134-codex-mcp-timeout-retirement/finding.md`  
Canonical implementation: `none; manager-layer prototype pending`  
Exact implementation head: `none`  
Exact base or source revision: `openai/codex@4642370542739d5dd080b0c87a9de06a6435d3db`  
Strongest evidence class: `target-executed` for the historical cancellation matrix; `source-read` for current manager ownership  
Reviewed input generation: `Fieldwork PR #163 matrix and current Codex binding/runtime/session/RMCP source`  
Current review disposition: `COMPARE and EXECUTE`  
Desk routing: `not-entered`  
Upstream contact authorized: `no`

## In simple words

Codex can stop waiting for an MCP tool while the server may still be working. Sending a cancellation message helps, but it does not prove the tool stopped or that a mutation did not happen.

The hard part is what Codex should do when cancellation cannot be delivered. Closing whatever client is currently registered under the same server name is unsafe: the timed-out call may belong to an older client that has already been replaced.

The current direction is:

1. carry the exact client identity with the prepared call;
2. return a typed receipt for timeout and cancellation facts;
3. retire a client only if that exact identity is still current;
4. reconnect only the affected server and republish its catalogue;
5. never replay the timed-out operation automatically.

## Why we care

A potentially mutating MCP call may complete after Codex reports a timeout. Unsafe recovery can then create one of two further failures:

- replay the operation and duplicate an effect;
- close or replace the wrong client, disrupting a newer connection or unrelated server.

The model, user, and recovery logic need an honest distinction between local timeout, cancellation delivery, transport retirement, replacement publication, and remote-effect settlement.

## What happens if we leave it alone

The current legacy path can return a local timeout while sending no cancellation. A cooperative delayed synthetic mutation then completes afterward and the same connection remains usable.

The historical matrix also shows:

- delivered cancellation can stop a cooperative fixture;
- a server can receive cancellation and still commit later;
- cancellation delivery can stall beyond the caller deadline;
- directly closing the shared service can bound the caller but lacks manager ownership and generation safety.

Frequency and production impact are unknown. The evidence is bounded to the executed synthetic fixtures and current source ownership map.

## Current finding

The production owner should be the MCP runtime/session refresh boundary, not `RmcpClient::call_tool` alone.

`PreparedMcpCall` already retains the exact connection set and exact managed client by `Arc` identity. `McpRuntime` owns the current immutable connection set, and `Session` owns desired-state reconstruction, refresh serialization, and publication. These existing identities can support a safe stale-retirement check without requiring server name alone to stand in for generation.

A numeric publication generation remains useful for ordering, diagnostics, and durable receipts. It is not the only possible safety fence: pointer identity can prove that a delayed timeout still refers to the current client before any shutdown occurs.

### Claim table

| Claim | Evidence class | Exact support | Limit |
| --- | --- | --- | --- |
| Current legacy timeout can return without cancellation while a delayed effect completes | `target-executed` | Fieldwork PR #163 matrix, baseline controls | Synthetic legacy fixture |
| Cancellation delivery does not prove mutation absence | `target-executed` | ignored-cancellation control in PR #163 | Does not measure real-service frequency |
| Bounded cancellation plus service shutdown can return within the caller bound | `target-executed` | leading historical candidate in PR #163 | Shutdown occurred below manager ownership |
| `PreparedMcpCall` retains exact client and connection-set identity | `source-read` | current `codex-mcp/src/binding.rs` | Fields are not yet exposed as an opaque retirement token |
| `McpRuntime` and `Session` own replacement and publication | `source-read` | current `runtime.rs` and `core/src/session/mcp.rs` | Current reconnect request is all-or-nothing |
| Pointer identity can prevent stale timeout retirement of a replacement client | `inferred design` | exact retained `Arc` identities plus current immutable publication | Requires implementation and adversarial execution |
| A targeted server reconnect is preferable to restarting every healthy server | `inferred design` | current all-server `reconnect_pending` behavior and independent server ownership | Policy for same-server concurrent calls remains to be executed |

## System and ownership map

```text
model step
→ PreparedMcpCall
   ├── exact connection set
   ├── exact managed client
   ├── exact catalogue revision
   └── exact tool/config authority
→ RMCP request handle
→ Codex active-time deadline
→ typed cancellation receipt
→ runtime current-client comparison
   ├── stale token: do not retire replacement
   └── current unhealthy client: targeted retirement
→ Session desired-state refresh
→ replacement connection and catalogue publication
→ no automatic replay; effect remains outcome-unknown
```

- `RmcpClient` owns request creation and cancellation delivery mechanics.
- `PreparedMcpCall` owns the exact execution identity for the call.
- `McpRuntime` owns the currently published connection set.
- `Session` owns refresh serialization and desired-state republication.
- Receipt and replay layers consume the result but must not infer settlement from timeout or cancellation delivery.

## Historical precedent

### Fieldwork cancellation matrix

- Source: Fieldwork PR #163, merged as `896a617c4b4dd8dd9fb9493d05f801c7baf9ade3`.
- Principle supported: timeout, dispatch, cancellation request, delivery, transport state, and remote effect are separate facts.
- Important difference: the leading experiment closed the service directly and did not own current-client comparison or replacement publication.

### Captured MCP call authority

- Source: current `codex-rs/codex-mcp/src/binding.rs` and public Codex PR #34588.
- Principle supported: a call can retain exact client and catalogue identity after runtime replacement.
- Important difference: current APIs do not expose a manager retirement token or typed cancellation receipt.

### Runtime reconnect and publication

- Source: current `codex-rs/codex-mcp/src/runtime.rs`, `core/src/session/mcp.rs`, and Fieldwork #84 publication/reconnect candidates.
- Principle supported: the runtime/session boundary owns immutable publication, reconnect intent, desired-state reconstruction, and catalogue replacement.
- Important difference: current reconnect intent is one boolean for all servers, and current public source lacks the owned monotonic publication-ticket candidate.

### RMCP request cancellation

- Source: RMCP SDK `RequestHandle::cancel`, timeout cancellation notification, and stateless disconnect regression at `3240b6e7828ed4146041d32dd0ce4ced7c04e411`.
- Principle supported: request-scoped cancellation delivery is available and can trigger cooperative server cancellation.
- Important difference: delivery does not settle a mutation and resumable transports have different disconnect semantics.

## Approaches considered

### Retained approach: exact-client token, typed receipt, targeted manager retirement

This approach keeps request cancellation at the client layer while moving stale-client comparison, shutdown policy, reconnect, and catalogue republication to their existing owners.

The token should be opaque and carry enough identity for the runtime to compare:

- connection set;
- exact managed/RMCP client;
- server name;
- optional publication generation for diagnostics and ordering.

The typed receipt should retain:

- deadline reached;
- dispatched or not;
- cancellation requested;
- delivery `delivered | failed | timed_out | not_supported`;
- transport `healthy | retired | replacement_pending | unknown`;
- remote effect `unknown` unless stronger evidence settles it.

### Declined: local timeout only

It preserves the current defect: the caller stops waiting without attempting request cancellation and without a recovery receipt.

### Declined: direct service shutdown inside `RmcpClient::call_tool`

That layer cannot prove the timed-out service is still the runtime's current client and cannot own catalogue republication. A delayed timeout could close a replacement.

### Declined: retire by server name alone

A server name is not a connection generation. It cannot distinguish the old timed-out client from a newer replacement.

### Declined: restart every configured MCP server

The current all-server reconnect boolean is suitable for explicit host configuration reload. Timeout escalation should not disrupt unrelated healthy servers when the unhealthy identity is known exactly.

### Declined: automatic replay after replacement

Cancellation or transport retirement does not prove the remote mutation did not commit. Replay is unsafe without a durable idempotency contract or reconciliation read.

### Deferred: publication generation as the only identity

A monotonic generation is valuable and should compose with this design. Pointer identity already supplies a strict in-process stale-client fence; the comparison should establish whether generation is required for safety, observability, restart lineage, or all three.

## Edge cases covered

| Edge case or control | Evidence | Result |
| --- | --- | --- |
| Cooperative server observes cancellation | PR #163 matrix | delayed cooperative effect prevented |
| Server ignores cancellation | PR #163 matrix | late commit still occurs; effect remains unknown |
| Cancellation write stalls | PR #163 matrix | bounded candidate returns and closes service |
| Unrelated concurrent request on successful request-scoped cancellation | PR #163 matrix | remains healthy |
| Elicitation exceeds active tool time | PR #163 matrix | Codex pause-aware policy preserved only by explicit pause-aware candidates |
| Modern high-level request stream | PR #163 matrix | unresolved separately; candidate transformations left it unchanged |
| Current call retains exact old client after replacement | current binding tests | pointer identity and captured authority remain available |

## Edge cases deferred or outside scope

| Edge case | Why deferred | Owning next record or reopening trigger |
| --- | --- | --- |
| Exact targeted retirement implementation | No current-source prototype yet | this finding's next carrier |
| Same-server unrelated in-flight calls | Policy must be explicit and executed | manager prototype controls |
| Cross-process/restart identity | Pointer identity is in-process only | typed receipt and durable operation lineage |
| Publication race ordering | Independent publication candidate owns monotonic publication | compose after current-head publication gate |
| Modern resumable HTTP cancellation | SDK/lifecycle semantics differ | separate modern-transport finding |
| Remote effect reconciliation | Service-specific read/idempotency contract required | receipt/reconciliation lanes |
| Public output changes | First slice should remain behavior-neutral where possible | separate protocol review if needed |

## Exact execution and receipts

| Repository/head | Command or workflow | Platform/environment | Result | Evidence class |
| --- | --- | --- | --- | --- |
| `teamleaderleo/codex@e322eb92a6745616953bc00a3db8046c499dc6a7` | Fieldwork PR #163 cancellation matrix, run `30513328316` | owned synthetic Rust fixtures | baseline and three candidate matrices passed | `target-executed` |
| `openai/codex@4642370542739d5dd080b0c87a9de06a6435d3db` | current binding/runtime/session/RMCP source read | read-only public source | exact identity and current reconnect/publication owners mapped | `source-read` |
| `modelcontextprotocol/rust-sdk@3240b6e7828ed4146041d32dd0ce4ced7c04e411` | request-handle and stateless-disconnect source read | read-only public source | native cancellation delivery mechanisms confirmed | `source-read` |

No current manager-layer source candidate has executed.

## Complete-diff and compatibility review

This finding branch contains documentation and evidence only. It changes no Codex product source.

Compatibility surfaces for the future prototype:

- Codex elicitation-aware active-time accounting;
- legacy request handles;
- modern stateless and resumable HTTP behavior;
- exact prepared-call authority;
- shared connection sets and concurrent calls;
- explicit host reload versus targeted timeout retirement;
- catalogue cache and publication ordering;
- outcome-unknown receipt and no-replay policy.

A source candidate must remain bounded to exact identity, typed receipt, targeted retirement, and reconnect/publication. Broader public protocol or replay changes require separate review.

## Current disposition and desk routing

- Finding state: `comparative-evaluation-active`
- Review disposition: `COMPARE and EXECUTE`
- Review Queue entry: none
- Delivery lane: `not-entered`
- Exact next transition: instantiate a current-source manager-layer prototype with an opaque exact-client token, typed cancellation receipt, current-client comparison, and targeted reconnect request
- Clearing condition: stale-token, stalled-delivery, unrelated-server, same-server invalidation, replacement-publication, and no-replay controls distinguish the retained design from direct shutdown and all-server restart
- Required subgates: current source fence, exact tests, publication composition, complete diff, compatibility review, source-only successor, independent exact-head review
- Autonomous work remaining: prototype, execution, adversarial review, and canonical reconciliation
- Non-delegable human decision: none currently

## Changes to the canonical conclusion

| Date | Record | Change in conclusion |
| --- | --- | --- |
| 2026-07-30 | Fieldwork PR #163 | Accepted the bounded legacy cancellation mechanism as evidence but held direct client-layer shutdown |
| 2026-07-31 | current-source ownership map | Identified existing exact pointer identity in `PreparedMcpCall` and runtime/session ownership for safe retirement and republication |
| 2026-07-31 | this finding | Selected exact-client token plus typed receipt plus targeted manager retirement as the provisional direction for execution |

## References

- Fieldwork issues #134, #162, #239, and #254.
- Fieldwork PR #163 and merge commit `896a617c4b4dd8dd9fb9493d05f801c7baf9ade3`.
- `findings/F134-codex-mcp-timeout-retirement/evidence/20260731-current-manager-ownership.md`.
- Public Codex `codex-rs/codex-mcp/src/binding.rs`.
- Public Codex `codex-rs/codex-mcp/src/runtime.rs`.
- Public Codex `codex-rs/core/src/session/mcp.rs`.
- Public Codex `codex-rs/rmcp-client/src/rmcp_client.rs`.
- RMCP SDK request-handle and stateless-disconnect source at `3240b6e...`.
- Public upstream interaction: none.
