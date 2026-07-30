# Review Profile

Kernel: [`KERNEL.md`](../KERNEL.md)

## Use this profile when

The assignment asks for exact-head review, acceptance, repair, execution, hold, rejection, promotion, delivery routing, or upstream-packet preparation.

## Work classification

Identify one primary class before reviewing:

- owned product delivery;
- upstream-fork research;
- execution carrier;
- evidence or documentation;
- blocked or security-sensitive work.

When a PR mixes classes, split it or name one canonical surface and treat the remainder as supporting evidence.

## Exact-head review

Record:

- repository and PR;
- canonical branch and exact head;
- exact base or current-main revision;
- complete changed-file fence;
- reviewed issue, finding, decision, or authority input generations;
- each disposition-relevant claim and evidence level;
- exact commands, runs, jobs, platforms, results, skipped checks, and failures;
- dependencies, replacements, supersession, and currentness boundary;
- author eligibility for final acceptance;
- disposition and one clearing transition.

Any movement of the code head or a disposition-bearing reviewed input expires the review unless semantic identity is proved within the reviewed fence.

## Required review behavior

1. Inspect the complete current diff, not only the latest commit or PR summary.
2. Confirm the intended assertion executed.
3. Inspect the first material failure rather than relying on a red or green summary.
4. Classify evidence per claim.
5. Separate harness, setup, fixture, installation, queue, timeout, and product behavior.
6. Challenge authority widening, cleanup replacement of primary errors, unbounded retained state, missing negative controls, and compatibility overclaims.
7. Verify canonical source and carrier identities are separate.
8. Verify temporary workflows or carrier files are absent from any candidate described as retired or canonical.
9. Reconcile issue state, live labels, finding, PR description, receipts, Review Queue, and Delivery Desk.
10. Preserve uncertainty and exact reopening conditions.

## Dispositions

Use one:

- `ACCEPT` — suitable for the exact stated next transition;
- `REPAIR` — a concrete defect must be corrected;
- `HOLD` — required evidence, dependency, authority, or safety primitive is missing;
- `EXECUTE` — source or test is prepared and target execution remains;
- `REJECT` — the premise or direction is unsound in its current form.

A disposition must name the next transition. Acceptance of research does not automatically accept a fix, proposal, merge, or upstream submission.

## Independent acceptance

Self-review prepares a handoff. It does not replace eligible independent final acceptance for consequential implementation, authority, security, destructive behavior, or upstream packets.

When review debt grows faster than dispositions, pause new promotion surfaces and consolidate, supersede, close, or finish existing work.
