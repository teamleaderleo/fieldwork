# Stale generation publishes after replacement

## Metadata

```json
{
  "schema": 1,
  "id": "stale-generation-publication",
  "kind": "bug-species",
  "maturity": "mature",
  "facets": {
    "domains": ["controllers", "storage", "agent-runtime"],
    "concerns": ["state-consistency", "authority", "ordering"],
    "mechanisms": ["generation", "publication", "replacement"],
    "triggers": ["overlap", "late-result", "partial-failure"]
  },
  "aliases": ["late-old-generation-wins", "stale-generation-overwrites-current"],
  "relations": [
    {"type": "violates", "target": "only-current-generation-may-publish"}
  ],
  "cases": [
    "teamleaderleo/fieldwork#180",
    "teamleaderleo/fieldwork#84"
  ]
}
```

## In simple words

A newer generation becomes current, but older work is still capable of publishing through a shared state owner. When the old work finishes late, it can overwrite, augment, or otherwise regain authority over future work.

Two very different cases preserve the same grammar:

```text
Tantivy:
old indexing workers still publish
+ replacement workers already admit work

Codex MCP catalogue refresh:
newer refresh C is current
+ older callback B finishes later
+ naive application can publish B after C
```

## Typical signatures

- overlapping refresh/relist/rebuild operations;
- generation A starts before B but completes after B;
- callbacks publish into one shared cache/updater without accepted-generation checks;
- replacement generation starts before old generation has quiesced;
- old in-flight work legitimately needs its captured runtime, making "cancel all old work" too broad;
- tests cover sequential replacement but not reverse completion order.

## Hunting questions

- What identity distinguishes replacement generations?
- Which generation owns future admission/publication?
- Can callbacks from an older generation still reach the shared publisher?
- Is "latest completion" accidentally treated as "latest generation"?
- Do in-flight operations need to retain old captured authority while future requests move to the new generation?
- Can failed replacement leave both generations partially live?

## Repair shapes

Depending on the lifecycle:

```text
quiesce old generation completely
→ publish/start replacement
```

or:

```text
assign monotonic generation/ticket
→ allow overlapping work
→ publish only if ticket is still accepted current
→ let old captured operations finish without future-publication authority
```

The first is useful when replacement must be exclusive. The second preserves legitimate overlap while fencing stale publication.

## Regression shape

Force reverse completion order:

```text
A starts
B starts
B becomes current
A finishes last
```

Assert future work still uses B. Add controls for healthy sequential replacement, failed B preparation, and in-flight A work that is allowed to finish under A without republishing A globally.

## Limits and counterexamples

This is not simply "old async result is stale." Some results are commutative, mergeable, or attached only to their original operation. The species requires a late result to regain or corrupt **shared future authority**.
