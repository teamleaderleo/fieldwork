# L01 — lifecycle capability provenance

Issue: [#35](../../../../issues/35)  
Campaign: [#31](../../../../issues/31)  
Synthesis PR: [#51](../../../../pull/51)  
Worker branch: `lane/35-lifecycle-provenance`

## Result in plain language

Codex has two capability lifecycles at once.

Thread-scoped host declarations are sticky. Dynamic tools and host-selected capability roots are saved in thread metadata. Cold resume, fork, process restart, and runtime upgrade recover those saved declarations. The public resume and fork APIs provide no replacement fields for either set.

Runtime-derived capabilities are rebuilt. Native tools, model/profile gates, feature flags, permissions, current environments, extensions, current authentication, current MCP configuration, and current connector discovery are captured from the active runtime for each session or request step.

That split produces a mixed effective surface:

- saved dynamic tools are preserved;
- saved thread roots are preserved;
- current ready environment roots are merged after thread roots;
- thread roots win duplicate root IDs, including location conflicts;
- native and MCP-derived tools are refreshed from current runtime state;
- a live reconnect rejoins the existing in-memory session;
- a cold reconnect creates a new session from saved history plus current runtime inputs.

The mismatch fixture demonstrates the unresolved host problem: a saved dynamic tool set `host_old` survives cold resume even when the current host set is `host_new`. The current host cannot express that replacement through `thread/resume` or `thread/fork`.

## Revisions and retrieval boundary

| Source | Revision | Role |
|---|---|---|
| Public Codex | `openai/codex@3725f02cf38d856bc82bb46dd68ab61bb96ec6fc` | primary public source and test evidence |
| Owned Codex | `teamleaderleo/codex@2b7b93081361b77f8ddaceaf362a09765b4153bf` | owned comparison |
| Retrieval boundary | `2026-07-29` | campaign pin |

Public upstream remained read-only. No upstream contact was made.

## Host contract before refresh semantics

Any refresh proposal needs an owner and lifetime contract for each input.

| Input | Proposed owner contract derived from current behavior | Lifetime |
|---|---|---|
| `dynamicTools` supplied by the host | The host declares a complete thread-scoped callable set at thread creation. Codex persists it and treats it as part of the thread identity. | sticky until an explicit host replacement or clear operation exists |
| `selectedCapabilityRoots` supplied by the host | The host selects thread-scoped capability identities. Codex persists the selection. Availability and resolved executor state may change independently. | selection is sticky; readiness is current |
| roots supplied by current environments | The environment supplies additive ready roots for the captured request step. | request-step snapshot |
| native/core tool plan | Codex derives the plan from the current model profile, provider capabilities, configuration, features, permissions, session source, and current environments. | rebuilt per request step |
| MCP/app/connector tools | Codex derives the binding from current auth, current config, current manager state, selected-root readiness, and current discovery. | refreshed current state |
| multi-agent version | Saved thread metadata wins; an inherited `Disabled` value wins first; legacy resumed/forked threads without metadata fall back to V1. | compatibility-selected at session creation |
| live reconnect | The existing in-memory session owns the effective surface. | existing session lifetime |
| cold reconnect / restart / upgrade | Saved thread declarations combine with current runtime-derived inputs. | new session lifetime |

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

Each request step captures current environments, selected-root readiness, executor discovery, current MCP binding, recommendations, extensions, and then builds the tool router:

- [step capture](https://redirect.github.com/openai/codex/blob/3725f02cf38d856bc82bb46dd68ab61bb96ec6fc/codex-rs/core/src/session/mod.rs#L3027-L3103)
- [current MCP and connector inputs](https://redirect.github.com/openai/codex/blob/3725f02cf38d856bc82bb46dd68ab61bb96ec6fc/codex-rs/core/src/session/turn.rs#L1464-L1580)
- [tool planning context](https://redirect.github.com/openai/codex/blob/3725f02cf38d856bc82bb46dd68ab61bb96ec6fc/codex-rs/core/src/tools/spec_plan.rs#L144-L213)
- [native sources selected by current config, model, features, permissions, and environments](https://redirect.github.com/openai/codex/blob/3725f02cf38d856bc82bb46dd68ab61bb96ec6fc/codex-rs/core/src/tools/spec_plan.rs#L609-L775)

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
| MCP/app tools | current host state + current configuration | current auth, manager state, connectors, selected-root readiness |
| dynamic tool handler/specs | saved thread metadata or current host start input | then inserted into the current router |
| multi-agent surface | compatibility logic | saved metadata and legacy fallback |
| running session surface | another source: live in-memory session | existing session wins |
| current runtime binary behavior | another source: current revision | affects all rebuilt planning after restart or upgrade |

## Transition table

| Lifecycle transition | Saved inputs | Current inputs | Winner / composition | Observed outcome |
|---|---|---|---|---|
| thread start | none | host dynamic tools, host roots, config, model/profile, environments, MCP/auth | current host thread declarations; current runtime plan | build |
| live reconnect to running thread | persisted history remains secondary | existing in-memory session | live session wins; differing overrides are ignored | preserve |
| cold resume | dynamic tools, thread roots, compatibility metadata | current config, current model/provider, permissions, environments, auth, MCP/discovery | saved host declarations + current runtime plan | preserve dynamic tools; merge roots; refresh runtime-derived tools |
| fork | copied dynamic tools, roots, compatibility metadata | current fork config and current runtime state | copied host declarations + current runtime plan | preserve dynamic tools; merge roots; refresh runtime-derived tools |
| process restart | same as cold resume | new process runtime state | same as cold resume | mixed preserve/refresh |
| runtime upgrade | same as cold resume | new binary, config, catalog, provider and discovery state | saved declarations interpreted by current code; compatibility fallbacks may apply | mixed preserve/refresh; no capability-generation check |
| selected executor disconnect/reconnect | saved selected-root identity | current environment readiness and MCP discovery | saved selection remains; current availability controls exposure | degrade while unavailable, recover after reattach |

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
5. **Fixed native/MCP set:** isolates thread-scoped host provenance from current runtime planning.
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
- Transport replay details remain assigned to lane L03 / issue #37.
- MCP/app convergence details remain assigned to lane L05 / issue #39.

## Candidate repair semantics

These are candidates, ordered after the host contract above.

### 1. Add an explicit capability lifecycle policy

Resume and fork should accept one of:

- `preserveSaved` — current behavior and compatibility default;
- `replaceFromHost` — host supplies a complete current snapshot;
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

Keep `preserveSaved` as the compatibility default. Add explicit host replacement and mismatch-rejection modes before any automatic refresh. Dynamic tools should use replace semantics. Selected roots can preserve identity while refreshing readiness, with typed conflict and degradation receipts.

The current code provides continuity, yet the host has no public way to assert that its thread-scoped capability set changed. That missing handshake is the repair target.
