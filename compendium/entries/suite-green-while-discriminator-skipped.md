# Suite green while the discriminator skipped

## Metadata

```json
{
  "schema": 1,
  "id": "suite-green-while-discriminator-skipped",
  "kind": "bug-species",
  "maturity": "mature",
  "facets": {
    "domains": ["testing", "ci", "research"],
    "concerns": ["evidence", "truthfulness", "completeness"],
    "mechanisms": ["test-prerequisite", "skip", "capability"],
    "triggers": ["missing-prerequisite", "environment-limit"]
  },
  "aliases": ["green-without-running-the-proof", "skipped-proof-reported-as-pass"],
  "relations": [
    {"type": "violates", "target": "required-discriminator-must-not-skip-green"}
  ],
  "cases": [
    "teamleaderleo/fieldwork#657"
  ]
}
```

## In simple words

The aggregate test command is green, but the one test capable of proving the behavior never executed because a helper, privilege, capability, device, or environment prerequisite was missing.

## Typical signatures

- CI says `passed` while the relevant test says `skipped` or `ignored`;
- a helper binary was never built, so capability setup could not run;
- privilege/capability detection silently turns the test into a skip;
- reviewers cite suite color without inspecting the discriminating test;
- the same branch produces green on environments incapable of exercising the claimed behavior.

## Repair shape

Make the proof harness explicit about required prerequisites. Treat unavailable prerequisites as unresolved evidence or route to an environment that can execute them. Preserve suite pass/fail semantics for unrelated optional tests.

## Limits

A skipped optional test is not a defect by itself. The species is an **evidence-classification bug** when a green aggregate result is promoted as proof of behavior the environment never exercised.
