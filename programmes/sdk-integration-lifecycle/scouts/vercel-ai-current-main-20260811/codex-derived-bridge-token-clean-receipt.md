## In simple words

The Codex deterministic bridge-token repair now has one clean current-main source commit and an exact target-native receipt.

Deterministic `mintBridgeToken(sandboxId)` sessions may resume from lifecycle state whose live bridge bearer token was redacted. The public package accepts that state only when deterministic minting is configured, then the adapter reconstructs the token from the authoritative resumed sandbox id. Default random-token sessions keep the previous strict validation boundary and reject a missing live token before sandbox resume.

The clean source passed `@ai-sdk/harness-codex` type-check and all 90 Node tests, including the five new lifecycle controls and the existing persisted-token precedence control. The builder found no further blocking issue in the complete four-file diff. Independent final review is still required.

## Exact source

Fieldwork campaign: #825  
Owned source PR: `teamleaderleo/ai#90`  
Canonical branch: `candidate/codex-derived-bridge-token-current`  
Exact source head: `eb738bafe9e5f33ea48b31c600048f072c2b785d`  
Exact public base/current main: `7d40fafc394a2c9033f931eb85c895e3817f4b58`  
Relation: one candidate commit directly on the exact public base  
Claim scope: interface  
Automated upstream contact: prohibited

## Complete source fence

1. `.changeset/calm-codex-bridge-resume.md`;
2. `packages/harness-codex/src/codex-harness.ts`;
3. `packages/harness-codex/src/index.ts`;
4. `packages/harness-codex/src/codex-harness-derived-bridge-token.test.ts`.

No temporary workflow, Fieldwork-only test, or exploratory artifact is present on the canonical source head.

## Runtime contract

The package-private adapter accepts live coordinates whose token can be absent. For one `doStart()` attempt it resolves:

```text
persisted bridge token
?? mintBridgeToken(resumed sandboxSession.id)
?? explicit missing-token failure
```

A derived token is memoized for that start attempt. If live attach fails, respawn recovery uses the same value rather than minting a second token.

The serialized `sandboxId` is retained as lifecycle metadata but is not trusted for token derivation. The resumed sandbox handle supplies the authoritative id.

## Public validation contract

`packages/harness-codex/src/index.ts` keeps the settings-dependent validation rule at the public package boundary:

```text
createCodex({ mintBridgeToken })
  -> redacted bridge.token is accepted by lifecycle validation
  -> sandbox resumes
  -> adapter reconstructs token from resumed sandbox id

createCodex()
  -> missing bridge.token is rejected by lifecycle validation
  -> sandbox resume is not called
```

The wrapper return type is explicitly `ReturnType<typeof createCodexImplementation>` so the Zod refinement remains an internal validation detail and does not alter the exported harness type.

## Exact execution

Execution carrier: `teamleaderleo/ai#83`  
Workflow run: `31443103518`  
Exact clean-head job: `93774654614`  
Runner: Ubuntu 24.04  
Node: `22.23.1`

The job log explicitly records:

```text
checkout ref: candidate/codex-derived-bridge-token-current
source head: eb738bafe9e5f33ea48b31c600048f072c2b785d
adapter prototype already materialized
final source head: eb738bafe9e5f33ea48b31c600048f072c2b785d
```

Validation:

```text
@ai-sdk/harness-codex type-check            PASS
Node test files                             11 / 11 PASS
Node tests                                  90 / 90 PASS
new bridge-token regression file             5 / 5 PASS
existing codex-harness tests                11 / 11 PASS
final exact-head / git diff fence           PASS
clean working tree                           PASS
```

Evidence class: `target-executed` for the clean Codex package behavior and public lifecycle boundary.

## Controls established

1. deterministic redacted resume through public `HarnessAgent.createSession()` reaches live attach;
2. derivation uses the resumed sandbox id rather than stale serialized sandbox metadata;
3. redacted default/random-token state fails before `resumeSession()`;
4. suspended-turn state preserves `lastSeenEventId` and the `resume` channel handshake;
5. direct random-token redaction fails before attach/recovery drift;
6. failed live attach and respawn reuse one derived token;
7. existing persisted-token state keeps precedence and does not mint a replacement on attach.

## Complete-diff self-review

Work class: upstream-fork research.

Builder review examined the complete four-file diff after execution. No blocking defect remains in the reviewed fence.

The earlier green prototype had one concrete review defect: it made the live token optional for default random-token harnesses as well as deterministic harnesses. That allowed malformed state to pass framework validation and reach sandbox acquisition. The current public wrapper restores strict pre-resume validation for the default harness while retaining deterministic redaction support.

Compatibility boundaries checked:

- random token creation is unchanged;
- persisted token precedence is unchanged;
- thread/session identity is unchanged;
- live cursor and replay handshake are unchanged;
- attach-failure recovery remains the same apart from reusing the reconstructed bearer;
- the public `createCodex` return type remains the implementation harness type;
- no other bridge-backed harness is changed.

Current upstream issue/PR searches found no active equivalent bridge-token reconstruction work.

## Disposition

Disposition: `READY FOR INDEPENDENT REVIEW`

Requested independent review lens:

1. Is package-local Zod refinement in the public wrapper an acceptable way to keep random-token validation strict without widening the generic Harness lifecycle contract?
2. Is token omission correctly limited to deterministic-mint harness instances?
3. Is one-operation derived-token reuse correct across attach failure and respawn fallback?
4. Are the public type surface and lifecycle compatibility boundaries preserved?
5. Does any recovery path still trust serialized sandbox identity where the resumed sandbox should own authority?

The builder materially designed and implemented the candidate and is not eligible to issue final `ACCEPT`.

Any source/base movement or contradictory evidence expires this review request.
