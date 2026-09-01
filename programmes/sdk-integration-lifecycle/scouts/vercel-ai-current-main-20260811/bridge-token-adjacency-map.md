## In simple words

Codex is not the only bridge-backed harness that stores a live bearer token in lifecycle state. Claude Code and OpenCode repeat the same basic sequence: strict `bridge.token` schema, live attach using the serialized token, and fresh deterministic minting only on spawn/respawn. ACP also stores the token but layers additional implementation identity, authentication profile, turn-start configuration, and recovery state around the bridge.

This supports testing Codex first. If the Codex repair survives exact execution and independent review, the reusable part is likely a small bridge-token resolver pattern. The lifecycle-state policy still belongs to each adapter/package because their resume payloads and recovery contracts differ.

## Source boundary

Public Vercel AI revision: `7d40fafc394a2c9033f931eb85c895e3817f4b58`  
Fieldwork campaign: #825  
Claim scope: interface  
Evidence class: `source-read`  
Upstream contact authorized: `false`

## Codex

`packages/harness-codex/src/codex-harness.ts`

Baseline pattern:

```text
bridge schema: token required
attach: coords.token
spawn/respawn: mintBridgeToken(sandboxSession.id) or random token
```

Campaign #825 owns the candidate that reconstructs a redacted deterministic token after sandbox resume while preserving strict default/random-token validation at the public package boundary.

## OpenCode

`packages/harness-opencode/src/opencode-harness.ts`

Current source repeats the Codex ownership pattern closely:

```text
openCodeBridgeCoordsSchema.token = z.string()
attach URL token = coords.token
attached session bridgeToken = coords.token
spawn/respawn token = mintBridgeToken(sandboxId) or randomBytes(...)
```

The same reconstruction question is therefore plausible, but OpenCode also carries `openCodeSessionId`, provider/model state, skills, and its own rerun path. No production change is justified until Codex establishes the contract and an OpenCode target-native control proves equivalence.

## Claude Code

`packages/harness-claude-code/src/claude-code-harness.ts`

Current source also uses:

```text
claudeCodeBridgeCoordsSchema.token = z.string()
resume state may carry bridge coordinates
live attach authorizes with the persisted token
spawn-based recovery uses the configured mint callback or random token
```

Claude's stopped-session state can be structurally empty and its recovery relies on SDK `continue: true` plus workdir state. That makes its lifecycle payload different enough that Codex tests cannot be treated as Claude evidence.

## ACP

`packages/harness-acp/src/acp-harness.ts` and `packages/harness-acp/src/v1/acp-v1-harness.ts`

ACP retains the same bearer coordinate fields:

```text
port
token
lastSeenEventId
sandboxId?
```

but its lifecycle state additionally carries implementation identity, authentication profile, ACP session identity, cold-session data, turn-start configuration, recovery mode, restoration method, and skill state. Attach still consumes `coords.token` directly.

A shared runtime resolver may eventually fit, but ACP's validation and process-loss behavior need a separate evidence packet rather than mechanical propagation from Codex.

## Current recommendation

1. Finish exact clean-head execution and independent review for Codex #825.
2. If accepted, extract the smallest reusable resolver only after comparing the final Codex code with Claude Code and OpenCode.
3. Give each additional adapter one native redaction/attach/fallback discriminator before changing its lifecycle schema.
4. Treat ACP as a separate follow-up because its resume contract carries materially more recovery and authentication state.

No cross-adapter implementation is authorized by this map.
