# Unit 24 — send the full first generated Responses Lite request after prewarm

## In simple words

Codex can prewarm a Responses Lite WebSocket by sending the model, reasoning settings, instructions, and tool-manifest prefix with `generate=false`. That response warms the connection; it does not represent a generated turn.

The retained client state treated the warmup response as the predecessor of the first generated request. The candidate ends that warmup response chain before generation. The first generated request therefore sends the complete current logical request with no warmup `previous_response_id`. After that generated response succeeds, ordinary incremental continuation resumes. A failed first generated request retries the same complete request without inheriting warmup state.

The source is now a clean one-commit, three-file child of public `openai/codex` revision `670f69416bf91c5dfd8b58669e78050b584ff053`. Historical exact-source execution passed the source fence and both focused client controls. The full-agent characterization reproduced a default Tokio worker-stack overflow and passed with a 16 MiB worker stack; that runner condition stays outside the product claim. Current-head blocking CI is running and contains repository-wide failures outside this unit's file fence. Fresh focused execution on the clean head remains the delivery gate.

## Current disposition

`REPAIR`

Last verified: `2026-08-01`  
Worker: `GPT-5.6 Thinking`  
Priority-zero parent: [`teamleaderleo/fieldwork#435`](https://github.com/teamleaderleo/fieldwork/issues/435)  
Upstream contact authorized: `no`

## Contribution

- Target project: `openai/codex`
- Proposed upstream destination: `openai/codex:main`
- Proposed title: `core: send full first Responses Lite turn after prewarm`
- Contribution synopsis: terminate the untraced Responses Lite warmup response chain before the first generated request, then prove full-first, incremental-continuation, and failed-first retry behavior with target-native WebSocket tests.
- Work class: `upstream-fork research`

## Exact identities

- Public upstream base inspected: [`670f69416bf91c5dfd8b58669e78050b584ff053`](https://github.com/openai/codex/commit/670f69416bf91c5dfd8b58669e78050b584ff053)
- Owned target fork: [`teamleaderleo/codex`](https://github.com/teamleaderleo/codex)
- Canonical source branch: [`fix/responses-lite-first-request`](https://github.com/teamleaderleo/codex/tree/fix/responses-lite-first-request)
- Canonical source head: [`2c3f21d38056d2d77215cd9dce820a680d11cfe8`](https://github.com/teamleaderleo/codex/commit/2c3f21d38056d2d77215cd9dce820a680d11cfe8)
- Canonical owned draft PR: [`teamleaderleo/codex#130`](https://github.com/teamleaderleo/codex/pull/130)
- Fieldwork packet branch: [`p0/435-unit-24-codex-responses-lite-first-request`](https://github.com/teamleaderleo/fieldwork/tree/p0/435-unit-24-codex-responses-lite-first-request/upstream/packets/24-codex-responses-lite-first-request)
- Fieldwork packet base: `920f87cb25dd0cc7901d59ea2019cd4b4a193b94`
- Fieldwork packet head: recorded in the latest continuation handoff on [`teamleaderleo/fieldwork#435`](https://github.com/teamleaderleo/fieldwork/issues/435), avoiding a stale self-reference inside the packet commit.
- Historical exact source: [`teamleaderleo/codex#87`](https://github.com/teamleaderleo/codex/pull/87), base `e6cfd40c3f444aadd6017c9eeab01db70f48961a`, head `e520da008366cd720ef58fa0b489efc0a2867e97`
- Historical execution carrier: [`teamleaderleo/codex#58`](https://github.com/teamleaderleo/codex/pull/58), head `40a56eefce26ea647a65779faeb783d65a84a49a`
- Earlier broad carrier: [`teamleaderleo/codex#23`](https://github.com/teamleaderleo/codex/pull/23)
- Internal transplant carrier: [`teamleaderleo/codex#129`](https://github.com/teamleaderleo/codex/pull/129), merged into the canonical branch
- Superseded source carriers: owned Codex PRs `#70`, `#79`, and `#87`

## Current code and tests

### Product code

- [`codex-rs/core/src/client.rs`](https://github.com/teamleaderleo/codex/blob/2c3f21d38056d2d77215cd9dce820a680d11cfe8/codex-rs/core/src/client.rs#L1609-L1631) — recognizes the first non-warmup Responses Lite request after untraced prewarm, clears the warmup response receiver, and sends a full request.

### Target-native tests

- [`agent_websocket.rs`](https://github.com/teamleaderleo/codex/blob/2c3f21d38056d2d77215cd9dce820a680d11cfe8/codex-rs/core/tests/suite/agent_websocket.rs) — full-agent request identity after startup prewarm.
- [`client_websockets.rs`](https://github.com/teamleaderleo/codex/blob/2c3f21d38056d2d77215cd9dce820a680d11cfe8/codex-rs/core/tests/suite/client_websockets.rs) — incremental continuation after the first generated response and full retry after first-generation failure.

### Required generated or dependency files

- `not applicable`

## Changed-file fence

| Path | Role | Keep upstream? |
| --- | --- | --- |
| `codex-rs/core/src/client.rs` | production | yes |
| `codex-rs/core/tests/suite/agent_websocket.rs` | regression | yes |
| `codex-rs/core/tests/suite/client_websockets.rs` | regression | yes |

The current compare is exactly one commit, three files, `+301/-1` from `670f69416bf91c5dfd8b58669e78050b584ff053` to `2c3f21d38056d2d77215cd9dce820a680d11cfe8`.

## Evidence summary

| Claim | Evidence class | Exact receipt | Limit |
| --- | --- | --- | --- |
| First generated Lite request severs warmup chain | source-read | current three-file diff on `2c3f21d...` | source proves control flow, not provider deployment behavior |
| Source fence contains exactly three intended files | target-executed | run `30584165709`, job `91011486628`, `FIELDWORK_LITE_SOURCE_FENCE=3/3` | executed on historical source `e520da...` |
| Both focused client controls pass | target-executed | same job, `FIELDWORK_LITE_CLIENT_EXACT=2/2` | executed on historical source `e520da...` |
| Full-agent request-identity assertion passes with larger worker stack | target-executed | same job, `FIELDWORK_LITE_AGENT=default:101;large:0` | default-stack overflow is a runner/runtime condition; current clean head still needs renewal |
| Current branch preserves the exact historical source patch | source-read | one-commit compare from `670f694...` to `2c3f21d...`; upstream drift did not touch the three files | current focused execution pending |

## Packet navigation

- [Deep dive](./DEEP_DIVE.md)
- [Approaches](./APPROACHES.md)
- [Tests and receipts](./TESTS.md)
- [Upstream issue draft](./UPSTREAM_ISSUE.md)
- [Upstream pull-request draft](./UPSTREAM_PR.md)
- [Review and human inspection guide](./REVIEW.md)

## Duplicate and prior-art result

- Search date: `2026-08-01`
- Current upstream issues/PRs checked: searches for `Responses Lite`, `prewarm`, `previous_response_id`, WebSocket warmup, and the candidate symbol/test names in `openai/codex`
- Equivalent implementation found: `no`
- Relationship to prior work: the owned broad carrier `#23` supplied early diagnostic evidence; `#87` is the exact historical source; `#58` supplied the exact execution receipt; planner/tool-exposure work linked from Fieldwork issues `#85` and `#239` is adjacent and excluded.

## Remaining work

Complete in this order:

1. Execute the two exact client tests and the full-agent request-identity test on `2c3f21d38056d2d77215cd9dce820a680d11cfe8`.
2. Run `just fmt`, `just fix -p codex-core`, and the focused `codex-core` test gate on the same source head, preserving any repository-wide failures as separate receipts.
3. Obtain independent complete-diff review on `teamleaderleo/codex#130`, then change the packet disposition to `READY` if the focused current-head evidence remains green.

## Blockers and limits

- Current-head focused tests have not completed on `2c3f21d...`.
- Blocking CI run `30674311295` includes a pre-existing manifest exception failure in `codex-rs/code-mode/Cargo.toml`, outside the changed-file fence, plus platform jobs that are red or still running.
- The default worker-stack full-agent run overflows; the exact same assertion passes at 16 MiB. That classification limits the ordinary full-agent receipt without rebutting the focused client controls.
- Current target contribution and AI-disclosure policy needs a fresh filing-time check; no repository-local `CONTRIBUTING.md` was present at the inspected revision.
- Public filing authority is absent.

## Latest handoff

State: `REPAIR`  
Exact source head: `2c3f21d38056d2d77215cd9dce820a680d11cfe8`  
Exact packet head: latest `p0/435-unit-24-codex-responses-lite-first-request` head recorded on issue `#435`  
Tests: historical exact source fence `3/3`; focused client controls `2/2`; full-agent `default:101;large:0`; current-head CI partial/red outside source fence; current-head focused tests pending  
Temporary machinery remaining: owned draft PR `#130`; historical carriers retained as receipts  
Next worker action: execute the three focused controls on `2c3f21d...` and attach the exact command/run receipt to `#130` and `#435`  
Public upstream interaction: `none`
