# Element loop becomes the accidental transaction boundary

## Metadata

```json
{
  "schema": 1,
  "id": "element-loop-becomes-accidental-transaction-boundary",
  "kind": "bug-species",
  "maturity": "supported",
  "facets": {
    "domains": ["controllers", "protocols", "configuration"],
    "concerns": ["atomicity", "authority", "state-consistency"],
    "mechanisms": ["validation", "authorization", "transaction"],
    "triggers": ["multi-item-request", "partial-failure"]
  },
  "aliases": ["mutate-as-you-validate", "partial-request-commit"],
  "relations": [
    {"type": "violates", "target": "validate-whole-logical-update-before-mutation"}
  ],
  "cases": [
    "teamleaderleo/fieldwork#657",
    "teamleaderleo/systemd#24",
    "teamleaderleo/systemd#29",
    "teamleaderleo/systemd#31"
  ]
}
```

## In simple words

One request claims one update, but implementation iteration validates and mutates each element in sequence. A later bad element rejects the request after earlier state is already live.

```text
item A valid → mutate
item B valid → mutate
item C unauthorized → error

request failed
state changed anyway
```

## Typical signatures

- validation and mutation are interleaved in one loop;
- authorization occurs immediately before each element's side effect;
- defaults or references for later elements can fail after earlier publication;
- the error response suggests the request failed atomically even though state partially changed;
- retry can apply earlier elements a second time.

## Repair shape

Separate phases: decode, validate, authorize, resolve, build candidate state, then publish according to the interface's transaction contract.

## Limits

This is not a defect for an explicitly streaming/incremental API whose documented unit of commit is each element. The bug is a mismatch between the external logical transaction and the implementation's loop boundary.
