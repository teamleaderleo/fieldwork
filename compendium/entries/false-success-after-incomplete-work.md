# False success after incomplete work

## Metadata

```json
{
  "schema": 1,
  "id": "false-success-after-incomplete-work",
  "kind": "bug-species",
  "maturity": "mature",
  "facets": {
    "domains": ["developer-tools", "storage", "lifecycle"],
    "concerns": ["completeness", "truthfulness", "recovery"],
    "mechanisms": ["aggregation", "status-publication"],
    "triggers": ["partial-failure", "skipped-work"]
  },
  "aliases": ["false-clean-certification", "incomplete-coverage-success"],
  "relations": [
    {"type": "violates", "target": "success-implies-complete-selected-work"}
  ],
  "cases": [
    "teamleaderleo/fieldwork#626",
    "teamleaderleo/linux-fieldwork#611"
  ]
}
```

## In simple words

The system publishes success, clean state, or an empty successful result even though work required by that claim failed or was skipped.

Two very different domains can produce the same misleading sentence:

```text
required work incomplete
        ↓
result surface forgets incompleteness
        ↓
SUCCESS / CLEAN / EMPTY
```

In one case a storage image can be marked clean after required metadata synchronization failed. In another an audit can exit successfully after every selected object was skipped because its required metadata could not be read.

## Typical signatures

- a warning exists on stderr but exit status is zero;
- a clean/current marker is written after an earlier error;
- an empty machine-readable result means either “nothing selected” or “everything skipped”;
- downstream recovery changes behavior because a success marker suppresses repair;
- aggregate success is computed only from completed items, while failed-to-enter items disappear from the denominator.

## Hunting questions

- What work did the operation claim to select?
- Which failures happen before an item reaches the result aggregation stage?
- Is success computed from the requested set or only the surviving completed subset?
- Which durable markers are published after an earlier failure?
- Can the same output represent both genuine emptiness and incomplete coverage?
- What does the next process infer from the success marker?

## Repair shape

Choose one explicit contract:

```text
complete success
```

or:

```text
partial result + explicit missing/error members
```

Do not silently turn required failures into absence.

For durable clean/current markers, publish them only after the operations that make the marker truthful have succeeded.

## Regression shape

Pair a genuine-empty or genuinely-clean control with forced incomplete work:

```text
nothing selected            → success
selected work all succeeds  → success
selected work partly fails  → non-success OR explicit partial state
selected work all skipped   → not indistinguishable from genuine empty
```

## Limits and counterexamples

Best-effort discovery tools can intentionally define “success means every *discoverable* object was handled.” That is a different contract. The bug exists only when callers or downstream state interpret success more strongly than the implementation's skip policy.
