# Canonical Case Packs

These packs provide reusable boundary inputs for fork-free experiments. They are prompts for evidence, not a claim that every system must behave identically.

## Pack format

```json
{
  "schema_version": 1,
  "name": "example",
  "description": "What this pack exercises.",
  "timeout_seconds": 5,
  "cases": [
    {
      "id": "case-id",
      "tags": ["boundary"],
      "stdin_json": {"value": 1},
      "expect": {
        "exit_code": 0,
        "stdout_json": {"value": 1}
      }
    }
  ]
}
```

Each case provides exactly one of:

- `stdin_json` — serialized as JSON with a trailing newline;
- `stdin_text` — sent exactly as written.

Expectations are optional. Without expectations, the runner records the case as `observed`. Supported expectations are:

- `exit_code`
- `stdout_json`
- `stdout_contains`
- `stderr_contains`
- `timed_out`

## Choosing cases

Use the smallest set that can separate the current hypotheses. Large indiscriminate matrices create output, not understanding.

Common categories:

- empty and missing values;
- scalar and nested JSON boundaries;
- Unicode and normalization;
- line endings and control characters;
- malformed and truncated input;
- duplicate and reordered events;
- timeouts, cancellation, retries, and partial success;
- concurrency and idempotency;
- paths, permissions, and case sensitivity;
- interruption and recovery.

Add a new canonical case only when it is broadly reusable. Project-specific fixtures belong inside the experiment that needs them.
