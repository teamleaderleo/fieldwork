# Scout: Harness control surfaces across Gemini CLI, OpenCode, and T3 Code

State: `ready-for-synthesis`

## In simple words

Gemini CLI and OpenCode directly own agent execution, sessions, tools, and terminal behavior. T3 Code sits above several agent harnesses and translates each provider's events into one persistent session model for its browser, desktop, and mobile control surfaces. That extra translation layer creates useful product flexibility, but it also creates a place where a provider can be finished while the controller still believes it is working.

Gemini CLI has already been mapped in Fieldwork, so this scout does not repeat that work. The strongest new branch is an OpenCode-to-T3 completion trace: prove that every OpenCode terminal state, especially after mid-turn steering, becomes the correct T3 canonical event, clears the persisted active turn, and survives restart without leaving the thread locked. Two public T3 issue reports describe the exact user-visible divergence, but the owning adapter path and root cause remain unproven.

## Assignment

- Worker: `chatgpt:gpt-5.6-thinking`
- Programme: `agent-cli-execution` (#14)
- Existing baseline: Gemini CLI scout #22 and cross-agent process scout #24
- Owned path: `programmes/agent-cli-execution/scouts/harness-control-surfaces/`
- Claim scope: `mechanism` and `interface`
- Retrieval date: `2026-07-30`
- Upstream contact authorized: `false`

Pinned sources:

- `teamleaderleo/gemini-cli@3499c84f7b8e70c86600e7cd2c67a7c65a667f5e`
- `teamleaderleo/opencode@7565e03536d19e850f9996c407f9bf5e932b5f7a`
- `teamleaderleo/t3code@85a89868703530e03c5e79797c7b952c684bd222`
- Fieldwork base: `teamleaderleo/fieldwork@ed91a4d1de9d62b3eab50d0b0188917b061746db`

## Question

Which lifecycle truths are owned by an agent harness, which truths are reinterpreted by a control surface, and where can process, terminal, session, approval, interruption, or completion state become stale or misleading across that boundary?

This is a neutral comparison. A direct harness and a multi-provider control plane solve different problems. The useful question is whether each boundary states its contract clearly and preserves enough information for the next layer to act correctly.

## Method and evidence labels

The scout read implementation, tests, architecture notes, and contribution guidance at the pinned revisions. It reused the completed Gemini source and probe findings instead of opening a second Gemini lane.

Evidence labels used here:

- **Source-confirmed** — directly supported by code at a pinned revision.
- **Documented** — stated by repository documentation.
- **Reported** — described in an external issue, not independently reproduced here.
- **Inferred** — a bounded implication from source-confirmed behavior that still needs a target-native trace.
- **Unknown** — the current source pass did not establish the answer.

A target-native run was not feasible in this execution environment because repository cloning and package installation could not reach external hosts. The retained adversarial case pack is therefore a specification for the next owned-fork trace, not a claimed reproduction.

## Existing Gemini baseline

Fieldwork #22 already mapped Gemini CLI approval, invocation, process ownership, cancellation, session persistence, interruption, and recovery. Its retained findings include discarded abort signals for project-discovered tool subprocesses, confirmation-call affinity risk, missing durable interrupted-tool receipts, kill acknowledgement before verified process-tree exit, and approval waiting state that can survive abort.

That baseline contributes two reusable rules to this scout:

1. A cancellation request, process signal, UI acknowledgement, direct-child exit, process-tree exit, output closure, turn completion, and durable session reconciliation are separate milestones.
2. A session history that records only model-facing content is insufficient to explain or recover partially completed tool and process work.

No new Gemini campaign is proposed here because #22 already produced ranked candidates and an owned-fork test-only draft.

## OpenCode map

### Agent shell tool

**Source-confirmed.** `packages/opencode/src/tool/shell.ts` runs commands through the selected shell. On non-Windows systems it requests a detached child; stdin is ignored. Output is consumed from the process handle's merged `all` stream, retained within bounded limits, and optionally spilled to a file when truncation limits are exceeded.

The shell tool races three outcomes:

- process exit;
- caller abort;
- timeout.

Abort and timeout both invoke process termination with forced escalation after three seconds. The public result distinguishes timeout and user abort in metadata, but the merged output contract does not retain stdout/stderr identity.

This is a coherent contract for a model-facing shell tool. It should not be mistaken for a raw terminal transcript or for proof that every descendant and inherited output descriptor has settled when the tool result returns.

### Managed PTY service

**Source-confirmed.** `packages/core/src/pty.ts` implements a separate interactive terminal contract:

- real PTY creation with `TERM=xterm-256color`;
- input and resize support;
- a two-megabyte retained string buffer;
- absolute output cursors;
- replay followed by live activation;
- exited-session retention;
- explicit remove semantics.

This service is a stronger fit for interactive terminal continuity than the agent shell tool, but it exposes three reusable boundary questions.

#### Replay gaps are not disclosed

When an attachment requests a cursor older than the retained buffer, replay starts at the oldest surviving character. The returned attachment reports the current end cursor, but no omitted-prefix count, lower-bound cursor, or gap flag.

**Inferred consequence.** A reconnecting client can receive a syntactically valid suffix and interpret it as complete history. This matters for terminal rendering, command prompts, approval text, and any client logic that rebuilds state from replay.

#### Buffer trimming is based on JavaScript string offsets

The service tracks cursor and capacity through string length and trims with `slice(excess)`.

**Inferred consequence.** Trimming can split a UTF-16 surrogate pair. The next replay can begin with an unpaired surrogate even though the original PTY stream contained a valid Unicode scalar sequence.

#### Inactive subscribers accumulate pending chunks

An attached subscriber remains inactive until the caller applies replay and calls `activate()`. Chunks arriving in that interval are appended to a per-subscriber pending array. No source-visible bound or detachment deadline is applied.

**Inferred consequence.** A stalled client can create subscriber-specific memory growth even though the global PTY replay buffer is bounded.

### OpenCode session truth

**Documented/source-visible contract.** OpenCode exposes structured session status and a `session.idle` event in its generated SDK/event surface. That is the provider-level completion truth a controller should consume rather than inferring completion from the last text token or terminal silence.

The exact OpenCode-to-T3 adapter mapping was not established in this source pass. That missing link is the main evidence gap, not permission to assume the mapping is absent.

## T3 Code map

### Role and architecture

**Documented.** T3 Code describes itself as an agent harness control surface. It can control Codex, Claude Code, Cursor, Grok Build, and OpenCode. Its Node server accepts browser WebSocket requests, routes provider operations through adapters, normalizes provider-native events into orchestration events, persists read-model state, and sends ordered pushes back to clients.

This is materially different from OpenCode's role. T3 does not need every provider to behave identically. It needs its canonical contract to preserve provider differences that affect correctness, approvals, interruption, recovery, and user-visible availability.

### Provider session routing and persistence

**Source-confirmed.** `ProviderService` routes operations by provider instance and persisted thread binding. On `sendTurn`, it may recover a missing live session from persisted resume state, forwards the turn to the adapter, then stores:

- provider and provider-instance identity;
- `status: running`;
- the returned resume cursor;
- `activeTurnId`;
- the last runtime operation and timestamp.

`ProviderRuntimeIngestion` owns the canonical clearing path. It applies `session.state.changed`, `turn.started`, `turn.completed`, and `session.exited` events to the persisted orchestration session. A non-active session state or turn completion clears `activeTurnId`; completed turns normally set the session to `ready`.

That means a thread can remain stuck for at least three distinct reasons:

1. the OpenCode adapter never emits the canonical completion/state event;
2. the event is emitted but rejected by lifecycle correlation or turn identity guards;
3. the event is accepted, but a later persisted or projected update restores stale running state.

The current evidence does not select among them.

### Reported OpenCode/T3 divergence

Two public issue reports are relevant context:

- `https://redirect.github.com/pingdotgg/t3code/issues/2173`
- `https://redirect.github.com/pingdotgg/t3code/issues/2886`

**Reported.** Both describe OpenCode-backed threads that finish at the provider but remain permanently `working` in T3. The later report says OpenCode itself shows the run ended, while T3 remains locked even after application restart. The later report was closed as a duplicate of the earlier open issue.

These reports establish a plausible and consequential integration symptom. They do not establish the implementation root cause. The next probe must capture the OpenCode event stream, T3 adapter output, canonical ingestion decision, and persisted session row for the same turn.

### Interrupt currently permits recovery

**Source-confirmed.** `ProviderService.interruptTurn` resolves a routable session with `allowRecovery: true`. If no live adapter session exists but the thread has persisted resume state, the routing path may start or resume the provider session before invoking `interruptTurn`.

**Inferred consequence.** A cancellation request can potentially create provider work or restore a dormant session solely to cancel a past turn. That may be intentional for providers whose cancellation protocol requires restoration, but it must be explicit and tested. The safer generic invariant is that cancellation does not resurrect execution unless the provider contract requires it and the UI can distinguish that recovery attempt.

The same recovery behavior exists for approval responses and user-input responses. This can be useful after a controller restart, but it also requires exact request identity, provider-instance affinity, and expiry checks so an old response cannot be applied to a different or already-finished request.

### Provider hot reload closes the old instance before replacement

**Source-confirmed.** The provider-instance registry gives each configured instance a child scope. During settings reconciliation it closes scopes for removed or changed instances before building replacements. Provider event subscribers rely on the old adapter stream ending and a registry-change notification causing new subscriptions to be installed.

**Inferred consequence.** An active turn can cross a replacement window in which the old final event is lost, the new adapter has no matching live session, or persisted state remains `running`. The registry correctly avoids two live instances with the same identity, but that invariant alone does not prove in-flight thread reconciliation.

### Event fanout and slow consumers

**Source-confirmed.** ProviderService publishes canonical runtime events through an unbounded PubSub. Multiple downstream consumers independently subscribe.

**Inferred consequence.** A slow or stalled consumer may accumulate events without applying backpressure to the provider adapter. This is preferable to globally blocking provider ingestion in some designs, but it needs queue observability, bounded failure behavior, or a documented memory contract.

## Cross-harness invariants

The following properties are useful across Gemini CLI, OpenCode, and T3 Code without requiring identical implementations:

1. **Completion provenance** — identify whether completion came from direct process exit, output closure, provider turn completion, provider idle, session exit, or controller reconciliation.
2. **Monotonic terminal state** — once a specific turn is durably complete, a delayed event must not restore it to running.
3. **Cancellation honesty** — acknowledge cancellation separately from verified provider/process settlement.
4. **No accidental resurrection** — interruption, denial, or stale response handling must not resume dormant work without an explicit provider requirement.
5. **Request affinity** — approval and user-input responses remain bound to the exact provider instance, session, turn, and request.
6. **Replay gap disclosure** — any bounded transcript or event replay states when earlier material has been omitted.
7. **Transport disclosure** — callers can tell whether they received merged pipes, tagged streams, raw PTY bytes/text, rendered screen state, or normalized provider events.
8. **Restart reconciliation** — persisted running state is checked against provider truth before the UI disables further input indefinitely.
9. **Adapter replacement settlement** — hot reload either drains and reconciles active sessions or explicitly marks them degraded/interrupted.
10. **Bounded subscriber state** — detached, inactive, and slow consumers have visible limits and cleanup behavior.

## Reusable adversarial cases

The retained `artifacts/contract-cases.json` describes these cases in machine-readable form:

1. Provider becomes idle but the controller remains running.
2. Controller restarts with a stale active turn while the provider is idle.
3. Interrupt against a persisted but inactive session.
4. Provider-instance hot reload during an active turn.
5. PTY attachment from a cursor older than retained history.
6. Inactive PTY subscriber while output continues.
7. Approval response after session recovery or provider-instance replacement.
8. Delayed running event after a completed event.

## Ranked branch candidates

### 1. Trace OpenCode completion into T3 persisted state

**Consequence:** a finished thread can remain unusable indefinitely and survive restart as falsely running.

**Likely owning boundary:** T3 OpenCode adapter, canonical provider-event contract, `ProviderRuntimeIngestion`, and persisted session projection.

**Evidence needed:** one target-native event trace containing provider session/turn identifiers, OpenCode idle/completion event, adapter-normalized event, lifecycle-guard decision, orchestration dispatch, persisted session state, and browser push.

**Recommendation:** open a narrow owned-fork campaign first.

### 2. Prevent interrupt-driven session resurrection

**Consequence:** a user cancellation can create or resume provider execution, produce new side effects, or target an obsolete turn.

**Likely owning boundary:** `ProviderService.resolveRoutableSession`, `recoverSessionForThread`, and adapter interruption contract.

**Evidence needed:** fake-adapter tests proving whether `interruptTurn` calls `startSession` when `hasSession` is false and resume state exists; then provider-specific tests for adapters that need restoration.

**Recommendation:** retain as a high-priority interface campaign.

### 3. Reconcile provider hot reload during active work

**Consequence:** settings changes can close an adapter before its terminal event is persisted, leaving a thread falsely active or silently detached.

**Likely owning boundary:** `ProviderInstanceRegistryLive`, adapter scope finalizers, ProviderService subscription reconciliation, and session directory.

**Evidence needed:** controlled fake adapter with an active turn, delayed terminal event, config replacement, and assertions over event delivery and final persisted state.

**Recommendation:** open after the completion trace, because both campaigns can share an event recorder.

### 4. Add explicit gap metadata to OpenCode PTY replay

**Consequence:** clients can treat a truncated suffix as complete terminal history.

**Likely owning boundary:** `packages/core/src/pty.ts` attachment contract and downstream terminal clients.

**Evidence needed:** service-level test with output exceeding the two-megabyte buffer and attachment from cursor zero; assert returned lower bound or gap metadata.

**Recommendation:** retain as a narrow OpenCode campaign.

### 5. Preserve approval affinity across recovery

**Consequence:** a stale approval or question response can be applied after the original request has expired, completed, or moved to another provider instance.

**Likely owning boundary:** T3 provider request contracts, persisted pending-request state, adapter response methods, and recovery routing.

**Evidence needed:** restart and provider-replacement tests with reused or delayed request identifiers.

**Recommendation:** another scout only if the completion trace does not already expose the request mapping.

### 6. Bound inactive and slow subscriber state

**Consequence:** a client that attaches but never activates, or a stalled canonical-event consumer, can accumulate memory independently of global replay limits.

**Likely owning boundary:** OpenCode PTY subscriber queues and T3 provider runtime PubSub.

**Evidence needed:** measured stress probes with controlled consumers and explicit memory/queue observations.

**Recommendation:** retain below correctness and recovery work.

## Negative results and stopped paths

- Gemini CLI was not re-scouted because #22 already completed the relevant lifecycle map and probes.
- No target-fork code was changed in this scout.
- No target-native executable or package test was run; external cloning/package access was unavailable in the execution environment.
- The OpenCode-to-T3 adapter root cause was not established. The issue reports remain context, not proof.
- UI styling, model quality, prompt quality, provider popularity, and influencer-driven product comparisons were excluded.
- T3's multi-provider normalization is not treated as inherently worse than a direct harness. It is a different contract with additional reconciliation responsibilities.
- OpenCode's merged agent-shell output is not treated as defective merely because a PTY or tagged-stream contract would differ.
- No ecosystem or operational prevalence claim is made from two issue reports.
- No upstream issue, comment, reaction, pull request, discussion, or direct contact occurred.

## Recommendation

Promote one owned-fork campaign: **OpenCode completion reconciliation through T3 Code**. Build a recorder at the adapter boundary and retain one trace covering a normal turn, a mid-turn steering prompt, completion, restart, and subsequent input availability. The trace should be reusable for provider hot reload and request-affinity work.

Keep the OpenCode PTY replay-gap candidate as a separate narrow campaign. Keep interrupt-driven recovery as the next T3 interface test because its source path is already concrete and can be tested with a fake adapter without model calls.
