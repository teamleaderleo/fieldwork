# Campaign 0010 Status

## In simple words

The runtime problem is proven and the owned application is protected. The workerd declaration candidate is credible, but its latest head has no current independent acceptance and no completed target-native focused receipt. This campaign is preserving the evidence and deciding whether the candidate deserves an upstream pull request.

- State: `submitted`
- Coordinator: Atlas / active Fieldwork session
- Parent issue: #230
- Programme: #15 — Web tooling and runtime correctness
- Target hub: #3 — Cloudflare Workers SDK ecosystem
- Primary code target: `cloudflare/workerd`
- Testbed: `teamleaderleo/stensibly`
- Canonical candidate: `teamleaderleo/workerd#1`
- Candidate branch: `research/issue-474-receiver-aware-types`
- Candidate head at materialization: `e7b15f8014e8ed49255d2f0c6774f0b3bfe1714a`
- Submitted upstream issue: [generated declarations omit receiver requirements](https://redirect.github.com/cloudflare/workerd/issues/6904)
- Upstream pull request: none
- New upstream contact authorized: no
- Last durable update: 2026-07-30

## Evidence state

| Claim | Evidence class | Current result |
| --- | --- | --- |
| workerd rejects unrelated receivers for Worker `fetch` | `integration-executed` | established in pinned native workerd |
| Bun and Node accept the same unrelated receiver | `integration-executed` | established; intentional compatibility boundary |
| the Stensibly wrapper prevents the production failure | `integration-executed` | merged in `teamleaderleo/stensibly#482` |
| TypeScript can model the direct receiver set | `model-executed` | established with TypeScript 5.8.3 |
| existing lint catches all receiver erasure | `model-executed` | disproved |
| the workerd candidate preserves receiver policy through overrides | `source-read` and focused fixture preparation | credible; exact-head target receipt outstanding |
| the current workerd head is accepted for upstream preparation | none | not established |

## Current blockers

1. The last visible independent review targeted `d08e2e968b6db600c220e2babe0a07befa728ba2`; the canonical head moved afterward.
2. Lint passed at `e7b15f8…`, while focused, Tests, Coverage, and CodSpeed workflows were cancelled.
3. No retained exact-head synthetic compiler receipt has been published for the final head.
4. Representative full generated-API compatibility remains bounded by fixtures rather than measured output.
5. The upstream issue has no maintainer response as of 2026-07-30.

## Next transition

Prepare a small exact-head model receipt, independently review the complete current diff, classify the cancelled native execution honestly, then choose `prepare patch`, `seek direction`, `publish finding`, or `negative result`.
