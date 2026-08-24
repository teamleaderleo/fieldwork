# Approaches — unit 21 Jotai async read generation

## In simple words

A per-key generation counter remains the selected direction. It directly represents which read or completed removal currently owns permission to change shared parsed identity. Promise identity can suppress some stale completions, while a broader all-operation generation would also cover writes and subscriptions; both widen or obscure this unit's accepted boundary.

The selected design is now materialized on a clean owned-fork branch at `dfe607d7637fbcf61ae41c39f4f470f61fa7c531`, stacked exactly on unit 20 head `b2f84273b53bbed9df073354dac503e520be7101`. The remaining decision inputs are exact-head workflow conclusions and independent review, not source admission.

## Decision criteria

1. Preserve unit 20's same-key identity behavior and unrelated-key isolation.
2. Fence stale valid and malformed asynchronous completions.
3. Include completed removal as an authority transition.
4. Keep caller-visible backend results and errors unchanged.
5. Keep the source diff narrow enough to stack cleanly after unit 20.
6. Avoid silently claiming write or subscription ordering.

## Selected approach

### Per-key initiation generation

- Design: increment a key-local integer when each read starts and when removal invalidation settles; only the current generation may publish or delete cache state.
- Owning boundary: `createJSONStorage()` because it owns parsed cache identity.
- Evidence: characterization PR #284, accepted repair PR #317, target runs `30623229098` and `30623229114`, the local 11-case model, and the clean target compare `b2f8427...dfe607d`.
- Advantages: directly encodes ordering; naturally includes completed removal; keeps backend values and rejection propagation unchanged; isolates keys.
- Costs and risks: one additional adapter-lifetime map; counter growth; depends on unit 20; exact-head workflow and independent-review evidence remain pending.
- Current source: `teamleaderleo/jotai:fix/utils-async-read-generation` at `dfe607d7637fbcf61ae41c39f4f470f61fa7c531`.
- Remaining controls: record the queued fork workflow conclusions and obtain independent complete-diff review.

## Viable alternatives

### Latest-promise identity

- Design: store the latest backend promise or thenable for each key and let a completion publish only when its promise remains current.
- Why it remains plausible: directly suppresses older asynchronous read completions.
- What it would improve: avoids an explicit integer counter for read/read races.
- What it would widen or complicate: completed removal has no natural promise identity matching an earlier read; synchronous backends and replacement mechanics need separate handling.
- Exact discriminator: a read starts, removal settles, then the read resolves. The design must fence publication without inventing an unrelated sentinel protocol.
- Reopening trigger: a simpler target-native implementation that covers read/read and read/removal with fewer states and equal clarity.

### One generation for every storage operation

- Design: advance one per-key operation generation for reads, writes, removals, and subscription events.
- Why it remains plausible: could define a complete cache authority model.
- What it would improve: covers the known read/write and read/subscription gaps.
- What it would widen or complicate: changes write and external-event semantics, result ownership, settlement ordering, and compatibility beyond this unit.
- Exact discriminator: concurrent read, `setItem`, removal, and subscription matrices with a documented authority contract.
- Reopening trigger: unit 21 cannot remain correct without write/subscription participation, or maintainers request one unified operation model.

## Executed losing approaches

### Completion-order publication

- Exact branch, patch, or commit: unit 20 carrier `d9dd61c4a0d1f9073c300519990e6ba9ec2855d9` plus characterization head `2fb60bd0497d5557afb54d11c3d6d1a31020b312`.
- What ran: five focused characterization cases on Node 22, 24, and 26, adjacent cache tests, existing storage tests, ESLint, Prettier, and TypeScript.
- Result: older completions can replace newer identity and repopulate after completed removal.
- Why it lost: shared cache authority follows scheduler timing instead of request/removal ordering.
- Useful evidence retained: PR #284 and run `30588753020`.

### Unit-21 patch directly on public main

- Exact inputs: Jotai `56a9cc51de8a5dd762b95a145820f12589cc47c9`; unit-21 patch from `34670f709753668827043bbc76c4159a8b36ade2`.
- What ran: local `git apply --check` against the exact source segment.
- Result: failed because public main still has `lastStr`/`lastValue` and lacks unit 20's `cachedValues` map.
- Why it lost: it would either fail mechanically or combine unit 20 into unit 21, violating the numbered contribution boundary.
- Useful evidence retained: [`20260801-local-reconciliation.md`](./receipts/20260801-local-reconciliation.md).

## Rejected easy answers

### Guard only successful parses

- Temptation: prevent stale valid publication and leave malformed behavior unchanged.
- Why incomplete: a stale malformed completion can delete newer valid identity.
- Negative control: the fifth repair test resolves newer valid JSON before an older malformed result.

### Advance generation only when reads complete

- Temptation: order authority by settlement.
- Why incomplete: reproduces completion-order publication and cannot fence an older read before it settles.
- Negative control: reverse completion characterization.

### Advance only on removal initiation

- Temptation: fence crossing reads immediately.
- Why incomplete: unit 20 deliberately preserves identity while asynchronous removal is pending and invalidates on terminal outcome, including commit-then-reject ambiguity.
- Source fact: unit 20 owns settlement timing; unit 21 advances inside its `invalidate()` path.

### Delete the cache on every rejection

- Temptation: treat backend rejection like malformed input.
- Why incomplete: rejection provides no serialized value and can erase valid prior identity. The selected model keeps rejection caller-visible, suppresses older publication through initiation authority, and preserves prior cache identity.

### Merge units 20 and 21 into one proposal without recording the stack

- Temptation: produce one branch directly from public main.
- Why incomplete: #435 counts two separate proposed contributions with different defects, tests, compatibility questions, and review surfaces.
- Reopening trigger: coordinator explicitly supersedes units 20 and 21 with one combined upstream proposal.

## Prior upstream approaches

| Link | Approach | Status | Relationship to this unit |
| --- | --- | --- | --- |
| [Jotai issue #1079](https://github.com/pmndrs/jotai/issues/1079) | mount/subscription consistency for one key | closed | establishes the same-key identity compatibility requirement |
| [Jotai PR #1080](https://github.com/pmndrs/jotai/pull/1080) | adapter-wide `lastStr`/`lastValue` memoization | merged | historical origin of parsed identity caching; complementary prior art |
| [commit `9e336c6...`](https://github.com/pmndrs/jotai/commit/9e336c6bd2bebf257ffca957b0af18f97444323c) | implementation of #1080 | merged | exact prior implementation to preserve for same-key behavior |

Searches on 2026-08-01 for `createJSONStorage async read generation`, `atomWithStorage stale async read`, and related pull requests found no equivalent current repair. The search is a current GitHub search result, not proof that no unindexed or differently worded discussion exists.

## Deferred adjacent work

- `setItem()` versus pending read authority — separate storage-operation ordering question.
- subscription callback versus pending read authority — separate external-event ordering question.
- adapter-lifetime generation retention — follows unit 20's selected policy and shares its dynamic-key reopening trigger.
- public bug discussion route — filing authority remains absent.

## Decision history

| Date | Exact inputs | Decision | Reason | Reopening trigger |
| --- | --- | --- | --- | --- |
| 2026-07-31 | characterization `2fb60bd...`, unit-20 base `d9dd61c4...` | reject completion-order publication | target matrix proves stale publication and removal-crossing repopulation | current source removes the behavior |
| 2026-07-31 | repair head `e99c7d2...`, review `4827783876` | accept per-key generation for direct materialization | six native controls and Node 22/24/26 execution pass | contradictory direct-source execution |
| 2026-08-01 | public main `56a9cc51...`, unit-20 and unit-21 patches | require a stacked source branch | local apply check proves unit 21 depends on unit 20 | unit 20 merges upstream or coordinator combines units |
| 2026-08-01 | 11-case Node `v22.16.0` model | retain rejection semantics and same-string precision | all model controls pass | target-native result differs |
| 2026-08-01 | owned source `b2f8427...dfe607d` | accept clean two-file, two-commit materialization | exact ancestry and complete diff match the packet boundary | exact-head workflows or independent review find a defect |
