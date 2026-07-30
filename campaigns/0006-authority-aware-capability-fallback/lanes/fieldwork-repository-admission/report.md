# Fieldwork repository admission and capability gate

Date: 2026-07-31  
Fieldwork lane: #244  
Parent campaign: #86  
Programme: #14  
Primary target hub: #8  
Owned testbed: `teamleaderleo/fieldwork`  
Worker: Codex lane L  
Upstream contact authorized: `false`

## In simple words

Fieldwork has a candidate repository contract and a deterministic admission check for workers that arrive with incomplete or stale tools. The check records five separate capability phases, blocks missing read access, permits read-only continuation only when at least one required read capability remains executable, and sends every proposed alternate route through Campaign #86's authority and execution-certainty classifier. A missing tool becomes an observation, never permission.

## Question

Can a repository-local Stensibly attachment plus the accepted authority-fallback classifier decide whether a client may begin requested work before any consequential dispatch?

## Source boundary

- Current Fieldwork base: `896a617c4b4dd8dd9fb9493d05f801c7baf9ade3`
- Superseded candidate head: `17d4fc3dd17e0f7a37516aa38a8767eca9ade591`
- Current branch: `fieldwork/codex/repository-admission-v3`
- Stensibly attachment-contract base: `7500506d6b9d451d12b2f6ef492ac46b496c3d6e`
- Campaign #86 fallback classifier:
  `campaigns/0006-authority-aware-capability-fallback/artifacts/classify_fallback.py`
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
- `degraded_read_only` — mutation capability is absent and at least one required read capability remains executable;
- `require_explicit_approval` — Campaign #86 finds a named authority change;
- `blocked` — required reads are missing, read-only recovery is unavailable, or Campaign #86 fails closed.

The receipt retains absence reason, route provenance, fallback decision and reason, and authority-delta digest. It stores no credentials, issue bodies, provider payloads, or command output.

## Review repair from the superseded candidate

Complete-diff review of PR #251 found one admission defect. A mutation-only request with its mutation route absent reached `degraded_read_only` despite declaring no executable read capability. That contradicted the candidate's own rule that read-only continuation exists only while required reads remain executable.

The current successor counts direct or authority-equivalent required read capabilities. An unresolved mutation with zero executable required reads now adds `read_only_recovery_capability_unavailable` and returns `blocked`. The new `blocked-write-absent-without-read` case protects this boundary.

## Decision precedence

1. Reject contradictory observations.
2. Block any Campaign #86 `fail_closed` result.
3. Block a missing required read capability.
4. Block read-only degradation when no required read capability remains executable.
5. Request approval for a named authority change.
6. Degrade missing mutation capability to read-only work.
7. Admit complete direct or equivalent capability.

This keeps an ambiguous prior mutation blocked even when replacement authority compares equal.

## Case matrix

The retained nine cases cover complete direct capability, valid read-only degradation, missing mutation with no read recovery, changed-account approval, ambiguous prior mutation, unknown read discovery, equivalent pre-dispatch fallback, a read request with an absent declared route, and contradictory phase revival.

Expected deterministic summary:

```text
9 cases
2 ready
1 degraded_read_only
1 require_explicit_approval
4 blocked
1 invalid
0 expectation mismatches
```

Evidence class before branch CI: `model-prepared`. Exact integration with the merged Campaign #86 classifier requires the successor branch workflow receipt.

## Change thesis

**Current behaviour:** repository policy and live tool availability are separate, and workers infer whether they can safely begin.

**Consequence:** a missing mutation tool can invite a route with different authority, while absent read capability can erase the durable recovery path while the evaluator still claims read-only continuation.

**Improvement:** one deterministic receipt classifies the complete request before dispatch, reuses the existing fallback authority gate, and proves the read recovery prerequisite before degrading.

**Evidence:** direct, valid degradation, absent recovery, approval, ambiguity, equivalent-fallback, read-loss, and contradictory-receipt cases.

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

State: `candidate — current-main successor awaiting exact-head CI and independent review`.
