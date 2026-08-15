# Fanout iterates live membership

## Metadata

```json
{
  "schema": 1,
  "id": "fanout-iterates-live-membership",
  "kind": "bug-species",
  "maturity": "candidate",
  "facets": {
    "domains": ["async-runtime", "sdk", "controllers"],
    "concerns": ["completeness", "lifecycle", "concurrency"],
    "mechanisms": ["fanout", "collection-iteration", "callback"],
    "triggers": ["mutation-during-iteration", "reentry"]
  },
  "aliases": ["attempt-all-over-mutable-collection", "live-membership-fanout"],
  "relations": [
    {"type": "violates", "target": "success-implies-complete-selected-work"}
  ],
  "cases": [
    "teamleaderleo/fieldwork#194",
    "teamleaderleo/fieldwork#225"
  ]
}
```

## In simple words

An operation intends to invoke every child that belongs to its opening membership set, but it iterates the live collection while callbacks are allowed to mutate that same collection. An early child can therefore make a later child disappear from the current fanout.

```text
opening members = [A, B, C]
invoke A
A removes B
continue live iteration
C runs, B never runs
```

Catching synchronous exceptions does not solve this: every invocation can return normally while the membership set changes underneath the loop.

## Typical signatures

- lifecycle methods promise to attempt every processor/reader/listener;
- child callbacks can unregister themselves or peers;
- tests prove exception isolation but not collection mutation;
- `map`, `forEach`, iterator, or index-based loops operate directly on a mutable owner collection;
- a later child is skipped only when an earlier child mutates membership.

## Hunting questions

- Which set of children is the operation supposed to cover: opening membership or continuously live membership?
- Can callbacks mutate the collection synchronously before the iterator reaches later members?
- Do removals apply to the current operation or only future operations?
- Does snapshotting preserve the existing concurrency and outward error contract?

## Repair shape

When the contract is "attempt every child present when the operation began":

```text
snapshot opening membership
→ invoke each snapshot member
→ convert per-child synchronous throw into the operation's normal failure representation
→ preserve live mutations for future operations
```

## Regression shape

Have child A remove child B during A's callback. Assert B still participates in the current operation but is absent from the next one. Pair that with a synchronous-throw case and ordinary concurrent fanout control.

## Limits

Some collections intentionally define live-iteration semantics. Snapshotting them would be a behavioral change. The species requires an opening-membership contract or an equivalent completeness expectation.
