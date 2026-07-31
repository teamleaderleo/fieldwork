# F84-codex-mcp-publication-generation: Let only the newest eligible MCP refresh publish its own result

Finding state: `delivery-gate-ready`

Workstream: `J/L/O — MCP runtime authority and current-source review`  
Canonical Fieldwork issue: `#84`  
Canonical finding path: `findings/F84-codex-mcp-publication-generation/finding.md`  
Canonical implementation: `teamleaderleo/codex#75`  
Exact implementation head: `c3373c717f3138ff5f0a979d12836f60800d2bcf`  
Exact base or source revision: `openai/codex@a01a2d91461a57809e944de7758477b92617ab01`; current public relation checked through `413492cd6c3a4d4f8dff6f406247ccda5a9d88aa`  
Strongest evidence class: `target-executed`  
Reviewed input generation: `complete one-file source diff; carrier #77 run 30584055792; independent review 4823972975`  
Current review disposition: `ACCEPT manager invariant; EXECUTE overlapping production-path fixture`  
Desk routing: `not-entered`  
Upstream contact authorized: `no`

## In simple words

MCP refresh builds a candidate set of connections and tool metadata before making it visible. Two refreshes can overlap: an older slow refresh can finish after a newer one.

The retained source gives each refresh a generation and freshness epoch. A candidate publishes only when it is still the newest eligible request. A stale candidate keeps its publication gate closed and a hard refresh returns its own accepted catalogue instead of reading whichever runtime is current later.

## Why we care

Without a publication winner rule, an older refresh can replace newer runtime state or return the wrong catalogue. Model-visible tools, approval metadata, connector identity, and executable clients can then describe different generations.

The current production Session path largely serializes replacement, so measured production frequency is unknown. The manager is also called directly and its contract should remain correct when overlap appears through tests, future callers, or cancellation/recovery paths.

## What happens if we leave it alone

The historical design used a reconnect-pending boolean and unconditional publication. It did not encode:

- which refresh request was newest;
- which freshness request a candidate satisfied;
- whether a stale candidate's gate should remain closed;
- whether `replace_fresh` returned its own accepted result.

A later caller can therefore inherit whichever runtime happens to be current after asynchronous work completes.

## Current finding

`McpRuntime` should own one publication state containing:

- monotonically increasing requested generation;
- current freshness epoch;
- last published freshness epoch.

Every refresh receives a ticket. Publication succeeds only when the ticket still matches the latest generation and freshness epoch. A successful publication advances the published freshness epoch.

### Claim table

| Claim | Evidence class | Exact support | Limit |
| --- | --- | --- | --- |
| An older generation is rejected after a newer request | `target-executed` | exact state control in run `30584055792` | State-machine control, not a delayed network build |
| A freshness request carries across overlapping candidates until an eligible winner publishes | `target-executed` | exact freshness controls | Does not prove host request routing |
| A stale candidate keeps its publication gate closed | `target-executed` | asynchronous gate control | Synthetic state path |
| `replace_fresh` returns the accepted candidate's own connection result | `source-read` | PR #75 one-file diff | Needs a complete overlapping runtime fixture |
| Public drift through `413492cd...` is file-disjoint | `source-read` | complete public compare | Later runtime drift expires the review |

## System and ownership map

```text
refresh request
→ issue generation/freshness ticket
→ build candidate connection set and catalogue
→ synchronous eligibility check
├── accepted: store candidate, mark freshness published, open gate
└── stale: discard candidate, keep gate closed
```

- `McpRuntime` owns published immutable runtime state.
- `McpConnectionSet` owns connection preparation and cache refresh work.
- The publication state protects future visibility.
- Prepared and active call authority remains a separate captured-binding finding.
- App-server and host request paths remain separate reconnect-entrypoint findings.

## Historical precedent

### Reuse MCP connections across runtime refreshes

- Source: openai/codex PR #34952.
- Principle supported: ordinary refresh can reuse unchanged ready connections.
- Important difference: reuse eligibility does not decide which overlapping candidate may publish.

### Reconnect on explicit refresh

- Source: openai/codex PR #35151.
- Principle supported: explicit freshness intent survives cancelled replacement.
- Important difference: freshness intent and publication generation are related but separate contracts.

### Immutable Apps runtime snapshots

- Source: openai/codex PR #31471.
- Principle supported: one manager owns committed connector runtime state and stale contexts stop advertising old tools.
- Important difference: that direction does not by itself prove newest-request publication in this runtime owner.

### Request-stable MCP snapshot

- Source: openai/codex PR #31292.
- Principle supported: one sampling request should consume one stable tool snapshot.
- Important difference: request stability starts after publication and does not choose the publication winner.

## Approaches considered

### Retained approach: generation plus freshness epoch

It keeps ordinary reuse and explicit freshness distinct, invalidates stale candidates, and gives an accepted hard refresh its own result identity.

### Declined: unconditional last-finisher publication

Completion order is not request order. A slow older candidate can regress visible state.

### Declined: reconnect boolean only

A boolean carries freshness intent but does not identify the newest request or distinguish accepted results.

### Declined: serialize every runtime build globally

Serialization avoids overlap by blocking independent work and can widen latency or cancellation coupling. A manager publication rule remains useful even when current callers serialize.

### Deferred: active-call authority

A call prepared under one runtime must retain captured binding or receive typed invalidation. That belongs to the MCP authority finding.

## Edge cases covered

| Edge case or control | Evidence | Result |
| --- | --- | --- |
| Older ordinary generation completes after newer | exact control | older rejected, newer accepted |
| Freshness requested before overlapping ordinary issues | exact control | both candidates require fresh connections; only newest publishes |
| Freshness advances after candidate issued | exact control | stale candidate rejected; replacement carries freshness |
| Stale candidate publication gate | async exact control | gate remained closed |
| Existing accepted gate behavior | retained runtime test | winning candidate opens gate |

## Edge cases deferred or outside scope

| Edge case | Why deferred | Owning next record or reopening trigger |
| --- | --- | --- |
| Slow older connection build versus fast newer build | Requires controllable production runtime builder | next exact integration fixture for this finding |
| App-server explicit reload | Request routing separate from publication state | reconnect finding and PR #82 |
| Prepared/active call uses old runtime | Publication controls future visibility only | MCP authority finding and PR #79 |
| Cancellation during connection build | Needs operation/cancellation controls | MCP lifecycle finding |
| Catalogue/result persistence | Different state owner | result and persistence findings |

## Exact execution and receipts

| Repository/head | Command or workflow | Platform/environment | Result | Evidence class |
| --- | --- | --- | --- | --- |
| `teamleaderleo/codex#77@0fb2e6b09a6ff03bcfcbd665b187cadb64d36b4b` | run `30584055792` | Linux owned current-pin carrier | five exact publication controls passed | `target-executed` |
| `teamleaderleo/codex#75@c3373c717f3138ff5f0a979d12836f60800d2bcf` | complete-diff review `4823972975` | owned source PR | manager invariant accepted; broader claim held for fixture | `source-read` review |

## Complete-diff and compatibility review

- Changed-file fence: exactly `codex-rs/codex-mcp/src/runtime.rs`.
- Source branch is one commit based on `a01a2d...`.
- Public Codex is two file-disjoint commits ahead at `413492cd...`.
- Mutex scope contains no await and covers only eligibility, `ArcSwap::store`, and state update.
- Existing ordinary reuse remains when a ticket does not require freshness.
- Execution carrier #77 remains temporary and should retire after receipt transfer.
- Routine remaining work: slow-older/fast-newer complete runtime fixture, current-head source identity, and final source review synchronization.

## Current disposition and desk routing

- Finding state: `delivery-gate-ready`
- Review disposition: `ACCEPT manager invariant; EXECUTE overlapping production-path fixture`
- Review Queue entry: none
- Delivery lane: `not-entered`
- Exact next transition: add one controllable slow-older/fast-newer runtime build test that proves connection preparation, candidate result identity, gate behavior, and published snapshot together.
- Clearing condition: the complete runtime overlap fixture passes at a current direct source head.
- Required subgates: integration fixture, current-head relation, exact source review, carrier retirement.
- Autonomous work remaining: fixture implementation, execution, and receipt synchronization.
- Non-delegable human decision: none.

## Changes to the canonical conclusion

| Date | Pull request or commit | Change in conclusion |
| --- | --- | --- |
| 2026-07-31 | historical #48 | Identified unconditional publication and generation residue |
| 2026-07-31 | source #75 / carrier #77 | Materialized current manager ticket model and exact controls |
| 2026-07-31 | run `30584055792` / review `4823972975` | Manager invariant accepted; full overlapping runtime fixture retained as the final evidence gate |

## References

- Fieldwork issues #84 and #239.
- Owned Codex PRs #48, #75, and #77.
- `findings/F239-codex-upstream-convergence/finding.md`.
- Public Codex source through `413492cd6c3a4d4f8dff6f406247ccda5a9d88aa`, read-only.
- Public upstream interaction: none.
