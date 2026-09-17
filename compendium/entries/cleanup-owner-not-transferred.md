# Cleanup owner not transferred

## Metadata

```json
{
  "schema": 1,
  "id": "cleanup-owner-not-transferred",
  "kind": "bug-species",
  "maturity": "supported",
  "facets": {
    "domains": ["process-lifecycle", "async-runtime", "systems"],
    "concerns": ["resource-ownership", "lifecycle", "recovery"],
    "mechanisms": ["ownership-transfer", "cleanup"],
    "triggers": ["backgrounding", "partial-initialization", "cancellation"]
  },
  "aliases": ["orphaned-cleanup-responsibility"],
  "relations": [
    {"type": "violates", "target": "resource-has-one-cleanup-owner"}
  ],
  "cases": [
    "teamleaderleo/fieldwork#319"
  ]
}
```

## In simple words

A component creates a resource, stops owning cleanup because work moved into another lifecycle phase, but never gives the new lifecycle owner enough information or authority to clean the resource later.

```text
creator allocates resource
       ↓
work becomes background / asynchronous
       ↓
creator suppresses cleanup
       ↓
new owner tracks work but not resource
       ↓
resource survives terminal completion
```

## Typical signatures

- temporary directories or files accumulate only for background work;
- foreground completion cleans correctly while background completion leaks;
- cancellation cleans process state but leaves setup artifacts;
- a boolean such as `is_background` disables a creator's `finally` cleanup;
- the component that observes actual exit has no cleanup callback/path/token.

## Hunting questions

- Which resources are created before the lifecycle transition?
- Who cleans them in the foreground path?
- What branch suppresses that cleanup?
- Does the successor receive the resource identity or an idempotent cleanup operation?
- If spawn/transfer fails, does the creator retain ownership?
- Does short work requested as background take the same transfer path?

## Repair shape

Make the ownership transfer explicit:

```text
creator owns cleanup
→ successor accepts cleanup token/callback/resource identity
→ mark transfer complete
→ successor cleans at authoritative terminal event
```

Failure before successful transfer leaves cleanup with the creator.

## Regression shape

Cover foreground, background completion, short-background completion, cancellation, pre-transfer failure, and cleanup failure. Assert exactly-once cleanup and that cleanup failure does not silently replace the primary operation result unless the API explicitly defines it as part of success.

## Limits and counterexamples

A deliberately persistent resource can outlive the operation. In that case there should still be an explicit durable owner or expiry policy. “Nobody cleans it because it is cached” is a policy only when the cache itself has a bounded lifecycle owner.
