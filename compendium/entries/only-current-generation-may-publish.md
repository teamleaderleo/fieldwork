# Only the current accepted generation may publish future authority

## Metadata

```json
{
  "schema": 1,
  "id": "only-current-generation-may-publish",
  "kind": "invariant",
  "maturity": "mature",
  "facets": {
    "domains": ["controllers", "storage", "agent-runtime"],
    "concerns": ["state-consistency", "authority", "ordering"],
    "mechanisms": ["generation", "publication", "replacement"],
    "triggers": ["overlap", "late-result", "partial-failure"]
  },
  "aliases": ["stale-generations-cannot-publish", "newest-accepted-generation-wins"],
  "relations": [
    {"type": "related-to", "target": "authoritative-state"},
    {"type": "related-to", "target": "publication"}
  ],
  "cases": [
    "teamleaderleo/fieldwork#180",
    "teamleaderleo/fieldwork#84"
  ]
}
```

## In simple words

When work is replaced by a newer generation, old work may still finish, but it must no longer be able to publish state that controls future operations.

```text
generation A starts
→ generation B supersedes A
→ B becomes accepted current
→ A finishes late
→ A result may be observed/retained
→ A must not replace B as future authority
```

This is stronger than "last callback wins" and different from requiring every old task to be cancelled immediately. Old work can sometimes finish safely as long as publication authority is fenced.

## Useful review questions

- What creates a new generation?
- Which event makes one generation accepted/current?
- Can older callbacks still arrive afterward?
- Does every publication carry or check generation identity?
- Are in-flight operations allowed to keep their captured old runtime while future work uses the new one?
- What happens if replacement preparation fails halfway?

## Limits

Some systems define mergeable or monotonic results where multiple generations may safely contribute. The invariant applies when publication selects exclusive future authority, not whenever older work completes after newer work.
