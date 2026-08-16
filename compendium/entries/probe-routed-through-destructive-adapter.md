# Probe routed through a destructive adapter

## Metadata

```json
{
  "schema": 1,
  "id": "probe-routed-through-destructive-adapter",
  "kind": "bug-species",
  "maturity": "supported",
  "facets": {
    "domains": ["process-lifecycle", "cli", "systems"],
    "concerns": ["authority", "safety", "compatibility"],
    "mechanisms": ["dispatch", "adapter", "operation-kind"],
    "triggers": ["broad-option", "platform-adapter"]
  },
  "aliases": ["non-destructive-operation-inherits-destructive-scope"],
  "relations": [
    {"type": "violates", "target": "classify-operation-before-destructive-adapter"}
  ],
  "cases": [
    "teamleaderleo/fieldwork#657",
    "teamleaderleo/execa#1"
  ]
}
```

## In simple words

A non-destructive operation shares a low-level API with destructive operations. Policy/adaptor selection happens first, so an option intended to broaden the destructive case also broadens the probe into a mutation.

```text
caller asks: inspect/probe
→ generic adapter selection sees broad option
→ destructive descendant/process-tree adapter chosen
→ probe now has side effects
```

## Typical signatures

- signal value `0`, HEAD-like probes, validation-only modes, or dry-run flags share a function with mutation paths;
- a broad-scope option is applied before operation kind is checked;
- platform adapters are named around the destructive case and receive probe inputs anyway;
- tests cover mutation scope but not non-destructive operations under the same options.

## Repair shape

Fence the non-destructive semantic operation before destructive adapter/policy selection. Keep scope-broadening options meaningful only where the operation contract permits side effects.

## Regression shape

Run the probe with every destructive-scope option enabled and prove it remains observational. Pair with a real destructive operation to prove the option still broadens the intended path.

## Limits

Shared low-level code is fine when it preserves the probe contract. The species concerns authority leakage across semantic operation kinds, not code reuse itself.
