# Validated identity must match used identity

## Metadata

```json
{
  "schema": 1,
  "id": "validated-identity-must-match-used-identity",
  "kind": "invariant",
  "maturity": "supported",
  "facets": {
    "domains": ["filesystems", "auth", "controllers"],
    "concerns": ["authority", "identity", "state-consistency"],
    "mechanisms": ["validation", "caching", "deferred-action"],
    "triggers": ["replacement", "credential-change", "filesystem-change"]
  },
  "aliases": ["check-and-use-same-object", "revalidate-after-context-change"],
  "relations": [],
  "cases": [
    "teamleaderleo/fieldwork#406",
    "teamleaderleo/fieldwork#471",
    "teamleaderleo/linux-fieldwork#164"
  ]
}
```

## In simple words

An authoritative action must operate on the same logical object and under the same relevant authority assumptions that were validated.

```text
validate object X under context C
        ↓
time / replacement / credential change
        ↓
use name/cache token X under context C'
        ↓
may now refer to a different object or authority
```

The implementation can preserve this invariant by pinning identity, by binding validation and use to one primitive, or by revalidating under the current context immediately before action with an explicit residual-race boundary.

## Useful review questions

- What exact object/authority did validation prove?
- What representation survives between validation and use: pathname, account ID, cache key, generation, handle, descriptor?
- Which parts of the environment can change before use?
- Does the later operation dereference the validated identity again?
- Can the caller change credentials, allowed roots, namespace, symlink structure, or generation in between?
- Is there a stronger handle/capability that can carry identity across the boundary?

## Limits

Revalidation alone does not close every race. On hostile filesystem boundaries, descriptor-relative or capability-like primitives may be required. Conversely, some contexts are immutable for the operation by construction; repeated checks there add noise without strengthening identity.
