# Deep dive — unit 24 Responses Lite first request after prewarm

## In simple words

Responses Lite serializes its tool catalogue and instructions as input items. Startup prewarm sends that reusable prefix with `generate=false`, which warms the WebSocket and server-side prefix but does not produce a generated turn.

Generic Responses-over-WebSocket behavior intentionally permits the next request to reuse the warmup response ID and transmit only a compressed delta. That behavior is valid for the generic transport and is preserved. The unit-24 correction applies only to Responses Lite: the first generated Lite request ends the untraced warmup chain and sends the complete current logical input with no warmup `previous_response_id`. After a generated response succeeds, ordinary incremental continuation resumes.

## Governing invariant

> A Responses Lite prewarm may establish transport state and transmit the reusable input prefix, but only a generated response may become the predecessor of later generated turns. The first generated Lite request must therefore carry the complete current logical request without a warmup `previous_response_id`.

## Exact source

- Public-source parent: `ee0247f95a6fe2b094ba2253d82cae2a2b4c2dff`
- Candidate head: `9fd4ba575de8dd77bc411362256591ce9e7d8c82`
- Canonical branch: `teamleaderleo/codex:fix/responses-lite-first-request`
- Canonical draft PR: `teamleaderleo/codex#130`
- Compare: one commit, exactly three files, `+301/-1`
- Public drift from the previous parent `670f69416bf91c5dfd8b58669e78050b584ff053`: five commits; none changed the three source-fence files

## Current behavior and ownership

The relevant owner is `ModelClientSession::stream_responses_websocket` in `codex-rs/core/src/client.rs`.

Before the candidate:

1. startup prewarm sends a `response.create` payload with `generate=false`;
2. the completed warmup response is retained in `last_response_rx`;
3. `last_response_from_untraced_warmup` marks its provenance;
4. generic incremental preparation may use that response ID for the first generated request;
5. Responses Lite can therefore send the first generated request as a continuation of setup state.

After the candidate, the first non-warmup request satisfying all three conditions:

- `model_info.use_responses_lite` is true;
- `last_response_from_untraced_warmup` is true;
- the current call is not itself a warmup;

clears `last_response_rx` and skips incremental request preparation. The existing full-request serializer then sends the complete current input.

The existing state update sets `last_response_from_untraced_warmup = warmup` after each request. A generated request therefore resets that provenance flag to false, and its successful response remains eligible for ordinary continuation.

Connection replacement already clears `last_request`, `last_response_rx`, and `last_response_from_untraced_warmup`; this change introduces no second state owner.

## Source map

| Area | Path | Responsibility | Control |
| --- | --- | --- | --- |
| request transition | `codex-rs/core/src/client.rs` | sever Lite warmup response authority before first generation | complete-diff review and exact client tests |
| full-agent identity | `codex-rs/core/tests/suite/agent_websocket.rs` | assert warmup prefix plus complete generated request through `test_codex` | `websocket_first_responses_lite_turn_sends_exact_current_request_after_startup_prewarm` |
| client continuation and retry | `codex-rs/core/tests/suite/client_websockets.rs` | isolate success continuation and failed-first retry | two `responses_lite_*` controls |

## Public prior art and compatibility

### Generic warmup compression is intentional

Merged `openai/codex#23581`, **Trace logical websocket request after untraced warmup**, records the complete logical request for rollout replay while intentionally retaining the compressed wire follow-up with `previous_response_id = warm-1` and an empty delta. Earlier trace work `#22825` and `#23278` addressed unresolved or omitted untraced warmup prefixes.

This is a compatibility constraint, not a duplicate. Unit 24 leaves generic WebSocket warmup reuse unchanged and applies its full-first rule only when `use_responses_lite` is true.

### Responses Lite changes request identity

Merged `openai/codex#27946`, **Use input items for Responses Lite tools**, moved Lite tools and instructions into `additional_tools` and developer input items to keep request identity one-to-one. This makes the complete input sequence materially significant for Lite and supplies the transport-specific reason for ending the setup response chain before first generation.

Adjacent Responses Lite PRs concerning transport headers, standalone tools, image formatting, metadata, and normalized tool names do not implement the same first-generated-request transition.

## Failure model

1. **Confirmed:** prewarm emits `generate=false` and receives a response ID.
2. **Confirmed:** the response is marked as an untraced warmup response.
3. **Confirmed:** generic incremental preparation can consume that response and derive a previous response ID plus an input delta.
4. **Confirmed public contract:** generic WebSocket code intentionally permits this compressed follow-up and repairs tracing separately.
5. **Responses Lite-specific risk:** Lite places the tool/instruction prefix in input items; chaining first generation to setup state leaves the complete generated request identity implicit in a response that did not generate a turn.
6. **Candidate correction:** send one complete first generated request, then continue incrementally only from a generated response.

## Tests and measured behavior

Historical exact-source execution on source `e520da008366cd720ef58fa0b489efc0a2867e97` recorded:

- `FIELDWORK_LITE_SOURCE_FENCE=3/3`
- `FIELDWORK_LITE_CLIENT_EXACT=2/2`
- `FIELDWORK_LITE_AGENT=default:101;large:0`

The two client controls passed under the ordinary runner. The full-agent assertion overflowed the default Tokio worker stack and passed with `RUST_MIN_STACK=16777216`; this is retained as a runner discriminator rather than presented as a product repair.

Fresh exact-head execution is assigned to execution-only PR `teamleaderleo/codex#135`, carrier head `fb77d59b2f5d07cebee889851a476ebab57c9e45`, workflow run `30690825055`, job `91345120846`. The workflow verifies the immutable source fence, formatting, both exact client controls, the agent default/16-MiB discriminator, `just test -p codex-core` with a 32-MiB worker stack, `just fix -p codex-core`, and a clean worktree.

## Compatibility analysis

- Public API: unchanged.
- Wire schema: unchanged; the candidate selects the existing full-request form.
- Generic Responses WebSocket behavior: unchanged.
- Responses Lite behavior: one complete first generated request after prewarm; later turns remain incremental.
- Persistence and replay: no schema change; logical trace behavior remains intact.
- Retry: a failed first generation retries the complete request without inheriting warmup state.
- Reconnect: existing session reset owns connection-state cleanup.
- Performance: one-time retransmission of the Lite prefix after prewarm; no steady-state retransmission.
- Rollback: revert the single source commit.

## Adversarial controls

- Success continuation: second generated turn must use `previous_response_id = resp-1` and only the new suffix.
- Failed first generation: retry must omit `previous_response_id` and repeat the complete request.
- Generic isolation: the predicate includes `use_responses_lite`, preserving `#23581` behavior for non-Lite requests.
- Reconnect isolation: existing connection replacement clears all response-chain state.
- Source isolation: one production hunk and two target-native test files; no planner, metadata, manifest, workflow, or generated-file changes.

## Review result

A complete-diff self-review is attached to `teamleaderleo/codex#130` at exact head `9fd4ba575de8dd77bc411362256591ce9e7d8c82`. It found no source blocker. Independent acceptance and exact-head execution remain separately recorded evidence boundaries.

## Reversing evidence

Reopen the implementation decision if any of the following is established:

- Responses Lite explicitly requires the first generated request to chain to a `generate=false` warmup response;
- the current exact tests show another mechanism already sends complete Lite identity while preserving warmup chaining;
- the one-time full Lite request violates a documented provider limit;
- a current-source failure is attributable to the three-file candidate rather than the repository baseline;
- equivalent public work lands before filing.

## Adjacent work excluded

- generic rollout-trace handling for untraced warmup parents;
- deferred tool exposure and Code Mode catalogue planning;
- worker-stack root-cause diagnosis;
- WebSocket reconnect policy beyond the failed-first retry path;
- production telemetry, provider deployment, proxy behavior, and long-running soak.
