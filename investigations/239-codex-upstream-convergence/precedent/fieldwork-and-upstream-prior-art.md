# Fieldwork and upstream prior art

Owner: lane J/O synthesis for Fieldwork #239  
Retrieval date: 2026-07-31  
Evidence class: documented upstream PR intent, current source-read, and retained Fieldwork execution records  
Upstream contact authorized: `false`

## In simple words

Most Codex findings sit near work upstream already performed: moving writes into `ThreadStore`, serializing refresh, reusing request-stable snapshots, bounding output, and ordering lifecycle events. That prior art changes the right proposal.

The strongest remaining Fieldwork ideas add a missing fact or ownership rule at an existing boundary. They should extend current owners instead of recreating old subsystems.

## How to read this file

Each precedent entry records:

- what the earlier work owns;
- which Fieldwork question it informs;
- which gap remains;
- how it affects proposal boundaries.

A related PR is evidence of design direction and existing behavior at its exact revision. Current source and target-native execution remain required before a present-tense claim.

## Thread store, append, and history

### Route live thread writes through ThreadStore — upstream PR #18882

Source: <https://github.com/openai/codex/pull/18882>

Established direction:

- `ThreadManager` owns loaded-thread coordination;
- `CodexThread` is the outside handle;
- `LiveThread` owns one active thread's persistence lifecycle;
- `ThreadStore` owns storage behavior;
- local rollout recording becomes a store implementation detail.

Fieldwork consequence:

Append-outcome work belongs at the `Session → LiveThread → ThreadStore::append_items` boundary. A new parallel recorder or session-owned persistence subsystem would fight the accepted ownership model.

Remaining gap:

Current session persistence logs append failure and returns no caller-visible outcome.

### Move live thread metadata handling above recorder — upstream PR #21874

Source: <https://github.com/openai/codex/pull/21874>

Established direction:

- canonical rollout writing and metadata projection have distinct owners;
- `LiveThread` sequences canonical items and explicit metadata updates;
- recorder responsibilities stay narrow.

Fieldwork consequence:

Typed result persistence should describe canonical append outcome before layering metadata visibility or projection status into the same enum.

Remaining gap:

A caller still needs to know whether the canonical result append was acknowledged, ambiguous, or absent.

### Thread history projection observers — upstream PR #26527

Source: <https://github.com/openai/codex/pull/26527>

Established direction:

- live append events can feed typed projection observers;
- turn items, summaries, and lifecycle mutations derive from canonical history events;
- persistence of those projections remains separable from canonical rollout append.

Fieldwork consequence:

Result identity and persistence outcome should be available before projections consume or compact the item. A projection success cannot repair an unknown canonical append.

### Project append metadata asynchronously — upstream PR #30669

Source: <https://github.com/openai/codex/pull/30669>

Established direction:

- normal `LiveThread::append_items` may return after rollout append acceptance while metadata projection continues;
- explicit visibility callers can wait on a projection generation;
- append critical-path latency and metadata query visibility are separate facts.

Fieldwork consequence:

A useful result model needs separate dimensions for canonical append acceptance and later metadata visibility. Treating every delayed projection as append failure would misclassify current architecture.

### Release thread writer after failed shutdown — upstream PR #31155

Source: <https://github.com/openai/codex/pull/31155>

Established direction:

- a terminal session can lose flush while still needing writer-lease cleanup;
- cleanup must remain tied to the writer generation captured when the cleanup handle is created;
- stale cleanup cannot discard a replacement writer after resume.

Fieldwork consequence:

Ambiguous persistence and writer-generation ownership survive past the immediate append call. Resume, cleanup, and retry need generation-aware rules.

### Session segmentation — upstream PR #27249

Source: <https://github.com/openai/codex/pull/27249>

Established direction:

- append, flush, shutdown, and rotation serialize through one per-thread writer transaction;
- accepted appends fall entirely before or after rotation;
- canonical rollout replacement avoids remove-then-rename gaps.

Fieldwork consequence:

Result-persistence proposals should reuse the writer transaction and generation model. They should avoid adding an independent operation journal inside session code.

### Avoid persisting shutdown completion after writer close — upstream PR #19630

Source: <https://github.com/openai/codex/pull/19630>

Established direction:

- terminal lifecycle events can become invalid after persistence ownership closes;
- event emission and durable recording require ordering discipline.

Fieldwork consequence:

The result shown to the model, the event shown to clients, and the item accepted by durable history require explicit ordering and failure policy.

### Rollout source and in-memory source — upstream PR #13096

Source: <https://github.com/openai/codex/pull/13096>

Established direction:

- replay readers can use a common rollout-source interface;
- one process-local in-memory source can track runtime writes;
- deferred file materialization and resumed history remain explicit boundaries.

Fieldwork consequence:

Live conversation authority and durable persistence authority can differ. An ephemeral source may be authoritative for one session while remaining unsuitable as proof of durable recovery.

### Store-owned thread catalog changes — upstream PR #29894

Source: <https://github.com/openai/codex/pull/29894>

Established direction:

- catalog-visible mutations publish through the store owner;
- subscribers consume IDs and reread store truth;
- receiver lag requires snapshot rebuild;
- lazy thread creation publishes only after real materialization.

Fieldwork consequence:

Publication follows successful store mutation. The same principle supports reporting append acknowledgement before downstream consumers treat a result as durable.

## MCP runtime, reconnect, and publication

### Reuse MCP connections across runtime refreshes — upstream PR #34952

Source: <https://github.com/openai/codex/pull/34952>

Established direction:

- unchanged ready servers can survive ordinary runtime refresh;
- transport, environment, authentication, credentials, capabilities, filters, timeouts, metadata, and provenance influence reuse;
- publication exposes a reconciled connection set.

Fieldwork consequence:

Host reload cannot mean “always reconnect” for every update path. Explicit refresh needs a distinct freshness request while ordinary unchanged reconciliation preserves reuse.

### Reconnect MCP servers on explicit refresh — upstream PR #35151

Source: <https://github.com/openai/codex/pull/35151>

Established direction:

- explicit refresh requests a rebuilt connection for configured servers;
- a cancelled replacement preserves the reconnect request for the next attempt.

Fieldwork consequence:

This directly overlaps owned Codex #46's host-refresh primitive and may absorb part of its behavior at newer source. The current convergence pass must compare exact call paths and tests before retaining a duplicate proposal.

Remaining question:

The Fieldwork publication-generation and accepted-result identity controls remain separate until current upstream proves them.

### Refresh one MCP server in place — upstream PR #30083

Source: <https://github.com/openai/codex/pull/30083>

Established direction:

- replacement can be prepared before swap;
- unrelated clients and in-flight readers remain intact;
- cancellation ownership transfers after successful swap;
- startup completion reports failures.

Fieldwork consequence:

A broad reconnect proposal should respect targeted replacement and reader lifetime. Prepared and active calls need captured binding through the swap.

### Apps runtime manager and immutable snapshot — upstream PR #31471

Source: <https://github.com/openai/codex/pull/31471>

Established direction:

- committed connector runtime state belongs to one manager;
- snapshots are immutable;
- stale contexts stop advertising or executing old tools;
- accepted snapshot persistence serializes so disk cannot regress behind memory.

Fieldwork consequence:

The newest-generation-only publication proposal aligns with manager-owned immutable snapshots. It should integrate with that owner and avoid a second cache or publication gate.

### Request-stable MCP tool snapshot — upstream PR #31292

Source: <https://github.com/openai/codex/pull/31292>

Established direction:

- one sampling step reuses one lazy tool snapshot;
- context and router construction see the same tool list;
- later steps refresh naturally.

Fieldwork consequence:

Capability authority should be step-stable. A proposal can compare the request snapshot's identity with the runtime binding without requiring global catalogue immutability.

### Stable plugin metadata separated from live runtime — upstream PR #29946

Source: <https://github.com/openai/codex/pull/29946>

Established direction:

- selected plugin metadata and live MCP processes have different lifetimes;
- environment-root facts can remain stable while runtime connections rebuild.

Fieldwork consequence:

Manifest identity must distinguish metadata provenance from live execution authority. Matching plugin metadata alone cannot prove that the current runtime owns the call.

### Shared Apps startup reconnect — upstream PR #31626

Source: <https://github.com/openai/codex/pull/31626>

Established direction:

- explicit client operations can join one in-flight startup reconnect;
- cached discovery stays non-blocking;
- hard refreshes route through the recovered client.

Fieldwork consequence:

Reconnect and publication proposals need concurrency controls that compose with shared in-flight recovery instead of spawning independent refresh work.

## Request manifests, Code Mode, and Responses Lite

### Responses Lite input-item tool contract — commit `33cc928d339307795d4f5987337c7c4607f70338`

Source: <https://github.com/openai/codex/commit/33cc928d339307795d4f5987337c7c4607f70338>

Established direction:

- Responses Lite carries tools through `additional_tools` and a developer input item;
- top-level tools and instructions no longer represent the full capability contract.

Fieldwork consequence:

The first generated request after startup prewarm must preserve the model-visible input prefix or deliberately establish equivalent server-side authority.

### Code Mode tool-name metadata — upstream PR #35271

Source: <https://github.com/openai/codex/pull/35271>

Established direction:

- Responses Lite metadata maps normalized Code Mode identifiers to structured tool names;
- reserved metadata remains hidden from external MCP servers;
- HTTP and websocket requests share the mapping behavior.

Fieldwork consequence:

Capability identity includes both declarations and metadata. A first-turn control should compare the complete logical prefix and relevant reserved metadata.

### Normalized Code Mode name collisions — upstream PR #36129

Source: <https://github.com/openai/codex/pull/36129>

Established direction:

- one registered tool wins each normalized identifier;
- executor dispatch and model-facing declaration use the same winner;
- direct and deferred exposure remain distinct.

Fieldwork consequence:

Deferred-loader work should reuse the canonical collision owner. A loader proposal must preserve the same normalized identity used for declaration and dispatch.

### Logical websocket trace after untraced prewarm — commit `20fedafff83f5c681fc62f73b0ca3227e42e3f8b`

Source: <https://github.com/openai/codex/commit/20fedafff83f5c681fc62f73b0ca3227e42e3f8b>

Established direction:

- transport compression may reuse a warmup response ID;
- rollout tracing records the logical model-visible request when wire input is empty.

Fieldwork consequence:

Logical tracing and capability transmission require separate tests. A correct trace can describe a request that the server reconstructed incorrectly.

### Standalone Code Mode host — commit `97576b1794872e342450ebd577123e052ab57626`

Source: <https://github.com/openai/codex/commit/97576b1794872e342450ebd577123e052ab57626>

Established direction:

- Code Mode execution moves to a standalone host boundary.

Fieldwork consequence:

The deferred executable-loader proposal must target the host's capability and execution contract rather than the historical in-core placement.

## Unified execution and terminal output

### Bound unified-exec output collection — upstream PR #31802

Source: <https://github.com/openai/codex/pull/31802>

Established direction:

- collection uses a bounded head/tail buffer;
- output continues draining after the retention limit;
- omission is explicit.

Fieldwork consequence:

Producer-owned retention must preserve the bounded policy. “Complete” means complete within the declared retained window plus omission metadata.

### Order unified-exec lifecycle events — upstream PR #34713

Source: <https://github.com/openai/codex/pull/34713>

Established direction:

- output-task closure signals trailing-output completion;
- remaining chunks drain before command completion;
- late network denial classification precedes the final result;
- interaction and completion events serialize.

Fieldwork consequence:

Terminal retention can rely on the close/drain ordering while adding the missing producer-before-broadcast ownership. Hard termination remains a separate gap.

### Avoid shifting streaming output bytes — upstream PR #36194

Source: <https://github.com/openai/codex/pull/36194>

Established direction:

- pending decode bytes use `VecDeque`;
- invalid UTF-8 advances without repeated front shifting;
- focused tests cover valid bytes around invalid input.

Fieldwork consequence:

The historical terminal patch must be reconstructed semantically. A direct cherry-pick would discard current decoding improvements.

### Windows process-tree containment — upstream PRs #29981 and #29982

Sources:

- <https://github.com/openai/codex/pull/29981>
- <https://github.com/openai/codex/pull/29982>

Established direction:

- restricted and elevated sessions enter a Job Object before readiness;
- timeout, explicit termination, and control transport loss terminate the job;
- output-reader joins follow containment and root-exit rules.

Fieldwork consequence:

Terminal transcript retention and process-tree settlement are adjacent but independent. A transcript patch should avoid claiming cross-platform termination guarantees.

## Fieldwork process precedent

### Separate result files from synthesis

[`COORDINATION.md`](../../../COORDINATION.md) assigns worker-owned lane reports and coordinator-owned synthesis and decision files. [`BATCHES.md`](../../../BATCHES.md) uses worker-owned `results/` plus coordinator synthesis and closeout.

Convergence consequence:

This workspace follows the same rule: findings remain independently authored; canonical outputs are explicit coordinator decisions.

### Separate execution carriers from canonical source

[`REVIEWING.md`](../../../REVIEWING.md) requires execution carriers to name the canonical source, exact workflow, and retained receipt, then retire after evidence transfer.

Convergence consequence:

Owned Codex #52 and #53 can prove source behavior while remaining unsuitable as delivery branches.

### Preserve alternatives and negative results

[`CHARTER.md`](../../../CHARTER.md) requires source state, hypotheses, experiments, alternatives, uncertainty, and final decisions. A disproved candidate can remain useful historical evidence.

Convergence consequence:

Absorbed or obsolete Codex candidates should produce explicit stopped records, avoiding repeated investigation.

## Precedent-driven proposal rules

The prior art supports these rules for future canonical outputs:

1. extend current owners instead of creating parallel stores, caches, or state machines;
2. separate canonical append from metadata projection and remote-effect settlement;
3. make generation and operation identity explicit across asynchronous replacement;
4. use request-stable snapshots for model-visible capability and dispatch agreement;
5. preserve bounded output policy and current lifecycle ordering;
6. keep exact execution carriers outside canonical source;
7. publish several bounded proposals when ownership, evidence, and compatibility differ.