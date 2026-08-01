# Review — unit 24 Responses Lite first request after prewarm

## Review subject

- Work class: `upstream-fork research`
- Target project: `openai/codex`
- Exact public-source parent: `ee0247f95a6fe2b094ba2253d82cae2a2b4c2dff`
- Exact candidate head: `9fd4ba575de8dd77bc411362256591ce9e7d8c82`
- Canonical source branch: `teamleaderleo/codex:fix/responses-lite-first-request`
- Canonical draft PR: `teamleaderleo/codex#130`
- Compare: one commit, exactly three files, `+301/-1`
- Upstream-contact authority: `none`

## Complete changed-file fence

1. `codex-rs/core/src/client.rs`
2. `codex-rs/core/tests/suite/agent_websocket.rs`
3. `codex-rs/core/tests/suite/client_websockets.rs`

No workflow, publisher, Fieldwork, manifest, lock, generated, snapshot, planner, or tool-registration file appears in the source diff.

## Complete-diff self-review

Review ID `4834209535` is attached to `teamleaderleo/codex#130` and pinned to exact head `9fd4ba575de8dd77bc411362256591ce9e7d8c82`.

Result: no source blocker found.

Findings:

- The predicate is limited to the first non-warmup Responses Lite request after an untraced warmup response.
- Clearing `last_response_rx` prevents the setup response ID from becoming the generated-turn predecessor and leaves serialization to the established full-request path.
- The request-completion state assignment resets warmup provenance after generation, allowing later generated responses to participate in ordinary incremental continuation.
- Existing reconnect logic clears every relevant response-chain field.
- The two client controls and full-agent control cover full first generation, post-generation continuation, and failed-first retry.
- Generic non-Lite warmup compression remains unchanged.

Reviewer eligibility: self-review only. Independent acceptance remains a separate evidence boundary.

## Public prior-art review

### Generic warmup transport

Merged `openai/codex#23581` intentionally retains a compressed first wire follow-up with a warmup `previous_response_id` while recording the complete logical request for rollout replay. Earlier `#22825` and `#23278` address unresolved or omitted untraced warmup parents in trace/replay.

Review consequence: any broad removal of warmup chaining would conflict with established generic behavior. The candidate avoids that conflict through the `use_responses_lite` predicate.

### Responses Lite request form

Merged `openai/codex#27946` moves Lite tools and instructions into input items. The complete input sequence therefore carries the Lite request identity.

Review consequence: the candidate has a transport-specific reason to send a complete first generated Lite request, and the full-first assertion is stronger than a generic trace-only repair.

### Duplicate result

Searches on 2026-08-01 covered:

- `Responses Lite`;
- `prewarm` and WebSocket warmup;
- `previous_response_id`;
- the three candidate test names;
- current open and closed Codex pull requests and issues.

No equivalent public implementation was found. The related public work either establishes generic warmup compression, introduces the Lite input-item contract, or changes adjacent metadata/tools/image behavior.

## Current-source staleness review

The previous parent was `670f69416bf91c5dfd8b58669e78050b584ff053`. Public main advanced by five commits to `ee0247f95a6fe2b094ba2253d82cae2a2b4c2dff` before this review.

The five commits changed app-server, protocol, realtime, plugin, request-user-input, hooks, exec-server, and related files. They did not change any of the three unit files. The candidate was replayed as one clean commit on the newer exact parent.

## Claims requiring independent judgment

| Claim | Current evidence | Reviewer question |
| --- | --- | --- |
| Lite setup response should not own first generated history | Lite input-item contract, lifecycle analysis, outbound JSON controls | Is any provider contract known to require first-generation chaining to `generate=false` Lite warmup? |
| The stream method owns the correction | all relevant state and serializer choices meet at this boundary | Is there a narrower response-provenance owner that would avoid clearing the receiver here? |
| Clearing the receiver fully severs warmup authority | surrounding source and reconnect reset logic | Can another field reintroduce the warmup response ID after this branch? |
| One complete first Lite request is acceptable | existing full serializer; later continuation control | Is there a documented Lite size/cache limit that makes the retransmission unsafe? |
| Stack result is a harness discriminator | isolated client pass; default/16-MiB historical agent split | Does the fresh exact-head run preserve the same classification? |

## Current exact execution

Execution-only PR: `teamleaderleo/codex#135`

- source base: `ee0247f95a6fe2b094ba2253d82cae2a2b4c2dff`
- source head: `9fd4ba575de8dd77bc411362256591ce9e7d8c82`
- carrier head: `fb77d59b2f5d07cebee889851a476ebab57c9e45`
- workflow run: `30690825055`
- job: `91345120846`

Required markers:

- `FIELDWORK_LITE_CURRENT_SOURCE_FENCE=3/3`
- `FIELDWORK_LITE_CURRENT_FORMAT=PASS`
- `FIELDWORK_LITE_CURRENT_CLIENT_EXACT=2/2`
- `FIELDWORK_LITE_CURRENT_AGENT=default:<status>;large:0`
- `FIELDWORK_LITE_CURRENT_CORE_RAISED_STACK=PASS`
- `FIELDWORK_LITE_CURRENT_FIX=PASS`
- `FIELDWORK_LITE_CURRENT_WORKTREE=CLEAN`

At this packet revision the job is queued for a hosted runner; this is an execution dependency, not a reason to abandon or widen the unit.

## Source cleanliness checklist

- [x] Direct one-commit child of the exact inspected public-source parent.
- [x] Exactly three intended source/test files.
- [x] No Fieldwork-only machinery in the source diff.
- [x] No generated or dependency churn.
- [x] Complete diff read at exact head.
- [x] Relevant generic warmup and Lite request-form prior art reviewed.
- [x] Duplicate search refreshed on 2026-08-01.
- [x] Complete-diff self-review recorded on the source PR.
- [ ] Exact-head execution receipt complete.
- [ ] Independent reviewer acceptance recorded.

## Current reviewer disposition

`REPAIR`

Reason: no source defect is known; the packet is continuing through the exact-head execution gate. Promotion will be reconsidered from the actual run receipt rather than from repository-wide or queue-state noise.

Clearing condition:

1. finish the exact execution run and classify every failed step;
2. repair any source-attributable failure and rerun;
3. transfer the receipt to PR `#130` and this packet;
4. record independent acceptance before public filing.

Public upstream interaction: `none`.
