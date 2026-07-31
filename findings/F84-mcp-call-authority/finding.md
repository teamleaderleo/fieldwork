# F84-mcp-call-authority: Preserve the authority a model saw while allowing cached MCP startup

Finding state: `comparative-evaluation-active`

Workstream: `L — MCP capability authority, reconnect, and catalogue replacement`  
Canonical Fieldwork issue: `#84`  
Canonical finding path: `findings/F84-mcp-call-authority/finding.md`  
Canonical implementation: `none; current-source execution carriers #90 and #92 are active`  
Exact implementation heads: `reconnect #90@cf9f8765b67562679f7776169fb506a6a0bb7d94; authority #92@af6af7da8c337364a48954521dde5a7f741558f5`  
Exact base or source revision: `openai/codex@4642370542739d5dd080b0c87a9de06a6435d3db`  
Strongest evidence class: `target-executed` for publication and bounded reconnect; `source-read` for callable authority; current exact-one and authority candidates executing  
Reviewed input generation: `canonical authoring PR #292@00e9292e4dc14d14316dc981ae127de23a5790a5; current public source; executed receipts; current carrier heads; merged public precedents #34588 and #35590`  
Current review disposition: `EXECUTE and COMPARE`  
Desk routing: `not-entered`  
Upstream contact authorized: `no`

## In simple words

Codex shows a model a list of MCP tools. The model chooses one of those tools. Before Codex sends the call, the server may finish starting, reconnect, or publish a different tool catalogue.

Two useful Codex rules currently meet at this boundary:

1. an ordinary model step should execute the exact client and catalogue it captured;
2. a cached tool may be shown before its server is ready, so that special case must wait for a live client before execution.

The selected direction keeps both rules:

- use the step's captured `PreparedMcpCall` whenever it exists;
- live-bind only when the step advertised a cached-only tool with no prepared call;
- before any approval, permission hook, file rewrite, memory marking, request metadata, or dispatch, prove that the live callable authority still matches what the model saw;
- fail closed when executable authority changed.

## Why we care

A same-name replacement tool can have a different input schema, connector, destructive policy, file-upload surface, or app metadata. If Codex silently routes an old model decision to that replacement, the model's earlier tool declaration becomes authority for a different operation.

Overly strict equality is also wrong. Current Codex deliberately permits cached presentation to age while preserving the same executable operation:

- dynamic descriptions may identify the old process while the live replacement executes;
- cached definitions deliberately clear a potentially stale `readOnlyHint`.

The comparison therefore needs to be strict about executable authority without treating presentation or deliberately weakened scheduling metadata as operation identity.

## What happens if we leave it alone

Current `McpHandler` retains the advertised `ToolInfo`, but the call path passes only server and raw tool name. `handle_mcp_tool_call` refreshes and prepares a call from the session's newest runtime, even when `StepContext` still carries the exact `McpBinding` used for that model step.

Bounded consequences:

- an ordinary call may leave its captured client and bind to a replacement;
- a cached-only call may inherit changed schema or approval authority;
- approval metadata, remembered approval keys, hooks, file rewriting, and dispatch can be derived from a live tool the model did not see.

Frequency and aggregate impact are unknown. The finding is limited to current source, historical precedent, owned execution, and synthetic controls.

## Current finding

Use two execution paths.

### Captured path

When `step_context.mcp.prepare_call(server, tool)` returns a `PreparedMcpCall`, execute that exact call. Its captured client, configuration, server metadata, tool information, and catalogue revision remain the authority for the operation.

Do not refresh and reroute that ordinary call to the session's newest client.

### Cached-only path

Only when the step binding contains the advertised `ToolInfo` but no `PreparedMcpCall` may Codex wait for startup and obtain a live prepared call.

Before pre-dispatch side effects, compare a deliberate structured callable-authority value.

### Structured callable-authority value

Include:

- raw MCP server name;
- raw MCP tool name;
- canonical callable namespace and name selected by the model;
- input schema;
- output schema;
- destructive, idempotent, and open-world hints;
- connector ID;
- OpenAI file-input rewrite map;
- execution-relevant tool metadata used for app identity, account authority, approval, rewriting, or dispatch.

Exclude or normalize:

- tool and namespace descriptions;
- tool title as a presentation label;
- connector display name and plugin display names;
- server origin and transport telemetry;
- parallel-call scheduling flags;
- cached `readOnlyHint`, which is deliberately cleared before advertisement.

A mismatch must return a model-visible unavailable/stale-authority result before approval registration, permission hooks, file rewriting, memory pollution marking, request metadata construction, or MCP dispatch.

### Claim table

| Claim | Evidence class | Exact support | Limit |
| --- | --- | --- | --- |
| A model step retains an exact MCP binding and fixed tool list | `source-read` | current `StepContext` | Does not prove current handler uses it for dispatch |
| `PreparedMcpCall` retains exact client and catalogue authority | `source-read` plus existing unit tests | current `binding.rs` and `binding_tests.rs` | Current call path may choose a newer prepared call first |
| Ordinary calls currently rebind to the newest runtime | `source-read` | current handler and `mcp_tool_call.rs` | Does not measure production frequency |
| Cached-only advertisements require a live fallback | `historical precedent` and `source-read` | public PR #35590 and current cache path | Does not authorize arbitrary live drift |
| Dynamic descriptions may drift while live execution remains compatible | `target-executed` upstream regression | `regular_mcp_definition_cache_preserves_live_session_state` | Other metadata remains independently authoritative |
| Cached `readOnlyHint` is deliberately weakened | `source-read` | current catalogue capture path | Destructive/open-world/idempotent hints remain in the proposed authority value |
| Whole serialized `ToolInfo` equality is too strict | `source-read` plus executed cache precedent | description drift and read-only weakening | Structured field selection still needs current-head execution and review |
| Reconnect route reaches ready thread clients | `target-executed` | source #89, run `30589313367`, exact `3/3` | Does not yet prove exact-one quiescence or failed-planning preservation |
| Publication ticket controls reject stale candidates | `target-executed` | source #75, run `30584055792`, exact `5/5`, complete `codex-mcp` package | Separate F84 publication finding owns current delivery state |

## System and ownership map

```text
model sampling request
→ StepContext
   ├── exact McpBinding
   ├── fixed advertised ToolInfo list
   └── finalized tool router
→ McpHandler retains advertised ToolInfo
→ call selection
   ├── captured PreparedMcpCall exists
   │   → execute exact captured client and authority
   └── cached-only advertisement
       → wait for live server
       → prepare live call
       → compare structured callable authority
          ├── equal: continue
          └── mismatch: fail before side effects
→ approval / hooks / file rewrite / request metadata
→ exact client dispatch
```

Adjacent owners remain separate:

- publication generation decides which runtime snapshot becomes current;
- explicit reload decides when ready clients must reconnect;
- timeout retirement and remote-effect certainty are now owned by F134 / Fieldwork PR #318;
- operation receipts and replay remain separate findings.

## Historical precedent

### Captured catalogue revisions

- Source: public Codex PR #34588.
- Principle supported: model-step calls must not reroute to a replacement client or catalogue revision.
- Important difference: the later cached-startup path introduced a legitimate no-prepared-call case.

### Cached definitions before startup

- Source: public Codex PR #35590.
- Principle supported: cached definitions may reach inference before a live client exists; execution waits for startup.
- Important difference: live rebinding was introduced for cached-only advertisements, not as a reason to discard captured authority for ordinary calls.

### Current cache regression

- Source: `codex-rs/core/tests/suite/mcp_tool_cache.rs` at `464237...`.
- Principle supported: process-specific descriptions may change while the same schema and operation execute on the live process.
- Important difference: the regression does not test schema, connector, file-input, or destructive-policy drift.

### Publication and reconnect

- Sources: owned Codex #75/#77 and #89/#90.
- Principle supported: stale runtime publication, ordinary reuse, and explicit freshness are independently testable.
- Important difference: runtime freshness does not by itself prove that a call was authorized by the catalogue the model saw.

## Approaches considered

### Retained: captured-first plus structured cached-only authority gate

This preserves the original captured-client invariant, keeps the intended startup-latency behavior, and creates a narrow fail-closed boundary before irreversible preparation.

### Declined: always use the newest live binding

This defeats request-scoped authority and permits a same-name replacement to inherit an old model decision.

### Declined: whole serialized `ToolInfo` equality

It rejects deliberate description drift and cached read-only weakening. It remains a useful conservative experiment, not the final compatibility policy.

### Declined: schema-only equality

It permits connector identity, destructive/open-world/idempotent semantics, file-input rewrite authority, and execution metadata to drift.

### Declined: never execute cached definitions

It removes the behavior intentionally introduced by #35590 instead of making that path safe.

### Deferred: one opaque hash over canonical authority

A hash may be useful for telemetry or durable receipts. Source code should first define and test the canonical structured fields so the policy remains reviewable and evolvable.

## Edge cases covered

| Edge case or control | Evidence | Result |
| --- | --- | --- |
| Slow older publication versus faster newer candidate | publication run `30584055792` | five exact controls passed |
| Explicit host reload versus ordinary runtime refresh | reconnect run `30589313367` | explicit reconnect and ordinary reuse controls passed |
| Public app-server reload route | reconnect run `30589313367` | route reached ready thread and observed one replacement initialization |
| Description drift across cached and live process | current upstream cache regression | live process executes despite old description |
| Cached read-only weakening | current source | read-only hint cleared before advertisement |
| Captured call retains old client after replacement | current binding unit test | pointer identity and authority retained |
| Full-structure equality carrier | authority #79 run `30584093534` | source transformer failed before tests; zero behavior evidence; carrier retired |

## Edge cases deferred or outside scope

| Edge case | Why deferred | Owner or reopening trigger |
| --- | --- | --- |
| Exact-one reconnect quiescence | current 3/3 route test observed only one increment | carrier #90 current head `cf9f876...` |
| Malformed reload preserves prior ready client | stronger negative control not in #89 | carrier #90 run `30595049466` |
| Structured authority candidate compilation and compatibility | current carrier queued | carrier #92 run `30595072484` |
| Zero approval/hook/file-rewrite/dispatch on mismatch | first authority carrier has only unit and existing integration controls | required successor integration carrier |
| Narrowing which `_meta` keys are execution authority | first candidate conservatively includes all tool metadata | review after target execution |
| Timeout cancellation and exact-client retirement | separate manager ownership | F134 / PR #318 |
| Restart-stable operation lineage | pointer identity is process-local | receipt/replay findings |
| Public proposal packaging | no authority and execution incomplete | explicit delivery request after acceptance |

## Exact execution and receipts

| Repository/head | Command or workflow | Platform/environment | Result | Evidence class |
| --- | --- | --- | --- | --- |
| `teamleaderleo/codex#75@c3373c717f3138ff5f0a979d12836f60800d2bcf` | run `30584055792`, job `91011123543` | owned exact-source carrier | `FIELDWORK_MCP_PUBLICATION_EXACT=5/5`; complete `codex-mcp` package passed | `target-executed` |
| publication carrier #77 cleanup `6f6f7f65b0c6605818680cd0a230f409eea2783a` | direct-diff and workflow absence | owned fork | empty direct diff; closed without merge | `carrier-retired` |
| authority carrier #79 executed head `d96bcf0b8d9b254474c1d27739bd40ee5c6a04fa` | run `30584093534`, job `91011250342` | owned carrier | transformer anchor failure; `0/2`; zero source behavior evidence | `carrier-only` |
| authority carrier #79 cleanup `1c1ded3a8c5f4eac44c2d21de29c84450a866793` | direct-diff and temporary-file absence | owned fork | empty direct diff; closed without merge | `carrier-retired` |
| `teamleaderleo/codex#89@51883318c606bfb60444032d16e500d51ff71da0` | run `30589313367`, job `91027881827` | owned current-route carrier | `FIELDWORK_MCP_RECONNECT_EXACT=3/3`; V8 passed | `target-executed` |
| reconnect carrier #82 cleanup `4b31b9c6956d6d1a01b6527734149fc090907b50` | direct-diff and temporary-file absence | owned fork | empty direct diff; closed without merge | `carrier-retired` |
| `teamleaderleo/codex#90@cf9f8765b67562679f7776169fb506a6a0bb7d94` | run `30595049466` | current public pin | queued; exact-one, quiet-period, failed-planning, and ready-client preservation controls | `target-test-prepared` |
| `teamleaderleo/codex#92@af6af7da8c337364a48954521dde5a7f741558f5` | run `30595072484` | current public pin | queued; structured authority and cache compatibility controls | `target-test-prepared` |

## Complete-diff and compatibility review

This Fieldwork PR changes documentation and retained evidence only.

Current compatibility surfaces examined:

- request-scoped `StepContext` and tool router;
- `McpBinding` and `PreparedMcpCall` lifetime;
- cached tool catalogue behavior;
- tool normalization and model-visible identity;
- approval policy, remembered approvals, and guardian metadata;
- permission hooks;
- OpenAI file argument rewriting;
- app and connector metadata;
- catalogue revision lease;
- explicit host reload and ordinary refresh reuse;
- runtime publication ordering.

The authority carrier is execution machinery and must publish a source-only successor only after success. It is not a delivery candidate. A successful 4/4 receipt remains insufficient for proposal promotion until end-to-end mismatch controls establish zero pre-dispatch side effects.

## Current disposition and desk routing

- Finding state: `comparative-evaluation-active`
- Review disposition: `EXECUTE and COMPARE`
- Review Queue entry: none
- Delivery lane: `not-entered`
- Exact next transition: settle current heads #90 and #92, then build the mismatch-before-side-effects integration successor if the structured direction survives
- Clearing condition: one current-source authority candidate passes captured-client, equivalent-cache, drift-rejection, and zero-side-effect controls and receives eligible exact-head review
- Required subgates: current source relation, exact tests, complete diff, compatibility, source-only publication, carrier retirement, independent review
- Autonomous work remaining: execution, repair if needed, negative integration controls, canonical reconciliation, and cleanup
- Non-delegable human decision: none currently

## Changes to the canonical conclusion

| Date | Record | Change in conclusion |
| --- | --- | --- |
| 2026-07-31 | initial F84 finding | Identified the conflict between captured authority and live cached startup |
| 2026-07-31 | authority carrier #79 failure | Recorded zero behavior evidence and retired whole-structure transformer carrier |
| 2026-07-31 | reconnect source #89 | Established the explicit public reload route and ordinary reuse boundary |
| 2026-07-31 | callable-authority fingerprint evidence | Rejected whole serialized equality and selected structured executable fields |
| 2026-07-31 | canonical base PR #292 moved to `00e9292...` | Renewed source identities, execution heads, limits, and next transitions |

## References

- Fieldwork issues #84, #134, #239, and #254.
- Fieldwork PRs #290, #292, and #318.
- `findings/F84-mcp-call-authority/evidence/20260731-lane-l-source-precedent-and-timeout.md`.
- `findings/F84-mcp-call-authority/evidence/20260731-authority-carrier-failure.md`.
- `findings/F84-mcp-call-authority/evidence/20260731-callable-authority-fingerprint.md`.
- Owned Codex PRs #75, #77, #79, #82, #89, #90, and #92.
- Public Codex source through `4642370542739d5dd080b0c87a9de06a6435d3db`, read-only.
- Public Codex PRs #34588 and #35590, read-only.
- Public upstream interaction: none.
