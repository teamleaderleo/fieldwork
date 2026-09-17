# Authoritative run state across agent runtimes

## In simple words

Agent systems often have several copies of “what is happening now”: an active model stream, a session status flag, persisted run data, a replay stream, a provider job, and UI state. This scout asks which copy is allowed to become authoritative when asynchronous paths overlap.

Four source-level candidates currently survive reduction:

1. Vercel AI SDK provider polling can accept a successful job after `pollTimeoutMs` has elapsed.
2. TanStack AI can persist an intermediate transformed generation result that differs from the final live result.
3. OpenCode can publish `idle` from an older completion while replacement work is active.
4. Vercel AI can adopt a previous assistant message when resuming a different run; this is already publicly reported and is retained as comparison evidence.

The dependency-free probes demonstrate ordering properties, not target-package execution. Focused owned-fork test carriers exist for the Vercel Google provider and OpenCode. The Vercel carrier has registered repository CI; the OpenCode carrier has not registered a check, so its evidence remains `target-test-prepared`.

## Assignment

- Fieldwork issue: `teamleaderleo/fieldwork#528`
- Worker: GPT-5.6 Thinking, directed by teamleaderleo
- Programme: `open-source-ecosystems`
- Owned path: `programmes/open-source-ecosystems/scouts/agent-runtime-run-authority/`
- Claim scope: mechanism and interface
- Retrieval date: 2026-08-02
- Upstream contact authorized: `false`

## Exact source pins

| Target | Revision | Retained source boundaries |
| --- | --- | --- |
| Vercel AI SDK | `3bc0d4f40df7a77af4b181bc97dc1c54843545ab` | Google, Google Vertex, FAL, Replicate, MiniMax, and xAI provider polling; chat resume state |
| TanStack AI | `6feb5644a38073c5865f7b4ff4d64d62195e755b` | generation middleware, persistence middleware, generation activities, generation client |
| OpenCode | `1882c33827cf0ce5c948b69ab5a87ed8f6790cf8` | Runner, SessionRunState, SessionStatus, prompt loop, Runner tests |

Codex was inspected as a possible comparison target, then excluded because Fieldwork already has a live convergence initiative and multiple exact-head authority, persistence, terminal, MCP, replay, and cancellation campaigns. This scout will not duplicate them.

## Candidate 1 — Vercel AI SDK polling timeout is not a deadline

### Current behavior

Several providers implement submit-then-poll independently.

The older loop family, including Google, Google Vertex, and Replicate, checks elapsed time before sleeping. It then sleeps for the full polling interval, performs a status request, and accepts a terminal response without checking the deadline again. FAL checks after an in-progress poll, sleeps without passing the available abort signal, and accepts a later successful poll before another timeout check.

A newer family, including xAI and MiniMax, uses the provider utility's abort-aware delay and checks elapsed time after sleeping. This fixes user-abort latency during the sleep and prevents the full-interval case. It still begins a status request before the deadline and can accept that response after the request itself carries elapsed time beyond `pollTimeoutMs`.

The shared `delay` utility already accepts an abort signal. The inconsistency comes from each provider owning its own clock, sleep, request, timeout error, and terminal-publication sequence.

### Consequence

`pollTimeoutMs` behaves as a periodic observation rather than an authoritative maximum wait:

- with `pollTimeoutMs = 5` and `pollIntervalMs = 30`, a legacy provider can return success after about 30 ms;
- with a newer provider, a poll started before the deadline can return success after the request pushes total elapsed time past the deadline;
- user abort can remain unobserved for one full polling interval in providers that call `delay(pollIntervalMs)` without the signal.

For default provider settings, the overshoot can be seconds. A caller using the timeout for request budgeting, fallback selection, billing control, job ownership, or UI settlement cannot rely on the configured value.

### Model receipt

Run:

```sh
node artifacts/vercel-poll-deadline-model.mjs
```

Observed:

```json
{
  "legacyIntervalOvershoot": {
    "outcome": "success",
    "elapsed": 30
  },
  "newerRequestOvershoot": {
    "outcome": "success",
    "elapsed": 35
  },
  "deadlineOwnedIntervalCase": {
    "outcome": "timeout",
    "elapsed": 5
  },
  "deadlineOwnedRequestCase": {
    "outcome": "timeout",
    "elapsed": 35
  }
}
```

Evidence class: `model-executed` plus `source-read`.

### Target-native carrier

Owned fork:

- branch: `teamleaderleo/ai:research/google-video-poll-deadline`
- exact base branch: `research/base-3bc0d4f`
- draft PR: `teamleaderleo/ai#16`
- test: `packages/google/src/google-video-poll-deadline.test.ts`
- current head: `d3aa766d6edb54aad8cf0115bb55a771bac03ec9`

The test configures a 5 ms timeout and a 30 ms interval. The first provider status poll returns a completed video. The invariant requires timeout rather than accepting the late completion. Repository CI registered as run `30754271977`; it was queued at the latest observation.

Evidence class: `target-test-prepared`, pending execution.

### Duplicate state

No open issue or pull request was found in the first searches for polling deadline overshoot, late completion after `pollTimeoutMs`, or abort-insensitive polling delay.

### Next discriminating tests

1. Run the Google target-native regression.
2. Add the same invariant to Google Vertex and one non-Google provider.
3. Add a slow status request that starts before the deadline and completes after it.
4. Abort during the sleep and assert prompt settlement rather than one-interval delay.
5. Check whether the remote provider exposes cancellation; keep local settlement and remote job certainty separate.

### Likely repair boundary

A correct repair needs one authoritative deadline across sleep and status fetch, not merely another elapsed-time check. Candidate shapes:

- a shared provider-utils polling primitive that combines the caller signal with a deadline signal, bounds sleep to remaining time, and supplies provider-specific timeout construction; or
- a smaller shared deadline controller used by provider-local loops.

The primitive must preserve provider-specific response handling, URL validation, status schemas, warnings, and error names. It must also define whether a response completed exactly at the deadline is accepted. The conservative candidate is deadline ownership by the caller: after expiry, late success cannot publish as the call result.

## Candidate 2 — TanStack AI persists an intermediate transform

### Current behavior

Generation middleware runs `onStart` in registration order. Middleware may append functions to one shared `ctx.resultTransforms` array. The activity later applies every transform in array order and returns the final value.

`withGenerationPersistence` appends a transform that writes result metadata to the durable generation run record. If another middleware registered after persistence appends a later transform, persistence stores the intermediate value while the activity returns or streams the later final value.

### Consequence

The same successful run can have two authoritative results:

- the live caller sees the final transformed result;
- a reload or server-authoritative hydration reconstructs the earlier persisted result.

For media generation this can mean different URLs, metadata, artifact references, or provider-normalized fields before and after reload.

### Model receipt

Run:

```sh
node artifacts/tanstack-transform-order-model.mjs
```

Observed:

```json
{
  "persisted": {
    "url": "provider://temporary"
  },
  "live": {
    "url": "durable://final"
  },
  "restoredMatchesLive": false
}
```

Evidence class: `model-executed` plus `source-read`.

### Negative result retained

The obvious mount-hydration race is already fenced in the current generation client: after hydration awaits, it re-checks that no live generation or restored snapshot has taken ownership before repainting. Rejoin cleanup also checks controller identity before clearing loading state. This scout does not reopen those paths.

### Next discriminating test

Use the target's generation middleware harness:

1. register persistence first;
2. register a custom middleware second that appends a visible result transform;
3. generate a synthetic result;
4. assert the returned result and reconstructed persisted result are identical.

Cover metadata-only and artifact persistence.

### Likely repair boundary

Durable result capture needs a post-transform/final-result boundary. It should not be an ordinary transform whose observation depends on middleware registration order. Artifact rewriting may remain a transform; recording the authoritative final result should occur after all transforms complete.

## Candidate 3 — OpenCode stale idle publication after replacement work

### Current behavior

`Runner.finishRun` changes the runner state from `Running` to `Idle`, then executes the returned `onIdle` effect. `SessionRunState` supplies an `onIdle` effect that first removes the runner from the session registry and then awaits `SessionStatus.set(...idle)`. Status publication awaits event delivery before deleting the busy status entry.

A new request can therefore create and start a replacement runner after the old registration is removed but before the old idle publication settles. The replacement loop writes `busy`; the older idle path can then publish `idle` and remove the status entry while the replacement remains active.

### Consequence

The session registry can correctly point at replacement work while the public status source says idle. Callers that use status to decide whether work can be awaited, displayed, cancelled, or replaced can act on stale authority. This is a deterministic replacement-ordering form of the broader stale-status family, not proof of every reported indefinite-busy symptom.

### Model receipt

Run:

```sh
node artifacts/opencode-stale-idle-model.mjs
```

Observed:

```json
{
  "beforeStaleIdle": {
    "registeredRunner": "B",
    "status": "busy"
  },
  "afterStaleIdle": {
    "registeredRunner": "B",
    "status": "idle"
  }
}
```

Evidence class: `model-executed` plus `source-read`.

### Target-native carrier

Owned fork:

- branch: `teamleaderleo/opencode:research/runner-stale-idle-authority`
- exact base branch: `research/base-1882c338`
- draft PR: `teamleaderleo/opencode#1`
- test: `packages/opencode/test/session/run-state-authority.test.ts`

The carrier uses the target's actual `Runner` and reproduces the SessionRunState ordering with a controllable status-publication barrier. A branch-scoped workflow was added, but no check or workflow run registered. Evidence remains `target-test-prepared`.

### Prior-art state

A current public issue reports server status lag after a prompt response completes. A closed unmerged draft previously grouped concurrent prompt races with stale busy cleanup. Neither inspected artifact demonstrates this exact replacement ordering on the current Runner/SessionRunState architecture.

### Likely repair boundary

Fence idle publication by the runner generation that still owns the session. A completion may remove or mark idle only if no replacement registration/run has taken authority. Do not fix this with a delay or client-side status heuristic.

## Candidate 4 — Vercel AI resume adopts the wrong assistant message

### Current behavior

The chat client seeds resumed stream state from the current last message whenever its role is `assistant`. The resumed stream's actual `messageId` arrives later in a `start` chunk, which renames the adopted message without checking identity. New resumed parts are then appended to the previous turn's parts.

### Consequence

A client reconnecting to a run started elsewhere can duplicate the prior assistant answer and attach it to the resumed run ID. The old answer remains in history.

### Model receipt

Run:

```sh
node artifacts/vercel-resume-adoption-model.mjs
```

The model produces two messages containing `first answer`; the resumed message contains both the previous answer and `RESUMED-TEXT`.

Evidence class: `model-executed` plus `source-read`.

### Duplicate state

This behavior is already described in a current public issue and remains present at the pinned revision. No open repair was found in the first PR search. Retain it as comparison evidence, not a novel Fieldwork unit.

### Likely repair boundary

Resume adoption must be identity-aware. The implementation must either defer adoption until `start`, or preserve a pristine baseline and discard adopted parts when IDs differ.

## Ranking

1. **Vercel AI cross-provider polling deadline** — broad runtime leverage, a concrete target-native carrier, and a likely shared invariant across rapidly expanding async providers.
2. **TanStack AI final-result persistence boundary** — high novelty and architectural leverage; small deterministic target-native test remains to be materialized.
3. **OpenCode replacement-run status authority** — high operational consequence and a pinned mechanism; exact target execution and prior-art distinction remain mandatory.
4. **Vercel AI resume identity** — high consequence but already known publicly.

## Negative results and stopped branches

- TanStack AI mount hydration does not blindly overwrite a live generation at the pinned revision.
- TanStack AI rejoin cleanup checks controller identity before clearing loading state.
- OpenCode's existing Runner tests cover cancellation followed by replacement work; the retained question is normal completion/replacement status authority.
- Vercel WorkflowAgent's missing sibling tool-result stream during approval pause is already publicly reported.
- Codex is excluded because existing Fieldwork initiatives already own the relevant authority, persistence, replay, MCP, terminal, and cancellation surfaces.

## Current disposition

State: `investigating`

Next work:

1. classify the Vercel Google CI result and expand the polling matrix;
2. decide shared primitive versus bounded provider-family repair through failing controls;
3. materialize the TanStack target-native regression;
4. execute or strengthen the OpenCode status-publication regression;
5. inspect one more distinct high-velocity architecture only if it adds a new authority model.

No external contact or upstream modification was performed.
