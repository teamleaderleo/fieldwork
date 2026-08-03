# Unit 24 — first generated Responses Lite request after prewarm

## Plain-language finding

Codex sends a startup WebSocket prewarm request with `generate=false`. For Responses Lite, that request includes the tool and instruction prefix but deliberately generates no assistant turn.

The first real generated request can nevertheless continue from the prewarm response ID and send only a suffix. That makes a non-generating setup response the parent of generated conversation state.

The proposed invariant is narrower and easier to reason about:

```text
prewarm                  -> connection/setup state
first generated response -> first incremental conversation baseline
later generated turns    -> ordinary incremental continuation
```

The first generated Lite request is complete and has no prewarm `previous_response_id`. A failed first generation retries complete. Generic non-Lite WebSocket warmup behavior remains unchanged.

## Recommended public route

`ISSUE FIRST`

This is the strongest first **original Codex issue** currently prepared in the Fieldwork backlog because it is:

- one concrete request sequence that can be explained without internal context;
- visible in current public source;
- a genuine architecture/correctness question rather than a speculative production diagnosis;
- backed by a one-hunk implementation proof and focused state-transition tests;
- compatible with Codex's current contribution rule that external changes begin with an issue and PRs are invitation-only.

The durable-append acknowledgement unit is a useful internal prerequisite but does not yet present as strong a standalone public issue. The terminal-completion retention unit has more direct user-facing potential but still needs its current-source repair and exact receipt. Unit 24 is the best first filing candidate now.

Public upstream interaction remains unauthorized and none has occurred.

## Current disposition

`ISSUE FIRST — filing package prepared; corrected current-head execution queued`

Last refreshed: `2026-08-04`

## Exact current source

- Target: `openai/codex:main`
- Exact inspected public parent: `e4e0c7070e53cf9535fd0083d8fb840b6cd410cf`
- Exact clean candidate: `abf61e5fb8505181e071674ce224faff17e79d77`
- Source branch: `teamleaderleo/codex:fix/responses-lite-first-request-e4e0c70`
- Exact-base alias: `teamleaderleo/codex:fix/responses-lite-first-request-base-e4e0c70`
- Owned-fork review PR: `teamleaderleo/codex#143`
- Compare: one commit, exactly three files, `+301/-1`

Changed files:

```text
codex-rs/core/src/client.rs
codex-rs/core/tests/suite/agent_websocket.rs
codex-rs/core/tests/suite/client_websockets.rs
```

No workflow, Fieldwork, manifest, dependency, lock, generated, or snapshot file appears in the source diff.

## Current implementation

At the first request where all three conditions hold:

```text
not warmup
Responses Lite enabled
retained response came from untraced startup prewarm
```

Codex clears the retained prewarm response receiver and skips incremental preparation. The existing full-request serializer sends the complete current Lite request. After generation succeeds, the existing response-state assignment installs the generated response as the ordinary incremental predecessor.

## Focused controls

- `websocket_first_responses_lite_turn_sends_exact_current_request_after_startup_prewarm`
  - complete first generated request;
  - no prewarm `previous_response_id`;
  - exact Lite prefix plus user input.

- `responses_lite_reuses_generated_response_after_full_first_turn`
  - later turn continues from the first generated response;
  - later turn sends only the new suffix.

- `responses_lite_retries_full_first_turn_after_failed_generation`
  - failed first generation retries complete;
  - no prewarm ancestry is inherited.

## Review

- Historical independent complete-diff review: `4834383404`
  - result: `ACCEPT — subject to exact-head execution`;
  - reviewed the same three-file patch before the current-base restack.
- Current exact-head complete-diff review on PR `#143`: `4848205363`
  - no source, scope, or packaging blocker;
  - current immutable-head execution remains the acceptance condition.
- The public-base advance from the previously reviewed source did not change any of the three unit files.

## Current execution lanes

All lanes test immutable Codex source `abf61e5...`; workflow commits are execution-only and excluded from the source diff.

- Codex carrier: `teamleaderleo/codex#142`, run `30849380733`.
- Fieldwork isolated carrier: `teamleaderleo/fieldwork#596`, run `30849709951`.
- Lightweight isolated carrier: `teamleaderleo/smolrunner#286`, run `30849910237`.

The first attempted current-head lane stopped before tests because the workflow ran Cargo from the repository root instead of `codex-rs/`. The carrier was corrected; this was an execution-harness error, not a source or test failure.

## Duplicate and prior-art result

Filing-time searches on `2026-08-04` found no issue or PR asking whether a `generate=false` Responses Lite prewarm response should be the parent of the first generated turn.

Related but non-equivalent public work:

- generic untraced-warmup tracing preserves compressed wire continuation while recording the logical request;
- Responses Lite places tools and instructions in input items;
- adjacent reports concern provider capability, request validation, context limits, and error handling rather than this startup ancestry contract.

## Public drafts

- [Issue-first draft](./UPSTREAM_ISSUE.md)
- [Conditional invited-PR draft](./UPSTREAM_PR.md)
- [Tests and receipts](./TESTS.md)
- [Review record](./REVIEW.md)
- [Technical deep dive](./DEEP_DIVE.md)
- [Approaches considered](./APPROACHES.md)

## Remaining steps before filing authorization

1. Record one corrected immutable-current-head green receipt.
2. Transfer the receipt into the issue, PR, tests, and review files.
3. Close and clean the execution-only carriers.
4. Perform one final duplicate search immediately before filing.
5. Obtain explicit authorization to open the public issue.

Public upstream interaction: `none`.
