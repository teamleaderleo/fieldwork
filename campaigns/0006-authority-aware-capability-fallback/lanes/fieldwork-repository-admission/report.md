# Fieldwork repository admission and capability gate

State: `composed repair candidate`

Date: 2026-07-31  
Fieldwork lane: #244  
Parent campaign: #86  
Programme: #14  
Primary target hub: #8  
Owned testbed: `teamleaderleo/fieldwork`  
Canonical branch: `repair/repository-admission-composed`  
Original carrier: closed PR #251  
Partial repair carriers: PR #257 and PR #259  
Composed successor: PR #273  
Upstream contact authorized: `false`

## In simple words

Fieldwork has a candidate repository contract and deterministic admission check for workers that arrive with incomplete or stale tools. It records five capability phases, blocks missing reads, permits read-only degradation only when an executable read route remains, and sends alternate routes through Campaign #86's authority and execution-certainty classifier.

Complete-diff review found three fail-open paths across earlier carriers:

1. an authority-equivalent route could be admitted with omitted evidence;
2. a partial comparison could still reach approval or blocked outcomes;
3. a missing mutation route could be labelled read-only when no readable route existed.

The composed candidate requires a complete 12-field authority comparison before any fallback decision, tracks direct and authority-equivalent readable routes, and rejects boolean schema versions.

## Question

Can a repository-local Stensibly attachment plus the Campaign #86 fallback classifier decide whether a client may begin requested work before consequential dispatch?

## Source boundary

- Fieldwork original base: `0ffc6d284ca8ac2d1ea0150ac7707e8a64697157`
- Restored base after connector cleanup: `33c57f7597ab1b4f6d0cb6adacf7cc7814362f35`
- Main reviewed for the composed draft: `896a617c4b4dd8dd9fb9493d05f801c7baf9ade3`
- Complete-authority source: PR #259 at `20a3eaef6db81c15ee2e0e725d180277990cff7c`
- Readable-recovery source: PR #257 at `61915028c97a0317d277c62a2258443b71e70563`
- Campaign #86 classifier: `campaigns/0006-authority-aware-capability-fallback/artifacts/classify_fallback.py`
- Public Codex source remains read-only.

## Static project attachment

Root `STENSIBLY.md` declares the Fieldwork repository, runner profiles, bounded concurrency, autonomous inspect/propose/draft-PR actions, mandatory approval gates, and named checks. It is policy and display context. Live claims, leases, approvals, credentials, capabilities, execution certainty, and dispatch authority remain server-owned.

## Admission receipt

The evaluator consumes:

- primitive integer schema version;
- request identity and operation kind;
- required capability IDs classified as read or potential mutation;
- route provenance;
- `advertised`, `registered`, `discoverable`, `callable`, and `executable` observations;
- optional fallback inputs using the Campaign #86 classifier contract.

Each phase is `present`, `absent`, or `unknown`. A receipt that becomes present after an earlier absent or unknown phase is invalid.

The output is:

- `ready` — every required capability is executable or has a fully evidenced authority-equivalent fallback;
- `degraded_read_only` — mutation capability is absent while at least one required direct or authority-equivalent read remains executable;
- `require_explicit_approval` — a complete comparison contains a named authority change requiring approval;
- `blocked` — required reads are missing, no readable recovery route exists, or a complete comparison causes Campaign #86 to fail closed.

## Authority-completeness repair

The original carrier accepted an arbitrary fallback object. The shared classifier defaults an omitted delta list to an empty comparison, permits absent binding-generation values in its digest, and treats omitted reversibility differently from explicit `false`. That combination could produce `allow_equivalent` without a complete comparison.

The first replacement closed the equivalent-route path but still allowed partial authority lists to reach approval or fail-closed outcomes. The composed evaluator enforces completeness before invoking the classifier, so every fallback decision receives the same full comparison boundary.

It requires:

1. exact fallback-input keys;
2. non-empty operation IDs, absence reason, execution certainty, captured and proposed binding generations, and route provenance;
3. strict boolean logical-identity and reversibility receipts;
4. a non-empty authority-delta list with exact keys, valid relations, and unique fields;
5. exactly one relation for each of account binding, provider, approval subject, actor delegation, user visibility, credential binding, permission scope, resource scope, audit, idempotency, rollback, and recovery;
6. rejection of omitted, empty, partial, duplicate, unknown, or contradictory comparisons before any ready, approval, or blocked decision.

## Readable-recovery repair

A missing mutation route may degrade only when the requested work retains at least one required read route that is:

- directly executable; or
- accepted by Campaign #86 as authority-equivalent.

A mutation-only request with no executable read recovery blocks with `read_only_recovery_capability_unavailable`. A simultaneous missing read and mutation also blocks through the missing-read reason and the readable-recovery guard.

This makes the decision label truthful: `degraded_read_only` always names an executable mode rather than a hypothetical one.

## Decision precedence

1. Reject malformed, weakly typed, partial, unknown, or contradictory receipts.
2. Block any Campaign #86 `fail_closed` result from a complete comparison.
3. Block a missing required read capability.
4. Block unresolved mutation when no required readable route remains executable.
5. Request approval for a named authority change from a complete comparison.
6. Degrade a missing mutation capability only when readable work remains executable.
7. Admit complete direct capability or a fully evidenced equivalent route.

An ambiguous prior mutation remains blocked even when replacement authority compares equal.

## Deterministic matrices

The authority-completeness base retains 14 cases:

```text
14 base cases
2 ready
1 degraded_read_only
1 require_explicit_approval
3 blocked
7 invalid
0 expectation mismatches
```

The composition matrix adds four discriminating cases:

```text
4 composition cases
0 ready
1 degraded_read_only
0 require_explicit_approval
2 blocked
1 invalid
0 expectation mismatches
```

The added controls require:

- degradation with an authority-equivalent read plus missing mutation;
- blocking mutation-only absence;
- blocking simultaneous missing read and mutation;
- rejecting `version: true`.

The workflow runs each matrix twice, compares byte-identical JSON output, and asserts the exact decision counts.

## Connector execution deviation

The first write attempt passed `branch_name` to an action whose accepted field is `branch`. Five candidate files landed transiently on `main`, then were deleted in five cleanup commits. The tree was restored at `33c57f7597ab1b4f6d0cb6adacf7cc7814362f35`. Those transient commits remain execution-path evidence and carry no accepted product disposition.

The later composition workflow remained queued without starting. Because its transformation was deterministic and fully specified in the carrier, the same composition was applied directly through repository writes. Temporary workflows and trigger material are removed before review.

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

State: `composed repair candidate — exact-head CI and independent complete-diff review required`.
