# Selected terminal outcome survives cleanup

## Metadata

```json
{
  "schema": 1,
  "id": "selected-terminal-outcome-survives-cleanup",
  "kind": "invariant",
  "maturity": "supported",
  "facets": {
    "domains": ["async-runtime", "process-lifecycle", "networking"],
    "concerns": ["lifecycle", "error-semantics", "truthfulness"],
    "mechanisms": ["cleanup", "terminal-state"],
    "triggers": ["cancellation", "cleanup-failure", "late-signal"]
  },
  "aliases": ["primary-outcome-precedes-cleanup"],
  "relations": [],
  "cases": [
    "teamleaderleo/linux-fieldwork#297",
    "teamleaderleo/fieldwork#76",
    "teamleaderleo/fieldwork#882"
  ]
}
```

## In simple words

Once an operation has enough authoritative evidence to select its terminal outcome, later cleanup should preserve that outcome rather than silently replacing it with a secondary signal, cleanup error, or cancellation artifact.

```text
operation selects terminal result
        ↓
cleanup / release / cancellation
        ↓
report selected result
+ separately retain cleanup trouble
```

This invariant is about **which result wins**. A related but separate question is whether cleanup is allowed to delay publication of that result indefinitely.

## Useful review questions

- At what point is the primary outcome complete?
- Which later operations exist only to clean up resources?
- Can a signal or cleanup error arrive after the primary result is already known?
- Does the implementation accidentally give the last failure to occur precedence over the most authoritative failure?
- Where are secondary cleanup failures recorded if they do not replace the primary result?

## Limits

Some APIs explicitly define cleanup success as part of the operation's success contract. In those systems cleanup failure may legitimately make an otherwise successful operation fail. The important distinction is whether cleanup is part of the claimed transaction or a later best-effort consequence.
