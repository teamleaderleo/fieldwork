# Cleanup replaces the selected outcome

## Metadata

```json
{
  "schema": 1,
  "id": "cleanup-replaces-selected-outcome",
  "kind": "bug-species",
  "maturity": "mature",
  "facets": {
    "domains": ["async-runtime", "process-lifecycle", "networking"],
    "concerns": ["error-semantics", "lifecycle", "truthfulness"],
    "mechanisms": ["cleanup", "terminal-state"],
    "triggers": ["cleanup-failure", "cancellation", "late-signal"]
  },
  "aliases": ["secondary-cleanup-overwrites-primary-result"],
  "relations": [
    {"type": "violates", "target": "selected-terminal-outcome-survives-cleanup"}
  ],
  "cases": [
    "teamleaderleo/linux-fieldwork#297",
    "teamleaderleo/fieldwork#76",
    "teamleaderleo/fieldwork#882"
  ]
}
```

## In simple words

The operation already has an authoritative result, but a later cleanup action, signal, or cancellation artifact becomes the value the caller sees instead.

```text
primary operation → result R
        ↓
cleanup → secondary result C
        ↓
caller receives C and loses R
```

This is often caused by ordinary exception propagation: cleanup runs later, so its failure naturally becomes the last exception unless the implementation explicitly preserves outcome precedence.

## Typical signatures

- a guest/protocol failure becomes a host signal exit code during teardown;
- an already-selected abort result is replaced by a provider error arriving later;
- body cancellation failure replaces an already-known download/size/status failure;
- cleanup succeeds in most tests, hiding the precedence rule entirely.

## Hunting questions

- When does the primary result become complete and authoritative?
- Which later operations are cleanup rather than part of the primary transaction?
- What happens if cleanup throws, rejects, receives a signal, or times out?
- Is outcome precedence explicit or merely whichever exception occurs last?
- Are secondary cleanup diagnostics retained somewhere useful?

## Repair shape

Select and preserve the primary outcome before beginning secondary cleanup. Run cleanup best-effort or under a separately defined failure policy. Report cleanup trouble without rewriting an already-authoritative terminal result.

## Regression shape

Construct a matrix rather than one happy-path test:

```text
primary success + cleanup success
primary failure + cleanup success
primary failure + cleanup failure
primary success + cleanup failure
primary completed + later signal
```

The expected precedence should be written as part of the contract.

## Limits and counterexamples

If cleanup is itself a required commit step, its failure can legitimately determine the operation result. Distinguish “release diagnostic resources after completion” from “perform the final durable transaction step.”
