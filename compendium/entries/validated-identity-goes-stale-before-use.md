# Validated identity goes stale before use

## Metadata

```json
{
  "schema": 1,
  "id": "validated-identity-goes-stale-before-use",
  "kind": "bug-species",
  "maturity": "supported",
  "facets": {
    "domains": ["filesystems", "auth", "controllers"],
    "concerns": ["authority", "identity", "state-consistency"],
    "mechanisms": ["validation", "caching", "deferred-action"],
    "triggers": ["replacement", "credential-change", "filesystem-change"]
  },
  "aliases": ["stale-authority-between-check-and-use", "validated-name-rebound-before-action"],
  "relations": [
    {"type": "violates", "target": "validated-identity-must-match-used-identity"}
  ],
  "cases": [
    "teamleaderleo/fieldwork#406",
    "teamleaderleo/fieldwork#471",
    "teamleaderleo/linux-fieldwork#164"
  ]
}
```

## In simple words

The system validates or selects one identity, retains a weaker token for later use, and then acts after the authority context or object binding has changed.

Three different-looking cases share the shape:

```text
filesystem: validate contained path → ancestor changes → later pathname mutation

auth: select/cache account under credential A → credential changes → cached account reused

cleanup: validate destination at setup → persist marker → filesystem changes → later destructive cleanup
```

## Typical signatures

- check and use are separated by `await`, restart, callback, or durable storage;
- a pathname is returned from validation and dereferenced later;
- a cache key omits the identity or authority generation that made the value valid;
- a durable marker stores text rather than a capability/contained identity;
- configuration, credentials, allowed roots, symlinks, or generations can change between check and action;
- static validation tests pass while replacement/race tests fail.

## Hunting questions

- What exactly was proven at validation time?
- What token carries that proof forward?
- Can that token be rebound to another object?
- Which context changes invalidate the proof?
- Can use operate through a pinned handle/capability instead of re-resolving a name?
- If revalidation is used, what race remains after the last check?

## Repair shapes

Depending on the boundary:

```text
validate + act through one identity-bearing primitive
```

or:

```text
capture non-secret authority generation
→ detect context change
→ revalidate before use
```

or:

```text
persist canonical contained identifier
→ full cleanup preflight
→ revalidate current resolution immediately before action
```

Do not choose a filesystem repair merely because an auth cache has the same abstract shape; the invariant transfers more readily than the mechanism.

## Regression shape

Establish a valid baseline, pause after validation/selection, replace one identity-bearing dependency, then resume the unchanged action. Assert either safe rejection or action against the newly revalidated intended object.

## Limits and counterexamples

This is broader than classic pathname TOCTOU and therefore easier to overapply. The entry requires a real authority/identity change between validation and use. Ordinary stale data that affects performance but not which object may be acted on belongs elsewhere.
