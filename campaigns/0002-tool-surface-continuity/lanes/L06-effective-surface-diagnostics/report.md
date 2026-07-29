# L06 — Effective tool-surface diagnostics

## In simple words

A conversation does not have one tool list. Saved host declarations, the logical request, the serialized request, the current server catalogue, the thread binding, router handlers, model exposure, discovery, execution, completion, durable results, client delivery, and status display can each hold a different view.

This lane defines one privacy-safe receipt and tests it against the accepted Campaign #31 fixtures. The receipt correctly identifies the earliest observable divergence in every retained failing case and returns `no_observed_divergence` for the healthy ChatGPT coexistence trial while explicitly listing the host views that remain unavailable.

The result is diagnostic policy, not an automatic reload rule. Each failure class retains its own repair boundary.

## Assignment and boundary

- Campaign: #31
- Lane issue: #43
- Owned path: `campaigns/0002-tool-surface-continuity/lanes/L06-effective-surface-diagnostics/`
- Public source pin: [Codex `3725f02cf38d856bc82bb46dd68ab61bb96ec6fc`](https://redirect.github.com/openai/codex/commit/3725f02cf38d856bc82bb46dd68ab61bb96ec6fc)
- Campaign base at takeover: `teamleaderleo/fieldwork@2e8117d85c7eb787c2901697f60ea503566139e7`
- Retrieval and run date: 2026-07-30
- Claim scope supported: interface, with source-derived instrumentation seams
- External source interaction: read-only
- Upstream contact authorized: false

The retained receipt excludes prompts, tool arguments, tool names, schemas, credentials, account identities, private resource contents, provider payloads, and opaque policy data.

## Durable artifacts

- `receipt.schema.json` — versioned receipt envelope and bounded per-view fields
- `fixtures.json` — normalized privacy-safe receipts derived from accepted campaign evidence
- `classify_receipts.py` — deterministic first-divergence classifier and privacy check
- `test_classify_receipts.py` — focused unit tests
- `results/latest.json` — authoritative classification output
- `run-output.txt` and `test-output.txt` — retained command output
- `commands.md` — execution and interpretation guide

## Receipt contract

### Envelope

Each receipt records:

- schema version and receipt identity;
- prior-receipt digest when continuity comparison is available;
- source/build boundary, model/profile, transport, lifecycle transition, and request kind when observable;
- operation class: read, mutation, or mixed;
- explicit `unavailable` states rather than inferred values.

### Ordered diagnostic views

The classifier evaluates causal order rather than UI order:

1. saved host, current host, and effective host reconciliation;
2. logical request manifest;
3. serialized wire request manifest;
4. global catalogue;
5. current thread or step binding;
6. registered router inventory;
7. model-visible direct exposure;
8. executable discovery route;
9. required executable path;
10. authoritative server or handler completion;
11. durable and normalized result identity;
12. client result delivery;
13. displayed or status projection;
14. fallback authority decision.

A view contains only a typed state plus bounded metadata such as count, stable digest, identity digest, provenance class, required flag, discovery executability, result-identity state, or fallback decision.

### Receipt result

The classifier returns:

- `divergence` or `no_observed_divergence`;
- earliest observable divergent layer;
- typed reason;
- bounded recovery direction;
- every unavailable view.

`no_observed_divergence` means all measured views and smoke tests agreed for that run. It does not upgrade unavailable private views into confirmed agreement.

## Classification precedence

The current v1 rules are deliberately narrow:

| Condition | First layer | Typed reason |
| --- | --- | --- |
| saved and current host declarations differ and the effective set uses saved state | host reconciliation | `saved_host_state_wins` |
| logical and serialized manifests differ | wire request | `wire_manifest_omitted` |
| current global catalogue differs from the captured binding | binding | `stale_binding` |
| a deferred family has no executable loader | discovery | `deferred_without_loader` |
| a required action has no current executable path | executable | `required_capability_absent` |
| completion exists while durable result identity is missing, duplicated, reordered, or orphaned | result persistence | `result_identity_ambiguous` |
| execution succeeds while display reports absence | display | `display_underreports_execution` |

Later versions can add typed auth, policy, unreachable-server, handler-missing, execution-failed, and client-delivery rules after retained fixtures establish those states.

## Fixture results

Command result: **8 receipts classified, 7 divergences, 1 healthy negative result, 0 expectation mismatches.**

| Evidence source | Transition | First observable divergence | Typed reason | Result |
| --- | --- | --- | --- | --- |
| L01 / #35 | cold resume | host reconciliation | `saved_host_state_wins` | saved dynamic declarations and roots remain authoritative over current host values |
| L02 / #37 | clean Responses Lite prewarm reuse | wire request | `wire_manifest_omitted` | logical additional tools exist while the incremental first generated request omits them |
| L03 / #38 | late result after compaction | result persistence | `result_identity_ambiguous` | authoritative completion precedes an orphaned result that disappears from the next prompt |
| L04 / #39 | stub-to-real ordinary refresh | binding | `stale_binding` | live global catalogue changes while the reused client binding, router, and model view remain old |
| L05 / #40 | final deferred planning | discovery | `deferred_without_loader` | the runtime remains registered but the request has neither direct exposure nor an executable loader |
| L07 / #44 | fallback selection | executable | `required_capability_absent` | the expected action path is absent; the next decision must compare fallback authority |
| L08 / #46 | context-summary boundary | none observed | none | connector and developer MCP reads and mutations remain successful; binding, router, and exact advertisement stay unavailable |
| Campaign evidence cluster H | status projection | display | `display_underreports_execution` | status reports zero while binding, advertisement, execution, completion, and delivery remain present |

The output preserves the campaign’s central separation: mutation ambiguity, host provenance, transport inheritance, stale client binding, unloadable deferral, missing execution, and stale display are different conditions.

## Source and instrumentation map

### Host lifecycle boundary

Consume the provenance fields mapped by L01 at thread start, live reconnect, cold resume, fork, restart, and runtime upgrade. Emit saved/current/effective host digests and the selected reconciliation policy before a new step is built.

Candidate seam: app-server thread start/resume/fork composition and `SessionMeta` recovery.

### Logical request and wire request

L02 established a shared logical request builder and a distinct incremental WebSocket serialization path. Emit one digest after logical tool planning and another after direct wire serialization. Record previous-response reuse and prewarm identity without retaining payload contents.

Candidate seam: Responses request preparation immediately before HTTP or WebSocket transmission.

### Global catalogue, binding, router, and model exposure

L04 established that ordinary runtime replacement can reuse a ready client whose startup catalogue remains captured. Emit global catalogue and remote identity digests before publication, binding digests at `McpBinding` capture, router digest at registration, and model-visible digest beside the finalized tool plan.

Candidate seams:

- MCP runtime replacement and fresh replacement;
- connection reuse decision;
- binding capture;
- tool-router registry and model-visible specification plan.

### Deferred discovery

L05 established that final planning can retain a deferred runtime while search is disabled or searchable metadata is missing. Emit deferred-family count, discovery tool class, loader executability, and a typed reason for any filtered runtime.

Candidate seam: final tool exposure planner after all native, dynamic, extension, MCP, app, model, provider, and code-mode decisions have been combined.

### Completion, result persistence, and delivery

L03 established that the first call/result identity divergence can occur before replacement history installation. Emit operation identity state before every compaction path, after handler or provider completion, after normalized history persistence, and at client delivery acknowledgement.

Candidate seams:

- raw-history pre-compaction validator;
- compaction replacement installation;
- late-result reconciliation;
- output normalization;
- client result-delivery boundary.

### Display

Display is a consumer of the receipt rather than an authority source. Status and doctor output should report the latest receipt identity, source age, and unavailable fields. It should never overwrite the runtime receipt or trigger a repair by itself.

### Fallback authority

L07 supplies the authority comparison vocabulary. When the required executable path is absent, append only an authority-delta count/digest and a decision enum: `allow_equivalent`, `require_explicit_approval`, or `fail_closed`.

## Privacy review

The executable privacy validator rejects obvious high-cardinality or sensitive keys, including prompts, arguments, credentials, schemas, tool names, provider payloads, account IDs, access tokens, and secrets.

The receipt still permits stable digests. Deployments should use a process- or installation-scoped keyed digest when raw catalogue membership could be inferred through repeated probing. Receipt retention should be bounded, and detailed receipts should remain local unless an explicit diagnostic export is requested.

## Recovery contract

The receipt supplies a reason-specific direction rather than a universal action:

- host mismatch: require an explicit preserve, replace, clear, or reject policy;
- wire omission: discard incompatible incremental reuse and send a full first generated request;
- stale binding: relist or reconnect, validate remote identity and catalogue digest, and capture a new binding;
- deferred without loader: direct-expose the family or reject planning;
- missing required execution: stop the intended action and compare fallback authority;
- ambiguous result identity: pause mutation continuation and reconcile before retry;
- stale display: refresh display projection while preserving execution state.

## Negative findings

- One request-scoped binding can keep router and model advertisement internally consistent while both remain stale.
- A healthy integration run can contain unavailable router and model views. The classifier preserves that uncertainty.
- Display absence alone cannot establish execution absence.
- Raw catalogue counts alone cannot diagnose Responses Lite inheritance.
- A fallback option does not establish equivalent authority.
- A synthetic `aborted` prompt result does not prove a mutation failed before completion.

## Limits

- The classifier consumes normalized retained evidence; it is not compiled into Codex or ChatGPT.
- Exact private ChatGPT model advertisement, router registration, policy snapshot, transport identity, reconnect, and application restart remain unavailable.
- The L01 fixture models observed precedence branches rather than a full compiled host mismatch journey.
- The L02 fixture proves the public client wire seam and leaves private server inheritance unresolved.
- The display control is source/report-derived campaign evidence rather than a new live reproduction in this lane.
- Counts and digests identify divergence; they do not reveal which individual tool changed.

## Adoption decision

Accept receipt v1 as the shared diagnostic contract for Campaign #31. Promote a small owned-fork implementation that emits receipts without changing execution. Use the retained cases as golden regression inputs.

Instrumentation should land before automatic repair work so each candidate repair can prove which layer changed and which layers remained stable.

## Ranked next work

1. **P0 mutation checkpoint:** add the pre-compaction identity gate and durable operation receipt fields; use L03 missing, duplicate, reordered, and late cases.
2. **P0 capability lifecycle checkpoint:** add host reconciliation policy fields and MCP remote identity/catalogue digest publication; use L01 and L04 cases.
3. **P1 request exposure checkpoint:** add logical/wire digest comparison and deferred-loader invariant; use L02 and L05 cases.
4. **P1 authority receipt:** attach the L07 decision enum after required execution absence.
5. **Conditional product trial:** exercise ChatGPT reconnect and application restart when the host exposes those controls or the incident recurs.

## Stop decision

Broad reconnaissance is complete. Further research should begin only when a focused implementation test fails, a private host control becomes available, or a new incident produces a previously unseen typed state.
