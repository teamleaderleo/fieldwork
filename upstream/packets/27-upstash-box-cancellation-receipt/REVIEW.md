# Review — Unit 27 cancellation-request receipt

## In simple words

The receipt design and Python ownership model are well supported. The decisive review question is whether TypeScript local stream shutdown can be separated cleanly from timeout while preserving current caller behavior. Until that composed path runs, the unit remains `REPAIR`.

## Review subject

- Work class: upstream-fork research
- Target repository: `upstash/box`
- Proposed upstream base: current `main`; last inspected `9f7533c645f6b519f612aa977f6f4acf86655db7`
- Canonical source branch: unavailable; intended `fix/shared-cancellation-request-receipt`
- Exact source head: none; retained patch hash `d30874c96f8e39350b9d725c58a6034554c561b073cb04969849ff2778c09e88`
- Fieldwork packet branch: `p0/435-unit-27-upstash-box-cancellation-receipt`
- Exact packet head: recorded in latest #435 handoff
- Complete packet fence: seven required Markdown files, one retained patch, one retained JSON receipt
- Upstream-contact authority: false

## Review reading order

1. [`README.md`](./README.md)
2. [`DEEP_DIVE.md`](./DEEP_DIVE.md)
3. [`APPROACHES.md`](./APPROACHES.md)
4. [`TESTS.md`](./TESTS.md)
5. [`patches/target-executed-b55d832.patch`](./patches/target-executed-b55d832.patch)
6. [`receipts/target-executed-b55d832.json`](./receipts/target-executed-b55d832.json)
7. [`UPSTREAM_ISSUE.md`](./UPSTREAM_ISSUE.md)
8. [`UPSTREAM_PR.md`](./UPSTREAM_PR.md)

## Exact diff links

- Retained source generator: [PR #389](https://github.com/teamleaderleo/fieldwork/pull/389)
- Target-executed carrier head: [`1e7909da`](https://github.com/teamleaderleo/fieldwork/commit/1e7909da440ab631fcea11d4d3777d2bce107277)
- Production materializer: [`apply_target_repair.py`](https://github.com/teamleaderleo/fieldwork/blob/ccaa28e40c5689aec7ad78c7f18c354e9966d7fd/programmes/high-leverage-open-source/scouts/upstash-box-cancel-receipts/target-materialization/apply_target_repair.py)
- Follow-up materializer: [`apply_sync_test_repair.py`](https://github.com/teamleaderleo/fieldwork/blob/ccaa28e40c5689aec7ad78c7f18c354e9966d7fd/programmes/high-leverage-open-source/scouts/upstash-box-cancel-receipts/target-materialization/apply_sync_test_repair.py)
- TypeScript controls: [`fieldwork-cancel-receipt-repair.test.ts`](https://github.com/teamleaderleo/fieldwork/blob/ccaa28e40c5689aec7ad78c7f18c354e9966d7fd/programmes/high-leverage-open-source/scouts/upstash-box-cancel-receipts/target-materialization/fieldwork-cancel-receipt-repair.test.ts)
- Python controls: [`test_cancel_receipt_repair.py`](https://github.com/teamleaderleo/fieldwork/blob/ccaa28e40c5689aec7ad78c7f18c354e9966d7fd/programmes/high-leverage-open-source/scouts/upstash-box-cancel-receipts/target-materialization/test_cancel_receipt_repair.py)

## Claims requiring judgment

| Claim or design choice | Evidence | Reviewer question |
| --- | --- | --- |
| separate request receipt is the smallest truthful API | model comparison and target execution | does the additive API justify its public surface? |
| failed receipt stays cached | no-replay controls | should deliberate retry exist now or later? |
| `detached` fits cancellation-request observer shutdown | existing early-termination semantics | does this preserve CLI and iterator expectations? |
| single-flight is per run object | exact constructors and local fields | is the narrowed scope acceptable? |
| Python coordinator belongs outside generated client | deterministic generation and parity | does target prefer a fallback module or current mapping? |

## Known risks

- Cancellation-request abort and timeout abort currently share one terminal catch.
- Stream iterator error text may change when abort origin is separated.
- Open CLI PR #82 relies on `cancel()` to stop iteration and tracks caller intent itself.
- Failure caching blocks automatic retry.
- No current owned target branch exists.

## Evidence limits

- Historical exact target, one Ubuntu environment.
- Local mocked requests.
- No hosted endpoint or provider behavior.
- No current-head target execution.
- No eligible independent acceptance.

## Staleness check

- Current upstream head checked: `9f7533c645f6b519f612aa977f6f4acf86655db7`
- Candidate base relationship: executed base is four commits behind
- Relevant source paths changed since execution: no in inspected compare
- Duplicate/overlap search date: `2026-08-01`
- Open replacement work found: none
- Packet reflects the latest `REPAIR` disposition

## Source cleanliness

- [ ] Clean owned target branch exists.
- [x] Retained patch inventory is complete.
- [x] Temporary workflow is absent from workflow-free carrier.
- [ ] Fieldwork-named tests are renamed/integrated.
- [x] No dependency change is selected.
- [ ] Commit-pinned links resolve to a renewed candidate head.

## Test review

- [x] Historical intended isolated assertions ran.
- [x] Baseline/candidate relationship is clear.
- [x] Setup and product failures are separated.
- [ ] Complete TypeScript stream failure path covered.
- [x] Compatibility controls exist.
- [x] Platform and integration limits are explicit.
- [x] Historical ordinary gates are named accurately.
- [ ] Current-head ordinary gates run.

## Draft review

- [x] Issue draft avoids impact/prevalence claims.
- [x] PR draft describes selected direction and blocker.
- [x] Target terminology is used.
- [x] Internal process vocabulary stays outside proposed public body.
- [ ] Current AI disclosure requirement checked at submission time.

## Reviewer disposition

`REPAIR`

Reviewed source: historical patch `d30874c...`; current source `9f7533c...`  
Reviewed packet head: latest #435 handoff  
Reason: exact source composition allows cancellation-request observer abort to flow through timeout handling and publish terminal `cancelled`.  
Clearing condition: source repair plus real stream-path, timeout, two-wrapper, focused, and complete current-head execution.  
Reviewer eligibility: self-review only

## Human deep-dive guide

Focus on:

1. abort-origin ownership and iterator outcome;
2. compatibility of `detached` for caller-requested local shutdown;
3. cached failure receipt and retry policy;
4. per-object identity scope;
5. direct PR after repair versus issue-first naming discussion.

Suggested response:

`Unit 27 remains REPAIR until the real stream path is renewed`  
—or—  
`Unit 27 concern: <specific source, test, compatibility, or framing issue>`
