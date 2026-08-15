# Shared terminal operation becomes its own dependency

## Metadata

```json
{
  "schema": 1,
  "id": "shared-terminal-operation-self-dependency",
  "kind": "bug-species",
  "maturity": "supported",
  "facets": {
    "domains": ["async-runtime", "sdk", "lifecycle"],
    "concerns": ["liveness", "reentry", "state-consistency"],
    "mechanisms": ["shared-promise", "fanout", "callback"],
    "triggers": ["reentry", "asynchrony"]
  },
  "aliases": ["shared-promise-self-cycle", "lifecycle-reentry-deadlock"],
  "relations": [
    {"type": "related-to", "target": "operation-owner"},
    {"type": "related-to", "target": "terminal-state-revokes-producer-authority"}
  ],
  "cases": [
    "teamleaderleo/fieldwork#216",
    "teamleaderleo/fieldwork#225"
  ]
}
```

## In simple words

Sharing one terminal operation among concurrent callers is usually useful. It becomes a deadlock when a child already awaited by that terminal operation later calls the same owner and receives the very promise whose completion depends on that child.

```text
owner shutdown promise P
    ↓ waits for
child callback
    ↓ async boundary
child calls owner.shutdown()
    ↓ receives
same promise P

P waits for child
child waits for P
```

An unrelated concurrent caller may also legitimately need to receive `P`, so the repair cannot simply reject every in-flight call.

## Typical signatures

- direct synchronous reentry is handled but delayed reentry hangs;
- a watchdog times out while no CPU-intensive work is occurring;
- unrelated callers normally join one shared terminal promise successfully;
- promise identity alone cannot distinguish a legitimate joiner from callback ancestry;
- one self-cycle traps later legitimate joiners behind the same canonical promise.

## Hunting questions

- Which callbacks are awaited by the shared terminal operation?
- Can any callback cross an async boundary and call the owner again?
- Does the reentrant call return the operation's shared promise?
- Can the runtime distinguish callback ancestry from unrelated concurrency?
- If a timeout breaks the cycle, who owns unfinished cleanup and late failures afterward?

## Repair directions

The invariant is about dependency ownership, not simply about "one promise per shutdown." Credible repairs may include explicit internal lifecycle provenance/capability, a reentry-aware owner protocol, or an operation-owned timeout **only when** the API also defines unfinished-cleanup and late-error semantics.

Do not treat caller-local timeout, raw promise-identity comparison, or rejecting all concurrent callers as complete repairs.

## Regression shape

Cover at least:

```text
direct synchronous self-reentry          → contained
async delayed same-owner reentry         → must not self-cycle
unrelated concurrent join                → still shares/settles correctly
cross-owner nested lifecycle operation   → still legal
```

## Limits

Reentry is not automatically invalid. Cross-owner nesting and unrelated concurrency can be healthy. The species requires a dependency cycle where the owner waits on a child that in turn waits on the owner's own pending terminal operation.
