# Classify the operation before selecting a destructive adapter

## Metadata

```json
{
  "schema": 1,
  "id": "classify-operation-before-destructive-adapter",
  "kind": "invariant",
  "maturity": "supported",
  "facets": {
    "domains": ["process-lifecycle", "cli", "systems"],
    "concerns": ["authority", "safety", "compatibility"],
    "mechanisms": ["dispatch", "adapter", "operation-kind"],
    "triggers": ["broad-option", "platform-adapter"]
  },
  "aliases": ["probe-before-kill-adapter", "non-destructive-ops-bypass-destructive-policy"],
  "relations": [
    {"type": "related-to", "target": "operation-owner"}
  ],
  "cases": [
    "teamleaderleo/fieldwork#657",
    "teamleaderleo/execa#1"
  ]
}
```

## In simple words

Decide whether an operation is destructive, observational, validating, or dry-run **before** routing it through an adapter whose options may broaden destructive scope.

```text
operation semantics
    ↓ classify
probe / validate / inspect  → non-destructive path
destructive action          → destructive adapter/policy
```

An option such as “include descendants” must not turn a process-existence probe into termination merely because both operations share a signal/adapter API.

## Useful review questions

- What semantic operation is the caller requesting?
- Which operations use the same low-level primitive but have different authority?
- Can an option broaden scope before the code distinguishes probe from mutation?
- Does a platform adapter assume every signal/action is destructive?
- Is dry-run/validate/inspect behavior fenced before mutation-capable policy?

## Limits

Sometimes an observational operation genuinely needs a privileged/destructive-looking adapter to obtain authoritative state. The invariant is to preserve the operation's authority semantics, not to ban shared implementations.
