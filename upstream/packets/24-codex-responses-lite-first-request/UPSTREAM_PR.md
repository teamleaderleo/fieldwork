# Upstream pull-request draft — core: send full first Responses Lite turn after prewarm

Draft status: `internal preparation`  
Proposed head: `teamleaderleo/codex:fix/responses-lite-first-request`  
Inspected public-source parent: `ee0247f95a6fe2b094ba2253d82cae2a2b4c2dff`  
Exact candidate head: `9fd4ba575de8dd77bc411362256591ce9e7d8c82`  
Public interaction authorized: `no`

---

## Summary

- End the untraced warmup response chain before the first generated Responses Lite WebSocket request.
- Send the complete current logical input with no warmup `previous_response_id`.
- Preserve generic WebSocket warmup compression and resume incremental reuse after the first generated response.
- Retry a failed first generation with the same complete request.

## Problem

Startup prewarm sends the Responses Lite input prefix with `generate=false`. That request prepares connection and prefix state; it does not produce a generated turn.

Generic Responses WebSocket transport intentionally allows a later request to reuse the warmup response ID and send a compressed input delta. For Responses Lite, however, tools and instructions are input items, so the complete input sequence owns the generated request identity. Chaining the first generation to setup state leaves that identity dependent on a response that did not generate a turn.

The rule implemented here is narrow: generic warmup compression remains unchanged, while the first generated Lite request is complete and independent. Only a generated response becomes the predecessor of later generated turns.

## Change

`ModelClientSession::stream_responses_websocket` recognizes the first request where:

- the call is not a warmup;
- Responses Lite is enabled; and
- the retained response came from untraced warmup.

At that transition it clears the warmup response receiver and skips incremental request preparation. The existing full-request serializer sends the complete current request. The existing post-request state update resets warmup provenance, so later successful responses continue through the ordinary incremental path.

No public API, wire schema, provider capability, planner behavior, or generic non-Lite transport behavior changes.

## Tests

Added target-native coverage:

- `websocket_first_responses_lite_turn_sends_exact_current_request_after_startup_prewarm`
  - warmup uses `generate=false` and carries a nonempty `additional_tools` manifest;
  - first generated request has no `previous_response_id`;
  - generated input preserves the complete warmup prefix and appends the user message.
- `responses_lite_reuses_generated_response_after_full_first_turn`
  - first generation is complete;
  - the next turn uses `previous_response_id = resp-1` and sends only the new suffix.
- `responses_lite_retries_full_first_turn_after_failed_generation`
  - first generation fails;
  - retry sends the same complete request with no warmup predecessor.

Historical exact-source receipt:

```text
FIELDWORK_LITE_SOURCE_FENCE=3/3
FIELDWORK_LITE_CLIENT_EXACT=2/2
FIELDWORK_LITE_AGENT=default:101;large:0
```

Fresh exact-head execution is retained in owned execution-only PR `teamleaderleo/codex#135`, workflow run `30690825055`, job `91345120846`. It verifies source identity, formatting, the three exact controls, the default/16-MiB agent discriminator, `just test -p codex-core` with a raised worker stack, `just fix -p codex-core`, and a clean worktree.

## Prior art

- Merged `openai/codex#23581` intentionally preserves generic compressed wire reuse after untraced warmup while recording the complete logical request for rollout replay. This change leaves that non-Lite behavior intact.
- Merged `openai/codex#27946` moves Responses Lite tools and instructions into input items. This change applies the complete-first-generation rule to that Lite request form.
- Refreshed issue, PR, and code searches on `2026-08-01` found no equivalent implementation.

## Compatibility

- Public API: unchanged.
- Wire schema: unchanged.
- Generic WebSocket transport: unchanged.
- Lite transport: one complete first generated request after prewarm; later turns remain incremental.
- Retry: failed first generation retries complete and independent from warmup.
- Performance: one-time retransmission of the Lite prefix after prewarm.
- Rollback: revert one commit.

## Limits

- Live provider, proxy, and long-running soak behavior is unmeasured.
- Production prevalence is unmeasured.
- Broad agent tests exhibit known worker-stack pressure; the exact client controls isolate the request-state behavior, and the agent control retains a default-versus-raised-stack discriminator.
- Repository-wide CI failures outside the three-file fence require classification but do not justify unrelated source changes.

## Exact source

```text
base  ee0247f95a6fe2b094ba2253d82cae2a2b4c2dff
head  9fd4ba575de8dd77bc411362256591ce9e7d8c82
files 3
commits 1
stat  +301/-1
```

Changed files:

```text
codex-rs/core/src/client.rs
codex-rs/core/tests/suite/agent_websocket.rs
codex-rs/core/tests/suite/client_websockets.rs
```

---

## Submission checklist

- [x] Direct one-commit child of the exact inspected public-source parent.
- [x] Diff contains only one production file and two target-native test files.
- [x] No temporary workflow, publisher, Fieldwork, manifest, lock, generated, or snapshot file in the source diff.
- [x] Every changed file and surrounding state owner read at exact head.
- [x] Generic warmup and Responses Lite public prior art reviewed.
- [x] Duplicate and overlap search refreshed on `2026-08-01`.
- [x] Complete-diff self-review recorded on owned PR `#130`.
- [ ] Fresh exact-head execution complete and receipt transferred.
- [ ] Every source-relevant current CI failure classified.
- [ ] Independent acceptance recorded.
- [x] No repository-local `CONTRIBUTING.md` exists at the inspected source parent; `AGENTS.md` instructions are recorded and applied to the execution gate.
- [ ] Filing-time contribution and AI-disclosure policy rechecked.
- [ ] Exact user authorization to contact public upstream recorded.
