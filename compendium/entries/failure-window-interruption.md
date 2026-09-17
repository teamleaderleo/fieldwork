# Failure-window interruption

## Metadata

```json
{
  "schema": 1,
  "id": "failure-window-interruption",
  "kind": "hunting-technique",
  "maturity": "mature",
  "facets": {
    "domains": ["systems", "distributed-systems", "async-runtime"],
    "concerns": ["ordering", "recovery", "state-consistency"],
    "mechanisms": ["fault-injection", "state-transition"],
    "triggers": ["partial-failure", "interruption"]
  },
  "aliases": ["what-if-we-stop-here", "phase-boundary-fault-injection"],
  "relations": [
    {"type": "related-to", "target": "publication-before-ownership"},
    {"type": "related-to", "target": "ambiguous-external-outcome"}
  ],
  "cases": [
    "teamleaderleo/linux-fieldwork#609",
    "teamleaderleo/linux-fieldwork#645",
    "teamleaderleo/fieldwork#83"
  ]
}
```

## In simple words

Write the important operation as phases and deliberately stop or fail it between them.

The core question is:

> **What if execution stops right here?**

```text
observe
→ reserve
→ prepare
→ publish
→ clean up
```

Every arrow is a candidate failure window when the two adjacent states carry different ownership, visibility, durability, or retry meaning.

## How to use it

1. name the invariant;
2. draw the smallest meaningful phase sequence;
3. identify fallible boundaries and externally visible transitions;
4. inject error, process death, cancellation, I/O failure, resource exhaustion, or lost acknowledgement at one boundary;
5. inspect surviving state;
6. restart/reopen/reconcile when persistence is involved;
7. run a negative control where the same probe crosses the boundary successfully.

## Strong observations

Look for disagreement between representations:

- live pointer versus allocator ownership;
- external effect versus local durable receipt;
- terminal result versus still-live producer;
- final filename versus incomplete bytes;
- success marker versus failed prerequisite.

## Limits

Do not inject arbitrary failures merely to create chaos. A useful interruption point distinguishes plausible invariants or ownership models. Prefer the earliest boundary that can make competing explanations diverge.
