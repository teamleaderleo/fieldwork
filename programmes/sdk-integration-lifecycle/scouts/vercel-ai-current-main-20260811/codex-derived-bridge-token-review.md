## In simple words

The first Codex adapter prototype proved that a missing deterministic bridge token can be reconstructed from the resumed sandbox identity without losing the live-attach cursor or respawn fallback. It passed the complete `@ai-sdk/harness-codex` Node suite.

Builder review then found a narrower invalid-state regression: making `bridge.token` optional for every Codex harness lets malformed random-token resume state pass framework validation and reach sandbox resume before the adapter rejects it. The repaired candidate keeps optional-token acceptance only on the public deterministic-mint harness while the default public `createCodex()` keeps strict pre-resume validation.

Current answer: the adapter-owned reconstruction direction remains viable, but the repaired clean source must receive an exact package type-check/test receipt before promotion.

## Scope

Fieldwork campaign: #825  
Source finding: #805  
Owned source: `teamleaderleo/ai#90`  
Canonical source branch: `candidate/codex-derived-bridge-token-current`  
Current source head at this receipt: `f42bee41c3f56eea02329b5e3da8144136c708bd`  
Review base/current public main: `7d40fafc394a2c9033f931eb85c895e3817f4b58`  
Original implementation ancestor: `74556f7946cdf50aa41c01c5d5b3bd2b733acc86`  
Claim scope: interface  
Automated upstream contact: prohibited

The public head is three commits ahead of the implementation ancestor. That delta does not touch `packages/harness-codex`; PR #90 is retargeted to an owned evidence branch at the exact public head so the current-base relation is explicit.

## Current source fence

1. `.changeset/calm-codex-bridge-resume.md`;
2. `packages/harness-codex/src/codex-harness.ts`;
3. `packages/harness-codex/src/index.ts`;
4. `packages/harness-codex/src/codex-harness-derived-bridge-token.test.ts`.

No temporary workflow or Fieldwork-only test is part of the source branch.

## Runtime ownership model

The package-private adapter accepts live coordinates whose token is optional. It resolves one operation-local token as:

```text
persisted bridge token
?? deterministic mint from resumed sandboxSession.id
?? explicit missing-token failure
```

The derived token is memoized for one `doStart()` attempt. If live attach fails and recovery respawns the bridge, the same derived value becomes `BRIDGE_CHANNEL_TOKEN` instead of invoking the mint callback again.

The serialized `sandboxId` is not an authority input for derivation. The resumed sandbox handle supplies the id.

## Public validation boundary

The implementation schema is intentionally permissive enough to represent deterministic redaction. The package export wraps only the default random-token harness with a stricter validation refinement.

```text
createCodex({ mintBridgeToken })
    -> optional live token is valid
    -> sandbox resumes
    -> adapter derives from resumed sandbox id

createCodex()
    -> missing live token rejected by lifecycle validation
    -> sandbox resume is not called
```

The wrapper return type is explicitly pinned to `ReturnType<typeof createCodexImplementation>` so the refined Zod schema does not widen or alter the public harness type.

## Required controls

The clean package regression file covers:

1. deterministic redacted resume through public `HarnessAgent.createSession()` reaches live attach;
2. derivation uses `resumed-sandbox` rather than stale serialized `sandboxId`;
3. random-token redaction is rejected before `resumeSession()`;
4. suspended-turn redaction retains `lastSeenEventId` and sends `open({ resume: true })`;
5. direct random-token redaction fails before attach/recovery drift;
6. failed live attach plus respawn reuses one derived token.

Existing `codex-harness.test.ts` remains the persisted-token precedence control: a stored token is reused on attach and deterministic minting is not invoked again.

## Executed prototype

First runtime prototype source: `3bacd44a987bd5cba6948a9a4aed96651d6719d3`.

Carrier: `teamleaderleo/ai#83`  
Run/job: `31443103518` / `93631688980`

```text
harness-codex type-check   PASS
harness-codex Node         11 files / 89 tests PASS
final source fence         PASS
```

That receipt establishes adapter-side derivation, cursor preservation, explicit random-token failure inside `doStart()`, and fallback reuse. It does **not** accept the final source because the stronger public pre-resume random-token control was added afterward.

## Self-review repair

Blocking finding on the first green generation:

```text
unconditionally optional token schema
    -> malformed random-token state validates
    -> HarnessAgent resumes sandbox
    -> adapter rejects later
    -> start-failure cleanup may act on the resumed sandbox
```

Repair selected:

- keep package-private optional-token representation for the adapter;
- expose deterministic harnesses unchanged through the public wrapper;
- refine the public default/random-token lifecycle schema so missing `bridge.token` remains invalid before sandbox acquisition;
- add an exact `HarnessAgent` negative control for `resumeSession()` remaining untouched.

A generic HarnessAgent hydration hook remains rejected for this first candidate because it would widen framework scope and still lacks the authoritative resumed sandbox identity at pre-validation time.

## Compatibility and overlap

Current public commits after the implementation ancestor do not touch the candidate subsystem.

Current upstream issue/PR searches for `mintBridgeToken`, bridge-token resume, and redaction found no active equivalent repair.

The candidate changes no random-token generation, normal persisted-token attach, thread identity, cursor serialization, replay classification, or caller-facing tool behavior.

## Evidence status

- current defect and caller-owned rehydration requirement: `target-executed` via #805;
- adapter-side derived-token mechanism: `target-executed` on the first prototype;
- public random-token pre-resume repair: `target-test-prepared` on clean source #90;
- final clean source package compatibility: pending exact execution.

## Disposition

Disposition: `EXECUTE`

Clearing condition:

1. the renewed `@ai-sdk/harness-codex` type-check and complete Node suite must run against exact source head `f42bee41c3f56eea02329b5e3da8144136c708bd` or a later explicitly reviewed generation;
2. all six new controls and the existing persisted-token precedence control must pass;
3. the final working-tree/source fence must be clean;
4. complete-diff self-review must be refreshed on that exact head;
5. only then may #825 be admitted for independent final review.

Any source-head movement expires the execution disposition until the receipt identifies the new exact source.
