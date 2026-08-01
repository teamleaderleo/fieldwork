# Unit 27 — Share a truthful cancellation-request receipt across Upstash Box SDKs

## In simple words

Upstash Box exposes `Run.cancel()` in TypeScript and Python. At the inspected source, a failed cancellation request is swallowed, the local run becomes terminal `cancelled`, and concurrent callers can send duplicate requests. The retained candidate adds one immutable receipt per in-memory `Run` instance, preserves legacy `cancel()` return values, and leaves remote outcome unknown until server data says otherwise.

The receipt design remains useful, but the TypeScript candidate still shares one `AbortController` between timeout handling and cancellation-request observer shutdown. The real stream iterator maps every `AbortError` to terminal `cancelled`, so the executed isolated controls do not prove truthful status for a streaming run. The packet therefore remains in repair.

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
- Contribution synopsis: preserve `cancel(): Promise<void>` and Python `cancel() -> None`, add additive immutable request-receipt APIs, single-flight the request per in-memory run object, keep provider error detail out of the receipt, and keep run status server/event-owned. Before upstream preparation, compose local stream-abort ownership with the existing timeout path.
- Work class: `upstream-fork research`

## Exact identities

- Historical public base executed: [`upstash/box@b55d832d6e3ae0156e32d21ea3863e231dfff9cd`](https://github.com/upstash/box/tree/b55d832d6e3ae0156e32d21ea3863e231dfff9cd)
- Current public upstream head inspected: [`upstash/box@9f7533c645f6b519f612aa977f6f4acf86655db7`](https://github.com/upstash/box/tree/9f7533c645f6b519f612aa977f6f4acf86655db7)
- Current-head relation: four commits ahead of the executed base; the compare contains no cancellation implementation or test path, so the relevant blobs remain unchanged
- Owned target fork: `repository admission needed`; the connected account has read-only access to `upstash/box` and no owned Box fork was available
- Intended clean source branch: `fix/shared-cancellation-request-receipt`
- Canonical source head: `none — clean target branch unavailable`
- Retained source candidate: patch SHA-256 `d30874c96f8e39350b9d725c58a6034554c561b073cb04969849ff2778c09e88`
- Target-executed Fieldwork carrier head: [`1e7909da440ab631fcea11d4d3777d2bce107277`](https://github.com/teamleaderleo/fieldwork/commit/1e7909da440ab631fcea11d4d3777d2bce107277)
- Workflow-free carrier head: [`ccaa28e40c5689aec7ad78c7f18c354e9966d7fd`](https://github.com/teamleaderleo/fieldwork/commit/ccaa28e40c5689aec7ad78c7f18c354e9966d7fd)
- Fieldwork packet branch: `p0/435-unit-27-upstash-box-cancellation-receipt`
- Fieldwork packet head: exact current head is recorded in the latest issue #435 handoff because a file cannot name the commit that contains itself
- Execution carrier: [PR #389](https://github.com/teamleaderleo/fieldwork/pull/389)
- Superseded carriers: [PR #332](https://github.com/teamleaderleo/fieldwork/pull/332), [PR #337](https://github.com/teamleaderleo/fieldwork/pull/337), [PR #372](https://github.com/teamleaderleo/fieldwork/pull/372), [PR #391](https://github.com/teamleaderleo/fieldwork/pull/391)

## Current code and tests

### Product code

- [`packages/sdk/src/client.ts` at current upstream](https://github.com/upstash/box/blob/9f7533c645f6b519f612aa977f6f4acf86655db7/packages/sdk/src/client.ts) — owns `Run.status`, the observer `AbortController`, cancellation, timeout, and stream error translation
- [`packages/python-sdk/upstash_box/_async/client.py` at current upstream](https://github.com/upstash/box/blob/9f7533c645f6b519f612aa977f6f4acf86655db7/packages/python-sdk/upstash_box/_async/client.py) — async source of truth for Python run cancellation
- [`packages/python-sdk/scripts/generate_sync.py`](https://github.com/upstash/box/blob/9f7533c645f6b519f612aa977f6f4acf86655db7/packages/python-sdk/scripts/generate_sync.py) — generates synchronous Python from async source
- [`apply_target_repair.py`](https://github.com/teamleaderleo/fieldwork/blob/ccaa28e40c5689aec7ad78c7f18c354e9966d7fd/programmes/high-leverage-open-source/scouts/upstash-box-cancel-receipts/target-materialization/apply_target_repair.py) and [`apply_sync_test_repair.py`](https://github.com/teamleaderleo/fieldwork/blob/ccaa28e40c5689aec7ad78c7f18c354e9966d7fd/programmes/high-leverage-open-source/scouts/upstash-box-cancel-receipts/target-materialization/apply_sync_test_repair.py) — fail-closed exact-source transformation retained for research

### Target-native tests

- [`fieldwork-cancel-receipt-repair.test.ts`](https://github.com/teamleaderleo/fieldwork/blob/ccaa28e40c5689aec7ad78c7f18c354e9966d7fd/programmes/high-leverage-open-source/scouts/upstash-box-cancel-receipts/target-materialization/fieldwork-cancel-receipt-repair.test.ts) — isolated TypeScript receipt, identity, failure, legacy-return, observer-abort, and no-replay controls
- [`test_cancel_receipt_repair.py`](https://github.com/teamleaderleo/fieldwork/blob/ccaa28e40c5689aec7ad78c7f18c354e9966d7fd/programmes/high-leverage-open-source/scouts/upstash-box-cancel-receipts/target-materialization/test_cancel_receipt_repair.py) — async waiter isolation, sync thread sharing, immutability, failure, legacy return, and no-replay controls
- Current upstream native run tests: [`TypeScript`](https://github.com/upstash/box/blob/9f7533c645f6b519f612aa977f6f4acf86655db7/packages/sdk/src/__tests__/run.test.ts), [`Python async`](https://github.com/upstash/box/blob/9f7533c645f6b519f612aa977f6f4acf86655db7/packages/python-sdk/tests/_async/test_run.py), [`Python sync`](https://github.com/upstash/box/blob/9f7533c645f6b519f612aa977f6f4acf86655db7/packages/python-sdk/tests/_sync/test_sync_client.py)

### Required generated or dependency files

- Generated sync client belongs in the target diff and must be regenerated from async source.
- No new dependency is selected.
- A changeset may be required by current target release practice; decide after maintainer direction.

## Changed-file fence

The retained target-executed patch contains 15 unique paths, 471 insertions, and 27 deletions by `git apply --stat`.

| Path group | Role | Keep upstream? |
| --- | --- | --- |
| TypeScript client, types, exports | production | yes after stream-abort repair |
| TypeScript native run test | regression/compatibility | yes |
| Fieldwork-named TypeScript test | execution control | rename and integrate before upstream |
| Python async client, types, exports, coordinator | production | yes after final design review |
| Generated Python sync client | generated | yes |
| Python async/sync native tests | regression/compatibility | yes |
| Fieldwork-named Python test | execution control | split into target-native files before upstream |
| Python parity documentation | public API parity | yes |
| Generator mapping | generated boundary | yes |

## Evidence summary

| Claim | Evidence class | Exact receipt | Limit |
| --- | --- | --- | --- |
| Baseline suppresses request failure, publishes local terminal `cancelled`, and duplicates concurrent requests | `target-executed` | Fieldwork #329; runs `30622339900` and `30623393254` | local mocked target tests only |
| Shared receipt API passes focused and full TS/Python gates | `target-executed` | run `30642924979`, job `91197101877`, artifact `8798217638` | executed at historical base `b55d832d...` |
| Retained patch matches receipt hash and contains 15 unique paths | `model-executed` | packet receipt and patch; local SHA/inventory check on 2026-08-01 | patch integrity only |
| Current relevant source remains byte-continuous from executed base | `source-read` | compare `b55d832d...9f7533c...` | no renewed target execution at current head |
| Complete TS stream lifecycle preserves server-authoritative status | `target-test-prepared` | required control described in review `4830012327` | control and source repair remain absent |
| Single-flight applies to remote run identity | `source-read` | constructors accept the same run ID in multiple objects | current candidate supports one in-memory `Run` instance only |

## Packet navigation

- [Deep dive](./DEEP_DIVE.md)
- [Approaches](./APPROACHES.md)
- [Tests and receipts](./TESTS.md)
- [Upstream issue draft](./UPSTREAM_ISSUE.md)
- [Upstream pull-request draft](./UPSTREAM_PR.md)
- [Review and human inspection guide](./REVIEW.md)
- [Retained exact target patch](./patches/target-executed-b55d832.patch)
- [Retained execution receipt](./receipts/target-executed-b55d832.json)

## Duplicate and prior-art result

- Search date: `2026-08-01`
- Current upstream issues checked: cancellation/receipt/status searches returned no issue
- Current upstream PRs checked: [#82](https://github.com/upstash/box/pull/82), [#68](https://github.com/upstash/box/pull/68), [#51](https://github.com/upstash/box/pull/51), plus broad cancellation searches
- Equivalent implementation found: `no`
- Relationship to prior work: PR #68 created the current `Run`/`StreamRun` status ownership model; PR #51 added hosted cancellation coverage; open PR #82 depends on `run.cancel()` for Ctrl+C and explicitly tracks caller intent separately, making legacy behavior compatibility important. None adds a shared truthful request receipt.

## Remaining work

Complete in this order:

1. Add a real `box.agent.stream()` reversing control with a pending body read, cancellation before settlement, and cancellation after settlement with a newly attached observer.
2. Separate cancellation-request observer shutdown from timeout abort in TypeScript. Keep cancellation-request shutdown nonterminal, likely `detached`, while preserving separately tested timeout behavior.
3. Add a two-wrapper/same-run-ID boundary test and narrow all claims to one in-memory `Run` instance.
4. Rerun the full current target gates, regenerate the patch and receipt, then create the clean target branch in an admitted owned fork.
5. Repeat current duplicate/policy search and obtain explicit upstream-contact authority.

## Blockers and limits

- TypeScript stream abort ownership is unresolved and invalidates the broad `no false terminal status` claim.
- Current single-flight scope is one in-memory run object.
- No owned target fork is connected, so a clean target-source branch could not be created.
- No current-head target execution was run in this unit.
- Hosted endpoint semantics, provider idempotency, billing, production interruption, and maintainer API naming remain unknown.
- Public upstream contact remains unauthorized.

## Latest handoff

State: `REPAIR`  
Exact source head: `none`; retained candidate is patch `d30874c96f8e39350b9d725c58a6034554c561b073cb04969849ff2778c09e88` from carrier head `1e7909da440ab631fcea11d4d3777d2bce107277`  
Exact packet head: see latest #435 handoff  
Tests: historical target run green; current unit verified receipt JSON, patch SHA, 15-path inventory, 471/27 diff stats, current-source continuity, and prior-art state  
Temporary machinery remaining: no workflow on workflow-free carrier; old carrier branch and PR #389 remain open research records  
Next worker action: implement and execute the real stream-path reversing control before refreshing the candidate  
Public upstream interaction: `none`
