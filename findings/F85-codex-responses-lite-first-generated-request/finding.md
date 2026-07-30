# F85-codex-responses-lite-first-generated-request: Send the full first generated Responses Lite request after startup prewarm

Finding state: `delivery-gate-ready`

Workstream: `J/M/O — Responses Lite request identity and current-source review`  
Canonical Fieldwork issue: `#85`  
Canonical finding path: `findings/F85-codex-responses-lite-first-generated-request/finding.md`  
Canonical implementation: `teamleaderleo/codex#87`  
Exact implementation head: `e520da008366cd720ef58fa0b489efc0a2867e97`  
Exact base or source revision: `openai/codex@e6cfd40c3f444aadd6017c9eeab01db70f48961a`; current public relation checked through `413492cd6c3a4d4f8dff6f406247ccda5a9d88aa`  
Strongest evidence class: `target-executed` for the client transport rule; `integration-executed` diagnostic for stack pressure  
Reviewed input generation: `carrier #58 run 30584165709; complete three-file source diff; independent review 4824085183`  
Current review disposition: `ACCEPT transport rule; SPLIT stack-pressure investigation`  
Desk routing: `not-entered`  
Upstream contact authorized: `no`

## In simple words

Responses Lite startup prewarm opens and warms a WebSocket without generating a model response. The prewarm request contains the current tool and instruction prefix.

The first real generated turn should reuse the warm connection while sending its complete current request. It should not use the untraced warmup response as an incremental parent. After the first generated response succeeds, later turns can resume ordinary incremental reuse.

If that first generated request fails, its retry should send the same full request again.

## Why we care

Responses Lite carries important capability information in input items. An incremental request that incorrectly inherits an untraced warmup response can depend on server-side state that the generated request did not explicitly establish or trace.

A failed first generated request adds another boundary: retrying with a warmup parent can reproduce the same missing or mismatched capability state.

## What happens if we leave it alone

The old request path could use the warmup response ID as the first generated request's incremental parent. That couples model-visible generation to an untraced setup response.

Logical trace repair can record the request Codex intended. It cannot prove the server received or reconstructed the full capability prefix.

## Current finding

When all of these are true:

- the request is generated rather than warmup;
- the model uses Responses Lite;
- the WebSocket session's last response came from untraced warmup;

the client should clear that warmup response parent and send a full request.

After a successful generated response, normal incremental reuse can begin from that generated response. A failed first generated request retains full-request retry behavior.

### Claim table

| Claim | Evidence class | Exact support | Limit |
| --- | --- | --- | --- |
| First generated Lite request sends no warmup `previous_response_id` | `target-executed` | exact client controls in run `30584165709` | WebSocket client harness |
| First generated input preserves the warmup capability/instruction prefix | `target-executed` | full-input assertions in source tests | Exact tested request shape only |
| Later successful continuation reuses the first generated response | `target-executed` | `responses_lite_reuses_generated_response_after_full_first_turn` | One generated continuation |
| Retry after first-generation failure sends the same full request | `target-executed` | `responses_lite_retries_full_first_turn_after_failed_generation` | Synthetic `response.failed` path |
| Full agent path still overflows default worker stack | `integration-executed` diagnostic | `FIELDWORK_LITE_AGENT=default:101;large:0` | Does not identify the production repair |
| Public drift through `413492cd...` is file-disjoint | `source-read` | complete public compare | Later relevant drift expires review |

## System and ownership map

```text
startup prewarm
→ warm WebSocket, generate=false, no model inference
→ first generated Lite request
   ├── full logical input, no warmup parent
   ├── failure: retry the same full request
   └── success: establish generated response parent
→ later incremental continuation
```

- `ModelClientSession` owns wire request construction and parent selection.
- Responses Lite input construction owns the capability prefix.
- Rollout tracing owns the recorded logical request.
- Standalone Code Mode host owns executable authority.
- Tokio worker-stack depth belongs to a separate execution-path investigation.

## Historical precedent

### Responses Lite input-item tools

- Source: public commit `33cc928d339307795d4f5987337c7c4607f70338`.
- Principle supported: Lite capability information lives in the request input prefix rather than only a top-level tools field.
- Important difference: that contract does not decide how startup prewarm and generated WebSocket parentage interact.

### Logical trace after untraced prewarm

- Source: public commit `20fedafff83f5c681fc62f73b0ca3227e42e3f8b`.
- Principle supported: rollout trace should record the complete logical request even when the wire request is compressed.
- Important difference: trace correctness and wire delivery are separate facts.

### Standalone Code Mode host

- Source: public commit `97576b1794872e342450ebd577123e052ab57626`.
- Principle supported: Code Mode execution authority moved to a standalone host.
- Important difference: a correct transport manifest does not prove every advertised tool has matching host authority.

## Approaches considered

### Retained approach: break only the warmup parent chain

This keeps the warmed connection, sends one complete first generated request, and resumes incremental reuse afterward.

### Declined: disable WebSocket prewarm

That removes the problematic transition by discarding the intended connection-warming behavior and its latency benefit.

### Declined: trust logical trace reconstruction as wire proof

A trace can describe the intended full request while the server consumes a different incremental parent chain.

### Declined: retransmit the full manifest on every Lite turn

Ordinary generated-response parentage already provides a valid incremental boundary. Repeating the full prefix every turn adds payload and changes established behavior without evidence.

### Deferred: increase worker stack as the fix

The larger stack is a discriminator. It does not identify why the full agent path is deeper or whether production should change stack size.

## Edge cases covered

| Edge case or control | Evidence | Result |
| --- | --- | --- |
| Warmup followed by first generated turn | exact client test | full request; no warmup parent |
| Generated continuation after success | exact client test | incremental request from generated response |
| First generated request fails | exact client test | retry sends same full request on new connection |
| Capability prefix | full request assertions | generated input starts with exact warmup input |
| Source fence | carrier | exactly `client.rs` and two WebSocket test files |
| Full agent default stack | exact diagnostic | overflowed with status 101 |
| Full agent large stack | exact diagnostic | passed with status 0 |

## Edge cases deferred or outside scope

| Edge case | Why deferred | Owning next record or reopening trigger |
| --- | --- | --- |
| Root cause of agent stack depth | Transport controls pass below full agent | separate stack-pressure finding |
| Deferred/direct executable host authority | Different owner | deferred-tool authority finding |
| Non-WebSocket Lite transport | Current candidate owns WebSocket prewarm path | reopen on equivalent HTTP prewarm behavior |
| Server implementation details | Public server state not directly observable | protocol or owned-server fixture when available |
| Public proposal packaging | Direct current-head source preferred | current-head successor and final complete-diff review |

## Exact execution and receipts

| Repository/head | Command or workflow | Platform/environment | Result | Evidence class |
| --- | --- | --- | --- | --- |
| `teamleaderleo/codex#58@40a56eefce26ea647a65779faeb783d65a84a49a` | run `30584165709`, job `91011486628` | Linux owned carrier | source fence 3/3; client controls 2/2; source published | `target-executed` |
| same carrier | full agent control | default and large stack | `default:101;large:0` | `integration-executed` diagnostic |
| `teamleaderleo/codex#87@e520da008366cd720ef58fa0b489efc0a2867e97` | review `4824085183` | owned source PR | transport rule accepted; stack split | independent source review |

## Complete-diff and compatibility review

- Changed-file fence: `core/src/client.rs`, `agent_websocket.rs`, and `client_websockets.rs`.
- Source is one commit parented by `e6cfd40...`.
- Public commits through `413492cd...` leave the three-file fence unchanged.
- Non-Lite request behavior remains on the existing path.
- Full-agent stack pressure remains explicitly outside the transport acceptance.
- Routine remaining work: direct-current-head successor or explicit file-disjoint acceptance, final source review synchronization, and carrier retirement.

## Current disposition and desk routing

- Finding state: `delivery-gate-ready`
- Review disposition: `ACCEPT transport rule; SPLIT stack-pressure investigation`
- Review Queue entry: none
- Delivery lane: `not-entered`
- Exact next transition: publish or confirm a direct-current-head source candidate with identical three-file behavior; create a separate stack-pressure finding from the retained default/large result.
- Clearing condition: current-head source identity and final diff review agree without importing stack-fix claims.
- Required subgates: current-head relation, source receipt, carrier retirement.
- Autonomous work remaining: current-head packaging and stack finding.
- Non-delegable human decision: none.

## Changes to the canonical conclusion

| Date | Pull request or commit | Change in conclusion |
| --- | --- | --- |
| 2026-07-31 | historical #23/#43 | Separated logical request intent from stack diagnostic |
| 2026-07-31 | carrier #58 run `30584165709` | Client transport controls passed and source published; stack overflow retained |
| 2026-07-31 | source #87 review `4824085183` | Transport rule accepted; full-agent stack pressure split |

## References

- Fieldwork issues #85 and #239.
- Owned Codex PRs #23, #43, #58, and #87.
- `findings/F239-codex-upstream-convergence/finding.md`.
- Public Codex source through `413492cd6c3a4d4f8dff6f406247ccda5a9d88aa`, read-only.
- Public upstream interaction: none.
