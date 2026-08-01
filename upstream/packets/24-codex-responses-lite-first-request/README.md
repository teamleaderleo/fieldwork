# Unit 24 — send the full first generated Responses Lite request after prewarm

## In simple words

Codex prewarms a Responses Lite WebSocket by sending its tool/instruction input prefix with `generate=false`. That operation prepares transport and prefix state; it is not a generated turn.

Generic WebSocket requests may intentionally continue from warmup state with a compressed delta. Responses Lite needs a narrower rule because its complete tools and instructions live in input items: the first generated Lite request ends the warmup response chain, sends the complete current logical input with no warmup `previous_response_id`, and then resumes ordinary incremental reuse from the first generated response. A failed first generation retries the complete request.

## Current disposition

`REPAIR`

The source has been rebased to the current inspected public-source parent, the complete diff has been reviewed, public prior art and duplicate searches have been refreshed, and a clean execution-only workflow is queued against the immutable current source. The disposition will be reconsidered from that exact run receipt rather than from unrelated repository-wide failures or runner queue state.

Last verified: `2026-08-01`  
Worker: `GPT-5.6 Thinking`  
Priority-zero parent: `teamleaderleo/fieldwork#435`  
Upstream contact authorized: `no`

## Contribution

- Target project: `openai/codex`
- Proposed upstream destination: `openai/codex:main`
- Proposed title: `core: send full first Responses Lite turn after prewarm`
- Work class: `upstream-fork research`
- Scope: one request-state transition and three target-native WebSocket controls

## Exact identities

### Current canonical source

- Public-source parent: `ee0247f95a6fe2b094ba2253d82cae2a2b4c2dff`
- Candidate head: `9fd4ba575de8dd77bc411362256591ce9e7d8c82`
- Branch: `teamleaderleo/codex:fix/responses-lite-first-request`
- Draft PR: `teamleaderleo/codex#130`
- Compare: one commit, exactly three files, `+301/-1`

### Current execution carrier

- Execution-only PR: `teamleaderleo/codex#135`
- Carrier head: `fb77d59b2f5d07cebee889851a476ebab57c9e45`
- Workflow run: `30690825055`
- Job: `91345120846`
- Status at this packet revision: queued

### Historical executed source

- Source base: `e6cfd40c3f444aadd6017c9eeab01db70f48961a`
- Source head: `e520da008366cd720ef58fa0b489efc0a2867e97`
- Execution carrier head: `40a56eefce26ea647a65779faeb783d65a84a49a`
- Workflow run/job: `30584165709` / `91011486628`

### Fieldwork packet

- Branch: `p0/435-unit-24-codex-responses-lite-first-request`
- Path: `upstream/packets/24-codex-responses-lite-first-request/`
- Packet base: `920f87cb25dd0cc7901d59ea2019cd4b4a193b94`
- Exact packet head: recorded in the latest unit-24 handoff on `teamleaderleo/fieldwork#435`

## Changed-file fence

| Path | Role |
| --- | --- |
| `codex-rs/core/src/client.rs` | production response-chain transition |
| `codex-rs/core/tests/suite/agent_websocket.rs` | full-agent first generated request identity |
| `codex-rs/core/tests/suite/client_websockets.rs` | continuation and failed-first retry controls |

No workflow, publisher, Fieldwork, manifest, lock, generated, snapshot, planner, or tool-registration file appears in the canonical source diff.

## Selected behavior

At the first request where all three facts hold:

```text
not warmup
Responses Lite enabled
last response came from untraced warmup
```

Codex clears the warmup response receiver and skips generic incremental request preparation. The existing full serializer sends the complete request. After generation, the existing state assignment resets warmup provenance and later turns continue incrementally from generated responses.

## Evidence summary

| Claim | Evidence | Current limit |
| --- | --- | --- |
| Candidate is one clean commit and three files | compare `ee0247...9fd4ba...` | source identity only |
| Public drift did not touch the unit files | compare `670f694...ee0247...` | five inspected commits |
| Historical exact source fence | `FIELDWORK_LITE_SOURCE_FENCE=3/3` | historical source `e520da...` |
| Historical client behavior | `FIELDWORK_LITE_CLIENT_EXACT=2/2` | historical source `e520da...` |
| Historical full-agent behavior | `FIELDWORK_LITE_AGENT=default:101;large:0` | default worker-stack overflow |
| Complete current diff review | owned PR `#130`, review ID `4834209535` | self-review, not independent acceptance |
| Fresh current execution | owned PR `#135`, run `30690825055`, job `91345120846` | queued at this revision |

## Public prior art and duplicate result

The refreshed 2026-08-01 search found related but non-equivalent work:

- merged `openai/codex#23581` intentionally preserves generic compressed wire reuse after untraced warmup while recording the complete logical request for trace replay;
- merged `openai/codex#27946` moves Responses Lite tools and instructions into input items;
- earlier trace changes `#22825` and `#23278` address unresolved or omitted warmup parents;
- adjacent Lite PRs cover headers, tools, metadata, images, and normalized names.

No public implementation was found that ends the warmup response chain only for the first generated Responses Lite request while preserving later continuation and failed-first full retry.

## Packet navigation

- [Deep dive](./DEEP_DIVE.md)
- [Approaches](./APPROACHES.md)
- [Tests and receipts](./TESTS.md)
- [Upstream issue draft](./UPSTREAM_ISSUE.md)
- [Upstream pull-request draft](./UPSTREAM_PR.md)
- [Review guide](./REVIEW.md)

## Current execution gate

Execution-only PR `#135` verifies:

1. immutable source parent/head and exact source fence;
2. formatting;
3. both exact client controls;
4. full-agent default/16-MiB stack discriminator;
5. `just test -p codex-core` with a raised worker stack;
6. `just fix -p codex-core`;
7. clean worktree and diff.

A failure is to be inspected, classified, and repaired if attributable to the source. Setup, runner, or repository-baseline failures are recorded and the unit continues through another bounded execution attempt.

## Current handoff

State: `REPAIR`  
Exact source base: `ee0247f95a6fe2b094ba2253d82cae2a2b4c2dff`  
Exact source head: `9fd4ba575de8dd77bc411362256591ce9e7d8c82`  
Exact source PR: `teamleaderleo/codex#130`  
Exact execution carrier: `teamleaderleo/codex#135@fb77d59b2f5d07cebee889851a476ebab57c9e45`  
Exact execution run/job: `30690825055` / `91345120846`  
Tests: historical source fence `3/3`, client controls `2/2`, agent `default:101;large:0`; current exact run queued  
Review: complete-diff self-review found no source blocker; independent acceptance absent  
Public upstream interaction: `none`
