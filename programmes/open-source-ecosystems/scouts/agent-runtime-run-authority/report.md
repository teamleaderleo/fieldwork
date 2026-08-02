# Authoritative run state across agent runtimes

## In simple words

Agent systems often have several copies of “what is happening now”: an active model stream, a session status flag, persisted run data, a replay stream, and UI state. This scout is testing whether an older asynchronous path can publish state after newer work has become authoritative.

Three source-level candidates currently survive reduction. OpenCode can publish `idle` from an older completion while a replacement run is active. TanStack AI can persist an intermediate transformed generation result that differs from the final live result. Vercel AI can adopt a previous assistant message when resuming a different run; that case is already publicly reported and is retained as comparison rather than novel work.

The dependency-free probes demonstrate ordering properties, not target-package execution. A focused OpenCode test carrier has also been prepared in the owned fork, but no workflow check registered, so it remains `target-test-prepared`, not `target-executed`.

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
| OpenCode | `1882c33827cf0ce5c948b69ab5a87ed8f6790cf8` | `packages/opencode/src/effect/runner.ts`, `packages/opencode/src/session/run-state.ts`, `packages/opencode/src/session/status.ts`, `packages/opencode/src/session/prompt.ts`, `packages/opencode/test/effect/runner.test.ts` |
| TanStack AI | `6feb5644a38073c5865f7b4ff4d64d62195e755b` | `packages/ai/src/activities/middleware/run.ts`, `packages/ai/src/activities/generateImage/index.ts`, `packages/ai-persistence/src/middleware.ts`, `packages/ai-client/src/generation-client.ts` |
| Vercel AI SDK | `3bc0d4f40df7a77af4b181bc97dc1c54843545ab` | `packages/ai/src/ui/chat.ts`, `packages/ai/src/ui/process-ui-message-stream.ts` |

## Candidate 1 — OpenCode stale idle publication after replacement work

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

The carrier uses the target's actual `Runner` and reproduces the SessionRunState ordering with a controllable status-publication barrier. A branch-scoped workflow was added, but no check or workflow run registered. Evidence class remains `target-test-prepared`.

### Prior-art state

A current public issue reports server status lag after a prompt response completes. A closed unmerged draft previously grouped concurrent prompt races with stale busy cleanup. Neither inspected artifact demonstrates this exact replacement ordering on the current `Runner`/`SessionRunState` architecture. The candidate is therefore not yet novel enough for contact, but it remains independently testable.

### Next discriminating test

Execute the prepared test in an authorized fork runner or local checkout. A stronger integration version should inject a controllable EventV2Bridge publication barrier into the real SessionRunState/SessionStatus layers.

### Likely repair boundary

Fence idle publication by the runner generation that still owns the session. A completion may remove or mark idle only if no replacement registration/run has taken authority. Do not fix this with a time delay or client-side status heuristic.

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

Use the target's generation middleware test harness:

1. Register persistence first.
2. Register a custom middleware second that appends a visible result transform.
3. Generate a synthetic result.
4. Assert the returned result and reconstructed persisted result are identical.

The test should cover both metadata-only persistence and artifact persistence.

### Likely repair boundary

Durable result capture needs a post-transform/final-result boundary. It should not be implemented as an ordinary transform whose observation depends on middleware registration order. Artifact rewriting may remain a transform; recording the authoritative final result should occur after all transforms complete.

## Candidate 3 — Vercel AI resume adopts the wrong assistant message

### Current behavior

The chat client seeds resumed stream state from the current last message whenever its role is `assistant`. The resumed stream's actual `messageId` arrives later in a `start` chunk, which renames the adopted message without checking identity. New resumed parts are then appended to the previous turn's parts.

### Consequence

A client that reconnects to a run started elsewhere can duplicate the prior assistant answer and attach it to the resumed run ID. The old answer remains in history, so UI and persisted history can contain the same content twice under different identities.

### Model receipt

Run:

```sh
node artifacts/vercel-resume-adoption-model.mjs
```

The model produces two messages containing `first answer`; the resumed message contains both the previous answer and `RESUMED-TEXT`.

Evidence class: `model-executed` plus `source-read`.

### Duplicate state

This behavior is already described in a current public issue and remains present at the pinned revision. No open repair was found in the first PR search. Retain it as a comparison architecture and possible independent validation, not as a novel Fieldwork contribution unit.

### Likely repair boundary

Resume adoption must be identity-aware. Because the authoritative ID arrives in the stream, the implementation must either defer adoption until `start`, or preserve a pristine baseline and discard adopted parts when the IDs differ. Same-message partial resume and part-level deduplication remain separate requirements.

## Ranking

1. **TanStack AI final-result persistence boundary** — highest novelty and architectural leverage; small deterministic target-native test; likely reusable invariant across all generation activities.
2. **OpenCode replacement-run status authority** — high operational consequence and strong source mechanism; related public reports exist, so exact current-head execution and prior-art distinction are mandatory.
3. **Vercel AI resume identity** — high consequence but known publicly; useful as validation/comparison unless active repair emerges.

## Negative results and stopped branches

- TanStack AI mount hydration does not blindly overwrite a live generation at the pinned revision; ownership is re-checked after the asynchronous request.
- TanStack AI rejoin cleanup does not blindly clear loading state after a replacement run; controller identity is checked.
- OpenCode's existing Runner tests already cover cancellation followed by replacement work. The retained question is stale status publication across normal completion/replacement, not the tested cancellation deadlock.
- Vercel AI WorkflowAgent's missing sibling tool-result stream on approval pause is already publicly reported; no duplicate Fieldwork implementation is justified from this scout.

## Current disposition

State: `investigating`

Next work:

1. target-native regression for TanStack transform/persistence ordering;
2. execute or strengthen the OpenCode controlled status-publication regression;
3. broader duplicate and current-PR checks;
4. inspect one materially different authority architecture before stopping, likely Codex durable event/turn state or a sandbox run store.

No external contact or upstream modification was performed.
