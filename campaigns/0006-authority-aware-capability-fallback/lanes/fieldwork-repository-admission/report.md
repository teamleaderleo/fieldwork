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

- Fieldwork base: `0ffc6d284ca8ac2d1ea0150ac7707e8a64697157`
- Stensibly attachment-contract base: `7500506d6b9d451d12b2f6ef492ac46b496c3d6e`
- Campaign #86 fallback classifier consumed from:
  `campaigns/0006-authority-aware-capability-fallback/artifacts/classify_fallback.py`
- Working branch: `fieldwork/codex/fieldwork-repository-admission`
- Public Codex source remains read-only.

## Current behaviour

Fieldwork's repository rules and GitHub records describe assignments, ownership, evidence, review, and handoff. The repository had no root `STENSIBLY.md`, and no executable repository-admission layer joined those durable rules to the client's currently observed capabilities.

Campaign #86 already classifies a proposed fallback route as:

- `allow_equivalent`;
- `require_explicit_approval`;
- `fail_closed`.

That classifier protects authority and mutation certainty after a route is missing. It does not decide whether the complete repository workload can begin.

## Candidate behaviour

### Static project attachment

Root `STENSIBLY.md` declares:

- project `fieldwork` and repository `teamleaderleo/fieldwork`;
- runner profiles `chatgpt-connected` and `codex-default`;
- project concurrency 4 and global concurrency 12;
- autonomous `inspect`, `propose`, and `create_draft_pr` actions;
- mandatory approval gates for merge, deploy, external messaging, provider or broad-permission change, credentials, destructive cleanup, and spend;
- named checks for Fieldwork integrity, the repository-admission matrix, and interaction-reference policy.

The attachment remains static policy and display context. It grants no live capability, claim, lease, approval, credential, or execution authority.

### Admission receipt

The evaluator consumes one versioned request with:

- request identity and operation kind;
- required capability IDs classified as read or potential mutation;
- one route provenance per observed capability;
- `advertised`, `registered`, `discoverable`, `callable`, and `executable` observations;
- optional fallback inputs using the exact Campaign #86 classifier contract.

Each phase is `present`, `absent`, or `unknown`. A receipt that becomes present after an earlier absent or unknown phase is rejected as contradictory.

The output is one of:

- `ready` — every required capability is executable or has an authority-equivalent fallback;
- `degraded_read_only` — required reads remain executable while one or more mutation capabilities have no admitted fallback;
- `require_explicit_approval` — a proposed route changes named authority and Campaign #86 requests approval;
- `blocked` — required reads are missing, a read request lacks any required route, or Campaign #86 fails closed.

The output retains per-capability absence reason, route provenance, fallback decision, fallback reason, and authority-delta digest. It stores no credentials, request bodies, issue bodies, or arbitrary provider output.

## Decision precedence

1. A contradictory receipt is invalid.
2. A Campaign #86 `fail_closed` result blocks the repository request.
3. A missing required read capability blocks the request.
4. A Campaign #86 approval result requests explicit approval.
5. Missing mutation capability with usable reads becomes `degraded_read_only`.
6. Complete direct or equivalent capability becomes `ready`.

This keeps an ambiguous prior mutation blocked even when the replacement route has equal authority.

## Case matrix

The retained matrix covers:

1. complete direct GitHub and Stensibly capability — `ready`;
2. executable reads with absent mutation routes — `degraded_read_only`;
3. a substitute connector using changed account and provider — `require_explicit_approval`;
4. equal-authority fallback after local timeout with unknown outcome — `blocked`;
5. unknown GitHub read discovery — `blocked`;
6. equal-or-narrower fallback before dispatch — `ready`;
7. a read request whose declared required route is absent — `blocked`;
8. a phase receipt that revives after absence — invalid.

A local dependency-free harness using the same evaluator interface produced:

```text
8 cases
2 ready
1 degraded_read_only
1 require_explicit_approval
3 blocked
1 invalid
0 expectation mismatches
```

Evidence class: `model-executed` for evaluator flow and deterministic output. Exact repository integration with the merged Campaign #86 classifier requires the branch CI receipt.

## Change thesis

**Current behaviour:** repository policy and live tool availability are separate, and workers must infer whether they can safely begin.

**Consequence:** a missing mutation tool can invite an improvised route with different authority, while a stale or unknown read route can leave the worker unable to reconcile GitHub truth.

**Improvement:** one deterministic admission receipt classifies the complete request before dispatch and reuses the existing fallback authority gate.

**Evidence:** synthetic direct, degraded, approval, ambiguity, equivalent-fallback, read-loss, and contradictory-receipt cases.

**Boundary:** the result establishes one owned repository interface. It does not establish Codex host integration, Stensibly hosted import, ecosystem adoption, live browser or connector semantics, or production approval UX.

## Rollback

Delete `STENSIBLY.md`, this lane directory, and `.github/workflows/issue-244-repository-admission.yml`. No production state, credential, provider configuration, external repository, or deployment is touched.

## Next integration gate

After exact-head CI and independent review:

1. import the root attachment through Stensibly's versioned preview and acceptance path once the hosted path is available;
2. bind observed client capability receipts to the accepted attachment identity and source revision;
3. expose repository admission as a read-only preflight before claim or dispatch;
4. preserve GitHub issue and commit identity as the recovery source when Stensibly or client tools disappear;
5. run one fresh-session and one resumed-session Fieldwork trial with synthetic operations and exact operation identities.

## Handoff state

State: `candidate — exact branch CI and independent review required`.
