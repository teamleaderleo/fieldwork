# Upstream issue draft — first generated Responses Lite request can inherit prewarm response state

Draft status: `not applicable — direct PR preferred`  
Public interaction authorized: `no`

---

## Summary

Responses Lite startup prewarm sends the request prefix with `generate=false` to establish the WebSocket and prepare the tool manifest. The first generated turn can then be constructed as an incremental continuation of that warmup response.

The desired contract is simpler: prewarm owns connection and prefix setup; the first generated turn owns a complete current logical request. Only a successfully generated response becomes the predecessor of later incremental turns.

## Reproduction

1. Configure a model with `use_responses_lite = true` and WebSocket transport.
2. Start a session with startup prewarm enabled.
3. Capture the warmup and first generated WebSocket request bodies.
4. Inspect `generate`, `previous_response_id`, and `input`.

Target-native characterization:

```text
cargo test -p codex-core --test all --locked \
  suite::agent_websocket::websocket_first_responses_lite_turn_sends_exact_current_request_after_startup_prewarm \
  -- --exact --nocapture
```

## Observed behavior

The warmup response is retained as untraced response-chain state. Generic incremental request preparation can use that state when constructing the first generated request.

## Expected behavior

The first generated Responses Lite request should:

- omit a warmup `previous_response_id`;
- carry the complete current Lite input prefix and submitted user input;
- allow later generated turns to continue incrementally from the first generated response;
- retry a failed first generation with the same complete request.

## Current source observation

`ModelClientSession::stream` owns both the prewarm transition and request construction. The session records whether the last response came from untraced warmup, while generic WebSocket request preparation can consume the available response receiver to build an incremental request.

## Candidate direction

At the first non-warmup request where Responses Lite is enabled and the last response came from untraced warmup:

1. clear the warmup response receiver;
2. skip incremental request preparation;
3. use the existing full-request serialization path.

After a generated response succeeds, existing incremental continuation remains unchanged.

## Compatibility and risks

- The wire schema stays unchanged.
- The first generated Lite request retransmits the complete current request once.
- Later turns retain incremental request reuse.
- Non-Lite requests and warmup requests stay on their existing paths.
- A broader full-agent test currently needs a larger Tokio worker stack in the retained execution environment; isolated client tests pass with the ordinary runner.

## Evidence limits

- Production prevalence has not been measured.
- Live provider and proxy paths have not been exercised for this packet.
- Current clean-head focused execution remains pending.
- Current public duplicate search on `2026-08-01` found no equivalent open issue or pull request.

## Versions and environment

- project commit inspected: `670f69416bf91c5dfd8b58669e78050b584ff053`
- candidate commit: `2c3f21d38056d2d77215cd9dce820a680d11cfe8`
- platform: GitHub Actions Linux for retained focused execution
- runtime/compiler: repository-pinned Rust toolchain and locked workspace dependencies
- relevant configuration: Responses Lite enabled; WebSocket startup prewarm enabled

## Additional context

A direct three-file candidate exists with one client hunk and three target-native WebSocket controls. An issue adds little value unless maintainers prefer contract discussion before reviewing the patch.

---

## Filing checklist

- [ ] Current upstream issue and PR search repeated immediately before filing.
- [ ] Reproduction works on a current public revision.
- [x] Severity and prevalence wording stays within evidence.
- [x] Private, internal, or evidence-only links removed from the public draft body.
- [ ] Target issue template and contribution policy followed.
- [ ] AI disclosure handled according to current project policy.
- [ ] Exact user authorization to file this issue recorded.
