# Execution Profile

Kernel: [`KERNEL.md`](../KERNEL.md)

## Use this profile when

The assignment needs target-native tests, integration execution, platform matrices, temporary workflows, execution carriers, or immutable receipts.

## Canonical source and carrier

Keep these identities separate:

- **canonical source** — the product source and tests being evaluated;
- **execution carrier** — temporary workflow or branch machinery used to run that source.

The carrier must name the exact source head it applies or tests, the exact command or workflow, the expected source fence, and the canonical record that consumes the receipt.

Default per invariant:

```text
one preferred source candidate
one active execution carrier
```

Create a replacement carrier only after classifying a harness or workflow defect, polluted diff, distinct execution purpose, or explicit retirement of the current carrier. Runner queue delay alone is not sufficient.

## Procedure

1. Confirm the canonical source branch, head, base, changed-file fence, and active carrier state.
2. Run the smallest discriminating control first.
3. Resolve exact test names and counts before claiming execution.
4. Follow the target repository's installation, build, test, lint, platform, and formatting sequence.
5. Record repository, source head, carrier head, workflow run, job, environment, command, assertion, and result.
6. Classify the first failing phase before changing source:
   - queue or runner;
   - checkout or identity;
   - installation or toolchain;
   - patch application or reconstruction;
   - fixture or setup;
   - target build;
   - intended test;
   - compatibility or full gate;
   - publication or cleanup.
7. Treat setup, installation, fixture, harness, queue, and timeout failures as execution-system evidence, not product behavior.
8. When a run changes the theory, update the canonical finding and source record before promotion.
9. Transfer useful receipts to the canonical source record.
10. Close or archive disposable carriers only after a later exact head proves temporary machinery is absent and the source plus receipt remain reviewable.

## Required controls

- Verify the exact source fence after reconstruction or patch application.
- Ensure intended tests execute exactly once unless multiplicity is part of the design.
- Preserve negative controls and compatibility cases.
- Separate larger-stack, debug-only, synthetic, or altered-environment results from the production contract.
- Re-run exact-head checks after source, test, workflow, or cleanup changes.
- Do not publish or promote from a synthetic merge commit without naming the contained source head.

## Queue pressure

When execution is runner-bound:

- do not create equivalent carriers;
- review complete source diffs;
- classify latest upstream or base drift;
- reconcile findings and receipts;
- retire stale or duplicate machinery;
- perform prior-art and source analysis that does not consume the blocked resource;
- leave the exact queued run and next action durable.
