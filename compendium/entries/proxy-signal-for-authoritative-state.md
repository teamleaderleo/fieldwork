# Proxy signal mistaken for authoritative state

## Metadata

```json
{
  "schema": 1,
  "id": "proxy-signal-for-authoritative-state",
  "kind": "bug-species",
  "maturity": "supported",
  "facets": {
    "domains": ["testing", "lifecycle", "controllers"],
    "concerns": ["ordering", "state-consistency", "truthfulness"],
    "mechanisms": ["observation", "state-transition"],
    "triggers": ["asynchrony", "reuse", "replacement"]
  },
  "aliases": ["correlated-symptom-as-completion"],
  "relations": [
    {"type": "violates", "target": "authoritative-state-gates-next-transition"}
  ],
  "cases": [
    "teamleaderleo/linux-fieldwork#423"
  ]
}
```

## In simple words

A test or controller waits for a symptom that usually accompanies a lifecycle transition and then acts as though the transition itself is complete.

```text
transition requested
      ↓
proxy symptom appears
      ↓
caller reuses / deletes / replaces state
      ↓
authoritative transition may still be finishing
```

## Typical signatures

- network/SSH loss is used as proof that shutdown completed;
- process disappearance is used as proof that all children/resources are gone;
- socket creation is used as readiness rather than a service-owned ready state;
- an output line or EOF is used as proof that durable publication finished;
- tests are flaky around immediate reuse after the proxy condition.

## Hunting questions

- What exact component owns the lifecycle transition?
- What event/state does that component expose when it is done?
- How is the proxy ordered relative to the authoritative event?
- Can the proxy arrive early under load or failure?
- What resource is reused immediately after the proxy?

## Repair shape

Observe the authoritative event/state when available. If no such signal exists, define one at the owner boundary or prove a stronger ordering contract for the proxy.

## Regression shape

Delay the authoritative completion after forcing the proxy symptom to occur. The next transition must remain blocked until the authoritative signal arrives.

## Limits and counterexamples

A proxy can be authoritative by contract. For example, a protocol may define connection close itself as the terminal event. The species requires an ordering gap between what is observed and what the caller actually needs to know.
