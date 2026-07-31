# Malformed canonical authority timestamp repair

Parent: PR #366 exact head `fa890d72589d36c6a0275c969183c9bf5bb3d37f`  
Source blob: `reconcile.py@9e664220b3b024b92cbbc4444c15e87545cbd3cd`  
Work class: deterministic mechanism repair  
Upstream contact authorized: no

## Defect

`_authority_conditions()` parses a canonical `expires_at` directly in the condition:

```python
if expires_at is not None and _parse_time(expires_at) <= now:
```

A malformed string, timezone-naive string, or non-string value raises before any projection is returned. One bad action therefore aborts reconciliation for every unrelated action, source condition, carrier condition, and continuity record.

The existing base control deliberately records this crash. PR #366 protects retained derived fields after a projection exists; it cannot reproduce or validate a projection that canonical reconciliation never produced.

## Selected repair

Parse each non-null action expiry inside a bounded `try` block.

On `TypeError` or `ValueError`:

- set only that action's effective authority to `denied`;
- emit `AuthorityUsable = Unknown / InvalidAuthorityTime`;
- preserve the exact malformed input in the condition receipt;
- continue reconciling unrelated actions.

Valid expired, current, denied, absent, revocation-bounded, revoked, and unresolved paths remain unchanged.

## Executable controls

The disposable regression:

1. proves the exact parent source blob;
2. proves the patch applies with `git apply --check` and zero fuzz;
3. retains the baseline whole-reconciliation `ValueError` negative control;
4. covers malformed text, timezone-naive text, and a non-string value;
5. requires only the malformed action to become `Unknown / InvalidAuthorityTime` and denied;
6. requires an unrelated bounded action to remain authorized;
7. requires a current revocation-bounded action to remain authorized;
8. composes the patched projection through PR #366's derived-integrity/currentness helper;
9. proves canonical record and live facts remain byte-for-byte unchanged.

## Boundary

This repair treats malformed per-action canonical expiry as a fail-closed action fact. A malformed global `observed_at` remains a projection-wide invalid observation boundary and is not reclassified here. Schema admission that prevents malformed canonical records before reconciliation remains a complementary control.

This stack carries a patch and execution harness only. A later composition may apply the one-source hunk to the canonical reconciliation branch, update the parent crash expectation, and rerun the complete observed-generation suite. No merge, production mutation, lease change, credentials, private data, spending, deployment, or public upstream interaction is included.
