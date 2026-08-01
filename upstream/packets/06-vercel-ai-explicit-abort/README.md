# Unit 06 — fix(ai): make explicit abort settlement nonblocking

## In simple words

`streamText` can be waiting for another provider chunk when a caller aborts the operation. The retained candidate makes the caller abort claim the terminal result once, rejects public result state, closes the outward abort stream, requests provider cancellation, and makes later provider values or errors yield to that abort.

The candidate is materialized on a clean owned-fork branch from current public main. Continued investigation corrected one packet premise: the pre-registration `await languageModelStream.cancel(reason)` already awaits a request-level cancellation promise. Native Web Streams modeling showed that this promise settles after forwarding cancellation while provider cleanup remains pending, and provider cleanup rejection is contained by the existing pipe chain. The production source therefore remains unchanged. A target-native regression for those exact semantics is now queued in ordinary repository CI.

## Current disposition

`EXECUTE`

Last verified: `2026-08-01`  
Worker: `OpenAI`  
Priority-zero parent: [`teamleaderleo/fieldwork#435`](https://github.com/teamleaderleo/fieldwork/issues/435)  
Upstream contact authorized: `no`

## Contribution

- Target project: `vercel/ai`
- Proposed upstream destination: `vercel/ai` `main`
- Proposed title: `fix(ai): make explicit abort settlement nonblocking`
- Contribution synopsis: make explicit operation abort settle public and outward state independently of observability callbacks and later provider outcomes, while preserving consumer-scoped reader cancellation.
- Work class: `upstream-fork research`

## Exact identities

- Public upstream base inspected: [`e84b8bc8154030cdb7469b0e0b8cd8b9354f19a0`](https://github.com/vercel/ai/commit/e84b8bc8154030cdb7469b0e0b8cd8b9354f19a0)
- Owned target fork: [`teamleaderleo/ai`](https://github.com/teamleaderleo/ai)
- Canonical source branch: `upstream/06-explicit-abort-nonblocking`
- Canonical source head: [`92079da650430d8376a7eeef2436910b44393411`](https://github.com/teamleaderleo/ai/commit/92079da650430d8376a7eeef2436910b44393411)
- Target-native cancellation-regression branch: `fieldwork/06-explicit-abort-cancel-boundary`
- Target-native cancellation-regression head: [`7ae1794889d9dd22eeef9faf4f33d01330c0918d`](https://github.com/teamleaderleo/ai/commit/7ae1794889d9dd22eeef9faf4f33d01330c0918d)
- Target-native cancellation-regression PR: [`teamleaderleo/ai#12`](https://github.com/teamleaderleo/ai/pull/12)
- Exact CI run: `30691171818`
- Fieldwork packet branch: `p0/435-unit-06-vercel-ai-explicit-abort`
- Fieldwork packet head: exact current head is recorded in the latest #435 handoff
- Materialization carrier: [`teamleaderleo/ai#8`](https://github.com/teamleaderleo/ai/pull/8), merged
- Historical source surfaces: [`teamleaderleo/ai#1`](https://github.com/teamleaderleo/ai/pull/1) characterization/provenance; [`teamleaderleo/ai#7`](https://github.com/teamleaderleo/ai/pull/7) stacked repair and execution receipts
- Superseded execution carriers: `teamleaderleo/ai#9`, `#10`, and `#11`

## Current code and tests

### Product code

- [`stream-text.ts`](https://github.com/teamleaderleo/ai/blob/92079da650430d8376a7eeef2436910b44393411/packages/ai/src/generate-text/stream-text.ts) — independent abort observation, root rejection, outward settlement before callbacks, terminal arbitration, and direct pre-registration provider cancellation.

### Target-native tests

- [`stream-text-explicit-abort.test.ts`](https://github.com/teamleaderleo/ai/blob/92079da650430d8376a7eeef2436910b44393411/packages/ai/src/generate-text/stream-text-explicit-abort.test.ts) — pending reads, roots and derived getters, pre-abort, local tools, provider cancellation, callback cardinality.
- [`stream-text-explicit-abort-races.test.ts`](https://github.com/teamleaderleo/ai/blob/92079da650430d8376a7eeef2436910b44393411/packages/ai/src/generate-text/stream-text-explicit-abort-races.test.ts) — callback stall, provider-error race, and multi-consumer abort cardinality.
- [`stream-text.test.ts`](https://github.com/teamleaderleo/ai/blob/92079da650430d8376a7eeef2436910b44393411/packages/ai/src/generate-text/stream-text.test.ts) — upstream-style result-promise regression.
- [`stream-language-model-call-cancellation.test.ts`](https://github.com/teamleaderleo/ai/blob/7ae1794889d9dd22eeef9faf4f33d01330c0918d/packages/ai/src/generate-text/stream-language-model-call-cancellation.test.ts) — exact cancellation reason, pending provider cleanup, and rejected provider cleanup.

### Required generated or dependency files

- [`.changeset/slow-streams-abort.md`](https://github.com/teamleaderleo/ai/blob/92079da650430d8376a7eeef2436910b44393411/.changeset/slow-streams-abort.md)

## Changed-file fence

### Canonical production candidate

| Path | Role | Keep upstream? |
| --- | --- | --- |
| `.changeset/slow-streams-abort.md` | release note | yes |
| `packages/ai/src/generate-text/stream-text.ts` | production | yes |
| `packages/ai/src/generate-text/stream-text.test.ts` | regression | yes |
| `packages/ai/src/generate-text/stream-text-explicit-abort.test.ts` | regression | yes, subject to consolidation |
| `packages/ai/src/generate-text/stream-text-explicit-abort-races.test.ts` | regression | yes, subject to consolidation |

### Exact-semantics execution candidate

| Path | Role | Keep upstream? |
| --- | --- | --- |
| `packages/ai/src/generate-text/stream-language-model-call-cancellation.test.ts` | cancellation-promise regression | yes, subject to consolidation |

## Evidence summary

| Claim | Evidence class | Exact receipt | Limit |
| --- | --- | --- | --- |
| Public main still lacks independent abort settlement | `source-read` | public base `e84b8bc…` | one exact revision |
| Callback-independent settlement and abort/error arbitration pass focused tests | `target-executed` | runs `30506931561` / job `90758627827` and `30507215391` / job `90759478304` | executed on prior exact repair diff, before current-main materialization |
| Clean current-main candidate exists | `source-read` | source head `92079da…` | canonical exact-head CI still required |
| Returned model-call stream cancellation settles while provider cleanup remains pending | `model-executed` | `receipts/2026-08-01-provider-cancel-promise-model.md` | native Web Streams model; package execution pending |
| Target-native cancellation semantics are encoded | `target-test-prepared` | PR #12 head `7ae179…`, CI `30691171818` | run queued |

## Packet navigation

- [Deep dive](./DEEP_DIVE.md)
- [Approaches](./APPROACHES.md)
- [Tests and receipts](./TESTS.md)
- [Provider-cancel promise receipt](./receipts/2026-08-01-provider-cancel-promise-model.md)
- [Upstream issue draft](./UPSTREAM_ISSUE.md)
- [Upstream pull-request draft](./UPSTREAM_PR.md)
- [Review and human inspection guide](./REVIEW.md)

## Duplicate and prior-art result

- Search date: `2026-08-01`
- Current upstream issue: [`vercel/ai#15430`](https://github.com/vercel/ai/issues/15430)
- Current upstream implementation: [`vercel/ai#16852`](https://github.com/vercel/ai/pull/16852), open at `0ef2ae9a7f143d90972b4ff217046e0b04ea67f1`
- Separate mid-body provider-error candidate: [`vercel/ai#15495`](https://github.com/vercel/ai/pull/15495)
- Equivalent implementation found: `partial`
- Relationship to prior work: the owned candidate extends the maintainer-authored pending-read fix with broader characterization, callback-independent settlement, deterministic post-abort arbitration, multi-consumer controls, and registration-gap cancellation. Public contribution should update or replace the existing PR only with maintainer direction.

## Remaining work

Complete in this order:

1. Finish ordinary repository CI run `30691171818` on exact test head `7ae1794889d9dd22eeef9faf4f33d01330c0918d`; classify every failure against the intended assertions.
2. Merge the cancellation regression into `upstream/06-explicit-abort-nonblocking`, then obtain ordinary repository CI on the resulting exact canonical head.
3. Review the complete canonical diff, retire temporary carrier branches and trigger files, and decide whether public delivery belongs as a revision of upstream PR #16852 or an issue/maintainer handoff.

## Blockers and limits

- Exact-head target-native CI remains queued.
- Canonical source head `92079da…` has historical matching repair evidence and lacks a completed ordinary current-head CI receipt.
- Final independent acceptance remains absent.
- Abort reports termination; it cannot reverse an external tool side effect that already committed.
- Public upstream contact remains unauthorized.

## Latest handoff

State: `EXECUTE`  
Exact canonical source head: `92079da650430d8376a7eeef2436910b44393411`  
Exact test head: `7ae1794889d9dd22eeef9faf4f33d01330c0918d`  
Exact packet head: see latest #435 handoff  
Tests: prior matching repair diff passed 6 Node and 6 Edge tests plus type, format/lint, and diff checks; cancellation promise model passed on Node `v22.17.0`; exact target-native CI run `30691171818` is queued  
Temporary machinery remaining: superseded owned-fork carriers #9–#11 and their branches; canonical branch contains no workflow files  
Next worker action: inspect run `30691171818`, repair any exact assertion or harness failure, then merge the regression into the canonical branch  
Public upstream interaction: none
