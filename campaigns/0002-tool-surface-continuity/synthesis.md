# Final Synthesis

## In simple words

Campaign #31 began with one user-visible symptom: a conversation could lose tools that still appeared installed, authenticated, previously used, or available elsewhere. The completed lanes show that this symptom has several independent causes.

The common solution is a diagnostic receipt, not a common repair. The receipt records bounded counts, digests, provenance, lifecycle state, result identity, and unavailable views. It identifies the earliest observable divergence and then selects a reason-specific recovery direction.

## Final model

A current capability journey crosses these ordered boundaries:

1. saved host declarations and current host declarations;
2. effective host reconciliation;
3. logical request planning;
4. direct wire serialization and prior-response reuse;
5. live global catalogue and remote server identity;
6. thread or step binding;
7. router registration;
8. model-visible direct exposure;
9. executable discovery;
10. required executable dispatch;
11. authoritative handler or provider completion;
12. durable and normalized result identity;
13. client result delivery;
14. displayed or status projection;
15. fallback authority selection.

Agreement at one boundary establishes only that boundary. Later views can agree with a stale earlier view, and earlier views can remain unavailable while direct execution succeeds.

## Accepted conclusions

### 1. Cold reconstruction combines sticky host state with refreshed runtime state

L01 found that saved dynamic tools and selected capability roots survive cold resume, fork, restart, and upgrade. Native, model, configuration, environment, MCP, connector, and discovery inputs rebuild from the current runtime. Public resume and fork expose no equivalent current-host replacement fields, and an empty dynamic-tool input means recovery rather than explicit clearing.

The missing contract is an explicit host policy: preserve saved, replace from current host, clear, or reject on mismatch.

### 2. Logical request equality does not establish direct wire equality

L02 found a distinct Responses Lite incremental WebSocket seam. A clean startup prewarm can make the first generated turn reference the previous response and omit the already-sent additional-tool prefix. HTTP, fresh WebSocket, reconnect, restart, changed-manifest, and non-Lite controls send the capability information directly.

The client source establishes the omission and inheritance dependency. Private server retention remains outside the public evidence.

### 3. Compaction can install a checkpoint after identity already became ambiguous

L03 found the first deterministic identity failure before replacement history installation. Missing output becomes a prompt-only synthetic `aborted` result. Duplicate and reordered outputs pass through. A result arriving after replacement becomes orphaned and disappears from the next prompt. Local, remote v1, and remote v2 then replace raw call/result identity, and resume or fork treats the newest replacement as authoritative.

Mutation safety therefore requires a raw-history gate before compaction, durable operation receipts, and late, duplicate, and causal-order reconciliation.

### 4. A healthy connection can retain a stale startup catalogue

L04 found that ordinary MCP runtime replacement can reuse a ready client when connection configuration is unchanged. The reuse identity excludes remote server identity and catalogue digest, while the managed client retains startup-captured server information and tools.

After a stub-to-real transition, the global server surface changes first. The binding, router, and model view remain mutually consistent with the stale client. Fresh thread, explicit reconnect, full restart, and connection-identity change converge.

### 5. A registered deferred runtime can become unreachable

L05 found that built-in MCP, app, and multi-agent paths generally direct-expose when request search is unavailable. Dynamic host and extension runtimes can still select deferred exposure independently. The final planner can also filter a deferred runtime whose searchable metadata is absent.

The compatibility-first repair is direct exposure at the final planner boundary. A typed planner rejection is the stricter alternative.

### 6. Capability absence and fallback authority are separate decisions

L07 found no automatic fallback in the reviewed public router. A later shell, protocol, browser, connector, or subagent action has its own credential, account, approval, scope, actor, identity, audit, and recovery properties.

The synthetic authority gate allowed five equivalent routes, required explicit approval for five changed-authority routes, and failed closed for three mutation routes. An availability-only selector silently rerouted all thirteen cases.

### 7. Current ChatGPT coexistence can remain healthy through a context boundary

L08 completed two reversible alternating GitHub connector and Stensibly developer-MCP lifecycles. Both survived sustained use, a host context-summary boundary, post-boundary mutation, and catalogue rediscovery. Every mutation returned a typed success and received a separate read confirmation.

The negative result narrows future product fieldwork to reconnect, application restart, auth refresh, timing, or a recurrence trigger. Exact private router, advertisement, policy, and transport views remain unavailable.

### 8. Display is a separate projection

Campaign evidence includes a control where status reports zero while invocation succeeds. Display should consume the latest receipt and expose age and unavailable views. It should never overwrite runtime state or trigger repair alone.

## Diagnostic receipt v1

L06 normalizes eight retained cases and applies causal precedence:

| First layer | Typed reason | Recovery direction |
| --- | --- | --- |
| host reconciliation | `saved_host_state_wins` | require preserve, replace, clear, or reject policy |
| wire request | `wire_manifest_omitted` | discard incompatible incremental reuse and send a full first generated request |
| binding | `stale_binding` | relist or reconnect, validate remote identity and catalogue digest, capture a new binding |
| discovery | `deferred_without_loader` | direct-expose or reject planning |
| executable | `required_capability_absent` | stop the intended action and evaluate fallback authority |
| result persistence | `result_identity_ambiguous` | pause mutation continuation and reconcile before retry |
| display | `display_underreports_execution` | refresh display projection without changing execution |

The healthy L08 receipt returns `no_observed_divergence` while listing unavailable saved-host, logical request, wire request, binding, router, model-exposure, and display views.

## Repair architecture

### Instrument first

Emit receipt views at lifecycle, request, catalogue, binding, router, planner, dispatch, completion, persistence, delivery, and display seams. Use process- or installation-scoped keyed digests where repeated catalogue probing could reveal membership.

### Repair by typed reason

Each repair should accept one typed state and preserve all earlier and later invariants:

- host replacement policy should not change current runtime planning;
- full-first-generated request should not change logical tools;
- hard refresh should not mutate an already captured step;
- direct exposure should not create a new authority path;
- compaction gate should not infer mutation failure from missing delivery;
- display refresh should not alter execution;
- fallback approval should not replay an ambiguous mutation.

## Competing hypotheses resolved

- One universal process-wide authentication failure is weakened by same-process fresh-task controls.
- One universal old-thread explanation is weakened by fresh-start and planner failures.
- One router/model race is weakened by request-scoped binding consistency.
- One compaction trigger is weakened by transport, catalogue, and host-provenance cases outside compaction.
- One ChatGPT coexistence defect is weakened by the current healthy integration run.
- One reload repair is rejected because each lane requires a different authority and recovery contract.

## Remaining unknowns

- private ChatGPT catalogue assembly, policy state, transport identity, reconnect, and restart;
- private Responses server inheritance after startup prewarm;
- compiled Codex end-to-end behavior for the source-derived host and MCP fixtures;
- operational frequency of each class;
- keyed digest and retention policy suitable for product diagnostics.

These unknowns do not block the first owned-fork implementation campaigns.

## Final decision

Close broad research. Accept receipt v1. Promote mutation identity around compaction first because ambiguous side effects carry the highest consequence. Promote host lifecycle and MCP catalogue refresh second. Keep request exposure and fallback authority as separate follow-ons. Preserve ChatGPT reconnect/restart as a conditional field trial.
