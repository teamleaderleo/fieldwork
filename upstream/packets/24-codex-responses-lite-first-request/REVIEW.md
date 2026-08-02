# Review — unit 24 Responses Lite first request after prewarm

## Review subject

- Work class: `upstream-fork research`
- Target project: `openai/codex`
- Exact public-source parent: `ee0247f95a6fe2b094ba2253d82cae2a2b4c2dff`
- Exact candidate head: `9fd4ba575de8dd77bc411362256591ce9e7d8c82`
- Canonical source branch: `teamleaderleo/codex:fix/responses-lite-first-request`
- Canonical draft PR: `teamleaderleo/codex#130`
- Compare: one commit, exactly three files, `+301/-1`
- Upstream-contact authority: `none`

## Complete changed-file fence

1. `codex-rs/core/src/client.rs`
2. `codex-rs/core/tests/suite/agent_websocket.rs`
3. `codex-rs/core/tests/suite/client_websockets.rs`

No workflow, publisher, Fieldwork, manifest, lock, generated, snapshot, planner, or tool-registration file appears in the source diff.

## Complete-diff reviews

### Self-review

Review `4834209535` is attached to `teamleaderleo/codex#130` and pinned to exact head `9fd4ba575de8dd77bc411362256591ce9e7d8c82`.

Result: no source blocker found.

### Independent review boundary

Review `4834383404` independently read the complete one-commit, three-file diff and surrounding response-chain implementation.

Result:

```text
ACCEPT — subject to exact-head execution
```

The review found no source, test, compatibility, or packaging defect inside the unit boundary. It required a repaired immutable-source execution receipt because an earlier target carrier failed before running source code.

That condition is satisfied by Fieldwork run `30691514386`, job `91346961426`, which checked out exact source `9fd4ba...` and passed the source fence, formatting, both exact client controls, the full-agent discriminator, and clean-worktree verification.

## Review findings

- The predicate is limited to the first non-warmup Responses Lite request after an untraced warmup response.
- Clearing `last_response_rx` prevents the setup response ID from becoming the generated-turn predecessor and leaves serialization to the established full-request path.
- Existing post-generation assignment resets warmup provenance and lets later generated responses participate in ordinary incremental continuation.
- Existing reconnect logic clears every relevant response-chain field.
- The client and full-agent controls cover complete first generation, post-generation continuation, and failed-first full retry.
- Generic non-Lite warmup compression remains unchanged.
- No alternate field was found that can reintroduce the discarded warmup response ID after the guarded branch.

## Public prior-art review

Merged `openai/codex#23581` intentionally retains generic compressed wire reuse after untraced warmup while recording the complete logical request for rollout replay. Earlier `#22825` and `#23278` address unresolved or omitted untraced warmup parents in trace/replay.

Merged `openai/codex#27946` moves Responses Lite tools and instructions into input items, making the complete input sequence the Lite request identity.

The candidate is compatible with both decisions: it changes wire chaining only for Responses Lite and only at the warmup-to-first-generation transition.

Searches covered `Responses Lite`, WebSocket prewarm, `previous_response_id`, all three test names, and current open/closed Codex issues and pull requests. No equivalent public implementation was found.

## Current-source staleness review

The candidate parent is `ee0247f95a6fe2b094ba2253d82cae2a2b4c2dff`. Public `openai/codex:main` was refreshed through `3e3d82d674d8a263cf2c33684f6a04beb9dcf8d7`, six commits later.

Those commits do not modify any of the three unit files. The one-commit candidate remains isolated from inspected public drift.

## Exact execution review

Execution PR: `teamleaderleo/fieldwork#459`  
Run: `30691514386`  
Job: `91346961426`  
Conclusion: `success`

Successful source-specific steps:

- immutable source checkout and exact three-file fence;
- target setup and pinned Rust toolchain;
- repository formatting;
- both exact client controls;
- exact full-agent request control and stack discriminator;
- clean worktree and `git diff --check`.

## Repository-wide result review

The current source matrix passed v8-canary, formatting, cargo-deny, codespell, blob-size policy, changed-area detection, and cargo-shear.

Its manifest check fails on `codex-rs/code-mode/Cargo.toml`, outside the unit. SDK/Bazel/macOS/Windows failures and cancellations identify no source-attributable change in the three-file fence. A separate broad `just test -p codex-core` job also fails after the exact source controls pass; the available receipt exposes no unit-specific failing assertion. The packet records these repository-health results without turning missing diagnostics into a source claim.

Supplementary base/candidate controls remain retained for repository-health follow-up. Runner allocation and unrelated broad-suite health do not reverse the completed exact execution and review result for this unit.

## Source cleanliness checklist

- [x] Direct one-commit child of the exact inspected public-source parent.
- [x] Exactly three intended source/test files.
- [x] No Fieldwork-only machinery in the source diff.
- [x] No generated or dependency churn.
- [x] Complete diff read at exact head.
- [x] Relevant generic warmup and Lite request-form prior art reviewed.
- [x] Duplicate search refreshed.
- [x] Complete-diff self-review recorded.
- [x] Independent complete-diff acceptance recorded.
- [x] Independent review’s exact-head execution condition satisfied.
- [x] Exact source fence, formatting, behavior, and clean-worktree receipt complete.
- [x] Broad repository failures classified outside the unit claim.

## Reviewer disposition

`READY`

The source-specific acceptance claim is supported by the exact current head, complete independent review, green exact behavior, formatting and cleanliness, and an unchanged public-file fence. Public filing remains a separate authority decision.

Public upstream interaction: `none`.
