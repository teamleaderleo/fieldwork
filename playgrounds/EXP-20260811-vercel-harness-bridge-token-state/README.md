# Vercel AI SDK bridge-token resume persistence

## State

`COMPLETE — source-read + model-executed; target-native follow-up proposed`

Owner: `chatgpt:gpt-5.6-sol`  
Created: `2026-08-11`  
Claim scope: interface  
Target: `target:vercel-ai`  
Target hub: #2  
Related broad scout: #17 (`ready-for-synthesis`)  
Public upstream contact authorized: `no`

## In simple words

`mintBridgeToken(sandboxId)` was introduced so an application that can derive a bridge authentication token from the sandbox id can reconstruct resume state without storing that secret.

At public main `fc3baaf1ff547efdfcc5cb5a5ee35ed72b8a284c`, live detach and suspended-turn state still carries the bridge token itself. A successful attach reads that persisted token directly and does not call `mintBridgeToken` again. The current bridge-coordinate schema also requires `token` whenever live bridge coordinates are present.

The official Workflow utilities then persist the returned lifecycle state as the durable checkpoint, and their multi-turn example writes `JSON.stringify(resumeState)` to storage. A consumer following that path therefore persists the bridge credential even when deterministic token minting is configured.

Current answer: deterministic minting controls token creation on spawn/respawn, but the supported live attach contract does not yet provide secretless durable resume.

## Bounded question

When a bridge-backed harness is configured with deterministic `mintBridgeToken(sandboxId)`, can callers persist the returned detach or suspend lifecycle state without persisting the live bridge authentication token?

At the pinned revision, **no** for the supported live attach/continue state shape.

## Exact subject

Public repository: https://github.com/vercel/ai  
Pinned public main: `fc3baaf1ff547efdfcc5cb5a5ee35ed72b8a284c`  
Merge: https://github.com/vercel/ai/commit/fc3baaf1ff547efdfcc5cb5a5ee35ed72b8a284c

Primary source paths:

- `packages/harness-claude-code/src/claude-code-harness.ts`;
- `packages/harness-claude-code/src/claude-code-harness.test.ts`;
- `packages/harness-acp/src/acp-harness.test.ts`;
- `packages/harness/src/v1/harness-v1-lifecycle-state.ts`;
- `packages/workflow-harness/src/harness-workflow-state.ts`;
- `packages/workflow-harness/src/run-harness-agent.ts`;
- `content/docs/03-ai-sdk-harnesses/06-workflow-utilities.mdx`.

Retrieval date: `2026-08-11`.

## Why this question appeared

The merge introducing `mintBridgeToken` states that bridge-backed harnesses previously generated a random authentication token that had to be persisted with resume state, and that callers able to deterministically derive the token from sandbox id need a way to reconstruct resume state without storing the secret.

That is a crisp persistence invariant to test:

```text
custom deterministic minting configured
        ↓
detach / suspend returns lifecycle state
        ↓
durable JSON persistence
        ↓
fresh process resumes / continues

wanted property: durable state can omit the bridge credential
```

## Source map

### Lifecycle state contract

`HarnessV1ResumeSessionState.data` and `HarnessV1ContinueTurnState.data` are adapter-defined JSON values intended to survive persistence.

For Claude Code, live bridge coordinates are currently:

```text
bridge
├── port
├── token              ← required
├── lastSeenEventId
└── sandboxId? 
```

### Spawn and respawn

When a bridge must be spawned, the adapter chooses:

```text
random token                        when mintBridgeToken is absent
mintBridgeToken(sandboxSession.id)  when it is present
```

The selected token becomes `BRIDGE_CHANNEL_TOKEN` and is used in the bridge WebSocket URL.

### Detach and suspend

Both `doDetach()` and `doSuspendTurn()` put `bridgeToken` into lifecycle state as `data.bridge.token` along with the port, event cursor, and sandbox id.

### Attach

When resume/continue state has live bridge coordinates, `doStart()` builds the attach URL from `coords.token`. Successful attach returns without invoking `mintBridgeToken`.

The merged Claude Code, ACP, and Codex tests make this behavior explicit: the returned detach state is expected to contain the custom token, and a subsequent attach is expected to leave the mint-call count at one.

### Durable Workflow path

`HarnessWorkflowState` is documented as the serializable state machine returned between Workflow steps, with the Workflow DevKit persisting that return value as the durable checkpoint.

`runHarnessAgent()` returns `continueFrom` after a time slice and calls `session.detach()` after a finished user turn to obtain `resumeFrom` for the next turn.

The Workflow documentation tells multi-turn consumers to persist opaque `resumeFrom` state by session id. Its storage example writes the whole state through `JSON.stringify(resumeState)`.

This connects the adapter behavior directly to an official durable-storage path without requiring an illustrative production architecture.

## Competing explanations

### H1 — the secretless-persistence goal is incomplete for live attach

Prediction: custom minting still leaves `token` in returned state; successful attach consumes that serialized value; removing it breaks the supported coordinate shape.

**Supported by source, merged tests, and the retained model.**

### H2 — callers are expected to scrub the token and let the harness reconstruct it

Prediction: bridge coordinates remain valid without `token`, or `doStart()` re-mints when it is absent.

**Weakened.** The current coordinate schema requires `token`, the successful attach path reads `coords.token`, and the merged tests expect the mint function not to run again on attach. No public reconstruction helper was found in the reviewed paths.

### H3 — deterministic minting is only intended for dead-bridge respawn

That use exists: a respawn calls the mint function again. It does not satisfy the merge's stated live-resume storage motivation, because live `detach()` / `suspendTurn()` state still retains the bridge secret and the attach examples persist that state.

## Executable discriminator

Run:

```sh
python3 playgrounds/EXP-20260811-vercel-harness-bridge-token-state/run.py
```

Retained execution environment:

- Python `3.13.5`;
- Linux `6.18.35` x86_64;
- zero dependencies;
- network disabled;
- synthetic HMAC secret only.

Observed:

```json
{
  "attach_reused_serialized_token": true,
  "mint_calls_after_spawn_and_attach": 1,
  "scrubbed_resume_state_validation": "rejected: missing required bridge coordinate field(s): token",
  "token_present_in_serialized_resume_state": true
}
```

The model is deliberately small and follows the exact disputed branches. It establishes the discriminator as `model-executed`; the source and merged tests remain the evidence for target behavior until a Fieldwork-owned fork runs target-native tests.

## Change thesis

Current behavior:

```text
mintBridgeToken configured
        ↓
spawn uses derived token
        ↓
detach/suspend serializes token
        ↓
workflow/storage persists opaque lifecycle state
        ↓
attach reuses serialized token
```

Concrete consequence: the official durable resume path still places the bridge authentication token in persisted lifecycle state even when the caller configured deterministic derivation specifically to avoid storing that secret.

Candidate direction:

```text
custom deterministic mint configured
        ↓
detach/suspend persist port + cursor + sandbox identity
        ↓
attach derives token from the resumed sandbox identity
        ↓
random-token default keeps its existing persisted-token behavior
```

A production change should derive from the **current resumed sandbox session id**, treating persisted sandbox identity as a consistency check rather than authority supplied by stored state.

## Candidate tests

A bounded target-native campaign should distinguish at least these cases:

1. custom deterministic mint + `detach()` returns live bridge coordinates without the token;
2. JSON round-trip of that state passes lifecycle validation;
3. a fresh harness instance re-mints from the resumed sandbox id and attaches without respawning;
4. `suspendTurn()` / continue follows the same secretless path;
5. default random-token mode preserves current state and attach semantics;
6. sandbox-id mismatch is rejected or otherwise cannot redirect token derivation;
7. mint failure follows the existing start-failure cleanup path;
8. documentation states the determinism/stability requirement across a live bridge lifetime.

If changing the state contract is undesirable, the smaller alternative is to narrow the option's documented promise so callers understand that live attach state still contains the credential. That would resolve the contract mismatch while leaving the original storage goal unmet.

## Negative results and dead ends

- The issue is not that custom minting is ignored on spawn; it is used there.
- The issue is not that attach generates a different token; the current tests deliberately preserve the existing token.
- The ordinary `doStop()` snapshot-resume path can return data without live bridge coordinates. That path has no live bridge credential to reattach to and does not answer the detach/suspend persistence question.
- No claim is made that a storage system exposes the persisted token to an attacker. The established consequence is narrower: the credential remains present in the documented durable state.

## Evidence classes

| Claim | Evidence class | Limit |
| --- | --- | --- |
| the feature motivation names avoiding persisted bridge secrets | `source-read` | merge text at pinned revision |
| live coordinates require and serialize `token` | `source-read` | Claude Code adapter path reviewed directly |
| attach reuses persisted token and skips re-minting | `source-read` | implementation plus merged tests |
| official workflow state is durably persisted and documented example JSON-serializes `resumeFrom` | `source-read` | official package source and docs |
| source-derived discriminator reproduces the lifecycle distinction | `model-executed` | no target package/runtime |
| a proposed secretless state change works in real sandbox attach/continue | `target-test-prepared: no` | follow-up required |

## Recommendation

Retain this as a finding and promote a bounded campaign if implementation capacity is available.

The next question is narrow:

> Can bridge-backed harnesses omit `token` from live resume/continue state when a deterministic mint function is configured, then rederive from the resumed sandbox identity while preserving random-token compatibility and attach/replay behavior?

This is separate from the completed #17 streaming/tool-lifecycle scout and from the current Vercel AI target hub implementation families. It arose from new public main after the hub's previous refresh.

## Boundaries

- Public upstream remained read-only throughout this investigation.
- No issue, pull request, comment, review, reaction, branch, or file was created or changed in `vercel/ai`.
- No credentials, production data, or paid provider calls were used.
- The retained probe is source-derived model evidence; target-native execution remains the next gate.
