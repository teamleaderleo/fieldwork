## In simple words

The deterministic bridge-token finding does not need a generic lifecycle hydration hook to become usable. The narrower boundary is already available inside each bridge-backed adapter: after the framework resumes the sandbox, `doStart()` has the authoritative `sandboxSession.id`, the adapter settings contain `mintBridgeToken`, and the attach path is about to consume the bridge token.

The strongest direction is therefore an adapter-side derived-secret resolver: make the serialized bridge token optional only when the adapter can reconstruct it, derive the missing token from the resumed sandbox id immediately before live attach, and preserve a hard error when neither persisted token nor deterministic minting exists. This keeps the generic `HarnessAgent` validation/ownership model intact while removing the caller's need to edit adapter-private lifecycle state.

This is a design comparison, not a production patch. It narrows the next target-native experiment.

## Exact source reviewed

Public Vercel AI revision: `74556f7946cdf50aa41c01c5d5b3bd2b733acc86`.

Relevant current boundaries:

- `packages/harness/src/agent/harness-agent.ts` validates `resumeFrom` / `continueFrom` before sandbox acquisition;
- `packages/harness-codex/src/codex-harness.ts` requires `bridge.token` in its lifecycle schema, then receives the resumed `sandboxSession.id` inside `doStart()`;
- the Codex attach path uses `coords.token` directly while the spawn/respawn path uses `settings.mintBridgeToken(sandboxId)` when configured;
- ACP carries the same shape: bridge coordinates require a token, `doStart()` has the resumed sandbox session, attach consumes the stored token, and recovery is adapter-owned;
- Claude Code, OpenCode, and DeepAgents expose the same bridge-backed lifecycle family.

The finding remains current on this revision.

## Competing designs

### A — adapter-side derived-secret resolution

Serialized bridge coordinates permit an omitted token. Inside `doStart()`, after sandbox resume and before live attach:

```text
resolved token =
  persisted bridge token
  ?? mintBridgeToken(resumed sandbox id)
  ?? error: live bridge token cannot be reconstructed
```

The resolved token is used for the attach URL and the returned in-memory session. Existing state containing a token keeps its current behavior. Random-token configurations continue to require persisted token material.

A small shared utility may reduce repetition across bridge-backed adapters, but ownership stays adapter-side because only the adapter knows whether a deterministic mint function exists and how attach/recovery should behave.

### B — generic Harness lifecycle hydration hook before validation

Add a `HarnessV1` hook that transforms lifecycle state before `lifecycleStateSchema` validation.

This appears general but sits before the framework resumes the sandbox. The hook therefore lacks the authoritative resumed `sandboxSession.id` unless it trusts an identifier already serialized into lifecycle data. That preserves the caller-state dependency the feature is trying to reduce and introduces a generic transformation stage for an adapter-specific derived credential.

Moving the hook after sandbox acquisition would change a stronger framework invariant: currently invalid lifecycle state is rejected before the sandbox provider is resumed. That would let malformed state trigger sandbox lifecycle work before validation and would widen the failure/cleanup surface for every harness.

### C — public serializer / rehydrator helper

Keep lifecycle schemas strict and provide helper APIs that remove and later restore derived secrets.

This makes the workflow supported, but the application still owns a two-step state transformation and must call the helper before `createSession()`. It also needs adapter-specific knowledge or a new generic serializer contract. It is cleaner than undocumented object surgery, yet it does not remove the awkward ordering that motivated the finding.

### D — documentation-only caller ownership

Document token redaction and reinsertion around storage.

This has the smallest implementation cost but exposes adapter-private lifecycle shape as an application contract and leaves validation failures dependent on callers reconstructing opaque state correctly.

## Comparison criteria

| Criterion | A: adapter resolve | B: generic hook | C: public helper | D: caller edits |
| --- | --- | --- | --- | --- |
| Uses authoritative resumed sandbox id | yes | no before validation | only if caller has it | caller-dependent |
| Keeps invalid-state rejection before sandbox resume | yes for non-secret shape | no if hook moves after resume | yes | yes |
| Removes caller editing of adapter-private state | yes | yes | partial | no |
| Keeps random-token default strict | yes with explicit missing-token error | possible | yes | yes |
| Preserves existing serialized states | yes | yes | yes | yes |
| Generic framework API expansion | none required | yes | likely | none |
| Cross-adapter duplication | small/shared helper possible | low | medium | none in SDK |
| Recovery policy remains with adapter | yes | partially split | yes | yes |

## Selected provisional direction

**A — adapter-side derived-secret resolution**, preferably with a tiny shared bridge-coordinate helper only if source review shows the repeated logic can be factored without hiding adapter recovery differences.

The decisive point is identity ownership. The resumed sandbox session is the live authority for the sandbox id. `doStart()` has that object before attempting attach, so token derivation can use the identity that the actual connection belongs to. A pre-validation generic hook does not.

## Required target-native controls

The next experiment should cover the same lifecycle state through both token modes.

### Deterministic token, redacted persisted state

1. create or construct valid detach state;
2. remove only `bridge.token`;
3. resume the sandbox;
4. derive with `mintBridgeToken(sandboxSession.id)`;
5. assert live attach uses the derived token and preserves the event cursor.

Expected: ordinary live attach succeeds without caller reinsertion.

### Deterministic token, suspended in-flight turn

Remove only the token from `continueFrom` state and verify the attach/replay path keeps `lastSeenEventId`, pending tool/approval state, and turn continuation semantics.

Expected: no new `start` is sent merely because the secret was redacted.

### Bridge-dead fallback

Use deterministic minting with redacted coordinates, make live attach fail, then exercise the existing disk-replay / rerun fallback.

Expected: deriving the token changes only authentication material; recovery selection remains identical to the persisted-token case.

### Existing persisted token

Provide a token together with deterministic minting.

Expected: persisted token wins for backward compatibility and the mint callback is not consulted during live attach, matching current behavior.

### Random-token default, redacted state

Remove the token with no `mintBridgeToken` setting.

Expected: fail explicitly before attempting an unauthenticated attach and before silently changing recovery semantics. Redaction is supported only for reconstructible secrets.

### Resumed sandbox identity wins

Provide stale or absent serialized `bridge.sandboxId` while the resumed sandbox exposes its actual id.

Expected: deterministic derivation uses the resumed sandbox session id. Serialized sandbox id remains diagnostic/recovery metadata rather than credential authority.

## Repair boundary

A production candidate should stay out of `HarnessAgent` unless target-native implementation demonstrates that adapter-side resolution cannot preserve one of the controls above.

Likely minimal changes per bridge-backed adapter:

1. permit `bridge.token` to be absent in the adapter lifecycle schema;
2. resolve a live attach token after sandbox resume;
3. make absence fail clearly when deterministic reconstruction is unavailable;
4. keep serialized-token precedence for compatibility;
5. use only the resolved in-memory token for attach/session construction;
6. add detach, suspend, bridge-dead, and random-token controls.

If the same resolver is byte-for-byte identical across Codex, Claude Code, OpenCode, DeepAgents, and ACP, factor that small resolver. Do not move lifecycle validation or recovery ownership into a generic hook merely to eliminate repeated lines.

## Reversing evidence

Reopen the generic-hook direction if a bridge-backed adapter must derive lifecycle fields that cannot be reconstructed inside `doStart()` after sandbox resume, or if a supported generic lifecycle serialization contract already exists and can perform secret derivation without trusting serialized sandbox identity or delaying validation.

Downgrade adapter-side resolution if target-native controls show that accepting a missing token necessarily makes random-token state ambiguously fall through to replay/rerun rather than failing explicitly.

## Evidence class and disposition

Evidence class: `source-read` design comparison on public revision `74556f7946cdf50aa41c01c5d5b3bd2b733acc86`, building on #805's existing `target-executed` characterization of the current validation behavior.

Disposition: **SELECT A FOR TARGET-NATIVE COMPARISON; NO PRODUCTION PATCH YET**.

Upstream contact authorization remains `false`.
