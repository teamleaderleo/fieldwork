# Upstream pull-request draft — core: send full first Responses Lite turn after prewarm

Draft status: `not ready`  
Proposed head: `teamleaderleo/codex:fix/responses-lite-first-request`  
Proposed base: `openai/codex:main` from inspected base `670f69416bf91c5dfd8b58669e78050b584ff053`  
Public interaction authorized: `no`

---

## Summary

- End the Responses Lite warmup response chain before the first generated WebSocket request.
- Send the complete current logical request with no warmup `previous_response_id`.
- Resume incremental reuse after the first generated response and retry a failed first generation with the complete request.

## Problem

Startup prewarm sends the Lite prefix with `generate=false`. That request prepares the connection and tool manifest; it does not own generated-turn history.

The client retains the warmup response in WebSocket session state. Generic incremental preparation can then construct the first generated request as a continuation of warmup state. This leaves the current logical request identity dependent on a setup response chain.

The governing rule is: prewarm may prepare transport state, while only a successfully generated response may become the predecessor of later generated turns.

## Change

`ModelClientSession::stream` now recognizes the first non-warmup request where:

- Responses Lite is enabled; and
- the last response came from untraced warmup.

At that transition it clears the warmup response receiver and skips incremental request preparation. The existing full-request path serializes the complete current request.

The change stays local to request selection. It changes no public API, provider schema, prewarm scheduling, planner behavior, or ordinary continuation after a generated response.

## Tests

Target-native tests added:

- `websocket_first_responses_lite_turn_sends_exact_current_request_after_startup_prewarm`
  - warmup uses `generate=false` and contains a nonempty Lite manifest;
  - first generated request has no `previous_response_id`;
  - first generated input preserves the exact warmup prefix and appends the user message.
- `responses_lite_reuses_generated_response_after_full_first_turn`
  - first generation is full;
  - the next turn uses `previous_response_id = resp-1` and sends only the new suffix.
- `responses_lite_retries_full_first_turn_after_failed_generation`
  - first generation fails;
  - retry sends the same full request with no warmup predecessor.

Retained historical execution:

```text
FIELDWORK_LITE_SOURCE_FENCE=3/3
FIELDWORK_LITE_CLIENT_EXACT=2/2
FIELDWORK_LITE_AGENT=default:101;large:0
```

Current clean-head execution remains required before submission:

```text
cargo test -p codex-core --test all --locked <resolved exact client test> -- --exact --nocapture
RUST_MIN_STACK=16777216 cargo test -p codex-core --test all --locked <resolved exact agent test> -- --exact --nocapture
just fmt
just fix -p codex-core
```

## Compatibility

- public API: unchanged
- existing behavior retained: prewarm remains enabled; post-generation incremental continuation remains enabled
- platform or runtime notes: one retained full-agent run overflows the default Tokio worker stack and passes at 16 MiB; isolated client controls pass normally
- performance or allocation notes: one complete first generated Lite request is transmitted after prewarm; later turns remain incremental
- migration or rollback: no migration; one-commit revert restores prior behavior

## Alternatives considered

- Disable prewarm: removes the transition by sacrificing startup preparation.
- Reconnect for every turn: removes incremental continuation and connection reuse.
- Compare serialized warmup and generated requests: widens normalization and schema-ordering concerns.
- Introduce typed response-provenance state: useful only as a broader refactor; excessive for this bounded correction.

## Limits

- Current-head exact test renewal is pending.
- Live provider, proxy, and long-running soak paths remain untested.
- Current ordinary CI has repository-wide red/incomplete jobs. One inspected failure is a stale manifest exception for `codex-rs/code-mode/Cargo.toml`, outside this three-file diff; remaining red jobs need classification.
- Production prevalence is unmeasured.

## Related work

- No equivalent public issue or pull request was found in the `2026-08-01` duplicate search for Responses Lite, prewarm, and `previous_response_id` overlap.

---

## Submission checklist

- [x] Branch is a direct child of inspected public head `670f69416bf91c5dfd8b58669e78050b584ff053`.
- [x] Diff contains only product source and target-native tests.
- [x] Fieldwork wording, temporary workflows, publishers, receipts, and evidence-only files are absent from the source diff.
- [x] Every changed file was read at exact head `2c3f21d38056d2d77215cd9dce820a680d11cfe8`.
- [ ] Focused regression relationship is renewed on the current baseline and candidate where practical.
- [ ] Project-declared ordinary gates complete or every failure is classified.
- [x] Current duplicate and overlap search completed on `2026-08-01`.
- [x] Commit history and title follow the target's current style.
- [ ] Target contribution and AI-disclosure policies checked at filing time.
- [ ] Exact user authorization to open the public pull request recorded.
