# Upstream issue draft — first generated Responses Lite request can inherit prewarm response state

Draft status: `not applicable — direct PR preferred`  
Public interaction authorized: `no`

---

## Summary

Responses Lite startup prewarm sends its tool/instruction input prefix with `generate=false` to establish the WebSocket and prepare reusable server-side state. Generic Responses-over-WebSocket requests intentionally can continue from that warmup response with a compressed delta.

Responses Lite needs a narrower first-generation rule because its complete tools and instructions are input items. The first generated Lite request should end the setup response chain, send the complete current logical input with no warmup `previous_response_id`, and let only a generated response become the predecessor of later generated turns.

A direct three-file correction and target-native tests already exist, so a separate issue adds little value unless maintainers prefer contract discussion before reviewing the patch.

## Reproduction

1. Configure a model with `use_responses_lite = true` and WebSocket transport.
2. Start a session with startup prewarm enabled.
3. Capture the `generate=false` warmup and first generated WebSocket request bodies.
4. Inspect `previous_response_id` and `input` on the generated request.

Target-native characterization:

```text
cargo test -p codex-core --test all --locked \
  suite::agent_websocket::websocket_first_responses_lite_turn_sends_exact_current_request_after_startup_prewarm \
  -- --exact --nocapture
```

## Observed behavior

The completed warmup response is retained as untraced response-chain state. Generic incremental request preparation can consume that response and construct the first generated request as a continuation of setup state.

## Expected behavior

The first generated Responses Lite request should:

- omit a warmup `previous_response_id`;
- carry the complete current Lite input prefix and submitted user input;
- preserve generic non-Lite warmup compression;
- allow later Lite turns to continue incrementally from the first generated response;
- retry a failed first generation with the same complete request.

## Candidate direction

At the first non-warmup request where Responses Lite is enabled and the retained response came from untraced warmup:

1. clear the warmup response receiver;
2. skip incremental request preparation;
3. use the existing full-request serializer.

After a generated response succeeds, the existing continuation path remains unchanged.

## Related work

- Generic untraced-warmup trace handling intentionally preserves compressed wire continuation while recording the complete logical request for replay.
- Responses Lite later moved tools and instructions into input items, making the complete input sequence the Lite request identity.
- Adjacent Responses Lite changes cover transport headers, standalone tools, metadata, image handling, and normalized tool names; none implement this first-generation transition.

Refreshed issue, pull-request, and code searches on `2026-08-01` found no equivalent public implementation.

## Compatibility and risks

- Public API and wire schema stay unchanged.
- Generic non-Lite WebSocket behavior stays unchanged.
- The first generated Lite request retransmits the complete input prefix once.
- Later Lite turns retain incremental reuse.
- A failed first generation retries independently from warmup state.
- Live provider, proxy, and long-running soak behavior remain unmeasured.

## Versions and environment

- public-source parent inspected: `ee0247f95a6fe2b094ba2253d82cae2a2b4c2dff`
- candidate commit: `9fd4ba575de8dd77bc411362256591ce9e7d8c82`
- source diff: one commit, three files, `+301/-1`
- platform: Linux GitHub Actions for retained focused execution
- runtime/compiler: repository-pinned Rust toolchain and locked workspace dependencies
- relevant configuration: Responses Lite enabled; WebSocket startup prewarm enabled

---

## Filing checklist

- [x] Current upstream issue, PR, and code search refreshed on `2026-08-01`.
- [x] Candidate reconciled onto a current inspected public-source parent.
- [x] Severity and prevalence wording stays within evidence.
- [x] Private, internal, and evidence-only links are absent from the public draft body.
- [ ] Exact-head execution receipt complete.
- [ ] Filing-time search and contribution guidance rechecked.
- [ ] AI disclosure handled according to current project policy.
- [ ] Exact user authorization to file this issue recorded.
