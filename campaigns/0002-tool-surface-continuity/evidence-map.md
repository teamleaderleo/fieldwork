# Effective Tool-Surface Evidence Map

## In simple words

The observed failures form several related clusters. They share a common symptom—one conversation has a smaller usable capability set than expected—while the evidence supports several possible owning boundaries. This map records what public source establishes, what public reports directly observe, which controls separate the clusters, and what remains inference.

Source retrieval date: 2026-07-29

Public source pin: [Codex revision `3725f02cf38d856bc82bb46dd68ab61bb96ec6fc`](https://redirect.github.com/openai/codex/commit/3725f02cf38d856bc82bb46dd68ab61bb96ec6fc)

## Evidence labels

- **Documented** — stated by official source or protocol.
- **Observed** — reproduced or recorded directly in a public report or owned incident.
- **Inferred** — explanation drawn from source and observations.
- **Unknown** — evidence has yet to distinguish the owning layer.
- **Negative result** — a suspected broad failure has a current guard or contrary control.

## Source-established lifecycle model

### Saved history inputs

**Documented:** Host dynamic tools can be stored in rollout `SessionMeta` and recovered from resumed or forked initial history.

**Documented:** Selected capability roots can be stored in session metadata and recovered from resumed or forked history.

**Documented:** Compatibility metadata influences the multi-agent or host-tool family selected for older resumed and forked threads.

**Boundary:** Public resume and fork request types at the source pin do not expose fresh `dynamicTools` or `selectedCapabilityRoots` inputs equivalent to thread start. A private host path may supply or reconcile current state; public source alone does not establish that path.

### Current runtime inputs

**Documented:** Native/core tools are planned from current model capabilities, features, permissions, environments, and turn configuration.

**Documented:** Configured MCP and curated app tools are derived from the current MCP binding, connector snapshot, accessible connector tools, app-enabled state, policy, selected roots, required servers, authentication, and configuration.

**Documented:** Search and suggestion capability is planned from current model and feature state.

**Documented:** A step can fall back to an empty MCP binding when refresh has completed but no current binding satisfies the required server set.

### Request-scoped consistency

**Documented:** [Merged request-scoped MCP router change](https://redirect.github.com/openai/codex/pull/34839) captures one MCP list and router for the sampling step and reuses it for advertisement, execution, compaction, and prompt debugging.

**Negative result:** This closes one within-step mismatch where the model could see a different MCP view than execution.

**Boundary:** The change does not prove correct hydration before the step, correct transport reuse after the step, or correct host policy outside public Codex source.

### Startup prewarm and transport

**Documented:** Startup Responses WebSocket prewarm creates a startup turn, captures a step context and router, builds a prompt, opens a session-scoped client, and passes that client into the first normal turn.

**Documented:** WebSocket request reuse compares tool payloads among the request properties used to decide compatibility.

**Inferred:** A reduced startup snapshot, stale response identity, or private routing state could affect the first normal request. A same-history request comparison is required to locate the first deterministic divergence.

### Deferred exposure

**Documented:** Current MCP/app runtime construction uses deferred exposure when search is enabled and direct exposure when search is disabled.

**Documented:** [Merged deferred-tool compaction fix](https://redirect.github.com/openai/codex/pull/19771) moved filtering into the router’s model-visible view so compact and normal request builders share the invariant.

**Boundary:** This fix protects request validity. It does not guarantee that every model/profile receiving deferred families also receives a callable discovery route.

## Public evidence clusters

### Cluster A — post-compaction task hydration

Primary report: [post-compaction loss of discovery, apps, and configured MCP](https://redirect.github.com/openai/codex/issues/34719).

**Observed:** App and configured-MCP calls work before manual compaction. The first post-compaction turn retains core tools and loses other families.

**Observed control:** A later report records an affected root task with zero GitHub tools while a fresh child in the same running process exposes the complete cached GitHub tool set and executes a call.

**Supports:** Per-task or per-thread hydration failure after compaction.

**Weakens:** Global account authentication, plugin installation, or process-wide cache failure as the sole explanation.

### Cluster B — same history, different transport

Primary report: [resumed compacted history loses native/code-mode tools over Responses WebSocket](https://redirect.github.com/openai/codex/issues/35751).

**Observed:** The WebSocket connection succeeds while the resumed compacted thread lacks a usable native/code-mode surface.

**Observed controls:** The same history works through HTTP, and a fresh WebSocket thread works. Forking the affected history preserves the failure.

**Supports:** History-dependent WebSocket prewarm, request construction, response reuse, or routing state.

**Weakens:** General model incapability and general WebSocket connectivity failure.

### Cluster C — healthy host catalogue, reduced task binding

Primary report: [Remote reconnect restores the host catalogue while the resumed context remains reduced](https://redirect.github.com/openai/codex/issues/35298).

**Observed:** The host reports a larger current MCP/app catalogue than the resumed execution context.

**Observed control:** Full application restart restores the missing connector without reauthorization.

**Additional observation:** A later-created task can lack an already-authorized connector even after an explicit plugin mention, while an earlier task on the same account succeeds.

**Supports:** Per-task catalogue hydration or provisioning can fail independently of account authorization.

**Weakens:** “The affected task predates installation” as a universal explanation.

### Cluster D — saved host dynamic tools and compatibility state

Primary report: [older resumed threads retain stale host dynamic tools](https://redirect.github.com/openai/codex/issues/25990).

**Observed:** An affected resumed thread lacks current thread-management tools while a fresh peer in the same installation receives them.

**Observed:** Recurrences continue across newer builds and include partial host surfaces such as one surviving automation tool.

**Supports:** Saved session metadata or compatibility selection can retain a reduced host surface.

**Boundary:** Fresh local session regressions also exist, so stale resumed metadata does not explain every host-dynamic failure.

### Cluster E — fresh-start dynamic-tool injection or filtering

Primary report: [fresh local sessions receive a reduced thread-management surface](https://redirect.github.com/openai/codex/issues/29223).

**Observed:** Same-machine history moves from a full host dynamic family to one tool and then zero tools across fresh sessions and versions.

**Observed diagnostic candidate:** A public fork commit adds a doctor check over recent rollout `SessionMeta.dynamic_tools`; this campaign treats it as a lead, pending independent source review and tests.

**Supports:** Fresh-start injection, gating, or filtering can fail separately from resume restoration.

### Cluster F — configured MCP stays globally enabled while the callable surface is stale

Primary report: [long-running configured MCP becomes unsupported](https://redirect.github.com/openai/codex/issues/26196).

**Observed:** A configured OAuth MCP works earlier and later returns unsupported calls while local status still reports it enabled and authenticated.

**Observed contradiction:** A fresh thread sometimes repairs the failure and sometimes inherits it.

**Observed stronger case:** A process can start while a bridge exposes an offline stub, later connect to the real server and display its large catalogue, while the active thread retains the stub until restart.

**Supports:** Startup binding capture and failure to converge after server identity or catalogue replacement.

**Requires:** A synthetic stub-to-real test to determine whether current public client source reproduces the stale binding.

### Cluster G — deferred tools without discovery

Primary reports:

- [model profile lacks `tool_search` while configured MCP is deferred](https://redirect.github.com/openai/codex/issues/33608)
- [discovered MCP tools remain hidden without a loader](https://redirect.github.com/openai/codex/issues/33609)

**Observed control:** The same server, installation, and prompt work with another model/profile that receives discovery.

**Supports:** Model/profile planning can select deferred exposure while omitting the route needed to load the tools.

**Weakens:** MCP server reachability as the sole explanation.

### Cluster H — displayed inventory differs from execution

Primary reports:

- [display says no MCP tools while invocation succeeds](https://redirect.github.com/openai/codex/issues/17021)
- [broader open display/discovery regression](https://redirect.github.com/openai/codex/issues/16028)

**Observed:** Status projection can report zero tools while an executable binding remains present.

**Supports:** Displayed inventory must remain a separate checkpoint from registered and executable inventories.

### Cluster I — call/result identity and continuation loss

Primary report: [tool-call output bookkeeping loss followed by restart](https://redirect.github.com/openai/codex/issues/14824).

**Observed:** A missing output for the same call identity can repeat through many continuations while the thread remains active.

**Adjacent Fieldwork finding:** Scout #23 demonstrates a separate local path where authoritative subprocess output and the bounded client transcript can diverge.

**Supports:** Provider completion, authoritative runtime result, normalized history result, and client delivery require separate evidence.

**Consequence:** Mutation replay policy should fail closed when current result identity is ambiguous.

### Cluster J — private ChatGPT coexistence and conversation policy

Owned incident: [Stensibly issue 490](https://redirect.github.com/teamleaderleo/stensibly/issues/490).

**Observed:** Official connector tools and a developer MCP can coexist and execute earlier in one conversation.

**Observed:** Later states include schemas without executable bindings, connector disappearance, a developer-MCP-only conversation restriction, and unclear mutation delivery.

**Supports:** The same inventory ladder and first-failing-turn checkpoint are useful for ChatGPT fieldwork.

**Boundary:** Public Codex source does not establish private ChatGPT catalogue assembly or conversation policy. Similar symptoms remain shared candidates rather than proof of one implementation or defect.

## Strong controls to preserve

1. affected thread versus fresh thread in the same process;
2. same history over HTTP and WebSocket;
3. same installation and server under two model profiles;
4. before and after manual compaction with the immediate next action fixed;
5. fork before and after the failing transition;
6. connector or MCP status versus benign executable call;
7. stub catalogue versus real catalogue after refresh;
8. explicit plugin mention versus implicit selection;
9. full application restart versus thread refresh;
10. provider completion receipt versus client-delivered result.

## Contradictions that require separate clusters

- Fresh threads can recover one affected task and can also inherit process-wide or profile-specific loss.
- A UI can under-report executable tools, while another failure advertises a tool whose handler is absent.
- Core tools can survive while custom families disappear, and native/code-mode tools can disappear while other families survive.
- Explicit mentions can trigger required-server loading, and explicit mentions can still fail when task provisioning is incomplete.
- Request-scoped router consistency can hold while the router itself was built from a reduced binding.

These contradictions argue against one universal root cause or one unconditional “reload tools” repair.

## Highest-value missing evidence

1. Byte-for-byte or digest-level HTTP/WebSocket request comparison for one compacted history.
2. Prewarm checkpoint versus first normal turn checkpoint on the same client session.
3. Stub-to-real MCP binding convergence in current public source.
4. Model/profile matrix proving which planner decision selects deferral without discovery.
5. Saved-versus-current host dynamic and selected-root fixture across resume and fork.
6. Compaction fixture preserving call/result identity under missing, duplicated, reordered, and late outputs.
7. Controlled fallback experiment comparing approvals and audit receipts after a required capability disappears.
8. ChatGPT alternating GitHub/Stensibly field trial with read-after-write reconciliation.

## Candidate repairs, pending lane evidence

- privacy-safe effective-surface receipt at prewarm and every sampling step;
- typed absence reasons distinguishing unconfigured, disabled, policy-blocked, auth-failed, unreachable, stale metadata, unbound, deferred-unloadable, handler-missing, and result-delivery-ambiguous states;
- reject or direct-expose deferred families when discovery is unavailable;
- refresh or replace a stale binding when server identity or catalogue digest changes;
- compare prewarm and first-turn executable digests and discard incompatible prewarmed state;
- explicit saved-versus-current host capability diagnostics on resume and fork;
- fail-closed mutation continuation when call/result identity is incomplete;
- user-visible, policy-aware reroute approval when a fallback path changes authority.