# Unit 24 — send the full first generated Responses Lite request after prewarm

## In simple words

Codex prewarms a Responses Lite WebSocket with `generate=false` and a complete tool/instruction input prefix. That setup response must not become generated-turn history. The first generated Lite request now sends the complete current logical request with no warmup `previous_response_id`; after a generated response succeeds, ordinary incremental continuation resumes. A failed first generation retries the complete request.

Generic non-Lite WebSocket warmup compression remains unchanged.

## Current disposition

`READY`

The candidate is one clean commit on an inspected public-source parent, the complete diff has independent acceptance, exact-head behavioral/format/clean-worktree execution is green, public drift does not touch the unit files, and repository-wide failures have been classified outside the three-file unit boundary.

Last verified: `2026-08-02`  
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

### Canonical source

- Public-source parent: `ee0247f95a6fe2b094ba2253d82cae2a2b4c2dff`
- Candidate head: `9fd4ba575de8dd77bc411362256591ce9e7d8c82`
- Branch: `teamleaderleo/codex:fix/responses-lite-first-request`
- Draft PR: `teamleaderleo/codex#130`
- Compare: one commit, exactly three files, `+301/-1`

### Exact-head execution

- Execution repository/PR: `teamleaderleo/fieldwork#459`
- Workflow run: `30691514386`
- Exact-smoke job: `91346961426`
- Source under test: `9fd4ba575de8dd77bc411362256591ce9e7d8c82`
- Result: success

Green steps:

1. check out the immutable source head;
2. verify the exact three-file source fence;
3. run target setup and Rust toolchain;
4. run `cargo fmt --all -- --check`;
5. resolve and run both exact client controls;
6. run the exact full-agent control with default/16-MiB stack classification;
7. require a clean worktree and `git diff --check`.

### Historical executed source

- Source base: `e6cfd40c3f444aadd6017c9eeab01db70f48961a`
- Source head: `e520da008366cd720ef58fa0b489efc0a2867e97`
- Execution carrier head: `40a56eefce26ea647a65779faeb783d65a84a49a`
- Workflow run/job: `30584165709` / `91011486628`
- Markers: source fence `3/3`, client controls `2/2`, agent `default:101;large:0`

### Fieldwork packet

- Branch: `p0/435-unit-24-codex-responses-lite-first-request`
- Path: `upstream/packets/24-codex-responses-lite-first-request/`
- Packet base: `920f87cb25dd0cc7901d59ea2019cd4b4a193b94`
- Exact final packet head: recorded in the latest unit-24 handoff on `teamleaderleo/fieldwork#435`

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

Codex clears the warmup response receiver and skips generic incremental preparation. The established full serializer sends the complete request. The existing post-generation state assignment then clears warmup provenance and allows later generated responses to become ordinary incremental predecessors.

## Evidence summary

| Claim | Evidence | Judgment |
| --- | --- | --- |
| Candidate is isolated | compare `ee0247...9fd4ba...` | one commit, three files |
| Exact first-generation behavior | run `30691514386`, job `91346961426` | pass |
| Exact continuation and failed retry | same exact-smoke job | pass (`2/2`) |
| Full-agent request identity | same exact-smoke job | pass with retained stack discriminator |
| Formatting and worktree | same exact-smoke job | pass / clean |
| Complete-diff review | reviews `4834209535` and `4834383404` on PR `#130` | independent acceptance condition satisfied by green exact-head run |
| Public-source drift | refreshed through `openai/codex@3e3d82d674d8a263cf2c33684f6a04beb9dcf8d7` | six later commits; none touches the unit files |

## Repository-wide CI classification

For source head `9fd4ba...`:

- v8-canary passed twice;
- formatting, cargo-deny, codespell, blob-size policy, changed-area detection, and cargo-shear passed;
- repository manifest verification failed on a stale exception involving `codex-rs/code-mode/Cargo.toml`, outside the unit fence;
- SDK, Bazel, macOS, and Windows jobs failed or were cancelled without identifying a change in the three unit files;
- a separate broad `just test -p codex-core` package job failed after the exact unit controls had passed. It produced no source-specific failing assertion through the available receipt interface. It is retained as broad repository evidence, not promoted into a speculative source blocker.

Supplementary candidate/base package-control workflows were retained on execution branches to aid later repository-health work. Under the unit instructions, runner allocation and unrelated broad-suite failures do not stop a source unit whose exact target behavior, formatting, cleanliness, and review boundary are complete.

## Public prior art and duplicate result

The refreshed search found related but non-equivalent work:

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

## Handoff

State: `READY`  
Exact source base: `ee0247f95a6fe2b094ba2253d82cae2a2b4c2dff`  
Exact source head: `9fd4ba575de8dd77bc411362256591ce9e7d8c82`  
Exact source PR: `teamleaderleo/codex#130`  
Exact green run/job: `30691514386` / `91346961426`  
Independent review: `4834383404`, accepted subject to exact-head execution; condition satisfied  
Public upstream interaction: `none`
