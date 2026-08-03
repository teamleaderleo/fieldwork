# Conditional upstream pull-request draft — core: send full first Responses Lite turn after prewarm

Draft status: `prepared only if a Codex maintainer invites a PR`  
Required public issue: `<issue number>`  
Public interaction authorized: `no`  
Proposed head: `teamleaderleo/codex:fix/responses-lite-first-request-e4e0c70`  
Exact public-source parent: `e4e0c7070e53cf9535fd0083d8fb840b6cd410cf`  
Exact candidate head: `abf61e5fb8505181e071674ce224faff17e79d77`

---

# core: send full first Responses Lite turn after prewarm

## What

- End the untraced prewarm response chain before the first generated Responses Lite WebSocket request.
- Send the complete current Lite input with no prewarm `previous_response_id`.
- Resume ordinary incremental reuse from the first generated response.
- Retry a failed first generation with the same complete request.
- Leave generic non-Lite WebSocket warmup compression unchanged.

Discussed in #<issue number>.

## Why

Startup prewarm sends the Responses Lite tool and instruction prefix with `generate=false`. Codex treats this as connection setup rather than an inference attempt, but the first generated request can currently reuse the prewarm response ID and send only an incremental suffix.

That makes the first real generated turn depend on server-side state created by a request that generated no turn. For Responses Lite, where tools and instructions are input items, the first generated request is easier to reason about and retry when it is complete and self-contained.

This change establishes a narrow boundary:

```text
prewarm                 -> connection/setup state
first generated response -> first incremental conversation baseline
later generated turns    -> ordinary incremental continuation
```

## How

`ModelClientSession::stream_responses_websocket` detects the first request where:

- the call is not itself a warmup;
- Responses Lite is enabled; and
- the retained response came from untraced startup prewarm.

At that transition, it clears the retained prewarm response receiver and skips incremental request preparation. The existing full-request serializer then sends the complete current request.

After the first generated response succeeds, the existing state assignment clears warmup provenance and installs that generated response as the next incremental predecessor. Reconnect and later continuation ownership remain unchanged.

No public API, wire schema, provider capability, planner behavior, or generic non-Lite transport behavior changes.

## Tests

Added focused mock-WebSocket coverage:

- `websocket_first_responses_lite_turn_sends_exact_current_request_after_startup_prewarm`
  - prewarm uses `generate=false` and carries the Lite tool/instruction prefix;
  - first generation omits `previous_response_id`;
  - generated input preserves the complete prewarm prefix and appends the user message.

- `responses_lite_reuses_generated_response_after_full_first_turn`
  - first generation is complete;
  - the next turn uses the first generated response ID;
  - the next turn sends only the new suffix.

- `responses_lite_retries_full_first_turn_after_failed_generation`
  - first generation fails;
  - retry sends the same complete request;
  - retry does not inherit a prewarm predecessor.

Validation for the exact current-source head:

```text
cargo fmt --all -- --check
cargo test -p codex-core --test all responses_lite_reuses_generated_response_after_full_first_turn -- --nocapture
cargo test -p codex-core --test all responses_lite_retries_full_first_turn_after_failed_generation -- --nocapture
cargo test -p codex-core --test all websocket_first_responses_lite_turn_sends_exact_current_request_after_startup_prewarm -- --nocapture
just fix -p codex-core
git diff --check
```

The final receipt should be inserted here after the corrected immutable-head run completes.

## Compatibility and tradeoffs

- Public API: unchanged.
- Wire schema: unchanged.
- Generic Responses WebSocket behavior: unchanged.
- Responses Lite: retransmits the complete prefix once for the first generated request after prewarm.
- Later turns: remain incremental.
- Failed first generation: retries independently from prewarm state.
- Rollback: one atomic commit.

The principal cost is one additional transmission of the Lite prefix at startup. Live provider latency and cache effects have not been measured; the issue discussion should confirm that this request-state invariant matches the intended backend contract before the PR is submitted.

## Scope

This PR does not attempt to fix or explain every Responses Lite validation, provider-compatibility, context-budget, or request-blocking report. It changes only the ownership transition from non-generating prewarm state to the first generated turn.

## Exact diff

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

- [x] Direct one-commit child of the exact inspected public-source parent.
- [x] Diff contains one production file and two target-native test files.
- [x] No workflow, Fieldwork, manifest, lock, generated, or snapshot file in the source diff.
- [x] Current contribution guidance rechecked: PR only after explicit maintainer invitation.
- [x] Public issue-first draft prepared.
- [ ] Public issue filed and linked.
- [ ] Maintainer invitation recorded.
- [ ] Corrected exact-head current-source execution complete.
- [ ] Filing-time rebase, duplicate search, and CI state refreshed.
- [ ] Exact user authorization to submit the invited PR recorded.
