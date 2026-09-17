# Scout: Harness control surfaces across Gemini CLI, OpenCode, and T3 Code

State: `ready-for-synthesis`

## In simple words

Gemini CLI and OpenCode directly own agent execution, sessions, tools, and terminal behavior. T3 Code sits above several agent harnesses and translates provider events into one persistent session model for its browser, desktop, and mobile control surfaces.

The strongest new finding is in T3's OpenCode adapter. OpenCode `session.status: idle` becomes a canonical T3 `turn.completed` event only when the adapter still has an in-memory active turn ID. When T3 resumes an OpenCode session, the durable cursor restores only the OpenCode session ID; the new adapter context starts with no active turn ID. An idle event after restart therefore cannot close the old T3 turn through this path. This is a source-supported explanation for why stale `working` state can survive restart. It does not yet prove why the state first becomes stuck during the reported mid-turn steering sequence.

A second concrete boundary appears in interruption. T3 may recover a dormant session before interrupting it. The OpenCode adapter then calls upstream abort and emits `turn.aborted`, but it does not itself clear the adapter's active turn or return the session to ready. T3's canonical lifecycle projection clears turns on `turn.completed`, inactive `session.state.changed`, or `session.exited`; `turn.aborted` is not one of those lifecycle transitions. Settlement therefore depends on a later OpenCode status event.

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

The scout read implementation, tests, architecture notes, and contribution guidance at the pinned revisions. It reused completed Gemini findings rather than opening a duplicate Gemini lane.

Evidence labels:

- **Source-confirmed** — directly supported by code at a pinned revision.
- **Documented** — stated by repository documentation.
- **Reported** — described in an external issue, not independently reproduced here.
- **Inferred** — a bounded implication from source-confirmed behavior that still needs a target-native trace.
- **Unknown** — the current source pass did not establish the answer.

A target-native run was not feasible in this execution environment because repository cloning and package installation could not reach external hosts. The retained adversarial case pack is a specification for the next owned-fork trace, not a claimed reproduction.

## Existing Gemini baseline

Fieldwork #22 already mapped Gemini CLI approval, invocation, process ownership, cancellation, session persistence, interruption, and recovery. Its retained findings include discarded abort signals for project-discovered tool subprocesses, confirmation-call affinity risk, missing durable interrupted-tool receipts, kill acknowledgement before verified process-tree exit, and approval waiting state that can survive abort.

Two rules carry forward:

1. A cancellation request, process signal, UI acknowledgement, direct-child exit, process-tree exit, output closure, turn completion, and durable session reconciliation are separate milestones.
2. A session history that records only model-facing content is insufficient to explain or recover partially completed tool and process work.

No new Gemini campaign is proposed here because #22 already produced ranked candidates and an owned-fork test-only draft.

## OpenCode map

### Agent shell tool

**Source-confirmed.** `packages/opencode/src/tool/shell.ts` runs commands through the selected shell. On non-Windows systems it requests a detached child; stdin is ignored. Output is consumed from the process handle's merged `all` stream, retained within bounded limits, and optionally spilled to a file.

The shell tool races process exit, caller abort, and timeout. Abort and timeout invoke process termination with forced escalation after three seconds. The result distinguishes timeout and user abort in metadata, while the merged output contract does not retain stdout/stderr identity.

This is a coherent model-facing shell contract. It should not be mistaken for a raw terminal transcript or proof that every descendant and inherited output descriptor has settled when the result returns.

### Managed PTY service

**Source-confirmed.** `packages/core/src/pty.ts` implements a separate interactive terminal contract:

- real PTY creation with `TERM=xterm-256color`;
- input and resize support;
- a two-megabyte retained string buffer;
- absolute output cursors;
- replay followed by live activation;
- exited-session retention;
- explicit remove semantics.

#### Replay gaps are not disclosed

When an attachment requests a cursor older than the retained buffer, replay starts at the oldest surviving character. The attachment reports the current end cursor, but no omitted-prefix count, lower-bound cursor, or gap flag.

**Inferred consequence.** A reconnecting client can receive a valid suffix and interpret it as complete history.

#### Buffer trimming uses JavaScript string offsets

The service tracks capacity through string length and trims with `slice(excess)`.

**Inferred consequence.** Trimming can split a UTF-16 surrogate pair, causing replay to begin with an unpaired surrogate.

#### Inactive subscribers accumulate pending chunks

An attached subscriber remains inactive until the caller applies replay and calls `activate()`. Chunks arriving in that interval are appended to a per-subscriber pending array without a source-visible bound or detachment deadline.

**Inferred consequence.** A stalled client can create subscriber-specific memory growth even though the shared replay buffer is bounded.

## T3 Code map

### Role and architecture

**Documented.** T3 Code describes itself as an agent harness control surface. It can control Codex, Claude Code, Cursor, Grok Build, and OpenCode. Its Node server routes provider operations through adapters, normalizes provider-native events into orchestration events, persists read-model state, and pushes updates to clients.

This is materially different from OpenCode's role. T3 does not need providers to behave identically. It needs its canonical contract to retain provider differences that affect correctness, approval, interruption, recovery, and availability.

### Provider session routing and persistence

**Source-confirmed.** `ProviderService` routes by provider instance and persisted thread binding. On `sendTurn`, it may recover a missing live session from persisted resume state, forwards the turn, then stores provider identity, `status: running`, resume cursor, `activeTurnId`, and last runtime operation.

`ProviderRuntimeIngestion` owns the orchestration clearing path. It applies `session.state.changed`, `turn.started`, `turn.completed`, and `session.exited`. A completed turn or inactive session state clears `activeTurnId`; a completed turn normally sets status to `ready`.

### Exact OpenCode adapter completion mapping

**Source-confirmed.** `apps/server/src/provider/Layers/OpenCodeAdapter.ts` subscribes to OpenCode SDK events and filters them by OpenCode session ID.

For `session.status`:

- `busy` updates the adapter's local `ProviderSession` to running;
- `retry` emits a canonical runtime warning;
- `idle` clears local active state and emits canonical `turn.completed` only when `context.activeTurnId` is present.

The adapter's `sendTurn` sets `context.activeTurnId` before calling `session.promptAsync`. A prompt sent while a turn is already active is treated as steering: it reuses the current turn ID and does not emit a second `turn.started`. Under normal event ordering, the next idle status should complete that shared turn.

This narrows the reported steering failure. A stuck pre-restart thread can arise if:

1. OpenCode does not deliver the expected idle status;
2. the adapter filters or loses the event;
3. adapter active-turn identity is cleared or absent before idle;
4. canonical completion is emitted but rejected or later overwritten downstream.

The source pass does not select among those four for the initial failure.

### Resume restores provider session identity, not active turn identity

**Source-confirmed.** The OpenCode resume cursor contains a schema version and OpenCode session ID. `startSession` can re-adopt that session and its conversation history. The newly built `OpenCodeSessionContext` initializes `activeTurnId` as undefined. The start input and cursor do not restore the old T3 turn ID.

**Source-supported consequence.** After T3 loses its in-memory adapter context while the orchestration projection still records a running turn, the resumed adapter cannot associate a later OpenCode idle status with that old turn. Its idle branch requires an in-memory turn ID before it emits `turn.completed`. T3's stale orchestration state therefore has no completion event from this path to clear it.

This supports the restart-persistence portion of the public reports. It remains possible that another reconciliation path clears stale state in some restart modes; that must be checked by the target-native trace.

### Reported OpenCode/T3 divergence

External issue context:

- `https://redirect.github.com/pingdotgg/t3code/issues/2173`
- `https://redirect.github.com/pingdotgg/t3code/issues/2886`

**Reported.** Both describe OpenCode-backed threads that finish at the provider but remain permanently `working` in T3. The later report says OpenCode itself shows the run ended while T3 remains locked after restart. It was closed as a duplicate of the earlier open issue.

The reports align with the source-supported restart identity gap. They do not prove the initial mid-turn steering failure has the same cause.

### Interrupt permits recovery and does not directly settle local lifecycle

**Source-confirmed.** `ProviderService.interruptTurn` resolves a session with `allowRecovery: true`. If no live adapter session exists but resume state is available, the controller may re-adopt or start a provider session before interruption.

The OpenCode adapter then calls `session.abort` and emits canonical `turn.aborted`. It does not clear `context.activeTurnId`, update its local session to ready, or emit `turn.completed` in the interrupt method.

`ProviderRuntimeIngestion` treats `turn.completed`, inactive `session.state.changed`, and `session.exited` as lifecycle transitions. `turn.aborted` is not included in that session-state transition block.

**Source-supported consequence.** Interruption acknowledgement and lifecycle settlement are separate. If OpenCode subsequently emits idle, the adapter can settle through `turn.completed`. If no idle arrives, local and persisted running state can remain until another recovery or stop path intervenes.

**Inferred consequence.** Because interruption permits recovery, a request to cancel an old turn can restore a dormant provider session solely to abort it. That may be necessary for some provider contracts, but it should be explicit and tested.

### Approval and user-input recovery

**Source-confirmed.** Approval responses and user-input responses also allow session recovery at the ProviderService layer. The OpenCode adapter checks its in-memory pending-permission or pending-question maps before replying.

**Source-supported consequence.** Re-adopting an OpenCode session does not reconstruct those pending maps from the cursor. A post-restart response can therefore fail as an unknown request even when the provider still considers it pending. Conversely, any future reconstruction must preserve provider-instance, session, turn, and request affinity.

### Provider hot reload closes old instance before replacement

**Source-confirmed.** Each provider instance owns a child scope. Settings reconciliation closes removed or changed instance scopes before building replacements. Provider event subscribers rely on the old stream ending and a registry-change notification installing new subscriptions.

**Inferred consequence.** An active turn can cross a replacement window in which the old terminal event is lost or persisted state remains running. The registry correctly prevents two live instances with the same identity, but that does not prove in-flight reconciliation.

### Event fanout and slow consumers

**Source-confirmed.** ProviderService publishes canonical runtime events through an unbounded PubSub, and the OpenCode adapter itself uses an unbounded runtime-event queue.

**Inferred consequence.** A stalled consumer can accumulate events without provider backpressure. This needs queue observability, a documented bound, or explicit overload behavior.

## Cross-harness invariants

1. **Completion provenance** — distinguish process exit, output closure, provider turn completion, provider idle, session exit, and controller reconciliation.
2. **Monotonic terminal state** — a delayed event must not restore a durably completed turn to running.
3. **Cancellation honesty** — acknowledge cancellation separately from verified provider/process settlement.
4. **No accidental resurrection** — interruption or stale response handling does not resume dormant work without an explicit provider requirement.
5. **Request affinity** — approval and user-input responses remain bound to provider instance, session, turn, and request.
6. **Replay gap disclosure** — bounded transcript or event replay states when earlier material was omitted.
7. **Transport disclosure** — callers know whether they received merged pipes, tagged streams, PTY text, rendered screen state, or normalized events.
8. **Restart reconciliation** — persisted running state is checked against provider truth before input is disabled indefinitely.
9. **Adapter replacement settlement** — hot reload drains/reconciles active sessions or marks them degraded/interrupted.
10. **Bounded subscriber state** — detached, inactive, and slow consumers have visible limits and cleanup behavior.

## Reusable adversarial cases

The retained `artifacts/contract-cases.json` covers:

1. provider idle clears persisted active turn;
2. restart with stale running state and lost adapter turn identity;
3. interrupt against a persisted but inactive session;
4. abort without a later idle status;
5. provider-instance hot reload during an active turn;
6. PTY replay from a cursor older than retained history;
7. inactive PTY subscriber while output continues;
8. approval response after recovery or instance replacement;
9. delayed running event after completion.

## Ranked branch candidates

### 1. OpenCode active-turn identity across T3 restart

**Consequence:** a finished provider session can remain permanently unusable in T3 after restart.

**Owning boundary:** OpenCode resume cursor, `OpenCodeSessionContext`, ProviderService recovery, and orchestration reconciliation.

**Evidence needed:** a fake/OpenCode adapter test that seeds a persisted running turn, rebuilds the adapter from its cursor, delivers busy then idle status, and asserts the old orchestration turn becomes ready with `activeTurnId: null`.

**Recommendation:** first owned-fork campaign.

### 2. Mid-turn steering completion trace

**Consequence:** a thread can become stuck before restart and remain impossible to continue.

**Owning boundary:** OpenCode SDK event ordering, session-ID filtering, adapter active-turn state, canonical completion, and lifecycle guard.

**Evidence needed:** one recorder covering normal turn, first steer, second steer, OpenCode status events, adapter events, ingestion decisions, persisted session row, and browser availability.

**Recommendation:** share instrumentation with candidate 1.

### 3. Interrupt settlement without relying on incidental idle

**Consequence:** cancellation can be acknowledged while adapter and controller remain running.

**Owning boundary:** `ProviderService.interruptTurn`, OpenCode `session.abort`, `turn.aborted`, and canonical lifecycle projection.

**Evidence needed:** fake SDK test with and without a later idle event; assert explicit final status and active-turn cleanup.

### 4. Provider hot reload during active work

**Consequence:** settings changes can close an adapter before its terminal event is persisted.

**Owning boundary:** `ProviderInstanceRegistryLive`, adapter finalizers, subscriber reconciliation, and session directory.

**Evidence needed:** delayed-terminal-event fake adapter plus config replacement.

### 5. OpenCode PTY replay gap metadata

**Consequence:** a client can treat a truncated suffix as complete terminal history.

**Owning boundary:** `packages/core/src/pty.ts` attachment contract.

**Evidence needed:** output exceeding retention, attachment from cursor zero, and assertion for lower-bound/gap metadata and Unicode boundary.

### 6. Pending request recovery affinity

**Consequence:** valid pending requests can become unanswerable after restart, or future reconstruction can misapply stale responses.

**Owning boundary:** OpenCode pending maps, resume contract, T3 request persistence, and response routing.

**Evidence needed:** restart tests for pending permission and question events.

### 7. Bound inactive and slow subscriber state

**Consequence:** inactive PTY clients or stalled event consumers can grow memory independently of shared replay limits.

**Owning boundary:** OpenCode PTY pending arrays and T3/OpenCode unbounded event queues.

**Evidence needed:** measured stress probe with controlled consumers.

## Negative results and stopped paths

- Gemini CLI was not re-scouted because #22 already completed the lifecycle map and probes.
- No target-fork code was changed in this scout.
- No target-native executable or package test was run; external cloning/package access was unavailable.
- The source supports a restart reconciliation gap, but does not prove the initial steering failure's root cause.
- Public issue reports are context, not prevalence evidence.
- UI styling, model quality, prompt quality, provider popularity, and influencer-driven product ranking were excluded.
- T3's multi-provider normalization is not treated as inferior to a direct harness. It has additional reconciliation responsibilities.
- OpenCode's merged agent-shell output is not treated as defective merely because its PTY contract differs.
- No upstream issue, comment, reaction, pull request, discussion, or direct contact occurred.

## Recommendation

Promote an owned-fork campaign combining **OpenCode active-turn identity across T3 restart** with the **mid-turn steering completion trace**. Add boundary recording to the T3 OpenCode adapter, then retain one trace for a normal turn, repeated steering, completion, restart, and subsequent input availability.

Keep interrupt settlement as the next fake-adapter test because the source path is concrete and does not require model calls. Keep OpenCode PTY replay-gap work separate and narrow.
