# Classify a red gate at the first failing boundary

## Metadata

```json
{
  "schema": 1,
  "id": "classify-red-gate-at-first-failing-boundary",
  "kind": "hunting-technique",
  "maturity": "mature",
  "facets": {
    "domains": ["testing", "ci", "research"],
    "concerns": ["evidence", "failure-attribution", "truthfulness"],
    "mechanisms": ["gate-classification", "build", "test-execution"],
    "triggers": ["ci-failure", "harness-failure"]
  },
  "aliases": ["find-first-red-boundary", "classify-aggregate-ci-failure"],
  "relations": [
    {"type": "related-to", "target": "required-discriminator-must-not-skip-green"}
  ],
  "cases": [
    "teamleaderleo/fieldwork#657"
  ]
}
```

## In simple words

A red aggregate badge tells you that something in the gate failed. It does not tell you whether changed product code ran, whether the relevant discriminator executed, or whether the failure can contradict the claim.

Classify the earliest meaningful failing owner:

```text
checkout
→ dependency/setup
→ code generation
→ broad build
→ changed target compile
→ relevant test starts
→ behavioral assertion
```

## Procedure

1. locate the first failing command/target;
2. identify its owner: product, fixture, capability, workflow, tooling, packaging, or evidence;
3. ask whether candidate code compiled or executed before failure;
4. ask whether the failure can falsify the claimed behavior;
5. reproduce on unchanged base when practical;
6. isolate a candidate-relevant target under the same toolchain when broad infrastructure is broken;
7. report the classification rather than replacing red with either `candidate broken` or `irrelevant CI` by instinct.

## Why pair it with skip classification

```text
green aggregate + discriminator skipped = insufficient evidence
red aggregate + candidate never executed = not automatically candidate failure
```

Both require reasoning about which proof boundary actually ran.
