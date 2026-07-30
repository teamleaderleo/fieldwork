# Fieldwork repository admission and capability gate

Date: 2026-07-31  
Fieldwork lane: #244  
Parent campaign: #86  
Programme: #14  
Primary target hub: #8  
Owned testbed: `teamleaderleo/fieldwork`  
Worker: Rook (`agent:rook-20260731`)  
Canonical branch: `fieldwork/codex/fieldwork-repository-admission-v2`  
Original carrier: closed PR #251  
Replacement carrier: draft PR #259  
Upstream contact authorized: `false`

## In simple words

Fieldwork has a candidate repository contract and a deterministic admission check for workers that arrive with incomplete or stale tools. The check records five capability phases, blocks missing reads, permits verified read-only work when mutation routes disappear, and sends proposed alternate routes through Campaign #86's authority and execution-certainty classifier.

Complete-diff review found two incomplete-evidence paths in the first replacement: an authority-equivalent route could be admitted with omitted fields, and a partial comparison could still reach an approval or blocked decision. The current carrier requires every fallback comparison to cover the full declared authority field set before any classifier decision is accepted.

## Question

Can a repository-local Stensibly attachment plus the Campaign #86 fallback classifier decide whether a client may begin requested work before consequential dispatch?

## Source boundary

- Fieldwork original base: `0ffc6d284ca8ac2d1ea0150ac7707e8a64697157`
- Restored base after connector cleanup: `33c57f7597ab1b4f6d0cb6adacf7cc7814362f35`
- Main reviewed for the replacement draft: `896a617c4b4dd8dd9fb9493d05f801c7baf9ade3`
- Stensibly attachment-contract base: `7500506d6b9d451d12b2f6ef492ac46b496c3d6e`
- Campaign #86 classifier: `campaigns/0006-authority-aware-capability-fallback/artifacts/classify_fallback.py`
- Original reviewed head: `17d4fc3dd17e0f7a37516aa38a8767eca9ade591`
- Initial authority repair commits: `f7a515ce168df73124135c996c66f85cd15c53a6` and `5676a1afe066568a572e148aa98751b434018e1d`
- Complete-comparison repair commits: `92a0a44da24cff655530f5c42daace839e5ccafa` and `f2ff5d17e999592def29d56d0491e65de0016ef5`
- Public Codex source remains read-only.

## Static project attachment

Root `STENSIBLY.md` declares the Fieldwork repository, runner profiles, bounded concurrency, autonomous inspect/propose/draft-PR actions, mandatory approval gates, and named checks. It is policy and display context. Live claims, leases, approvals, credentials, capabilities, execution certainty, and dispatch authority remain server-owned.

## Admission receipt

The evaluator consumes:

- request identity and operation kind;
- required capability IDs classified as read or potential mutation;
- route provenance;
- `advertised`, `registered`, `discoverable`, `callable`, and `executable` observations;
- optional fallback inputs using the Campaign #86 classifier contract.

Each phase is `present`, `absent`, or `unknown`. A receipt that becomes present after an earlier absent or unknown phase is invalid.

The output is:

- `ready` — every required capability is executable or has a fully evidenced authority-equivalent fallback;
- `degraded_read_only` — required reads remain executable while mutation capability is absent;
- `require_explicit_approval` — a complete comparison contains a named authority change requiring approval;
- `blocked` — required reads are missing or a complete comparison causes Campaign #86 to fail closed.

## Authority-completeness repair

The original carrier accepted an arbitrary fallback object. The shared classifier defaults an omitted delta list to an empty comparison, permits absent binding-generation values in its digest, and treats omitted reversibility differently from explicit `false`. That combination could produce `allow_equivalent` without a complete comparison.

The first replacement closed the equivalent-route path but still allowed partial authority lists to reach approval or fail-closed outcomes. The current evaluator enforces completeness before invoking the classifier, so every fallback decision receives the same full comparison boundary.

The current evaluator requires:

1. exact fallback-input keys;
2. non-empty operation IDs, absence reason, execution certainty, captured and proposed binding generations, and route provenance;
3. strict boolean logical-identity and reversibility receipts;
4. a non-empty authority-delta list with exact keys, valid relations, and unique fields;
5. exactly one relation for each of account binding, provider, approval subject, actor delegation, user visibility, credential binding, permission scope, resource scope, audit, idempotency, rollback, and recovery;
6. rejection of omitted, empty, partial, duplicate, unknown, or contradictory comparisons before any ready, approval, or blocked decision.

## Decision precedence

1. Reject malformed, partial, unknown, or contradictory receipts.
2. Block any Campaign #86 `fail_closed` result from a complete comparison.
3. Block a missing required read capability.
4. Request approval for a named authority change from a complete comparison.
5. Degrade a missing mutation capability to read-only work.
6. Admit complete direct capability or a fully evidenced equivalent route.

An ambiguous prior mutation remains blocked even when replacement authority compares equal.

## Case matrix

The retained matrix contains 14 cases:

```text
14 cases
2 ready
1 degraded_read_only
1 require_explicit_approval
3 blocked
7 invalid
0 expectation mismatches
```

The seven invalid controls cover contradictory phase revival, omitted deltas, empty deltas, partial mutation authority, empty binding generation, omitted reversibility, and partial read authority. The approval and ambiguous-prior controls now carry complete 12-field comparisons.

Evidence class: `model-executed` for the deterministic matrix. Repository execution requires exact-head workflow receipts from PR #259.

## Connector execution deviation

The first write attempt passed `branch_name` to an action whose accepted field is `branch`. Five candidate files landed transiently on `main`, then were deleted in five cleanup commits. The tree was restored at `33c57f7597ab1b4f6d0cb6adacf7cc7814362f35`. Those transient commits remain execution-path evidence and carry no accepted product disposition.

## Evidence boundary

This carrier proves an owned-repository admission model and deterministic synthetic cases. It does not prove hosted Stensibly import, Codex runtime dispatch, live connector semantics, trusted comparator provenance, production approval UI, provider behavior, or wider adoption.

## Rollback

Delete `STENSIBLY.md`, this lane directory, and `.github/workflows/issue-244-repository-admission.yml`. The carrier changes no production state, credential, provider configuration, deployment, or external repository.

## Next integration gate

After exact-head CI and independent review:

1. import the attachment through Stensibly's versioned preview and acceptance path;
2. bind capability receipts to accepted attachment identity, source revision, and trusted comparator identity;
3. expose admission as a read-only preflight before claim or dispatch;
4. keep GitHub issue and commit identity as recovery when client tools disappear;
5. run fresh-session and resumed-session trials with synthetic operation identities.

## Handoff state

State: `draft repair candidate — exact-head CI and independent review required`.
