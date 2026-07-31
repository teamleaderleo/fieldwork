# Observed-generation reconciliation pilot

State: `target-test-prepared`  
Owning issue: #325  
Parent proposal: #300  
Parent experiment: PR #327 at `60ba3d2c5d7cff88411ec27a9fb51e9d6ffe223f`  
Provisional state vocabulary: PR #306 at `a9337a3dc2b3e84b4eac834b1f48a18dc13a1519`  
Upstream contact authorized: `false`

## In simple words

This experiment asks whether a small read-only controller can report current, stale, false, and unknown coordination facts without rewriting the records it inspects.

The repaired model binds every projection to:

- the explicit structured-record generation;
- a canonical digest of the structured record;
- the canonical-finding generation;
- the live-fact snapshot generation;
- a canonical digest of the live facts;
- each active carrier's exact observation generation.

A consumer rejects the projection when any required input moves. Canonical digests make a forgotten generation-label bump fail closed in this deterministic pilot. Missing source, alternative, carrier, revocation, or generation facts become `Unknown`; they do not become negative technical conclusions. Authority remains unusable whenever it lacks bounded expiry, a resolved versioned revocation path, or current observation evidence.

## What the model covers

Three fixtures exercise different pressure points:

1. a stopped path that retains and renders its evidence boundary, research avenues, reopening triggers, and smallest safe next probe;
2. a comparative finding with one preferred source, one repair surface, one active comparison, and one retained losing alternative;
3. a canonical source and execution carrier in different repositories with a repository-qualified parent issue.

The repaired controls prove:

- exact source/review currentness;
- source movement expiring old review;
- semantic record movement expiring a projection even when a manual token is unchanged;
- independent spec, finding, and live-fact generation expiry;
- alternative-local review expiry;
- `Unknown` handling for missing live facts;
- fail-closed absent, expired, revoked, unresolved, and permanent-unrevocable authority;
- duplicate-carrier conflict without silent selection;
- carrier head, state, accessibility, check, and observation-generation reconciliation separate from WIP cardinality;
- repository-scoped writer-lease collision detection;
- terminal continuity retained in the compact rendered output;
- byte-preserving success and failure paths.

## Command

```bash
python3 playgrounds/EXP-20260731-observed-generation/test_reconcile.py
```

No network access or third-party package is required.

## Distinguishing result

A green run establishes only the mechanism claim: deterministic exact-input reconciliation is feasible over the retained fixtures.

It does not establish compatibility with PR #306, production suitability, a complete cockpit, lease takeover authority, or a safe automatic mutation path. The lease helper remains a repository-scoped collision detector rather than a complete expiry, renewal, or transfer evaluator. Compatibility requires a pinned green and independently accepted PR #306 generation. Any state field needed by the fixtures but absent from that accepted generation returns as a schema repair request rather than being hidden in controller code.

## Current evidence boundary

The parent ten-control result remains `model-executed`. This repair adds five primary controls and several carrier subcases on `repair/327-complete-observed-generations`; they remain `target-test-prepared` until the exact workflow receipt passes. No merge, release, deployment, data access, spending, automatic mutation, or public upstream interaction is included.
