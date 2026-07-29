# Cross-lane follow-up

Review date: 2026-07-30  
Lane: L05 / issue #40  
Reviewed campaign lanes: #35, #37, #38, #39, #43, #44, and #46

## What changed

The original L05 result remains valid: a present deferred family needs an executable route that can load that family.

The campaign findings broaden the checkpoint:

1. L02 (#37 / PR #58) found that the first generated Responses Lite WebSocket turn can omit the `AdditionalTools` prefix and rely on `previous_response_id`. A logical `tool_search` entry therefore does not prove effective delivery.
2. L04 (#39 / PR #62) reproduced a stable-endpoint stub-to-real transition where the active thread binding, router, and model declaration remained consistently stale. An executable loader can therefore return zero or old results while the current server catalogue contains different tools.
3. L01 (#35 / PR #61) found that host dynamic tools and selected roots are sticky saved declarations. A valid loader can expose an old saved generation.
4. L03 (#38 / PR #64) located tool-call/result identity loss before compaction installation. This is downstream of discovery and should remain a separate diagnostic state.
5. L07 (#44 / PR #60) showed that shell, protocol, connector, browser, or subagent reroutes can change authority even when they restore availability.
6. L08 (#46 / PR #57) completed sustained alternating GitHub/developer-MCP use and a host context-summary boundary without capability loss. Repeating that trigger alone has low expected information gain.

## Updated diagnosis

The public reports around `gpt-5.6-sol` support the symptom:

```text
deferred family
+ no usable native loader
= unreachable native tools
```

Four paths can produce that observation:

| Candidate | First divergent checkpoint | Discriminator |
|---|---|---|
| private model/profile planner mismatch | planned deferred family versus planned loader | planner family and loader digests |
| generic dynamic/extension invariant gap | registered deferred runtime versus searchable index | per-runtime exposure and search metadata |
| incremental transport omission | logical request versus wire/inherited manifest | logical digest, wire digest, previous-response receipt |
| stale catalogue/binding | current host catalogue versus thread binding/search index | catalogue, binding, and search-index generation digests |

The generic dynamic/extension gap is a source-supported issue. The exact owning path for the reported private sessions remains open.

## Ranked exploration

### High information gain

1. **First generated Responses Lite turn A/B.** Capture privacy-safe logical and wire tool digests. Compare full first generated request against incremental reuse. Require an explicit inherited-manifest receipt before treating an omitted loader as delivered.
2. **Search index and binding generation.** Record current host catalogue digest, thread binding digest, router digest, deferred search-index digest, and the generation used by each search result.
3. **Private profile parity.** Compare model slug, effective `supports_search_tool`, provider namespace capability, tool mode, and effective loader presence without retaining prompts or schemas.
4. **Dynamic host replacement semantics.** Exercise saved deferred tools across resume/fork with explicit preserve, clear, and replace inputs when a writable owned fork exists.

### Useful, secondary

5. Add compiled Codex tests covering deferred dynamic and extension runtimes under search-disabled model/provider combinations.
6. Feed L05 fixtures into L06 and verify first-divergence classification for logical absence, wire omission, stale catalogue, and stale saved provenance.
7. Add authority comparison before any automated workaround after discovery failure.

### Low information gain now

- more same-conversation sustained-use and context-summary-only trials;
- another planner-only configured-MCP test without transport or catalogue digests;
- model-quality testing after valid delivery;
- treating every zero-result search as a loader failure.

## Receipt fields proposed to L06

```text
effective_model_profile_digest
provider_capability_digest
host_catalogue_digest
thread_binding_digest
router_registered_digest
planner_advertised_digest
deferred_search_index_digest
wire_tool_manifest_digest
inherited_tool_manifest_digest
inherited_manifest_verified
dynamic_tool_saved_generation
dynamic_tool_current_generation
loader_presence_reason
search_result_generation
```

The digests should cover stable sanitized identifiers and typed state only. Arguments, prompts, credentials, private names, schemas, and provider payloads stay excluded.

## Repair implications

- Planner gap: direct-expose the affected runtime or return a typed planner error.
- Wire omission: send the loader directly or require verified inheritance.
- Stale catalogue: rebuild/relist the client and publish a new binding/index generation.
- Stale saved host declaration: add explicit preserve/clear/replace lifecycle semantics.
- Fallback: compare authority and require approval or fail closed when the route changes it.
