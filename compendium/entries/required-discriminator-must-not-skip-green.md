# A required discriminator must not skip green

## Metadata

```json
{
  "schema": 1,
  "id": "required-discriminator-must-not-skip-green",
  "kind": "invariant",
  "maturity": "mature",
  "facets": {
    "domains": ["testing", "ci", "research"],
    "concerns": ["evidence", "truthfulness", "completeness"],
    "mechanisms": ["test-prerequisite", "skip", "capability"],
    "triggers": ["missing-prerequisite", "environment-limit"]
  },
  "aliases": ["skip-is-nonevidence", "required-test-fails-closed-on-skip"],
  "relations": [
    {"type": "related-to", "target": "success-implies-complete-selected-work"}
  ],
  "cases": [
    "teamleaderleo/fieldwork#657"
  ]
}
```

## In simple words

If one test is the discriminator for a claimed behavior, that test not running is **unknown evidence**, not a passing result.

```text
required discriminator
→ prerequisite missing
→ test skipped

claim status = unresolved
not green
```

A suite can truthfully report that all executed tests passed while still providing no evidence for the claim under review.

## Useful review questions

- Which exact test distinguishes the competing behaviors?
- Did it execute, or did setup/capability detection skip it?
- Was its helper binary/fixture actually built?
- Does the hosted environment have the required privilege/capability/device?
- Can the harness assert prerequisites and fail closed rather than silently skip?

## Regression shape

Deliberately remove one prerequisite and prove the evidence harness turns red/unresolved. Then restore the prerequisite and prove the discriminator actually reaches its behavioral assertion.

## Limits

Optional portability tests may legitimately skip on unsupported environments. The invariant applies only when a skipped test is being used as proof for a claim that depends on that environment/capability.
