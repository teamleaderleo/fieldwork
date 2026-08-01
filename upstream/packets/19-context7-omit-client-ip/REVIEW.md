# Review — unit 19, Context7 client-IP encryption fallback

## In simple words

The retained candidate is technically strong: it owns the failure at the encryption/header boundary, passes focused and complete package tests, preserves unrelated headers, and bounds diagnostics. The decisive review fact is public prior art. Context7 already received the same omission-on-failure contract in issue #1965 and PR #2104, then closed both because the behavior was not intended.

A final reviewer should challenge only whether new maintainer direction exists. Without that, the correct action is retirement.

## Review subject

- Work class: `upstream-fork research / prior-art validation`
- Target repository: `upstash/context7`
- Proposed upstream base: `master@594a73133e14631af8c915a1b4f2c8039c964fe1`
- Canonical source branch: `none; intended fix/omit-client-ip-on-encryption-failure if explicitly reopened`
- Exact owned source head: `none`
- Exact public prior-art source head: `5a36c505e88da3fe74d34ae3f4dd01124031bb88`
- Exact target-executed carrier: `3360d80d8aa90e3eaafea3367ff9dcfd4dfe0345`
- Exact workflow-free retained carrier: `ec5fdb2cf3ce498fb88aa90991699d2c607b1246`
- Fieldwork packet branch: `p0/435-unit-19-context7-omit-client-ip`
- Exact packet head: packet PR and final #435 handoff
- Complete revived changed-file fence: `packages/mcp/src/lib/encryption.ts`, `packages/mcp/test/encryption.test.ts`
- Upstream-contact authority: `none`

## Review reading order

1. [`README.md`](./README.md)
2. [`DEEP_DIVE.md`](./DEEP_DIVE.md)
3. [`APPROACHES.md`](./APPROACHES.md)
4. [`TESTS.md`](./TESTS.md)
5. [retained product/test patch](./patches/malformed-key-omit-metadata.patch)
6. [retained target-native test](./fixtures/malformed-key-omit-metadata.test.ts)
7. [`UPSTREAM_ISSUE.md`](./UPSTREAM_ISSUE.md)
8. [`UPSTREAM_PR.md`](./UPSTREAM_PR.md)
9. [exact execution receipt](./receipts/context7-omit-client-ip-on-encryption-failure.json)

## Exact diff links

- current upstream source: [`encryption.ts@594a731`](https://github.com/upstash/context7/blob/594a73133e14631af8c915a1b4f2c8039c964fe1/packages/mcp/src/lib/encryption.ts)
- exact declined source commit: [`5a36c505`](https://github.com/upstash/context7/commit/5a36c505e88da3fe74d34ae3f4dd01124031bb88)
- Fieldwork retained candidate: [`malformed-key-omit-metadata.patch@ec5fdb2`](https://github.com/teamleaderleo/fieldwork/blob/ec5fdb2cf3ce498fb88aa90991699d2c607b1246/programmes/high-leverage-open-source/scouts/context7-http-boundary/malformed-key-omit-metadata.patch)
- Fieldwork retained test: [`malformed-key-omit-metadata.test.ts@ec5fdb2`](https://github.com/teamleaderleo/fieldwork/blob/ec5fdb2cf3ce498fb88aa90991699d2c607b1246/programmes/high-leverage-open-source/scouts/context7-http-boundary/malformed-key-omit-metadata.test.ts)
- generated or dependency files: `none`

## Claims requiring judgment

| Claim or design choice | Evidence | Reviewer question |
| --- | --- | --- |
| plaintext fallback exists | current source plus PR #343 execution | does any current source or service contract contradict this local observation? |
| omission candidate is narrow and green | run `30635777158`, job `91172880796` | do the named assertions cover the exact changed paths? |
| public default key limits confidentiality claims | current source and PR #2056/Fieldwork review | is any broader privacy language still present? |
| contribution should retire | issue #1965 and PR #2104 close record | has a maintainer since invited the same change? |

## Known risks

- header omission can affect telemetry or service behavior; upstream's public rejection confirms this compatibility concern or product intent is active;
- maintainer rationale is concise, so the exact downstream dependency remains unknown;
- the fixed public default key raises a separate privacy question that can tempt scope expansion;
- old Fieldwork carrier titles may still look contribution-ready unless readers follow this packet and #435 handoff.

## Evidence limits

- local package and source execution only;
- one Linux/Node 22 environment;
- no hosted service, real credentials, Redis, production deployment, or downstream header consumer;
- no eligible independent acceptance of the technical candidate;
- no current public invitation to revisit the declined behavior.

## Staleness check

- Current upstream head checked: `master@594a73133e14631af8c915a1b4f2c8039c964fe1` on `2026-08-01`
- Candidate base relationship: exact tested target is current upstream head
- Relevant source paths changed upstream since execution: `no`
- Duplicate/overlap search date: `2026-08-01`
- Open replacement work found: `no`; exact work is closed and declined
- Packet and retained candidate descriptions synchronized: `yes; candidate is evidence-only`

## Source cleanliness

- [x] Retained target diff contains no Fieldwork-only files.
- [x] Retained workflow-free carrier contains no temporary workflows or publishers.
- [x] Exact execution artifacts are transferred into compact receipts.
- [x] No unrelated formatting or generated churn appears in the target patch.
- [x] No snapshots, lock files, or dependencies change.
- [x] Commit-pinned links resolve to exact reviewed heads.
- [ ] Owned target branch exists; intentionally absent because the unit is retired.

## Test review

- [x] Intended malformed-key and runtime-failure assertions ran.
- [x] Baseline/candidate relationship is explicit.
- [x] Setup and packaging failures are separated from product behavior.
- [x] Both failure paths are covered.
- [x] Valid-key and unrelated-header compatibility controls are present.
- [x] Platform and integration limits are explicit.
- [x] Ordinary target gates are named from exact job logs.

## Draft review

- [x] Issue draft states the exact duplicate and prevents refiling.
- [x] PR draft describes the actual retained two-file candidate.
- [x] Target terminology is used.
- [x] Internal workflow language is outside the archival public draft body.
- [x] No AI-disclosure policy was found in repository search; policy must be rechecked only if filing is later authorized.

## Reviewer disposition

`REJECT`

Reviewed source head: `5a36c505e88da3fe74d34ae3f4dd01124031bb88` as exact declined public prior art; no owned source head  
Reviewed packet head: packet PR and final #435 handoff  
Reason: the exact core implementation and issue were already closed by upstream because omission was not intended; stronger tests and diagnostics do not create a materially different contract.  
Clearing condition: explicit current maintainer direction accepting this behavior or requesting a revised design.  
Reviewer eligibility: `self-review only`

## Human deep-dive guide

The final human reviewer should focus on:

1. whether the maintainer close statement is superseded by any newer public direction;
2. whether a future proposal changes the wire contract materially enough to avoid duplicating PR #2104;
3. whether default-key confidentiality deserves a separate unit without reopening this one;
4. whether internal PR #397 should be closed or relabeled after packet review.

Suggested response:

`Unit 19 retirement confirmed; retain evidence and stop upstream preparation`  
—or—  
`Unit 19 reopening trigger: <specific current maintainer request or materially different contract>`
