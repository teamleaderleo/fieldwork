# Conditional upstream pull-request draft — core: send the full first Responses Lite request after prewarm

Draft status: `use only if a Codex maintainer invites a PR`  
Required public issue: `<issue number>`  
Public interaction authorized: `no`  
Proposed head: `teamleaderleo/codex:fix/responses-lite-first-request-e4e0c70`  
Public-source parent: `e4e0c7070e53cf9535fd0083d8fb840b6cd410cf`  
Candidate head: `abf61e5fb8505181e071674ce224faff17e79d77`

---

# core: send the full first Responses Lite request after prewarm

## What changed

- The first generated Responses Lite request no longer uses the prewarm response ID.
- It sends the full current input, including the tool and instruction prefix.
- Later requests continue from the first generated response as before.
- A failed first generation retries the same full request.
- The non-Lite WebSocket path is unchanged.

Discussed in #<issue number>.

## Why

Startup prewarm sends a Responses Lite request with `generate=false`. It sends the tool and instruction prefix and prepares the WebSocket path, but it does not ask the model to produce an answer.

Before this change, the first generated request could use the prewarm response ID as `previous_response_id` and send only the new user input. The service then had to recover the rest of the request from the prewarm response.

This change keeps prewarm as setup. The first generated request is complete. Its response ID becomes the starting point for later incremental requests.

```text
prewarm request          -> setup
first generated request  -> full request
later generated requests -> continue from the first generated response
```

## How

`ModelClientSession::stream_responses_websocket` checks whether:

- the request is not a warmup request;
- Responses Lite is enabled; and
- the stored response came from startup prewarm.

When all three are true, it clears the stored prewarm response and does not build an incremental request. The existing full-request serializer sends the current input.

After the request succeeds, the existing state update stores the generated response ID. Later requests use the normal incremental path.

No API or wire-format changes are included.

## Tests

The added WebSocket tests cover:

- `websocket_first_responses_lite_turn_sends_exact_current_request_after_startup_prewarm`
  - prewarm uses `generate=false`;
  - prewarm sends the Lite tool prefix;
  - the first generated request has no `previous_response_id`;
  - the first generated request includes the prewarm prefix and the user message.

- `responses_lite_reuses_generated_response_after_full_first_turn`
  - the first generated request is full;
  - the next request uses the first generated response ID;
  - the next request sends only the new suffix.

- `responses_lite_retries_full_first_turn_after_failed_generation`
  - the first generation fails;
  - the retry sends the same full request;
  - the retry does not use the prewarm response ID.

Validation:

```text
cargo fmt --all -- --check
cargo test -p codex-core --test all responses_lite_reuses_generated_response_after_full_first_turn -- --nocapture
cargo test -p codex-core --test all responses_lite_retries_full_first_turn_after_failed_generation -- --nocapture
cargo test -p codex-core --test all websocket_first_responses_lite_turn_sends_exact_current_request_after_startup_prewarm -- --nocapture
just fix -p codex-core
git diff --check
```

The current-head receipt should be added here after the queued run completes.

## Tradeoff

The first generated request sends the Lite prefix again. Later requests still use incremental continuation.

This PR does not claim a measured latency improvement or a fix for connector hangs. It changes the request sequence so that the first generated turn does not depend on a `generate=false` response.

## Scope

This change covers one point in the Responses Lite WebSocket lifecycle: the move from startup prewarm to the first generated request.

It does not change tool execution, connector networking, tool-call timeouts, cancellation, model selection, or the generic Responses WebSocket path.

## Diff

```text
base    e4e0c7070e53cf9535fd0083d8fb840b6cd410cf
head    abf61e5fb8505181e071674ce224faff17e79d77
commits 1
files   3
stat    +301/-1
```

Changed files:

```text
codex-rs/core/src/client.rs
codex-rs/core/tests/suite/agent_websocket.rs
codex-rs/core/tests/suite/client_websockets.rs
```

---

## Internal submission checklist

- [x] One commit on the inspected public-source parent.
- [x] One production file and two test files.
- [x] No workflow, Fieldwork, manifest, lock, generated, or snapshot file in the source diff.
- [x] Contribution guidance rechecked: PR only after a maintainer invitation.
- [x] Issue-first draft prepared.
- [ ] Public issue filed and linked.
- [ ] Maintainer invitation recorded.
- [ ] Current-head execution complete.
- [ ] Filing-time rebase, duplicate search, and CI state refreshed.
- [ ] User authorization to submit recorded.
