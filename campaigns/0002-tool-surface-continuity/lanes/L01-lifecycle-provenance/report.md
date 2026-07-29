# L01 — lifecycle capability provenance

Issue: [#35](https://redirect.github.com/teamleaderleo/fieldwork/issues/35)  
Campaign: [#31](https://redirect.github.com/teamleaderleo/fieldwork/issues/31)  
Synthesis PR: [#51](https://redirect.github.com/teamleaderleo/fieldwork/pull/51)  
Worker branch: `lane/35-lifecycle-provenance`

## Result in plain language

Codex has at least three capability lifetimes, plus a transport reuse layer.

Thread-scoped host declarations are sticky. Dynamic tools and host-selected capability roots are saved in thread metadata. Cold resume, fork, process restart, and runtime upgrade recover those saved declarations. The public resume and fork APIs provide no replacement fields for either set.

Session-scoped runtime snapshots can also be sticky. A thread-owned MCP runtime may reuse a ready client and its startup-captured catalogue when connection identity remains unchanged. Recomputing desired MCP configuration therefore does not guarantee that the executable binding has learned a changed server catalogue.

Request planning is rebuilt from current inputs. Native tools, model/profile gates, feature flags, permissions, current environments, extensions, current authentication, desired MCP configuration, and connector discovery are captured for each session or request step.

Responses transport can add another reuse boundary. A Responses Lite startup-prewarm handoff may send the first generated turn through `previous_response_id` without directly repeating the `additional_tools` input prefix. A logical discovery loader therefore counts as delivered only when it appears on the generated wire request or the same manifest is verified as inherited from the previous response.

These lifetimes produce a mixed candidate surface:

- saved dynamic tools are preserved;
- saved thread roots are preserved;
- current ready environment roots are merged after thread roots;
- thread roots win duplicate root IDs, including location conflicts;
- native/core tools are replanned from current request state;
- desired MCP/app inputs are recomputed, while an unchanged live connection can retain a stale catalogue and binding;
- a live reconnect rejoins the existing in-memory session and its session-owned snapshots;
- a cold reconnect creates a new session from saved history plus current runtime inputs;
- transport reuse can make direct wire advertisement depend on retained prior-response state;
- a preserved dynamic tool can have a valid loader while still belonging to a stale saved host generation.

The mismatch fixture demonstrates the unresolved host problem: a saved dynamic tool set `host_old` survives cold resume even when the current host set is `host_new`. The current host cannot express that replacement through `thread/resume` or `thread/fork`.

## Revisions and retrieval boundary

| Source | Revision | Role |
|---|---|---|
| Public Codex campaign pin | `openai/codex@3725f02cf38d856bc82bb46dd68ab61bb96ec6fc` | primary public source and retained campaign evidence |
| Public Codex current-head recheck | `openai/codex@7579a2b41353470efaef93c08b4a21068a366b7f` | seven-commit delta recheck after campaign closeout |
| Owned Codex | `teamleaderleo/codex@2b7b93081361b77f8ddaceaf362a09765b4153bf` | owned comparison |
| Official Rust MCP SDK | `modelcontextprotocol/rust-sdk@cb50ae7890d8a5daacae1a4ad95f395f06733c07` | `rmcp` 3.0.0 release line plus current post-release fix |
| Retrieval boundary | `2026-07-30` | campaign closeout and dependency recheck |

Public upstream remained read-only. No upstream contact was made.

## Host contract before refresh semantics

Any refresh proposal needs an owner and lifetime contract for each input.

| Input | Proposed owner contract derived from current behavior | Lifetime |
|---|---|---|
| `dynamicTools` supplied by the host | The host declares a complete thread-scoped callable set at thread creation. Codex persists it and treats it as part of the thread identity. | sticky until an explicit host replacement or clear operation exists |
| `selectedCapabilityRoots` supplied by the host | The host selects thread-scoped capability identities. Codex persists the selection. Availability and resolved executor state may change independently. | selection is sticky; readiness is current |
| roots supplied by current environments | The environment supplies additive ready roots for the captured request step. | request-step snapshot |
| native/core tool plan | Codex derives the plan from the current model profile, provider capabilities, configuration, features, permissions, session source, and current environments. | rebuilt per request step |
| MCP/app/connector tools | Codex recomputes desired runtime inputs from current auth, config, manager state, selected-root readiness, and discovery. A matching ready client can retain its startup-captured catalogue; the request-step binding is then built from that client. | desired inputs: request-step; ready client/catalogue: session-scoped until reconnect or rebuild; binding: request-step snapshot |
| multi-agent version | Saved thread metadata wins; an inherited `Disabled` value wins first; legacy resumed/forked threads without metadata fall back to V1. | compatibility-selected at session creation |
| live reconnect | The existing in-memory session owns the candidate surface, including session-owned MCP client and catalogue snapshots. | existing session lifetime |
| cold reconnect / restart / upgrade | Saved thread declarations combine with a newly created runtime and current planning inputs. | new session lifetime |
| Responses startup-prewarm state | The transport may reuse a prior response whose input carried the logical tool declarations. Omitted declarations require a receipt proving that the same manifest was inherited. | WebSocket client-session / previous-response lifetime |

This contract supports continuity without granting an implicit host refresh. A host-driven replacement needs an explicit request, complete snapshot semantics, and a receipt describing the resulting surface.

## Source map

### Saved thread metadata

`SessionMeta` persists `dynamic_tools`, `selected_capability_roots`, and `multi_agent_version`:

- [protocol `SessionMeta`](https://redirect.github.com/openai/codex/blob/3725f02cf38d856bc82bb46dd68ab61bb96ec6fc/codex-rs/protocol/src/protocol.rs#L3060-L3118)
- [history getters for dynamic tools and selected roots](https://redirect.github.com/openai/codex/blob/3725f02cf38d856bc82bb46dd68ab61bb96ec6fc/codex-rs/protocol/src/protocol.rs#L2642-L2662)

New and forked persistent threads write the effective dynamic tools and selected roots back into thread metadata:

- [session persistence inputs](https://redirect.github.com/openai/codex/blob/3725f02cf38d856bc82bb46dd68ab61bb96ec6fc/codex-rs/core/src/session/session.rs#L593-L641)

### Current host state

`thread/start` exposes both host capability inputs:

- [start protocol fields](https://redirect.github.com/openai/codex/blob/3725f02cf38d856bc82bb46dd68ab61bb96ec6fc/codex-rs/app-server-protocol/src/protocol/v2/thread.rs#L59-L140)
- [start request forwarding and extension initialization](https://redirect.github.com/openai/codex/blob/3725f02cf38d856bc82bb46dd68ab61bb96ec6fc/codex-rs/app-server/src/request_processors/thread_processor.rs#L974-L1084)
- [start options receive dynamic tools and selected roots](https://redirect.github.com/openai/codex/blob/3725f02cf38d856bc82bb46dd68ab61bb96ec6fc/codex-rs/app-server/src/request_processors/thread_processor.rs#L1243-L1289)

`thread/resume` and `thread/fork` expose configuration overrides while omitting `dynamicTools` and `selectedCapabilityRoots`:

- [resume protocol](https://redirect.github.com/openai/codex/blob/3725f02cf38d856bc82bb46dd68ab61bb96ec6fc/codex-rs/app-server-protocol/src/protocol/v2/thread.rs#L327-L420)
- [fork protocol](https://redirect.github.com/openai/codex/blob/3725f02cf38d856bc82bb46dd68ab61bb96ec6fc/codex-rs/app-server-protocol/src/protocol/v2/thread.rs#L511-L594)

### Saved-versus-current precedence

Dynamic tools use an overloaded empty-vector rule:

1. a non-empty caller-supplied vector wins;
2. an empty vector falls back to saved `SessionMeta.dynamic_tools`;
3. absent saved metadata becomes an empty set.

- [dynamic-tool precedence](https://redirect.github.com/openai/codex/blob/3725f02cf38d856bc82bb46dd68ab61bb96ec6fc/codex-rs/core/src/session/mod.rs#L650-L673)

Cold resume and fork pass an empty dynamic-tool vector, activating saved fallback:

- [resume passes `Vec::new()`](https://redirect.github.com/openai/codex/blob/3725f02cf38d856bc82bb46dd68ab61bb96ec6fc/codex-rs/core/src/thread_manager.rs#L858-L936)
- [fork passes `Vec::new()`](https://redirect.github.com/openai/codex/blob/3725f02cf38d856bc82bb46dd68ab61bb96ec6fc/codex-rs/core/src/thread_manager.rs#L1190-L1225)

Selected roots use internal extension initialization first, saved history second:

- [selected-root initialization precedence](https://redirect.github.com/openai/codex/blob/3725f02cf38d856bc82bb46dd68ab61bb96ec6fc/codex-rs/core/src/session/session.rs#L593-L603)

The public start path inserts selected roots only when the supplied list is non-empty. Public resume and fork provide no equivalent insertion point.

### Current configuration and model/profile planning

Cold resume and fork load current configuration using current config-manager logic, while applying persisted model metadata and request overrides where defined:

- [cold resume configuration load](https://redirect.github.com/openai/codex/blob/3725f02cf38d856bc82bb46dd68ab61bb96ec6fc/codex-rs/app-server/src/request_processors/thread_processor.rs#L3028-L3217)
- [fork configuration load](https://redirect.github.com/openai/codex/blob/3725f02cf38d856bc82bb46dd68ab61bb96ec6fc/codex-rs/app-server/src/request_processors/thread_processor.rs#L3978-L4225)

Each request step captures current environments, selected-root readiness, executor discovery, desired MCP inputs, recommendations, extensions, and then obtains a binding and builds the tool router:

- [step capture](https://redirect.github.com/openai/codex/blob/3725f02cf38d856bc82bb46dd68ab61bb96ec6fc/codex-rs/core/src/session/mod.rs#L3027-L3103)
- [current MCP and connector inputs](https://redirect.github.com/openai/codex/blob/3725f02cf38d856bc82bb46dd68ab61bb96ec6fc/codex-rs/core/src/session/turn.rs#L1464-L1580)
- [tool planning context](https://redirect.github.com/openai/codex/blob/3725f02cf38d856bc82bb46dd68ab61bb96ec6fc/codex-rs/core/src/tools/spec_plan.rs#L144-L213)
- [native sources selected by current config, model, features, permissions, and environments](https://redirect.github.com/openai/codex/blob/3725f02cf38d856bc82bb46dd68ab61bb96ec6fc/codex-rs/core/src/tools/spec_plan.rs#L609-L775)

Cross-lane evidence from L04 shows that the desired MCP projection and the executable catalogue have different lifetimes. Ordinary refresh can reuse a matching ready client and preserve its startup tool vector. Fresh thread creation, explicit reconnect, full restart, or a connection-identity change creates a fresh client and converges the measured catalogue, binding, router, model declaration, and execution layers.

### Current environment state and root merge

Thread roots are iterated first. Current environment roots follow. Duplicate IDs retain the first root. A conflicting later location emits a warning and is ignored:

- [selected-root merge and resolution](https://redirect.github.com/openai/codex/blob/3725f02cf38d856bc82bb46dd68ab61bb96ec6fc/codex-rs/core/src/session/mcp.rs#L316-L368)

The upstream integration test persists a selected root across restart, observes its tools disappear while the selected executor is unavailable, and observes them return after the environment is reattached:

- [selected capability availability and resume test](https://redirect.github.com/openai/codex/blob/3725f02cf38d856bc82bb46dd68ab61bb96ec6fc/codex-rs/app-server/tests/suite/v2/selected_capability_stack.rs#L68-L266)

### Compatibility logic

Multi-agent selection uses this order:

1. inherited `Disabled`;
2. saved history version;
3. inherited version;
4. legacy V1 for resumed or forked history without runtime metadata.

- [multi-agent compatibility precedence](https://redirect.github.com/openai/codex/blob/3725f02cf38d856bc82bb46dd68ab61bb96ec6fc/codex-rs/core/src/session/mod.rs#L476-L492)

### Live reconnect

A running `thread/resume` request rejoins the loaded session. Capability replacement fields are absent. Configuration overrides that differ from the active session are ignored while another observer can still see the session:

- [running-thread resume](https://redirect.github.com/openai/codex/blob/3725f02cf38d856bc82bb46dd68ab61bb96ec6fc/codex-rs/app-server/src/request_processors/thread_processor.rs#L3445-L3562)
- [core returns the existing running thread](https://redirect.github.com/openai/codex/blob/3725f02cf38d856bc82bb46dd68ab61bb96ec6fc/codex-rs/core/src/thread_manager.rs#L1721-L1770)

## Provenance classes

| Input | Provenance class | Notes |
|---|---|---|
| saved dynamic tools | saved thread metadata | used on resume/fork/restart/upgrade because the caller passes empty |
| saved selected roots | saved thread metadata | used unless an internal host supplies extension initialization |
| `thread/start.dynamicTools` | current host state | non-empty set wins at new thread creation |
| `thread/start.selectedCapabilityRoots` | current host state | inserted into thread extension initialization |
| environment-selected roots | current host/environment state | additive per-step roots after thread roots |
| model/provider profile | model/profile planning | current model manager and provider capabilities |
| native/core tools | current configuration + model/profile planning | rebuilt per request step |
| permission-gated tools | current configuration | current permission profile and feature gates |
| MCP/app desired state | current host state + current configuration | current auth, manager state, connectors, selected-root readiness; recomputed for the request step |
| MCP ready client/catalogue | another source: live in-memory session | can preserve startup-captured server identity and tool vector across ordinary refresh when connection identity matches |
| dynamic tool handler/specs | saved thread metadata or current host start input | then inserted into the current router; visibility still depends on direct/deferred planning and discovery availability |
| multi-agent surface | compatibility logic | saved metadata and legacy fallback |
| running session surface | another source: live in-memory session | existing session wins |
| current runtime binary behavior | another source: current revision | affects all rebuilt planning after restart or upgrade |
| Responses previous-response state | another source: transport session | can carry the logical tool prefix across a prewarm-to-turn incremental handoff |

## Transition table

| Lifecycle transition | Saved/session inputs | Current inputs | Winner / composition | Observed outcome |
|---|---|---|---|---|
| thread start | none | host dynamic tools, host roots, config, model/profile, environments, MCP/auth | current host thread declarations; current request plan; new session runtime | build |
| live reconnect to running thread | existing in-memory session, including MCP ready clients and catalogue snapshots | listener/client attachment state | live session wins; differing overrides are ignored | preserve the loaded candidate surface |
| ordinary in-session MCP refresh | existing ready client and startup-captured catalogue | desired config, auth, environments, roots, connector inputs | matching connection identity permits client reuse | desired state can refresh while catalogue, binding, router, and model declaration remain stale |
| cold resume | dynamic tools, thread roots, compatibility metadata | current config, current model/provider, permissions, environments, auth, MCP/discovery | saved host declarations + new session runtime + current request plan | preserve dynamic tools; merge roots; fresh runtime can converge current MCP catalogue |
| fork | copied dynamic tools, roots, compatibility metadata | current fork config and current runtime state | copied host declarations + new thread runtime + current request plan | preserve dynamic tools; merge roots; fresh runtime can converge current MCP catalogue |
| process restart | same saved declarations as cold resume | new process runtime state | same composition as cold resume | mixed preserve/refresh; fresh MCP runtime |
| runtime upgrade | same saved declarations as cold resume | new binary, config, catalogue, provider and discovery state | saved declarations interpreted by current code; compatibility fallbacks may apply | mixed preserve/refresh; no capability-generation check |
| selected executor disconnect/reconnect | saved selected-root identity | current environment readiness and executor/MCP discovery | saved selection remains; current availability controls exposure | degrade while unavailable, recover after reattach |
| Responses Lite startup prewarm → first generated turn | prior response state carries the logical input prefix | freshly built logical request and turn metadata | reuse predicate accepts unchanged logical tools; incremental wire request may omit direct `additional_tools` | wire advertisement depends on retained prior-response state |

## Mismatch fixture

Files:

- `artifacts/lifecycle_provenance_fixture.py`
- `artifacts/fixture-run.md`

Command:

```bash
python3 campaigns/0002-tool-surface-continuity/lanes/L01-lifecycle-provenance/artifacts/lifecycle_provenance_fixture.py
```

Fixture inputs:

- saved dynamic tools: `["host_old"]`
- current host dynamic tools: `["host_new"]`
- saved root: `root-a -> /saved/root-a`
- current host start roots: `root-a -> /host/root-a`, `root-c`
- current environment roots: `root-a -> /current/root-a`, `root-b`
- current native and MCP tools remain fixed as controls

Assertions:

| Transition | Dynamic tools | Effective root result |
|---|---|---|
| start | `host_new` | host `root-a`, host `root-c`, current environment `root-b` |
| live reconnect | `host_live` | live root wins duplicate ID |
| cold resume | `host_old` | saved `root-a` wins conflict; current `root-b` merges |
| fork | `host_old` | saved `root-a` wins conflict; current `root-b` merges |
| restart | `host_old` | saved `root-a` wins conflict; current `root-b` merges |
| upgrade | `host_old` | saved `root-a` wins conflict; current `root-b` merges |

Local execution completed with exit code `0` and all assertions passing.

## Controls

1. **Start control:** proves the model allows current host declarations to win where the API accepts them.
2. **Live-session control:** separates listener reconnect from cold reconstruction.
3. **Same-ID root conflict:** tests precedence, warning-only handling, and stale-location retention.
4. **Distinct-ID environment root:** proves current environment state can merge additively.
5. **Fixed native/MCP set:** isolates thread-scoped host provenance from current planning; the fixture does not test session-owned MCP catalogue freshness.
6. **Pinned compatibility version:** avoids attributing unrelated multi-agent changes to host capability refresh.
7. **Upstream integration control:** the selected-capability-stack test exercises a real persisted root with unavailable and reattached executor state.

## Evidence and confidence

| Claim | Label | Confidence |
|---|---|---|
| dynamic tools persist in `SessionMeta` and are recovered for resume/fork | observed code | high |
| public resume/fork cannot supply replacement dynamic tools or selected roots | observed protocol/code | high |
| non-empty current dynamic input wins; empty means recover saved | observed code | high |
| saved thread roots precede current environment roots and win ID conflicts | observed code | high |
| selected-root availability refreshes after restart and reattach | observed upstream integration test | high |
| live reconnect preserves the loaded session | observed code | high |
| restart follows cold-resume composition | direct code-path inference | high |
| upgrade follows cold-resume composition under the new binary | code-path inference | medium-high |
| a changed current host dynamic set silently remains stale on cold resume | source-derived executable fixture | high for precedence, medium for end-to-end UX |
| desired MCP inputs can refresh while a reused ready client retains a stale catalogue | observed L04 source trace and controlled fixture | high within L04 boundary |
| a preserved dynamic tool can remain model-invisible when deferred discovery is unavailable | observed L05 source trace and invariant fixture | high within L05 boundary |
| a logical discovery loader is insufficient unless delivered directly or through verified previous-response inheritance | observed L05 follow-up cross-lane fixture | high for the modeled client boundary |
| stale saved provenance can pass the discovery-route invariant while still requiring a lifecycle warning | observed L05 follow-up cross-lane fixture | high for classification |
| Responses Lite prewarm reuse can omit direct tool declarations from the first generated wire request | observed L02 source trace and protocol fixture | high for client wire behavior; server consequence unknown |
| owned revision retains the same decisive precedence | observed owned code | high |

Owned comparison references:

- [owned dynamic-tool precedence](https://redirect.github.com/teamleaderleo/codex/blob/2b7b93081361b77f8ddaceaf362a09765b4153bf/codex-rs/core/src/session/mod.rs#L642-L670)
- [owned selected-root precedence and persistence](https://redirect.github.com/teamleaderleo/codex/blob/2b7b93081361b77f8ddaceaf362a09765b4153bf/codex-rs/core/src/session/session.rs#L593-L636)

## Negative results and limits

- No public `thread/resume` or `thread/fork` field carries a fresh host dynamic-tool set or fresh host-selected roots.
- No typed capability-generation, digest, or mismatch receipt appears in these lifecycle paths.
- The existing selected-capability integration test covers saved selection plus current readiness. It does not create a changed host thread-selection set.
- A direct upstream end-to-end dynamic-tool mismatch test was not found at the pinned public revision.
- The lane fixture models the observed branches and asserts their consequences. It does not execute the full Codex binary.
- Transport and startup-prewarm reuse details remain assigned to lane L02 / issue #37.
- Compaction and result-identity details remain assigned to lane L03 / issue #38.
- MCP/app catalogue convergence details remain assigned to lane L04 / issue #39.
- Deferred exposure and discovery details remain assigned to lane L05 / issue #40.
- Effective-surface receipt v1 was accepted through L06 / issue #43 / merged PR #81. It classifies the earliest observed divergence and performs no repair.
- Fallback authority remains assigned to lane L07 / issue #44.
- ChatGPT connector/developer-MCP coexistence remains an integration-scope lane L08 / issue #46.

## Cross-lane review

The other campaign lanes refine the lifecycle map without overturning the saved-metadata precedence.

Reviewed campaign records:

| Lane | Durable record | Cross-lane effect |
|---|---|---|
| L02 | PR #58 / issue #37 | adds transport previous-response lifetime |
| L03 | PR #64 / issue #38 | separates capability provenance from compacted call/result identity |
| L04 | PR #62 / issue #39 | distinguishes desired MCP state from a reused live catalogue |
| L05 | PR #59 and follow-up PR #77 / issue #40 | separates preservation from model visibility, wire delivery, and provenance freshness |
| L06 | merged PR #81 / issue #43 | accepts receipt v1 and separates the earliest observed divergence from recovery policy |
| L07 | PR #60 / issue #44 | constrains fallback after loss |
| L08 | PR #57 / issue #46 | healthy ChatGPT integration control with restart/reconnect still untested |

### L02 — Responses transport and startup prewarm

L02 establishes a transport-scoped reuse layer after logical request construction. HTTP and WebSocket build the same logical request, while a clean Responses Lite prewarm handoff can send the first generated turn through `previous_response_id` without directly repeating the `additional_tools` prefix. This means L01 should describe current planning separately from direct wire advertisement.

### L03 — compaction and tool-result identity

L03 concerns call/result identity rather than capability declaration provenance. Compaction makes its replacement history authoritative for resume and fork and can remove raw call/result pairs. This does not refresh saved `SessionMeta.dynamic_tools` or selected roots, but it adds a separate persisted history boundary that diagnostics must report.

### L04 — MCP/app catalogue convergence

L04 corrects the broadest sentence in the first L01 draft. Current auth, config, roots, and connector inputs can be recomputed while a matching ready MCP client retains its startup-captured catalogue. Ordinary refresh can therefore remain stale. Fresh thread creation, explicit reconnect, restart, and connection-identity change converge the controlled fixture.

### L05 — deferred discovery invariant

L05 shows that preservation and executability are separate claims. A saved dynamic tool can survive resume and enter the router as a deferred runtime while remaining invisible and unloadable when `tool_search` is unavailable or searchable metadata is missing.

The L05 follow-up in PR #77 extends that rule through delivery. A logical loader is effective only when it is present on the generated wire request or the same manifest is verified as inherited through `previous_response_id`. It also classifies stale catalogue and stale saved provenance as typed warnings rather than discovery-route failures. In particular, L01's `host_old` condition can have a valid loader and still be wrong for the current host generation. L01 therefore owns replacement and generation semantics; L05 owns loader reachability.

### L07 — fallback authority

L07 begins after a capability is missing or unusable and asks whether rerouting preserves authority. Its findings do not alter provenance. They strengthen the requirement for typed degradation and fallback receipts before any substitute route executes.

### L08 — ChatGPT coexistence field trial

L08 is a healthy integration-scope negative result. GitHub connector and developer-MCP calls remained executable through sustained use, a context-summary boundary, and rediscovery. The trial could not exercise disconnect/reconnect or application restart and could not inspect raw model advertisements or router inventories, so it neither confirms nor contradicts Codex cold-reconstruction behavior.

### L06 — effective-surface diagnostics

L06 was accepted through merged PR #81. Receipt v1 classifies eight normalized campaign cases: seven distinct first divergences, one healthy control, zero expectation mismatches, and seven focused tests passed. Its ordered observations cover saved/current/effective host state, logical and wire manifests, catalogue and binding, router/model exposure, discovery, required execution, completion, result persistence, client delivery, display, and fallback authority.

The accepted receipt keeps recovery advisory. It distinguishes a valid loader with stale saved provenance from a missing loader, and a stale catalogue from a wire omission. That preserves the ownership split established by L01, L02, L04, and L05.

## Post-closeout Codex and Rust SDK recheck

The current public Codex head `7579a2b41353470efaef93c08b4a21068a366b7f` remains consistent with the campaign result:

- `thread/start` accepts `dynamicTools` and `selectedCapabilityRoots`, while `thread/resume` and `thread/fork` still provide no equivalent replacement or clear fields;
- Codex pins `rmcp = 3.0.0`;
- MCP client reuse still compares configured transport, environment, credentials, authentication, and protocol-related inputs, but not the remote server identity or current tool-catalogue digest;
- `ManagedClient` still retains server information and the startup-listed tool vector;
- a server `notifications/tools/list_changed` event invalidates the Rust SDK's own cached `tools/list` response before callback routing, but the SDK default callback is a no-op and Codex's callback currently logs the event without relisting or replacing its separate startup-listed `ManagedClient.tools` vector;
- the newest additional Codex commit changes environment-native MCP file-upload path handling, not lifecycle or catalogue publication.

The Rust SDK 3.0 line adds modern discovery and lifecycle negotiation, subscription support, response caching, and more accurate OAuth discovery errors. Its response cache has a private generation counter: invalidation advances the generation and suppresses stale in-flight response writes. That protects the SDK cache, but it does not order Codex's application-level catalogue publication. The stale-catalogue repair therefore belongs in Codex integration code, while an SDK follow-up could offer a reusable opt-in relist coordinator with notification coalescing, generation ordering, and reconnect signals.

The current Rust SDK head is one fix beyond the 3.0.0 release: it stamps server information on graceful subscription results. Release PR #1081 proposes 3.0.1 for that fix. This does not alter the catalogue-reuse finding.

### Existing Codex Apps publication pattern

Current Codex already contains most of the safe publication model for Codex Apps:

- `hard_refresh_codex_apps_tools_cache` serializes relist and publication;
- fetch tickets accept only the newest catalogue fetch;
- each accepted publication increments one exact `tool_catalog_revision`;
- `McpBinding` freezes the advertised tools and captured clients for one request;
- `PreparedMcpCall` checks its captured revision before irreversible preparation;
- a call which already holds the old revision may finish while publication waits;
- an old prepared call that has not begun irreversible preparation is rejected after the revision changes.

Generic MCP should generalize this existing policy rather than inventing another publication model. The request-authority rule is therefore narrower than “old bindings always remain executable”: already-started work may finish under captured authority, stale not-yet-started calls fail closed, and new steps use the accepted new revision.

## Candidate repair semantics

These are candidates, ordered after the host contract above.

### 1. Add an explicit capability lifecycle policy

Resume and fork should accept one of:

- `preserveSaved` — current behavior and compatibility default;
- `replaceFromHost` — host supplies a complete current snapshot;
- `clear` — host explicitly removes the saved host declarations for the reconstructed thread;
- `rejectOnMismatch` — compare saved and current generations before creating the session.

Implicit refresh would blur thread ownership and can remove tools that the saved conversation expects.

### 2. Give dynamic tools tri-state request semantics

- omitted: preserve saved;
- empty list: clear;
- non-empty list: replace.

The current internal empty-vector rule combines “no override” and “clear,” preventing an explicit clear during reconstruction.

### 3. Make selected-root conflicts explicit

For duplicate root IDs with different locations, return a typed conflict receipt or apply the lifecycle policy. The current saved-first warning can retain a stale location while current state presents a replacement.

### 4. Persist provenance and generation

Persist, expose, and compare:

- owner (`host`, `environment`, `config`, `model`, `compatibility`);
- generation or digest;
- schema version;
- last resolution status;
- degradation reason.

### 5. Return an effective-surface receipt

Start, resume, and fork responses should include the effective capability digest and per-source counts. A degraded saved root should carry a typed status such as `selected_unavailable`, with current resolution details.

### 6. Gate upgrade compatibility

A new runtime should compare persisted capability schema and generation before interpreting saved declarations. Unsupported entries should produce an explicit reject or degraded receipt.

## Recommendation

Keep `preserveSaved` as the compatibility default. Add explicit replace, clear, and mismatch-rejection modes before any automatic refresh. Selected roots can preserve identity while refreshing readiness, with typed conflict and degradation receipts.

Treat host-declaration reconciliation, MCP relist or reconnection, deferred-discovery repair, and Responses prewarm reuse as separate controls. They have different owners and lifetimes. A single generic “refresh tools” operation would conceal which state changed. Require direct loader delivery or verified inheritance, and report stale saved provenance separately from loader absence.

The current-head and Rust SDK recheck strengthens the next implementation split. Codex needs the host lifecycle handshake and should generalize its existing Codex Apps publication/revision policy to generic MCP. The Rust SDK already surfaces tool-list-change notifications, invalidates its own cache, and exposes lifecycle events; optional helper APIs may make ordered relisting easier, but the SDK should not silently replace a client's published catalogue or request binding. Campaign #84 is now claimed through owned Codex draft PR #5; its first slice tests reconnecting at the host config-reload boundary while preserving ordinary per-turn reuse.

The current code provides continuity, yet the host has no public way to assert that its thread-scoped capability set changed. That missing handshake remains the L01 repair target and feeds implementation campaign #84.
