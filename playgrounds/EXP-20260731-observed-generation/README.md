# Observed-generation reconciliation pilot

State: `target-test-prepared`  
Owning issue: #325  
Parent proposal: #300  
Provisional state vocabulary: PR #306 at `a9337a3dc2b3e84b4eac834b1f48a18dc13a1519`  
Upstream contact authorized: `false`

## In simple words

This experiment asks whether a small read-only controller can report current, stale, false, and unknown coordination facts without rewriting the records it inspects.

The model binds every projection to one `observed_generation`. A consumer must reject that projection after the desired record moves to another generation. Missing source, alternative, or revocation facts become `Unknown`; they do not become negative technical conclusions. Authority remains unusable whenever its currentness cannot be established.

## What the model covers

Three fixtures exercise different pressure points:

1. a stopped path that retains its evidence boundary, research avenues, reopening triggers, and smallest safe next probe;
2. a comparative finding with one preferred source, one repair surface, one active comparison, and one retained losing alternative;
3. a canonical source and execution carrier in different repositories with a repository-qualified parent issue.

The retained controls prove:

- exact source/review currentness;
- source movement expiring old review;
- rejection of generation-N output after generation N+1;
- alternative-local review expiry;
- `Unknown` handling for missing live facts;
- fail-closed absent, expired, revoked, and unresolved authority;
- duplicate-carrier conflict without silent selection;
- repository-scoped writer-lease identity;
- terminal continuity visibility;
- byte-preserving success and failure paths.

## Command

```bash
python3 playgrounds/EXP-20260731-observed-generation/test_reconcile.py
```

No network access or third-party package is required.

## Distinguishing result

A green run establishes only the mechanism claim: deterministic generation-bound reconciliation is feasible over the retained fixtures.

It does not establish compatibility with PR #306, production suitability, a complete cockpit, or a safe automatic mutation path. Compatibility requires a pinned green and independently accepted PR #306 generation. Any state field needed by the fixtures but absent from that accepted generation returns as a schema repair request rather than being hidden in controller code.

## Current evidence boundary

The executable model and ten controls are retained on `experiment/325-observed-generation-pilot`. Native workflow execution is pending. Until that receipt exists, the state remains `target-test-prepared`.
