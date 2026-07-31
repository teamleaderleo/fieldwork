# Unit 06 — fix(ai): make explicit abort settlement nonblocking

## In simple words

`streamText` can be waiting for another provider chunk when a caller aborts the operation. The retained candidate makes the caller abort claim the terminal result once, rejects public result state, closes the outward abort stream, requests provider cancellation, and lets later provider values or errors yield to that abort.

The candidate is now materialized on a clean owned-fork branch from current public main. One concrete repair remains: the provider stream returned during the abort/registration gap is cancelled with an awaited promise. A provider `cancel()` that rejects or never settles can keep the internal setup task alive. That cancellation must become a handled request that cannot delay release, with hostile regression controls.

## Current disposition

`REPAIR`

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
- Fieldwork packet branch: `p0/435-unit-06-vercel-ai-explicit-abort`
- Fieldwork packet head: exact final head is recorded in the latest #435 handoff
- Execution carriers: [`teamleaderleo/ai#8`](https://github.com/teamleaderleo/ai/pull/8) materialized the combined candidate onto the clean branch
- Superseded carriers: [`teamleaderleo/ai#1`](https://github.com/teamleaderleo/ai/pull/1) characterization/provenance; [`teamleaderleo/ai#7`](https://github.com/teamleaderleo/ai/pull/7) stacked repair and execution receipts

## Current code and tests

### Product code

- [`stream-text.ts`](https://github.com/teamleaderleo/ai/blob/92079da650430d8376a7eeef2436910b44393411/packages/ai/src/generate-text/stream-text.ts) — independent abort observation, root rejection, outward settlement before callbacks, terminal arbitration, and pre-registration provider cancellation.

### Target-native tests

- [`stream-text-explicit-abort.test.ts`](https://github.com/teamleaderleo/ai/blob/92079da650430d8376a7eeef2436910b44393411/packages/ai/src/generate-text/stream-text-explicit-abort.test.ts) — pending reads, roots and derived getters, pre-abort, local tools, provider cancellation, callback cardinality.
- [`stream-text-explicit-abort-races.test.ts`](https://github.com/teamleaderleo/ai/blob/92079da650430d8376a7eeef2436910b44393411/packages/ai/src/generate-text/stream-text-explicit-abort-races.test.ts) — callback stall, provider-error race, and multi-consumer abort cardinality.
- [`stream-text.test.ts`](https://github.com/teamleaderleo/ai/blob/92079da650430d8376a7eeef2436910b44393411/packages/ai/src/generate-text/stream-text.test.ts) — upstream-style result-promise regression.

### Required generated or dependency files

- [`.changeset/slow-streams-abort.md`](https://github.com/teamleaderleo/ai/blob/92079da650430d8376a7eeef2436910b44393411/.changeset/slow-streams-abort.md)

## Changed-file fence

| Path | Role | Keep upstream? |
| --- | --- | --- |
| `.changeset/slow-streams-abort.md` | release note | yes |
| `packages/ai/src/generate-text/stream-text.ts` | production | yes |
| `packages/ai/src/generate-text/stream-text.test.ts` | regression | yes |
| `packages/ai/src/generate-text/stream-text-explicit-abort.test.ts` | regression | yes, subject to consolidation |
| `packages/ai/src/generate-text/stream-text-explicit-abort-races.test.ts` | regression | yes, subject to consolidation |

## Evidence summary

| Claim | Evidence class | Exact receipt | Limit |
| --- | --- | --- | --- |
| Public main still lacks independent abort settlement | `source-read` | public base `e84b8bc…` | one exact revision |
| Callback-independent settlement and abort/error arbitration pass focused tests | `target-executed` | runs `30506931561` / job `90758627827` and `30507215391` / job `90759478304` | executed on prior exact source diff, before current-main materialization |
| Clean current-main candidate exists | `source-read` | source head `92079da…` | no current-head test run |
| Awaited pre-registration cancellation can retain setup on hostile provider cancellation | `source-read` | `stream-text.ts` at `92079da…` | hostile target test still required |

## Packet navigation

- [Deep dive](./DEEP_DIVE.md)
- [Approaches](./APPROACHES.md)
- [Tests and receipts](./TESTS.md)
- [Upstream issue draft](./UPSTREAM_ISSUE.md)
- [Upstream pull-request draft](./UPSTREAM_PR.md)
- [Review and human inspection guide](./REVIEW.md)

## Duplicate and prior-art result

- Search date: `2026-08-01`
- Current upstream issue: [`vercel/ai#15430`](https://github.com/vercel/ai/issues/15430)
- Current upstream implementation: [`vercel/ai#16852`](https://github.com/vercel/ai/pull/16852), open at `0ef2ae9a7f143d90972b4ff217046e0b04ea67f1`
- Equivalent implementation found: `partial`
- Relationship to prior work: the owned candidate extends the maintainer-authored pending-read fix with broader characterization, callback-independent settlement, deterministic post-abort arbitration, multi-consumer controls, and registration-gap cancellation. Public contribution should update or replace the existing PR only with maintainer direction.

## Remaining work

Complete in this order:

1. Replace awaited pre-registration `languageModelStream.cancel(reason)` with a handled nonblocking cancellation request; add rejecting and never-settling cancel controls plus unhandled-rejection observation.
2. Run focused Node and Edge tests, AI package TypeScript, Ultracite, and `git diff --check` on the resulting exact current-main head.
3. Obtain ordinary repository CI, review the complete five-file diff, and decide whether public delivery belongs as a revision of upstream PR #16852 or an issue/maintainer handoff.

## Blockers and limits

- No workflow run exists for current source head `92079da…`.
- The earlier ordinary fork CI run ended `action_required` with zero jobs.
- Final independent acceptance remains absent.
- Abort reports termination; it cannot reverse an external tool side effect that already committed.
- Public upstream contact remains unauthorized.

## Latest handoff

State: `REPAIR`  
Exact source head: `92079da650430d8376a7eeef2436910b44393411`  
Exact packet head: see final #435 handoff  
Tests: prior matching repair diff passed 6 Node and 6 Edge tests plus type, format/lint, and diff checks; current-main materialization unexecuted  
Temporary machinery remaining: no workflow files; internal materialization PR #8 is merged  
Next worker action: repair and test hostile pre-registration provider cancellation on `upstream/06-explicit-abort-nonblocking`  
Public upstream interaction: none