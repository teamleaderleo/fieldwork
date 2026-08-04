# Unit 24 — first generated Responses Lite request after prewarm

## What this is

Codex can send a WebSocket prewarm request before the first user turn. For Responses Lite, that request contains tools and instructions and sets `generate=false`.

The first real model request can then point to the prewarm response ID and send only the new user input.

This unit tests another sequence:

```text
prewarm request          -> setup
first generated request  -> full input
later generated requests -> continue from the first generated response
```

A failed first generation retries the full request. The non-Lite WebSocket path is unchanged.

## Public route

`ISSUE FIRST`

Codex accepts outside code only by invitation, so the issue is the expected first public step. The code and PR draft are prepared in owned repositories in case the team asks for them.

No public upstream contact has occurred.

## Current source

- Public-source parent: `e4e0c7070e53cf9535fd0083d8fb840b6cd410cf`
- Candidate head: `abf61e5fb8505181e071674ce224faff17e79d77`
- Source branch: `teamleaderleo/codex:fix/responses-lite-first-request-e4e0c70`
- Owned-fork review PR: `teamleaderleo/codex#143`
- Compare: one commit, three files, `+301/-1`

Changed files:

```text
codex-rs/core/src/client.rs
codex-rs/core/tests/suite/agent_websocket.rs
codex-rs/core/tests/suite/client_websockets.rs
```

The source diff contains no workflow, Fieldwork, manifest, lock, generated, or snapshot file.

## What the code changes

For the first generated Responses Lite request after prewarm, Codex stops using the prewarm response ID and sends the full current request.

After that request succeeds, later requests use the generated response ID and the existing incremental path.

If the first generated request fails, the retry sends the same full request.

## Tests

- `websocket_first_responses_lite_turn_sends_exact_current_request_after_startup_prewarm`
  - first generated request has no prewarm `previous_response_id`;
  - it includes the tool and instruction prefix plus the user message.

- `responses_lite_reuses_generated_response_after_full_first_turn`
  - the next request continues from the first generated response;
  - it sends only the new suffix.

- `responses_lite_retries_full_first_turn_after_failed_generation`
  - the retry sends the full request;
  - it does not use the prewarm response ID.

## Evidence state

The same three Git blobs passed the earlier focused execution at source `9fd4ba575de8dd77bc411362256591ce9e7d8c82`:

- source fence;
- formatting;
- the two client tests;
- the full-agent request test;
- clean worktree.

The current source is a one-commit restack with identical blobs for all three changed files. A run tied to the current commit SHA remains queued and is not recorded as complete.

## What this does not claim

This unit does not show that the current request sequence causes:

- GitHub connector hangs;
- connector calls that never time out;
- Codex app freezes;
- model timeouts;
- tool-execution failures.

Those symptoms pass through other parts of the system. This unit concerns the first model request in a prewarmed Responses Lite session.

## Draft workspace

- [Draft working notes](./DRAFT_NOTES.md)
- [Issue draft](./UPSTREAM_ISSUE.md)
- [Conditional PR draft](./UPSTREAM_PR.md)
- [Tests and receipts](./TESTS.md)
- [Review record](./REVIEW.md)
- [Technical deep dive](./DEEP_DIVE.md)
- [Approaches considered](./APPROACHES.md)

## Next steps

1. Review the issue explanation and tone.
2. Settle the current-commit execution run.
3. Refresh public main and duplicate search before filing.
4. File the issue only after user authorization.
5. Submit code only if a Codex maintainer invites a PR and the user authorizes it.

Public upstream interaction: `none`.
