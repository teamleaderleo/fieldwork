# Campaign 0002: Effective Tool-Surface Continuity

State: `ready`

Campaign issue: #31

Programme: #14

Primary target: #8

Upstream contact authorized: `false`

## In simple words

- **What is this?** Research into why an agent can use a tool earlier in a conversation and later lose the ability to discover or execute it.
- **Where does it sit?** Between saved thread history, the current host catalogue, model-facing tool declarations, executable routing, transport state, and result delivery.
- **What is uncertain?** Several capability families are assembled through different paths, and lifecycle transitions can leave those paths with different views of the same conversation.
- **Why could anyone care?** Capability loss can strand long-running work, hide a completed mutation, or push the agent into a fallback path with different approval and audit behaviour.
- **Current answer:** Request-scoped advertisement and execution now share one router in current public Codex source. Restoration across compaction, resume, reconnect, runtime upgrade, model policy, and private ChatGPT host restrictions remains open.

## Campaign question

Across thread start, repeated turns, compaction, resume, fork, Remote reconnect, application restart, transport switch, and runtime upgrade, which layer first causes an installed, historically used, displayed, or model-advertised capability to lose its current executable binding?

The campaign also asks which diagnostic receipt can identify that layer during the first failing turn and which recovery preserves durable work without replaying an ambiguous side effect.

## Source boundary

- Public source: [Codex revision `3725f02cf38d856bc82bb46dd68ab61bb96ec6fc`](https://redirect.github.com/openai/codex/commit/3725f02cf38d856bc82bb46dd68ab61bb96ec6fc), retrieved 2026-07-29.
- Owned comparison fork: `teamleaderleo/codex@2b7b93081361b77f8ddaceaf362a09765b4153bf`.
- Owned effective-surface contract: `teamleaderleo/stensibly@7690ca0022048443fae9ec9d9eb3fd17ac1c58b6`.
- Canonical owned research programme: `teamleaderleo/stensibly#544`.
- Active owned coexistence incident: `teamleaderleo/stensibly#490`.

The public source is read-only. Publication, comments, reactions, pull requests, and other interaction with the external target require a separate human decision.

## Capability classes

The campaign treats these as separate provenance classes:

1. native shell, file-edit, and other core tools;
2. code-mode and `additional_tools` capabilities;
3. host dynamic tools supplied by the app-server or another harness;
4. curated app and connector tools;
5. configured MCP tools;
6. discovery tools such as `tool_search` and `tool_suggest`;
7. displayed or status inventory.

A historical successful call proves earlier availability. Each checkpoint must test current executable capability independently.

## Inventory ladder

A useful diagnosis keeps these observations separate:

1. **Host or account catalogue** — installed, enabled, authenticated, and globally accessible capabilities.
2. **Current runtime binding** — the exact MCP, connector, and host-tool state attached to the thread or step.
3. **Registered router inventory** — handlers and runtimes available to dispatch.
4. **Model-advertised inventory** — direct declarations plus any discovery route shown to the model.
5. **Executable inventory** — benign calls the router can dispatch during the current step.
6. **Result-delivery state** — call/result identity, provider completion, normalization, and delivery to the client.
7. **Displayed inventory** — UI, doctor, status, or inspection output.

Agreement at one rung does not establish agreement at another.

## Established starting model

At the source pin:

- rollout session metadata can retain host dynamic tools, selected capability roots, and compatibility metadata across resume or fork;
- native/core tools are planned from current model, feature, permission, environment, and turn state;
- configured MCP and app tools are rebuilt from current auth, configuration, connector state, selected roots, required servers, policy, and the current binding;
- each sampling step captures a router and model-visible list intended to serve one request-scoped view;
- startup WebSocket prewarming captures a separate startup step and passes a session-scoped client into the first normal turn;
- deferred tools depend on a functioning discovery route;
- inability to obtain a binding satisfying required servers can leave a step with an empty MCP binding;
- public reports demonstrate different failure classes after compaction, resume, reconnect, startup catalogue capture, model/profile selection, and transport reuse.

## Work units

| Lane | Issue | Owned output | Question |
| --- | --- | --- | --- |
| L01 lifecycle provenance | #35 | `lanes/L01-lifecycle-provenance/report.md` | Which capability inputs are saved, rebuilt, host-supplied, or compatibility-selected? |
| L02 transport and prewarm | #37 | `lanes/L02-responses-transport-prewarm/report.md` | Where can HTTP and WebSocket build or retain different usable manifests? |
| L03 compaction and result identity | #38 | `lanes/L03-compaction-result-identity/report.md` | Does history replacement preserve declarations, call IDs, results, and pending execution state? |
| L04 MCP and app convergence | #39 | `lanes/L04-mcp-app-catalogue-convergence/report.md` | Does refresh or reconnect converge global catalogue, thread binding, router, advertisement, and execution? |
| L05 deferred discovery | #40 | `lanes/L05-deferred-discovery-invariant/report.md` | Can a tool family be deferred while every executable discovery route is absent? |
| L06 diagnostics | #43 | `lanes/L06-effective-surface-diagnostics/report.md` | Which privacy-safe receipt identifies the first divergent inventory? |
| L07 fallback authority | #44 | `lanes/L07-adversarial-fallback-authority/report.md` | Does capability loss silently change approval, identity, resource, or audit boundaries? |
| L08 ChatGPT field trial | #46 | `lanes/L08-chatgpt-coexistence-field-trial/report.md` | Which observable layer fails first when an official connector and developer MCP coexist? |

## Prior reconnaissance

Scout #23 and Fieldwork PR #33 mapped broad Codex tool, process, terminal, interruption, and recovery paths. Its retained high-confidence candidate concerns unified-exec producer output versus a bounded client transcript. Campaign 0002 consumes that map and keeps terminal transcript repair as a separate decision. The intersection is result delivery: authoritative runtime state may exist while a client transcript loses evidence.

Scout #24 owns cross-agent process and terminal comparison. Any future cross-harness capability-restoration comparison should be promoted through that programme decision or a new evidence-backed campaign after the Codex lanes establish a stable case pack.

## Shared checkpoint

Each applicable lane records:

- product/build, runtime/source revision, model/profile, transport, and transition;
- redacted thread, turn, and prior-checkpoint digests;
- class counts and digests;
- selected-root and required-server digests;
- displayed, global, bound, registered, advertised, and executable inventories;
- one benign call result and exact typed error per class;
- provider and authentication health;
- request, response, call, and result identity;
- recovery after refresh, HTTP fallback, restart, fork, or fresh thread.

## Stop conditions

Narrow or stop a lane when:

- current source or a controlled experiment disproves its premise;
- the observation cannot be separated from model-output nondeterminism;
- the consequence is limited to cosmetic presentation;
- the experiment requires credentials, private prompts, production payloads, or live destructive resources;
- another lane owns the same question;
- implementation would precede a failing test and demonstrated consequence.

## Expected decisions

The campaign may conclude with one or several outcomes:

- a privacy-safe diagnostic receipt;
- a regression fixture or owned-fork experiment;
- a local Stensibly recovery control;
- a bounded candidate repair;
- a publication packet held for human approval;
- separate defect clusters with no common repair;
- a negative result showing current public client code preserves the tested invariant.