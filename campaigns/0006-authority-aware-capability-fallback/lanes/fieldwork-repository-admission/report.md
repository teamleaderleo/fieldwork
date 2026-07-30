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

Complete-diff review found three incomplete-admission paths across the carrier generations:

1. an authority-equivalent route could be admitted with omitted authority facts;
2. a partial authority comparison could still reach approval or blocked;
3. a mutation-only request could receive `degraded_read_only` with zero executable read routes.

The current carrier requires every fallback comparison to cover the full declared authority field set and requires one directly executable or authority-equivalent read capability before degradation.

## Question

Can a repository-local Stensibly attachment plus the Campaign #86 fallback classifier decide whether a client may begin requested work before consequential dispatch?

## Source boundary

- Fieldwork original base: `0ffc6d284ca8ac2d1ea0150ac7707e8a64697157`
- Restored base after connector cleanup: `33c57f7597ab1b4f6d0cb6adacf7cc7814362f35`
- Main reviewed for the replacement draft: `896a617c4b4dd8dd9fb9493d05f801c7baf9ade3`
- Stensibly attachment-contract base: `7500506d6b9d451d12b2f6ef492ac46b496c3d6e`
- Campaign #86 classifier: `campaigns/0006-authority-aware-capability-fallback/artifacts/classify_fallback.py`
- Original reviewed head: `17d4fc3dd17e0f7a37516aa38a8767eca9ade591`
- Complete-authority comparison head: `20a3eaef6db81c15ee2e0e725d180277990cff7c`
- Mutation-only discriminator head: `831ba998af5c9ffd811b9f3352853c63b4ecf6cd`
- Executable-read degradation repair source: `63ced110236929841a3afd1b9d9642627498ab24`
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
- `degraded_read_only` — at least one required read route is admitted while one or more required mutation routes remain unavailable;
- `require_explicit_approval` — a complete comparison contains a named authority change requiring approval;
- `blocked` — required reads are missing, no executable read-only work remains, or a complete comparison causes Campaign #86 to fail closed.

The receipt also lists admitted read capabilities so the degradation claim is inspectable.

## Authority-completeness repair

The original carrier accepted an arbitrary fallback object. The shared classifier defaults an omitted delta list to an empty comparison, permits absent binding-generation values in its digest, and treats omitted reversibility differently from explicit `false`. That combination could produce `allow_equivalent` without a complete comparison.

The first replacement closed the equivalent-route path but still allowed partial authority lists to reach approval or fail-closed outcomes. The current evaluator enforces completeness before invoking the classifier, so every fallback decision receives the same full comparison boundary.

The evaluator requires:

1. exact fallback-input keys;
2. non-empty operation IDs, absence reason, execution certainty, captured and proposed binding generations, and route provenance;
3. strict boolean logical-identity and reversibility receipts;
4. a non-empty authority-delta list with exact keys, valid relations, and unique fields;
5. exactly one relation for each of account binding, provider, approval subject, actor delegation, user visibility, credential binding, permission scope, resource scope, audit, idempotency, rollback, and recovery;
6. rejection of omitted, empty, partial, duplicate, unknown, or contradictory comparisons before any ready, approval, or blocked decision.

## Executable-read degradation repair

The complete-comparison head still returned `degraded_read_only` whenever an unavailable mutation capability remained and no higher-precedence result existed. That rule admitted a mutation-only request with zero read capabilities.

Review `4823835807` established the missing invariant: **degradation requires admitted read work.**

The repair tracks required read capabilities that are either directly executable or admitted through an authority-equivalent fallback. When unresolved mutation capability remains:

- one or more admitted reads produce `degraded_read_only`;
- zero admitted reads produce `blocked` with `mutation_capability_missing:no_executable_read_only_work`.

The existing positive degradation case retains an executable `github.read` route while `github.write` is absent. A separate mutation-only discriminator expects blocked.

## Decision precedence

1. Reject malformed, partial, unknown, or contradictory receipts.
2. Block any Campaign #86 `fail_closed` result from a complete comparison.
3. Block a missing required read capability.
4. Block unavailable mutation work when zero admitted read capabilities remain.
5. Request approval for a named authority change from a complete comparison.
6. Degrade unavailable mutation capability only when admitted read work remains.
7. Admit complete direct capability or a fully evidenced equivalent route.

An ambiguous prior mutation remains blocked even when replacement authority compares equal.

## Case matrix

The retained primary matrix contains 14 cases:

```text
14 cases
2 ready
1 degraded_read_only
1 require_explicit_approval
3 blocked
7 invalid
0 expectation mismatches
```

A fifteenth standalone discriminator covers mutation-only absence and expects `blocked`.

The seven invalid controls cover contradictory phase revival, omitted deltas, empty deltas, partial mutation authority, empty binding generation, omitted reversibility, and partial read authority. The approval and ambiguous-prior controls carry complete 12-field comparisons.

Evidence class: `model-executed` after exact-head workflows pass. Repository execution requires the issue #244 workflow, Fieldwork integrity, and Campaign #86 classifier on one source generation.

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

State: `repair candidate — exact-head CI and independent review required`.
