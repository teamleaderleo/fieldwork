# Unit 06 — fix(ai): make explicit abort settlement nonblocking

## In simple words

`streamText` can be waiting for another provider chunk when a caller aborts the operation. The retained candidate makes the caller abort claim the terminal result once, rejects public result state, closes the outward abort stream, requests provider cancellation, and makes later provider values or errors yield to that abort.

The candidate is materialized on a clean owned-fork branch from current public main. Continued investigation corrected one packet premise: the pre-registration `await languageModelStream.cancel(reason)` already awaits a request-level cancellation promise. Native Web Streams modeling showed that this promise settles after forwarding cancellation while provider cleanup remains pending, and provider cleanup rejection is contained by the existing pipe chain. A target-native regression for those semantics is now part of the canonical branch.

A broader code-first pass found one separate shared-helper defect: when an SDK async iterator receives a source-stream error, it propagates the error but retains its reader lock. Native iteration and a minimal catch-and-release candidate both leave the stream unlocked. This affects many streaming APIs and belongs in a separate follow-up, outside the six-file explicit-abort candidate.

The source direction remains coherent. Promotion is held on ordinary exact-head CI and independent acceptance.

## Current disposition

`HOLD`

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
- Current-public-base branch: `upstream/06-public-main-base`
- Canonical source branch: `upstream/06-explicit-abort-nonblocking`
- Canonical source head: [`3035f6e5a3ef6ff9236c8d1b08f4ea3dfe852c15`](https://github.com/teamleaderleo/ai/commit/3035f6e5a3ef6ff9236c8d1b08f4ea3dfe852c15)
- Canonical owned-fork review PR: [`teamleaderleo/ai#13`](https://github.com/teamleaderleo/ai/pull/13)
- Exact Verify Changesets run: `30691402294`
- Exact ordinary CI run: `30691402306`
- Fieldwork packet branch: `p0/435-unit-06-vercel-ai-explicit-abort`
- Fieldwork packet head: exact current head is recorded in the latest #435 handoff
- Materialization carrier: [`teamleaderleo/ai#8`](https://github.com/teamleaderleo/ai/pull/8), merged
- Target-native cancellation-regression PR: [`teamleaderleo/ai#12`](https://github.com/teamleaderleo/ai/pull/12), squash-merged as `3035f6e5a3ef6ff9236c8d1b08f4ea3dfe852c15`
- Historical source surfaces: [`teamleaderleo/ai#1`](https://github.com/teamleaderleo/ai/pull/1) characterization/provenance; [`teamleaderleo/ai#7`](https://github.com/teamleaderleo/ai/pull/7) stacked repair and execution receipts
- Superseded execution carriers: `teamleaderleo/ai#9`, `#10`, and `#11`

## Current code and tests

### Product code

- [`stream-text.ts`](https://github.com/teamleaderleo/ai/blob/3035f6e5a3ef6ff9236c8d1b08f4ea3dfe852c15/packages/ai/src/generate-text/stream-text.ts) — independent abort observation, root rejection, outward settlement before callbacks, terminal arbitration, and direct pre-registration provider cancellation.

### Target-native tests

- [`stream-text-explicit-abort.test.ts`](https://github.com/teamleaderleo/ai/blob/3035f6e5a3ef6ff9236c8d1b08f4ea3dfe852c15/packages/ai/src/generate-text/stream-text-explicit-abort.test.ts) — pending reads, roots and derived getters, pre-abort, local tools, provider cancellation, callback cardinality.
- [`stream-text-explicit-abort-races.test.ts`](https://github.com/teamleaderleo/ai/blob/3035f6e5a3ef6ff9236c8d1b08f4ea3dfe852c15/packages/ai/src/generate-text/stream-text-explicit-abort-races.test.ts) — callback stall, provider-error race, and multi-consumer abort cardinality.
- [`stream-text.test.ts`](https://github.com/teamleaderleo/ai/blob/3035f6e5a3ef6ff9236c8d1b08f4ea3dfe852c15/packages/ai/src/generate-text/stream-text.test.ts) — upstream-style result-promise regression.
- [`stream-language-model-call-cancellation.test.ts`](https://github.com/teamleaderleo/ai/blob/3035f6e5a3ef6ff9236c8d1b08f4ea3dfe852c15/packages/ai/src/generate-text/stream-language-model-call-cancellation.test.ts) — exact cancellation reason, pending provider cleanup, and rejected provider cleanup.

### Required generated or dependency files

- [`.changeset/slow-streams-abort.md`](https://github.com/teamleaderleo/ai/blob/3035f6e5a3ef6ff9236c8d1b08f4ea3dfe852c15/.changeset/slow-streams-abort.md)

## Changed-file fence

| Path | Role | Keep upstream? |
| --- | --- | --- |
| `.changeset/slow-streams-abort.md` | release note | yes |
| `packages/ai/src/generate-text/stream-text.ts` | production | yes |
| `packages/ai/src/generate-text/stream-text.test.ts` | regression | yes |
| `packages/ai/src/generate-text/stream-text-explicit-abort.test.ts` | regression | yes, subject to consolidation |
| `packages/ai/src/generate-text/stream-text-explicit-abort-races.test.ts` | regression | yes, subject to consolidation |
| `packages/ai/src/generate-text/stream-language-model-call-cancellation.test.ts` | cancellation-promise regression | yes, subject to consolidation |

The adjacent async-iterator finding changes `packages/ai/src/util/async-iterable-stream.ts` and its tests. It is excluded from this fence and from the canonical source branch.

## Evidence summary

| Claim | Evidence class | Exact receipt | Limit |
| --- | --- | --- | --- |
| Public main still lacks independent abort settlement | `source-read` | public base `e84b8bc…` | one exact revision |
| Callback-independent settlement and abort/error arbitration pass focused tests | `target-executed` | runs `30506931561` / job `90758627827` and `30507215391` / job `90759478304` | executed on prior exact repair diff, before current-main materialization |
| Clean current-main candidate exists | `source-read` | source head `3035f6e5…` | ordinary exact-head jobs queued |
| Returned model-call stream cancellation settles while provider cleanup remains pending | `model-executed` | `receipts/2026-08-01-provider-cancel-promise-model.md` | native Web Streams model |
| Target-native cancellation semantics are encoded canonically | `target-test-prepared` | source head `3035f6e5…` | ordinary exact-head jobs queued |
| SDK async iteration retains its reader lock after source error | `source-read` + `model-executed` | `receipts/2026-08-01-adjacent-stream-lifecycle-scout.md` | Node `v22.16.0`; target-native Node/Edge regression absent |
| Pre-aborted first provider invocation is shared across `streamText` and `generateText` | `source-read` | adjacent lifecycle scout | contract and callback semantics unresolved |

## Packet navigation

- [Deep dive](./DEEP_DIVE.md)
- [Approaches](./APPROACHES.md)
- [Tests and receipts](./TESTS.md)
- [Provider-cancel promise receipt](./receipts/2026-08-01-provider-cancel-promise-model.md)
- [Adjacent stream lifecycle scout](./receipts/2026-08-01-adjacent-stream-lifecycle-scout.md)
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
- Adjacent async-iterator lock-release search found no obvious current issue or pull request under the inspected terms. This is a quiet search result, not proof of uniqueness.

## Remaining work

Complete in this order:

1. Obtain ordinary repository CI and changeset verification on exact canonical head `3035f6e5a3ef6ff9236c8d1b08f4ea3dfe852c15`; current runs `30691402306` and `30691402294` have jobs created and queued with zero started jobs.
2. Obtain an independent complete-diff disposition on owned-fork PR #13.
3. Decide whether public delivery belongs as a revision of upstream PR #16852 or an issue/maintainer handoff.
4. Outside this unit, prepare and execute a focused Node/Edge regression for async-iterator lock release after source error before opening a separate campaign or source candidate.
5. Characterize pre-aborted provider and callback invocation across `streamText` and `generateText` only if that contract becomes a selected follow-up.

## Blockers and limits

- Exact-head Actions jobs remain queued; this is an execution availability/authorization blocker with no product-test conclusion.
- Final independent acceptance remains absent.
- Abort reports termination; it cannot reverse an external tool side effect that already committed.
- The adjacent iterator result is model-executed, without target-native execution or demonstrated application frequency.
- Public upstream contact remains unauthorized.

## Latest handoff

State: `HOLD`  
Exact canonical source head: `3035f6e5a3ef6ff9236c8d1b08f4ea3dfe852c15`  
Exact packet head: see latest #435 handoff  
Tests: prior matching repair diff passed 6 Node and 6 Edge tests plus type, format/lint, and diff checks; cancellation promise model passed on Node `v22.17.0`; adjacent iterator model passed on Node `v22.16.0`; exact canonical Verify Changesets `30691402294` and CI `30691402306` remain queued  
Temporary machinery remaining: no workflow files on the canonical head; superseded carrier and trigger branch tips were reset to the canonical source head; historical PRs remain as evidence  
Next worker action: inspect exact canonical runs when jobs start, obtain independent review, and route the separate async-iterator lock-release finding through its own characterization  
Public upstream interaction: none
