# F254-linux-ecosystem-overlap: retain the PPMd lesson without duplicating an active equivalent fix

Finding state: `stopped`

Workstream: `H`  
Canonical Fieldwork issue: `#254`  
Canonical finding path: `findings/F254-linux-ecosystem-overlap/finding.md`  
Investigation workspace: `investigations/254-linux-storage-archive-reproducibility/`  
Canonical implementation: none; overlap record in `teamleaderleo/linux-fieldwork` PRs #214 and #219  
Exact implementation head: overlap record `d9c09cb81c1258612dda601b5bf5f6b703833b8a`  
Exact base or source revision: public equivalent fix observed 2026-07-31 at `78b75ec7c9bca13870cecb5cd4f60272bed86fc9`  
Reviewed input generation: 2026-07-31 read-only public-state refresh  
Current review disposition: `HOLD`  
Desk routing: `not-entered`  
Upstream contact authorized: `no`

## In simple words

A libarchive PPMd decoder case showed that bytes read ahead at the end of one input block could be omitted from consumed-input accounting and replayed on the next read.

Linux Fieldwork had enough source and fixture detail to pursue the bug, but a live refresh found an active public fix covering the same mechanism and boundary. The right action was not to race it with a duplicate implementation.

The technical lesson, exact active-fix head, and future reopening trigger are retained. Independent implementation stays stopped while the equivalent fix remains active.

## Why we care

Duplicate work consumes review capacity and can create conflicting patches for the same defect. The opposite failure is also dangerous: treating an old open pull request as permanently active and never rechecking.

An overlap stop must therefore be exact and perishable. It should preserve enough mechanism detail to recognize equivalence, record the observed head and date, and say what future state would justify reopening.

## What happens if we leave it alone

If the overlap record is absent, a later worker may independently reproduce and patch the same refill-accounting defect while an equivalent fix is already under review. If the record omits date and head, the worker may also assume the fix is still active long after it changed, closed, or shipped.

The retained internal record prevents both mistakes by coupling the stop to one exact read-only observation and requiring a fresh check before branch creation.

## Current finding

At the 2026-07-31 refresh, the public libarchive repair remained open and mergeable at exact head `78b75ec7c9bca13870cecb5cd4f60272bed86fc9` and covered the same PPMd small-buffer mechanism and fixture boundary:

- a decoder reads ahead after exhausting an input block;
- read-ahead bytes are excluded from consumed-input accounting;
- the next refill can replay those bytes;
- the regression crosses the boundary with four 1 KiB entries and 1000-byte input blocks.

Independent implementation is stopped. The case remains useful for parser refill accounting, regression-fixture design, and downstream patch retirement after release adoption.

### Claim table

| Claim | Evidence class | Exact support | Limit |
| --- | --- | --- | --- |
| The live public repair covered the same PPMd refill-accounting mechanism and fixture boundary as the local candidate. | source-read | public PR 3340 at `78b75ec7...`; Linux selection record | No claim of merge, release, or final correctness. |
| The active public repair was open and mergeable on 2026-07-31. | source-read | read-only GitHub state refresh retained in Linux PR #219 | State expires immediately when the public head or status changes. |
| The internal overlap record passed repository CI and merged locally. | full-gate | Linux PR #219 head `d9c09cb8...`; Linux Fieldwork CI `30581903516` / 629 success; merge `d256fd69...` | This validates documentation integrity, not the public product patch. |
| Independent implementation should remain stopped while equivalence and active ownership remain current. | inferred from source-read overlap | programme status and selection rule | A fresh check can reverse the stop. |

## System and ownership map

- Public source owner: libarchive PPMd decoder and its tests.
- Local intake owner: Linux Fieldwork ecosystem scan and programme status.
- Decision owner: the overlap rule decides whether local implementation should begin.
- Evidence owner: exact public head/date, mechanism comparison, environment gate, and local record CI.
- Side effect avoided: duplicate branch, patch, review packet, and possible maintainer burden.
- Reopening owner: the next worker must perform a fresh read-only state and source comparison before branch creation.

## Historical precedent

### Linux Fieldwork promotion-expiry rule

- Source: https://github.com/teamleaderleo/linux-fieldwork/blob/main/programmes/ecosystem-contributions/STATUS.md
- Revision or date: exact internal record merged through PR #219 on 2026-07-30 UTC
- Principle supported: promotion expires when a matching pull request, assignee, claim, or equivalent fix appears; recheck immediately before branch creation.
- Important difference: this finding records one concrete active-fix head and mechanism rather than a general programme rule alone.

### Ecosystem selection record

- Source: https://github.com/teamleaderleo/linux-fieldwork/blob/main/research/rounds/2026-07-30-ecosystem-candidate-scan/selection.md
- Revision or date: latest overlap refresh 2026-07-31
- Principle supported: active fixes remain useful technical references and later downstream-retirement signals even when independent implementation stops.
- Important difference: the record does not endorse or interact with the public patch.

### Downstream patch retirement lane

- Source: https://github.com/teamleaderleo/linux-fieldwork/tree/main/programmes/ecosystem-contributions/lanes/LF-36-downstream-patch-retirement
- Revision or date: retained programme state as of 2026-07-31
- Principle supported: exact upstream fixes and releases can trigger removal of downstream workarounds.
- Important difference: this PPMd case currently owns only an overlap stop and future release-adoption check.

## Approaches considered

### Retained approach: exact active-fix reference plus stop

Preserve the mechanism, fixture, head, date, and reopening trigger. This avoids duplicate implementation without losing the lesson.

### Declined: create a parallel local implementation anyway

The active fix covers the same mechanism and regression. A duplicate would add review cost without a distinct invariant or evidence advantage.

### Declined: record only that “upstream is working on it”

That phrase has no expiry boundary. The exact head, date, and equivalence basis are necessary for future revalidation.

### Deferred: validate the public patch or prepare downstream retirement

Those transitions depend on later public head/release state and a fresh source/package context. The current authority permits read-only observation, not public review or submission.

## Edge cases covered

| Edge case or control | Evidence | Result |
| --- | --- | --- |
| exact public head | 2026-07-31 read-only refresh | `78b75ec7c9bca13870cecb5cd4f60272bed86fc9` retained |
| public state and mergeability | same refresh | open and mergeable at observation time |
| mechanism equivalence | source/fixture comparison in selection record | same refill accounting and small-buffer boundary |
| local stale carrier | PR #142 audit | closed and replaced by current-main PR #214 |
| unique exact-state refinements | PR #219 | merged after CI run 629 success |
| public interaction boundary | programme and initiative records | read only; no comment, review, reaction, or submission |

## Edge cases deferred or outside scope

| Edge case | Why deferred | Owning next record or reopening trigger |
| --- | --- | --- |
| public head changes | current equivalence may expire | fresh read-only source and state check |
| public PR closes unmerged or becomes abandoned | ownership may no longer block local work | re-evaluate exact source and issue state |
| public fix merges but is absent from a needed release | downstream users may still need a bounded patch | LF-36 downstream retirement or package-specific finding |
| material semantic divergence appears | current stop depends on equivalence | reopen as a distinct invariant with a new fixture |
| public review or contact | no authority | explicit user authorization required |

## Exact execution and receipts

| Repository/head | Command or workflow | Platform/environment | Result | Evidence class |
| --- | --- | --- | --- | --- |
| linux-fieldwork@`338e3bc6fcd9d9ab7c89a64720ee92e78a1c1612` | PR #214 documentation/current-main review | owned repository | merged as `4795165508a2781b8a894620be99e00f6178b6b3` | source-read |
| linux-fieldwork@`d9c09cb81c1258612dda601b5bf5f6b703833b8a` | Linux Fieldwork CI `30581903516` / 629 | hosted Linux | success | full-gate for internal record |
| public source@`78b75ec7c9bca13870cecb5cd4f60272bed86fc9` | read-only state and source comparison | GitHub observation, 2026-07-31 | open, mergeable, equivalent mechanism | source-read |

## Complete-diff and compatibility review

- Internal changed-file fence: two files in PR #219, refining the two-file current-main restack in PR #214.
- Current-base relationship: PR #219 base `8d9f7fa9...`; merge commit `d256fd697457eac29862e1073d974813a488725c`.
- Temporary carrier status: stale PR #142 and conflicting PR #209 were closed after content transfer.
- Compatibility surfaces examined: mechanism, fixture boundary, public head/state, local source identity, promotion expiry, and downstream-retirement use.
- Known routine repair remaining: none in the internal overlap record.
- Review eligibility: the internal record is merged and green; the public patch itself was not executed or reviewed for acceptance here.

## Current disposition and desk routing

- Finding state: `stopped`
- Review disposition: `HOLD`
- Review Queue entry: none
- Delivery lane: `not-entered`
- Exact next transition: no independent implementation while equivalent public work remains active
- Clearing condition: a fresh read-only check shows the fix closed, abandoned, materially different, or absent from a required released version
- Required subgates: exact public head/state, source equivalence, and environment need
- Autonomous work remaining: none until a reopening trigger occurs
- Non-delegable human decision: none; public contact would require separate authority if later proposed

## Changes to the canonical conclusion

| Date | Pull request or commit | Change in conclusion |
| --- | --- | --- |
| 2026-07-30 | original ecosystem scan | candidate entered the current-CI queue |
| 2026-07-31 | live overlap refresh | equivalent active public fix found; implementation stopped |
| 2026-07-30 UTC | PR #214 merge `47951655...` | stale local carrier replaced on current main |
| 2026-07-30 UTC | PR #219 head `d9c09cb8...` | exact head/date and promotion-expiry wording merged after run 629 |

## References

- https://github.com/teamleaderleo/linux-fieldwork/pull/214
- https://github.com/teamleaderleo/linux-fieldwork/pull/219
- https://github.com/teamleaderleo/linux-fieldwork/blob/main/programmes/ecosystem-contributions/STATUS.md
- https://github.com/teamleaderleo/linux-fieldwork/blob/main/research/rounds/2026-07-30-ecosystem-candidate-scan/selection.md
- https://github.com/libarchive/libarchive/pull/3340
- Linux Fieldwork CI `30581903516`
