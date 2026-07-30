# Fieldwork repository admission and capability gate

Date: 2026-07-30  
Fieldwork lane: #244  
Parent campaign: #86  
Programme: #14  
Primary target hub: #8  
Owned testbed: `teamleaderleo/fieldwork`  
Worker: Rook (`agent:rook-20260731`)  
Upstream contact authorized: `false`

## In simple words

Fieldwork now has a candidate repository contract and a deterministic admission check for workers that arrive with incomplete or stale tools. The check records five separate capability phases, blocks missing read access, permits a read-only degradation when mutation routes disappear, and sends every proposed alternate route through Campaign #86's authority and execution-certainty classifier. A missing tool becomes an observation, never permission.

## Question

Can a repository-local Stensibly attachment plus the accepted authority-fallback classifier decide whether a client may begin requested work before any consequential dispatch?

## Source boundary

- Fieldwork original base: `0ffc6d284ca8ac2d1ea0150ac7707e8a64697157`
- Restored current-main base after connector cleanup: `33c57f7597ab1b4f6d0cb6adacf7cc7814362f35`
- Stensibly attachment-contract base: `7500506d6b9d451d12b2f6ef492ac46b496c3d6e`
- Campaign #86 fallback classifier:
  `campaigns/0006-authority-aware-capability-fallback/artifacts/classify_fallback.py`
- Canonical branch: `fieldwork/codex/fieldwork-repository-admission-v2`
- Public Codex source remains read-only.

## Baseline

Fieldwork's repository rules and GitHub records describe assignments, ownership, evidence, review, and handoff. The repository has no accepted root `STENSIBLY.md`, and no executable repository-admission layer joins those durable rules to the client's currently observed capabilities.

Campaign #86 already classifies a proposed fallback route as `allow_equivalent`, `require_explicit_approval`, or `fail_closed`. That classifier protects authority and mutation certainty after a route is missing. It does not decide whether the complete repository workload can begin.

## Candidate

### Static project attachment

Root `STENSIBLY.md` declares the Fieldwork repository, two runner profiles, bounded concurrency, autonomous inspect/propose/draft-PR actions, mandatory approval gates, and named verification profiles. The attachment remains static policy and display context. It grants no live capability, claim, lease, approval, credential, or execution authority.

### Admission receipt

The evaluator consumes:

- request identity and operation kind;
- required capability IDs classified as read or potential mutation;
- route provenance;
- `advertised`, `registered`, `discoverable`, `callable`, and `executable` observations;
- optional fallback inputs using Campaign #86's classifier contract.

Each phase is `present`, `absent`, or `unknown`. A receipt that becomes present after an earlier absent or unknown phase is rejected as contradictory.

The output is:

- `ready` — every required capability is executable or has an authority-equivalent fallback;
- `degraded_read_only` — required reads remain executable while mutation capability is absent;
- `require_explicit_approval` — Campaign #86 finds a named authority change;
- `blocked` — required reads are missing or Campaign #86 fails closed.

The receipt retains absence reason, route provenance, fallback decision and reason, and authority-delta digest. It stores no credentials, issue bodies, provider payloads, or command output.

## Decision precedence

1. Reject contradictory observations.
2. Block any Campaign #86 `fail_closed` result.
3. Block a missing required read capability.
4. Request approval for a named authority change.
5. Degrade missing mutation capability to read-only work.
6. Admit complete direct or equivalent capability.

This keeps an ambiguous prior mutation blocked even when replacement authority compares equal.

## Case matrix

The retained eight cases cover complete direct capability, read-only degradation, changed-account approval, ambiguous prior mutation, unknown read discovery, equivalent pre-dispatch fallback, a read request with an absent declared route, and contradictory phase revival.

A local dependency-free harness exercising the evaluator contract produced:

```text
8 cases
2 ready
1 degraded_read_only
1 require_explicit_approval
3 blocked
1 invalid
0 expectation mismatches
```

Evidence class: `model-executed` for evaluator flow and deterministic output. Exact integration with the merged Campaign #86 classifier requires the branch CI receipt.

## Connector execution deviation

The first write attempt passed `branch_name` to a connector action whose actual field is `branch`. Five candidate files landed transiently on `main`, then were deleted in five cleanup commits. The final tree was restored at `33c57f7597ab1b4f6d0cb6adacf7cc7814362f35`. The canonical candidate is this `-v2` branch; the transient commits are execution-path evidence and carry no accepted product disposition.

## Change thesis

**Current behaviour:** repository policy and live tool availability are separate, and workers infer whether they can safely begin.

**Consequence:** a missing mutation tool can invite a route with different authority, while stale read capability can remove the recovery path to GitHub truth.

**Improvement:** one deterministic receipt classifies the complete request before dispatch and reuses the existing fallback authority gate.

**Evidence:** direct, degraded, approval, ambiguity, equivalent-fallback, read-loss, and contradictory-receipt cases.

**Boundary:** one owned-repository interface only. Hosted Stensibly import, Codex host integration, live browser or connector semantics, production approval UI, and wider adoption remain open.

## Rollback

Delete `STENSIBLY.md`, this lane directory, and `.github/workflows/issue-244-repository-admission.yml`. No production state, credential, provider configuration, deployment, or external repository is touched.

## Next integration gate

After exact-head CI and independent review:

1. import the attachment through Stensibly's versioned preview and acceptance path when hosted import is available;
2. bind capability receipts to accepted attachment identity and source revision;
3. expose admission as a read-only preflight before claim or dispatch;
4. keep GitHub issue and commit identity as recovery when Stensibly or client tools disappear;
5. run fresh-session and resumed-session trials with synthetic operations and exact operation identities.

## Handoff state

State: `candidate — exact branch CI and independent review required`.
