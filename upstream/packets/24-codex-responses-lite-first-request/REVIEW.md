# Review — Unit 24 Responses Lite first request after prewarm

## Review subject

- Work class: `upstream-fork research`
- Target project: `openai/codex`
- Exact source parent: `e4e0c7070e53cf9535fd0083d8fb840b6cd410cf`
- Exact candidate head: `abf61e5fb8505181e071674ce224faff17e79d77`
- Canonical source branch: `teamleaderleo/codex:fix/responses-lite-first-request-e4e0c70`
- Owned-fork draft PR: `teamleaderleo/codex#143`
- Compare: one commit, exactly three files, `+301/-1`
- Public route: `ISSUE FIRST`
- Upstream-contact authority: `none`

## Changed-file fence

1. `codex-rs/core/src/client.rs`
2. `codex-rs/core/tests/suite/agent_websocket.rs`
3. `codex-rs/core/tests/suite/client_websockets.rs`

No workflow, Fieldwork, manifest, lock, dependency, generated, snapshot, planner, or tool-registration file appears in the source diff.

## Complete-diff reviews

### Historical independent review

Review `4834383404` independently read the complete predecessor diff and surrounding response-chain implementation.

Result:

```text
ACCEPT — subject to exact-head execution
```

That predecessor received a green immutable-head execution receipt in run `30691514386`, job `91346961426`.

### Current exact-head review

Review `4848205363` is attached to `teamleaderleo/codex#143` and pinned to current source `abf61e5fb8505181e071674ce224faff17e79d77`.

Findings:

- the production predicate is limited to the first non-warmup Responses Lite request after untraced startup prewarm;
- clearing the retained response receiver prevents the setup response ID from becoming generated-turn ancestry;
- serialization remains owned by the existing full-request path;
- existing post-generation assignment makes the first generated response the later incremental baseline;
- reconnect cleanup and generic non-Lite warmup behavior remain unchanged;
- the three controls cover complete first generation, generated-response continuation, and failed-first complete retry;
- no source, scope, compatibility, or packaging blocker was found.

Current immutable-head execution is the remaining acceptance condition.

## Exact blob-equivalence control

The current source was compared against the previously green exact head `9fd4ba575de8dd77bc411362256591ce9e7d8c82`.

All three complete file blobs are identical:

| File | Git blob SHA |
| --- | --- |
| `codex-rs/core/src/client.rs` | `157fb71748d3293bca4fe6983c4f50d98ded58b4` |
| `codex-rs/core/tests/suite/agent_websocket.rs` | `3e39cdd92e921352dcaa4c9667d4cd4861ee4556` |
| `codex-rs/core/tests/suite/client_websockets.rs` | `8ceb0f571971b26f0bdc8bfc04921e7e55db6a55` |

This proves that the current restack did not merely reproduce a similar patch; it contains the exact production and test file contents that passed the historical immutable-head lane.

The packet still distinguishes that strong predecessor evidence from a fresh current-commit integration receipt.

## Current public drift

The source is a direct child of `e4e0c707...`. During final review, public main advanced one commit to `3149fa4b992a49356d720bbca6f59c2ad4f963a9`.

That commit changes Git process-tree containment, Git utility dependencies, PTY Job Object handling, and their tests. It does not touch any Unit 24 file or the adjacent Responses WebSocket path.

The exact source therefore remains mechanically isolated through the latest inspected public head. A filing-time rebase remains required because Codex main is fast-moving.

## Duplicate and prior-art review

Filing-time issue and PR searches on `2026-08-04` covered:

- `Responses Lite prewarm first generated previous_response_id`;
- `generate=false warmup response parent websocket`;
- the exact test names and relevant state fields.

No equivalent issue or implementation was found.

Related public work remains non-equivalent:

- generic untraced-warmup tracing preserves compressed wire continuation while recording the logical request;
- Responses Lite represents tools and instructions inside input items;
- adjacent public reports concern provider capabilities, request validation, full-context fallback, and error reporting rather than the first-generation prewarm ancestry contract.

## Execution review

### Historical exact execution

- run: `30691514386`
- job: `91346961426`
- exact predecessor source: `9fd4ba575de8dd77bc411362256591ce9e7d8c82`
- result: source fence, formatting, exact controls, full-agent request shape, and clean worktree passed.

### Current exact execution

Lightweight carrier `teamleaderleo/smolrunner#286` tests immutable current source `abf61e5...`:

- run: `30849910237`
- job: `91807127950`
- status at packet update: queued for hosted-runner allocation.

The first current-head attempt stopped before tests because its workflow invoked Cargo from the repository root rather than `codex-rs/`. That harness error was corrected and is not treated as a source failure.

## Source-cleanliness checklist

- [x] Direct one-commit child of the exact inspected source parent.
- [x] Exactly three intended source/test files.
- [x] No execution machinery in the source diff.
- [x] No generated or dependency churn.
- [x] Complete diff read at exact current head.
- [x] Current source blobs proven identical to the green predecessor.
- [x] Generic warmup and Lite request-form prior art reviewed.
- [x] Duplicate search refreshed.
- [x] Current exact-head complete-diff review recorded.
- [x] Public route aligned with issue-first/invitation-only contribution guidance.
- [ ] Corrected current-commit immutable execution completes.
- [ ] Execution receipt transferred and disposable carrier closed.
- [ ] Filing-time rebase and duplicate search refreshed immediately before public action.
- [ ] Explicit public-filing authorization recorded.

## Reviewer disposition

`ISSUE FIRST — TECHNICALLY REVIEWABLE; CURRENT INTEGRATION RECEIPT QUEUED`

The issue question, current clean source, identical tested blobs, and complete-diff review are ready for human evaluation. The package does not claim a fresh current-commit green run until the queued lane actually completes.

Public upstream interaction: `none`.
