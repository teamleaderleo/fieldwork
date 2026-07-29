# Initial Synthesis

## In simple words

A conversation’s “tools” are several different inventories connected by lifecycle steps. The evidence shows those inventories can diverge in both directions: a tool can remain displayed while execution is absent, and execution can remain available while status reports zero tools. Current public Codex source protects consistency inside one sampling step, while the strongest open questions sit before and after that step—restoration, catalogue convergence, transport reuse, discovery, and result delivery.

This is an initial synthesis. Lane findings may revise it.

## Established conclusions

### 1. Capability continuity is a state-reconciliation problem

The working surface is assembled from at least three time domains:

- saved thread history and compatibility metadata;
- current runtime, account, model, policy, connector, and MCP state;
- request- and response-scoped transport state.

A current execution step must reconcile those domains. Reading only history, global status, or the model-facing declaration leaves important gaps.

### 2. Tool provenance predicts different failure modes

- Host dynamic tools can become stale through saved metadata or fail during fresh injection.
- Native and code-mode tools can fail through planning, serialization, or history-dependent transport paths.
- Apps and configured MCP tools can fail through auth, catalogue, connector selection, policy, required-server resolution, binding refresh, or router registration.
- Discovery can fail independently and make a healthy deferred catalogue unreachable.
- Display can lag behind or diverge from execution.

One repair applied to every class would erase useful diagnostics and risk widening authority.

### 3. Request-scoped consistency is necessary and incomplete

The current router/list invariant means advertisement and dispatch can share one exact step snapshot. That removes a meaningful race and reduces within-step ambiguity.

The same invariant can faithfully preserve a reduced snapshot. It therefore needs lifecycle evidence describing how the snapshot was produced and whether it matches current required capabilities.

### 4. Compaction, resume, fork, reconnect, restart, and transport switch are separate controls

Public reports show different outcomes for each transition. The campaign should resist the temptation to treat “old thread” or “long context” as one trigger.

The strongest experiments pair one transition with immediate class-specific smoke tests and a fresh-thread or alternate-transport control.

### 5. Discovery is part of the executable surface

A deferred tool family without an executable loader is functionally absent for the model, even while the server, catalogue, and handler are healthy.

The effective-surface receipt should therefore count discovery as its own required class and record whether each deferred family has a matching route.

### 6. Result delivery belongs in the capability model

A handler can execute and the provider can complete while the client lacks a trustworthy result. A capability surface that stops at dispatch cannot distinguish failed execution from completed work with lost delivery.

Every consequential mutation needs logical operation identity, call identity, authoritative completion evidence, normalized result identity, and client-delivery state.

### 7. Fallback behaviour can change authority

Capability loss may cause an agent to try shell protocol requests, Computer Use, browser interaction, a substitute connector, or a subagent. These alternatives can change:

- credential and resource ownership;
- approval and review path;
- idempotency and mutation identity;
- audit visibility;
- provider semantics;
- recovery after ambiguity.

A reroute therefore needs an explicit equivalence or approval decision. “Another tool can reach the same service” is insufficient.

### 8. ChatGPT and Codex require a shared vocabulary and separate claims

The same inventory ladder describes both systems usefully. Public Codex source can explain public Codex behaviour. The ChatGPT field trial can record direct product observations. Shared symptoms support shared candidates, while private host policy and catalogue behavior remain separate until evidence connects them.

## Current hypotheses ranked by evidence value

### H1 — reduced snapshot captured before a healthy step

A lifecycle transition produces a smaller binding or planned surface, and request-scoped consistency then carries that reduced view correctly.

Distinguishing evidence:

- global catalogue exceeds current binding;
- registered, advertised, and executable digests agree with each other while all remain reduced;
- restart or fresh task rebuilds the larger view.

Primary lanes: #35, #39, #43.

### H2 — prewarm or WebSocket reuse retains incompatible request state

A startup or resumed WebSocket session retains history-dependent state that HTTP or a fresh WebSocket session avoids.

Distinguishing evidence:

- same history and model produce different manifests or usable `additional_tools` across transports;
- prewarm and first-turn checkpoints differ;
- discarding the prewarmed session or forcing HTTP restores capability.

Primary lane: #37.

### H3 — deferred policy lacks a discovery route

A family is intentionally omitted from direct declarations, while model/profile or request planning omits every loader.

Distinguishing evidence:

- catalogue and handler exist;
- direct model-visible function declaration is absent by deferral policy;
- discovery is absent or cannot return the family;
- another model/profile on the same runtime receives discovery and succeeds.

Primary lane: #40.

### H4 — stale binding survives catalogue replacement

A process begins with an empty or stub catalogue, later connects to the real server, and updates status without replacing the thread’s callable binding.

Distinguishing evidence:

- global and displayed catalogue digest changes;
- current binding, router, and executable digest remain stale;
- explicit refresh or restart changes the callable digest.

Primary lane: #39.

### H5 — saved host metadata wins over current host capability

Resume or fork restores dynamic tools and capability roots from saved metadata without a complete reconciliation with the current harness.

Distinguishing evidence:

- saved metadata differs from current host catalogue;
- resumed/forked surface follows saved metadata;
- fresh thread follows current host state;
- an explicit private-host reinjection path is absent or incomplete.

Primary lane: #35.

### H6 — call/result identity fails after execution

Execution completes or begins, while compaction, normalization, retry, or delivery loses the paired result identity.

Distinguishing evidence:

- authoritative runtime or provider completion exists;
- normalized history lacks or duplicates the result;
- repeated continuation advances with the same missing call ID;
- replay risks duplicating the side effect.

Primary lane: #38, with dependency on #23.

### H7 — private conversation policy reclassifies allowed tool families

A ChatGPT conversation transitions from connector/MCP coexistence to a restricted policy state.

Distinguishing evidence:

- registry or schema remains present while policy rejects execution;
- account-level connector health remains good;
- a fresh conversation under the same account restores coexistence;
- the exact first policy error is captured before other recovery attempts.

Primary lane: #46.

## Recovery model

The campaign currently supports a conservative recovery sequence:

1. stop consequential mutation when the current required executable surface degrades or result identity becomes ambiguous;
2. persist the last confirmed receipt, durable work state, operation identity, exact next action, and source revisions;
3. run benign class-specific smoke tests;
4. try a bounded control: refresh, alternate transport, restart, fork, or fresh thread;
5. continue from durable GitHub and Stensibly state in a healthy context;
6. retain the affected thread and receipts as evidence;
7. avoid replay until read-after-write reconciliation establishes the prior mutation outcome.

## Repair candidates worth testing

### Candidate A — effective-surface receipt

Emit a privacy-safe receipt at startup prewarm and each step capture. Include class counts and digests, lifecycle transition, selected roots, required servers, registered router, model-visible surface, executable surface, and prior receipt identity.

Value: identifies the first divergent layer and supplies a fail-closed dispatch input.

Owner: #43 after source inputs arrive.

### Candidate B — prewarm compatibility gate

Compare the prewarm executable digest with the first normal turn. Discard the prewarmed session or force a fresh request when required capability is lost.

Value: bounded transport repair with a direct regression seam.

Owner: #37.

### Candidate C — deferred/discovery invariant

Reject the planned request or directly expose the family whenever deferral is selected without a functioning discovery route.

Value: converts silent absence into a deterministic planning decision.

Owner: #40.

### Candidate D — catalogue convergence on identity or digest change

Replace or refresh the thread binding when server identity, configuration, selected roots, required servers, or catalogue digest changes.

Value: targets stale startup and reconnect states.

Owner: #39.

### Candidate E — saved-versus-current host capability receipt

Record provenance and differences between saved dynamic tools/roots and the current host catalogue on resume and fork.

Value: diagnoses stale histories while avoiding speculative automatic replacement.

Owner: #35.

### Candidate F — fail-closed result reconciliation

Terminate or pause continuation after an unmatched tool call/result identity and expose one repair state instead of repeatedly sampling.

Value: protects side effects and prevents replay amplification.

Owner: #38.

### Candidate G — authority-aware fallback policy

Require an explicit reroute decision when the alternative path changes credentials, approvals, audit visibility, resource scope, or idempotency guarantees.

Value: prevents silent privilege or accountability changes after capability loss.

Owner: #44.

## What remains unknown

- The private host path, if any, that reinjects current dynamic tools and roots on resume or fork.
- The exact private server state participating in the same-history WebSocket failure.
- The complete mapping between model profiles and tool planning delivered by private configuration.
- The ChatGPT conversation-policy state machine behind connector/developer-MCP segregation.
- The frequency and operational consequence of each cluster outside public reports and owned trials.
- Whether one retained diagnostic can observe every inventory without exposing sensitive catalogue details.

## Synthesis rule

Lane reports should preserve separate defect clusters until a shared failing source path or controlled reproduction establishes a common cause. Similar user-visible absence is insufficient to merge causes, repairs, or authority decisions.