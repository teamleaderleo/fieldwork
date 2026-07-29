# Retry and Idempotency Example

This retained playground demonstrates how a tiny local model can test one property while a separate integration-context dossier explains why the property is relevant in larger systems.

## Question

If a service commits a side effect but its response is lost, can the caller retry without creating the effect twice?

## Run

```text
python3 scripts/run_playground_cases.py \
  --pack playgrounds/cases/retry-idempotency.json \
  --adapter "python3 playgrounds/examples/retry-idempotency/run.py" \
  --output /tmp/fieldwork-retry-idempotency.json
```

## Cases

- `safe-retry-after-lost-response` — the second attempt replays the retained outcome and creates no second effect.
- `naive-retry-duplicates-effect` — the same logical request commits twice.
- `key-reuse-with-different-payload` — one identity cannot silently represent different intent.
- `distinct-operations-remain-distinct` — separate identities still create separate effects.

## What the model preserves

- ambiguity after response loss;
- logical request identity;
- durable side-effect count;
- remembered result replay;
- conflict when identity and payload disagree.

## What the model omits

- actual HTTP transport;
- distributed storage and replication;
- concurrent requests;
- crashes and recovery;
- key retention and eviction;
- authentication and tenancy;
- retry backoff and amplification;
- tracing and metrics;
- any particular upstream implementation.

The wider context and primary sources are recorded in `contexts/patterns/retry-idempotency.md`. The isolated test should not be cited as evidence for any omitted production property.