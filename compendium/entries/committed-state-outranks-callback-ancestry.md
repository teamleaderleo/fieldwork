# Committed state outranks callback ancestry

## Metadata

```json
{
  "schema": 1,
  "id": "committed-state-outranks-callback-ancestry",
  "kind": "invariant",
  "maturity": "supported",
  "facets": {
    "domains": ["async-runtime", "auth", "controllers"],
    "concerns": ["authority", "ordering", "state-consistency"],
    "mechanisms": ["callback", "generation", "commit-point"],
    "triggers": ["overlap", "late-result"]
  },
  "aliases": ["committed-generation-beats-callback-order", "callback-ancestry-is-not-authority"],
  "relations": [
    {"type": "related-to", "target": "authoritative-state"},
    {"type": "related-to", "target": "generation"},
    {"type": "related-to", "target": "commit-point"}
  ],
  "cases": [
    "teamleaderleo/fieldwork#657"
  ]
}
```

## In simple words

When overlapping callbacks can represent different committed generations, authority should come from committed state/version/receipt rather than from which callback started first, registered first, or happens to be on the current call stack.

```text
callback A belongs to old committed state
callback B belongs to new committed state

A registered earlier
A may finish later

registration/call ancestry ≠ authority
committed generation decides
```

## Useful review questions

- Which durable or committed state names the currently accepted generation?
- Can two callbacks share a token/name while representing different logical results?
- Does callback order merely describe timing?
- Can a late callback from an older committed generation overwrite or notify as if current?
- Is there a version/removal epoch/receipt that carries stronger authority?

## Limits

Some callback APIs explicitly define ordering itself as the contract. In those systems call or registration order can be authoritative. The invariant applies when the callbacks are reports about independently committed state rather than the commit mechanism itself.
