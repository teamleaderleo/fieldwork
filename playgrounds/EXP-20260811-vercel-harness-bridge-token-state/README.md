# Vercel AI SDK bridge-token resume persistence

## State

`PROMOTED — source-read + model-executed; target-native carrier #49 queued; campaign #788`

Owner: `chatgpt:gpt-5.6-sol`  
Created: `2026-08-11`  
Claim scope: interface  
Target: `target:vercel-ai`  
Target hub: #2  
Related broad scout: #17 (`ready-for-synthesis`)  
Promoted campaign: #788  
Owned execution carrier: `teamleaderleo/ai#49`  
Public upstream contact authorized: `no`

## In simple words

`mintBridgeToken(sandboxId)` was introduced so applications that can derive a bridge authentication token from sandbox identity have a path toward reconstructing resume state without storing that secret.

At public main `fc3baaf1ff547efdfcc5cb5a5ee35ed72b8a284c`, live detach and suspended-turn state still carries the bridge token itself. A successful attach reads that persisted token directly and does not call `mintBridgeToken` again. The bridge-coordinate schemas require `token` whenever live coordinates are present.

The official Workflow utilities persist returned lifecycle state as a durable checkpoint, and their multi-turn example writes `JSON.stringify(resumeState)` to storage. The documented path therefore persists the live bridge credential even when a caller uses deterministic token derivation.

A second pass found an important compatibility constraint: the public `mintBridgeToken` hook accepts any synchronous `(sandboxId) => string` function. Adapter documentation requires a suitably secret result but does not require it to be deterministic or stable across processes. Existing callers may therefore use a rotating custom mint function and depend on the current persisted-token attach behavior. A repair cannot safely equate “custom mint hook exists” with “token may be omitted.”

Current answer: secretless live resume is absent from the public lifecycle contract. A compatibility-preserving implementation needs an explicit rederive/secretless mode, or another contract that distinguishes stable derivation from ordinary custom minting.

## Bounded question

When a bridge-backed harness is configured with deterministic `mintBridgeToken(sandboxId)`, can callers persist returned detach or suspend lifecycle state without persisting the live bridge authentication token?

At the pinned revision, **no** for the supported live attach/continue state shape.

## Exact subject

Public repository: https://github.com/vercel/ai  
Pinned public main: `fc3baaf1ff547efdfcc5cb5a5ee35ed72b8a284c`  
Merge: https://github.com/vercel/ai/commit/fc3baaf1ff547efdfcc5cb5a5ee35ed72b8a284c

Primary source paths:

- `packages/harness-claude-code/src/claude-code-harness.ts`;
- `packages/harness-claude-code/src/claude-code-harness.test.ts`;
- `packages/harness-codex/src/codex-harness.ts`;
- `packages/harness-acp/src/acp-harness.ts`;
- `packages/harness-acp/src/acp-harness.test.ts`;
- `packages/harness-acp/src/v1/acp-v1-harness.ts`;
- `packages/harness-acp/src/v1/acp-v1-lifecycle.ts`;
- `packages/harness-acp/src/v1/acp-v1-lifecycle.test.ts`;
- `packages/harness/src/v1/harness-v1-lifecycle-state.ts`;
- `packages/workflow-harness/src/harness-workflow-state.ts`;
- `packages/workflow-harness/src/run-harness-agent.ts`;
- `packages/sandbox-vercel/src/vercel-sandbox.ts`;
- `content/docs/03-ai-sdk-harnesses/06-workflow-utilities.mdx`.

Retrieval date: `2026-08-11`.

## Why this question appeared

The merge introducing `mintBridgeToken` states that bridge-backed harnesses previously generated a random authentication token that had to be persisted with resume state, and that callers able to deterministically derive the token from sandbox id need a way to reconstruct resume state without storing the secret.

That gives a persistence invariant to test:

```text
stable deterministic derivation selected
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

For Claude Code and Codex, live bridge coordinates currently include:

```text
bridge
├── port
├── token              ← required
├── lastSeenEventId
└── sandboxId?
```

ACP has the same required token coordinate plus additional lifecycle compatibility data.

### Spawn and respawn

When a bridge must be spawned, adapters choose:

```text
random token                        when mintBridgeToken is absent
mintBridgeToken(sandboxSession.id)  when it is present
```

The selected token becomes `BRIDGE_CHANNEL_TOKEN` and is used in the bridge WebSocket URL.

### Detach and suspend

Bridge-backed adapters put `bridgeToken` into lifecycle state as `data.bridge.token` alongside the port, event cursor, and sandbox id.

### Attach

When resume/continue state has live bridge coordinates, attach builds the WebSocket URL from `coords.token`. Successful attach returns without invoking `mintBridgeToken`.

Merged Claude Code, ACP, and Codex tests make this behavior explicit: returned detach state is expected to contain the custom token, and subsequent attach is expected to leave the mint-call count at one.

### Durable Workflow path

`HarnessWorkflowState` is documented as the serializable state machine returned between Workflow steps, with Workflow persisting that value as the durable checkpoint.

`runHarnessAgent()` returns `continueFrom` after a time slice and calls `session.detach()` after a finished user turn to obtain `resumeFrom` for the next turn.

The Workflow documentation tells multi-turn consumers to persist opaque `resumeFrom` state by session id. Its storage example writes the whole state through `JSON.stringify(resumeState)`.

This connects adapter behavior directly to an official durable-storage path without relying on an illustrative production architecture.

### Sandbox identity authority

The Vercel sandbox provider derives the sandbox selected for resume from the caller-supplied harness `sessionId`: `resumeSession({ sessionId })` looks up the per-session sandbox name. The resumed `sandboxSession.id` is therefore the live sandbox identity available to the adapter.

ACP compares persisted `bridge.sandboxId` with the current sandbox id and has a focused test requiring a mismatch to fail before attach. Claude Code and Codex persist `sandboxId` but the reviewed attach paths do not perform the same explicit check.

This makes sandbox-identity validation a repair dependency for any rederived-token path and an independently useful lifecycle invariant.

## Competing explanations

### H1 — the secretless-persistence goal is incomplete for live attach

Prediction: custom minting still leaves `token` in returned state; successful attach consumes that serialized value; removing it breaks the supported coordinate shape.

**Supported by source, merged tests, and the retained model.**

### H2 — callers are expected to scrub the token and let the harness reconstruct it

Prediction: bridge coordinates remain valid without `token`, or `doStart()` re-mints when it is absent.

**Weakened.** Current coordinate schemas require `token`, attach reads `coords.token`, and merged tests expect the mint function not to run again on attach. No public reconstruction helper was found in the reviewed paths.

### H3 — deterministic minting is only useful for dead-bridge respawn

That use exists: a respawn calls the mint function again. It does not satisfy the merge's stated live-resume storage motivation, because live detach/suspend state still retains the bridge secret and official workflow paths persist that state.

### H4 — presence of `mintBridgeToken` is enough to select secretless semantics

**Rejected as a compatibility rule.** The hook's public type and docs allow a custom secret token function without promising determinism. A rotating function works with the current persisted-token attach contract. Re-minting automatically for every custom hook would change valid behavior.

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

The model follows the exact disputed branches. It establishes the discriminator as `model-executed`; target behavior is controlled by source and target-native execution.

## Target-native carrier

Owned fork branch: `fieldwork/788-bridge-token-resume-state-tests`  
Owned PR: `teamleaderleo/ai#49`  
Exact base: `fc3baaf1ff547efdfcc5cb5a5ee35ed72b8a284c`

The first carrier intentionally encodes the direct interpretation “custom mint hook implies secretless state” as three Claude Code assertions:

1. detach omits the credential;
2. secretless attach re-mints from current sandbox identity;
3. mismatched persisted sandbox identity is rejected.

After source review rejected assertion 1/2 as a safe default for arbitrary custom mint functions, this carrier remains useful as a characterization of current behavior and identity mismatch. Its semantic repair premise is superseded by the explicit-opt-in design below. Preserve its execution result rather than silently rewriting the historical probe.

## Change thesis

Current behavior:

```text
mintBridgeToken configured
        ↓
spawn uses caller token
        ↓
detach/suspend serializes token
        ↓
workflow/storage persists opaque lifecycle state
        ↓
attach reuses serialized token
```

Concrete consequence: the documented durable resume path carries the bridge authentication token in persisted lifecycle state, so callers with stable deterministic derivation have no supported way to realize the merge's stated secretless-resume motivation.

Selected compatibility direction:

```text
existing default / custom mint
        ↓
persist token exactly as today

explicit stable-rederive mode + mint function
        ↓
detach/suspend persist port + cursor + sandbox identity, omit token
        ↓
resume validates persisted sandbox identity against current sandbox
        ↓
attach rederives token from current sandboxSession.id
```

The exact public API name is still a design question. The important compatibility property is explicit opt-in: existing `mintBridgeToken` callers retain current semantics unless they declare stable rederivation.

A production change should derive from the **current resumed sandbox session id**, with persisted sandbox identity used as a consistency check rather than credential authority supplied by stored state.

## Candidate tests

A bounded target-native campaign should distinguish at least these cases:

1. current default random-token mode preserves token persistence and attach semantics;
2. current custom `mintBridgeToken` mode also preserves persisted-token semantics unless the new secretless mode is selected;
3. secretless/rederive mode requires a mint function;
4. secretless mode + `detach()` returns live coordinates without `token`;
5. JSON round-trip of secretless state passes lifecycle validation;
6. a fresh harness instance re-mints from the current resumed sandbox id and attaches without respawning;
7. `suspendTurn()` / continue supports the same secretless path;
8. rotating custom mint without secretless mode continues to attach using the persisted live token;
9. sandbox-id mismatch is rejected before attach;
10. mint failure follows existing start-failure cleanup;
11. attach failure still falls through to the adapter's existing replay/rerun recovery behavior;
12. docs state the stability requirement and persistence tradeoff of the explicit mode.

If adding a second contract switch is undesirable, the smaller alternative is to narrow the option's documented promise so callers understand that live attach state still contains the credential. That resolves the expectation mismatch while leaving the original storage goal unmet.

## Negative results and dead ends

- Custom minting is used correctly on spawn; the finding concerns durable live attach state.
- Attach intentionally reuses the persisted token at the pinned revision.
- `doStop()` snapshot-resume can return data without live bridge coordinates; that path has no live bridge credential to reattach to and does not answer detach/suspend persistence.
- Hook presence alone cannot safely select rederive semantics because the hook does not encode determinism.
- No claim is made that a storage system exposes the persisted token to an attacker. The established consequence is narrower: the credential remains present in documented durable state.
- No claim is yet made that Claude/Codex sandbox-id mismatch causes cross-user exposure. The source-level invariant is narrower: ACP rejects the mismatch before attach while the reviewed Claude/Codex paths lack the same explicit validation.

## Evidence classes

| Claim | Evidence class | Limit |
| --- | --- | --- |
| feature motivation names avoiding persisted bridge secrets | `source-read` | merge text at pinned revision |
| live coordinates require and serialize `token` | `source-read` | reviewed bridge adapter paths |
| attach reuses persisted token and skips re-minting | `source-read` | implementation plus merged tests |
| official workflow state is durably persisted and documented example JSON-serializes `resumeFrom` | `source-read` | official package source and docs |
| custom mint API does not require deterministic output | `source-read` | public type and adapter docs |
| ACP rejects sandbox-id mismatch before attach | `source-read` | implementation plus focused lifecycle test |
| source-derived discriminator reproduces persistence distinction | `model-executed` | no target package/runtime |
| Claude target-native characterization | `target-test-prepared` | carrier #49 queued at this revision |
| explicit secretless mode works in real attach/continue | `target-test-prepared: no` | implementation follow-up required |

## Recommendation

Keep campaign #788 open, but use the revised bounded question:

> Can bridge-backed harnesses add an explicit stable-rederive mode that omits the live token from persisted resume/continue state, derives it from the currently resumed sandbox identity, preserves every existing random/custom-mint caller by default, and enforces sandbox identity consistently across adapters?

Treat Claude/Codex sandbox-identity parity as a required discriminator within the campaign. Split it into an independent finding or campaign only if target-native evidence shows a consequence that stands apart from secretless resume.

This work is separate from the completed #17 streaming/tool-lifecycle scout and arose from new public main after the target hub's previous refresh.

## Boundaries

- Public upstream remained read-only throughout this investigation.
- No issue, pull request, comment, review, reaction, branch, or file was created or changed in `vercel/ai`.
- No credentials, production data, or paid provider calls were used.
- The retained model is source-derived evidence; owned-fork target execution remains the next gate.
