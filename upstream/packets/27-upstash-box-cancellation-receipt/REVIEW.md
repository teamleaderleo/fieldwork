# Review — Unit 27 cancellation-request receipt

## In simple words

The receipt design and Python ownership model are well supported. The TypeScript repair is now concrete: a private first-owner map for agent-stream aborts, cancellation-specific iterator rejection, and `detached` local status. The decisive remaining question is execution on the real stream body-reader path, including timeout races and the current command/code stream boundary.

## Review subject

- Work class: upstream-fork research
- Target repository: `upstash/box`
- Proposed upstream base: current `main`; last inspected `9f7533c645f6b519f612aa977f6f4acf86655db7`
- Open CLI compatibility head: `fce8c8cfc269bc09d07eb991ee39d0433029027e`
- Canonical source branch: unavailable; intended `fix/shared-cancellation-request-receipt`
- Exact source head: none; retained historical patch hash `d30874c96f8e39350b9d725c58a6034554c561b073cb04969849ff2778c09e88`
- Selected unmaterialized repair: first-owner `WeakMap<AbortController, "cancel-request" | "timeout">`
- Fieldwork packet branch: `p0/435-unit-27-upstash-box-cancellation-receipt`
- Exact packet head: recorded in latest #435 handoff
- Upstream-contact authority: false

## Review reading order

1. [`README.md`](./README.md)
2. [`DEEP_DIVE.md`](./DEEP_DIVE.md)
3. [`RELATED_CONTEXT.md`](./RELATED_CONTEXT.md)
4. [`APPROACHES.md`](./APPROACHES.md)
5. [`TESTS.md`](./TESTS.md)
6. [`patches/README.md`](./patches/README.md)
7. [`receipts/target-executed-b55d832.json`](./receipts/target-executed-b55d832.json)
8. [`UPSTREAM_ISSUE.md`](./UPSTREAM_ISSUE.md)
9. [`UPSTREAM_PR.md`](./UPSTREAM_PR.md)

## Exact source and evidence links

- Retained source generator: [PR #389](https://github.com/teamleaderleo/fieldwork/pull/389)
- Target-executed carrier head: [`1e7909da`](https://github.com/teamleaderleo/fieldwork/commit/1e7909da440ab631fcea11d4d3777d2bce107277)
- Production materializer: [`apply_target_repair.py`](https://github.com/teamleaderleo/fieldwork/blob/ccaa28e40c5689aec7ad78c7f18c354e9966d7fd/programmes/high-leverage-open-source/scouts/upstash-box-cancel-receipts/target-materialization/apply_target_repair.py)
- Follow-up materializer: [`apply_sync_test_repair.py`](https://github.com/teamleaderleo/fieldwork/blob/ccaa28e40c5689aec7ad78c7f18c354e9966d7fd/programmes/high-leverage-open-source/scouts/upstash-box-cancel-receipts/target-materialization/apply_sync_test_repair.py)
- TypeScript controls: [`fieldwork-cancel-receipt-repair.test.ts`](https://github.com/teamleaderleo/fieldwork/blob/ccaa28e40c5689aec7ad78c7f18c354e9966d7fd/programmes/high-leverage-open-source/scouts/upstash-box-cancel-receipts/target-materialization/fieldwork-cancel-receipt-repair.test.ts)
- Python controls: [`test_cancel_receipt_repair.py`](https://github.com/teamleaderleo/fieldwork/blob/ccaa28e40c5689aec7ad78c7f18c354e9966d7fd/programmes/high-leverage-open-source/scouts/upstash-box-cancel-receipts/target-materialization/test_cancel_receipt_repair.py)

## Claims requiring judgment

| Claim or design choice | Evidence | Reviewer question |
| --- | --- | --- |
| separate request receipt is the smallest truthful API | model comparison, historical target execution, Google/Temporal contract context | does the additive API justify its public surface? |
| request-state value is named `accepted` | local HTTP settlement only; endpoint contract unknown | should the value be `sent`, `acknowledged`, or another narrower term? |
| failed receipt stays cached | no-replay controls | should deliberate retry exist now or later? |
| first-owner weak map is the smallest abort repair | Box source, Ky ownership pattern, race analysis | is module-local controller ownership acceptable to maintainers? |
| cancellation-specific rejection plus `detached` | target early-break semantics and open CLI PR #82 | does this preserve desired iterator and CLI behavior? |
| local observer shutdown is agent-stream-specific | exact constructors | narrow the claim or widen command/code streams? |
| single-flight is per run object | exact constructors and local fields | is the narrowed scope acceptable? |
| Python coordinator belongs outside generated client | deterministic generation and parity | does target prefer a fallback module or current mapping? |

## Selected repair inspection

Confirm the implementation has these exact properties:

1. one private helper records the owner only when the controller is not already aborted;
2. timeout and cancellation-request paths both use the helper;
3. later abort attempts cannot overwrite the first owner;
4. cancellation-request `AbortError` does not write terminal status;
5. cancellation-request path still rejects the iterator with non-timeout prose;
6. existing iterator `finally` retains partial output and publishes `detached`;
7. timeout behavior remains covered separately;
8. controller replacement does not inherit stale ownership;
9. public claims name agent stream rather than all stream types unless command/code controllers are added.

## Known risks

- Cancellation-specific error prose is an observable change from the current false `Stream timed out` message.
- Open CLI PR #82 is unmerged compatibility evidence and may change.
- `detached` corrects status truthfulness but may differ from caller expectations built around local `cancelled`.
- Agent stream has controller ownership; command/code streams currently do not.
- Failure caching blocks automatic retry.
- Request-state naming may overstate endpoint evidence.
- Timeout callbacks appear not to be cleared in inspected agent paths; retained as adjacent, unexecuted context.
- No current owned target branch exists.

## Evidence limits

- Historical exact target, one Ubuntu environment.
- Local mocked requests.
- No hosted endpoint or provider behavior.
- No current-head target execution.
- Related repositories support interface reasoning only.
- No eligible independent acceptance.

## Staleness check

- Current upstream head checked: `9f7533c645f6b519f612aa977f6f4acf86655db7`
- Candidate base relationship: executed base is four commits behind
- Relevant source paths changed since execution: no in inspected compare
- Duplicate/overlap search date: `2026-08-01`
- Open replacement work found: none
- Open compatibility consumer checked: PR #82 at `fce8c8c...`
- Packet reflects the latest `REPAIR` disposition

## Source cleanliness

- [ ] Clean owned target branch exists.
- [x] Retained historical patch inventory is complete.
- [x] Temporary workflow is absent from workflow-free carrier.
- [ ] First-owner TypeScript repair is materialized.
- [ ] Fieldwork-named tests are renamed/integrated.
- [x] No dependency change is selected.
- [ ] Commit-pinned links resolve to a renewed candidate head.

## Test review

- [x] Historical intended isolated assertions ran.
- [x] Baseline/candidate relationship is clear.
- [x] Setup and product failures are separated.
- [x] Exact real-stream and race controls are specified.
- [ ] Complete TypeScript agent-stream failure path covered.
- [ ] Timeout/cancel race orders covered.
- [ ] Same-ID two-wrapper scope covered.
- [ ] Command/code stream boundary covered.
- [ ] CLI catch-flow compatibility covered.
- [x] Historical compatibility controls exist.
- [x] Platform and integration limits are explicit.
- [x] Historical ordinary gates are named accurately.
- [ ] Current-head ordinary gates run.

## Draft review

- [x] Issue draft avoids impact/prevalence claims.
- [x] PR draft describes selected direction and blocker.
- [x] Target terminology is used.
- [x] Internal process vocabulary stays outside proposed public body.
- [ ] Receipt request-state name is settled.
- [ ] Agent-only observer scope is reflected in final public text.
- [ ] Current AI disclosure requirement checked at submission time.

## Reviewer disposition

`REPAIR`

Reviewed source: historical patch `d30874c...`; current source `9f7533c...`; selected repair unmaterialized  
Reviewed packet head: latest #435 handoff  
Reason: exact repair and reversing tests are now selected, but no target source or execution proves them.  
Clearing condition: materialize first-owner abort classification, settle naming/scope, execute real pending-read/race/boundary controls and complete current-head gates, then retain a new exact patch/receipt.  
Reviewer eligibility: self-review only

## Human deep-dive guide

Focus on:

1. first-owner race semantics;
2. cancellation-specific error plus `detached` compatibility;
3. agent-stream versus command/code scope;
4. receipt request-state vocabulary;
5. cached failure receipt and retry policy;
6. per-object identity scope;
7. direct PR after repair versus issue-first naming discussion.

Suggested response:

`Unit 27 remains REPAIR until the selected real stream path is materialized and executed`  
—or—  
`Unit 27 concern: <specific source, test, compatibility, naming, or scope issue>`
