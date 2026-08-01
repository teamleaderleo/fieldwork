# Unit 09 — Add opt-in SSE keep-alive comments to AI SDK UI streams

## In simple words

AI SDK UI responses can remain silent before their first application chunk and during long idle periods. Some HTTP servers and reverse proxies wait for a body byte before flushing the response or close a connection after a long silent interval. The owned candidate adds optional SSE comments only to the client-facing branch, leaving canonical UI data and persisted SSE bytes unchanged.

The technical direction is demonstrated and the owned candidate passes its complete fork CI. A current public issue and pull request now cover the same API and repair family. A second submission would duplicate active upstream work. This unit is therefore retained as independent validation and source review, including two edge controls the public pull request currently lacks.

## Current disposition

`SUPERSEDED — validation only`

Last verified: `2026-08-01`  
Worker: `GPT-5.6 Thinking`  
Priority-zero parent: [`teamleaderleo/fieldwork#435`](https://github.com/teamleaderleo/fieldwork/issues/435)  
Upstream contact authorized: `no`

## Contribution

- Target project: `vercel/ai`
- Proposed upstream destination: `vercel/ai:main`
- Historical proposed title: `fix(ai): add keepAliveMs option to UI message stream responses`
- Contribution synopsis: add optional immediate and idle SSE comments after the canonical persistence tee, propagate `keepAliveMs` through Fetch, Node, `streamText`, and agent helpers, and preserve disabled behavior and canonical persistence bytes.
- Work class: `upstream-fork research; superseded candidate retained as validation`

## Exact identities

- Public upstream base inspected: [`e84b8bc8154030cdb7469b0e0b8cd8b9354f19a0`](https://github.com/vercel/ai/commit/e84b8bc8154030cdb7469b0e0b8cd8b9354f19a0)
- Owned target fork: [`teamleaderleo/ai`](https://github.com/teamleaderleo/ai)
- Canonical source branch: [`fieldwork/ui-message-stream-keepalive`](https://github.com/teamleaderleo/ai/tree/fieldwork/ui-message-stream-keepalive)
- Canonical source head: [`b4b572631f6f288f296d1dcbb6d69e5e848cd9fb`](https://github.com/teamleaderleo/ai/commit/b4b572631f6f288f296d1dcbb6d69e5e848cd9fb)
- Historical source base: [`2b872b0db3769decf69945830c66a897c1e37347`](https://github.com/teamleaderleo/ai/commit/2b872b0db3769decf69945830c66a897c1e37347)
- Owned candidate PR: [`teamleaderleo/ai#4`](https://github.com/teamleaderleo/ai/pull/4)
- Public replacement issue: [`vercel/ai#17805`](https://github.com/vercel/ai/issues/17805)
- Public replacement PR: [`vercel/ai#17921`](https://github.com/vercel/ai/pull/17921) at [`21cd681724103701c3596770d7252a7ef0ad18db`](https://github.com/vercel/ai/commit/21cd681724103701c3596770d7252a7ef0ad18db)
- Fieldwork packet branch: [`p0/435-unit-09-vercel-ai-ui-stream-keepalive`](https://github.com/teamleaderleo/fieldwork/tree/p0/435-unit-09-vercel-ai-ui-stream-keepalive/upstream/packets/09-vercel-ai-ui-stream-keepalive)
- Exact packet head: published in the latest unit-09 handoff on `teamleaderleo/fieldwork#435`
- Execution carrier: [`teamleaderleo/ai#6`](https://github.com/teamleaderleo/ai/pull/6), closed without merge at `e89ff00f9f9a0a3badc8a249562a27cc88107114`
- Superseded formatter and predecessor generations: `88849192b0b235ef79cc6d0fb1aaa9b9a17e98b5`, `7c8b95b12e7a47e0f614ff949b645e546488eea7`, `bf3942cd1b615baa43fadcb27388a6911c0c5390`, `b0bbcf29aec186014ddd05dc05194da0a5b8a114`

## Current code and tests

### Product code

- [`create-sse-keep-alive-stream.ts`](https://github.com/teamleaderleo/ai/blob/b4b572631f6f288f296d1dcbb6d69e5e848cd9fb/packages/ai/src/ui-message-stream/create-sse-keep-alive-stream.ts) — validates the interval, emits opening and idle comments, owns one pending source read, respects downstream demand, and retires timer work on every terminal path.
- [`create-ui-message-stream-response.ts`](https://github.com/teamleaderleo/ai/blob/b4b572631f6f288f296d1dcbb6d69e5e848cd9fb/packages/ai/src/ui-message-stream/create-ui-message-stream-response.ts) — validates before lock/tee/callback and wraps only the client branch after persistence separation.
- [`pipe-ui-message-stream-to-response.ts`](https://github.com/teamleaderleo/ai/blob/b4b572631f6f288f296d1dcbb6d69e5e848cd9fb/packages/ai/src/ui-message-stream/pipe-ui-message-stream-to-response.ts) — applies the same transport behavior to Node responses.
- [`ui-message-stream-response-init.ts`](https://github.com/teamleaderleo/ai/blob/b4b572631f6f288f296d1dcbb6d69e5e848cd9fb/packages/ai/src/ui-message-stream/ui-message-stream-response-init.ts) — exposes the optional public API.

### Target-native tests

- [`create-ui-message-stream-response-keep-alive.test.ts`](https://github.com/teamleaderleo/ai/blob/b4b572631f6f288f296d1dcbb6d69e5e848cd9fb/packages/ai/src/ui-message-stream/create-ui-message-stream-response-keep-alive.test.ts) — opening/idle/reset behavior, canonical completion, persistence isolation, invalid-option ordering, cancellation independence, and 100-cycle timer/cancel soak.
- [`pipe-ui-message-stream-to-response-keep-alive.test.ts`](https://github.com/teamleaderleo/ai/blob/b4b572631f6f288f296d1dcbb6d69e5e848cd9fb/packages/ai/src/ui-message-stream/pipe-ui-message-stream-to-response-keep-alive.test.ts) — Node helper output and pre-side-effect validation.
- [`stream-text-ui-response-keep-alive.test.ts`](https://github.com/teamleaderleo/ai/blob/b4b572631f6f288f296d1dcbb6d69e5e848cd9fb/packages/ai/src/generate-text/stream-text-ui-response-keep-alive.test.ts) — `streamText` propagation.
- [`create-agent-ui-stream-response-keep-alive.test.ts`](https://github.com/teamleaderleo/ai/blob/b4b572631f6f288f296d1dcbb6d69e5e848cd9fb/packages/ai/src/agent/create-agent-ui-stream-response-keep-alive.test.ts) and [`pipe-agent-ui-stream-to-response-keep-alive.test.ts`](https://github.com/teamleaderleo/ai/blob/b4b572631f6f288f296d1dcbb6d69e5e848cd9fb/packages/ai/src/agent/pipe-agent-ui-stream-to-response-keep-alive.test.ts) — agent-helper propagation.

### Required generated or dependency files

- Patch changeset: [`.changeset/ui-stream-keep-alive.md`](https://github.com/teamleaderleo/ai/blob/b4b572631f6f288f296d1dcbb6d69e5e848cd9fb/.changeset/ui-stream-keep-alive.md)
- Dependency or lockfile changes: `not applicable`
- Temporary workflow files on canonical source head: `none`

## Changed-file fence

The owned candidate contains exactly 13 files: one changeset, one reference document, one keep-alive implementation, six public-helper source/type changes, and five focused tests. The exact list and roles are recorded in [`REVIEW.md`](./REVIEW.md).

## Evidence summary

| Claim | Evidence class | Exact receipt | Limit |
| --- | --- | --- | --- |
| Optional comments preserve disabled behavior and persistence bytes | `target-executed` | CI `30592239115` at `b4b57263...` | Owned fork gate |
| Opening bytes reach a real Node client before UI data | `integration-executed` | run `30506032517`, job `90755875694` at `7c8b95b...` | Self-hosted Node server |
| Periodic comments preserve a connection past a 450 ms controlled idle cutoff | `integration-executed` | same carrier, 1,050 ms source silence and 75 ms comments | Synthetic forwarding proxy |
| Repeated open/cancel retires timers and issues one source cancel | `full-gate` for the named CI | 100-iteration test in CI `30592239115` | Fake-timer target test |
| Repository format, type, build, docs, examples, and AI test shards pass | `full-gate` | CI `30592239115`; Verify Changesets `30592239084` | Fork CI; no named production proxy matrix |
| Public replacement covers SDK parser invisibility and broader docs | `source-read` and contributor-reported execution | public PR `#17921` at `21cd6817...` | Hosted public runs are `action_required`; no review yet |

## Packet navigation

- [Deep dive](./DEEP_DIVE.md)
- [Approaches](./APPROACHES.md)
- [Tests and receipts](./TESTS.md)
- [Upstream issue result](./UPSTREAM_ISSUE.md)
- [Upstream pull-request result](./UPSTREAM_PR.md)
- [Review and human inspection guide](./REVIEW.md)

## Duplicate and prior-art result

- Search date: `2026-08-01`
- Current public issue checked: [`vercel/ai#17805`](https://github.com/vercel/ai/issues/17805)
- Current public pull request checked: [`vercel/ai#17921`](https://github.com/vercel/ai/pull/17921)
- Equivalent implementation found: `yes, with two material edge differences`
- Relationship to prior work: `superseded for submission; independent validation and review input`

The public pull request uses the same `keepAliveMs` API, client-only post-tee comments, single outstanding read, helper propagation, parser compatibility test, documentation, and Node example. The owned candidate adds two controls that remain useful during review:

1. validate before locking, teeing, or calling `consumeSseStream`; the public pull request validates inside the wrapper after the tee/callback path;
2. client cancellation requests branch cancellation without awaiting the tee branch's cancellation promise; the public pull request returns `reader.cancel(reason)`, which may remain pending while an independent persistence branch remains active.

## Remaining work

Complete only if this unit is deliberately reopened:

1. re-check the public issue, pull request, and current `main`;
2. confirm whether upstream incorporated pre-tee validation and persistence-branch-independent client cancellation;
3. revive or rebase the owned source only after the public replacement closes without an equivalent accepted fix and explicit upstream-contact authority is granted.

## Blockers and limits

- A live directly overlapping public pull request occupies the upstream submission lane.
- Public PR hosted CI and changeset workflows are `action_required`; its author reports local package tests, checks, typecheck, parser coverage, and a Node example.
- Public PR has no maintainer review at the inspected head.
- Representative production proxy evidence comes from the public reporter's stated deployment and the owned controlled Node/proxy carrier; Fieldwork did not access that production system.
- Upstream contact remains unauthorized.

## Latest handoff

State: `SUPERSEDED — validation only`  
Exact source head: `b4b572631f6f288f296d1dcbb6d69e5e848cd9fb`  
Exact packet head: latest unit-09 handoff on `teamleaderleo/fieldwork#435`  
Tests: full owned-fork CI and changeset verification passed; real Node and controlled proxy carrier passed  
Temporary machinery remaining: no temporary files on the source head; closed carrier branch/PR remains as historical evidence  
Next worker action: check the public replacement for the two retained edge controls before any revival decision  
Public upstream interaction: `none`
