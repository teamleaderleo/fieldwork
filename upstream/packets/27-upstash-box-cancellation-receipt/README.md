# Unit 27 — Share a truthful cancellation-request receipt across Upstash Box SDKs

## In simple words

Upstash Box exposes `Run.cancel()` in TypeScript and Python. At the inspected source, a failed cancellation request is swallowed, the local run becomes terminal `cancelled`, and concurrent callers can send duplicate requests. The retained candidate adds one immutable receipt per in-memory `Run` instance, preserves legacy `cancel()` return values, and leaves remote outcome unknown until server data says otherwise.

Deeper review selected the missing TypeScript repair. Record the first owner of an agent-stream abort in a private weak controller map. A cancellation-request abort should keep iterator rejection for existing CLI consumers, use cancellation-specific error prose, and let the current iterator cleanup publish `detached`. Timeout remains separately classified. Command and code streams currently lack the attached controller used by this path, so local observer-shutdown claims must stay agent-stream-specific unless those implementations are deliberately widened and tested.

## Current disposition

`REPAIR`

Last verified: `2026-08-01`  
Worker: `GPT-5.6 Thinking`  
Priority-zero parent: [`teamleaderleo/fieldwork#435`](https://github.com/teamleaderleo/fieldwork/issues/435)  
Upstream contact authorized: `no`

## Contribution

- Target project: `upstash/box`
- Proposed upstream destination: `upstash/box` `main`
- Proposed title: `fix: share cancellation request receipts without publishing terminal run state`
- Contribution synopsis: preserve `cancel(): Promise<void>` and Python `cancel() -> None`, add additive immutable request-receipt APIs, single-flight the request per in-memory run object, keep provider error detail out of the receipt, keep run status server/event-owned, and classify TypeScript agent-stream cancellation-request abort separately from timeout.
- Work class: `upstream-fork research`

## Exact identities

- Historical public base executed: [`upstash/box@b55d832d6e3ae0156e32d21ea3863e231dfff9cd`](https://github.com/upstash/box/tree/b55d832d6e3ae0156e32d21ea3863e231dfff9cd)
- Current public upstream head inspected: [`upstash/box@9f7533c645f6b519f612aa977f6f4acf86655db7`](https://github.com/upstash/box/tree/9f7533c645f6b519f612aa977f6f4acf86655db7)
- Current-head relation: four commits ahead of the executed base; the compare contains no cancellation implementation or test path, so the relevant blobs remain unchanged
- Open CLI compatibility head inspected: [`upstash/box#82@fce8c8cfc269bc09d07eb991ee39d0433029027e`](https://github.com/upstash/box/pull/82)
- Owned target fork: `repository admission needed`; connected access to `upstash/box` is read-only and no owned Box fork was available
- Intended clean source branch: `fix/shared-cancellation-request-receipt`
- Canonical source head: `none — clean target branch unavailable`
- Retained source candidate: [ordered exact patch series](./patches/README.md), reconstructed SHA-256 `d30874c96f8e39350b9d725c58a6034554c561b073cb04969849ff2778c09e88`
- Target-executed Fieldwork carrier head: [`1e7909da440ab631fcea11d4d3777d2bce107277`](https://github.com/teamleaderleo/fieldwork/commit/1e7909da440ab631fcea11d4d3777d2bce107277)
- Workflow-free carrier head: [`ccaa28e40c5689aec7ad78c7f18c354e9966d7fd`](https://github.com/teamleaderleo/fieldwork/commit/ccaa28e40c5689aec7ad78c7f18c354e9966d7fd)
- Fieldwork packet branch: `p0/435-unit-27-upstash-box-cancellation-receipt`
- Fieldwork packet head: exact current head is recorded in the latest issue #435 handoff because a file cannot name the commit that contains itself
- Execution carrier: [PR #389](https://github.com/teamleaderleo/fieldwork/pull/389)
- Superseded carriers: [PR #332](https://github.com/teamleaderleo/fieldwork/pull/332), [PR #337](https://github.com/teamleaderleo/fieldwork/pull/337), [PR #372](https://github.com/teamleaderleo/fieldwork/pull/372), [PR #391](https://github.com/teamleaderleo/fieldwork/pull/391)

## Current code and tests

### Product code

- [`packages/sdk/src/client.ts` at current upstream](https://github.com/upstash/box/blob/9f7533c645f6b519f612aa977f6f4acf86655db7/packages/sdk/src/client.ts) — owns `Run.status`, the agent observer controller, cancellation, timeout, stream error translation, and command/code stream implementations
- [`packages/python-sdk/upstash_box/_async/client.py` at current upstream](https://github.com/upstash/box/blob/9f7533c645f6b519f612aa977f6f4acf86655db7/packages/python-sdk/upstash_box/_async/client.py) — async source of truth for Python run cancellation
- [`packages/python-sdk/scripts/generate_sync.py`](https://github.com/upstash/box/blob/9f7533c645f6b519f612aa977f6f4acf86655db7/packages/python-sdk/scripts/generate_sync.py) — generates synchronous Python from async source
- [`apply_target_repair.py`](https://github.com/teamleaderleo/fieldwork/blob/ccaa28e40c5689aec7ad78c7f18c354e9966d7fd/programmes/high-leverage-open-source/scouts/upstash-box-cancel-receipts/target-materialization/apply_target_repair.py) and [`apply_sync_test_repair.py`](https://github.com/teamleaderleo/fieldwork/blob/ccaa28e40c5689aec7ad78c7f18c354e9966d7fd/programmes/high-leverage-open-source/scouts/upstash-box-cancel-receipts/target-materialization/apply_sync_test_repair.py) — fail-closed exact-source transformations retained for research

### Target-native tests

- [`fieldwork-cancel-receipt-repair.test.ts`](https://github.com/teamleaderleo/fieldwork/blob/ccaa28e40c5689aec7ad78c7f18c354e9966d7fd/programmes/high-leverage-open-source/scouts/upstash-box-cancel-receipts/target-materialization/fieldwork-cancel-receipt-repair.test.ts) — isolated TypeScript receipt, identity, failure, legacy-return, observer-abort, and no-replay controls
- [`test_cancel_receipt_repair.py`](https://github.com/teamleaderleo/fieldwork/blob/ccaa28e40c5689aec7ad78c7f18c354e9966d7fd/programmes/high-leverage-open-source/scouts/upstash-box-cancel-receipts/target-materialization/test_cancel_receipt_repair.py) — async waiter isolation, sync thread sharing, immutability, failure, legacy return, and no-replay controls
- Current upstream native run tests: [`TypeScript Run`](https://github.com/upstash/box/blob/9f7533c645f6b519f612aa977f6f4acf86655db7/packages/sdk/src/__tests__/run.test.ts), [`TypeScript agent stream`](https://github.com/upstash/box/blob/9f7533c645f6b519f612aa977f6f4acf86655db7/packages/sdk/src/__tests__/box-agent-run.test.ts), [`Python async`](https://github.com/upstash/box/blob/9f7533c645f6b519f612aa977f6f4acf86655db7/packages/python-sdk/tests/_async/test_run.py), [`Python sync`](https://github.com/upstash/box/blob/9f7533c645f6b519f612aa977f6f4acf86655db7/packages/python-sdk/tests/_sync/test_sync_client.py)

### Required generated or dependency files

- Generated sync client belongs in the target diff and must be regenerated from async source.
- No new dependency is selected.
- A changeset may be required by current target release practice; decide after maintainer direction.

## Changed-file fence

The retained target-executed patch contains 15 unique paths, 471 insertions, and 27 deletions by `git apply --stat`.

| Path group | Role | Keep upstream? |
| --- | --- | --- |
| TypeScript client, types, exports | production | yes after agent-stream abort repair |
| TypeScript native run test | regression/compatibility | yes |
| Fieldwork-named TypeScript test | execution control | rename and integrate before upstream |
| Python async client, types, exports, coordinator | production | yes after final naming review |
| Generated Python sync client | generated | yes |
| Python async/sync native tests | regression/compatibility | yes |
| Fieldwork-named Python test | execution control | split into target-native files before upstream |
| Python parity documentation | public API parity | yes |
| Generator mapping | generated boundary | yes |

No new repair patch has been retained yet. The selected weak-controller-owner repair remains source/test prepared in the packet and must be materialized on a target tree.

## Evidence summary

| Claim | Evidence class | Exact receipt | Limit |
| --- | --- | --- | --- |
| Baseline suppresses request failure, publishes local terminal `cancelled`, and duplicates concurrent requests | `target-executed` | Fieldwork #329; runs `30622339900` and `30623393254` | local mocked target tests only |
| Shared receipt API passes focused and full TS/Python gates | `target-executed` | run `30642924979`, job `91197101877`, artifact `8798217638` | executed at historical base `b55d832d...` |
| Retained patch matches receipt hash and contains 15 unique paths | `model-executed` | packet receipt and ordered patch series; local SHA/inventory check on 2026-08-01 | patch integrity only |
| Current relevant source remains byte-continuous from executed base | `source-read` | compare `b55d832d...9f7533c...` | no renewed target execution at current head |
| Box already uses `detached` for local agent-stream reader termination | `source-read` | current iterator and native early-break test | does not prove remote result |
| Open CLI cancellation work requires iterator rejection | `source-read` | PR #82 head `fce8c8c...` | open consumer, not merged contract |
| First-owner weak map repairs abort classification | `target-test-prepared` | exact design and matrix in packet | source and tests unmaterialized |
| Single-flight applies to remote run identity | `source-read` | constructors accept the same run ID in multiple objects | false; current candidate supports one object only |
| All TypeScript streams have local observer abort | `source-read` | agent vs command/code constructors | false at inspected source |

## Packet navigation

- [Deep dive](./DEEP_DIVE.md)
- [Related repository and contract context](./RELATED_CONTEXT.md)
- [Approaches](./APPROACHES.md)
- [Tests and receipts](./TESTS.md)
- [Upstream issue draft](./UPSTREAM_ISSUE.md)
- [Upstream pull-request draft](./UPSTREAM_PR.md)
- [Review and human inspection guide](./REVIEW.md)
- [Retained exact target patch series](./patches/README.md)
- [Retained execution receipt](./receipts/target-executed-b55d832.json)

## Duplicate and prior-art result

- Search date: `2026-08-01`
- Current upstream issues checked: cancellation/receipt/status searches returned no issue
- Current upstream PRs checked: [#82](https://github.com/upstash/box/pull/82), [#68](https://github.com/upstash/box/pull/68), [#51](https://github.com/upstash/box/pull/51), plus broad cancellation searches
- Equivalent implementation found: `no`
- Relationship to prior work: PR #68 created the current `Run`/`StreamRun` status ownership model; PR #51 added hosted cancellation coverage; open PR #82 depends on iterator rejection after `run.cancel()` and explicitly tracks caller intent separately. None adds a shared request receipt or abort-owner classification.

## Deeper context result

Read-only source comparisons were added for:

- Upstash Redis subscriptions — expected local abort is observer teardown, not a fabricated remote outcome;
- Ky — timeout ownership is explicit rather than inferred from a generic abort;
- Google long-running operations — cancellation starts best-effort asynchronous work and requires later state reads;
- Temporal Go — request initiation, request receipt, and operation completion are separate lifecycle stages.

These are supporting interface context. They do not establish Box endpoint semantics, hosted behavior, or ecosystem impact.

## Remaining work

Complete in this order:

1. Materialize the private first-owner `WeakMap` helper and route agent-stream timeout plus `requestCancel()` through it.
2. Keep cancellation-request iterator rejection, change it to cancellation-specific prose, and let `finally` publish partial output plus `detached`.
3. Add real `box.agent.stream()` pending-read controls before receipt settlement, timeout-only behavior, and both race orders.
4. Add later-controller, same-ID/two-wrapper, authoritative-update, CLI compatibility, and stream-type boundary controls.
5. Decide whether command/code streams remain explicitly outside local observer shutdown or gain their own controllers in a separately justified widening.
6. Review receipt naming (`accepted` versus a narrower acknowledgement term).
7. Rerun full current target gates, regenerate the patch and receipt, then create the clean target branch in an admitted owned fork.
8. Repeat current duplicate/policy search and obtain explicit upstream-contact authority.

## Blockers and limits

- Selected TypeScript source repair is not materialized or executed.
- Current single-flight scope is one in-memory run object.
- Agent stream has local controller ownership; command/code streams currently do not.
- Receipt request-state naming depends on undocumented endpoint semantics.
- No owned target fork is connected, so a clean target-source branch could not be created.
- No current-head target execution was run in this context pass.
- Hosted endpoint semantics, provider idempotency, billing, production interruption, and maintainer API naming remain unknown.
- Public upstream contact remains unauthorized.

## Latest handoff

State: `REPAIR`  
Exact source head: `none`; retained historical candidate is ordered patch series SHA `d30874c96f8e39350b9d725c58a6034554c561b073cb04969849ff2778c09e88` from carrier head `1e7909da440ab631fcea11d4d3777d2bce107277`  
Exact packet head: see latest #435 handoff  
Tests: historical target run green; current pass added source-read context and an exact unexecuted reversing matrix  
Temporary machinery remaining: no workflow on workflow-free carrier; old carrier branch and PR #389 remain open research records  
Next worker action: materialize the first-owner agent-stream repair and run the pending-read/race matrix before refreshing the candidate  
Public upstream interaction: `none`
