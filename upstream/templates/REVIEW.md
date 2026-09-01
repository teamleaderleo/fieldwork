# Review — <unit and title>

## In simple words

<State the proposed contribution, what is already supported, and the main thing a final reviewer should challenge.>

## Review subject

- Work class:
- Target repository:
- Proposed upstream base:
- Canonical source branch:
- Exact source head:
- Fieldwork packet branch:
- Exact packet head:
- Complete changed-file fence:
- Upstream-contact authority:

## Review reading order

1. [`README.md`](./README.md)
2. [`DEEP_DIVE.md`](./DEEP_DIVE.md)
3. [`APPROACHES.md`](./APPROACHES.md)
4. [`TESTS.md`](./TESTS.md)
5. exact product diff
6. exact test diff
7. [`UPSTREAM_ISSUE.md`](./UPSTREAM_ISSUE.md)
8. [`UPSTREAM_PR.md`](./UPSTREAM_PR.md)

## Exact diff links

- complete compare:
- production files:
- tests:
- generated or dependency files:

## Claims requiring judgment

| Claim or design choice | Evidence | Reviewer question |
| --- | --- | --- |
| `<claim>` | `<exact link>` | `<challenge>` |

## Known risks

- `<risk and current mitigation>`

## Evidence limits

- `<limit>`

## Staleness check

- Current upstream head checked:
- Candidate base relationship:
- Relevant source paths changed upstream since execution: `yes | no | unclear`
- Duplicate/overlap search date:
- Open replacement work found:
- Packet and target PR descriptions synchronized:

## Source cleanliness

- [ ] No Fieldwork-only files in target source diff.
- [ ] No temporary workflows or publishers.
- [ ] No stale execution artifacts.
- [ ] No unrelated formatting or generated churn.
- [ ] Required snapshots or lock changes are explained.
- [ ] Commit-pinned links resolve to the reviewed head.

## Test review

- [ ] Intended assertion actually ran.
- [ ] Baseline/candidate relationship is clear.
- [ ] Setup and product failures are separated.
- [ ] Failure and cleanup paths are covered.
- [ ] Compatibility controls are present.
- [ ] Platform and integration limits are explicit.
- [ ] Ordinary target gates are named accurately.

## Draft review

- [ ] Issue draft does not oversell impact or prevalence.
- [ ] PR draft describes the actual current diff.
- [ ] Target terminology and contribution format are used.
- [ ] Internal process vocabulary and private context are absent.
- [ ] AI disclosure requirement was checked, not assumed.

## Reviewer disposition

`ACCEPT | REPAIR | HOLD | EXECUTE | REJECT`

Reviewed source head: `<sha>`  
Reviewed packet head: `<sha>`  
Reason: `<reason>`  
Clearing condition: `<exact next action>`  
Reviewer eligibility: `<independent | self-review only>`

## Human deep-dive guide

The final human reviewer should focus on:

1. `<most consequential design choice>`
2. `<highest compatibility risk>`
3. `<largest evidence gap>`
4. `<whether issue-first or direct PR is the better route>`

Suggested response:

`Unit <NN> looks ready for upstream preparation`  
—or—  
`Unit <NN> concern: <specific source, test, compatibility, or framing issue>`
